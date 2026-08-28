"""doc_extractor——插件化文档抽取器（OOP Project 2）。

所有模块实现完成后，在这里补上公共 API 的 re-export。
"""
from .core.document import Document
from .core.registry import Registry
from .core.reader import DocumentReader

__all__ = ["Document", "Registry", "DocumentReader"]