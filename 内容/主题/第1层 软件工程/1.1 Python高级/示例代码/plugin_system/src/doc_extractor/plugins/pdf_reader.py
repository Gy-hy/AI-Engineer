"""PDF 插件——用 pypdf 解析 PDF 为 Document。

职责边界（架构约定）：
- 本文件只负责【解析】：pypdf 的 API 怪癖全部锁在这里，
  不泄漏到 core/ 或调用方；
- 不负责【资源】：不 open()、不 close()——stream 由主程序打开并关闭；
- 不负责【注册】：继承 DocumentReader 即自动注册，无需 import Registry。

新增一种格式支持 = 复制本文件的模式新建一个插件文件，core/ 零修改。
"""

from typing import BinaryIO

from pypdf import PdfReader as PyPdfReader

from ..core.document import Document
from ..core.exceptions import DocumentReaderError
from ..core.reader import DocumentReader


class PdfReader(DocumentReader):
    """PDF → Document。"""

    extensions = (".pdf",)

    def read(self, stream: BinaryIO) -> Document:
        """按 DocumentReader.read 的契约实现：不关 stream、无状态、失败抛 DocumentReaderError。"""
        try:
            # 库的类与本插件类同名，import 时已别名为 PyPdfReader。
            # PyPdfReader 接受 file-like，所以 BinaryIO 契约直接可用。
            pdf = PyPdfReader(stream)
        except Exception as e:
            # 库抛的是它自己的语言（PdfReadError、EmptyFileError 等）——
            # 包装成 DocumentReaderError（插件作者的语言），并保留 cause 链。
            # 更上层的 Extractor 会再包成 ExtractError（调用方的语言）。
            raise DocumentReaderError(f"PDF 解析失败: {e}") from e

        texts: list[str] = []
        for page in pdf.pages:
            text = page.extract_text()
            # extract_text() 对扫描版 PDF、纯图片页会返回 None 或空串——
            # 必须过滤，否则 join 时会炸。没有文字的页不算错误，跳过即可。
            if text:
                texts.append(text)

        return Document(
            text="\n".join(texts),
            # metadata 的契约是 dict[str, str]——值必须是字符串，数字要转。
            metadata={"pages": str(len(pdf.pages))},
        )