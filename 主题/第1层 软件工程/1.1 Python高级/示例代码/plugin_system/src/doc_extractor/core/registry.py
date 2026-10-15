from typing import TYPE_CHECKING

if TYPE_CHECKING:                      # 只给类型检查器用——避免循环
    from .reader import DocumentReader

class Registry:
    """扩展名 → 插件类的映射。"""

    _readers: dict[str, "type[DocumentReader]"] = {}

    @classmethod
    def register(cls, reader_cls: "type[DocumentReader]") -> None:
        """注册插件类。重复扩展名立即报错——fail fast。"""
        if not reader_cls.extensions:
            raise ValueError(f"{reader_cls.__name__} must declare extensions")
        for ext in reader_cls.extensions:
            if not (isinstance(ext, str) and ext.startswith(".")):
                raise ValueError(f"invalid extension {ext!r}: must be str starting with '.'")
            if ext in cls._readers:
                raise ValueError(
                    f"extension {ext!r} already registered by {cls._readers[ext].__name__}"
                )
            cls._readers[ext] = reader_cls

    @classmethod
    def get(cls, extension: str) -> "type[DocumentReader] | None":
        """按扩展名查插件——没有返回 None。"""
        return cls._readers.get(extension)

    @classmethod
    def supported_formats(cls) -> list[str]:
        """已注册的全部扩展名——给错误信息用。"""
        return sorted(cls._readers)

    @classmethod
    def clear(cls) -> None:
        """清空注册表——测试用（每个测试重新开始）。"""
        cls._readers.clear()