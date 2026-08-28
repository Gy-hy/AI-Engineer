from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeout
from pathlib import Path

from .document import Document
from .exceptions import ExtractError, ExtractTimeoutError, UnsupportedFormatError
from .registry import Registry

class Extractor:
    """主程序——资源管控层。管：文件句柄、超时、并发上限、异常兜底。
    不管：怎么解析（那是插件的事）。"""

    def __init__(self, timeout: float = 30.0, max_concurrency: int = 4):
        self._timeout = timeout
        # ThreadPoolExecutor 一石二鸟：
        # max_workers 限制并发数；future.result(timeout) 实现超时
        self._executor = ThreadPoolExecutor(max_workers=max_concurrency)

    def extract(self, path: Path | str) -> Document:
        path = Path(path)
        reader_cls = Registry.get(path.suffix)
        if reader_cls is None:
            raise UnsupportedFormatError(path, path.suffix)
        future = self._executor.submit(self._run, reader_cls(), path)
        try:
            return future.result(timeout=self._timeout)
        except FutureTimeout:
            raise ExtractTimeoutError(path, path.suffix) from None

    def _run(self, reader, path: Path) -> Document:
        """在线程池中执行：打开文件 → 多态调用 → 异常兜底。"""
        try:
            with open(path, "rb") as stream:      # 文件句柄——主程序管
                return reader.read(stream)        # 多态调用——只认 ABC 接口
        except Exception as e:
            raise ExtractError(path, path.suffix, e) from e