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

---

## 四、多态

### 4.1 多态是什么

多态（Polymorphism）的字面意思是"多种形态"。在 OOP 中它指的是：

> **同一个接口（方法名），不同的对象给出不同的实现，调用方不需要知道具体是哪个实现。**

```python
def make_sound(animal) -> str:
    return animal.speak()     # 调用方只依赖 speak() 这个接口

class Dog:
    def speak(self):
        return "woof!"

class Cat:
    def speak(self):
        return "meow!"

class Duck:
    def speak(self):
        return "quack!"

>>> for animal in [Dog(), Cat(), Duck()]:
...     print(make_sound(animal))
# woof!
# meow!
# quack!
```

`make_sound` 不知道也不关心传进来的是什么类——只要它有 `speak()` 方法就能工作。这是多态最核心的价值：**调用方写一次，实现方随意扩展。**

注意这三个类**没有任何继承关系**——它们只是碰巧都有 `speak()` 方法。这在 Java 里不可能（Java 的多态要求显式 `implements Animal` 接口），但在 Python 里这是多态的标准形式。

---

### 4.2 Duck Typing —— Python 的多态机制

#### "如果它像鸭子一样走路、像鸭子一样叫，那它就是鸭子"

**Duck Typing（鸭子类型）**是 Python 多态的底层哲学：**一个对象的类型由它的行为（方法）决定，而不是由它继承自谁决定。**

```python
def calculate_total(items) -> float:
    total = 0.0
    for item in items:          # 要求：可迭代
        total += item           # 要求：支持 + 运算
    return total

>>> calculate_total([1, 2, 3])            # list 可以
>>> calculate_total((1.5, 2.5))           # tuple 可以
>>> calculate_total({"a": 1})             # dict 可以——迭代的是 key
>>> calculate_total(range(10))            # range 可以
```

`calculate_total` 不检查 `isinstance(items, list)`——它只要求传入的对象"像序列一样能迭代"。任何满足这个行为契约的对象都能工作。

#### Duck Typing vs 名义类型（Nominal Typing）的对比

| | Java/C++（名义类型） | Python（鸭子类型） |
|---|---|---|
| 多态的资格 | 必须显式 `implements`/`extends` 声明的接口或类 | 有正确的方法就行——不需要任何声明 |
| 类型检查 | 编译期强制——不满足就编译失败 | 运行时——调用不存在的方法时 `AttributeError` |
| 扩展性 | 新类型要符合已有接口，接口要先被设计出来 | 新类型只要"行为正确"就能无缝插入 |
| 风险 | 更安全——错误在编译期暴露 | 更灵活——错误可能要到运行时才暴露 |

鸭子类型的本质是**结构化类型（Structural Typing）**：类型由结构（有什么方法）决定，不由名字（叫什么、继承自谁）决定。

**Duck Typing 的典型陷阱：**

```python
class Dog:
    def speak(self):
        return "woof!"

def make_sound(animal):
    return animal.speak()     # 鸭子类型——期望参数有 .speak()

>>> make_sound(Dog())          # 可以
>>> make_sound("hello")        # AttributeError: 'str' object has no attribute 'speak'
```

鸭子类型不检查类型，只在使用时验证。如果你的函数期望一个"有 speak() 方法的对象"，但调用者传了个没有这个方法的对象，错误会在**运行时**爆发——可能是代码深处、可能是在生产环境。这就是为什么类型标注（typing）在大型工程中变得重要——`Protocol` 可以在静态检查阶段补上这层保护（后面的 typing 章节会讲）。

---

### 4.3 Override —— 覆盖

#### 方法覆盖

子类定义一个和父类同名的方法，就覆盖了父类的实现：

```python
class Animal:
    def speak(self):
        return "..."

class Dog(Animal):
    def speak(self):          # 覆盖——同名方法
        return "woof!"

class SilentDog(Dog):
    pass                      # 不覆盖——继承 Dog 的实现

>>> Dog().speak()         # "woof!"——覆盖生效
>>> SilentDog().speak()   # "woof!"——继承 Dog 的实现
```

Override 不需要任何特殊关键字（Java 要 `@Override` 注解）——同名即可。查找机制就是 1.3 节的属性查找：MRO 链上先遇到子类的 `speak`，父类的就被遮住了。

#### 覆盖时调用被覆盖的方法——`super()`

覆盖一个方法时，最常见需求是"在父类逻辑的基础上**扩展**"，而不是完全替换：

```python
class Animal:
    def __init__(self, name: str):
        self.name = name

class Dog(Animal):
    def __init__(self, name: str, breed: str):
        super().__init__(name)    # 先跑父类的初始化逻辑
        self.breed = breed        # 再初始化自己的属性
```

`super()` 在这里返回 MRO 中 `Dog` 的下一个类（单继承下就是 `Animal`），调用它的 `__init__`——先完成父类的初始化，再初始化子类自己的部分。

**不调用 `super()` 的后果：** 父类的初始化逻辑被完全跳过——`self.name` 永远不会被设置：

```python
class BadDog(Animal):
    def __init__(self, name: str, breed: str):
        self.breed = breed        # 忘了 super().__init__(name)！

>>> bad = BadDog("Rex", "Labrador")
>>> bad.breed     # "Labrador"
>>> bad.name      # AttributeError——父类初始化从未执行
```

这种 bug 不会立即报错——`BadDog` 能正常实例化，但所有依赖 `name` 的方法在稍后某个时刻才崩溃。**覆盖 `__init__` 时忘记 `super().__init__()` 是 OOP 最常见的错误之一。**

#### 覆盖的完整行为表

| 子类动作 | 效果 |
|---------|------|
| 不定义该方法 | 完整继承父类实现 |
| 定义同名方法，不调 `super()` | 完全替换——父类逻辑不执行 |
| 定义同名方法，调 `super().method()` | 扩展——先（或后）执行父类逻辑，再加入自己的 |

第三种模式叫 **Template Method 模式**的一种变体——父类定义流程骨架，子类通过覆盖特定方法来定制具体步骤。这是继承最有价值的用法之一（设计原则一节会进一步展开）。

---

### 4.4 多态的工程价值——以插件系统为例

OOP 的必做项目是插件系统。多态是它成立的基础：

```python
# 主程序只知道统一的接口——这是多态的"调用方"
class DocumentReader:                     # Port——统一接口
    def read(self, path: str) -> str:
        raise NotImplementedError

class PDFReader(DocumentReader):          # Adapter 1
    def read(self, path: str) -> str:
        return f"[PDF] {path}"

class DocxReader(DocumentReader):         # Adapter 2
    def read(self, path: str) -> str:
        return f"[DOCX] {path}"

def process_file(reader: DocumentReader, path: str) -> str:
    return reader.read(path)              # 多态调用——不关心具体是哪个 Reader

>>> process_file(PDFReader(), "report.pdf")   # "[PDF] report.pdf"
>>> process_file(DocxReader(), "notes.docx")  # "[DOCX] notes.docx"
```

`process_file` 只依赖 `read()` 接口。以后要支持 Excel、Markdown、任何格式，只需**新增一个类**——主程序一行都不用改。这就是多态 + 插件系统 = **开放封闭原则（Open-Closed Principle）**：对扩展开放，对修改封闭。

---

### 4.5 总结

| 知识点 | 一句话要点 |
|--------|----------|
| 多态 | 同一接口、不同实现——调用方只依赖方法名，不依赖具体类型 |
| Duck Typing | 类型由行为决定——有 `speak()` 的就是"会叫的动物"，不需要继承声明 |
| 鸭子类型的代价 | 错误从编译期推迟到运行时——大型工程用类型标注（Protocol）补回安全性 |
| Override | 子类同名方法覆盖父类——无特殊语法，靠 MRO 查找顺序实现 |
| 覆盖 + super() | 在父类逻辑基础上扩展——忘调 `super().__init__()` 是最常见的 OOP 错误 |
| 多态的工程价值 | 开放封闭原则——新增插件不改主程序；插件系统项目的基础 |

---

## 五、抽象

### 5.1 抽象是什么，为什么需要

鸭子类型有个问题：**它不表达意图。** 看这段代码：

```python
class PDFReader:
    def read(self, path: str) -> str:
        ...

class DocxReader:
    def read(self, path: str) -> str:
        ...
```

`PDFReader` 和 `DocxReader` 都有 `read()`——但从代码结构上看不出**这是巧合还是约定**。没有东西在说："任何 Reader 都必须实现 `read()` 方法。" 如果新同事写了一个 `ExcelReader` 但忘了 `read()` 方法（比如写成了 `parse()`），什么都不会发生——直到运行时某个调用点 `AttributeError` 爆炸。

**抽象（Abstraction）解决的就是这个问题：把"接口约定"从"巧合"变成"声明"。** Python 提供两个工具：**ABC**（运行时强制）和 **Protocol**（静态检查，typing 章节讲）。本节讲 ABC。

---

### 5.2 ABC 与 `abstractmethod`

#### 基本用法

```python
from abc import ABC, abstractmethod

class DocumentReader(ABC):                       # 继承 ABC——标记为抽象基类
    @abstractmethod
    def read(self, path: str) -> str:            # 抽象方法——子类必须实现
        ...

class PDFReader(DocumentReader):
    def read(self, path: str) -> str:            # 实现了——可以实例化
        return f"[PDF] {path}"

class ExcelReader(DocumentReader):               # 没有实现 read()！
    pass
```

```python
>>> PDFReader()               # 可以——read 已实现
>>> DocumentReader()          # TypeError: Can't instantiate abstract class DocumentReader
                              # with abstract method read
>>> ExcelReader()             # TypeError: Can't instantiate abstract class ExcelReader
                              # with abstract method read
```

**ABC 的运行时行为：**

1. `DocumentReader` 继承 `ABC`——`ABC` 的元类（metaclass）是 `ABCMeta`，它记录了哪些方法是抽象的。
2. `DocumentReader` 自己不能实例化——它包含未实现的抽象方法。
3. `ExcelReader` 也不能实例化——它继承了 `read` 但 `read` 仍然是抽象的（没有被覆盖成具体实现）。
4. `PDFReader` 可以实例化——它覆盖了 `read`，`read` 不再是抽象的。

**这就是 ABC 和鸭子类型的本质区别：** 鸭子类型"默认信任，出错再说"；ABC **在实例化时就拒绝**不完整的实现——错误提前暴露，而且错误信息精确到"哪个类缺哪个方法"。

#### `abstractmethod` 的细节

抽象方法可以有默认实现——子类可以用 `super()` 调用它：

```python
from abc import ABC, abstractmethod

class DocumentReader(ABC):
    @abstractmethod
    def read(self, path: str) -> str:
        return f"[generic] {path}"    # 抽象方法可以有实现体

class PDFReader(DocumentReader):
    def read(self, path: str) -> str:
        return super().read(path).replace("generic", "PDF")
        # 复用抽象基类里的默认实现
```

`@abstractmethod` 的语义是"**子类必须覆盖这个方法**"——不是"这个方法不能有实现体"。这是常见的误解。

**`@abstractmethod` 和 `@property` 的组合——注意顺序：**

```python
from abc import ABC, abstractmethod

class Shape(ABC):
    @property
    @abstractmethod
    def area(self) -> float:
        ...

# ❌ 顺序错了：
class Wrong(ABC):
    @abstractmethod
    @property          # 这样写 property 会把 abstractmethod 包住——abstract 标记失效
    def area(self) -> float:
        ...
```

规则：**`@abstractmethod` 必须是最内层（最靠近 `def`）的装饰器。** 这样它标记的是"这个方法本身"，而外层的 `@property`、`@classmethod` 等包装器才能正常生效。

---

### 5.3 标准库中的 ABC——`collections.abc`

ABC 不只是你自己的代码里用——**Python 标准库本身就大量使用 ABC 来定义协议**：

```python
from collections.abc import Iterable, Iterator, Sequence, Mapping, MutableMapping, Callable

>>> isinstance([1, 2, 3], Sequence)       # True——list 是 Sequence
>>> isinstance("hello", Sequence)         # True——str 是 Sequence
>>> isinstance({"a": 1}, Mapping)         # True——dict 是 Mapping
>>> isinstance(lambda x: x, Callable)     # True——函数是 Callable
```

`collections.abc` 定义了 Python 数据结构的**接口层级**——`Iterable`、`Iterator`、`Sequence`、`Mapping`、`Set` 等。这层 ABC 有双重用途：

1. **检查协议**：`isinstance(obj, Iterable)` 检查 obj 是否可迭代——不是检查继承自谁，而是检查**有没有实现 `__iter__`**（或 `__getitem__` 等后备协议）。
2. **继承获得默认实现**：继承 `Sequence` 并实现 `__getitem__` 和 `__len__`，就免费获得 `__contains__`、`__iter__`、`index`、`count` 等方法——这些方法都基于 `__getitem__` 的默认实现。

第 2 点是 mixin 模式的体现——这也是 Collection Library 项目中实现自定义容器时的标准做法（Python 高级教程 5.4 节有完整展开）。

---

### 5.4 抽象方法的检测机制——`__abstractmethods__`

理解 ABC 的底层有助于调试：

```python
>>> from abc import ABC, abstractmethod
>>> class Base(ABC):
...     @abstractmethod
...     def method(self):
...         ...
...
>>> Base.__abstractmethods__      # frozenset({'method'})
>>> class Concrete(Base):
...     def method(self):
...         pass
...
>>> Concrete.__abstractmethods__  # frozenset()
```

- 每个类有一个 `__abstractmethods__` 属性——它是**尚未被实现的抽象方法名的集合**。
- 实例化时 Python 检查 `cls.__abstractmethods__`——非空就 `TypeError`。
- 子类覆盖了抽象方法 → 名字从集合中移除 → 集合空了 → 可以实例化。

**这个机制的解释力：** `ExcelReader`（没实现 `read`）的 `__abstractmethods__` 里还有 `read`，所以不能实例化。`PDFReader` 的集合是空的，所以可以。

---

### 5.5 ABC vs Duck Typing——什么时候用哪个

| 场景 | 用 Duck Typing | 用 ABC |
|------|--------------|--------|
| 只有一两个方法的小接口，内部使用 | ✅ | 过度设计 |
| 接口会被第三方/其他模块实现——需要**文档化的契约** | ❌ | ✅ |
| 错误要**尽早暴露**（实例化时 vs 调用时） | ❌ | ✅ |
| 需要 `isinstance` 检查（比如插件注册、序列化分发） | ❌ | ✅ |
| 灵活的原型/脚本 | ✅ | 过度设计 |

**经验法则：** 内部小接口用鸭子类型（灵活）；跨模块/跨团队/被插件实现的公共接口用 ABC（明确的契约 + 早期失败）。插件系统项目就是后者的典型场景——插件开发者需要一份明确的"必须实现什么"的清单，ABC 就是这个清单。

---

### 5.6 总结

| 知识点 | 一句话要点 |
|--------|----------|
| 抽象的作用 | 把"接口约定"从巧合变成声明——新实现缺方法时立即失败 |
| `ABC` + `abstractmethod` | 含未实现抽象方法的类不能实例化——错误提前到实例化时暴露 |
| 抽象方法可有实现体 | `abstractmethod` 语义是"子类必须覆盖"，不是"不能有实现" |
| 装饰器顺序 | `@abstractmethod` 必须是最内层——`@property`/`@classmethod` 在外层 |
| `collections.abc` | 标准库的接口层级——`isinstance` 检查协议 + mixin 提供默认实现 |
| `__abstractmethods__` | 未实现抽象方法名的集合——实例化时非空即 `TypeError` |
| ABC vs Duck Typing | 内部小接口用鸭子类型；跨模块公共接口用 ABC——插件系统属于后者 |

---

## 六、数据类

### 6.1 问题：样板代码（Boilerplate）

写一个"只存数据"的类，传统方式要写大量机械的样板代码：

```python
class Point:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def __repr__(self):                    # 打印友好
        return f"Point(x={self.x}, y={self.y})"

    def __eq__(self, other):               # 值相等判断
        if not isinstance(other, Point):
            return NotImplemented
        return self.x == other.x and self.y == other.y
```

`__init__`、`__repr__`、`__eq__` 这些代码和"Point 有两个坐标"这个业务信息毫无关系——它们是每个数据类都要重复的机械劳动。

**`@dataclass` 解决的问题：** 用声明字段的方式描述数据类，让 Python 自动生成这些方法：

```python
from dataclasses import dataclass

@dataclass
class Point:
    x: float
    y: float
```

就这么简单。`dataclass` 会自动生成 `__init__`、`__repr__`、`__eq__`（以及 `__hash__`、`__match_args__` 等）：

```python
>>> p1 = Point(1.0, 2.0)
>>> p2 = Point(1.0, 2.0)
>>> p1                      # Point(x=1.0, y=2.0)——自动 __repr__
>>> p1 == p2                # True——自动 __eq__（值相等，不是身份相等）
>>> p1.x                    # 1.0
```

**注意：`@dataclass` 生成的 `__eq__` 是"值相等"而不是"身份相等"**——两个不同的实例，只要字段值相同就 `==`。这是和默认 object 行为（`is` 身份比较）的关键区别。

---

### 6.2 `field()` —— 精细控制字段

#### `default` 与可变默认值的陷阱

```python
from dataclasses import dataclass, field

# ❌ 错误——可变默认值：所有实例共享同一个 list！
@dataclass
class BadTeam:
    members: list[str] = []

# ✅ 正确——用 default_factory，每个实例创建自己的 list
@dataclass
class Team:
    members: list[str] = field(default_factory=list)
```

这个陷阱和普通函数参数的 `def f(x=[])` 是同一个问题的 dataclass 版本：**默认值在类定义时只创建一次，所有实例共享同一个对象。** `default_factory` 告诉 dataclass"每次实例化时调用这个工厂函数来创建新的默认值"。

```python
>>> t1 = Team()
>>> t2 = Team()
>>> t1.members.append("Alice")
>>> t1.members    # ['Alice']
>>> t2.members    # []——独立！如果用了 [] 会变成 ['Alice']
```

**常见 `default_factory`：** `list`、`dict`、`set`、`lambda: 0.0`（要动态计算的默认值）。注意 `lambda` 可以作为工厂——比如默认值为当前时间 `field(default_factory=datetime.now)`。

#### `field()` 的其他参数

```python
@dataclass
class User:
    name: str
    age: int = field(compare=False)      # 不参与 __eq__ 比较
    _cache: dict = field(default_factory=dict, repr=False)   # 不显示在 __repr__ 中
```

| 参数 | 作用 |
|------|------|
| `default` | 默认值——只允许不可变类型 |
| `default_factory` | 默认值工厂函数——可变默认值用这个 |
| `init` | `False` 时该字段不出现在 `__init__` 参数中 |
| `repr` | `False` 时该字段不出现在 `__repr__` 中 |
| `compare` | `False` 时该字段不参与 `__eq__`/`__lt__` 等比较 |

---

### 6.3 `frozen=True` —— 不可变数据类

```python
@dataclass(frozen=True)
class Point:
    x: float
    y: float
```

```python
>>> p = Point(1.0, 2.0)
>>> p.x = 5.0    # dataclasses.FrozenInstanceError: cannot assign to field 'x'
>>> hash(p)      # 可以 hash——frozen 数据类的 __hash__ 自动生成
```

`frozen=True` 的机制：dataclass 生成的 `__setattr__` 会拒绝任何赋值（在 `__init__` 完成后）。

**`frozen=True` 的实际价值：**

1. **可哈希**——frozen 实例自动获得 `__hash__`，可以作为 dict 的 key 或 set 的元素。
2. **防意外修改**——数据在创建后不可变，符合"值对象（Value Object）"语义：坐标点、配置、事件记录这类"创建后就不该变"的数据。

**常见误解——frozen 是"浅冻结"：**

```python
@dataclass(frozen=True)
class FrozenTeam:
    members: list[str]    # 字段本身是可变类型！

>>> team = FrozenTeam(["Alice"])
>>> team.members.append("Bob")    # 这不会报错！
>>> team.members                  # ['Alice', 'Bob']——内部数据被改了
```

`frozen=True` 阻止的是"给字段重新赋值"（`team.members = [...]`），**不是"修改字段指向的可变对象"**。如果字段是 list/dict，它们的内容仍然可以变。真正的不可变需要字段本身也是不可变类型（tuple、frozenset、str、int 等）。

---

### 6.4 `slots=True` —— 内存优化

```python
@dataclass(slots=True)
class Point:
    x: float
    y: float
```

`slots=True`（Python 3.10+）让 dataclass 使用 `__slots__` 而非 `__dict__` 存储实例属性：

```python
>>> p = Point(1.0, 2.0)
>>> p.__dict__    # AttributeError——没有 __dict__
```

**`__slots__` 的机制**（Python 高级教程 1.6 节的展开）：普通实例用一个 dict（`__dict__`）存属性——灵活但每个实例都有 dict 的内存开销。`__slots__` 用**固定大小的 C 结构体**存属性——省内存，代价是不能动态添加新属性。

```python
>>> p = Point(1.0, 2.0)
>>> p.z = 3.0    # AttributeError: 'Point' object has no attribute 'z'
```

**什么时候用：** 需要创建**大量实例**（百万级）且字段集合固定时——每个实例省一个 dict 的开销，内存差异巨大。普通业务代码不需要——可读性和灵活性比省那点内存重要。

---

### 6.5 dataclass 在数据模型三层划分中的位置

回顾 1.1 Python高级里"数据模型的三层划分"：

| 层级 | 工具 | 运行时校验 | 场景 |
|------|------|-----------|------|
| 定义数据结构 | **`dataclass`** | 否 | 程序内部自己构造 |
| 运行时数据流转 | `TypedDict` | 否 | 模块间传递，彼此信任 |
| 接口级数据流转 | `pydantic.BaseModel` | **是** | 外部输入（HTTP body、MQ、第三方 API） |

`dataclass` 是三层中的第一层——**内部数据结构的标准写法**。它不校验类型（`Point("a", "b")` 不会报错，尽管标注了 `float`），它的价值是消除样板代码 + 类型标注给 IDE/静态检查器用。

**关键边界：** 一旦数据来自外部输入（HTTP 请求体、消息队列、用户上传的文件），`dataclass` 不够——你需要 pydantic 的运行时校验。`dataclass` 的信任前提是"构造它的人就是你自己团队"。

---

### 6.6 总结

| 知识点 | 一句话要点 |
|--------|----------|
| `@dataclass` | 自动生成 `__init__`/`__repr__`/`__eq__`——消除样板代码 |
| `__eq__` 语义 | 值相等而非身份相等——两个实例字段相同就 `==` |
| 可变默认值陷阱 | `field(default_factory=list)`——和函数默认参数同一个坑 |
| `field()` | 精细控制：`compare`/`repr`/`init` 排除字段 |
| `frozen=True` | 不可变 + 可哈希——但只是浅冻结，字段内容仍然可变 |
| `slots=True` | 用 `__slots__` 存属性——百万级实例时省内存，代价是失去动态属性 |
| 三层划分 | dataclass 是内部数据结构层——外部输入需要 pydantic 的运行时校验 |

---

## 七、设计原则

### 7.1 SOLID——面向对象设计的五个原则

SOLID 是五个设计原则的首字母缩写。它们不是法律条文，而是"当你犹豫怎么设计时，朝这个方向想"的指南。

#### S —— Single Responsibility Principle（单一职责原则）

> **一个类只应该有一个变化的原因。**

反例：

```python
class Report:
    def __init__(self, data: dict):
        self.data = data

    def calculate_statistics(self):    # 职责 1：计算统计
        ...

    def format_as_html(self):          # 职责 2：格式化成 HTML
        ...

    def save_to_database(self):        # 职责 3：存数据库
        ...
```

这个类有三个变化原因：统计口径变了要改、HTML 样式变了要改、数据库 schema 变了也要改。任何一个改动都可能意外影响其他两个职责。

正例：

```python
class Statistics:
    def calculate(self, data: dict) -> dict:    # 只负责计算
        ...

class HTMLFormatter:
    def format(self, stats: dict) -> str:       # 只负责格式化
        ...

class ReportRepository:
    def save(self, report: str) -> None:        # 只负责持久化
        ...
```

**判断标准：** 能否用一句话描述这个类的职责？如果描述里出现"和"字，很可能违反 SRP。

#### O —— Open-Closed Principle（开放封闭原则）

> **对扩展开放，对修改封闭。** 新增功能时，应该通过新增代码（扩展）实现，而不是修改已有代码。

这是插件系统项目的核心原则（4.4 节已经见过）：

```python
# ❌ 违反 OCP——每加一种文件格式，就要改这个函数
def process_file(path: str) -> str:
    if path.endswith(".pdf"):
        return process_pdf(path)
    elif path.endswith(".docx"):
        return process_docx(path)
    elif path.endswith(".xlsx"):       # 每次加格式都改这里
        return process_excel(path)
    ...
```

```python
# ✅ 符合 OCP——新格式只需要新加一个类，已有代码一行不改
class Reader(ABC):
    @abstractmethod
    def read(self, path: str) -> str: ...

class PDFReader(Reader):
    def read(self, path): ...

class DocxReader(Reader):
    def read(self, path): ...

class ExcelReader(Reader):     # 新增——扩展，不修改
    def read(self, path): ...
```

**判断标准：** 新增一种场景，你是在加新类/新函数，还是在已有函数里加 `elif` 分支？前者是 OCP，后者不是。

#### L —— Liskov Substitution Principle（里氏替换原则）

> **子类必须能替换父类，而程序行为不改变。** 凡是父类能出现的地方，换成子类，调用方感知不到差异（除了行为的具体实现）。

这是 SOLID 里最容易被违反也最隐蔽的一个。经典反例——矩形/正方形：

```python
class Rectangle:
    def __init__(self, width: float, height: float):
        self._width = width
        self._height = height

    def set_width(self, w: float):
        self._width = w

    def set_height(self, h: float):
        self._height = h

class Square(Rectangle):
    def __init__(self, side: float):
        super().__init__(side, side)

    def set_width(self, w: float):
        self._width = w
        self._height = w      # 保证正方形——但破坏了矩形的独立设置语义

    def set_height(self, h: float):
        self._width = h       # 同上
        self._height = h
```

问题：

```python
def scale(rect: Rectangle, factor: float):
    rect.set_width(rect.width * factor)     # 调用方假设 width/height 独立

>>> r = Rectangle(3, 4)
>>> scale(r, 2)      # width=6, height=4——矩形行为正常
>>> s = Square(3)
>>> scale(s, 2)      # 期望：正方形放大。实际：width=6, height=3——不再是正方形！
```

`Square` 在数学上是 `Rectangle` 的特例，但**在可变对象的世界里它不是**——因为 `Rectangle` 的契约包含"width 和 height 可以独立修改"，而 `Square` 无法履行这个契约。调用 `scale` 的代码假设它拿到的是"真矩形"，换成 `Square` 后行为悄悄变了——这就是 LSP 违规。

**Python 中的 LSP 信号：**

- 子类覆盖方法时**收窄了参数范围**或**抛出不相关的异常**（父类方法明确不会抛的异常）
- 子类的方法**不做事**（`pass`）或**抛 `NotImplementedError`**——说明这个方法对子类无意义，继承关系本身就错了
- 子类改变了父类方法的**返回值语义**（比如父类返回非负数，子类可能返回负数）

#### I —— Interface Segregation Principle（接口隔离原则）

> **调用方不应该被迫依赖它不需要的接口。**

Java 版本：一个大接口有 10 个方法，实现类只用 2 个，却被迫实现全部 10 个（用空实现或 `UnsupportedOperationException` 凑数）。解决方案是把大接口拆成多个小接口。

Python 版本——用 ABC 表达：

```python
# ❌ 一个臃肿的 ABC——所有"机器"都必须实现全部方法
class Machine(ABC):
    @abstractmethod
    def print_document(self): ...

    @abstractmethod
    def scan_document(self): ...

    @abstractmethod
    def fax_document(self): ...

# 打印机被迫实现扫描和传真——空实现或抛错凑数
class Printer(Machine):
    def print_document(self):
        ...
    def scan_document(self):
        raise NotImplementedError    # 打印机不会扫描——被迫实现无关方法
    def fax_document(self):
        raise NotImplementedError
```

```python
# ✅ 拆成小接口——每个实现类只依赖它需要的
class Printer(ABC):
    @abstractmethod
    def print_document(self): ...

class Scanner(ABC):
    @abstractmethod
    def scan_document(self): ...

class Fax(ABC):
    @abstractmethod
    def fax_document(self): ...

class PrinterOnly(Printer):
    def print_document(self): ...

class AllInOne(Printer, Scanner, Fax):    # 全能机才实现全部
    ...
```

**Python 的天然优势：** 鸭子类型让 Python 默认就接近 ISP——你不需要声明"实现哪个接口"，只实现你需要的方法。ISP 在 Python 中主要体现为：**ABC 要小而专注**——如果一个 ABC 有 10 个抽象方法而大多数实现类只用其中 3 个，这个 ABC 该拆了。

#### D —— Dependency Inversion Principle（依赖倒置原则）

> **高层模块不应该依赖低层模块，两者都应该依赖抽象；抽象不应该依赖细节，细节应该依赖抽象。**

```python
# ❌ 违反 DIP——ReportService 直接依赖具体的 MySQL 实现
class MySQLRepository:
    def save(self, report: str):
        ...    # 直接写 MySQL

class ReportService:
    def __init__(self):
        self._repo = MySQLRepository()    # 硬编码依赖具体类

# ❌ 换数据库 = 改 ReportService = 违反 DIP
```

```python
# ✅ 符合 DIP——依赖抽象接口
class ReportRepository(ABC):              # 抽象
    @abstractmethod
    def save(self, report: str) -> None: ...

class MySQLRepository(ReportRepository):  # 细节依赖抽象
    def save(self, report: str):
        ...

class S3Repository(ReportRepository):     # 换存储 = 新增类，不改服务
    def save(self, report: str):
        ...

class ReportService:
    def __init__(self, repo: ReportRepository):    # 依赖注入——传接口
        self._repo = repo

    def create_report(self, data: dict):
        ...
        self._repo.save(...)               # 只依赖 save 接口
```

`ReportService` 只依赖 `ReportRepository` 这个抽象——用 MySQL、S3、本地文件都行，服务代码一行不改。**依赖注入（构造函数传入依赖）是 DIP 的落地方式。**

DIP 和六边形架构的关系：学习目标里讲的"Port/Adapter"——Port 就是抽象接口，Adapter 就是具体实现。DIP 是那个架构的底层原则。

#### SOLID 速查

| 原则 | 一句话 |
|------|--------|
| S 单一职责 | 一个类只有一个变化原因——描述里出现"和"字要警惕 |
| O 开放封闭 | 新功能靠新增代码（新类），不靠修改已有代码（加 elif） |
| L 里氏替换 | 子类能无缝替换父类——子类"不做事"或"抛异常"的方法说明继承错了 |
| I 接口隔离 | ABC 小而专注——调用方不被迫实现用不到的方法 |
| D 依赖倒置 | 依赖抽象（ABC）不依赖具体——依赖注入落地 |

---

### 7.2 Composition > Inheritance（组合优于继承）

> 这个原则的完整表述是：**能用组合（has-a）解决的问题，不要用继承（is-a）解决。** 它不是"禁止继承"，而是"继承是最后的手段"。

#### 为什么继承是危险的

继承在三种情况下会伤害你：

1. **继承打破了封装。** 子类能看到（并依赖）父类的内部实现——父类改一个"内部"属性，所有子类可能都崩。而组合通过接口交互，内部实现完全隔离。
2. **继承是静态的、编译期（定义期）决定的。** `Dog` 永远是 `Animal`，不能运行时改变。而组合的对象可以在运行时替换（把 `Engine` 换成 `ElectricEngine`）。
3. **深层继承链难以理解。** `Animal → Mammal → Canine → Dog → Labrador`——任何一个类的行为都散落在五层里，读代码要爬五层才能理解一个方法。

#### 组合的两种落地模式

**（a）直接组合——把对象存为属性：**

```python
class Engine:
    def start(self):
        return "engine started"

class Car:
    def __init__(self, engine: Engine):    # Car 有一个 Engine——has-a
        self._engine = engine

    def start(self):
        return self._engine.start()         # 委托——把工作交给 Engine

# 换引擎类型——运行时替换，Car 类不用改
>>> car = Car(ElectricEngine())
>>> car.start()
```

**（b）Mixin 组合——用多继承实现行为复用：**

```python
class JSONSerializable:
    def to_json(self) -> str:
        import json
        return json.dumps(self.__dict__)

class User(JSONSerializable):       # User 有一个"能 JSON 化"的能力
    def __init__(self, name: str):
        self.name = name

>>> User("Alice").to_json()     # '{"name": "Alice"}'
```

Mixin 是 Python 对"组合优于继承"的独特答案——它是**受限的继承**：Mixin 类不承载"是什么"的语义（`User` 不是 `JSONSerializable` 的一种），只注入"有什么能力"。规范：

- Mixin 类名以 `Mixin` 或 `-able` 结尾（`JSONSerializable`、`LoggingMixin`）
- Mixin 不定义 `__init__`（除非是协作式多继承的 `**kwargs` 模式）
- 每个 Mixin 只提供一个能力——小而专注（呼应 ISP）

#### 何时用继承，何时用组合

| 关系 | 用 | 例子 |
|------|-----|------|
| is-a——真正的"是一种" | 继承 | `Dog` is `Animal` |
| has-a——"有一个" | 组合 | `Car` has `Engine` |
| 需要复用**大部分**父类行为，只改一小部分 | 继承 | 框架基类、Template Method |
| 需要复用**少量**能力，其余无关 | Mixin 或组合 | 日志、序列化、缓存 |
| 不确定 | **组合** | 组合更容易重构 |

**经验法则：先写组合。** 组合写起来略啰嗦（要写委托方法），但重构代价低、耦合小。继承写起来省事，但改起来贵。默认组合，明确是 is-a 时才继承。

---

### 7.3 总结

| 知识点 | 一句话要点 |
|--------|----------|
| S 单一职责 | 一个类只有一个变化原因——职责描述里有"和"要警惕 |
| O 开放封闭 | 新增功能靠新增类（扩展），不靠改已有代码（加分支） |
| L 里氏替换 | 子类必须能无缝替换父类——`Square` 继承 `Rectangle` 的经典反例 |
| I 接口隔离 | ABC 小而专注——实现类不被迫实现无关方法 |
| D 依赖倒置 | 依赖抽象不依赖具体——构造函数注入（依赖注入）落地 |
| Composition > Inheritance | 继承打破封装、静态绑定、链深难懂；组合隔离、可替换、易重构 |
| Mixin | Python 的受限继承——注入"能力"不承载"是什么"语义 |
| 默认选择 | 不确定就用组合——继承留给明确的 is-a 关系 |

---

## 八、Project 2：插件系统（Plugin System）

### 8.1 项目是什么

实现一个**文档抽取器（Document Extractor）**：接收任意格式的文档文件（PDF、DOCX、Excel……），统一抽取为 `Document` 对象。

这个项目要练的不是"解析文档"——那有现成的库（pypdf、python-docx、openpyxl）。要练的是**插件架构**：如何设计一个系统，让"新增一种格式支持"变成"新增一个插件文件"，主程序一行代码都不用改。

这正是学习目标中说的——**插件系统就是六边形架构（Ports & Adapters）的落地**：

| 六边形架构的概念 | 本项目中的对应物 |
|-----------------|-----------------|
| Port（端口——业务要什么） | `DocumentReader` ABC——统一的 `read(stream) -> Document` 接口 |
| Adapter（适配器——具体怎么做） | `plugins/` 下的 `PDFReader`、`DocxReader`、`ExcelReader` |
| 核心不依赖细节 | `core/` 只认识 `DocumentReader`，从不 import 具体插件 |
| 资源管控归主程序 | `Extractor` 管文件句柄、超时、并发、异常兜底 |

这套 Port/Adapter 思路在后端工程里无处不在——存储后端可以换（本地磁盘/S3/OSS）、消息队列可以换（Kafka/RabbitMQ）、认证方式可以换（JWT/OAuth/Session）。把这个模式吃透，对后续的 Backend Engineering 是直接可复用的底层认知，而不是孤立的语法练习。

### 8.2 需求总览

**核心功能（对应学习目标的四个要求）：**

| # | 要求 | 说明 |
|---|------|------|
| 1 | 基类 | `DocumentReader(ABC)`——所有插件的统一抽象接口 |
| 2 | 插件注册 | 插件类被定义时自动注册到注册表（扩展名 → 类） |
| 3 | 动态加载 | `load_plugins()` 扫描插件目录、用 `importlib` 导入——主程序不 import 任何具体插件 |
| 4 | 多态调用 | `extractor.extract(path)` 按扩展名路由到对应插件，通过统一接口调用 |

**资源管控（学习目标明确要求——归主程序，不归插件）：**

| # | 要求 | 说明 |
|---|------|------|
| 5 | 文件句柄归主程序 | `Extractor` 负责打开/关闭文件；插件只接收已打开的文件流，**不得自己 open/close** |
| 6 | 超时控制 | `Extractor(timeout=...)`——插件超时抛 `ExtractTimeoutError`，不无限等待 |
| 7 | 并发数量限制 | `Extractor(max_concurrency=...)`——同时执行的解析数有上限 |
| 8 | 异常兜底 | 插件抛的任何异常都被主程序包成统一的 `ExtractError`，不向调用方泄漏 |

**周边：**

- `Document` 数据类（用第六节的 dataclass）
- 三种插件：PDF / DOCX / Excel
- 命令行入口：`python -m doc_extractor <path>`
- 测试、样例文件、README

### 8.3 架构设计

```
                    调用方
                      │ extract(path)
                      ▼
            ┌─────────────────────────┐
            │       Extractor         │  主程序——资源管控层
            │  ├ 文件句柄（open/close） │
            │  ├ 超时、并发上限         │
            │  └ 异常兜底（→ExtractError）│
            └───────────┬─────────────┘
                        │ 只依赖 DocumentReader（Port）
                        │ 按 path.suffix 查注册表
        ┌───────────────┼───────────────┐
        ▼               ▼               ▼
  ┌──────────┐   ┌──────────┐   ┌──────────┐
  │PDFReader │   │DocxReader│   │ExcelReader│  plugins/——Adapter 层
  │(.pdf)    │   │(.docx)   │   │(.xlsx)   │  只做"怎么解析"
  └──────────┘   └──────────┘   └──────────┘
```

**依赖方向是关键：** `core/` 不 import 任何插件；插件 import `core/`（继承 ABC、触发注册）。依赖永远指向核心——这就是六边形架构中"核心不依赖细节，细节依赖核心"。

### 8.4 接口契约

以下签名是**必须严格遵守的契约**——实现时不允许偏离。

#### `Document`——统一输出类型

```python
# core/document.py
from dataclasses import dataclass, field

@dataclass(frozen=True)
class Document:
    """抽取结果——所有插件统一输出这个类型。"""
    text: str
    metadata: dict[str, str] = field(default_factory=dict, compare=False)
    # compare=False 的原因：frozen=True 自动生成的 __hash__ 会对所有参与
    # 相等比较的字段求 hash——而 dict 不可哈希，不排除 metadata 的话
    # hash(doc) 会抛 TypeError。排除后：Document 的"值"由 text 决定，
    # metadata 是辅助信息（页码、作者等），不参与相等判断。
    #
    # frozen：Document 是值对象——创建后不该变
    # 注意浅冻结：metadata 的内容仍可变（6.3 节讲过），但字段不可重新赋值
```

#### 异常层级——两层设计

```python
# core/exceptions.py
class ExtractError(Exception):
    """主程序的统一错误——extract() 的任何失败最终都是它（或其子类）。"""

    def __init__(self, path, fmt: str, cause: Exception | None = None):
        self.path = path
        self.fmt = fmt
        self.cause = cause          # 原始异常——保留完整 cause 链
        msg = f"extract failed: {path} ({fmt})"
        super().__init__(msg if cause is None else f"{msg} -> {cause}")

class UnsupportedFormatError(ExtractError):
    """没有插件支持该扩展名——错误信息必须列出已支持的格式。"""

class ExtractTimeoutError(ExtractError):
    """插件执行超时。"""

class DocumentReaderError(Exception):
    """插件内部解析失败时抛出——这是插件作者报告自己错误的方式。"""
```

**分层的意义：** 插件抛 `DocumentReaderError`（插件作者的语言）→ 主程序包成 `ExtractError`（调用方的语言）。调用方只需要 catch 一个 `ExtractError`，不需要知道 PDF 插件内部会抛什么。

#### `DocumentReader`——Port（基类）

```python
# core/reader.py
from abc import ABC, abstractmethod
from typing import BinaryIO

from .document import Document
from .registry import Registry

class DocumentReader(ABC):
    """Port——所有插件必须继承这个抽象基类。

    插件作者要做的全部事情：
    1. 继承 DocumentReader
    2. 声明 extensions（支持的扩展名）
    3. 实现 read()
    ——注册自动发生（见 __init_subclass__）。
    """

    extensions: tuple[str, ...] = ()
    """支持的扩展名，如 (".pdf",)。"""

    def __init_subclass__(cls, **kwargs):
        """类定义完成时自动注册（3.5 节的模式）。"""
        super().__init_subclass__(**kwargs)
        if not cls._remaining_abstract_methods():
            Registry.register(cls)    # 只有具体类才注册——中间抽象类跳过

    @classmethod
    def _remaining_abstract_methods(cls) -> set[str]:
        """cls 创建完成后还会剩下哪些抽象方法？

        不能直接读 cls.__abstractmethods__，理由见下方"陷阱"说明。
        按 ABCMeta 自己的算法提前算一遍：
        1. 本类新声明的抽象方法；
        2. 父类未实现的抽象方法中，本类没有覆盖成具体实现的。
        """
        abstract = {
            name for name, value in vars(cls).items()
            if getattr(value, "__isabstractmethod__", False)
        }
        for base in cls.__bases__:
            for name in getattr(base, "__abstractmethods__", frozenset()):
                if getattr(getattr(cls, name, None), "__isabstractmethod__", False):
                    abstract.add(name)
        return abstract

    @abstractmethod
    def read(self, stream: BinaryIO) -> Document:
        """从已打开的文件流解析出 Document。

        契约（必须遵守）：
        - stream 由主程序打开并负责关闭——插件【不得】关闭它
        - 解析失败时抛 DocumentReaderError（其他异常主程序也会兜底）
        - 实现必须无状态——read() 不得依赖或修改实例状态
        """
        ...
```

> **⚠️ 陷阱：`cls.__abstractmethods__` 在 `__init_subclass__` 里必然 AttributeError——不是代码问题，是 CPython 的刻意设计。**
>
> 天经地义的写法 `if not cls.__abstractmethods__:` 在这里会炸，两个事实叠加：
>
> 1. **时机**：`__init_subclass__` 在 `type.__new__` 内部执行，而 ABCMeta 要等它返回之后，才把 `__abstractmethods__` 写进新类自己的 `__dict__`——那一刻属性还不存在。
> 2. **特殊查找规则（bpo-10006）**：CPython 对这个名字的类属性查找不走 MRO——只在类自己的 `__dict__` 里找，找不到就直接抛 AttributeError。原因是 `type` 元类身上带有一个同名描述符，如果允许沿 MRO 查找，所有类都会继承到它。后果：普通类属性（比如 `x`）在那一刻能正常沿 MRO 找到父类的值，唯独 `__abstractmethods__` 不行。
>
> 动手验证：在任何 ABC 的 `__init_subclass__` 里 `print(cls.__abstractmethods__)`，再定义一个具体子类——子类的定义语句本身就会抛 AttributeError（哪怕父类明确有这个属性，实验里 `parent.__abstractmethods__` 一切正常）。
>
> 两个看似能用的绕法都要警惕：`getattr(cls, "__abstractmethods__", frozenset())` 会静默拿到默认值——**中间抽象类也被注册**，fail-open 比崩溃更糟（静默错误）；`inspect.isabstract(cls)` 在新版 CPython 被专门修复过（实测 3.12 正确），但本项目手写算法，把机制摊开在明面上。

#### `Registry`——注册表

```python
# core/registry.py
from typing import TYPE_CHECKING

if TYPE_CHECKING:                      # 只给类型检查器用——避免循环 import
    from .reader import DocumentReader

class Registry:
    """扩展名 → 插件类的映射。"""

    _readers: dict[str, "type[DocumentReader]"] = {}

    @classmethod
    def register(cls, reader_cls: "type[DocumentReader]") -> None:
        """注册插件类。重复扩展名立即报错——fail fast。"""
        if not reader_cls.extensions:
            raise ValueError(f"{reader_cls.__name__} must declare extensions")
        for ext in reader_cls.extensions:
            if not (isinstance(ext, str) and ext.startswith(".")):
                raise ValueError(f"invalid extension {ext!r}: must be str starting with '.'")
            if ext in cls._readers:
                raise ValueError(
                    f"extension {ext!r} already registered by {cls._readers[ext].__name__}"
                )
            cls._readers[ext] = reader_cls

    @classmethod
    def get(cls, extension: str) -> "type[DocumentReader] | None":
        """按扩展名查插件——没有返回 None。"""
        return cls._readers.get(extension)

    @classmethod
    def supported_formats(cls) -> list[str]:
        """已注册的全部扩展名——给错误信息用。"""
        return sorted(cls._readers)

    @classmethod
    def clear(cls) -> None:
        """清空注册表——测试用（每个测试重新开始）。"""
        cls._readers.clear()
```

#### `Extractor`——主程序（资源管控 + 多态调用）

```python
# core/extractor.py
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeout
from pathlib import Path

from .document import Document
from .exceptions import ExtractError, ExtractTimeoutError, UnsupportedFormatError
from .registry import Registry

class Extractor:
    """主程序——资源管控层。管：文件句柄、超时、并发上限、异常兜底。
    不管：怎么解析（那是插件的事）。"""

    def __init__(self, timeout: float = 30.0, max_concurrency: int = 4):
        self._timeout = timeout
        # ThreadPoolExecutor 一石二鸟：
        # max_workers 限制并发数；future.result(timeout) 实现超时
        self._executor = ThreadPoolExecutor(max_workers=max_concurrency)

    def extract(self, path: Path | str) -> Document:
        path = Path(path)
        reader_cls = Registry.get(path.suffix)
        if reader_cls is None:
            raise UnsupportedFormatError(path, path.suffix)
        future = self._executor.submit(self._run, reader_cls(), path)
        try:
            return future.result(timeout=self._timeout)
        except FutureTimeout:
            raise ExtractTimeoutError(path, path.suffix) from None

    def _run(self, reader, path: Path) -> Document:
        """在线程池中执行：打开文件 → 多态调用 → 异常兜底。"""
        try:
            with open(path, "rb") as stream:      # 文件句柄——主程序管
                return reader.read(stream)        # 多态调用——只认 ABC 接口
        except Exception as e:
            raise ExtractError(path, path.suffix, e) from e
```

**注意超时的一个诚实的细节：** Python 线程无法被强杀——超时只是"调用方不等了"，线程池里的任务还会继续跑完，文件在任务结束时正常关闭。超时保护的是**调用方**不被无限阻塞，不是取消底层工作。

### 8.5 关键设计决策

#### 决策 1：注册机制用 `__init_subclass__` 而不是装饰器

| | `__init_subclass__`（本项目采用） | 装饰器 `@register` |
|---|---|---|
| 注册时机 | 类定义完成时自动 | 装饰器显式调用 |
| 忘记注册的风险 | **无** | 有——忘了加装饰器，插件静默失效 |
| 新增插件的样板代码 | 零 | 每个类多一行 |
| 灵活性 | 继承即注册，耦合在基类上 | 可以注册非子类（如第三方类） |

选择自动注册的理由：**"插件存在但不生效"是插件系统最危险的事故**——它静默失败，要等到某个文件抽取不出来才发现。`__init_subclass__` 从机制上消灭了"忘记注册"这类错误。这是 3.5 节学过的模式在本项目中的实战应用。

#### 决策 2：`read(stream: BinaryIO)` 而不是 `read(path)`

资源边界表达在类型签名上。`BinaryIO` 的意思是"**已经打开**的文件对象"——插件物理上拿不到打开文件的资格，只有解析的资格。如果传 path，插件就得自己 open——句柄泄漏、忘记 close、路径校验的责任全都下放到每个插件重复实现。主程序统一管资源，插件只管解析——这就是"资源管控归主程序"的落地方式。

#### 决策 3：错误分两层（`DocumentReaderError` → `ExtractError`）

插件抛自己的错误（插件作者的语言），主程序统一包装（调用方的语言）。调用方只需 `except ExtractError` 一个分支——不管未来增加多少插件、插件内部怎么失败，调用方的错误处理代码永远不变。这是"异常兜底"的实现方式，也是 OCP（开放封闭）在错误处理上的体现。

#### 决策 4：`extract_many` 不能复用 `extract()`——线程池嵌套死锁

如果要实现批量抽取 `extract_many(paths)`，**不能**写成：

```python
# ❌ 死锁陷阱！
def extract_many(self, paths):
    return [self.extract(p) for p in paths]
# 用 ThreadPoolExecutor 并发版本时：extract 提交的嵌套任务在等待池中
# 的空闲 worker，而所有 worker 都在等 extract 返回——互相等待，死锁
```

正确做法：`extract_many` 直接 submit 底层任务 `self._run(...)`，不要经过 `extract()`。这是线程池编程的经典陷阱——嵌套提交到同一个池。

### 8.6 项目结构

项目放在 `示例代码/plugin_system/`，与 `collection_lib/` 并列：

```
plugin_system/
├── pyproject.toml
├── README.md
├── src/
│   └── doc_extractor/
│       ├── __init__.py
│       ├── __main__.py            # CLI 入口——python -m doc_extractor <path>
│       ├── core/                  # 核心——不依赖任何具体插件
│       │   ├── __init__.py
│       │   ├── document.py        # Document 数据类
│       │   ├── exceptions.py      # 两层异常体系
│       │   ├── reader.py          # DocumentReader ABC + 自动注册
│       │   ├── registry.py        # 扩展名 → 类 注册表
│       │   ├── loader.py          # importlib 动态加载
│       │   └── extractor.py       # 主程序——资源管控 + 分发
│       └── plugins/               # 插件目录——新增格式只改这里
│           ├── __init__.py
│           ├── pdf_reader.py
│           ├── docx_reader.py
│           └── excel_reader.py
├── samples/                       # 样例文件（.pdf/.docx/.xlsx 各一个）
└── tests/
    ├── test_document.py
    ├── test_registry.py
    ├── test_loader.py
    ├── test_extractor.py
    └── test_plugins.py
```

依赖（pyproject.toml）：`pypdf`、`python-docx`、`openpyxl`（解析用）；dev 依赖加 `pytest`、`reportlab`（生成 PDF 样例用）。

### 8.7 验收标准（毕业标准）

逐条自测，全部通过才算完成：

1. **零修改扩展**：新增一种格式支持 = 在 `plugins/` 下新增一个文件，`core/` 和 CLI 零修改。实际演示一次（例如新增 `MarkdownReader`）来证明。
2. **三种格式可用**：`.pdf`、`.docx`、`.xlsx` 各能正确抽取文本内容。
3. **不支持格式有结构化错误**：`UnsupportedFormatError`，错误信息包含该扩展名和已支持的格式列表。
4. **文件句柄契约**：代码评审确认——所有插件代码中没有任何 `open()`/`close()` 调用。
5. **超时生效**：写一个 `sleep` 的慢插件，`Extractor(timeout=0.1)` 调用它 → 收到 `ExtractTimeoutError`，不无限等待。
6. **并发限制生效**：`max_concurrency=1` 时，同时只有一个 `read()` 在执行（测试用计数器验证）。
7. **异常兜底**：插件抛任意异常（包括非 `DocumentReaderError` 的），调用方收到的都是 `ExtractError`，且 `cause` 链完整可追溯。
8. **坏插件容错**：`plugins/` 里放一个 import 会失败的模块，`load_plugins()` 不中断，其余插件正常工作。
9. **重复注册 fail fast**：两个插件声明同一个扩展名 → 导入时报 `ValueError`。
10. **测试通过**：核心路径（注册、加载、分发、超时、兜底）有测试覆盖。
11. **CLI 可运行**：`python -m doc_extractor samples/sample.pdf` 输出抽取的文本。

### 8.8 分步实施指南

| 步骤 | 内容 | 用到的教程章节 |
|------|------|---------------|
| 1 | 项目骨架：`pyproject.toml` + src 布局 | 参照 collection_lib |
| 2 | `Document` 数据类 + `test_document.py` | 六、数据类 |
| 3 | `DocumentReader` ABC + `Registry` + 自动注册 + `test_registry.py` | 五、抽象；3.5 `__init_subclass__` |
| 4 | 三个插件 + `test_plugins.py` | 四、多态；二、封装 |
| 5 | `loader.py` 动态加载 + `test_loader.py` | 8.5 决策 4 |
| 6 | `Extractor` 资源管控 + `test_extractor.py` | 8.4 契约 |
| 7 | CLI + samples + README | — |
| 8 | 按 8.7 验收标准逐条自测 | — |

**建议实现顺序：** 先跑通"一个插件、无动态加载、无超时"的最小闭环（步骤 2-4 + 简化版 Extractor），再逐步加 loader 和资源管控。每步都有对应测试，测试先行能让你每一步都确信自己没把之前的搞坏。