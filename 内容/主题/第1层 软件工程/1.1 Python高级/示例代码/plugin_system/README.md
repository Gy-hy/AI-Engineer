# doc_extractor —— 插件化文档抽取器

`1.1 Python高级` 主题的 **OOP Project 2（必做项目：插件系统）**。

把 PDF / DOCX / XLSX / Markdown 统一抽取为 `Document`。**新增格式支持 = 在 `plugins/` 下新增一个文件，core 与 CLI 零修改。**

## 架构

```
src/doc_extractor/
├── __main__.py          # CLI 入口
├── core/                # 主程序层——只认 DocumentReader（Port），从不 import 具体插件
│   ├── document.py      # Document 数据类（frozen + compare=False）
│   ├── exceptions.py    # 两层异常：DocumentReaderError → ExtractError
│   ├── reader.py        # DocumentReader ABC + __init_subclass__ 自动注册
│   ├── registry.py      # 扩展名 → 插件类
│   ├── loader.py        # importlib 动态加载（唯一 import 具体插件的地方）
│   └── extractor.py     # 资源管控 + 分发 + 超时/并发/异常兜底
└── plugins/             # 插件目录——新增格式只改这里
```

## 快速开始

```bash
cd plugin_system
uv sync --extra dev                            # 装依赖（pytest/reportlab 在 dev 组）
uv run pytest                                  # 全部测试
uv run python samples/make_samples.py          # 生成样例文件
uv run python -m doc_extractor samples/sample.pdf
```

## 如何新增一种格式

1. 在 `plugins/` 下新建一个文件，继承 `DocumentReader`、声明 `extensions`、实现 `read(stream)`——**注册自动发生**（`__init_subclass__`）。
2. 完。`core/`、loader、CLI 全部零修改。示例见 `plugins/markdown_reader.py`（它本身就是验收标准 1 的现场演示）。

插件必须遵守的契约（`DocumentReader.read` 的 docstring）：

- stream 由主程序打开并关闭，插件不得 close
- 解析失败抛 `DocumentReaderError`
- 无状态——read 不得依赖或修改实例状态

## 测试

| 文件 | 覆盖 |
|---|---|
| `test_document.py` | Document 数据类契约（冻结、相等、哈希、浅冻结） |
| `test_registry.py` | 注册机制（自动注册、抽象类跳过、fail fast、测试隔离） |
| `test_loader.py` | 动态加载、坏插件容错、幂等、下划线过滤 |
| `test_plugins.py` | 插件对 read 契约的符合性（含验收 1 的 md 插件） |
| `test_extractor.py` | 分发、超时、并发限制、异常兜底（验收 3/5/6/7） |

## 对应教程

[02 OOP.md](../../02%20教程/02%20OOP.md) — 第八节 Project 2：插件系统（8.7 验收标准逐条对应）。