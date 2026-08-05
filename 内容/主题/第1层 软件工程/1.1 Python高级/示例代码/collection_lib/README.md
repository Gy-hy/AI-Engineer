# collection_lib

## 对应章节

- 主题：`1.1 Python高级`
- 对应教程章节：[01 Python高级](../02%20教程/01%20Python高级.md)
- 关联内容：
  - Python 内置数据结构
  - 泛型与类型标注
  - 魔术方法与协议

## 项目目标

手写一个小型集合库，包含 5 个常用数据结构。不是为了"造轮子"，而是通过实现过程理解：

- 每种结构**该选什么底层**（Queue 用 deque 不能是 list、LRU Cache 用 dict+双向链表）
- 如何让自定义容器**融入 Python 语法**（`__len__`、`__iter__`、`__contains__`、`__getitem__`）
- 泛型怎么用（`Stack[int]`、`LRUCache[str, int]`）

## 已实现

| 组件 | 底层 | 核心考点 |
|------|------|---------|
| `Stack[T]` | `list` | 同端操作 O(1) |
| `Queue[T]` | `deque` | **禁止用 list**——`popleft()` 是 O(1)，`list.pop(0)` 是 O(n) |
| `LinkedList[T]` | 单向链表（`_Node`） | `_tail` 指针保 O(1) append、哨兵思想 |
| `PriorityQueue[T]` | `heapq` | `(priority, counter, item)` 三元组防 TypeError |
| `LRUCache[K, V]` | `dict` + 双向链表 + 哨兵 | get/put 双 O(1) |

## 目录结构

```
collection_lib/
├── pyproject.toml
├── README.md
├── src/
│   └── collection_lib/
│       ├── __init__.py
│       ├── stack.py
│       ├── queue.py
│       ├── linked_list.py
│       ├── priority_queue.py
│       └── lru_cache.py
└── tests/
    ├── __init__.py
    ├── test_stack.py
    ├── test_queue.py
    ├── test_linked_list.py
    ├── test_priority_queue.py
    └── test_lru_cache.py
```

## 快速开始

### 安装

```bash
cd "内容/主题/第1层 软件工程/1.1 Python高级/示例代码/collection_lib"
pip install -e ".[dev]"
```

### 跑测试

```bash
# 全部
pytest

# 详细信息
pytest -v

# 单个文件
pytest tests/test_stack.py -v

# 单个测试
pytest tests/test_lru_cache.py::TestLRUCache::test_evicts_lru_when_full -v
```

### 试一下

```python
from collection_lib import Stack, Queue, LinkedList, PriorityQueue, LRUCache

# Stack —— LIFO
s = Stack[int]()
s.push(1); s.push(2); s.push(3)
print(s.pop())   # 3
print(list(s))   # [2, 1]（栈顶→栈底）

# LRU Cache —— 容量 2
c = LRUCache[str, int](capacity=2)
c.put("a", 1); c.put("b", 2)
c.get("a")       # 1——访问让 a 变"最近使用"
c.put("c", 3)    # 淘汰 b（最久没被访问）
print("a" in c)  # True
print("b" in c)  # False
```