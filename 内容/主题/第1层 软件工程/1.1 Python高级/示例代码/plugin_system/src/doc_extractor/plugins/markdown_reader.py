"""Markdown 插件——验收标准 1 的现场演示：零修改扩展。

新增一种格式支持的全部工作 = 在 plugins/ 新增本文件（继承 DocumentReader）。
core/、loader、CLI 全部零修改——它们只认 DocumentReader 这个 Port。
"""

from typing import BinaryIO

from ..core.document import Document
from ..core.exceptions import DocumentReaderError
from ..core.reader import DocumentReader


class MarkdownReader(DocumentReader):
    """Markdown → Document（纯文本格式，解析就是解码）。"""

    extensions = (".md",)

    def read(self, stream: BinaryIO) -> Document:
        try:
            text = stream.read().decode("utf-8")
        except Exception as e:
            raise DocumentReaderError(f"Markdown 解析失败: {e}") from e
        return Document(text=text)