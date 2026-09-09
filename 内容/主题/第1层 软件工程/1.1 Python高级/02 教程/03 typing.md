# typing（★★★★★）

> **目标：用类型标注把 Python 从"运行时才能发现错误"拉回"写代码时就被检查器抓住"——不是学一堆语法，而是理解类型系统能替你承担什么、不能替你承担什么。**

---

## 零、先建立一个认知：类型标注改变的是"检查时机"，不是"运行行为"

在进入任何语法之前，必须先把一个最根本、也最容易被误解的事实钉死：

```python
def add(a: int, b: int) -> int:
    return a + b

>>> add(1, 2)          # 3
>>> add("a", "b")      # "ab"——不报错！Python 运行时完全无视类型标注
```

`a: int` 这个标注，**Python 解释器在运行时会原样忽略**。它不校验、不强制、不报错——程序该怎么跑还怎么跑。

那么类型标注到底改变什么？它改变的是**检查时机**：

| | 没有类型标注 | 有类型标注 + 静态检查器 |
|---|---|---|
| 类型错误在哪里暴露 | 运行时（可能在生产环境、可能几个月后才触发） | **写代码时**（IDE 里立刻标红 / mypy 命令行） |
| 谁来发现 | 异常堆栈 | 类型检查器（mypy / pyright） |
| IDE 能否补全/跳转 | 不能——它不知道 `x` 是什么 | 能——它知道 `x: int` |

所以类型标注的本质是：**把一份"接口契约"写进代码，交给工具去机器验证。** 它不替代运行时校验（那是 pydantic 的事，本教程 1.1 学习目标里的"三层划分"会呼应），它替代的是"靠人脑记住每个变量的类型"。

**这条认知贯穿全章**：下面每一个标注工具，你都要问自己两个问题——「它让检查器能多发现什么错误？」「它会在运行时留下什么副作用吗？」

---

## 一、基础标注：变量、函数、参数

### 1.1 变量与函数标注

```python
name: str = "Alice"              # 变量标注
count: int = 0

def greet(name: str) -> str:     # 参数标注 + 返回值标注
    return f"Hello, {name}"
```

规则很简单：

- **参数**：`参数名: 类型`
- **返回值**：在 `)` 和 `:` 之间用 `-> 类型`
- **变量**：`变量名: 类型 = 值`（标注可以和赋值分离，`x: int` 单独一行也是合法的）

标注只在**静态层面**有意义，运行时它们以 `__annotations__` 的形式挂在对象上，但不会被强制执行：

```python
>>> greet.__annotations__       # {'name': <class 'str'>, 'return': <class 'str'>}
```

### 1.2 内置类型与容器类型

```python
# 标量
x: int
y: float
z: bool
s: str
b: bytes
n: None                # None 的类型是 NoneType，直接标 None

# 容器（Python 3.9+ 用内置泛型语法）
nums: list[int]                # 3.9 之前要写 List[int]（from typing import List）
pairs: dict[str, int]
coords: tuple[float, float]
names: set[str]
```

**版本边界（重要，容易写错）：** `list[int]`、`dict[str, int]` 这种**小写内置泛型**语法要求 **Python ≥ 3.9**。3.8 及以下必须从 `typing` 导入 `List`、`Dict`、`Tuple` 等大写版本：

```python
from typing import List, Dict, Tuple    # 仅 3.8 及以下需要

nums: List[int]
pairs: Dict[str, int]
```

这套教程假定 Python ≥ 3.9，全章一律用 `list[int]` 小写语法。

**嵌套容器**：

```python
matrix: list[list[int]]                    # 二维数组
scores: dict[str, list[float]]             # 键是 str，值是 float 列表
registry: dict[str, tuple[int, str]]       # 值是一个二元组
```

### 1.3 标注的两个常见误区

**误区一：以为标注会运行时校验。** 前面已经讲过，`add("a", "b")` 照样跑。标注是给工具看的，不是给解释器看的。

**误区二：不写返回值标注。** 很多人只标参数不标返回值。但返回值标注往往更重要——它是**函数的对外承诺**，调用方靠它知道"我能拿到什么"。漏掉返回值标注，等于把你的接口契约只写了一半。

```python
# ❌ 只标入参，不标返回——调用方不知道拿到的是什么
def find_user(user_id: int):
    ...

# ✅ 完整契约
def find_user(user_id: int) -> User | None:
    ...
```

### 1.4 `type[X]`——"类本身"作为类型

一个容易漏掉、但插件系统里一定会用到的标注：**怎么标注"传进去的是一个类，而不是一个实例"？**

```python
class Dog:
    def __init__(self, name: str):
        self.name = name

def create(cls: type[Dog], name: str) -> Dog:    # cls 是"Dog 这个类本身"
    return cls(name)

d = create(Dog, "Rex")     # ✅ 传类
d = create(Dog(), "Rex")   # ❌ mypy 报错：传了实例，不是类
```

`type[Dog]` 读作"`Dog` 这个类对象"（或它的子类）。它和 `Dog` 是**两个不同的类型**：

- `Dog` 是"一个 Dog **实例**"；
- `type[Dog]` 是"`Dog` 这个**类本身**"。

这正是插件系统 `Registry` 的核心标注——注册表存的是「扩展名 → 类」（"存类不存实例"），所以它的类型是 `dict[str, type[DocumentReader]]`：值是**类**，不是 `DocumentReader` 的实例。这个知识点在第十四节的项目里会实际用到。

---

## 二、联合与可选：`Union`、`Optional` 和 `|`

### 2.1 一个值可能属于多种类型

函数可能返回整数或字符串、参数可能传列表或元组——这时需要**联合类型**：

```python
from typing import Union

def parse(value: str) -> Union[int, float]:
    ...
```

`Union[int, float]` 表示"`int` 或 `float` 都行"。

**Python 3.10+ 的简写**——用 `|` 运算符：

```python
def parse(value: str) -> int | float:      # 等价于 Union[int, float]
    ...
```

这套教程统一用 `|` 语法（要求 Python ≥ 3.10），它更简洁、无需 import。

### 2.2 `Optional`——"可能是 None"的联合

编程里最常见的联合类型是"`X` 或 `None`"——查不到就返回 `None`：

```python
from typing import Optional

def find_user(user_id: int) -> Optional[User]:
    if user_id in db:
        return db[user_id]
    return None                              # 找不到时返回 None
```

`Optional[User]` 等价于 `Union[User, None]`——它**不是**"这个参数可传可不传"（那叫默认参数），而是"这个值可能是 `None`"。

**3.10+ 的等价写法：**

```python
def find_user(user_id: int) -> User | None:   # 推荐——更直白
    ...
```

**关键——`Optional` 逼着调用方处理 `None`。** 一个标了 `Optional[User]` 的函数，检查器会强制调用方在使用返回值前先判空：

```python
user = find_user(42)
print(user.name)          # ❌ mypy 报错：user 可能是 None
                          # error: Item "None" of "Optional[User]" has no attribute "name"

if user is not None:      # ✅ 判空之后才安全
    print(user.name)
```

这正是类型标注最有价值的时刻：**它把"你忘了判空"这种最常见的运行时崩溃，提前到写代码时抓出来。**

### 2.3 联合类型的陷阱：别用 `Union` 糊弄接口设计

`Union` 是万能的，但滥用它是坏味道。如果一个函数返回三种以上互不相干的类型，通常意味着**接口设计有问题**——调用方被迫写一堆 `isinstance` 分支才能用返回值：

```python
# ❌ 反模式——返回类型太杂，调用方没法干净地使用
def get_data() -> str | int | list | None:
    ...

# ✅ 更好的设计——拆成明确的接口，或用自定义类型（见后面的 TypedDict/dataclass）
```

一个值得记住的经验：**`Optional` 是合理的、高频的；但四五个类型的大杂烩联合，往往是设计缺陷的信号。**

---

## 三、`Any`——类型系统里的"逃生舱"

### 3.1 `Any` 是什么

`Any` 表示"任意类型，完全放弃检查"：

```python
from typing import Any

def process(data: Any) -> Any:
    return data
```

一个标了 `Any` 的值，可以做**任何事**而检查器不抱怨——调任何方法、访问任何属性、赋给任何类型：

```python
x: Any = some_function()
x.foo()            # 不报错
x.bar = 1          # 不报错
y: int = x         # 不报错——Any 能赋给任何类型
```

`Any` 在类型系统里是**双向可赋**的：任何类型都能赋给 `Any`，`Any` 也能赋给任何类型。它就像一个黑洞，把类型检查整个吸掉。

### 3.2 `Any` 的正确用法与滥用

**正确用法**——当你确实处理"完全动态"的数据时：

```python
def deserialize(raw: str) -> Any:     # JSON 解析结果类型未知——用 Any 合理
    import json
    return json.loads(raw)
```

**滥用**——把 `Any` 当偷懒的借口：

```python
# ❌ 滥用——明明知道是什么类型，却用 Any 糊弄，检查器形同虚设
def get_user() -> Any:
    return {"name": "Alice", "age": 30}    # 你知道这是 dict[str, ...]
```

**核心原则：`Any` 是逃生舱，不是默认选项。** 每写一个 `Any`，你都应该能说出理由。`Any` 一旦扩散，类型检查的价值就归零了——一个 `Any` 变量会把"任意类型"传染给所有用到它的表达式，检查器对整条链都闭嘴。

**`Any` 与 `object` 的区别（容易混淆）：**

```python
def f1(x: Any) -> Any: ...       # 放弃检查——x 什么都能干
def f2(x: object) -> object: ... # x 是"最宽泛的基类"——但它没有具体方法
```

`object` 是"所有类的基类"，标了 `object` 的变量**仍然受检查**——你不能在它上面调 `foo()`，因为 `object` 没有这个方法。而 `Any` 是"彻底不检查"。两者语义完全不同：`object` 是"一个我不知道具体类型、但保证是个对象的值"，`Any` 是"别管了，我什么都可能是"。

---

## 四、字面量与常量：`Literal`、`Final`

### 4.1 `Literal`——把"具体的几个值"作为类型

有些参数的合法取值是**有限的几个字面量**，而不是一个宽泛的 `str`：

```python
from typing import Literal

def set_mode(mode: Literal["read", "write", "append"]) -> None:
    ...

set_mode("read")          # ✅
set_mode("r")             # ❌ mypy 报错：只能是 "read" / "write" / "append"
```

`Literal["read", "write", "append"]` 的意思是：这个参数**只接受这三个字符串**。检查器会在你写错字面量（比如拼错、用了 `"r"` 这种简写）时立刻报警。

**典型场景**——区分重载语义、限制枚举值：

```python
def fetch(data: str, fmt: Literal["json", "csv"]) -> str:
    ...

# 配合 Union 表达"有限可选值之一"
Alignment = Literal["left", "center", "right"]

def align(text: str, mode: Alignment) -> str:
    ...
```

**注意 `Literal` 的边界：** 它是给**静态检查器**看的，运行时没有任何作用——`set_mode("r")` 照样能跑，只是 mypy 会报错。它表达的是"契约上只允许这几个值"，配合检查器在写代码阶段拦截拼写错误和非法值。

### 4.2 `Final`——标记"不可重新赋值"

`Final` 用来声明"这个名字不该被重新赋值"：

```python
from typing import Final

MAX_RETRIES: Final = 3
API_BASE_URL: Final[str] = "https://api.example.com"

MAX_RETRIES = 5        # ❌ mypy 报错：不能重新赋值给 Final 变量
```

`Final` 有三个用途：

**（a）模块级常量**——阻止"常量被意外修改"：

```python
DEFAULT_TIMEOUT: Final[float] = 30.0
```

**（b）类属性不被子类覆盖**：

```python
class Base:
    VERSION: Final = "1.0"

class Child(Base):
    VERSION = "2.0"     # ❌ mypy 报错：不能覆盖 Final 类属性
```

**（c）`@final` 装饰器——方法/类不被覆盖**（注意是**小写 `@final` 装饰器**，不是 `Final[...]` 标注）：

```python
from typing import final

class Base:
    @final
    def locked(self) -> None: ...    # 这个方法不允许子类 override

@final
class Sealed: ...                   # 这个类不允许被继承
```

**`Final[...]` 和 `@final` 是两个不同的东西，别混：** `Final[int]` 是**标注**，标在**变量/属性**上，表示"这个值不该被重新赋值"；`@final` 是**装饰器**，标在**方法/类**上，表示"这个方法不该被覆盖 / 这个类不该被继承"。两者来源相同（都表达"到此为止，别再改了"），但作用于不同的对象。

**同样注意：`Final` 是静态约定，不是运行时强制。** Python 解释器**不会**真的阻止你 `MAX_RETRIES = 5`——它照样执行。`Final` 的约束只在 mypy/pyright 层面生效。这一点和 Java 的 `final` 有本质区别（Java 是编译期强制）。

---

## 五、可调用对象：`Callable`

### 5.1 把"函数"本身作为参数/返回值

高阶函数（函数接受函数、函数返回函数）需要描述"函数"这个类型：

```python
from typing import Callable

def apply(func: Callable[[int], int], value: int) -> int:
    return func(value)

def double(x: int) -> int:
    return x * 2

>>> apply(double, 5)    # 10
```

`Callable[[int], int]` 的读法是：**第一个方括号里是参数类型列表，第二个位置是返回值类型**。

- `Callable[[int], int]`——接受一个 `int`，返回 `int` 的函数
- `Callable[[int, str], bool]`——接受 `int` 和 `str`，返回 `bool` 的函数
- `Callable[[], None]`——不接受参数、返回 `None` 的函数（空参数列表 `[]`）

### 5.2 `Callable` 的局限——它描述不了参数名

`Callable` 只能描述**位置和类型**，描述不了**关键字参数名**。下面这个场景 `Callable` 就力不从心：

```python
# 想表达"接受关键字参数 name 和 age 的函数"——Callable 做不到
# Callable[[int, str], ...] 只能描述位置，丢了参数名信息
```

这种"需要精确描述参数签名"的场景，应该用 `Protocol`（见第八节）——`Protocol` 可以完整声明一个带参数名的方法签名。记住这个边界：**`Callable` 适合"匿名回调"（一个函数参数就够），`Protocol` 适合"有明确签名契约的对象"。**

---

## 六、类型别名：`TypeAlias`

### 6.1 给复杂类型起个名字

当某个类型标注又长又重复出现时，给它起个别名：

```python
from typing import TypeAlias

UserId: TypeAlias = int
Matrix: TypeAlias = list[list[float]]
Result: TypeAlias = dict[str, list[int]]
Callback: TypeAlias = Callable[[int], str]
```

之后就能直接用别名，代码可读性大幅提升：

```python
def process(user_id: UserId, data: Matrix) -> Result:
    ...
```

**为什么要有 `TypeAlias` 这个显式标记？** 因为裸赋值有歧义：

```python
x: int = 3            # 这是"一个 int 类型的变量"
UserId = int          # 这到底是"类型别名"还是"一个变量"？——从代码看不出
UserId: TypeAlias = int    # 显式声明：这是类型别名，不是变量
```

`TypeAlias`（Python 3.10+）就是消除这个歧义的标记，让检查器和读代码的人都知道"这是一个类型的另一个名字，不是运行时变量"。

### 6.2 别名 vs 新类型——什么时候用 `NewType`

**关键区分：** 类型别名只是"同一个类型的另一个名字"，**不创造新的类型**。如果两个概念在语义上不该混用、但底层类型相同，别名救不了你：

```python
UserId: TypeAlias = int
OrderId: TypeAlias = int

def get_order(order_id: OrderId) -> Order: ...

uid: UserId = 42
get_order(uid)        # ✅ 不报错！——UserId 和 OrderId 都是 int，别名挡不住
```

想真正区分"语义上不同的两个 int"，用 `NewType`：

```python
from typing import NewType

UserId = NewType("UserId", int)
OrderId = NewType("OrderId", int)

uid = UserId(42)
get_order(uid)        # ❌ mypy 报错：UserId 不能当 OrderId 用
```

`NewType` 在**静态层面**创造了一个新类型（检查器会区分），但**运行时它就是个恒等函数**（`UserId(42)` 返回的就是 `42` 本身，零开销）。这是它和 `class UserId(int)` 的本质区别——后者会在运行时真正创建一个子类对象，有开销。

**什么时候用 `NewType`：** 两个底层类型相同、但语义上绝不能混淆的标识（用户 ID vs 订单 ID、美元金额 vs 人民币金额）。它能防止"把订单 ID 错当成用户 ID 传进去"这类逻辑 bug。

---

## 七、泛型：`TypeVar` 与 `Generic`

### 7.1 问题：如何描述"装着任意类型的容器"

看这个函数：

```python
def first(items: list) -> ???:    # 返回值类型取决于 items 里装的是什么
    return items[0]
```

`first([1, 2, 3])` 返回 `int`，`first(["a", "b"])` 返回 `str`——返回值类型**由入参决定**。普通标注无法表达"返回类型 = 入参列表的元素类型"这种关系。

这就是**泛型（Generic）**要解决的问题：用一个**类型变量**代表"某个未知的类型"，并建立"入参与返回之间共享这个类型"的关系。

### 7.2 `TypeVar`——声明类型变量

```python
from typing import TypeVar

T = TypeVar("T")        # 声明一个类型变量 T，代表"任意类型"

def first(items: list[T]) -> T:
    return items[0]
```

现在检查器能精确推断：

```python
x = first([1, 2, 3])        # x 的类型是 int
y = first(["a", "b"])       # y 的类型是 str
```

`TypeVar("T")` 的 `"T"` 是名字（必须和变量名 `T` 一致）。类型变量是一个**占位符**，检查器在每次调用时把它绑定到实际类型，从而在 `list[T] → T` 之间建立"进什么、出什么"的关联。

### 7.3 约束类型变量——限定 T 的范围

有时类型变量不是"任意类型"，而是"某几个类型之一"：

```python
from typing import TypeVar

Number = TypeVar("Number", int, float)     # Number 只能是 int 或 float

def add(a: Number, b: Number) -> Number:
    return a + b
```

`TypeVar("Number", int, float)` 表示 `Number` 被**约束**为 `int` 或 `float`，检查器会拒绝其他类型。

另一个约束方式是 `bound=`（限定上界——必须是某类型的子类）：

```python
class Animal: ...

AnimalType = TypeVar("AnimalType", bound=Animal)    # 必须是 Animal 的子类

def feed(a: AnimalType) -> AnimalType:
    ...
```

**`TypeVar` 约束 vs `bound` 的区别：**

| | `TypeVar("T", int, float)` | `TypeVar("T", bound=Animal)` |
|---|---|---|
| 允许的类型 | 明确列出的这几个 | `Animal` 及其所有子类 |
| 语义 | "只能是这几个之一" | "必须是某个家族的一员" |

### 7.4 `Generic`——泛型类

泛型不只用于函数，也用于**类**。最经典的场景就是"一个容器类，装着某种类型的元素"：

```python
from typing import Generic, TypeVar

T = TypeVar("T")

class Box(Generic[T]):
    def __init__(self, item: T):
        self._item = item

    def get(self) -> T:
        return self._item

int_box: Box[int] = Box(42)          # 装着 int 的盒子
str_box: Box[str] = Box("hello")     # 装着 str 的盒子

n = int_box.get()    # n 是 int——检查器知道
s = str_box.get()    # s 是 str——检查器知道
```

`class Box(Generic[T])` 声明这是一个泛型类，`T` 是它的类型参数。使用时用 `Box[int]`、`Box[str]` 指定具体类型。

### 7.5 呼应学习目标——泛型化的 Response 设计

学习目标 1.4 里提过「泛型化 Schema 设计」，这里正好完整展开。不用泛型时，后端项目会为每个资源写几乎一样的响应结构：

```python
class UserResponse:
    data: User
    code: int
    message: str

class OrderResponse:
    data: Order
    code: int
    message: str

class ProductResponse:      # 每加一个资源，就复制粘贴一份
    data: Product
    code: int
    message: str
```

用 `Generic[T]` 一次性消灭这种重复：

```python
from typing import Generic, TypeVar

T = TypeVar("T")

class Response(Generic[T]):
    data: T
    code: int = 0
    message: str = "ok"

class PaginatedResponse(Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int
```

使用时按需实例化：

```python
user_resp: Response[User] = ...
order_resp: Response[Order] = ...
page: PaginatedResponse[Product] = ...
```

**一个 `Response[T]` 泛型，替代了所有 `xxResponse` 的重复定义**——这就是泛型省下的真实劳动，也是"能跑"和"工程化"之间的分界线。

---

## 八、结构化类型：`Protocol`

### 8.1 问题：鸭子类型丢失了"可检查性"

回顾 OOP 教程 4.2 的鸭子类型：

```python
def make_sound(animal) -> str:
    return animal.speak()    # 依赖"有 speak() 方法"这个隐含契约
```

问题在于：这个契约**只存在于程序员的脑子里**，检查器看不到。传错对象时，错误要等到运行时才 `AttributeError`。

`Protocol` 解决的就是这个：**把"结构契约"写出来，让鸭子类型变得可静态检查。**

### 8.2 `Protocol` 的用法

```python
from typing import Protocol

class Speaker(Protocol):
    def speak(self) -> str: ...

def make_sound(animal: Speaker) -> str:    # 标注协议，而非具体类
    return animal.speak()
```

`Protocol` 声明了一个**结构约定**：任何**拥有** `speak(self) -> str` 方法的类，都自动"满足" `Speaker` 协议——**不需要继承它**：

```python
class Dog:
    def speak(self) -> str:
        return "woof!"

class Cat:
    def speak(self) -> str:
        return "meow!"

>>> make_sound(Dog())    # ✅ 检查器认可——Dog 有 speak()
>>> make_sound(Cat())    # ✅ 检查器认可——Cat 有 speak()

def make_sound_wrong(x: Speaker) -> str:
    return x.speak()

>>> make_sound_wrong(42)    # ❌ mypy 报错：int 没有 speak 方法
```

这就是 **结构化类型（Structural Typing）** 的形式化：**类型由"有什么方法"决定，不由"继承自谁"决定**。`Protocol` 把鸭子类型从"运行时才发现"变成"写代码时就能验证"。

### 8.3 `Protocol` vs ABC——关键区别

| | ABC（`collections.abc`/自定义） | `Protocol` |
|---|---|---|
| 实现类要不要继承 | 要——必须显式继承才"是"它 | 不要——有方法就算满足 |
| 检查方式 | 运行时（实例化时拒绝） | 静态（检查器检查） |
| 是否创造运行时开销 | 有（metaclass、继承关系） | **无**——纯标注，运行时不存在 |

**核心区别一句话：** ABC 是"名义类型"（`isinstance(obj, ABC)` 靠继承关系），Protocol 是"结构类型"（看有没有方法，不看继承）。所以：

- 需要运行时 `isinstance` 检查、需要 mixin 默认实现 → 用 **ABC**；
- 只想给鸭子类型补上静态检查、不想强迫别人继承你的基类 → 用 **Protocol**。

`Protocol` 尤其适合**跨库协作**：你想约束"传入的对象必须有 `close()` 方法"，但那个对象来自第三方库、你不可能去改它的继承——这时 Protocol 就是唯一解。

---

## 九、类型化字典：`TypedDict`

### 9.1 问题：裸 `dict` 丢了键值结构信息

```python
def get_config() -> dict:
    return {"host": "localhost", "port": 8080}

cfg = get_config()
cfg["host"]       # 检查器不知道 "host" 这个键存在不存在、值是什么类型
cfg["hst"]        # 拼写错误——但检查器看不出来，运行时才 KeyError
```

裸 `dict` 是最灵活的，也是最容易出错的——**键名拼错、键值类型记错，检查器一概抓不到**。

`TypedDict` 解决的就是这个：给 dict 的**键值结构**打上标注。

### 9.2 `TypedDict` 的用法

```python
from typing import TypedDict

class Config(TypedDict):
    host: str
    port: int

def get_config() -> Config:
    return {"host": "localhost", "port": 8080}

cfg = get_config()
cfg["host"]           # ✅ 检查器知道 "host" 存在，值是 str
cfg["hst"]            # ❌ mypy 报错：TypedDict "Config" 没有 "hst" 键
cfg["port"] = "80"    # ❌ mypy 报错：port 应该是 int
```

### 9.3 `TypedDict` 的关键事实——它运行时就是普通 dict

**最重要的一点：`TypedDict` 在运行时不存在任何东西。**

```python
class Config(TypedDict):
    host: str
    port: int

>>> Config                # <class 'dict'>——TypedDict 就是个普通 dict
>>> isinstance({"a": 1}, Config)    # 返回 dict 的类型检查，没有 Config 这个类型
```

`TypedDict` 是**纯静态标注**：它只存在于类型检查器里，运行时不产生任何新类型、不产生任何校验。你甚至可以 `cfg["anything"] = 123` 而不报错（运行时），只是 mypy 会标红。

**因此它只适合"内部高频、彼此信任"的数据流转**（呼应学习目标 1.1 的三层划分）：

| 层级 | 工具 | 运行时校验 | 场景 |
|------|------|-----------|------|
| 定义数据结构 | `dataclass` | 否 | 程序内部自己构造 |
| 运行时数据流转 | **`TypedDict`** | 否 | 模块间传递，彼此信任 |
| 接口级数据流转 | `pydantic.BaseModel` | **是** | 外部输入（HTTP body、MQ、第三方 API） |

`TypedDict` 适合"两个内部函数之间传一个配置字典"——没必要花运行时校验的开销。但一旦数据来自外部输入（前端 JSON、消息队列），必须换 `pydantic.BaseModel` 做真正的运行时校验，否则脏数据会穿透到业务逻辑。

### 9.4 `TypedDict` 的细节：`total` 与可选键

默认所有键都是**必需的**。想让某些键可选，用 `total=False` 或 `NotRequired`：

```python
from typing import TypedDict, NotRequired    # 3.11+ 用 NotRequired

class Config(TypedDict):
    host: str
    port: int
    timeout: NotRequired[float]    # 可选键——可以不传
```

（Python 3.10 及以下用 `total=False` 声明整个 dict 的键都可选，或用 `typing_extensions` 的 `NotRequired`。）

---

## 十、携带元数据的标注：`Annotated`

### 10.1 在类型之外附加信息

有时你不仅想标注类型，还想在类型上**挂额外的元数据**——比如取值范围、单位、校验规则：

```python
from typing import Annotated

UserId = Annotated[int, "primary key"]
Port = Annotated[int, "0-65535"]

def connect(port: Port) -> None:
    ...
```

`Annotated[int, "0-65535"]` 的意思是：**类型是 `int`，附带一段元数据 `"0-65535"`**。类型检查器只认第一个参数（`int`），后面的元数据对检查器是透明的。

### 10.2 `Annotated` 的真正威力——配合 pydantic 做运行时校验

`Annotated` 单独用意义不大，它的价值在于**让运行时校验框架（pydantic）读到元数据**：

```python
from typing import Annotated
from pydantic import BaseModel, Field

class User(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=50)]
    age: Annotated[int, Field(ge=0, le=150)]
    email: Annotated[str, Field(pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$")]
```

这里 `Annotated[str, Field(...)]` 把**类型**（`str`）和**校验约束**（`Field`）绑在一起：类型检查器看到 `str`，pydantic 在运行时读到 `Field` 的约束并真正校验。

**`Annotated` 的本质：** 它是"类型的容器"——第一项永远是真实类型，后面任意项是给不同工具消费的元数据。类型检查器消费第一项，pydantic 消费 `Field`，其他工具可以消费别的。这让你能**在一个标注上叠加多层语义**，而不是为每种语义造一个类型。

---

## 十一、`Self` 与 `Never`

### 11.1 `Self`——方法返回"当前类型"

一个常见的场景：方法返回 `self`，用于**链式调用**（fluent API）：

```python
class Builder:
    def set_name(self, name: str) -> Builder:    # ❌ 写死 Builder 有隐患
        self._name = name
        return self

    def set_age(self, age: int) -> Builder:
        self._age = age
        return self
```

问题在哪？当子类继承 `Builder` 时：

```python
class UserBuilder(Builder):
    def set_role(self, role: str) -> UserBuilder:
        self._role = role
        return self

UserBuilder().set_name("a").set_role("admin")
#                  ↑ 返回 Builder 类型，检查器认为没有 set_role 方法！
```

`set_name` 标注返回 `Builder`，所以链式调用时检查器认为后面只能调 `Builder` 的方法，`set_role` 会报错——但运行时它明明存在。

**`Self`（Python 3.11+）解决的就是"返回当前类型"**：

```python
from typing import Self

class Builder:
    def set_name(self, name: str) -> Self:    # ✅ 返回"调用它的那个类型"
        self._name = name
        return self

    def set_age(self, age: int) -> Self:
        self._age = age
        return self

class UserBuilder(Builder):
    def set_role(self, role: str) -> Self:
        self._role = role
        return self

UserBuilder().set_name("a").set_role("admin")
#                  ↑ 现在返回 UserBuilder，set_role 能正常补全
```

`Self` 表示"**当前这个类的类型**"，子类调用时它自动变成子类类型——链式调用在继承体系里也能正确工作。这是 fluent API、builder 模式在类型层面的标准解法。

### 11.2 `Never`——"这个函数不会正常返回"

有些函数**永远不会返回**——要么抛异常，要么无限循环：

```python
from typing import Never    # 3.11+；3.10 及以下从 typing_extensions 导入

def fail(message: str) -> Never:
    raise RuntimeError(message)

def halt() -> Never:
    while True:
        pass
```

`Never` 是**底部类型（bottom type）**——它表示"没有任何值属于这个类型"。它的实际价值在于**让检查器做不可达代码分析**：

```python
def process(x: int | None) -> int:
    if x is None:
        fail("x 不能是 None")     # fail 返回 Never——检查器知道这之后不会继续执行
    return x + 1                   # 这里检查器确认 x 不是 None（因为 None 分支已"退出"）
```

因为 `fail` 标注了 `-> Never`，检查器知道 `if x is None` 分支调用 `fail` 后**不会返回**，所以后面 `x + 1` 时 `x` 已经确定是 `int`（`None` 的可能已被排除）——这正好是第十二节讲过的**类型收窄（narrowing）**的配合。

---

## 十二、类型收窄（Narrowing）——检查器如何"读懂"你的分支

前面多个地方都出现了"检查器知道你判空后就不是 None 了"，这里把机制讲清楚。

### 12.1 什么是类型收窄

**类型收窄**：检查器根据你的控制流（`if`、`isinstance` 等）**自动缩小**变量的可能类型范围。

```python
def process(x: int | str) -> str:
    if isinstance(x, int):        # 进入这个分支，x 被"收窄"为 int
        return str(x + 1)         # ✅ x 是 int
    else:
        return x.upper()          # ✅ 这里 x 被收窄为 str
```

检查器不需要你手动 `cast`——它**自己追踪** `isinstance` 分支，知道 `if` 里面 `x` 是 `int`、`else` 里 `x` 是 `str`。

### 12.2 常见的收窄手段

```python
def handle(value: int | None) -> int:
    # 手段一：is None / is not None
    if value is None:
        return 0
    return value + 1        # 收窄为 int

def handle2(obj: object) -> str:
    # 手段二：isinstance
    if isinstance(obj, str):
        return obj.upper()   # 收窄为 str
    return str(obj)

# 手段三：真值判断（但要小心 0、"" 这些假值）
def handle3(x: int | None) -> int:
    if x:                    # 收窄掉 None 和 0
        return x
    return 0
```

### 12.3 收窄失效的陷阱

**陷阱一：赋值后收窄失效。** 检查器只在**它看得懂**的情况下收窄，如果变量被函数调用"污染"，收窄会丢失：

```python
def process(x: int | None) -> int:
    if x is None:
        return 0
    some_function()        # 检查器保守起见——不知道 some_function 有没有改 x
    return x + 1           # ⚠️ 某些情况下检查器仍报 x 可能为 None
```

（实际上闭包变量捕获 `x` 会被检查器视为"可能被修改"，导致收窄失效——这是新手常困惑的点。）

**陷阱二：`isinstance` 才能精确收窄，`==` 不行。** 用 `type(x) == int` 或 `==` 比较，检查器通常**不能**正确收窄，因为它不保证运行时行为——统一用 `isinstance`。

**核心价值：** 类型收窄是类型系统"读懂你的意图"的体现——你写正常的防御性判断（判空、判类型），检查器就自动帮你排除掉错误分支，不需要任何额外标注。

---

## 十三、工具：mypy 与 pyright

类型标注写完了，谁来检查？两个主流工具。

### 13.1 mypy——事实标准

**mypy** 是 Python 类型检查的事实标准，由 Python 官方（Guido 参与）维护：

```bash
# 安装
pip install mypy

# 检查单个文件
mypy my_module.py

# 检查整个项目
mypy src/

# 严格模式——最严的检查，适合新项目
mypy --strict src/
```

**mypy 的配置**（`pyproject.toml`）：

```toml
[tool.mypy]
python_version = "3.11"
strict = true              # 严格模式：隐式 Optional 也报错、禁止未标注的函数
disallow_untyped_defs = true    # 禁止未标注的函数定义
warn_return_any = true          # 返回 Any 时警告
```

**关键概念——mypy 是"渐进式"的：** 你不需要一次性给整个项目标注完。mypy 允许**逐步推进**——先标核心模块，检查通过，再扩大范围。未标注的部分 mypy 默认放行（除非开了 `strict`）。这让"给已有项目加类型"这件事变得可行。

### 13.2 pyright——微软出品，IDE 友好

**pyright** 是微软出品，特点是**速度快**（用 TypeScript 写的，增量检查）、**IDE 集成好**（VS Code 的 Pylance 就是 pyright 的引擎）：

```bash
pip install pyright
pyright src/
```

pyright 和 mypy 的核心能力相似，选型经验：

| | mypy | pyright |
|---|---|---|
| 维护方 | Python 官方/社区 | 微软 |
| 速度 | 较慢（全量分析） | 快（增量） |
| IDE 集成 | 需要插件 | 原生（Pylance 内核） |
| 严格性默认 | 适中 | 更严格 |
| 生态/插件 | 更成熟 | 增长快 |

**学习目标里 mypy 是必学、pyright 是了解**——把 mypy 用好即可，pyright 知道它存在、知道它是 VS Code Pylance 的内核就够。

---

## 十四、Project 3：给已有项目做 100% 类型标注

### 14.1 项目目标

学习目标要求：**把一个已有项目做到 100% 类型标注，并通过 mypy 检查。**

"已有项目"可以直接用上一章的**插件系统**（`plugin_system/`），它已经有一部分标注了（`Document`、`Extractor`、异常体系里都有标注），正好作为练习对象。

### 14.2 正确的推进顺序（重要）

不要试图"一次性全标完"，那是放弃的前奏。渐进式推进：

**第 1 步：开严格检查，看基线。**

```bash
cd 示例代码/plugin_system
mypy --strict src/doc_extractor/
```

先跑一次，看看**当前有多少个错误**——这是你的起点。别被错误数量吓到，渐进式推进本来就是"从 50 个错减到 0"。

**第 2 步：从"叶子"开始，从下往上标。**

先标**没有依赖的底层模块**（`document.py`、`exceptions.py`），再标依赖它们的上层（`reader.py`、`registry.py`、`loader.py`），最后标入口（`extractor.py`、`__main__.py`）。这样每标完一层，mypy 的报错会随之减少，而不是互相纠缠。

**第 3 步：消灭 `Any`。**

全项目搜 `Any`，逐个判断：真动态的（如 `json.loads` 结果）保留，偷懒的（能推断出具体类型的）改成精确类型。这一步最能体现"类型标注的质量"，而不只是"有没有标注"。

**第 4 步：处理难啃的泛型。**

插件系统里 `Registry` 存的是 `type[DocumentReader]`（见 1.4 节）、`loader.py` 返回 `list[ModuleType]`、`extractor._reader_for` 返回 `DocumentReader`——这些是体现你泛型/协议功力的地方。遇到 `Protocol`、`Generic` 的场景，用本教程第七、八节的知识精确标注。

**第 5 步：mypy 零错误通过。**

```bash
mypy --strict src/doc_extractor/
# Success: no issues found in N source files
```

### 14.3 验收标准（毕业标准）

1. **全项目零 `Any`**（除 `json.loads` 这类真动态场景，且要有注释说明为什么）。
2. **`mypy --strict` 零错误**——严格模式通过，不是默认模式。
3. **所有函数都有完整的参数 + 返回值标注**——不允许 `disallow_untyped_defs` 下的漏标。
4. **协议和泛型用对**——`Registry` 用 `Protocol`/ABC 精确标注，`extract_many` 的返回值是 `list[Document]` 而非 `list`。
5. **IDE 里无类型报错**——在 VS Code/PyCharm 里打开项目，不应该有红色波浪线（类型错误）。

---

## 十五、全章速查表

| 知识点 | 一句话要点 |
|--------|----------|
| 类型标注的本质 | 改变"检查时机"（写代码时 vs 运行时），**不影响运行行为** |
| `Union` / `\|` | 多种类型之一——`int \| float`（`\|` 语法需 3.10+） |
| `Optional` | "可能是 None"——`User \| None`，逼调用方判空 |
| `Any` | 类型系统的逃生舱——双向可赋、彻底不检查，滥用则检查归零 |
| `Literal` | 有限字面量作为类型——`Literal["read", "write"]` |
| `Final` | 标记"不可重新赋值"——静态约定，运行时**不**强制 |
| `Callable` | 描述函数类型——`Callable[[int], int]`（参数列表 + 返回类型） |
| `TypeAlias` | 给类型起别名——显式标记消除"类型 vs 变量"歧义 |
| `NewType` | 创造静态新类型区分语义——运行时是零开销恒等函数 |
| `TypeVar` | 类型变量——`T = TypeVar("T")`，建立入参/返回的类型关联 |
| `Generic` | 泛型类——`class Box(Generic[T])`，`Box[int]` 指定类型 |
| `Protocol` | 结构化类型——有方法就算满足，**不需继承**，运行时零开销 |
| `TypedDict` | 给 dict 键值结构打标注——运行时就是普通 dict，无校验 |
| `Annotated` | 类型 + 元数据——`Annotated[int, Field(...)]` 供 pydantic 等消费 |
| `Self` | 返回"当前类型"——链式调用在继承下正确（3.11+） |
| `Never` | 底部类型——"不返回"的函数，配合收窄做不可达分析 |
| 类型收窄 | 检查器根据 `isinstance`/`is None` 自动缩小类型范围 |
| mypy | 事实标准检查器——`--strict` 严格模式，渐进式推进 |
| pyright | 微软出品——快、IDE 集成好，是 VS Code Pylance 内核 |
| 三层数据模型 | `dataclass`（内部结构）/ `TypedDict`（内部流转）/ `pydantic`（外部输入） |

---

## 十六、一条贯穿全章的判断

学完这些工具，最后记住一条贯穿全章的心法：

> **类型标注是"给工具写契约"，不是"给运行时加护栏"。**

- 想要**写代码时**就抓住错误（拼错键、传错类型、忘判空）→ 用本教程的标注工具 + mypy。
- 想要**运行时**拦住脏数据（外部输入不可信）→ 用 pydantic 的运行时校验（`Annotated` + `Field` 是两者的桥）。
- 两者**不冲突、也不互相替代**——一个管"程序员自己写错的"，一个管"外部世界传来的脏东西"。

类型系统替你承担了"记住每个变量类型"的认知负担，好让你把脑子省下来，花在真正难的逻辑上。这才是它的全部价值。
