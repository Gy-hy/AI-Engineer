# doc_extractor —— 插件化文档抽取器

`1.1 Python高级` 主题的 **OOP Project 2（必做项目：插件系统）**。

把 PDF / DOCX / XLSX / Markdown 统一抽取为 `Document`。**新增格式支持 = 在 `plugins/` 下新增一个文件，core 与 CLI 零修改。**

前置知识：教程 [02 OOP.md](../../02%20教程/02%20OOP.md) 第一至七章。建议读完一遍后再回来精读本项目的代码。

## 目录

- [5 分钟跑起来](#5-分钟跑起来)
- [学习路线：按什么顺序读](#学习路线按什么顺序读)
- [考点地图：每个文件教什么](#考点地图每个文件教什么)
- [动手实验清单](#动手实验清单)
- [测试即契约](#测试即契约)
- [坑与陷阱速查表](#坑与陷阱速查表)
- [常见问题：几个设计决策的为什么](#常见问题几个设计决策的为什么)
- [架构](#架构)
- [如何新增一种格式](#如何新增一种格式)
- [对应教程](#对应教程)

---

## 5 分钟跑起来

先体验再解剖——在读懂代码之前，先看系统活着：

```bash
cd plugin_system
uv sync --extra dev                            # 依赖（pytest/reportlab 在 dev 组）
uv run pytest                                  # 47 个测试全绿
uv run python samples/make_samples.py          # 生成样例文件
uv run python -m doc_extractor samples/sample.pdf
uv run python -m doc_extractor README.md       # ← 试试这个：.md 也能抽（第 4 个插件）
```

## 学习路线：按什么顺序读

阅读顺序 = **依赖方向**。谁被依赖谁先读：`document` 被 `reader` 依赖，`reader/registry` 被插件依赖，插件被 `loader/extractor` 依赖，最后才是 CLI。每个概念都在前一步有铺垫。

**每步的读法：先读测试，再读实现。** 测试是这个系统最精确的规格说明书——没有废话，每一条断言都是一条被锁死的契约。读实现时对照注释里的"为什么"，跑一遍该文件的测试，再做对应实验。

| 步 | 读什么 | 时间 | 学到的 OOP 概念 | 该动手的事 |
|---|--------|------|----------------|-----------|
| 0 | 上面的"5 分钟跑起来" | 5min | 全局感知 | — |
| 1 | `core/document.py` + `test_document.py` | 15min | dataclass、frozen、`compare=False` 的坑 | 实验 1 |
| 2 | `core/reader.py` + `core/registry.py` + `test_registry.py` | 30min | ABC、abstractmethod、`__init_subclass__` 自动注册 | 实验 2（全项目最重要的坑） |
| 3 | `plugins/pdf_reader.py` → 对比其余三个 + `test_plugins.py` | 30min | 多态、封装（库的脏活锁在插件里） | 实验 3（亲手加一个插件） |
| 4 | `core/exceptions.py` + `core/loader.py` + `core/extractor.py` + 对应测试 | 30min | 异常分层、DIP、importlib、线程池、8.5 四个决策 | 实验 4、5 |
| 5 | `__main__.py` + `samples/` + `test_loader.py` 的坑注释 | 10min | 组合根、资源生命周期 | — |

## 考点地图：每个文件教什么

| 文件 | 教学重点 | 对应教程章节 |
|------|---------|-------------|
| `core/document.py` | frozen dataclass；dict 字段必须 `compare=False`（否则 `__hash__` 炸） | 六、数据类 |
| `core/reader.py` | ABC + abstractmethod；`__init_subclass__` 自动注册；`__abstractmethods__` 陷阱 | 五、抽象；3.5；8.4 陷阱说明 |
| `core/registry.py` | 类方法；`TYPE_CHECKING` 解循环导入；fail fast；"存类不存实例" | 二、封装；8.4 |
| `core/exceptions.py` | 两层异常（插件语言 → 调用方语言）；cause 链；OCP 在错误处理上的体现 | 8.5 决策 3 |
| `core/loader.py` | importlib 动态加载；幂等来自 import 缓存；参数化包名（DIP） | 7.1；8.7 验收 8 |
| `core/extractor.py` | 资源所有权（open/close 归主程序）；线程池双职（并发+超时）；`extract_many` 提交/等待分离（复用 `extract()` 会丢并发）；上下文管理器 | 8.5 决策 2、4 |
| `plugins/*.py` | 多态落地；各库 API 怪癖的封装；read 契约（不关 stream、无状态） | 四、多态；二、封装 |
| `__main__.py` | 组合根：唯一的对象装配点；`main(argv)` 参数化 | 7.1（DIP） |
| `tests/*.py` | 测试隔离（fixture 双清、快照恢复）；契约测试（stream 不被关） | 8.7 |

## 动手实验清单

每个实验 10 分钟以内。做完你对系统的理解会完全不同。破坏后记得改回来（或用 `git diff`/`git checkout` 恢复）。

1. **`compare=False` 为什么必须存在**：删掉 `document.py` 里的 `compare=False` → 跑 `uv run pytest tests/test_document.py`，看哪些测试炸、为什么。再在 REPL 里 `hash(Document("a"))` 亲自看 TypeError。
2. **`__abstractmethods__` 陷阱（必做）**：在 `reader.py` 的 `__init_subclass__` 里加一行 `print(cls.__abstractmethods__)` → 跑 `uv run pytest tests/test_plugins.py` → 类定义阶段直接 AttributeError。然后想：为什么"看起来天经地义"的写法会炸？（答案在教程 8.4 的陷阱说明。）
3. **亲手加一个插件（验收 1 亲历版）**：新建 `plugins/txt_reader.py`（继承 `DocumentReader`、`extensions = (".txt",)`、`read` 里 decode）→ `echo hello > /tmp/x.txt && uv run python -m doc_extractor /tmp/x.txt`。整个过程中 core/ 和 CLI 一行没改——这就是"零修改扩展"。
4. **坏插件容错**：往 `plugins/` 放一个顶层 `raise RuntimeError("boom")` 的文件 → CLI 依然正常工作，只是多一条 warning。删掉它。
5. **并发限制的探针测试**：把 `test_extractor.py` 的 `test_max_concurrency_one` 里 `max_concurrency=1` 改成 4 → 测试必挂。这就是"探针测试"锁死行为的方式。

## 测试即契约

47 个测试 = 47 条锁死的契约，分三个层次：

- **行为测试**：`test_extract_text`——能抽出内容；
- **契约测试**：`test_stream_not_closed`、`test_stateless`——docstring 里的规则变成了会失败的断言；
- **陷阱回归测试**：`test_register_duplicate`（fail fast）、`test_skips_bad_plugin`（容错）、`test_max_concurrency_one`（并发）——每一条都对应一个"不写测试就会悄悄坏掉"的坑。

学习用法：读实现前先读同目录的测试；每步只跑一个文件（如 `uv run pytest tests/test_registry.py -v`）；修改任何代码后全量跑一遍——测试是你每次破坏的安全网。

## 坑与陷阱速查表

本项目开发中真实踩过（并已修复/解释）的坑，每个都值得懂"为什么"：

| 坑 | 现象 | 原理 | 出处 |
|---|------|------|------|
| `cls.__abstractmethods__` 在 `__init_subclass__` 里 AttributeError | 插件类一定义就炸 | ABCMeta 在 `__init_subclass__` 返回后才写入该属性；且 CPython 对此名的查找只查自己的 `__dict__`、不走 MRO（bpo-10006） | `reader.py` 注释 + 教程 8.4 |
| dict 字段的 frozen dataclass 不可哈希 | `hash(doc)` 抛 TypeError | 自动生成的 `__hash__` 覆盖所有参与 eq 的字段，dict 不可哈希 | `document.py` |
| 批量抽取用列表推导复用 `extract()` | 并发全丢，总耗时 ≈ 串行 | `extract()` = submit + 立即等待；推导式每轮等当前任务完成才提交下一个，池中至多 1 个任务在跑 | `extractor.py` 的 `extract_many` 注释 |
| 超时 ≠ 取消 | 超时后任务还在跑 | Python 线程无法强杀，超时只是"调用方不等了" | `exceptions.py` 的 `ExtractTimeoutError` |
| 测试跨文件污染 | 加了新测试文件后旧测试莫名挂 | 注册表是进程级全局状态；clear 了别人的东西要恢复 | `test_loader.py` 的 `_preserve_registry` |
| sys.modules 缓存 + 同名临时包 | 第二个测试拿到第一个测试的旧模块 | import 的语义是"执行且只执行一次" | `test_loader.py` 的 fixtures 注释 |
| 公式单元格抽出来是空的 | XLSX 某单元格缺失 | `data_only=True` 读缓存值，缓存值由 Excel 软件保存时写入 | `excel_reader.py` / `make_samples.py` |
| reportlab 中文乱码 | PDF 中文变方块 | 默认字体 Helvetica 无中文字形 | `test_plugins.py` / `make_samples.py` |

## 常见问题：几个设计决策的为什么

- **注册表为什么存类不存实例？** 插件契约是无状态的（`read` 不依赖实例状态），存类最省事；也反过来约束了插件必须无状态。
- **`Registry.get` 为什么返回 None 而不是抛 KeyError？** 查不到扩展名是正常业务情形（用户给了一个 .txt），不是编程错误——由调用方（Extractor）决定怎么处理。
- **插件文件里为什么没有 `import Registry`？** 注册是 import 的副作用：`load_plugins` → import 模块 → 类定义 → `__init_subclass__` → `Registry.register`。写进去反而是画蛇添足。
- **`plugins/__init__.py` 为什么是空的？** 谁 import 插件是架构决策——归 loader 管。在这里 import 就成了隐式加载，破坏"动态发现"的机制。
- **`excel_reader.py` 里的 `wb.close()` 不算违反"插件不得关闭 stream"吗？** 它关的是 openpyxl 内部的 ZipFile 归档，不是 stream——ZipFile 从不关闭外部传入的 file-like 对象，`test_stream_not_closed` 测试锁死了这一点。

## 架构

```
src/doc_extractor/
├── __main__.py          # CLI 入口（组合根）
├── core/                # 主程序层——只认 DocumentReader（Port），从不 import 具体插件
│   ├── document.py      # Document 数据类（frozen + compare=False）
│   ├── exceptions.py    # 两层异常：DocumentReaderError → ExtractError
│   ├── reader.py        # DocumentReader ABC + __init_subclass__ 自动注册
│   ├── registry.py      # 扩展名 → 插件类
│   ├── loader.py        # importlib 动态加载（唯一 import 具体插件的地方）
│   └── extractor.py     # 资源管控 + 分发 + 超时/并发/异常兜底
└── plugins/             # 插件目录——新增格式只改这里
```

调用链：`CLI → load_plugins()（import 插件 → 自动注册）→ Extractor.extract(path) → Registry.get(后缀) → reader.read(stream) → Document`

## 如何新增一种格式

1. 在 `plugins/` 下新建一个文件，继承 `DocumentReader`、声明 `extensions`、实现 `read(stream)`——**注册自动发生**（`__init_subclass__`）。
2. 完。`core/`、loader、CLI 全部零修改。示例见 `plugins/markdown_reader.py`（它本身就是验收标准 1 的现场演示）。

插件必须遵守的契约（`DocumentReader.read` 的 docstring）：

- stream 由主程序打开并关闭，插件不得 close
- 解析失败抛 `DocumentReaderError`
- 无状态——read 不得依赖或修改实例状态

## 测试文件清单

| 文件 | 覆盖 |
|---|---|
| `test_document.py` | Document 数据类契约（冻结、相等、哈希、浅冻结） |
| `test_registry.py` | 注册机制（自动注册、抽象类跳过、fail fast、测试隔离） |
| `test_loader.py` | 动态加载、坏插件容错、幂等、下划线过滤 |
| `test_plugins.py` | 插件对 read 契约的符合性（含验收 1 的 md 插件） |
| `test_extractor.py` | 分发、超时、并发限制、异常兜底（验收 3/5/6/7） |

## 对应教程

[02 OOP.md](../../02%20教程/02%20OOP.md) — 第八节 Project 2：插件系统（8.7 验收标准逐条对应）。