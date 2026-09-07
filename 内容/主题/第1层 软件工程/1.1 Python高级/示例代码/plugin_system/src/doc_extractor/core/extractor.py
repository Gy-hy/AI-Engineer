"""Extractor——主程序层（资源管控 + 分发）。

职责边界（8.4）：
- 管：文件句柄（open/close）、超时、并发上限、异常兜底
- 不管：怎么解析——那是插件的事

多态在这里兑现：_run 只调用 reader.read(stream)，
它不知道也不关心 reader 是 PdfReader 还是未来第 100 个插件。
"""

from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeout
from pathlib import Path
from typing import Iterable

from .document import Document
from .exceptions import (
    ExtractError,
    ExtractTimeoutError,
    UnsupportedFormatError,
)
from .reader import DocumentReader
from .registry import Registry


class Extractor:
    """插件系统对外的门面——调用方只需要认识这一个类。"""

    def __init__(self, timeout: float = 30.0, max_concurrency: int = 4):
        self._timeout = timeout
        # ThreadPoolExecutor 一石二鸟：
        # max_workers 限制并发上限；future.result(timeout) 实现超时。
        # 线程池在 __init__ 创建——Extractor 拥有线程资源，所以提供
        # close()/上下文管理器（资源所有权 = 生命周期管理）。
        self._executor = ThreadPoolExecutor(max_workers=max_concurrency)

    # ---------- 资源生命周期 ----------

    def close(self) -> None:
        """释放线程池（等待已提交任务跑完）。之后本实例不可再用于 extract。"""
        self._executor.shutdown(wait=True)

    def __enter__(self) -> "Extractor":
        return self

    def __exit__(self, *exc) -> None:
        self.close()

    # ---------- 对外接口 ----------

    def extract(self, path: Path | str) -> Document:
        """抽取单个文件。失败统一抛 ExtractError（或其子类）。"""
        path = Path(path)
        reader = self._reader_for(path)
        future = self._executor.submit(self._run, reader, path)
        try:
            return future.result(timeout=self._timeout)
        except FutureTimeout:
            # from None：超时不是由底层异常引起的，不该挂 cause 链
            raise ExtractTimeoutError(path, path.suffix) from None

    def extract_many(self, paths: Iterable[Path | str]) -> list[Document]:
        """批量抽取，结果顺序与输入一致。

        8.5 决策 4——为什么【不能】写成 [self.extract(p) for p in paths]：
        extract = submit + 立即等待。放进列表推导后，每一轮都要先等
        当前任务跑完才提交下一个——任意时刻池中至多 1 个任务在执行，
        并发被完全浪费（总耗时 ≈ 顺序执行之和），max_workers 形同虚设。
        正确做法：提交与等待分离——先把全部任务一次性 submit 进池
        （任务间零依赖、worker 自由领取），主线程再按序收割。
        """
        path_list = [Path(p) for p in paths]
        # 先在快路径查注册表：坏扩展名在提交前就以异常暴露，
        # 而不是进线程池之后变成难排查的 Future 内部错误
        readers = [self._reader_for(p) for p in path_list]
        futures = [self._executor.submit(self._run, r, p)
                   for r, p in zip(readers, path_list)]
        results: list[Document] = []
        for future, p in zip(futures, path_list):
            try:
                results.append(future.result(timeout=self._timeout))
            except FutureTimeout:
                raise ExtractTimeoutError(p, p.suffix) from None
        return results

    # ---------- 内部 ----------

    def _reader_for(self, path: Path) -> DocumentReader:
        """按扩展名找到插件类并实例化。

        注册表存的是类（插件契约无状态），每次现造实例。
        """
        reader_cls = Registry.get(path.suffix)
        if reader_cls is None:
            # 错误信息带扩展名 + 已支持格式列表（验收 3）
            raise UnsupportedFormatError(path, path.suffix, Registry.supported_formats())
        return reader_cls()

    def _run(self, reader: DocumentReader, path: Path) -> Document:
        """线程池中的实际工作：打开文件 → 多态调用 → 异常兜底。

        8.5 决策 2：文件句柄在这里 open/close——资源所有权归主程序，
        插件物理上拿不到打开文件的资格，只能收到已打开的 stream。
        8.5 决策 3：任何异常（包括非 DocumentReaderError 的，如插件代码
        自己的 bug）都包装成 ExtractError，cause 链完整保留（验收 7）。
        """
        try:
            with open(path, "rb") as stream:
                return reader.read(stream)   # 多态调用——只认 Port 接口
        except Exception as e:
            raise ExtractError(path, path.suffix, e) from e