"""两层异常体系（8.5 决策 3）。

- DocumentReaderError：插件内部解析失败时抛——"插件作者的语言"。
  插件只负责报告自己的错误，不关心调用方怎么处理。
- ExtractError：主程序的统一错误——"调用方的语言"。
  无论哪个插件失败、怎么失败，调用方只需要 except ExtractError 一个分支。
  未来新增 100 个插件，调用方的错误处理代码一行都不用改
  （OCP——开放封闭原则在错误处理上的体现）。

分层关系：插件抛 DocumentReaderError → Extractor 包成 ExtractError，
cause 链层层保留，原始异常永远可追溯（验收 7）。
"""

from pathlib import Path


class ExtractError(Exception):
    """extract() 的任何失败最终都是它（或其子类）。"""

    def __init__(self, path: Path, fmt: str, cause: Exception | None = None):
        self.path = path        # 文件路径
        self.fmt = fmt          # 格式标识，通常是扩展名
        self.cause = cause      # 原始异常——cause 链的起点
        msg = f"extract failed: {path} ({fmt})"
        super().__init__(msg if cause is None else f"{msg} -> {cause}")


class UnsupportedFormatError(ExtractError):
    """没有插件支持该扩展名——错误信息必须列出已支持的格式（验收 3）。"""

    def __init__(self, path: Path, fmt: str, supported: list[str]):
        super().__init__(path, fmt)
        self.supported = supported
        # 父类的消息模板是固定的，这里需要附加"已支持格式"信息。
        # Exception 的消息存在 args 里，直接重写是扩展消息的惯用做法
        # （cause 仍为 None，cause 链不受影响）。
        self.args = (
            f"extract failed: {path} ({fmt}) -> unsupported format; "
            f"supported: {', '.join(supported) if supported else '(none)'}",
        )


class ExtractTimeoutError(ExtractError):
    """插件执行超时。

    诚实说明：Python 线程无法被强杀——超时只表示"调用方不等了"，
    线程池里的任务还会继续跑完，文件会在任务结束时正常关闭。
    超时保护的是调用方不被无限阻塞，不是取消底层工作。
    """


class DocumentReaderError(Exception):
    """插件内部解析失败时抛出——这是插件作者报告自己错误的方式。"""