"""真实插件测试——三个插件对 DocumentReader 契约的符合性。

fixture 策略：不依赖磁盘样例文件（samples/ 是步骤 7 的事）。
三个解析库都"能读也能写"——测试在内存里生成文档（BytesIO）
再交给插件解析，全程不碰磁盘、无顺序依赖。

与 test_registry.py 的分工：
- test_registry 用假 stub 测【注册机制】本身；
- 本文件用真插件测【真实插件确实注册了】+【read 契约被遵守】。
注册是模块 import 的副作用（收集阶段发生一次、之后只读），
所以本文件不需要也不应该 clear 注册表。
"""

import io

import docx
import pytest
from openpyxl import Workbook
from reportlab.pdfgen import canvas

from doc_extractor import Registry
from doc_extractor.core.exceptions import DocumentReaderError
from doc_extractor.plugins.docx_reader import DocxReader
from doc_extractor.plugins.excel_reader import ExcelReader
from doc_extractor.plugins.markdown_reader import MarkdownReader
from doc_extractor.plugins.pdf_reader import PdfReader


# ---------- 内存 fixture 工厂（可读可写：先在内存里"造"文档） ----------

def _make_pdf() -> io.BytesIO:
    """生成一页含 'hello pdf' 的 PDF。

    注意：reportlab 默认字体 Helvetica 不含中文字形，
    中文文本会乱码——测试内容一律用 ASCII。
    """
    buf = io.BytesIO()
    c = canvas.Canvas(buf)
    c.drawString(100, 750, "hello pdf")
    c.save()
    buf.seek(0)
    return buf


def _make_docx() -> io.BytesIO:
    """生成含一个 'hello docx' 段落的 DOCX。"""
    buf = io.BytesIO()
    d = docx.Document()
    d.add_paragraph("hello docx")
    d.save(buf)
    buf.seek(0)
    return buf


def _make_xlsx() -> io.BytesIO:
    """生成单 sheet、两行数据的 XLSX（第二行含数字，验证 str 转换）。"""
    buf = io.BytesIO()
    wb = Workbook()
    ws = wb.active
    ws.append(["name", "age"])
    ws.append(["alice", 30])
    wb.save(buf)
    buf.seek(0)
    return buf


def _make_md() -> io.BytesIO:
    """生成一个 Markdown 文档（纯文本，无编码要求）。"""
    return io.BytesIO(b"# hello md\n\nsome content")


# 每个用例对全部插件跑一遍（DRY：不写 N 份几乎相同的测试）。
# MarkdownReader 也在列——它就是验收标准 1"零修改扩展"的演示插件，
# 与其余三个走完全相同的测试，证明"新增格式"没有特殊待遇。
PLUGIN_CASES = [
    pytest.param(PdfReader, ".pdf", _make_pdf, "hello pdf", id="pdf"),
    pytest.param(DocxReader, ".docx", _make_docx, "hello docx", id="docx"),
    pytest.param(ExcelReader, ".xlsx", _make_xlsx, "alice", id="xlsx"),
    pytest.param(MarkdownReader, ".md", _make_md, "hello md", id="md"),
]


class TestPlugins:
    @pytest.mark.parametrize("reader_cls, ext, make_buf, expected", PLUGIN_CASES)
    def test_extract_text(self, reader_cls, ext, make_buf, expected):
        """抽取文本：能拿到 fixture 里写进去的内容。"""
        doc = reader_cls().read(make_buf())
        # 用 in 不用 ==：抽取结果常带换行/空白差异，断言内容本身更稳。
        assert expected in doc.text

    @pytest.mark.parametrize("reader_cls, ext, make_buf, expected", PLUGIN_CASES)
    def test_stream_not_closed(self, reader_cls, ext, make_buf, expected):
        """stream 不被关闭：把契约"插件不得关闭 stream"变成可执行断言。

        DocumentReader.read 的 docstring 规定 stream 归主程序管——
        插件只借不还。如果某个插件偷偷 close 了，这个测试立刻抓出来。
        （这也是验收标准 4"插件代码中无 open/close"的运行时兜底。）
        """
        buf = make_buf()
        reader_cls().read(buf)
        assert not buf.closed

    @pytest.mark.parametrize("reader_cls, ext, make_buf, expected", PLUGIN_CASES)
    def test_stateless(self, reader_cls, ext, make_buf, expected):
        """无状态：同一个实例连续 read 两个文档都成功。

        锁定契约"read 不得依赖或修改实例状态"——如果插件把中间结果
        存在实例上（比如上次的页数），第二次 read 就会出错。
        """
        reader = reader_cls()
        assert expected in reader.read(make_buf()).text
        assert expected in reader.read(make_buf()).text

    @pytest.mark.parametrize("reader_cls, ext, make_buf, expected", PLUGIN_CASES)
    def test_auto_registered(self, reader_cls, ext, make_buf, expected):
        """自动注册：真实插件在 import 时就进了注册表（验收标准 9 的机制在真插件上兑现）。"""
        assert Registry.get(ext) is reader_cls

    @pytest.mark.parametrize(
        "reader_cls", [PdfReader, DocxReader, ExcelReader], ids=["pdf", "docx", "xlsx"]
    )
    def test_bad_file_raises_document_reader_error(self, reader_cls):
        """坏文件：插件把库的原始异常包装成 DocumentReaderError（验收标准 7 的前半段）。

        注意 MarkdownReader 不在参数列——纯文本格式任何字节都能解码，
        不存在"坏文件"；这也提醒我们：契约的适用范围因格式而异。
        """
        with pytest.raises(DocumentReaderError):
            reader_cls().read(io.BytesIO(b"this is not a real document"))


class TestPdfMetadata:
    def test_metadata_pages_is_str(self):
        """PDF 的 metadata 契约：键值都是 str（数字要转字符串）。"""
        doc = PdfReader().read(_make_pdf())
        assert doc.metadata["pages"] == "1"