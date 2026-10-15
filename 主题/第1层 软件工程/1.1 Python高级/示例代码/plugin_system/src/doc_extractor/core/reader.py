from abc import ABC, abstractmethod
from typing import BinaryIO

from .document import Document
from .registry import Registry

class DocumentReader(ABC):
    """Port——所有插件必须继承这个抽象基类。

    插件作者要做的全部事情：
    1. 继承 DocumentReader
    2. 声明 extensions（支持的扩展名）
    3. 实现 read()
    ——注册自动发生（见 __init_subclass__）。
    """

    extensions: tuple[str, ...] = ()
    """支持的扩展名，如 (".pdf",)。"""

    def __init_subclass__(cls, **kwargs):
        """类定义完成时自动注册（3.5 节的模式）。"""
        super().__init_subclass__(**kwargs)
        if not cls._remaining_abstract_methods():
            Registry.register(cls)  # 只有具体类才注册——中间抽象类跳过

    @classmethod
    def _remaining_abstract_methods(cls) -> set[str]:
        """cls 创建完成后还会剩下哪些抽象方法？

        不能直接读 cls.__abstractmethods__，理由见下方"陷阱"说明。
        按 ABCMeta 自己的算法提前算一遍：
        1. 本类新声明的抽象方法；
        2. 父类未实现的抽象方法中，本类没有覆盖成具体实现的。
        """
        abstract = {
            name
            for name, value in vars(cls).items()
            if getattr(value, "__isabstractmethod__", False)
        }
        for base in cls.__bases__:
            for name in getattr(base, "__abstractmethods__", frozenset()):
                if getattr(getattr(cls, name, None), "__isabstractmethod__", False):
                    abstract.add(name)
        return abstract

    @abstractmethod
    def read(self, stream: BinaryIO) -> Document:
        """从已打开的文件流解析出 Document。

        契约（必须遵守）：
        - stream 由主程序打开并负责关闭——插件【不得】关闭它
        - 解析失败时抛 DocumentReaderError（其他异常主程序也会兜底）
        - 实现必须无状态——read() 不得依赖或修改实例状态
        """
        ...