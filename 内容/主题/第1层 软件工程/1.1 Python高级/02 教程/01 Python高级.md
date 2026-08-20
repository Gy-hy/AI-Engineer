# Python高级

> 本文件承载 `1.1 Python高级` 这一大块教程内容。
>
> 后续只继续补 `OOP`、`typing`、`asyncio` 这类同层级大章节，不把 `数据模型` 继续单独拆出去。

## 一、数据模型

### 1.1 一切皆对象

**一句话定义：** 在 Python 中，你操作的每一个东西都是对象——不只是 `class` 定义的实例，连 `int`、`str`、函数、类本身、模块、甚至 `type` 都是对象。每个对象都有**身份（identity）、类型（type）、值（value）** 三元组。

---

#### 是什么：从具体到抽象的逐层验证

**第一层：基本数据类型是对象**

```python
>>> x = 42
>>> type(x)          # <class 'int'>
>>> dir(x)           # 有一堆魔术方法，比如 __add__, __str__, __repr__
>>> x.__add__(1)     # 43。本质上 x + 1 就是调 x.__add__(1)
```

你写的 `x + 1`，Python 在底层执行的是 `x.__add__(1)`——`+` 只是语法糖，`int` 是一个完整的对象，有方法、有属性。

**第二层：函数是对象**

```python
>>> def greet(name):
...     return f"Hello, {name}"
...
>>> type(greet)       # <class 'function'>
>>> greet.__name__    # 'greet'
>>> greet.__code__    # <code object>——函数的字节码
>>> greet.__dict__    # {}——函数也可以挂属性
>>> greet.version = "1.0"   # 往函数上挂属性，完全合法
>>> greet.version     # '1.0'
```

函数可以赋值给变量、放进 list、作为参数传递——因为函数**就是**对象，`def` 只是创建了一个 `function` 类型的实例。

**第三层：类本身也是对象**

```python
>>> class Dog:
...     pass
...
>>> type(Dog)         # <class 'type'>
>>> Dog.__bases__     # (<class 'object'>,)
>>> Dog.__dict__      # mappingproxy 装着类属性和方法
```

`class Dog` 执行时，Python 调用了 `type()` 来**动态创建一个类对象**。类就是一个 `type` 的实例。这也解释了为什么元类（metaclass）是 `type` 的子类——元类就是"用来创建类的类"。

**第四层：连 `type` 自己都是对象**

```python
>>> type(type)        # <class 'type'>
>>> type(object)      # <class 'type'>
>>> isinstance(object, type)  # True
>>> isinstance(type, object)  # True
```

这是一个自洽的闭环：`type` 是 `type` 的实例，`object` 是 `type` 的实例，`type` 继承自 `object`。这条关系链构成了 Python 整个对象模型的根。

---

#### 为什么要谈这个：工程意义

(a) **赋值 = 绑定标签，不是复制数据**

```python
>>> a = [1, 2, 3]
>>> b = a        # b 和 a 指向同一个对象
>>> b.append(4)
>>> a            # [1, 2, 3, 4]——a 也变了！
```

`a = [1, 2, 3]` 不是"把数据放进变量 a"，而是"在内存中创建一个 list 对象，然后把标签 `a` 贴到这个对象上"。`b = a` 是"再贴一个标签 `b` 到同一个对象上"，没有复制任何数据。这是理解和避免 Python 中最常见 bug 的核心认知。

(b) **可变对象 vs 不可变对象的本质**

```python
# 不可变对象：int, str, tuple, bytes, frozenset(不可变集合，可作为字典的 key 或集合的元素)
>>> a = "hello"
>>> a[0] = "H"    # TypeError: 'str' object does not support item assignment

# 可变对象：list, dict, set, bytearray
>>> b = [1, 2, 3]
>>> b[0] = 99     # 没问题
```

不可变对象一旦创建，其值就不能改变。任何"修改"操作实际上是创建了一个新对象：

```python
>>> a = "hello"
>>> id(a)              # 4352013296
>>> a = a + " world"   # 这不是修改，是创建了新对象
>>> id(a)              # 4352013424——不同的 id！
```

工程上的影响：
- **不可变对象是线程安全的**——多线程读写同一个 `str` 或 `tuple` 不需要加锁，因为没人能改它。
- **可变对象做默认参数是经典陷阱**——函数定义时默认参数只求值一次，之后每次调用共享同一个可变对象：

```python
>>> def add_item(item, target=[]):  # 危险！
...     target.append(item)
...     return target
>>> add_item(1)   # [1]
>>> add_item(2)   # [1, 2]——不是 [2]！同一个 list 对象被复用了
```

正确的写法：

```python
>>> def add_item(item, target=None):
...     if target is None:
...         target = []
...     target.append(item)
...     return target
```

---

### 1.2 对象引用与拷贝

```python
>>> import copy
>>> a = [[1, 2], [3, 4]]

>>> b = a                # 引用：b 和 a 是同一个对象
>>> b = list(a)          # 浅拷贝：外层 list 是新的，内层 list 还是共享的
>>> b = copy.deepcopy(a) # 深拷贝：完完全全独立的一份
```

**浅拷贝 vs 深拷贝的直观验证：**

```python
>>> import copy
>>> a = [[1, 2], [3, 4]]
>>> b = copy.copy(a)     # 浅拷贝

>>> a is b               # False——外层 list 不是同一个
>>> a[0] is b[0]         # True——但内层 list 还是共享的！

>>> a[0].append(99)
>>> b[0]                 # [1, 2, 99]——b 也被影响了
```

```python
>>> c = copy.deepcopy(a) # 深拷贝
>>> a[1] is c[1]         # False——内层也完全独立了
```

**工程场景：** 但凡函数接收可变参数且内部要修改它，要么用 `copy()`，要么返回新对象，不要原地修改入参——这会让调用方受到意料之外的副作用。

---

### 1.3 `id()`、`is`、`==`

| 操作 | 比较的是什么 | 底层调用 |
|------|------------|----------|
| `a is b` | 身份（两个名字是否指向同一个内存对象） | `id(a) == id(b)` |
| `a == b` | 值（两个对象的内容是否相等） | `a.__eq__(b)` |
| `id(a)` | 对象的内存地址（CPython 实现细节） | — |

```python
>>> a = [1, 2, 3]
>>> b = [1, 2, 3]
>>> a == b    # True——值相等
>>> a is b    # False——不是同一个对象
>>> a is None # 正确的单例比较方式
>>> a == None # 也能用，但 is 更快且不会被 __eq__ 覆盖
```

**关键原则：`is` 用于单例/身份比较，`==` 用于值比较。**

**工程陷阱——小整数缓存：**

```python
>>> a = 256
>>> b = 256
>>> a is b    # True——CPython 内部缓存了小整数 [-5, 256]

>>> a = 257
>>> b = 257
>>> a is b    # False——超过缓存范围，两个不同的对象
```

这不只是面试题。真实代码里如果用 `is` 比较数字、字符串、或其他"看起来像值"的东西，结果在不同 CPython 版本下可能不一致。**永远用 `==` 比较值。**

**字符串的 intern 机制也是同样的道理：**

```python
>>> a = "hello"
>>> b = "hello"
>>> a is b    # True——短字符串会被 intern，共享同一个对象

>>> a = "hello world!" * 1000
>>> b = "hello world!" * 1000
>>> a is b    # False——长字符串不一定被 intern
```

---

### 1.4 `__dict__` —— 对象属性的存储机制

因为"一切皆对象"，每个对象都需要存储自己的属性。默认方式是用 `__dict__`——每个实例自带一个字典：

```python
>>> class Point:
...     def __init__(self, x, y):
...         self.x = x
...         self.y = y
...
>>> p = Point(1, 2)
>>> p.__dict__    # {'x': 1, 'y': 2}
>>> p.z = 3       # 动态添加属性——因为 __dict__ 就是普通字典
>>> p.__dict__    # {'x': 1, 'y': 2, 'z': 3}
```

**代价：** 每个 `__dict__` 大约消耗 240 bytes（空字典的开销）。如果你创建几百万个小对象，光是 `__dict__` 自身就能吃掉上百 MB 内存。

---

### 1.5 `__slots__` —— 关闭字典，用数组存属性

当你知道一个类只有固定的几个属性，可以用 `__slots__` 直接告诉 Python："不要建字典，用 C 数组的方式存"：

```python
>>> class PointSlots:
...     __slots__ = ('x', 'y')
...     def __init__(self, x, y):
...         self.x = x
...         self.y = y
...
>>> p = PointSlots(1, 2)
>>> p.__dict__    # AttributeError: 'PointSlots' object has no attribute '__dict__'
>>> p.z = 3       # AttributeError: 不能再动态添加属性了
```

**效果对比：**

| | 默认 `__dict__` | `__slots__` |
|---|---|---|
| 属性存储 | 字典（flexible） | C 数组（fixed） |
| 每个实例内存开销 | ~240 bytes（空 dict） | 几乎没有额外开销 |
| 能否动态添加属性 | 能 | 不能 |
| 属性访问速度 | 字典查找 | 数组偏移（更快） |

**工程决策：** 当你定义的是"大量创建的小型数据对象"（比如一个游戏里的坐标 Point、一个金融系统中的 Tick 数据点），`__slots__` 的内存和性能收益是显著的。当你定义的是一般性的业务对象（创建数量少，可能需要灵活的属性），默认的 `__dict__` 就够了。

---

### 1.6 引用计数

每个 Python 对象内部维护一个引用计数器。基于"一切皆对象"的前提，这个计数器跟踪"有多少个地方在引用这个对象"：

```python
>>> import sys
>>> a = []
>>> sys.getrefcount(a)    # 2（a 持有 1 个 + getrefcount 的临时参数）
>>> b = a
>>> sys.getrefcount(a)    # 3（a, b, 临时参数）
>>> del b
>>> sys.getrefcount(a)    # 2
```

**规则：** 当引用计数归零时，对象被立即回收（`__del__` 被调用，内存归还给操作系统）。

**引用计数的增/减场景：**
- 增：赋值 `a = obj`、传参 `func(obj)`、放入容器 `list.append(obj)`
- 减：`del a`、变量离开作用域、容器被销毁或元素被移除

**优点：** 回收是即时的、确定性的——不像 Java/C# 依赖 GC 在不确定的时间点触发。
**缺陷：** 处理不了循环引用。

---

### 1.7 垃圾回收（GC）

引用计数处理不了**循环引用**：

```python
>>> a = []
>>> b = []
>>> a.append(b)   # a 引用 b
>>> b.append(a)   # b 引用 a
>>> del a
>>> del b
# 此时 a 和 b 的引用计数都不为 0（它们互相引用），
# 但外部已经没有任何人能访问它们了——这就是"不可达的循环引用"
```

CPython 的解决方案是**分代垃圾回收（Generational GC）**：

```python
>>> import gc
>>> gc.get_threshold()   # (700, 10, 10)
# generation 0: 新创建的对象，当数量超过 700 时触发回收
# generation 1: 经历过一次 GC 还活着的，当数量超过 10 时触发
# generation 2: 经历过两次 GC 还活着的，当数量超过 10 时触发
```

**核心思想：** 大部分对象是短命的（"朝生暮死"假说），所以 GC 主要扫描新对象（generation 0），老对象不常扫描，减少 GC 开销。

**GC 只处理容器对象**（list、dict、set、自定义类实例等可能产生循环引用的类型），`int`、`str` 这类不可变基础类型不参与 GC——它们只靠引用计数回收。

**工程实践：**
```python
# 通常不需要手动干预，但了解这些 API 是必要的：
>>> gc.collect()        # 手动触发一次完整的垃圾回收
>>> gc.disable()        # 禁用自动 GC（极端性能场景）
>>> gc.set_threshold(1000, 15, 15)  # 调高阈值，减少 GC 频率
```

**什么时候需要关心 GC？**
- 大规模数据处理：频繁创建大量容器对象，GC 可能成为性能瓶颈
- 性能分析时 `cProfile` 显示大量时间消耗在 `gc.collect` 上
- 实现了 `__del__` 且对象参与循环引用——GC 不会回收这类对象（Python 3.4+ 改善了但仍有陷阱）

---

### 1.8 总结

"一切皆对象"不是一句哲学口号，它直接决定了以下每一条在工程中的实际行为：

| 你写的代码 | 因为"一切皆对象"所以 |
|------------|----------------------|
| `b = a` | 绑定新标签到同一个对象，不是复制 |
| `a is b` | 比较的是 id，不是值 |
| `a == b` | 调用 `__eq__`，比较的是值 |
| `a.__dict__` | 实例属性存在一个 dict 里（默认） |
| `__slots__` | 关闭 dict，用 C 数组存属性，省内存 |
| `del a` | 减少引用计数，不是手动释放内存 |
| GC 偶尔触发 | 正在清理循环引用 |
| `def` / `class` | 都是在创建对象（function 对象 / type 对象） |

理解到这个层面，才能像课程目标说的——**"具备编写大型 Python 工程的能力，而不是只会写脚本"**。

---

## 二、Python 内置数据结构

> **目标：不只是"会用"，而是理解每个结构的底层实现、时间复杂度、以及什么时候该用它。**

---

### 2.1 时间复杂度速查总表

这是你每次选数据结构时都应该在脑子里过一遍的表：

| 操作 | `list` | `tuple` | `dict` | `set` | `deque` |
|------|--------|---------|--------|-------|---------|
| 按下标访问 | O(1) | O(1) | — | — | O(1)（两端）|
| 按 key 查找 | — | — | O(1) 平均 | O(1) 平均 | — |
| 末尾插入 | O(1) 摊销 | — | O(1) 平均 | O(1) 平均 | O(1) |
| 头部插入 | O(n) | — | O(1) 平均 | O(1) 平均 | O(1) |
| 中间插入 | O(n) | — | O(1) 平均 | O(1) 平均 | O(n) |
| 删除 | O(n) | — | O(1) 平均 | O(1) 平均 | O(1) 两端 / O(n) 中间 |
| 成员判断 `x in` | O(n) | O(n) | O(1) 平均 | O(1) 平均 | O(n) |
| 遍历 | O(n) | O(n) | O(n) | O(n) | O(n) |
| 内存开销 | 低 | 最低 | 较高 | 较高 | 中等 |

**这张表不是用来背的——是用来在每一次写代码前帮你多想一步的。** 比如你看到一段代码在一个 `list` 上反复做 `x in items`，就该立刻意识到这是 O(n²)，该换成 `set`。

---

### 2.2 基础结构

#### 2.2.1 list —— 动态数组

**底层实现：** C 层面的 `PyObject*` 指针数组。CPython 会预分配超出当前长度的空间（over-allocate），所以 `append` 大部分时候是 O(1)，但偶尔触发 realloc 时是 O(n)（摊销后仍是 O(1)）。

```python
# 内部结构示意（不是 Python 代码，是 C 层面的逻辑）
# list 对象内部：
#   ob_item: [*ptr_to_obj0, *ptr_to_obj1, *ptr_to_obj2, NULL, NULL, NULL, NULL, NULL]
#                              ↑ allocated = 8
#              ↑ ob_size = 3
# append 时如果 ob_size < allocated，直接写指针 O(1)
# append 时如果 ob_size == allocated，先 realloc 扩容（新容量 ≈ old * 1.125 + 3），再写 O(n)
```

```python
>>> import sys
>>> lst = []
>>> sys.getsizeof(lst)    # 56——空 list 本身的开销（64 位 CPython）
>>> lst.append(1)
>>> sys.getsizeof(lst)    # 88——预分配了空间
>>> for i in range(10):
...     lst.append(i)
>>> sys.getsizeof(lst)    # 152——动态扩容
```

**关键操作复杂度背后的原因：**

| 操作 | 复杂度 | 原因 |
|------|--------|------|
| `lst[i]` | O(1) | 指针数组 + 偏移量，一步算出地址 |
| `lst.append(x)` | O(1) 摊销 | 预分配空间，偶尔扩容 |
| `lst.insert(0, x)` | O(n) | 插入位置的右侧所有元素都要往右挪一位 |
| `lst.pop()` | O(1) | 只删最后一个，不需要挪动其他元素 |
| `lst.pop(0)` | O(n) | 删除第一个，后面所有元素往左挪一位 |
| `x in lst` | O(n) | 线性扫描，没捷径 |
| `lst.remove(x)` | O(n) | 先 O(n) 找到位置，再 O(n) 挪动后面元素 |

**工程陷阱——迭代中删除：**

```python
>>> lst = [1, 2, 3, 4, 5]
>>> for x in lst:
...     if x % 2 == 0:
...         lst.remove(x)
>>> lst
[1, 3, 5]  # 看起来对了？但把列表加长试试：
>>> lst = [1, 2, 4, 3, 5]
>>> for x in lst:
...     if x % 2 == 0:
...         lst.remove(x)
>>> lst
[1, 4, 3, 5]  # 4 被跳过了！因为迭代器不知道你改了列表
# for 循环其实就是在不断调用迭代器的 __next__() 方法，next()使用的是index，而不是内存地址。
```

正确做法——列表推导式（创建新列表）：

```python
>>> lst = [1, 2, 4, 3, 5]
>>> lst = [x for x in lst if x % 2 != 0]
>>> lst
[1, 3, 5]
```

**使用场景：**
- 需要按下标随机访问 → `list`
- 数据量不大，频繁在末尾增删 → `list`
- 需要保持插入顺序 → `list`
- 需要在头部或中间频繁增删 → **不要用 list，用 deque 或自己实现链表**

---

#### 2.2.2 tuple —— 不可变数组

**底层实现：** 和 list 几乎一样的 C 层面指针数组，但**不可变**——没有 `append`、`insert`、`remove` 等方法，创建后就不能改了。

```python
>>> t = (1, 2, 3)
>>> t[0]         # 1——支持下标访问 O(1)
>>> t[0] = 99    # TypeError: 'tuple' object does not support item assignment
```

**tuple 和 list 的真正区别不是"能不能改"，而是语义：**

| 用 list | 用 tuple |
|---------|----------|
| "这是一组同类的、数量可能变化的东西" | "这是一个有固定结构的记录" |
| 比如：用户列表、日志行 | 比如：坐标 `(x, y)`、RGB 颜色 `(255, 128, 0)`、数据库一行 |
| 遍历、过滤、变换 | 解包、当作 dict 的 key、当作函数的多个返回值 |

**tuple 可以做 dict 的 key，list 不能：**

```python
>>> d = {}
>>> d[(1, 2)] = "point A"   # OK——tuple 是可哈希的
>>> d[[1, 2]] = "point A"   # TypeError: unhashable type: 'list'
```

原因是 dict 的 key 必须不可变——key 的 hash 值一旦计算好就不能变了，否则 dict 内部就找不到它了。

**单元素 tuple 的陷阱：**

```python
>>> t = (1)      # 这不是 tuple！这是带括号的 int
>>> type(t)      # <class 'int'>
>>> t = (1,)     # 这才是 tuple——逗号才是 tuple 的标志，不是括号
>>> type(t)      # <class 'tuple'>
```

**解包（unpacking）：**

```python
>>> x, y, z = (1, 2, 3)    # 基本解包
>>> a, *rest = (1, 2, 3, 4) # a=1, rest=[2, 3, 4]
>>> *head, tail = (1, 2, 3)  # head=[1, 2], tail=3
```

tuple 比 list 更省内存（因为没有预分配空间），加上不可变带来的线程安全和哈希能力，工程里能优先用 tuple 就该用。

---

#### 2.2.3 dict —— 哈希表

**底层实现：** CPython 3.6+ 使用**紧凑哈希表**——entry 数组（存储 key 的 hash、key 指针、value 指针）+ indices 数组（稀疏→紧凑的映射）。PyPy 首创，CPython 3.6 实现，Python 3.7 正式成为语言保证：**dict 保持插入顺序**。

```python
>>> d = {}
>>> d["a"] = 1
>>> d["b"] = 2
>>> d["c"] = 3
>>> list(d.keys())   # ['a', 'b', 'c']——按插入顺序，Python 3.7+ 保证
```

**关键操作的内部原理：**

```python
# 查找 d[key] 的过程：
# 1. 计算 hash(key)
# 2. hash % table_size → 起始索引 i
# 3. 检查 indices[i] 对应的 entry 是否匹配（先比 hash，hash 相同再比 key ==）
# 4. 如果冲突（不同 key 的 hash 落到同一个槽），线性探测找下一个空槽
# 5. 找到 → 返回值；没找到 → KeyError
```

**时间复杂度：**
- 查找/插入/删除：O(1) 平均，O(n) 最坏（所有 key 的 hash 都冲突，退化为链表）
- 成员判断 `k in d`：O(1) 平均

**dict 能作为 switch-case 替代：**

```python
# 不用 dict：每次 O(n) 判断
def handle(event_type):
    if event_type == "click":
        return handle_click()
    elif event_type == "scroll":
        return handle_scroll()
    elif event_type == "keydown":
        return handle_keydown()
    # ... 再加 10 个 elif

# 用 dict：O(1) 分发
handlers = {
    "click": handle_click,
    "scroll": handle_scroll,
    "keydown": handle_keydown,
}
handler = handlers.get(event_type, default_handler)
handler()
```

**常用方法速查：**

```python
d.get(key, default)      # 安全取值，不存在时返回 default 而不是抛异常
d.setdefault(key, val)   # key 不存在才设值，返回当前值（很适合做缓存/分组）
d.pop(key, default)      # 取出并删除
d.popitem()              # 弹出最后一个键值对（LIFO，Python 3.7+ 保证）
d.update(other_dict)     # 合并另一个 dict
d | other                # Python 3.9+：合并两个 dict 并返回新 dict
d |= other               # Python 3.9+：就地合并
```

**遍历性能注意事项：**

```python
# ✅ 好：直接遍历
for key in d:
    v = d[key]

# ✅ 也好：同时需要 key 和 value
for key, value in d.items():
    pass

# ❌ 差：O(n²)——每次检查 key 都在遍历
for key in d:
    if key in d:  # 多余！已经在遍历了
        pass
```

---

#### 2.2.4 set —— 无重复元素的哈希集合

**底层实现：** 和 dict 共享同一套哈希表实现——set 本质上就是一个只有 key 没有 value 的 dict。所以它的性能特性和 dict 几乎一样。

```python
>>> s = {1, 2, 3, 3, 3}
>>> s               # {1, 2, 3}——自动去重
>>> 2 in s          # True——O(1) 平均
>>> s.add(4)        # O(1)
>>> s.remove(2)     # O(1)
```

**set 最核心的价值：O(1) 的去重和集合运算**

```python
# 去重：O(n) vs 手写循环 O(n²)
>>> items = [1, 2, 2, 3, 3, 3]
>>> unique = list(set(items))    # [1, 2, 3]，但顺序不保证
>>> unique = list(dict.fromkeys(items))  # [1, 2, 3]，且保持原顺序

# 集合运算——用方法而不是写循环
>>> a = {1, 2, 3, 4}
>>> b = {3, 4, 5, 6}
>>> a & b      # {3, 4}——交集
>>> a | b      # {1, 2, 3, 4, 5, 6}——并集
>>> a - b      # {1, 2}——差集（a 有但 b 没有）
>>> a ^ b      # {1, 2, 5, 6}——对称差（只在一边的）
>>> a <= b     # False——a 是 b 的子集吗？
```

**工程场景：**

```python
# 两个 10 万行的文件，找出交集：
# ❌ 差：双重循环 O(n²)，跑几个小时
# ✅ 好：set(a_list) & set(b_list)，O(n)，秒出

# 大量数据的成员判断：
# ❌ 用 list：`if item in huge_list` 每次 O(n)
# ✅ 用 set：`if item in huge_set` 每次 O(1)
```

**可哈希（hashable）≠ 不可变（immutable）——这是两个独立的概念，不能混用。**

一个对象是"可哈希的"，当且仅当：

1. 它实现了 `__hash__()` 方法（返回一个整数）
2. 它实现了 `__eq__()` 方法（用于比较相等性）
3. **关键约束：** 在其整个生命周期内，`__hash__()` 的返回值必须保持不变——否则 dict/set 的内部哈希表会被破坏（对象存进去时在一个桶，hash 变了之后在另一个桶里找，永远找不到）

Python 内置可变类型（`list`、`dict`、`set`）之所以不可哈希，是因为它们故意把 `__hash__` 设为了 `None`——这是一种**设计选择**，不是"可变就一定不可哈希"的物理定律：

```python
>>> hash([1, 2, 3])       # TypeError: unhashable type: 'list'
>>> hash({"a": 1})        # TypeError: unhashable type: 'dict'
>>> hash({1, 2, 3})       # TypeError: unhashable type: 'set'

# 但不可变 ≠ 一定可哈希：
>>> t = (1, 2, [3, 4])    # tuple 是不可变的，但包含了可变的 list
>>> hash(t)                # TypeError: unhashable type: 'list'——因为 t 的 hash 依赖于内部 list

# 反过来，你自己写的类默认是可哈希的，即使它是可变的：
>>> class MutablePoint:
...     def __init__(self, x, y):
...         self.x = x
...         self.y = y
...
>>> p = MutablePoint(1, 2)
>>> hash(p)       # 正常返回——默认用 id() 作为 hash
>>> d = {p: "A"}
>>> p.x = 999     # 对象变了，但 hash 没变（还是那个 id）——所以 dict 不受影响
```

**正确的理解：**
- `int`、`str`、`bytes`、`frozenset`：不可变，且可哈希 ✅
- `tuple`：本身不可变，但**只有当它包含的所有元素也都可哈希时**，它才是可哈希的
- 你自己定义的类实例：**默认可哈希**（基于 `id()`），即使你往上面随便改属性——但这是把双刃剑：如果用值语义的 `__eq__` 覆盖了默认的基于 `id()` 的相等比较，就必须把 `__hash__` 设为 `None`，否则 dict 行为会错乱
- `list`、`dict`、`set`：内置可变类型，`__hash__` 被显式禁用了

**工程实践：** 如果需要按内容去重自定义对象，用 `dataclass(frozen=True)`——它会自动生成正确的 `__hash__` 实现，且保证实例不可变，从根源上避免 hash 漂移问题。

---

### 2.3 collections 模块 —— 工程中真正常用的结构

上面的 `list`、`tuple`、`dict`、`set` 是基础，下面的才是你在后端工程里天天会碰到的。

#### 2.3.1 deque —— 双端队列

**底层实现：** 双向链表组成的块（block）——每个 block 存 64 个元素，blocks 之间用指针连接。这样既保证了双端都是 O(1)，又避免了纯链表的内存碎片和缓存不友好。

```python
from collections import deque

>>> dq = deque([1, 2, 3])
>>> dq.append(4)        # 右端入队 O(1)
>>> dq.appendleft(0)    # 左端入队 O(1)
>>> dq.pop()            # 右端出队 O(1) → 4
>>> dq.popleft()        # 左端出队 O(1) → 0
>>> dq                   # deque([1, 2, 3])
```

**deque vs list 的核心差异：**

```python
# list 头部操作：灾难
>>> lst = list(range(100000))
>>> lst.pop(0)          # O(n)——10 万元素全部左移一位

# deque 头部操作：O(1)
>>> dq = deque(range(100000))
>>> dq.popleft()        # O(1)——只改指针
```

**deque 的参数 `maxlen`：天然适合做定长队列**

```python
>>> from collections import deque
>>> recent = deque(maxlen=5)  # 只保留最近 5 条
>>> for i in range(10):
...     recent.append(i)
>>> recent   # deque([5, 6, 7, 8, 9])——最旧的自动挤出
```

**使用场景：**
- 实现 Queue / Stack → `deque` 同时胜任
- 最近 N 条记录（历史、日志、滑动窗口）→ `deque(maxlen=N)`
- BFS / 树的层序遍历 → `deque.popleft()` O(1)
- 需要"从两端插入/弹出"的任何场景

---

#### 2.3.2 defaultdict —— 带默认值的 dict

**是什么：** `defaultdict` 就是 dict 的子类，重写了 `__missing__` 方法——当 key 不存在时，调用你指定的工厂函数自动生成默认值，而不是抛 `KeyError`。

```python
from collections import defaultdict

# 分组——defaultdict 的经典用法
>>> users = [("北京", "张三"), ("上海", "李四"), ("北京", "王五")]
>>> by_city = defaultdict(list)
>>> for city, name in users:
...     by_city[city].append(name)    # key 不存在时自动创建空 list
>>> dict(by_city)
{'北京': ['张三', '王五'], '上海': ['李四']}

# 不用 defaultdict 的写法——每次都要判断：
>>> by_city = {}
>>> for city, name in users:
...     if city not in by_city:
...         by_city[city] = []
...     by_city[city].append(name)
```

**常用工厂函数：**

| 工厂 | 效果 |
|------|------|
| `defaultdict(list)` | key 不存在 → `[]`，天然适合分组 |
| `defaultdict(int)` | key 不存在 → `0`，天然适合计数 |
| `defaultdict(set)` | key 不存在 → `set()`，天然适合去重归类 |
| `defaultdict(dict)` | key 不存在 → `{}`，天然适合嵌套字典 |
| `defaultdict(lambda: 0)` | 自定义默认值 |

**嵌套 defaultdict——任意深度的字典：**

```python
>>> tree = lambda: defaultdict(tree)
>>> root = tree()
>>> root["a"]["b"]["c"] = 1  # 不需要逐层检查 key 是否存在
```

---

#### 2.3.3 Counter —— 计数器

**是什么：** `dict` 的子类，专门用来计数——"这个元素出现了几次"。

```python
from collections import Counter

>>> c = Counter("abracadabra")
>>> c
Counter({'a': 5, 'b': 2, 'r': 2, 'c': 1, 'd': 1})

# 和 defaultdict(int) 的不同：Counter 自带排序和统计方法
>>> c.most_common(3)       # [('a', 5), ('b', 2), ('r', 2)]——Top N
>>> c.total()              # 11——Python 3.10+ 总计数
>>> c["z"]                 # 0——不存在的 key 返回 0 而不是 KeyError
```

**Counter 的运算——不是玩具，工程里很有用：**

```python
>>> a = Counter("hello")     # Counter({'l': 2, 'h': 1, 'e': 1, 'o': 1})
>>> b = Counter("world")     # Counter({'w': 1, 'o': 1, 'r': 1, 'l': 1, 'd': 1})
>>> a + b                    # 计数相加
>>> a - b                    # 计数相减（负数归零）——比如比较两天的日志差异
>>> a & b                    # 取计数的最小值——两个记录的交集
>>> a | b                    # 取计数的最大值
```

**工程场景：**
- 统计 API 调用频率分布 → `Counter([r.status_code for r in responses])`
- 找出最频繁的报错信息 → `Counter(error_msgs).most_common(10)`
- 比较两个时间段的日志差异 → `counter_today - counter_yesterday`
- 词频统计、用户行为分布

---

#### 2.3.4 OrderedDict —— 能记住插入顺序的字典（了解）

**现在基本被普通 dict 取代了（Python 3.7+ dict 保证插入顺序）**，但仍有几个独特用法。

```python
from collections import OrderedDict

>>> od = OrderedDict()
>>> od["a"] = 1
>>> od["b"] = 2
>>> od["c"] = 3
>>> list(od.keys())   # ['a', 'b', 'c']——这和普通 dict 一样

# OrderedDict 独有的：比较时会考虑顺序
>>> OrderedDict([("a", 1), ("b", 2)]) == OrderedDict([("b", 2), ("a", 1)])
# False！——dict 会认为相等

# OrderedDict 独有的：move_to_end()
>>> od.move_to_end("a")    # 把 "a" 移到最后
>>> list(od.keys())        # ['b', 'c', 'a']

>>> od.move_to_end("a", last=False)  # 把 "a" 移到最前
>>> list(od.keys())        # ['a', 'b', 'c']
```

**什么时候还用 OrderedDict？**
- 实现 LRU Cache 时用 `move_to_end()` 配合 `popitem(last=False)` 非常自然
- 需要按顺序比较两个字典是否"完全一致"的场景

---

#### 2.3.5 ChainMap —— 多层字典的叠加视图（了解）

**是什么：** 把多个字典"叠"在一起，查找时按层依次搜索，修改只影响第一层。最适合"配置覆盖"场景。

```python
from collections import ChainMap

# 经典场景：命令行参数 > 环境变量 > 配置文件 > 默认值
>>> cli_args = {"host": "prod.example.com"}
>>> env_vars = {"port": "5432", "host": "staging.example.com"}
>>> defaults = {"host": "localhost", "port": "8080", "debug": True}

>>> config = ChainMap(cli_args, env_vars, defaults)
>>> config["host"]     # 'prod.example.com'——从 cli_args 优先取
>>> config["port"]     # '5432'——从 env_vars 取
>>> config["debug"]    # True——从 defaults 取

# 修改只影响第一层
>>> config["debug"] = False
>>> defaults["debug"]  # True——不受影响！因为改的是 cli_args（第一层）

# 新增也是写到第一层
>>> config["timeout"] = 30
>>> cli_args           # {'host': 'prod.example.com', 'debug': False, 'timeout': 30}
```

**和 `{**defaults, **env_vars, **cli_args}` 的区别：**
- `ChainMap` 不会复制数据——它只是持有了对原始 dict 的引用，原始 dict 的任何变更都会实时反映出来。合并字典的方式是创建了一个全新的独立副本。
- `ChainMap` 更省内存，且适合"配置源本身可能动态变化"的场景。

**使用场景：**
- 多层配置覆盖（命令行 → 环境变量 → 配置文件 → 默认值）
- 请求级别的上下文覆盖（全局 context + 请求 context 叠加）
- 嵌套作用域模拟（类似 LEGB 规则）

---

### 2.4 heapq —— 堆队列

**是什么：** `heapq` 模块把一个普通 `list` 当作**最小堆**来维护——堆顶 `list[0]` 永远是最小元素。它不是独立的数据结构类，而是一组操作普通 list 的函数。

**底层实现：** 二叉最小堆——用数组存完全二叉树。对于下标 `i` 的元素，其左子节点在 `2*i+1`，右子在 `2*i+2`，父节点在 `(i-1)//2`。

```python
import heapq

>>> nums = [3, 1, 4, 1, 5, 9, 2, 6]
>>> heapq.heapify(nums)   # 原地转换成堆 O(n)
>>> nums                  # [1, 1, 2, 3, 5, 9, 4, 6]——堆顺序，不是排序顺序
>>> nums[0]               # 1——堆顶是最小元素（注意：nums[1] 未必是第二小！）

# 基本操作
>>> heapq.heappush(nums, 0)    # 压入 O(log n)
>>> heapq.heappop(nums)        # 弹出最小元素 O(log n) → 0
>>> heapq.heappushpop(nums, 7) # 先 push 再 pop，比分开调用更高效
>>> heapq.heapreplace(nums, 8) # 先 pop 再 push，比分开调用更高效
```

**top-k 问题——heapq 最经典的应用：**

```python
# 从一个超大流中找出最大的 k 个——不用把全部数据加载到内存排序
import heapq

def top_k(iterable, k):
    heap = []
    for item in iterable:
        if len(heap) < k:
            heapq.heappush(heap, item)
        elif item > heap[0]:      # 比堆里最小的还大，替换
            heapq.heapreplace(heap, item)
    return sorted(heap, reverse=True)  # 最终排个序输出

# 如果数据是 [1, 2, 3, 4, 5, ..., 1000000]，找 top 10
# 用排序 → O(n log n)，需要加载全部数据
# 用堆 → O(n log k)，内存里只保留 k 个元素
```

**常用工程场景：**

| 场景 | 做法 |
|------|------|
| Top-K 问题 | 维护大小为 k 的最小堆 |
| 优先级队列 | `(priority, item)` 元组入堆——Python 比较元组从左往右 |
| 合并多个有序序列 | `heapq.merge(*sorted_lists)` |
| 定时任务调度 | 按下次执行时间入堆，每次取堆顶（最近的任务） |
| Dijkstra 最短路径 | 按距离维护未访问节点 |

**用 `(priority, item)` 做优先级队列时的陷阱：**

```python
>>> heap = []
>>> heapq.heappush(heap, (1, Task("send_email")))
>>> heapq.heappush(heap, (1, Task("send_sms")))  # priority 相同
# TypeError: '<' not supported between instances of 'Task'——Python 会去比较元组的第二个元素！

# 解决：加入一个递增的 counter 打破平局
>>> from itertools import count
>>> counter = count()
>>> heapq.heappush(heap, (1, next(counter), Task("send_email")))
>>> heapq.heappush(heap, (1, next(counter), Task("send_sms")))  # OK
```

---

### 2.5 选择决策树

每次你不确定该用什么结构时，走一遍这个决策流程：

```
需要按键查找？
 ├── 是 → dict（需要顺序）/ defaultdict（分组+计数）/ Counter（纯计数）
 └── 否 → 需要去重/集合运算？
           ├── 是 → set
           └── 否 → 需要快速头部操作？
                     ├── 是 → deque
                     └── 否 → 需要最大/最小值快速访问？
                               ├── 是 → heapq
                               └── 否 → 需要不可变性/可哈希？
                                         ├── 是 → tuple
                                         └── 否 → list
```

**常见选错场景及纠正：**

| 错误 | 后果 | 纠正 |
|------|------|------|
| 大列表用 `x in lst` | O(n) 每次，累积 O(n²) | 换成 `set` |
| 用 `list.insert(0, x)` | 每次 O(n) | 换成 `deque.appendleft()` |
| 用 `list` 手动实现队列 | `pop(0)` 是 O(n) | 换成 `deque` |
| 大量数据全排序取 Top-10 | O(n log n) 内存爆炸 | 换成 `heapq` 的 k-size heap |
| 用 `if k in d: d[k].append()` | 冗余判断 | 换成 `defaultdict(list)` |
| 用 dict 但只需要判断存在 | 浪费 value 槽位 | 换成 `set` |
| 用 `list` 存几百万个同质小数据 | 预分配空间浪费 | 换成 `tuple` 或 `array('i')` |

---

### 2.6 综合示例：把选择决策落实到代码

```python
from collections import defaultdict, Counter, deque
import heapq

# 场景：处理一条 API 访问日志流，要求：
# 1. 按 IP 分组统计访问次数
# 2. 找出被访问最多的 5 个接口
# 3. 每个 IP 只保留最近 100 条记录（滑动窗口）
# 4. 有一个始终按优先级排序的告警队列

# 1. 分组统计 → defaultdict
ip_counter = defaultdict(int)
for log in logs:
    ip_counter[log.ip] += 1

# 2. Top-5 接口 → Counter
endpoint_counter = Counter(log.endpoint for log in logs)
top_5 = endpoint_counter.most_common(5)

# 3. 滑动窗口 → deque(maxlen=100)
ip_history = defaultdict(lambda: deque(maxlen=100))
for log in logs:
    ip_history[log.ip].append(log)

# 4. 优先级告警队列 → heapq
alert_queue = []  # 元素为 (priority, counter, alert_msg)
heapq.heappush(alert_queue, (1, next(counter), "磁盘使用率 80%"))
heapq.heappush(alert_queue, (0, next(counter), "服务不可达"))  # priority 小的先处理
next_alert = heapq.heappop(alert_queue)  # (0, ..., "服务不可达")
```

每一个选择都对应着一个时间复杂度上的理由——这就是从"我会用 Python 的数据结构"到"我知道为什么在这个场景选这个结构"的分界线。

---

## 三、函数

> **目标：理解 Python 函数是 first-class object，掌握参数系统的全部细节，以及闭包和作用域在工程中的实际影响。**

---

### 3.1 参数传递机制 —— Call by Sharing

Python 的参数传递既**不是**传值（call by value），也**不是**传引用（call by reference），而是一种被广泛称为 **call by sharing**（传对象引用，也叫 call by object）的语义。要精确理解它，只需要记住两条规则：

**规则一：函数接收的是实参所指向的那个对象的一个引用（不是副本）。**

```python
>>> def append_one(lst):
...     lst.append(1)          # 通过这个引用修改了对象
...
>>> a = []
>>> append_one(a)
>>> a                          # [1]——外部可见
```

**规则二：在函数内部对形参名重新赋值，只是把这个局部名字绑定到另一个对象，对外部没有任何影响。**

```python
>>> def reassign(lst):
...     lst = [2, 3]           # 只是把局部变量名 lst 重新绑定了
...
>>> a = [1]
>>> reassign(a)
>>> a                          # [1]——外部不受影响
```

把这两条放在一起，就能避免最常见的混淆——很多人看到规则一会说"这是传引用"，看到规则二发现外部没变又困惑。关键在于区分两个操作：**通过引用修改对象** vs **重新绑定变量名**。

```python
>>> def modify_and_reassign(lst):
...     lst.append(1)          # 修改对象——外部可见
...     lst = [2, 3]           # 重绑定——外部不可见
...     lst.append(4)          # 修改新对象——外部不可见（lst 已经不是原来的 list 了）
...
>>> a = []
>>> modify_and_reassign(a)
>>> a                          # [1]——只有第一个 append 生效了
```

**对比其他语言澄清概念：**

| 语言 | 语义 | Python 的差异 |
|------|------|--------------|
| C 传值 | 把值复制一份给函数 | Python 不复制对象本身，只复制引用（指针） |
| C++ 传引用 `&` | 函数内的赋值影响外部变量 | Python 做不到——重绑定永远是局部的 |
| Java | 和 Python 完全一样——传对象引用的副本 | 无差异 |

Python 之所以被误解为"传引用"，是因为传入可变对象时，通过引用**修改对象内容**对外部可见。但真正的传引用（如 C++ 的 `&`）意味着对形参的赋值本身就是对外部变量的赋值——Python 做不到这一点。

---

### 3.2 参数系统的完整语法

Python 函数签名有五种参数类型，按定义顺序必须是：

```
def f(positional-only, /, standard, *args, keyword-only, **kwargs):
```

其中 `/` 和 `*`（或 `*args`）是分界线。下面逐类解释。

---

#### 3.2.1 `*args` —— 接收多余的**位置**参数，打包为 tuple

```python
>>> def log_all(*args):
...     print(args)  # args 是一个 tuple
...
>>> log_all(1, 2, 3)         # (1, 2, 3)
>>> log_all("a")             # ('a',)
>>> log_all()                # ()——可以传零个
```

**`args` 只是约定俗成的名字**——你完全可以用 `*items`、`*values` 等任何合法标识符。`*` 才是语法核心，不是 `args` 这个单词。

**工程中最常用的模式：作为中间层，透传所有位置参数，只加不改。**

```python
# 代理函数——自己不处理，只是把参数原样转给另一个函数
>>> def proxy(*args, **kwargs):
...     return real_function(*args, **kwargs)  # * 在这里是 unpacking，不是定义
```

注意 `*` 的两个完全相反的含义：
- **定义时** `def f(*args)`：打包（packing）——把多个参数收进一个 tuple
- **调用时** `f(*items)`：解包（unpacking）——把一个可迭代对象拆成多个参数传递

---

#### 3.2.2 `**kwargs` —— 接收多余的**关键字**参数，打包为 dict

```python
>>> def config(**kwargs):
...     print(kwargs)  # kwargs 是一个普通 dict
...
>>> config(host="localhost", port=8080)  # {'host': 'localhost', 'port': 8080}
>>> config()                              # {}——可以传零个
```

**`kwargs` 也只是约定俗成的名字**——用 `**options`、`**settings` 等也是合法的。和 `*args` 一样，`**` 才是语法本身。

**工程场景：作为中间层透传参数，或者收集未知配置项。** 和 `*args` 一样，`**kwargs` 在定义时打包、在调用时解包。

---

#### 3.2.3 Keyword-only 参数 —— 必须用关键字方式传递

出现在 `*args` 或单独的 `*` 之后的参数，调用时**只能**用 `key=value` 的方式传递，不能用位置方式。

```python
>>> def connect(host, *, timeout=30, retries=3):
...     pass
...
>>> connect("localhost", timeout=10)        # OK
>>> connect("localhost", retries=5)         # OK
>>> connect("localhost", 10, 3)             # TypeError: 最多 1 个 positionals，传了 3 个
```

**为什么需要这个语法？**

没有 keyword-only 之前，工程师想实现类似效果只能自己从 `**kwargs` 里手动取，然后在 docstring 里说明——没有编译器支持，传错了静默通过。

keyword-only 解决了两类真实问题：

(a) **布尔 flag 不写 keyword 根本读不懂：**

```python
# ❌ 这是啥意思？
>>> search("python", True, False, 100)

# ✅ keyword-only 强制调用者写出含义
>>> def search(query, *, case_sensitive=True, exact_match=False, limit=100):
...     pass
>>> search("python", case_sensitive=False, limit=50)  # 一目了然
```

(b) **API 演化安全——新增可选参数时，防止未来调用者踩坑：**

keyword-only 不解决"旧调用自动兼容新签名"的问题——旧代码该改还得改。它解决的是另一个更隐蔽的问题：**阻止调用者用位置方式传递新参数，从而保护 API 未来继续演化的自由。**

```python
# 初始设计——只有一个可选参数 retries
>>> def connect(host, retries=3):
...     pass
>>> connect("localhost")       # host="localhost", retries=3
>>> connect("localhost", 5)    # host="localhost", retries=5
```

现在要加一个 `timeout` 参数。比较两种做法：

```python
# 做法 A：加在末尾，不做 keyword-only
>>> def connect(host, retries=3, timeout=30):
...     pass
>>> connect("localhost", 5)           # 仍然 OK：host="localhost", retries=5, timeout=30
>>> connect("localhost", 5, 10)       # 也 OK：timeout=10——调用者开始用位置方式传 timeout 了
```

表面上看做法 A 向后兼容了。但问题在下一步：如果以后还要加 `ssl_verify`，那些写了 `connect("localhost", 5, 10)` 的调用者——他们用位置方式传了三个参数——就会在加第四个参数时面临同样的"谁对应谁"的脆弱性。**每允许一个参数用位置方式传递，就等于把它排进了"位置队列"里，以后想在这个队列中间插入新参数就会踩踏已有调用。**

```python
# 做法 B：新参数用 keyword-only——阻止它进入"位置队列"
>>> def connect(host, retries=3, *, timeout=30):
...     pass
>>> connect("localhost", 5)              # 仍然 OK：旧调用不受影响
>>> connect("localhost", 5, timeout=10)  # 必须显式写关键字——timeout 永远不会被位置传递
>>> connect("localhost", 5, 10)          # TypeError——位置队列里只有 2 个槽，10 没地方放
```

做法 B 的关键收益不是今天——是未来。因为调用者从来就不能用位置方式传 `timeout`，所以以后加 `ssl_verify`、改参数顺序、甚至废弃 `timeout` 时，没有任何调用者会因为"按位置传了 timeout"而静默错乱。**keyword-only 是把"这个参数不参与位置排队"写进了语法层面，而不只是写在文档里指望每个人都读。**

---

#### 3.2.4 Positional-only 参数 —— 必须用位置方式传递（Python 3.8+）

出现在 `/` 之前的参数，调用时**只能**按位置传递，不能用 `key=value` 的方式。

```python
>>> def greet(name, /, greeting="Hello"):
...     return f"{greeting}, {name}"
...
>>> greet("Alice")                   # OK
>>> greet("Alice", greeting="Hi")    # OK——greeting 在 / 之后，可以用 keyword
>>> greet(name="Alice")              # TypeError——name 在 / 之前，不能用 keyword
```

**为什么需要这个语法？**

对库作者来说，参数名是 API 的一部分——一旦用户开始用 `f(name=value)` 调用，这个参数名就被冻结了，改名就是 breaking change。把参数放在 `/` 之前意味着"I reserve the right to rename this parameter"。

**典型场景：**

```python
# 内置函数都用了 positional-only（C 实现的函数天然就是 positional-only）
>>> len(obj=[1, 2, 3])     # TypeError: len() takes no keyword arguments
>>> abs(x=-5)              # TypeError: abs() takes no keyword arguments

# 纯 Python 中用 / 声明
>>> def push(item, /, *, priority=0):
...     """item 必须位置传递，priority 必须关键字传递"""
...
>>> push("task", priority=1)  # OK
>>> push(item="task")         # TypeError
>>> push("task", 1)           # TypeError—priority 是 keyword-only
```

**`/` 和 keyword-only 的组合** 是 API 设计的强力工具：`/` 左边的参数既不能被改名也不能被传 keyword，`*` 右边的参数必须用 keyword——左右边界都加固了，只有中间可以有选择地保留兼容性。

---

#### 3.2.5 五种参数类型的完整排序规则

定义顺序必须是：`positional-only` → `standard` → `*args` → `keyword-only` → `**kwargs`

```python
>>> def full_signature(a, b, /, c, d, *args, e="e_default", f="f_default", **kwargs):
...     print(f"{a=}, {b=}, {c=}, {d=}, {args=}, {e=}, {f=}, {kwargs=}")
...
>>> full_signature(1, 2, 3, 4, 5, 6, 7, e=8, g=9, h=10)
# a=1, b=2, c=3, d=4, args=(5, 6, 7), e=8, f='f_default', kwargs={'g': 9, 'h': 10}
```

**调用时同一条规则是镜像的：** `f(positional, keyword, *iterable, **mapping)`

---

### 3.3 Lambda —— 匿名函数

**语法：** `lambda 参数: 表达式`——表达式的结果就是返回值，不能包含 `return`、`=`、`if` 语句、`for` 循环等。

```python
>>> add = lambda a, b: a + b
>>> add(2, 3)  # 5
```

**lambda 的主体只能是单个表达式（expression），不能是语句（statement）。** 这是 Python 语言层面的硬限制，不是"不推荐"的问题——`lambda x: (x = x + 1)` 就是语法错误。

**但表达式可以很复杂：利用 `if-else` 三元表达式、`or` 短路求值、tuple 等在表达式中完成多逻辑：**

```python
# 三元表达式
>>> categorize = lambda n: "large" if n > 100 else ("medium" if n > 10 else "small")

# 短路求值做条件执行
>>> safe_reciprocal = lambda x: x != 0 and 1 / x or float("inf")
```

**lambda 的真正用途不是替代 `def`，而是在需要"传一个简单函数进去"的场景里避免定义命名函数：**

```python
# sorted 的 key——lambda 最典型的用途
>>> users = [{"name": "Bob", "age": 25}, {"name": "Alice", "age": 30}]
>>> sorted(users, key=lambda u: u["age"])  # 按年龄排序

# 不需要这样写：
# >>> def get_age(u):
# ...     return u["age"]
# >>> sorted(users, key=get_age)
```

**当 lambda 超过一行逻辑时，就应该用 `def` 定义具名函数——这是工程纪律，不是语法限制。** 具名函数可读性更好，出错时的 traceback 也会显示函数名而不是 `<lambda>`。

---

### 3.4 闭包（Closure）

**定义：** 闭包是一个函数，它捕获了其外部作用域中的变量，并在外部函数返回后仍然持有对这些变量的引用。

```python
>>> def make_multiplier(factor):
...     def multiply(x):
...         return x * factor    # factor 是从外层作用域捕获的
...     return multiply
...
>>> double = make_multiplier(2)
>>> triple = make_multiplier(3)
>>> double(10)    # 20——factor=2 还活着
>>> triple(10)    # 30——factor=3 也还活着，彼此独立
```

**发生了什么：** `make_multiplier` 返回后，按说 `factor` 这个局部变量的生命周期就该结束了。但 `multiply` 内部引用了 `factor`，Python 检测到这一点，在创建 `multiply` 函数对象时把 `factor` 的值打包存进了 `multiply.__closure__`，所以 `factor` 得以"存活"，并且在每次调用 `make_multiplier` 时创建的闭包之间是相互独立的。

```python
>>> double.__closure__[0].cell_contents   # 2
>>> triple.__closure__[0].cell_contents   # 3
```

---

#### 3.4.1 闭包的经典陷阱——循环中的延迟绑定

这是 Python 面试和真实代码中最常见的闭包陷阱：

```python
>>> funcs = []
>>> for i in range(3):
...     funcs.append(lambda: i)   # 捕获的是变量名 i，不是当时的"值"
...
>>> funcs[0]()   # 2——不是 0！
>>> funcs[1]()   # 2——不是 1！
>>> funcs[2]()   # 2
```

**根因：** `lambda` 捕获的是变量名 `i`，不是 `i` 在循环那一刻的值。当循环结束后 `i = 2`，三个闭包都查找 `i`，都找到了同一个 `2`。这不是 bug——这是 LEGB 查找规则的直接后果（闭包查找 enclosing 作用域时是**按名查找，不是按创建时的快照**）。

**三种解法：**

```python
# 解法一（推荐）：用默认参数的"定义时求值"特性
>>> funcs = []
>>> for i in range(3):
...     funcs.append(lambda i=i: i)   # i=i 在定义时求值，之后不再变
>>> funcs[0]()   # 0 ✅

# 解法二：再包一层函数，用外层函数的参数形成独立作用域
>>> funcs = []
>>> for i in range(3):
...     def make_func(n):
...         return lambda: n          # n 是每次调用独立创建的局部变量
...     funcs.append(make_func(i))
>>> funcs[0]()   # 0 ✅

# 解法三（Python 3.9+ 最干净）：functools.partial
>>> from functools import partial
>>> funcs = []
>>> for i in range(3):
...     funcs.append(partial(print, i))
```

---

### 3.5 LEGB —— 变量查找规则

Python 解析一个变量名时，按 **L → E → G → B** 的顺序依次查找。

| 层级 | 英文 | 范围 | 例子 |
|------|------|------|------|
| **L** | Local | 当前函数内部 | 函数里的局部变量 |
| **E** | Enclosing | 嵌套的外层函数的作用域 | 闭包捕获的变量 |
| **G** | Global | 模块级别 | 模块顶部定义的变量和函数 |
| **B** | Built-in | Python 内置命名空间 | `print`、`len`、`range`、`Exception` |

```python
x = "global"                # G: 模块级

def outer():
    x = "enclosing"         # E: 嵌套作用域（对 inner 而言）

    def inner():
        x = "local"         # L: 局部作用域
        print(x)

    inner()

outer()  # 输出 "local"——L 优先于 E
```

**同一个变量名在不同层可以同时存在，查找在找到第一处就停止：**

```python
>>> print = "I shadowed the built-in"  # 在 G 层覆盖了 B 层的 print
>>> print("hello")                      # TypeError: 'str' object is not callable
```

**两个关键字：**

- **`global`**：告诉 Python "在这个函数里，这个名字映射到 G 层（模块级），不要创建新的局部变量"。
- **`nonlocal`**：告诉 Python "在这个函数里，这个名字映射到 E 层（最近的封闭作用域），不要创建新的局部变量"。

```python
>>> counter = 0

>>> def increment():
...     global counter       # 没有这行，counter += 1 会创建一个局部变量 counter
...     counter += 1         # 现在在修改模块级的 counter

>>> def make_counter():
...     count = 0
...     def increment():
...         nonlocal count   # 没有这行，count += 1 会在 increment 里创建局部 count
...         count += 1       # 现在在修改 enclosing 作用域的 count
...         return count
...     return increment
```

**工程上值得注意的一点：** LEGB 是运行时的**动态**查找——每次访问变量名都会按 L→E→G→B 找一次，不是创建函数时的"快照"。这也正是上一节循环中闭包陷阱的根本原因。

---

### 3.6 高阶函数（Higher-order Functions）

**定义：** 接收一个函数作为参数，或者返回一个函数的函数。

这不是什么特殊的语法——只是函数在 Python 中是 first-class object 的自然推论（还记得 1.1 节里 `greet.__dict__` 吗）。

#### 3.6.1 接收函数作为参数

```python
# sorted 的 key 参数是典型的高阶函数
>>> words = ["banana", "apple", "Cherry"]
>>> sorted(words, key=str.lower)    # ['apple', 'banana', 'Cherry']

# map / filter（用 generator expression 或 list comprehension 更 Pythonic）
>>> list(map(str.upper, ["a", "b"]))       # ['A', 'B']——但 [s.upper() for s in ["a", "b"]] 更好
>>> list(filter(str.isdigit, ["a1", "23", "b4"]))  # ['23']
```

#### 3.6.2 返回函数 —— 装饰器的前身

```python
>>> def make_greeting(prefix):
...     def greet(name):
...         return f"{prefix}, {name}!"
...     return greet
...
>>> hello = make_greeting("Hello")
>>> hi = make_greeting("Hi")
>>> hello("World")    # 'Hello, World!'
>>> hi("World")       # 'Hi, World!'
```

这就是闭包的组合使用——返回的函数捕获了 `prefix`，构成了一个"配置好行为的函数"。装饰器（Decorator）的底层原理就是这个：`@deco` 等价于 `func = deco(func)`——装饰器就是一个接收函数、返回函数的高阶函数。

#### 3.6.3 `functools.partial` —— 函数的部分应用

```python
>>> from functools import partial
>>> def connect(host, port, timeout=30):
...     return f"connecting to {host}:{port}"

>>> connect_localhost = partial(connect, host="localhost", port=5432)
>>> connect_localhost()           # 'connecting to localhost:5432'
>>> connect_localhost(timeout=60) # 'connecting to localhost:5432'
```

**和闭包的区别：** `partial` 是显式地"冻结"某些参数——更清晰、不会引入额外的作用域嵌套、对 `inspect.signature` 友好。对于简单的参数预填充，`partial` 通常比手写闭包更合适。

---

### 3.7 总结

| 知识点 | 一句话要点 |
|--------|----------|
| 参数传递 | call by sharing：传的是对象引用的副本，重绑定是局部的，变异（mutate）是可见的 |
| `*args` | 定义时打包多余位置参数为 tuple，调用时解包可迭代对象 |
| `**kwargs` | 定义时打包多余关键字参数为 dict，调用时解包字典 |
| keyword-only | `*` 之后的参数只能用关键字传——强制可读性 + API 演化安全 |
| positional-only | `/` 之前的参数只能用位置传——保护参数名不被冻结 |
| lambda | 单表达式匿名函数，长逻辑用 `def` |
| 闭包 | 内部函数捕获外层变量，按名称查找，非快照 |
| LEGB | 变量查找顺序 L→E→G→B，动态查找（循环中闭包陷阱的根因） |
| 高阶函数 | 函数是第一公民的自然推论——装饰器、`partial`、回调的基础 |

---

## 四、Pythonic

> **目标：写出地道的 Python 代码——不只是能跑，而是让其他 Python 工程师一眼就能读懂、维护成本最低的写法。**

---

### 4.1 Comprehension —— 声明式构造集合

Comprehension（推导式）是 Python 最核心的语法糖之一：用**一个表达式**声明性地构造一个新的集合对象，而不需要写"创建空容器 → for 循环 → append/add"这种命令式代码。

#### 4.1.1 List Comprehension

```python
# ❌ 命令式——4 行，心里要执行一遍循环才能知道结果是什么
>>> squares = []
>>> for x in range(10):
...     if x % 2 == 0:
...         squares.append(x ** 2)
>>> squares  # [0, 4, 16, 36, 64]

# ✅ 声明式——1 行，直接告诉你"你想要什么"
>>> squares = [x ** 2 for x in range(10) if x % 2 == 0]
>>> squares  # [0, 4, 16, 36, 64]
```

**语法：** `[表达式 for 变量 in 可迭代对象 if 条件]`

- `if` 子句是可选的
- 表达式先于 for，这个顺序刻意模仿了数学中的集合构造记法 `{x² | x ∈ ℕ, x < 10, x is even}`
- List comprehension 会**立即**构造整个列表并返回——所有元素都在内存里

**嵌套循环：**

```python
>>> [(x, y) for x in range(2) for y in range(3)]
# [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2)]
# 等价于：
# for x in range(2):
#     for y in range(3):
#         result.append((x, y))
```

注意嵌套的 for 顺序和命令式写法的顺序**一致**——外层 for 在前面，内层 for 在后面。这和很多初学者直觉相反。

**工程纪律：超过两层嵌套或条件逻辑超过一个 `if` 时，就应该拆成普通循环或提取函数。** Comprehension 的目的是提高可读性，不是为了在一行里塞进尽可能多的逻辑。

---

#### 4.1.2 Dict Comprehension

```python
>>> {x: x ** 2 for x in range(5)}
# {0: 0, 1: 1, 2: 4, 3: 9, 4: 16}

# 反转 key/value
>>> d = {"a": 1, "b": 2, "c": 3}
>>> {v: k for k, v in d.items()}
# {1: 'a', 2: 'b', 3: 'c'}
```

**带条件的 dict comprehension：**

```python
>>> {k: v for k, v in d.items() if v > 1}
# {'b': 2, 'c': 3}
```

---

#### 4.1.3 Set Comprehension

语法和 list comprehension 一样，只是用 `{}` 代替 `[]`——会自动去重。

```python
>>> {x % 3 for x in range(20)}
# {0, 1, 2}

# 去重某个字段
>>> users = [{"name": "Alice"}, {"name": "Bob"}, {"name": "Alice"}]
>>> {u["name"] for u in users}
# {'Alice', 'Bob'}
```

**注意：** `{}` 是空 dict，不是空 set。空 set 必须用 `set()` 创建。

---

#### 4.1.4 Generator Expression —— 惰性求值

把 list comprehension 的 `[]` 换成 `()`，你就得到了一个生成器表达式。

```python
>>> gen = (x ** 2 for x in range(10 ** 9))
>>> gen
# <generator object <genexpr> at 0x...>——没有计算任何值，不占内存
>>> next(gen)  # 0——现在才计算第一个
>>> next(gen)  # 1——第二个
```

**和 list comprehension 的关键区别：**

| | List Comprehension | Generator Expression |
|---|---|---|
| 语法 | `[x for x in ...]` | `(x for x in ...)` |
| 求值时机 | 立即——返回完整 list | 惰性——每次 `next()` 才产出一个值 |
| 内存占用 | O(n) | O(1) |
| 可复用 | 可以多次遍历 | **只能遍历一次** |
| 适用场景 | 数据量可控，需要多次使用结果 | 数据量不可控/很大，只需要遍历一次 |

**只遍历一次——这是 generator expression 最大的陷阱：**

```python
>>> gen = (x ** 2 for x in range(5))
>>> list(gen)      # [0, 1, 4, 9, 16]
>>> list(gen)      # []——已经耗尽了！
```

**语法糖：当 generator expression 是函数调用的唯一参数时，可以省略外层的括号：**

```python
>>> sum(x ** 2 for x in range(1000000))  # 没有额外的 () ——不是 sum((x**2 for x in ...))
# 这对 sum/max/min/all/any 都很实用——不需要在内存里构造整个中间 list
```

---

### 4.2 Iterable、Iterator 与迭代协议

这是整个 Python for 循环系统的底层机制——理解它之后，生成器、`yield`、`async for` 等都有了一条统一的心智模型。

#### 4.2.1 概念定义

| 术语 | 定义 | 协议 |
|------|------|------|
| **Iterable（可迭代对象）** | 任何可以被 `for` 遍历的东西 | 实现 `__iter__()`，返回一个 iterator |
| **Iterator（迭代器）** | 维护"遍历到哪了"的状态机 | 实现 `__next__()` 返回下一个元素，耗尽时抛出 `StopIteration`；同时实现 `__iter__()` 返回自身 |
| **Generator（生成器）** | 一种特殊的 iterator——由包含 `yield` 的函数或 generator expression 创建 | 自动满足 iterator 协议 |

**关键——每一个 iterator 都是 iterable（它的 `__iter__()` 返回自身），但反过来不成立：** list 是 iterable 但不是 iterator——它有 `__iter__()` 但没有 `__next__()`。

#### 4.2.2 for 循环到底干了什么

```python
# 你写的：
for x in obj:
    print(x)

# Python 实际执行的等价代码：
iterator = iter(obj)      # 调用 obj.__iter__() 获取迭代器
while True:
    try:
        x = next(iterator)  # 调用 iterator.__next__() 逐个取值
        print(x)
    except StopIteration:
        break                # 迭代完成，退出
```

这就是为什么任何实现了 `__iter__` + `__next__` 的对象都能被 `for` in——Python 不关心你是什么类型，只关心你是否遵循了这套协议。这就是**鸭子类型（Duck Typing）**在迭代系统里的体现——也是 Pythonic 思维的核心。

#### 4.2.3 自己实现一个 Iterator

```python
class Countdown:
    """从 n 倒数到 1 的迭代器"""
    def __init__(self, n):
        self.n = n

    def __iter__(self):
        return self          # iterator 的 __iter__ 返回自身

    def __next__(self):
        if self.n <= 0:
            raise StopIteration
        self.n -= 1
        return self.n + 1    # 返回递减前的值

>>> for num in Countdown(3):
...     print(num)
# 3
# 2
# 1
```

**注意 `__iter__` 返回 `self` 的后果：** 这意味着 iterator 自身就是它的迭代器，每次遍历都会消耗它——它是一次性的：

```python
>>> cd = Countdown(3)
>>> list(cd)   # [3, 2, 1]
>>> list(cd)   # []——同一个 iterator 已经被耗尽了
```

这也是 generator 只能遍历一次的原因——generator 是一种 iterator，`__iter__` 返回自身。

**对比——Iterable 但不是 Iterator（可重复遍历）：**

```python
class CountdownIterable:
    """可重复遍历的倒数对象"""
    def __init__(self, n):
        self.n = n

    def __iter__(self):
        return Countdown(self.n)   # 每次调用 iter() 都返回一个新的 iterator

>>> cd = CountdownIterable(3)
>>> list(cd)   # [3, 2, 1]
>>> list(cd)   # [3, 2, 1]——每次 iter() 产生全新的 iterator
```

这就是 list、tuple、dict 等容器的工作原理——它们的 `__iter__()` 每次都返回一个**新的** iterator 从头开始遍历，而不是返回自身。

---

### 4.3 实用内置工具

#### 4.3.1 `enumerate` —— 同时获取索引和值

```python
# ❌ 反模式
>>> i = 0
>>> for item in items:
...     print(i, item)
...     i += 1

# ✅ Pythonic
>>> for i, item in enumerate(items):
...     print(i, item)

# enumerate 第二个参数：起始索引
>>> for i, line in enumerate(lines, start=1):
...     print(f"第 {i} 行: {line}")
```

`enumerate` 返回的是一个惰性的 enumerate 对象（也是一个 iterator），不是 list——它不会在内存中额外创建任何集合。

---

#### 4.3.2 `zip` —— 并行遍历多个可迭代对象

```python
>>> names = ["Alice", "Bob", "Charlie"]
>>> scores = [95, 87, 91]
>>> for name, score in zip(names, scores):
...     print(f"{name}: {score}")
# Alice: 95
# Bob: 87
# Charlie: 91
```

**zip 的行为细节——以最短的输入为准（严格模式在 3.10+ 才有）：**

```python
>>> list(zip("abc", [1, 2, 3, 4, 5]))  # [('a', 1), ('b', 2), ('c', 3)]——4, 5 被静默丢弃！
```

**Python 3.10+ 用 `strict=True` 时，长度不一致会抛出 `ValueError`：**

```python
>>> list(zip("abc", [1, 2, 3, 4, 5], strict=True))
# ValueError: zip() argument 2 is longer than argument 1
```

**解压缩——用 `zip(*zipped)` 还原：**

```python
>>> zipped = [('a', 1), ('b', 2), ('c', 3)]
>>> letters, numbers = zip(*zipped)
>>> letters   # ('a', 'b', 'c')
>>> numbers   # (1, 2, 3)
```

---

#### 4.3.3 `any` / `all` —— 布尔聚合

```python
>>> any([False, False, True])   # True——至少有一个为真
>>> all([True, True, False])    # False——不是全为真
```

**两者都支持短路求值**（尽管示例用了 list，但和 generator expression 配合时短路才有价值）：

```python
# all 遇到第一个 False 就停止，any 遇到第一个 True 就停止
>>> any(x > 100 for x in range(10 ** 9))   # False——但不需要迭代全部 10⁹ 个元素
>>> all(x.is_valid() for x in huge_list)   # 遇到第一个无效就停
```

**注意 `any([])` 返回 `False`，`all([])` 返回 `True`**——这是数学上"空和的析取为假、空和的合取为真"的逻辑，和其他语言一致。

---

#### 4.3.4 `sorted` + `key` —— 排序的瑞士军刀

```python
# key 参数：对每个元素调用 key 函数，用返回值进行排序
>>> words = ["banana", "apple", "Cherry"]
>>> sorted(words, key=str.lower)    # ['apple', 'banana', 'Cherry']——大小写不敏感

# 按对象的某个属性排序
>>> users = [{"name": "Bob", "age": 25}, {"name": "Alice", "age": 30}]
>>> sorted(users, key=lambda u: u["age"])  # 按年龄升序

# 多级排序——返回 tuple：按第一个字段排，相同时按第二个
>>> data = [("Alice", 30), ("Bob", 25), ("Alice", 25)]
>>> sorted(data, key=lambda x: (x[0], x[1]))  # 先按名字，再按年龄

# 降序——reverse=True
>>> sorted(data, key=lambda x: x[1], reverse=True)
```

**`key` 函数对每个元素只调用一次**（排序过程中缓存），和很多其他语言的 comparator（每比较一次就调用）不同——Python 使用 **key function** 模式也叫 Schwartzian transform，O(n) 次 key 调用而非 O(n log n) 次 comparator 调用。这是刻意设计的。

---

#### 4.3.5 Unpacking —— 解包

Python 3 极大增强了 unpacking 的能力：

```python
# 基本 unpacking
>>> a, b = [1, 2]             # a=1, b=2

# 用 * 捕获剩余元素
>>> first, *middle, last = [1, 2, 3, 4, 5]
>>> first   # 1
>>> middle  # [2, 3, 4]——总是 list，即使只有一个元素
>>> last    # 5

>>> a, *rest = [1]    # rest = []——可以捕获 0 个

# 深层 unpacking
>>> (a, (b, c)) = (1, (2, 3))   # a=1, b=2, c=3

# 函数参数 unpacking——前面 3.2 节详细讲过
>>> nums = [1, 2, 3]
>>> print(*nums)                   # 1 2 3
>>> kwargs = {"sep": "|"}
>>> print(*nums, **kwargs)         # 1|2|3

# 合并字典（Python 3.5+：** unpacking；3.9+：| 运算符）
>>> d1, d2 = {"a": 1}, {"b": 2}
>>> {**d1, **d2}       # {'a': 1, 'b': 2}
>>> d1 | d2            # {'a': 1, 'b': 2}——Python 3.9+ 更简洁
```

---

### 4.4 泛型化 Schema 设计（进阶）

> 这一节适用于后端开发中构建通用 API 响应结构的场景——如果你还没接触 FastAPI/Pydantic，可以先理解思路，具体细节在 Layer 2（Backend Engineering）中会再次遇到。

#### 4.4.1 问题：没有泛型时的重复代码

```python
# 每个资源都要写一遍几乎一样的响应壳子
class UserResponseSchema(BaseModel):
    code: int = 0
    message: str = "ok"
    data: UserSchema              # 唯一不同的就是这里

class OrderResponseSchema(BaseModel):
    code: int = 0
    message: str = "ok"
    data: OrderSchema             # 又是重复

class ProductResponseSchema(BaseModel):
    code: int = 0
    message: str = "ok"
    data: ProductSchema           # 再重复……
```

项目里有 20 个资源就要写 20 个几乎一样的类——这就是"能跑"和"工程化"之间的典型鸿沟。

#### 4.4.2 解决方案：`Generic[T]`

```python
from typing import Generic, TypeVar
from pydantic import BaseModel

T = TypeVar("T")

class ResponseSchema(BaseModel, Generic[T]):
    code: int = 0
    message: str = "ok"
    data: T                        # T 是类型变量——可以是任何类型

# 使用时用 [] 填入具体类型
# ResponseSchema[list[UserSchema]]   → data 的类型是 list[UserSchema]
# ResponseSchema[list[OrderSchema]]  → data 的类型是 list[OrderSchema]
# ResponseSchema[UserSchema]         → data 的类型是 UserSchema
```

**发生了什么：** `TypeVar("T")` 创建了一个类型变量——一个占位符。`Generic[T]` 告诉 Python："这个类的某个字段具体是什么类型，在使用时再确定"。然后在 `ResponseSchema[UserSchema]` 中 `T` 被替换为 `UserSchema`，`data: T` 就等价于 `data: UserSchema`。

**泛型的分页 Schema——更进一步：**

```python
class PaginatedResponse(BaseModel, Generic[T]):
    code: int = 0
    message: str = "ok"
    data: list[T]                  # 数据列表
    total: int                     # 总数
    page: int                      # 当前页
    page_size: int                 # 每页条数
    total_pages: int               # 总页数

# 所有资源的分页接口复用同一套结构：
# GET /api/users     → PaginatedResponse[UserSchema]
# GET /api/orders    → PaginatedResponse[OrderSchema]
# GET /api/products  → PaginatedResponse[ProductSchema]
```

**工程收益：** 泛型化 Schema 把"响应壳子"从 N 个重复类减少为 1 个通用类。以后要加字段（比如加 `trace_id`），只改一个地方，所有接口自动受益。

---

### 4.5 ORM 映射中的 `exclude_unset` 和 `exclude_none`（进阶）

> 这一节也同样属于后端工程范畴——在 Layer 2 中实现 PATCH 接口时会直接用到。

#### 4.5.1 背景

当一个 Pydantic 模型从 ORM 对象（如 SQLAlchemy model）转换时：

```python
# ORM → Pydantic（正向）：安全，链路成熟
user_schema = UserSchema.model_validate(db_user, from_attributes=True)
```

陷阱在于**反向操作**——用 Pydantic 模型去局部更新（PATCH）一个已存在的数据库行：

```python
# 前端发来 PATCH /users/1，JSON body 为 {"nickname": "new_name"}——只想改昵称
# 后端：
patch_data = UserPatchSchema.model_validate(request.json())
db_user.update(**patch_data.model_dump())   # ⚠ 危险！下面详细解释
```

#### 4.5.2 `model_dump()` 的行为——问题根源

`UserPatchSchema` 的定义：

```python
class UserPatchSchema(BaseModel):
    nickname: str | None = None    # 默认值是 None
    bio: str | None = None         # 默认值是 None
    age: int | None = None
```

如果客户端只传了 `{"nickname": "new_name"}`，那么 `bio` 和 `age` 字段没有被设值——但 Pydantic 会用**默认值** `None` 填充它们：

```python
>>> patch_data = UserPatchSchema(nickname="new_name")
>>> patch_data.model_dump()
# {'nickname': 'new_name', 'bio': None, 'age': None}——bio 和 age 被填成了 None！
```

此时如果把这个 dict 原样 `update()` 到数据库，**用户没传的字段全被覆盖为 None 了**！用户只想改昵称，结果 bio 和 age 被清空了。这就是 PATCH 接口最常见的线上事故之一。

#### 4.5.3 两种排除模式——解决不同的问题

**(a) `exclude_unset=True` —— PATCH 的正确选择：**

```python
>>> patch_data.model_dump(exclude_unset=True)
# {'nickname': 'new_name'}——只包含客户端明确传了的字段！
```

语义：**"只有被显式赋值过的字段才包含在输出里"**——其他字段保持 Pydantic 层未设置的状态，不参与序列化。

**(b) `exclude_none=True` —— 序列化输出**

```python
>>> user.model_dump(exclude_none=True)
# {'nickname': 'new_name', 'age': 25}——bio 为 None，被排除了
```

语义：**"值为 None 的字段不包含在输出里"**。适用场景是不想把空字段吐给前端。

#### 4.5.4 两者对比——别用混

| 维度 | `exclude_unset` | `exclude_none` |
|------|-----------------|----------------|
| 判断依据 | 字段是否被**显式赋值过** | 字段的**当前值**是不是 None |
| 适用场景 | PATCH 请求的局部更新 | 序列化输出时省略空字段 |
| 典型错误 | PATCH 不用它 → 数据库被 None 覆盖清空 | 用 `exclude_none` 代替 `exclude_unset` 做 PATCH——如果客户端特意把某个字段设为 `None` 表示"删除"，就会被错误地忽略 |

```python
# exclude_none 不能替代 exclude_unset 的典型案例：
# 前端 PATCH body: {"bio": null}——用户想清空 bio
>>> patch_data = UserPatchSchema(bio=None)
>>> patch_data.model_dump(exclude_none=True)
# {}——bio 被排除了！用户的"清空 bio"操作丢失了

>>> patch_data.model_dump(exclude_unset=True)
# {'bio': None}——正确保留了用户的意图
```

**一句话总结：** `exclude_unset` 关心的是"字段传没传"（语义层面），`exclude_none` 关心的是"值是不是 None"（数据层面）。PATCH 用 `exclude_unset`，序列化用 `exclude_none`。在 PATCH 场景用错是生产级 bug 的高发源头。

---

### 4.6 总结

| 知识点 | 一句话要点 |
|--------|----------|
| List/Dict/Set Comprehension | 声明式构造集合——`[expr for x in iterable if cond]` |
| Generator Expression | 惰性求值 `()`，O(1) 内存，只能遍历一次 |
| Iterable vs Iterator | Iterable 有 `__iter__`，Iterator 有 `__next__`；Iterator 是 Iterable 但反过来不是 |
| `for` 循环本质 | `iter()` → 反复 `next()` → `StopIteration` 退出 |
| enumerate | 同时拿索引和值，惰性 |
| zip | 并行遍历，默认以最短为准，3.10+ 支持 `strict=True` |
| any / all | 短路布尔聚合，配合 generator expression 省内存 |
| sorted + key | Schwartzian transform：O(n) 次 key 调用，非 comparator |
| unpacking | `*` 捕获剩余为 list，`**` 合并字典 |
| Generic Schema | 用 `TypeVar` + `Generic[T]` 消灭重复的响应壳子 |
| `exclude_unset` | PATCH 安全——只导出客户端传了的字段 |
| `exclude_none` | 序列化输出——排除值为 None 的字段 |

---

## 五、魔术方法（Magic Methods）

> **目标：理解 Python 对象模型的核心机制——魔术方法不是要背的 API，而是让自己的类融入 Python 语法的"协议接口"。**

---

### 5.0 什么是魔术方法

魔术方法（也叫 dunder methods，来自 double underscore）是 Python 对象模型的核心：它们是 Python 解释器在特定语法下自动调用的**协议方法**。你写的 `len(obj)`，Python 实际执行的是 `obj.__len__()`；你写的 `obj[0]`，Python 实际执行的是 `obj.__getitem__(0)`。

这背后的设计哲学是：**Python 的语法不属于任何一个具体类型，而是属于实现了对应协议的任意类型。** 只要你的类实现了 `__len__`，它就能被 `len()` 调用——Python 不关心你是不是 `list` 的子类。这就是鸭子类型在解释器层面的体现。

**关键区分——魔术方法不是在类上直接调用的，是解释器通过 type 查找的：**

```python
>>> class A:
...     def __len__(self):
...         return 42
...
>>> a = A()
>>> len(a)         # ✅ 42——解释器调用了 type(a).__len__(a)
>>> a.__len__()    # ✅ 42——手动调用也行，但没人这么写
>>> A.__len__(a)   # ✅ 42——这才是解释器实际的调用路径
```

这意味着魔术方法必须定义在**类**上——如果你通过 `a.__len__ = lambda: 42` 给实例挂一个，`len(a)` 不会用它。解释器走的是 `type(a)` 这条路径，绕过了实例字典。

---

### 5.1 字符串表示——`__str__` 与 `__repr__`

这是两个最常用也最容易被混淆的魔术方法。

| | `__str__` | `__repr__` |
|---|---|---|
| 调用者 | `str(obj)`、`print(obj)`、f-string `f"{obj}"` | `repr(obj)`、交互式解释器的 `>>> obj`、list/dict 等容器的内部显示 |
| 目标受众 | **人**——终端用户 | **开发者**——调试、日志、排查 |
| 语义要求 | 可读——好看就行 | 无歧义——最好能 "eval 回来" |
| 未定义时的 fallback | 调用 `__repr__` | 显示默认的 `<ClassName at 0x...>` |

```python
>>> from datetime import datetime
>>> dt = datetime(2026, 7, 9, 14, 30, 0)

>>> str(dt)         # '2026-07-09 14:30:00'——给人看的
>>> repr(dt)        # 'datetime.datetime(2026, 7, 9, 14, 30)'——给开发者看的，可以 eval
```

**如果只能实现一个，就实现 `__repr__`**——因为 `__str__` 未定义时会 fallback 到 `__repr__`，反之不会。

```python
>>> class Point:
...     def __init__(self, x, y):
...         self.x = x
...         self.y = y
...     def __repr__(self):
...         return f"Point({self.x}, {self.y})"

>>> p = Point(1, 2)
>>> p               # Point(1, 2)——在交互式解释器里直接能看到值
>>> print(p)        # Point(1, 2)——__str__ 没定义，fallback 到 __repr__
>>> [p]             # [Point(1, 2)]——容器内部用的是 repr
```

**工程上的 `__repr__` 金规则：** `eval(repr(obj))` 最好能等价于 `obj`。即使做不到完全精确，至少要让开发者一眼就能看出对象的类型和关键状态——排查线上问题时，日志里一行 `Point(1, 2)` 比 `<__main__.Point object at 0x7f8b...>` 强一万倍。

---

### 5.2 容器协议——`__len__`、`__getitem__`、`__setitem__`、`__contains__`

#### 5.2.1 `__len__` —— 被 `len()` 调用

```python
>>> class Deck:
...     def __init__(self):
...         self.cards = list(range(52))
...     def __len__(self):
...         return len(self.cards)

>>> len(Deck())   # 52
```

**合约：** `__len__` 必须返回一个 `>= 0` 的整数。如果返回了非整数或负数，Python 的行为取决于具体使用场景——例如 `bool(obj)` 会调用 `__bool__`（fallback 到 `__len__`），此时负数被视为 truthy。

---

#### 5.2.2 `__getitem__` —— 被 `obj[key]` 调用

```python
>>> class Deck:
...     def __init__(self):
...         self.cards = list(range(52))
...     def __getitem__(self, index):
...         return self.cards[index]

>>> deck = Deck()
>>> deck[0]          # 0——索引访问
>>> deck[10:15]      # [10, 11, 12, 13, 14]——切片！Python 自动把切片语法转成了 slice 对象
>>> for card in deck:
...     pass          # 可以 for 循环了！即使没有 __iter__，Python 会用 __getitem__ fallback
```

**三个重要细节：**

(a) **实现了 `__getitem__` 就是 Iterable（即使没有 `__iter__`）**——Python 的迭代回退机制：先找 `__iter__`，找不到就找 `__getitem__`，从 `0` 开始每次 `+1` 调用，直到 `IndexError` 结束。

(b) **切片语法 `obj[a:b:c]` 会传入一个 `slice` 对象：**

```python
>>> class Deck:
...     def __getitem__(self, index):
...         if isinstance(index, slice):
...             return self.cards[index.start:index.stop:index.step]
...         return self.cards[index]
```

(c) **`__getitem__` 接收的 key 可以是任何可哈希类型**——`obj["name"]` 传 `str`，`obj[(1, 2)]` 传 `tuple`，`obj[1:10, 2:5]` 传 `tuple(slice, slice)`（NumPy 多维切片就是这样工作的）。

---

#### 5.2.3 `__setitem__` —— 被 `obj[key] = value` 调用

```python
>>> class MutableDeck:
...     def __init__(self):
...         self.cards = list(range(52))
...     def __getitem__(self, index):
...         return self.cards[index]
...     def __setitem__(self, index, value):
...         self.cards[index] = value

>>> deck = MutableDeck()
>>> deck[0] = 99        # __setitem__ 被调用
>>> deck[0]             # 99
```

---

#### 5.2.4 `__contains__` —— 被 `x in obj` 调用

```python
>>> class Deck:
...     def __init__(self):
...         self.cards = set(range(52))  # 用 set 加速 O(1) 查找
...     def __contains__(self, card):
...         return card in self.cards

>>> 10 in Deck()    # True
```

**如果没有 `__contains__`，Python 会自动 fallback**：用 `__iter__`（或 `__getitem__`）逐个遍历，线性查找直到找到或耗尽。对于大容器，实现 `__contains__` 并把复杂度降到 O(1) 是一行代码换来的显著性能提升。

---

### 5.3 迭代协议——`__iter__` 与 `__next__`

这两个方法在 4.2 节已经详细展开过了，这里只做精简回顾和补充。

```python
class Countdown:
    def __init__(self, n):
        self.n = n

    def __iter__(self):
        return self               # iterator 返回自身

    def __next__(self):
        if self.n <= 0:
            raise StopIteration   # 终止信号
        self.n -= 1
        return self.n + 1
```

**关键区分——Iterable 还是 Iterator？**

| 模式 | `__iter__` 返回 | 能否重复遍历 | 例子 |
|------|----------------|-------------|------|
| **Iterator** | `self` | 否——一次性 | generator、文件对象 |
| **Iterable** | 新的 iterator 对象 | 是——每次 `iter()` 获得新起点 | list、dict、tuple |

**如果一个类既实现了 `__iter__` 又实现了 `__getitem__`，`__iter__` 优先。**

---

### 5.4 `__call__` —— 让实例变成"函数"

**定义：** `obj()` 调用触发 `obj.__call__()`。实现 `__call__` 的对象叫做 callable——它们可以像函数一样被调用，但背后可以有内部状态。

```python
>>> class Counter:
...     def __init__(self):
...         self.count = 0
...     def __call__(self):
...         self.count += 1
...         return self.count

>>> counter = Counter()
>>> counter()    # 1
>>> counter()    # 2
>>> counter()    # 3——每次调用维护了自己的状态
```

**为什么需要这个？因为有状态的"行为"用 callable 对象比闭包更可读：**

```python
# 闭包方案——状态藏在 __closure__ 里，调试时看不到
>>> def make_counter():
...     count = 0
...     def counter():
...         nonlocal count
...         count += 1
...         return count
...     return counter

# callable 对象方案——状态是 self.count，一目了然
>>> class Counter:
...     def __init__(self, start=0):
...         self.count = start
...     def __call__(self):
...         self.count += 1
...         return self.count
```

callable 对象的另一个优势是**可以额外配置**——通过 `__init__` 传入参数：

```python
>>> class ThresholdChecker:
...     def __init__(self, threshold):
...         self.threshold = threshold
...     def __call__(self, value):
...         return value > self.threshold

>>> over_100 = ThresholdChecker(100)
>>> over_100(150)   # True
>>> over_100(50)    # False
```

**判断一个对象是否 callable——`callable(obj)`：**

```python
>>> callable(print)          # True
>>> callable(Counter())      # True——实现了 __call__
>>> callable([1, 2, 3])     # False——list 没有 __call__
```

---

### 5.5 上下文管理器协议——`__enter__` 与 `__exit__`

这两个方法是 `with` 语句的底层机制。在 4.2 的 asyncio 章节会详讲 Context Manager 的高级用法，这里聚焦魔术方法本身。

```python
>>> class ManagedFile:
...     def __init__(self, filename, mode="r"):
...         self.filename = filename
...         self.mode = mode
...     def __enter__(self):
...         self.file = open(self.filename, self.mode)
...         return self.file           # 返回值赋给 as 后的变量
...     def __exit__(self, exc_type, exc_val, exc_tb):
...         self.file.close()          # 无论如何都会执行
...         return False               # False = 不抑制异常；True = 吞掉异常

>>> with ManagedFile("/tmp/test.txt", "w") as f:
...     f.write("hello")
# with 块结束后，文件自动关闭
```

**`__exit__` 的三个参数：**

- `exc_type`：异常类型（没有异常时为 `None`）
- `exc_val`：异常值
- `exc_tb`：traceback 对象

**`__exit__` 的返回值控制异常是否向上传播：**

- 返回 `False`（或 `None`）：异常正常向上抛出——这是最常用的行为
- 返回 `True`：**吞掉**异常——`with` 块外部不会看到这个异常

```python
>>> class SuppressError:
...     def __enter__(self):
...         return self
...     def __exit__(self, exc_type, exc_val, exc_tb):
...         print(f"Suppressed: {exc_type.__name__}: {exc_val}")
...         return True        # 吞掉所有异常

>>> with SuppressError():
...     1 / 0
# Suppressed: ZeroDivisionError: division by zero
# ——程序继续运行，不崩溃
```

**工程实践：除非有非常明确的原因，否则永远不要在 `__exit__` 中返回 `True`。** 吞掉异常会让调用方在不知情的情况下继续执行错误状态，排查难度远大于让它直接崩溃。

---

### 5.6 属性访问陷阱（了解）——`__getattr__` 与 `__getattribute__`

这两个方法只要求"了解"，因为它们容易写出难以调试的代码。但理解它们有助于理解 Python 属性查找的完整机制。

#### 5.6.1 正常的属性查找流程

```
obj.name 的查找顺序：
1. 调用 type(obj).__getattribute__(obj, "name")   ← 无条件拦截
2. 在 type(obj) 及其 MRO 的 __dict__ 中查找 name（data descriptor 优先）
3. 在 obj.__dict__ 中查找 name（实例属性）
4. 在 type(obj) 及其 MRO 中查找 name（non-data descriptor、普通类属性）
5. 以上都失败 → 调用 type(obj).__getattr__(obj, "name")  ← 兜底
6. __getattr__ 也找不到 → 抛出 AttributeError
```

#### 5.6.2 `__getattr__` —— 属性查找失败时的兜底

**只有当常规查找失败后，Python 才会调用 `__getattr__`。**

```python
>>> class DefaultDict:
...     def __init__(self):
...         self._data = {}
...     def __getattr__(self, name):
...         if name.startswith("_"):  # 内部属性直接放行
...             raise AttributeError(name)
...         return self._data.get(name, 0)  # 返回默认值

>>> dd = DefaultDict()
>>> dd.count          # 0——count 不存在，__getattr__ 返回默认值
>>> dd._data          # {}——_data 存在，不走 __getattr__
```

**注意保护哨：`if name.startswith("_")`**——如果没有这个分支，`dd._data` 也会进入 `__getattr__`，而 `__getattr__` 内部又访问了 `self._data`，形成无限递归。同理，在 `__getattr__` 内部访问 `self` 的任何属性时，只能用 `self.__dict__` 或者调用 `super().__getattr__`，不能写 `self.xxx`。

#### 5.6.3 `__getattribute__` —— 拦截所有属性访问

**`__getattribute__` 在每次属性访问时都会被调用——包括属性存在的情况。** 这给了你拦截一切的能力，也带来了极高的风险。

```python
>>> class LoggedAccess:
...     def __init__(self):
...         self._secret = 42
...     def __getattribute__(self, name):
...         if not name.startswith("_"):
...             print(f"Accessing: {name}")
...         return super().__getattribute__(name)  # 必须用 super()，不能写 self.xxx

>>> obj = LoggedAccess()
>>> obj._secret      # 不打印——以 _ 开头
>>> obj.public       # 打印 "Accessing: public" → AttributeError（存在性检查之后）
```

**`__getattribute__` 中无限递归是 100% 会踩的陷阱：**

```python
>>> class Broken:
...     def __getattribute__(self, name):
...         return self.__dict__[name]   # ❌ self.__dict__ 本身又触发 __getattribute__！
```

**黄金规则：在 `__getattribute__` 或 `__getattr__` 内部访问自己的任何属性，必须通过 `super().__getattribute__(name)` 或 `object.__getattribute__(self, name)`，永远不要写 `self.xxx`。** 同样，访问 `self.__dict__` 也会触发 `__getattribute__`——这是故意的，所以你才能在上面那个例子中拦截对 `__dict__` 本身的访问。

#### 5.6.4 `__getattr__` vs `__getattribute__` —— 选哪个

| | `__getattr__` | `__getattribute__` |
|---|---|---|
| 触发时机 | 仅当常规查找**失败**后 | 每次属性访问**都**触发 |
| 风险 | 低——只影响不存在的属性 | 极高——不小心就无限递归 |
| 典型用途 | 代理模式、动态默认值、懒加载 | 日志/审计/调试（记录"谁在什么时间访问了什么"） |
| 推荐程度 | 理解即可，谨慎使用 | 除非你确切知道你在做什么，否则不要覆盖 |

---

### 5.7 总结

| 魔术方法 | 触发语法 | 一句话合约 |
|---------|---------|-----------|
| `__str__` | `str(obj)`、`print(obj)` | 返回给人看的字符串 |
| `__repr__` | `repr(obj)`、`>>> obj` | 返回给开发者看的无歧义字符串，最好能 `eval` |
| `__len__` | `len(obj)` | 返回 `>= 0` 的整数 |
| `__getitem__` | `obj[key]`、`obj[a:b]` | 按 key（或 slice）返回值；实现它就是 iterable |
| `__setitem__` | `obj[key] = value` | 设置值 |
| `__contains__` | `x in obj` | 返回 `bool`；没实现时自动 fallback 到遍历 O(n) |
| `__iter__` | `iter(obj)`、`for x in obj` | 返回一个 iterator |
| `__next__` | `next(obj)` | 返回下一个元素，耗尽时 `raise StopIteration` |
| `__call__` | `obj()` | 让实例像函数一样可调用——有状态的 callable |
| `__enter__` | `with obj:` 进入 | 获取资源，返回值赋给 `as` 变量 |
| `__exit__` | `with obj:` 退出 | 释放资源；返回 `True` 吞异常（几乎永远不该吞） |
| `__getattr__` | `obj.xxx`（xxx 不存在时） | 兜底——只在常规查找全部失败后触发 |

---

## 六、Project 1：Python Collection Library

> **需求明确，方案清晰，是工程化的第一步——在写第一行代码之前，先把"要做什么"和"怎么做"定清楚。**

---

### 6.1 项目目标

#### 什么是"Collection Library"？

在编程中，**collection（集合/容器）** 是指任何存放和组织多个数据的结构。Python 内建了最基础的 collections——`list`、`tuple`、`dict`、`set`——以及标准库 `collections` 模块中的 `deque`、`Counter`、`defaultdict` 等。

但"基础"意味着它们提供了最通用的操作范式。"通用"的另一面是：**它们在具体场景下不都高效，也不都有最直观的接口。**

举例：

- Python 有 `list`，但没有 `Stack`——你可以用 `list.append()` + `list.pop()` 模拟栈的 LIFO，但六个月后别人（或你自己）读这段代码，能在第一眼就确定"这是一个栈"吗？还是只是"一个碰巧只从末尾增删的 list"？
- Python 有 `list` 和 `deque`，但没有 `Queue`——如果你用 `list.pop(0)` 来模拟 `dequeue`，它确实能跑，但每次取元素都要把所有剩余元素左移一位，O(n)。一个 10 万条消息的队列，`dequeue` 一次就要移动 99999 个指针。
- Python 有 `dict`，但没有 `LRUCache`——你可以手写一个限定容量的字典，在 `put` 时检查 `len()` 来决定要不要删某个旧 key。但删哪个？怎么高效地追踪"哪个 key 最久没被用过"？这就不再是"换个名字"的问题，而是数据结构设计的问题。

**这就是 Collection Library 的定义：** 它是在 Python 内建结构之上，提供**语义明确、接口直观、性能可靠**的专用容器。使用者不需要知道内部是 `list`、`deque` 还是 `dict`+双向链表——他们只需要知道"这是一个栈，它能 push 和 pop"。

#### 为什么不直接用标准库？

在真实工程中应该用——`collections.deque`、`functools.lru_cache`、`heapq`、`queue.Queue` 这些标准库模块经过了大量生产验证，自己写的轮子很难比它们更好。

**但这个项目不是"造轮子"，是"拆轮子"——把自己逼到造轮子的位置，才会真正理解轮子为什么长这样。**

具体来说，当你写完这 5 个结构后：

- 你会知道 **Stack 用 list 是对的，Queue 用 list 是灾难**——因为同端操作 O(1)，异端操作 O(n)。标准库的 `deque` 之所以存在，就是为了解决 `list.pop(0)` 的 O(n) 问题。你自己踩过这个坑，以后看任何 Queue 实现第一反应就是"这东西底层是不是 deque"。
- 你会理解 **LRU Cache 的核心不是缓存逻辑，是"如何在 O(1) 时间里找到最久未使用的元素并删掉它"**——这需要同时满足 O(1) 按 key 查找（dict）和 O(1) 维护时序（双向链表+哨兵）。标准库 `functools.lru_cache` 内部也是这个思路，但你手写一遍之后，以后再遇到"需要同时 O(1) 的查找和顺序维护"的需求，会立刻想起这个组合。
- 你会亲手踩 **`(priority, item)` 元组比较的坑**——当两个 item 的 priority 相同时，Python 会去比较 item 本身，如果 item 类型不支持 `<`，就会炸。标准库 `heapq` 文档告诉你"用 tuple 时注意元素可比较性"——但只有你真的写过一个带自定义对象的 Priority Queue 并看到 `TypeError`，才能真正理解为什么需要在 tuple 里加一个 `counter`。

#### 这个项目在前五章的坐标系中处于什么位置

```
前五章学的东西         →    Project 1 怎么用上它
─────────────────────────────────────────────────────
一、数据模型            →   Stack/Queue/LinkedList 都要实现 __len__、__repr__、
    __dict__/__slots__       LRU Cache 的 _Node 用 __slots__ 省内存

二、内置数据结构         →   选对底层：Queue 用 deque 不是 list、
                            PriorityQueue 用 heapq、LRU Cache 用 dict+双向链表

三、函数                 →   每个方法签名的参数设计、TypeVar 泛型约束

四、Pythonic            →   __iter__/__contains__/__getitem__ 让自定义容器
                            融入 Python 的 for/in/[] 语法

五、魔术方法            →   具体落地——每个容器都要实现多个魔术方法来满足协议
```

换句话说，**Project 1 是整个 1.1 Python 高级的综合毕业项目——它不是学完之后的附加题，而是学完之后的验证：你到底是能背语法，还是能用语法解决一个完整的工程问题。**

---

### 6.2 总体设计原则

在拆解每个结构之前，先定几条贯穿所有组件的规则：

1. **统一接口风格**：所有 collection 类共享一致的方法命名和异常行为——`push()`/`put()` 用于添加，`pop()`/`get()` 用于获取并移除，`peek()` 用于获取不移除，`is_empty()` 判断空，`__len__` 返回大小。
2. **使用 Python 协议，不只是自定义方法**：每个 collection 必须实现 `__len__`、`__repr__`；适合的要实现 `__iter__`、`__contains__`、`__getitem__`——让这些类能融入 Python 的 `for`/`in`/`len()`/`[]` 语法。
3. **选择正确的底层实现**：不是每个结构都用 `list`——Queue 用 `deque` 而不是 `list`（否则 `dequeue` 是 O(n)），LRU Cache 用 `dict` + 双向链表（否则 `get` 是 O(n)），Priority Queue 用 `heapq`（否则每次 pop 要 O(n) 扫描）。**选错底层实现是这个项目最核心的扣分项。**
4. **完整的类型标注**：所有公开方法必须有 type hint。
5. **合理的异常**：栈空时 `pop()` 抛 `IndexError`（和 `list.pop` 行为一致），LRU Cache 的 key 不存在时 `get()` 抛 `KeyError`（和 `dict` 行为一致）。

---

### 6.3 各组件详细需求

#### 6.3.1 Stack（栈）

**行为：** 后进先出（LIFO）。最后放进去的元素最先被取出。

**接口定义：**

```python
class Stack[T]:
    def push(self, item: T) -> None: ...
    def pop(self) -> T: ...
    def peek(self) -> T: ...
    def is_empty(self) -> bool: ...
    def __len__(self) -> int: ...
    def __repr__(self) -> str: ...
    def __iter__(self) -> Iterator[T]: ...
```

**方法合约：**

| 方法 | 返回值 | 副作用 | 空栈行为 |
|------|--------|--------|---------|
| `push(item)` | `None` | 将 item 压入栈顶 | — |
| `pop()` | 栈顶元素 | 移除并返回栈顶 | `IndexError("pop from empty stack")` |
| `peek()` | 栈顶元素 | 不移除，只返回 | `IndexError("peek from empty stack")` |
| `is_empty()` | `bool` | 无 | `True` |
| `__len__` | `int` | 无 | `0` |
| `__iter__` | `Iterator` | 无——从栈顶到栈底 | 空迭代器 |

**底层实现方案：** 用 Python `list` 作为内部存储。

```
内部：self._items: list[T] = []

push → self._items.append(item)       # O(1) 摊销
pop  → self._items.pop()              # O(1)
peek → self._items[-1]                # O(1)
```

**为什么选 list：** Stack 的所有操作都在同一端（栈顶），而 `list.append()` 和 `list.pop()` 都是 O(1) 摊销。如果选了 `deque` 也没问题，但 list 对于 Stack 场景已经完全足够，且不需要额外 import。**如果选了链表——那就是把简单问题复杂化，纯 Python 链表的内存和 GC 开销远超 list。**

---

#### 6.3.2 Queue（队列）

**行为：** 先进先出（FIFO）。先放进去的元素最先出来。

**接口定义：**

```python
class Queue[T]:
    def enqueue(self, item: T) -> None: ...
    def dequeue(self) -> T: ...
    def peek(self) -> T: ...
    def is_empty(self) -> bool: ...
    def __len__(self) -> int: ...
    def __repr__(self) -> str: ...
    def __iter__(self) -> Iterator[T]: ...
```

**方法合约：**

| 方法 | 返回值 | 副作用 | 空队列行为 |
|------|--------|--------|-----------|
| `enqueue(item)` | `None` | 将 item 加入队尾 | — |
| `dequeue()` | 队首元素 | 移除并返回队首 | `IndexError("dequeue from empty queue")` |
| `peek()` | 队首元素 | 不移除 | `IndexError("peek from empty queue")` |
| `is_empty()` | `bool` | 无 | `True` |

**底层实现方案——必须用 `collections.deque`，禁止用 `list`：**

```
内部：self._items: deque[T] = deque()

enqueue  → self._items.append(item)    # O(1)
dequeue  → self._items.popleft()       # O(1) ← 这是关键！
```

**为什么禁止用 list：** `list.pop(0)` 也是从左边移除，但它是 O(n)——每次都要把剩余元素全部左移一位。对于 10 万元素的队列，`dequeue()` 一次就要移动 99999 个指针。这是本项目中**最重要的"选择正确底层实现"的考点**：Stack 用 list（同端操作 O(1)），Queue 用 deque（双端操作 O(1)）。

---

#### 6.3.3 LRU Cache（最近最少使用缓存）

**行为：** 固定容量。当缓存满时，淘汰**最久未被访问**的元素。"访问"包括 `get()`（读取）和 `put()`（写入/更新）。

**接口定义：**

```python
class LRUCache[K, V]:
    def __init__(self, capacity: int) -> None: ...
    def get(self, key: K) -> V: ...
    def put(self, key: K, value: V) -> None: ...
    def __len__(self) -> int: ...
    def __contains__(self, key: K) -> bool: ...
    def __repr__(self) -> str: ...
```

**方法合约：**

| 方法 | 返回值 | 副作用 | 异常 |
|------|--------|--------|------|
| `get(key)` | key 对应的 value | **该 key 被标记为"最近使用"** | key 不存在：`KeyError(key)` |
| `put(key, value)` | `None` | 插入/更新；若满则淘汰最久未使用的 key | `capacity` 必须 `> 0`，否则 `ValueError` |
| `__contains__(key)` | `bool` | **不改变**使用顺序（查询存在性不算访问） | — |

**`put` 的精确行为：**
- 如果 `key` 已存在 → 更新 `value`，标记为最近使用
- 如果 `key` 不存在且 `len < capacity` → 直接插入
- 如果 `key` 不存在且 `len == capacity` → **淘汰最久未使用的 key**，然后插入新 key

**`capacity` 边界：**
- `capacity <= 0` → 构造函数抛 `ValueError("capacity must be positive")`
- `capacity == 1` → 正常运作，只有一个元素的 LRU（退化情况不需要特殊处理）

**底层实现方案：`dict` + 双向链表（必须 O(1)）：**

LRU Cache 是本项目中最有挑战的结构——要求 `get` 和 `put` 都必须是 O(1)。

```
需要的操作：
1. 把任意一个已有节点移到"最近使用"端 → O(1)
2. 在"最近使用"端插入新节点           → O(1)
3. 删除"最久未使用"端节点             → O(1)
4. 通过 key 快速找到节点               → O(1)

方案：双向链表（操作 1-3 O(1)）+ dict 做 key→node 映射（操作 4 O(1)）

内部结构示意：

  dict: {key → Node}          ← O(1) 查找
  双向链表: HEAD ↔ node1 ↔ node2 ↔ ... ↔ nodeN ↔ TAIL
                  ↑ 最近使用              ↑ 最久未使用
```

**双向链表的节点：**

```python
class _Node:
    __slots__ = ("key", "value", "prev", "next")  # 省内存——大量节点时有用
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.prev: _Node | None = None
        self.next: _Node | None = None
```

**哨兵节点（Dummy Head/Tail）：** 使用两个哨兵节点 `_head` 和 `_tail`，可以避免插入/删除时对头尾进行空检查。这是链表工程实践中的标准技巧。

```python
# 初始化后的链表：
# _head ↔ _tail
# 插入第一个节点后：
# _head ↔ node1 ↔ _tail
#
# 所有实际的插入/删除操作都在"两个哨兵之间"进行，不需要判断 prev 或 next 是否为 None
```

**操作分解（用哨兵简化后）：**

```
_move_to_front(node):
    _remove_node(node)           # 从链表中摘下
    _add_to_front(node)          # 插到 _head 后面

_remove_node(node):
    node.prev.next = node.next
    node.next.prev = node.prev

_add_to_front(node):
    node.next = self._head.next
    node.prev = self._head
    self._head.next.prev = node
    self._head.next = node

_pop_tail():                     # 淘汰最久未使用（_tail 前面的节点）
    lru = self._tail.prev
    if lru is self._head:        # 链表为空
        return None
    _remove_node(lru)
    return lru
```

**为什么不能用 `OrderedDict`：** Python 的 `OrderedDict` 从 3.7 起已经能实现同样功能（`move_to_end` + `popitem(last=False)`），而且只有几行代码。但本章的 LRU Cache 是**手写版**——目的是通过实现双向链表 + 哨兵模式，把指针操作的肌肉记忆刻进脑子里。在生产环境中确实应该直接用 `OrderedDict`，但在学习环境中，手写一遍是理解"为什么 dict 本身不能维持顺序"和"哨兵模式省了多少空检查"最快的路。

---

#### 6.3.4 Linked List（链表）

**行为：** 单向链表。每个节点持有数据和一个指向下一节点的引用。

**接口定义：**

```python
class LinkedList[T]:
    def append(self, value: T) -> None: ...
    def prepend(self, value: T) -> None: ...
    def insert(self, index: int, value: T) -> None: ...
    def delete(self, value: T) -> bool: ...
    def find(self, value: T) -> _Node[T] | None: ...
    def __getitem__(self, index: int) -> T: ...
    def __len__(self) -> int: ...
    def __iter__(self) -> Iterator[T]: ...
    def __repr__(self) -> str: ...
```

**方法合约：**

| 方法 | 返回值 | 复杂度 | 异常 |
|------|--------|--------|------|
| `append(value)` | `None` | O(1)——维护了 tail 指针 | — |
| `prepend(value)` | `None` | O(1) | — |
| `insert(index, value)` | `None` | O(n)——需要遍历到 index-1 | `index` 越界抛 `IndexError` |
| `delete(value)` | `bool`——是否找到并删除 | O(n) | 未找到返回 `False`（不抛异常） |
| `find(value)` | `_Node` 或 `None` | O(n) | 未找到返回 `None` |
| `__getitem__(index)` | `T` | O(n) | `index < 0` 或 `>= len` 抛 `IndexError` |
| `__iter__` | `Iterator[T]` | O(n) | — |

**内部实现方案：**

```python
class _Node[T]:
    __slots__ = ("value", "next")
    def __init__(self, value: T):
        self.value = value
        self.next: _Node[T] | None = None

class LinkedList[T]:
    def __init__(self):
        self._head: _Node[T] | None = None
        self._tail: _Node[T] | None = None  # 维护尾指针，保证 append 是 O(1)
        self._length: int = 0
```

**关键设计决策：**

- **维护 `_tail` 指针**：没有 tail 指针的 `append` 需要从 head 遍历到末尾，每次 O(n)。加上 tail 指针后，`append` 变成 O(1)——这是生产级链表的基本操作。
- **`delete` 只删第一个匹配项**：如果链表中有多个值等于 `value` 的节点，只删除第一个。和 Python `list.remove()` 行为一致。
- **`__getitem__` 支持负数索引**：`ll[-1]` 返回最后一个元素。这需要先把链表转成 list？不——对于单向链表，`__getitem__` 本身是 O(n)，支持负数索引需要额外处理。建议**不支持负数索引**（和 `list` 不同），在文档中明确说明：链表的 `__getitem__` 只接受 `0 <= index < len`。

---

#### 6.3.5 Priority Queue（优先级队列）

**行为：** 每次 `pop()` 返回**优先级最小**的元素。这是一个**最小优先队列**。

**接口定义：**

```python
from typing import TypeVar, Generic

T = TypeVar("T")

class PriorityQueue[T]:
    def push(self, item: T, priority: int) -> None: ...
    def pop(self) -> T: ...
    def peek(self) -> T: ...
    def is_empty(self) -> bool: ...
    def __len__(self) -> int: ...
    def __repr__(self) -> str: ...
```

**方法合约：**

| 方法 | 返回值 | 副作用 | 空队列行为 |
|------|--------|--------|-----------|
| `push(item, priority)` | `None` | 将 `(priority, counter, item)` 入堆 | — |
| `pop()` | 优先级最小的 item | 移除并返回 | `IndexError("pop from empty priority queue")` |
| `peek()` | 优先级最小的 item | 不移除 | `IndexError("peek from empty priority queue")` |
| `is_empty()` | `bool` | 无 | `True` |

**底层实现方案：用 `heapq` + list + counter 保证 O(log n)：**

```python
import heapq
from itertools import count

class PriorityQueue[T]:
    def __init__(self):
        self._heap: list[tuple[int, int, T]] = []
        self._counter = count()  # 递增计数器，打破优先级相同的比较

    def push(self, item: T, priority: int) -> None:
        heapq.heappush(self._heap, (priority, next(self._counter), item))

    def pop(self) -> T:
        if not self._heap:
            raise IndexError("pop from empty priority queue")
        return heapq.heappop(self._heap)[2]

    def peek(self) -> T:
        if not self._heap:
            raise IndexError("peek from empty priority queue")
        return self._heap[0][2]  # 堆顶是最小元素（不 pop）
```

**为什么 `(priority, counter, item)` 是三元组：** Python 比较元组是从左往右逐个字段比的。如果只用 `(priority, item)`，当两个 item 的 priority 相同时，Python 会尝试比较 item 本身——如果 item 类型的 `<` 没有定义（比如自定义对象），就会在 `heappush` 时抛 `TypeError`。加入递增的 `counter` 作为第二字段，保证每个三元组都是独一无二的（counter 永不重复），优先级相同的 item 按插入顺序排列，且永远不会去比较 item。

**counter 不重置：** `count()` 是从 0 开始的无限递增迭代器，不因 `pop` 而重置。这意味着即使队列空了再 push，counter 也继续递增——不会出现同一个 counter 值的冲突。

---

### 6.4 项目目录结构

```
collection_lib/
├── pyproject.toml              # 项目配置、依赖、类型检查
├── src/
│   └── collection_lib/
│       ├── __init__.py         # 公开 API：from collection_lib import Stack, Queue, ...
│       ├── stack.py
│       ├── queue.py
│       ├── lru_cache.py
│       ├── linked_list.py
│       └── priority_queue.py
└── tests/
    ├── __init__.py
    ├── test_stack.py
    ├── test_queue.py
    ├── test_lru_cache.py
    ├── test_linked_list.py
    └── test_priority_queue.py
```

### 6.5 验收标准

实现完成后，以下检查项必须全部通过：

| # | 检查项 | 怎么验证 |
|---|--------|---------|
| 1 | Stack 的 `push`/`pop`/`peek` 行为正确、空栈抛 `IndexError` | 单元测试 |
| 2 | Queue 的 `enqueue`/`dequeue` 使用 `deque`，不是 `list` | 检查源码——`self._items` 的类型是 `deque` |
| 3 | LRU Cache 的 `get`/`put` 都是 O(1)，容量满时正确淘汰最久未使用的 key | 单元测试 + 人工推算访问序列 |
| 4 | LRU Cache 使用双向链表 + dict，不是 `OrderedDict` | 检查源码——内部有 `_Node` 类和哨兵节点 |
| 5 | Linked List 的 `append`/`prepend` 是 O(1)，维护了 `_tail` 指针 | 检查源码——有 `_tail` 属性且 `append` 直接使用它 |
| 6 | Priority Queue 的 `push`/`pop` 使用 `heapq`，三元组防止 item 比较 | 检查源码——内部是 `(priority, counter, item)` |
| 7 | 所有集合都实现了 `__len__`、`__repr__` | 交互式 `>>> len(obj)` 和 `>>> obj` 正常 |
| 8 | Stack/Queue/LinkedList 实现了 `__iter__` | `for x in obj` 遍历正常 |
| 9 | 所有公开方法有类型标注 | 运行 `mypy src/` 无错误 |
| 10 | LRU Cache 实现了 `__contains__` | `key in cache` 正常 |
| 11 | pyproject.toml 完整可用 | `pip install -e .` 成功 |
| 12 | `capacity <= 0` 时 `LRUCache` 正确抛 `ValueError` | 单元测试 |

### 6.6 实现顺序建议

按复杂度递进、底层依赖关系排列：

```
1. Linked List     ← 纯指针操作，不依赖其他结构，也给 LRU Cache 的双向链表练手
2. Stack           ← 用 list 一行一个方法，最快验证"协议+接口设计"是否正确
3. Queue           ← 和 Stack 镜像设计，但强制用 deque——这时才会意识到选错底层的代价
4. Priority Queue  ← 用 heapq，三元组防比较——到这一步开始用标准库模块做底层
5. LRU Cache       ← 综合项目：dict + 双向链表 + 哨兵模式，把前面都串起来
```

**Stack 在 Linked List 之后做？** 是的——Linked List 让你从零感受"数据结构是内存里怎么组织数据"，做完它再回到 Stack/Queue，你对"用 list 的 append 为什么是 O(1)"会有更深的理解。LRU Cache 放最后是因为它实际上是"双向链表 + dict"的组合，必须先有链表的基础。
| `__getattribute__` | `obj.xxx`（每次） | 拦截一切——内部访问自己的属性必须用 `super()` |


```Python
from abc import ABC, abstractmethod
from contextlib import contextmanager
import sqlite3
from typing import Optional

# ==========================================
# 1. Application 层：定义 Port (接口) & Runtime
# ==========================================


# 端口 (Port)：应用层声明自己需要什么能力，但不关心谁来实现
class UserRepository(ABC):

  @abstractmethod
  def get_user_name(self, user_id: int) -> Optional[str]:
    pass


# 运行时容器：只持有抽象接口
class Runtime:

  def __init__(self):
    self.user_repo: Optional[UserRepository] = None  # 挂载的是接口类型


# ==========================================
# 2. Infrastructure 层：实现 Adapters (适配器)
# ==========================================


# 适配器 A：SQLite 实现
class SqliteUserRepository(UserRepository):

  def __init__(self, conn: sqlite3.Connection):
    self.conn = conn

  def get_user_name(self, user_id: int) -> Optional[str]:
    cursor = self.conn.cursor()
    cursor.execute("SELECT name FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    return row[0] if row else None


# 适配器 B：Postgres 实现
class PostgresUserRepository(UserRepository):

  def __init__(self, dsn: str):
    self.dsn = dsn
    print(f"  [Postgres] 连接到 {dsn}...")

  def get_user_name(self, user_id: int) -> Optional[str]:
    print("  [Postgres] 执行 SQL: SELECT name FROM users...")
    return "Bob"  # 模拟从 Postgres 查出的数据

  def close(self):
    print("  [Postgres] 关闭连接 pool...")


# ==========================================
# 3. 上下文管理器：组装厂 (DI Container)
# ==========================================
@contextmanager
def app_lifespan(runtime: Runtime, db_type: str = "sqlite"):
  print(f"\n[启动] 初始化基础设施，驱动类型: {db_type}")

  if db_type == "sqlite":
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE users (id INT, name TEXT)")
    conn.execute("INSERT INTO users VALUES (1, 'Alice')")
    conn.commit()

    # 实例化适配器并挂载到 Runtime
    runtime.user_repo = SqliteUserRepository(conn)

  elif db_type == "postgres":
    pg_repo = PostgresUserRepository("postgresql://user:pass@localhost/db")
    runtime.user_repo = pg_repo

  try:
    yield runtime
  finally:
    print(f"[关闭] 清理 {db_type} 资源...")
    # 如果适配器有资源清理逻辑，在这里处理
    if db_type == "sqlite":
      conn.close()
    elif db_type == "postgres":
      pg_repo.close()


# ==========================================
# 4. 业务代码 (Application Service)
# ==========================================
def fetch_user_service(runtime: Runtime, user_id: int) -> Optional[str]:
  # 纯粹的依赖倒置：业务逻辑只面向 Port (UserRepository) 编程，没有一行 if-else
  return runtime.user_repo.get_user_name(user_id)


# ==========================================
# 5. 运行测试
# ==========================================
if __name__ == "__main__":
  runtime = Runtime()

  # 场景 A: 使用 SQLite 驱动
  with app_lifespan(runtime, db_type="sqlite"):
    name = fetch_user_service(runtime, user_id=1)
    print(f"-> 业务层获取到用户: {name}")

  # 场景 B: 无缝切换到 Postgres 驱动
  with app_lifespan(runtime, db_type="postgres"):
    # 业务代码 fetch_user_service 内部完全不用改，运行流畅
    name = fetch_user_service(runtime, user_id=1)
    print(f"-> 业务层获取到用户: {name}")
```