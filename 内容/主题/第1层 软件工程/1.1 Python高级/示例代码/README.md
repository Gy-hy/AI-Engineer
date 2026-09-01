# 示例代码

本目录用于存放 `1.1 Python高级` 主题的示例项目与实现代码。

## 项目列表

### collection_lib

手写 Python 集合库，包含 5 个数据结构：`Stack`、`Queue`、`LinkedList`、`PriorityQueue`、`LRUCache`。

- **对应教程：** [01 Python高级](../02%20教程/01%20Python高级.md) — Project 1
- **考点：** 底层选型（Queue 用 deque 非 list）、魔术方法协议、泛型、LRU 的双向链表+哨兵
- **快速开始：**

```bash
cd collection_lib
pip install -e ".[dev]"
pytest -v          # 95 个测试
```

详见 [collection_lib/README.md](collection_lib/README.md)。

---

### plugin_system

插件化文档抽取器——PDF/DOCX/XLSX/Markdown 统一抽取为 `Document`，新增格式 = 在 `plugins/` 新增一个文件，core 零修改。

- **对应教程：** [02 OOP.md](../02%20教程/02%20OOP.md) — Project 2
- **考点：** ABC + `__init_subclass__` 自动注册、多态、封装、dataclass、两层异常、importlib 动态加载、线程池超时/并发
- **快速开始：**

```bash
cd plugin_system
uv sync --extra dev
uv run pytest -v
uv run python -m doc_extractor samples/sample.pdf
```

详见 [plugin_system/README.md](plugin_system/README.md)。

---

## 目录约定

- 不预先按章节创建空目录
- 直接按实际示例项目创建文件夹
- 每个项目目录单独写 `README.md`，至少说明对应章节、解决的问题、如何运行