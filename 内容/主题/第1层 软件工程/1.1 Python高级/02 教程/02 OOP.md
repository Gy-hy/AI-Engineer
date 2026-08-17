# OOP（★★★★★）

> **目标：理解 Python 面向对象编程的完整机制——不只是语法，而是 class 的运行时行为、属性和方法的底层模型、封装在 Python 中的实际含义。**

---

## 一、类

### 1.1 `class` —— 创建类的语句

#### 是什么

`class` 是 Python 中**在运行时创建类型对象**的语句。当你写下：

```python
class Dog:
    species = "Canis familiaris"

    def __init__(self, name):
        self.name = name

    def bark(self):
        return f"{self.name} says woof!"
```

Python 做了三件事：

1. **执行 class body**——在 `class` 缩进块内的代码（`species = ...`、`def __init__`、`def bark`）会像一个函数体一样被执行，但运行在一个**独立的局部命名空间**中。
2. **收集命名空间**——执行完后，把这个局部命名空间中的所有名字打包成一个 dict。
3. **调用元类创建类对象**——把这个 dict 传给 `type(name, bases, namespace)`（默认元类是 `type`），返回一个类对象，然后把这个类对象绑定到 `Dog` 这个名字。

所以 `class Dog` **不是编译时的声明**，而是运行时的执行语句。这意味着你可以在 `if` 里定义类、在函数里定义类——类定义本身也是可执行代码。

```python
# 运行时条件定义类——合法的（虽然很少需要）
if use_debug_version:
    class Dog:
        def bark(self):
            return "DEBUG: woof"
else:
    class Dog:
        def bark(self):
            return "woof"
```

#### 类本身是对象

这是 1.1 Python 高级里"一切皆对象"的直接延伸：**类本身是 `type` 的实例**。这意味着：

```python
>>> type(Dog)            # <class 'type'>
>>> Dog.__bases__        # (<class 'object'>,)——默认继承自 object
>>> Dog.__dict__         # mappingproxy——类的命名空间，装着 species、__init__、bark
>>> Dog.__name__         # 'Dog'
>>> hasattr(Dog, "bark") # True——类属性可以被 hasattr 检查
```

这也是为什么你能给类动态挂属性、能 `isinstance(obj, type)` 检查一个东西是不是类——因为类就是普通的 Python 对象，只不过它的类型是 `type`。

---

### 1.2 `instance` —— 实例

#### `__init__` 不是构造函数

看到 `__init__` 这个名字，很多人以为它是 constructor（构造函数）。**它不是。**

Python 中真正的"创建对象"方法是 `__new__`——它是一个静态方法（即使没加 `@staticmethod` 装饰器），负责分配内存并返回一个新的实例对象。**`__init__` 只是初始化器**——它在 `__new__` 返回的对象上设置初始状态。

```python
# __new__ → __init__ 的调用顺序
class Example:
    def __new__(cls, *args, **kwargs):
        print("1. __new__ called——分配对象")
        instance = super().__new__(cls)   # 实际分配内存并创建对象
        return instance                    # 必须返回一个实例

    def __init__(self, value):
        print("2. __init__ called——初始化对象")
        self.value = value

>>> e = Example(42)
# 1. __new__ called——分配对象
# 2. __init__ called——初始化对象
```

**关键合约：**

- `__new__` 必须返回一个实例（通常是 `cls` 的实例，但也可以是其他任何对象——只是没人这么做除非你在写一种非常奇怪的模式）。如果 `__new__` 返回的不是 `cls` 的实例，`__init__` **不会被调用**。
- `__init__` 必须返回 `None`——返回任何其他值都会引发 `TypeError`。
- `__new__` 的 `cls` 参数是类本身（被自动传入，和 `self` 一样是隐式的）；`__init__` 的 `self` 是 `__new__` 返回的那个实例。

**为什么几乎从来不需要覆盖 `__new__`：** 只有在需要控制"创建什么类型的对象"或"创建后能不能被修改"时才需要——最典型的就是单例模式（`__new__` 总是返回同一个实例）和不可变类型的子类（`str`、`int`、`tuple` 的子类，值在 `__new__` 时确定，因为 `__init__` 时已经不能改了）。

#### `type` 调用等价于 `__new__` + `__init__` 的组合

有一个常见的误解是 `Circle(radius=5)` 直接调用 `__init__`。实际上 Python 的解释机制是：

```python
# Python 把 Circle(radius=5) 翻译成：
# 1. instance = Circle.__new__(Circle, radius=5)   # 创建
# 2. if isinstance(instance, Circle):               # 检查类型
# 3.     instance.__init__(radius=5)                # 初始化
# 4. return instance                                # 返回
```

其中第 1 步 `Circle.__new__(Circle)` 等价于 `object.__new__(Circle)`（没覆盖 `__new__` 时），它调用 C 层面的内存分配，返回一个"空壳"对象——这个空壳还没有任何实例属性。

步骤 2 的类型检查很关键：如果你不小心在 `__new__` 里返回了一个**别的类型**的对象，`__init__` 就被静默跳过了。这就是"单例返回已有实例"等工作方式的基础——`__new__` 返回缓存的对象，`__init__` 不被二次调用。

---

### 1.3 `attribute` —— 属性

#### 实例属性 vs 类属性——这是 Python 里最经典的区分之一

```python
class Dog:
    species = "Canis familiaris"    # 类属性——共享

    def __init__(self, name):
        self.name = name             # 实例属性——每个实例独有
```

**类属性**绑定在类对象上，存储在 `Dog.__dict__` 中，所有实例共享同一个值。

**实例属性**绑定在实例对象上，存储在 `instance.__dict__` 中，每个实例各自独立。

```python
>>> d1 = Dog("Rex")
>>> d2 = Dog("Buddy")
>>> d1.species   # "Canis familiaris"——从类属性读的
>>> d2.species   # "Canis familiaris"——同上
>>> Dog.species = "Canis lupus"   # 改类属性
>>> d1.species   # "Canis lupus"——所有实例都看到了
>>> d2.species   # "Canis lupus"
```

**陷阱——通过实例给类属性赋值：**

```python
>>> d1.species = "custom species"   # 这不会改类属性！这是给 d1 创建了一个实例属性！
>>> d1.species      # "custom species"——d1 自己的实例属性，遮盖了类属性
>>> d2.species      # "Canis lupus"——d2 没有实例属性，还是从类读取
>>> Dog.species     # "Canis lupus"——类属性完全没变
```

背后的机制是**属性查找规则（3.3 节的细节）**：

1. 先找 `instance.__dict__`
2. 再找 `type(instance).__dict__` 及其 MRO 链

当你写 `d1.species = "custom species"` 时，Python 在执行**属性赋值**而非查找——赋值直接写进 `d1.__dict__`，所以创建了一个实例属性 `species`，和类属性的 `species` 是两个完全独立的键。之后再读 `d1.species` 时，步骤 1 就命中了实例属性，步骤 2 的类属性永远不会被看到——这叫**遮盖（shadowing）**。

#### 属性查找的完整机制

读 `obj.name` 和写 `obj.name = value` 走的是两条不同的路径：

**读（get）：**

```
1. data descriptor?  → type(obj).__dict__[name] 且该 descriptor 有 __set__
                       → 调用 descriptor.__get__(obj, type(obj))
2. instance dict?    → obj.__dict__[name]
3. non-data descriptor? → type(obj).__dict__[name] 且有 __get__
                       → 调用 descriptor.__get__(obj, type(obj))
4. class attribute?  → type(obj).__dict__[name]
5. MRO 链上的父类?  → 沿 type(obj).__mro__ 逐个查找
6. __getattr__?      → 兜底——只有以上全部失败才调用
```

**写（set）：**

```
1. data descriptor?  → type(obj).__dict__[name] 且有 __set__
                       → 调用 descriptor.__set__(obj, value)——不碰实例 dict
2. 否 → obj.__dict__[name] = value——直接写进实例 dict
```

这个"读写不对齐"的设计解释了之前说的 `d1.species = "custom"` 为什么是创建实例属性——step 2 直接写进 `obj.__dict__`，类属性根本没被问到。

**这也是 `property` 工作的基础**——`property` 是一个 data descriptor（同时有 `__get__` 和 `__set__`），所以赋值时 descriptor 的 `__set__` 拦截了操作，值不会进实例 dict。

---

### 1.4 `method` —— 方法

#### 方法就是碰巧在类里的函数

```python
class Dog:
    def bark(self):
        return f"{self.name} says woof!"
```

`bark` 在类字典里存的是**一个普通的 function 对象**。它之所以变成 method，是因为 **descriptor 协议**。

当你写 `d1.bark` 时，Python 查找过程是：

1. 在 `d1.__dict__` 里找 `bark`——找不到。
2. 在 `Dog.__dict__` 里找 `bark`——找到了，是一个 function 对象。
3. function 对象实现了 `__get__` 方法（它是一个 non-data descriptor）。所以 Python 调用 `function.__get__(d1, Dog)`。
4. `__get__` 返回一个 **bound method 对象**——把 `d1` 绑定为 `self`。
5. `d1.bark()` 调用这个 bound method，Python 自动把绑好的 `self` 作为第一个参数传入。

```python
# 完整的等价关系
>>> d1 = Dog("Rex")
>>> d1.bark                          # <bound method Dog.bark of <Dog object>>
>>> Dog.bark                         # <function Dog.bark>——没绑定，就是普通函数
>>> Dog.bark(d1)                     # "Rex says woof!"——手动传 self 也是合法的
```

**`self` 不是关键字——是约定：**

```python
class Example:
    def method(this_doesnt_have_to_be_called_self):
        return this_doesnt_have_to_be_called_self

# 可以工作——但不应该这么做。任何 Python 工程师看到非 self 的第一个参数名
# 都会认为这有特殊的含义。遵守约定。
```

#### Bound method 的内部

bound method 是一个轻量对象，只存了两个引用：

- `__func__`：原始 function 对象
- `__self__`：绑定的实例

```python
>>> bm = d1.bark
>>> bm.__func__       # <function Dog.bark>
>>> bm.__self__       # <Dog object at 0x...>
>>> bm.__func__(bm.__self__)   # 等价于 bm()
```

这就是为什么 bound method 可以作为回调传递——它自带了 `self`，调用方不需要传：

```python
>>> methods = [d1.bark, d2.bark]
>>> for m in methods:
...     print(m())
# Rex says woof!
# Buddy says woof!
```

每个 bound method 各自绑定了不同的 `__self__`，调用时自动传正确的实例。

#### 类方法、静态方法、实例方法——一张表区分

| | 实例方法 | `@classmethod` | `@staticmethod` |
|---|---|---|---|
| 定义 | `def m(self):` | `def m(cls):` | `def m():`（没有隐式参数） |
| 绑定的对象 | 实例（`self`） | 类（`cls`） | 不绑定 |
| 通过实例调用 | `obj.m()`，`self` 自动传入 | `obj.m()`，`cls` 自动传入 | `obj.m()`，无隐式参数 |
| 通过类调用 | `C.m(obj)`，手动传实例 | `C.m()`，`cls` 自动传入 | `C.m()`，无隐式参数 |
| 典型用途 | 操作实例数据 | 工厂方法、替代构造器 | 和类相关的工具函数，但不碰实例/类数据 |

```python
class Dog:
    species = "Canis familiaris"

    def __init__(self, name):
        self.name = name

    def bark(self):                    # 实例方法
        return f"{self.name} says woof!"

    @classmethod
    def from_dict(cls, data):          # 类方法——替代构造器
        return cls(data["name"])

    @staticmethod
    def is_valid_name(name):           # 静态方法——纯工具
        return isinstance(name, str) and len(name) > 0
```

**`@classmethod` 的真正价值不在"能读类属性"——实例方法也能通过 `type(self).species` 读。它的价值在于多态：** 子类调用 `cls()` 会创建子类的实例，而不是父类实例。这是工厂方法模式在 Python 中的标准实现。

**`@staticmethod` 几乎不做任何事情**——它只是一个普通的函数，恰好位于类的命名空间中。如果一段逻辑既不碰 `self` 也不碰 `cls`，可以考虑：它真的需要放在这个类里吗？还是应该作为模块级函数？

---

### 1.5 类体在定义时就执行了——不是声明性的

这一点非常关键，却被大多数 OOP 教程忽略：

```python
>>> class Demo:
...     print("Class body executing!")    # 定义时立即执行
...     items = []
...     for i in range(3):
...         items.append(i)
...
# Class body executing!
>>> Demo.items    # [0, 1, 2]
```

类体是可执行语句的堆叠——不只是 `def` 和赋值，任何语句（`print`、`for`、条件判断）都可以放在类体里，而且会在类定义时立即执行。

**实际应用：** 这是元类（metaclass）和 `__init_subclass__` 能作用于类定义的前提——类体先执行，收集命名空间，然后命名空间传给元类。

---

### 1.6 总结

| 知识点 | 一句话要点 |
|--------|----------|
| class | `class` 是运行时语句——执行类体、收集命名空间、传给 `type` 创建类对象 |
| instance | `__new__` 创建对象（真正的构造器），`__init__` 初始化对象；`__new__` 如果返回非 cls 实例则 `__init__` 不调用 |
| instance attribute | 存在 `instance.__dict__`，每个实例独立；赋值直接进实例 dict |
| class attribute | 存在 `Class.__dict__`，所有实例共享；通过实例赋值会创建实例属性遮盖类属性 |
| attribute lookup | 读：data descriptor → instance dict → non-data descriptor → class dict → MRO → `__getattr__`；写：data descriptor 的 `__set__` 直接拦截，否则进 instance dict |
| method | 函数通过 descriptor 协议变成 bound method——`function.__get__(instance)` 返回绑定好 `self` 的 method 对象 |
| `self` | 不是关键字——是约定；第一个参数名可以叫任何名字但不应该 |
| classmethod | 绑定 `cls` 而非 `self`——工厂方法的标准实现，真正价值在子类多态 |
| staticmethod | 不绑定的普通函数——如果既不碰 self 也不碰 cls，考虑是否该移出类 |

---

## 二、封装

### 2.1 Python 的封装哲学：信任，不强制

C++/Java 的封装靠编译器强制执行——`private` 就是编译器拒绝让你访问，绕不过去。Java 里通过反射可以绕，但至少名义上编译器会挡你。

**Python 没有访问控制。** 所有属性和方法在运行时都是可访问的。Python 的答案是**约定（convention）**而非**强制（enforcement）**：

> "We're all consenting adults here."
> — Python 社区格言

这不是 Python 的设计缺陷，而是一个明确的设计选择：**语言不替你判断谁能访问什么，但社区有明确的命名约定来表达意图。** 想违反约定？可以——但你应该清楚自己在干什么，后果自负。

Python 通过**一个下划线**和**两个下划线**这两种前缀来表达"这个属性/方法有多 '内部' "，而不是"这个属性/方法有多 '不能碰' "。

---

### 2.2 `public` —— 没有下划线

没有任何下划线前缀的名字就是公共的——它是类/模块的公开 API，外部代码可以自由使用。

```python
class BankAccount:
    def __init__(self, owner: str, balance: float):
        self.owner = owner          # public
        self.balance = balance      # public——你希望调用者直接读写
```

`owner` 和 `balance` 没有任何前缀——它们是 public。没有需要解释的东西，因为它就是默认行为。

**什么时候用 public：** 当这个属性就是类对外承诺的接口的一部分时。如果改了它会导致类的行为不正常，那它不应该叫 "为了让你方便而 public" —— 阅读下一节。

---

### 2.3 `_protected` —— 单下划线前缀

#### 约定含义

`_name` 形式的单下划线前缀是 Python 社区的约定，表达**"这是内部实现细节，不是公开 API 的一部分；外部可以用，但如果它在下个版本变了甚至消失了，别来找我"**。

```python
class BankAccount:
    def __init__(self, owner: str, balance: float):
        self.owner = owner
        self._balance = balance     # protected——别直接碰，用我提供的 public 方法

    def deposit(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("deposit amount must be positive")
        self._balance += amount

    def withdraw(self, amount: float) -> None:
        if amount > self._balance:
            raise ValueError("insufficient funds")
        self._balance -= amount

    def get_balance(self) -> float:
        return self._balance
```

`_balance` 带了一个下划线，告诉读代码的人：**"你可以读我、可以写我，但如果你直接碰 `obj._balance` 而不是走 `deposit`/`withdraw`，你绕过了校验逻辑——出了 bug 是你自己的问题。"**

**Python 不会阻止你直接访问它：**

```python
>>> acc = BankAccount("Alice", 100.0)
>>> acc._balance            # 100.0——可以读
>>> acc._balance = -99999   # 可以写——绕过了 withdraw 的校验
>>> acc.get_balance()       # -99999——你的代码坏了，但这不怪 Python
```

在 Java 里这种场景会设成 `private` 然后用 `getBalance()`/`setBalance()` 来控制。Python 的哲学是：**用一个下划线表明"这内部"，然后信任调用者足够专业、不会故意走捷径。** 如果调用者硬要走捷径，那他们自己承担后果。

#### 实际效果——不只是文档

单下划线前缀虽然没有运行时强制，但它有几项**实际的行为后果**，不只是意图表达：

**(a) `from module import *` 不会导入 `_name`**

```python
# bank.py
__all__ = ["BankAccount"]   # 显式指定公开 API（覆盖 * 导入的行为）

class BankAccount:
    ...
```

如果没有定义 `__all__`，`from bank import *` 默认不导入任何以 `_` 开头的名字。所以 `_balance` 不会污染导入方的命名空间——这是 Python 语言规范里写明的行为，不是惯例。

但注意：`from module import _name` 仍然可以显式导入——`import *` 会跳过下划线名字，显式导入不会。

**(b) IDE 和 linter 会警告**

在 PyCharm/VS Code 中，从外部模块访问 `obj._protected` 时，IDE 通常会提示"Access to a protected member"。这是工具链层面的"软强制"——代码能跑，但你的 IDE 会一直提醒你"你在碰不该碰的东西"。

**(c) `help()` 和文档生成工具**

一些文档生成工具（如 Sphinx 的 autodoc）默认跳过 `_` 前缀的成员，不在文档中展示它们。这进一步强化了"内部实现细节，不影响公开 API"的语义。

---

### 2.4 `__private` —— 双下划线前缀（Name Mangling）

#### 是什么

`__name` 形式（双下划线前缀，最多一个后缀下划线）触发 **name mangling（名字改写）**。

```python
class BankAccount:
    def __init__(self, owner: str, balance: float):
        self.owner = owner
        self.__balance = balance    # 双下划线——触发 name mangling

    def get_balance(self):
        return self.__balance       # 在类体内访问——会自动改写
```

Name mangling 的规则很简单：`__balance` 在类体内被 Python 自动改写为 `_BankAccount__balance`（单下划线 + 类名 + 双下划线原名）。

```python
>>> acc = BankAccount("Alice", 100.0)
>>> acc.__dict__
# {'owner': 'Alice', '_BankAccount__balance': 100.0}
#                       ^^^^^^^^^^^^^^^^^^^^^^^^ 注意实际存储的键名
>>> acc.__balance            # AttributeError——这个名字不存在
>>> acc._BankAccount__balance  # 100.0——这才是实际名字
```

**但 Python 仍然不会阻止你访问它：**

```python
>>> acc._BankAccount__balance = -99999   # 仍然可以——如果你知道改写后的名字
```

Name mangling 的目标**不是安全**——它不阻止任何人访问。它的目标是**防止子类意外覆盖**：

```python
class Parent:
    def __init__(self):
        self.__internal = "parent's internal"   # 实际存为 _Parent__internal

class Child(Parent):
    def __init__(self):
        super().__init__()
        self.__internal = "child's internal"    # 实际存为 _Child__internal——完全不同的键！
```

子类的 `__internal` 被改写为 `_Child__internal`，父类的被改写为 `_Parent__internal`——两者是**不同的属性**，不会互相覆盖。这就是 name mangling 的唯一目的：**在多继承和复杂继承体系中，防止子类无意间覆盖父类的关键内部属性。**

#### 不应该用 `__` 的情况

**误区：用 `__` 来"保护"数据、防止外部访问。** Name mangling 不是为了这个。大多数人用 `__` 是因为从 Java/C++ 带过来的直觉——"private 就是别人不能碰"——这是 Python 里最常见的误用之一。

```python
# ❌ 错误——用 __ 企图"保护"数据
class Bad:
    def __init__(self, value):
        self.__value = value   # 写的人以为：别人不能碰我的 value

    def get_value(self):
        return self.__value

# 实际上这完全没有保护——任何调用者都可以：
>>> obj = Bad(42)
>>> obj._Bad__value = 999   # 绕过了

# 而且还让调试和测试更麻烦：
>>> obj.__value   # AttributeError——调试时多了一个无意义的障碍
```

```python
# ✅ 正确——用 _ 表达"内部实现细节，别碰"
class Good:
    def __init__(self, value):
        self._value = value    # 单下划线就够了——表达意图，不添障碍

    def get_value(self):
        return self._value
```

**用 `__` 的合理场景：**
- 你写的类会被广泛地被子类化，而某个属性对类的内部正确性至关重要——子类如果覆盖它会导致父类逻辑崩溃。这时 `__` 的 name mangling 提供了命名空间隔离。
- 典型例子：框架/库的基类里的内部控制状态。

**大多数应用代码都不需要 `__`。** 单下划线 `_` 足够表达"内部实现"的意图了。

---

### 2.5 多下划线约定的速查表

| 形式 | 命名法 | 行为 | 意图 |
|------|--------|------|------|
| `name` | 无下划线 | `obj.name` 直接访问 | 公开 API——调用者可以自由使用 |
| `_name` | 单下划线前缀 | `obj._name` 可访问；`import *` 不导入 | 内部实现细节——别碰，碰了后果自负 |
| `__name` | 双下划线前缀 | `obj._Class__name` 可访问（name mangling） | 防止子类意外覆盖——不是安全机制 |
| `__name__` | 双下划线前后缀 | `obj.__name__` 可访问，不触发 mangling | Python 语言的魔术方法/特殊属性——不要自己发明这种名字 |
| `name_` | 单下划线后缀 | `obj.name_` 可访问 | 避开 Python 关键字冲突——`class_`、`type_`、`import_` |

**注意：** `__name__` 是 Python 保留给语言内部使用的命名形式（如 `__init__`、`__repr__`、`__dict__`）。你**不应该**为自己的属性/方法创建这种名字——Python 的未来版本可能定义新的 `__magic__` 名字，会和你的冲突。这不是"规范建议"——PEP 8 明确禁止。

---

### 2.6 `@property` —— Python 封装的标准姿势

#### 问题：如果 `_balance` 是内部实现，调用者怎么获取它？

回到上面的例子：

```python
class BankAccount:
    def __init__(self, owner: str, balance: float):
        self.owner = owner
        self._balance = balance

    def get_balance(self):          # Java 风格——在 Python 里很丑
        return self._balance

    def set_balance(self, value):   # Java 风格——更丑
        if value < 0:
            raise ValueError
        self._balance = value
```

这种 `get_xxx` / `set_xxx` 模式是从 Java 平移过来的，在 Python 里**不 Pythonic**。调用代码看起来像：

```python
acc.get_balance()    # 方法调用——读一个值为什么要加括号？
acc.set_balance(50)  # 方法调用——赋一个值为什么像在调函数？
```

而 Python 的方式是 `@property`——让你可以用**属性访问的语法**来执行**方法调用**：

```python
class BankAccount:
    def __init__(self, owner: str, balance: float):
        self.owner = owner
        self._balance = balance

    @property
    def balance(self) -> float:          # getter——acc.balance 就像读属性
        return self._balance

    @balance.setter
    def balance(self, value: float):     # setter——acc.balance = 50 就像写属性
        if value < 0:
            raise ValueError("balance cannot be negative")
        self._balance = value
```

```python
>>> acc = BankAccount("Alice", 100.0)
>>> acc.balance          # 100.0——读属性（实际调用了 getter）
>>> acc.balance = 50     # 调用了 setter——校验通过
>>> acc.balance = -10    # ValueError: balance cannot be negative——校验被触发了
```

**关键好处：** 调用方的代码写法完全不变——`acc.balance` 读和 `acc.balance = x` 写。如果未来需要在读/写时加入校验、缓存、日志、触发通知，你只需要改 property 方法的内部实现，对外 API 没有任何变化。这和 Java 的"一开始就要写 getter/setter 否则将来没法改 API"是同样的需求，但 Python 的 `@property` 让你可以**先写成朴素的 public 属性，将来在需要时再无缝替换成 property**——调用方代码零修改。

#### `@property` 的底层——它是个 descriptor

回到 1.3 节的属性查找流程：`property` 是一个 **data descriptor**（同时实现了 `__get__`、`__set__`、`__delete__`）。这就是为什么它能在读写时拦截属性访问。

```python
# property 的等价手动实现（简化版）——只是为了理解它的内部机制
class Property:
    def __init__(self, fget=None, fset=None):
        self.fget = fget
        self.fset = fset

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self                     # 通过类访问时返回 property 本身
        return self.fget(obj)               # 通过实例访问时调用 getter

    def __set__(self, obj, value):
        if self.fset is None:
            raise AttributeError("can't set attribute")
        self.fset(obj, value)               # 赋值时调用 setter
```

这就是为什么 1.3 节的属性查找规则里，data descriptor 的优先级高于 instance dict——`property` 在类字典里，它的 `__set__` 拦截了 `obj.balance = x` 这种赋值，值不会进 `obj.__dict__`，而是走了你写的校验逻辑。

#### 常见模式：只读 property 与 computed property

**只读 property**——只定义 getter，不定义 setter：

```python
class Circle:
    def __init__(self, radius: float):
        self._radius = radius

    @property
    def radius(self) -> float:
        return self._radius

    @property
    def area(self) -> float:          # 不定义 setter——只读，area 由 radius 决定
        return 3.14159 * self._radius ** 2

>>> c = Circle(5)
>>> c.area        # 78.53975——像读属性一样
>>> c.area = 100  # AttributeError: can't set attribute
```

**computed property**（计算属性）——值不是存的而是算的：`area` 就是典型的计算属性。不存在 `c._area` 这个实例属性，每次访问 `c.area` 都是动态计算的。这对调用方是透明的——调用方不需要关心这个值是"存的"还是"算的"，这是封装的真正价值。

#### 什么时候不该用 property

`@property` 不是银弹。以下情况不适合：

- **操作有副作用的计算**（比如访问它会发网络请求、查数据库、写文件）。属性访问在直觉上是"便宜的、即时的"——没人会在 `obj.name` 时期待它阻塞半秒去调 API。这种场景应该用普通方法。
- **操作很昂贵**（比如 `obj.large_dataset` 每次访问都做大量计算）。属性访问预期是 O(1) 的轻量操作。昂贵的操作用方法——`obj.load_large_dataset()`——方法名明确告诉调用者"这个操作不便宜"。
- **不应该返回当前值以外的信息**——属性读应该像观察一个特性，不要有"修改状态"的隐藏动作。

**判断标准：** 如果去掉括号后读代码的人会误以为这是一个简单的值访问，而实际上它做了"重"的事情——那就是滥用了 `@property`。

---

### 2.7 总结

| 知识点 | 一句话要点 |
|--------|----------|
| Python 封装哲学 | 靠约定而非强制——"we're all consenting adults" |
| `public` | 无下划线——公开 API，调用者可自由使用 |
| `_protected` | 单下划线前缀——内部实现，别碰（`import *` 不导入，IDE 会警告） |
| `__private` | 双下划线触发 name mangling——改写为 `_Class__name`，目的是防子类意外覆盖，不是安全机制 |
| `__magic__` | 双下划线前后缀——Python 保留，不要自己发明 |
| `name_` | 单下划线后缀——避开关键字冲突（`class_`、`type_`） |
| `@property` | 用属性语法调方法——底层是 data descriptor，允许未来在不改 API 的前提下加校验/缓存 |
| property 禁区 | 副作用大的（网络/IO）、昂贵的（大量计算）——用普通方法代替 |

---

## 三、继承

### 3.1 单继承

#### 基本语法

```python
class Animal:
    def __init__(self, name: str):
        self.name = name

    def speak(self) -> str:
        return "..."

class Dog(Animal):
    def speak(self) -> str:
        return f"{self.name} says woof!"
```

`Dog` 继承 `Animal`——`Dog` 拥有 `Animal` 的全部方法和属性，可以选择覆盖（override）其中某些部分。

#### 属性查找走 MRO 链

当你写 `dog.name` 时，查找过程是：

1. `dog.__dict__` → 找不到 `name`
2. `Dog.__dict__` → 找不到
3. `Animal.__dict__` → 找不到（`name` 不在类字典里，它在 `__init__` 里被赋值的）
4. 继续沿 MRO 往上...最终也没找到
5. 触发 `__getattr__`（如果定义了）

等等——`dog.name` 是 `__init__` 里设置的实例属性，它在步骤 1 的 `dog.__dict__` 里就能找到。之所以提这个例子是为了区分：**实例属性（`self.name`）是 init 时写进实例 dict 的**，只在步骤 1 查找；**方法（`speak`）是类属性**，沿 MRO 链在类字典中查找。

这解释了为什么覆盖（override）方法不需要特殊语法——子类在它的 `__dict__` 里放一个同名方法，父类的就自然被遮住了（MRO 链上先遇到子类）。

#### `isinstance` / `issubclass`

```python
>>> dog = Dog("Rex")
>>> isinstance(dog, Dog)       # True
>>> isinstance(dog, Animal)    # True——子类实例也是父类实例
>>> isinstance(dog, object)    # True——一切皆 object
>>> issubclass(Dog, Animal)    # True
>>> issubclass(Dog, object)    # True
>>> issubclass(Animal, Dog)    # False——父类不是子类的子类
```

`isinstance` 检查的是——这个对象的类型链（`type(obj).__mro__`）里是否包含目标类。这就是为什么 `isinstance(dog, Animal)` 是 True。

---

### 3.2 多继承与 Diamond Problem

#### 多继承语法

Python 支持多继承——一个类可以有多个父类：

```python
class Flyable:
    def fly(self):
        return "flying"

class Swimmable:
    def swim(self):
        return "swimming"

class Duck(Animal, Flyable, Swimmable):
    def speak(self) -> str:
        return "quack!"
```

```python
>>> duck = Duck("Donald")
>>> duck.speak()   # "quack!"——自己的方法
>>> duck.fly()     # "flying"——从 Flyable 继承
>>> duck.swim()    # "swimming"——从 Swimmable 继承
```

#### Diamond Problem（菱形继承问题）

当多个父类有共同的祖先时，就形成了菱形继承结构：

```python
class A:
    def method(self):
        return "A"

class B(A):
    def method(self):
        return "B"

class C(A):
    def method(self):
        return "C"

class D(B, C):    # D 继承 B 和 C，两者都继承 A
    pass           # 菱形：A 在 top，B 和 C 在中间，D 在 bottom
```

```
    A
   / \
  B   C
   \ /
    D
```

问题是：**`D().method()` 应该返回 "B" 还是 "C"？** 答案取决于 Python 以什么顺序搜索父类。

这就是 **MRO（Method Resolution Order，方法解析顺序）** 解决的问题。

---

### 3.3 MRO —— 方法解析顺序

#### 什么是 MRO

MRO 是一个**线性的类列表**，Python 按这个列表的顺序依次搜索属性/方法。每个类有且仅有一个 MRO。

```python
>>> D.__mro__
# (D, B, C, A, object)
```

MRO 告诉我们：`D` 的实例查找方法时，先找 `D` 自己，再找 `B`，再 `C`，再 `A`，最后 `object`。

所以 `D().method()` 返回 `"B"`——`B` 在 MRO 中排在 `C` 前面，先被搜到。

```python
>>> D.mro()    # 等价于 D.__mro__，但返回 list
# [<class 'D'>, <class 'B'>, <class 'C'>, <class 'A'>, <class 'object'>]
```

#### C3 Linearization

Python 的 MRO 不是简单的"深度优先"或"广度优先"——它是 **C3 线性化算法**。C3 满足两个约束：

1. **局部优先（Local Precedence Order）**：子类排在父类前面。`D → B`（`D` 的声明里 `B` 在第一个），`D → C`，`B → A`，`C → A`。
2. **单调性（Monotonicity）**：子类的 MRO 不能改变父类之间的相对顺序。如果 `B` 的 MRO 里 `B` 在 `A` 前面，那 `D` 的 MRO 里也必须保持 `B` 在 `A` 前面。

C3 会拒绝生成不一致的继承结构。最经典的例子是两个类以**相反的相对顺序**声明了同一对父类：

```python
class A:
    pass

class B:
    pass

class X(A, B):    # X 说：A 在 B 前面
    pass

class Y(B, A):    # Y 说：B 在 A 前面
    pass

# class Z(X, Y):  # TypeError: Cannot create a consistent MRO
#     pass
```

为什么 `Z` 不能创建？检查两个父类的 MRO：

- `X.__mro__` = `(X, A, B, object)`——`A` 在 `B` 前面
- `Y.__mro__` = `(Y, B, A, object)`——`B` 在 `A` 前面

要生成 `Z` 的 MRO，C3 需要把这两个列表合并成一个——但 `X` 要求 `A → B`，`Y` 要求 `B → A`，这是不可调和的矛盾。Python 拒绝创建 `Z`，**这不是 bug，是 Python 在阻止你创造一个方法查找顺序不确定的类。**

注意这里的 `A` 和 `B` **不共享基类**（都直接继承 `object` 但彼此独立）。如果它们有共享基类（比如 `B(A)`），那情况会更复杂——有时候看似矛盾的声明被 C3 在更早的阶段就消解了，有时候看似合理的声明反而被拒绝。所以最简单的做法是：**当多继承涉及两个以上父类、且它们之间有共同祖先时，永远检查 `__mro__` 确认顺序是否符合预期。**

#### 理解 MRO 的最简单方式

不需要记住 C3 算法的公式——以下几点就够了：

1. **子类总是排在父类前面。**
2. **在 `class D(B, C)` 中，`B` 排在 `C` 前面。**
3. **如果无法同时满足这些约束，Python 拒绝创建这个类（`TypeError`）。**
4. 任何时候不确定 MRO 顺序，直接 `print(ClassName.__mro__)`——它是运行时信息，不是需要死记的。

---

### 3.4 `super()` —— 委托给 MRO 中的下一个

#### `super()` 不是"调用父类"

这是 Python 中最普遍、也最危险的误解：**`super()` 不是"调用父类的方法"**。

`super()` 的准确含义是：**返回 MRO 链上的下一个类的代理对象**。在单继承中，"下一个"恰好就是父类——所以误解在这时没有暴露。但在多继承中，"下一个"可能不是你的直接父类。

```python
class A:
    def method(self):
        print("A")

class B(A):
    def method(self):
        print("B")
        super().method()     # super() 是 MRO 中的下一个——是谁取决于 self 的实际类型

class C(A):
    def method(self):
        print("C")
        super().method()

class D(B, C):
    def method(self):
        print("D")
        super().method()
```

```python
>>> D().method()
# D
# B
# C
# A
```

执行的调用链是：`D.method` → `B.method` → `C.method` → `A.method`。注意 `B.method` 里的 `super()` 调的不是 `A.method`——它调的是 **MRO 中 B 后面的下一个**，也就是 `C`。

`D.__mro__` 是 `(D, B, C, A, object)`，所以 `super()` 的解析就是沿这个列表往后走：

```
D.method()  → super() → B.method()
B.method()  → super() → C.method()   ← 关键：不是 A！
C.method()  → super() → A.method()
A.method()  → super() → object.method()
```

**这就是 `super()` 和 "调用父类" 最根本的区别。**

#### Cooperate Multiple Inheritance（协作式多继承）

上面的 `D → B → C → A` 是一条完整调用链——每个类的 `method` 都调了 `super().method()`，最终到达 `A`，整个链没有断。这种编写模式叫 **cooperative multiple inheritance（协作式多继承）**——每个参与类都调用 `super()`，把控制权传给 MRO 中的下一个。

最经典的应用场景是 `__init__`：

```python
class Animal:
    def __init__(self, name: str, **kwargs):
        super().__init__(**kwargs)   # 把剩余的 kwarg 传给 MRO 的下一个
        self.name = name

class Flyable:
    def __init__(self, wingspan: float = 0.0, **kwargs):
        super().__init__(**kwargs)   # 同上
        self.wingspan = wingspan

class Swimmable:
    def __init__(self, dive_depth: float = 0.0, **kwargs):
        super().__init__(**kwargs)   # 同上
        self.dive_depth = dive_depth

class Duck(Animal, Flyable, Swimmable):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)   # 把全部 kwarg 沿 MRO 链分发
```

`Duck.__mro__` 是 `(Duck, Animal, Flyable, Swimmable, object)`。当 `Duck(**kwargs)` 被调用时：

1. `Duck.__init__` 调用 `super().__init__(**kwargs)` → 进入 `Animal.__init__`
2. `Animal.__init__` 消费 `name`，把剩余的 `**kwargs` 通过 `super()` 传给 `Flyable.__init__`
3. `Flyable.__init__` 消费 `wingspan`，把剩余的传给 `Swimmable.__init__`
4. `Swimmable.__init__` 消费 `dive_depth`，把剩余的传给 `object.__init__`
5. `object.__init__` 不接受参数——如果还有未消费的 kwarg 就会报错

```python
>>> duck = Duck(name="Donald", wingspan=0.8, dive_depth=3.0)
>>> duck.name         # "Donald"
>>> duck.wingspan     # 0.8
>>> duck.dive_depth   # 3.0
```

**关键约定：**
- 每个参与协作的 `__init__` 必须接受 `**kwargs` 并用 `super().__init__(**kwargs)` 把不认识的参数往下传。
- 参数通过关键字传递——位置参数在多继承协作中几乎是不可管理的。
- 所有协作类的最终基类（通常就是 `object`）必须也能接受 `**kwargs`——好在 `object.__init__()` 不接受任何参数，所以当它收到未消费的 kwarg 时会 `TypeError`，帮你发现拼写错误。

**如果不遵循这个模式**——某个类的 `__init__` 没有调 `super().__init__()`——那 MRO 链就在那个类断了，后面的类都不会被初始化。`Duck` 可能只有 `name` 而没有 `wingspan` 和 `dive_depth`，而且不会报错——这是多继承中最隐蔽的 bug。

#### Python 3 `super()` 的无参数形式

```python
class Dog(Animal):
    def __init__(self, name: str, breed: str):
        super().__init__(name)    # Python 3：不需要写 super(Dog, self)
        self.breed = breed
```

Python 3 的 `super()` 不带参数时，编译器自动填入 `super(__class__, self)`——即当前类和当前实例。这在 99% 的场景下就是你想要的。

只有一种情况需要带参数：你想跳过 MRO 中的某一个类，直接从更后面的类开始。这几乎只在写出极复杂 delegate/proxy 模式时才需要——大多数工程师一辈子用不着。

---

### 3.5 `__init_subclass__` —— 子类被定义时触发

这是一个较新（Python 3.6）但很实用的钩子：当**一个类被另一个类继承时**，父类的 `__init_subclass__` 会被自动调用。它不同于 `__init__`（实例化时触发）——它是在**类定义时**就触发。

```python
class PluginBase:
    _registry: dict[str, type] = {}

    def __init_subclass__(cls, **kwargs):
        """每次有类继承 PluginBase 时自动调用。"""
        super().__init_subclass__(**kwargs)
        PluginBase._registry[cls.__name__] = cls

class PDFPlugin(PluginBase):
    pass

class ExcelPlugin(PluginBase):
    pass

>>> PluginBase._registry
# {'PDFPlugin': <class 'PDFPlugin'>, 'ExcelPlugin': <class 'ExcelPlugin'>}
```

这就是注册模式/插件系统的基础机制——不需要手动注册每个子类，继承本身就完成了注册。在后续的插件系统项目中我们会深入使用这个模式。

---

### 3.6 继承 vs 组合——初始判断

继承是"is-a"关系：`Dog` **是** `Animal`。组合是"has-a"关系：`Car` **有** `Engine`。

**继承被滥用的最常见信号：** 你覆盖了父类的大部分方法，或者父类的很多方法对你的子类没有意义。这时候继承可能是错的选择——你在用"is-a"语法描述一个"has-a"或"is-like-a"的关系。

```python
# ❌ 滥用继承——Stack 不是 list（Stack 不应该有 .insert(2, x)、.sort() 等方法）
class Stack(list):
    def push(self, item):
        self.append(item)
    def pop(self):
        return super().pop()

# ✅ 用组合——Stack 包含一个 list
class Stack:
    def __init__(self):
        self._items: list = []
    def push(self, item):
        self._items.append(item)
    def pop(self):
        return self._items.pop()
```

（设计原则中的 "Composition > Inheritance" 会在第七节展开。）

---

### 3.7 总结

| 知识点 | 一句话要点 |
|--------|----------|
| 单继承 | 子类拥有父类的全部方法/属性；override 只需在子类中定义同名方法 |
| 多继承 | Python 支持——多个父类用逗号分隔；菱形继承用 MRO 解决冲突 |
| MRO | C3 线性化算法——每个类的 MRO 是一个确定的线性列表；`ClassName.__mro__` 查看 |
| `super()` | **不是"调父类"**——是委托给 MRO 中的下一个类；多继承中下一个可能不是你的直接父类 |
| 协作式多继承 | 每个类用 `super().__init__(**kwargs)` 把不认识的参数往下传——链不断，所有父类都初始化 |
| `__init_subclass__` | 子类继承时自动触发——注册模式/插件系统的基础 |
| 继承 vs 组合 | 继承是 is-a，组合是 has-a；覆盖了父类大部分方法 → 你应该用组合 |