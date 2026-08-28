"""Excel 插件——用 openpyxl 解析 .xlsx 为 Document。

职责边界与 pdf_reader 相同：只解析、不管资源、靠继承自动注册。
"""

from typing import BinaryIO

from openpyxl import load_workbook

from ..core.document import Document
from ..core.exceptions import DocumentReaderError
from ..core.reader import DocumentReader


class ExcelReader(DocumentReader):
    """XLSX → Document。"""

    extensions = (".xlsx",)

    def read(self, stream: BinaryIO) -> Document:
        """按 DocumentReader.read 的契约实现：不关 stream、无状态、失败抛 DocumentReaderError。"""
        try:
            # read_only=True：流式解析，大文件省内存（代价：只能读）。
            # data_only=True：公式单元格读【缓存的计算值】而不是公式文本
            #   （=SUM(A1:A2) → 读出 "3"）。注意：缓存值由 Excel 软件保存时
            #   写入——openpyxl 自己生成的文件里没有，公式会读出 None。
            wb = load_workbook(stream, read_only=True, data_only=True)
        except Exception as e:
            # 损坏文件 / 不是 zip 容器时抛 InvalidFileException 等——同上包装。
            raise DocumentReaderError(f"XLSX 解析失败: {e}") from e

        try:
            parts: list[str] = []
            for ws in wb.worksheets:
                parts.append(f"# {ws.title}")   # sheet 名做分节标记
                for row in ws.iter_rows(values_only=True):
                    # 单元格值可能是 None（空格）或数字——过滤 None 并统一转字符串。
                    # 行内用制表符连接，保留"表"的列结构。
                    cells = [str(v) for v in row if v is not None]
                    if cells:                   # 整行为空（只有 None）就不输出
                        parts.append("\t".join(cells))
            return Document(text="\n".join(parts))
        finally:
            # read_only 模式建议显式关闭工作簿以释放底层归档。
            # 它关的是 openpyxl 内部的 ZipFile——ZipFile 从不关闭外部传入的
            # file-like 对象，所以不违反"插件不得关闭 stream"契约（测试会锁定这一点）。
            wb.close()