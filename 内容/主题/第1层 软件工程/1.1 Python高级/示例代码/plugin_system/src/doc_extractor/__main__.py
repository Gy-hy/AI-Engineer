"""CLI 入口：python -m doc_extractor <文件> [<文件> ...]

安装后可用的 doc-extractor 命令（pyproject.toml 的 [project.scripts]）
也指向这里的 main()。
"""

import argparse
import sys

from .core.exceptions import ExtractError
from .core.extractor import Extractor
from .core.loader import load_plugins


def main(argv: list[str] | None = None) -> int:
    """返回进程退出码（0 成功 / 1 失败）。argv 参数化是为了可测试。"""
    parser = argparse.ArgumentParser(
        prog="doc-extractor",
        description="插件化文档抽取器：从 PDF/DOCX/XLSX/Markdown 抽取纯文本",
    )
    parser.add_argument("paths", nargs="+", help="要抽取的文档路径")
    args = parser.parse_args(argv)

    load_plugins()   # 动态加载全部插件——CLI 不 import 任何具体插件

    try:
        # with：抽完自动释放线程池
        with Extractor() as ex:
            for path in args.paths:
                doc = ex.extract(path)
                print(f"===== {path} =====")
                print(doc.text)
                if doc.metadata:
                    print(f"[metadata] {doc.metadata}")
    except ExtractError as e:
        # 两层异常的价值：调用方只需一个 except 分支——
        # 不管哪个插件失败、怎么失败，处理代码永远是这一行
        print(f"error: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())