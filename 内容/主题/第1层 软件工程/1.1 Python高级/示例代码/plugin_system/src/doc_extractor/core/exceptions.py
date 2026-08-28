
class ExtractError(Exception):
    """主程序的统一错误——extract() 的任何失败最终都是它（或其子类）。"""
    
    def __init__(self, path, fmt: str, cause: Exception | None = None):
        self.path = path        # 文件路径
        self.fmt = fmt      # 文件格式标识，通常就是扩展名（"pdf"、"docx"）
        self.cause = cause      # 原始异常——保留完整 cause 链
        msg = f"extract failed: {path} ({fmt})"
        super().__init__(msg if cause is None else f"{msg} -> {cause}")  # 最终字符串传给 Exception 的构造器，str(e)就返回该字符串

class UnsupportedFormatError(ExtractError):
    """没有插件支持该扩展名——错误信息必须列出已支持的格式。"""




class ExtractTimeoutError(ExtractError):
    """插件执行超时。"""


class DocumentReaderError(Exception):
    """插件内部解析失败时抛出——这是插件作者报告自己错误的方式。"""

