"""doc_extractor——插件化文档抽取器（OOP Project 2）。

公共 API：Document、Registry、DocumentReader、Extractor、load_plugins。
典型用法：

    from doc_extractor import Extractor, load_plugins

    load_plugins()
    with Extractor() as ex:
        doc = ex.extract("report.pdf")
"""
from .core.document import Document
from .core.extractor import Extractor
from .core.loader import load_plugins
from .core.reader import DocumentReader
from .core.registry import Registry

__all__ = ["Document", "Registry", "DocumentReader", "Extractor", "load_plugins"]