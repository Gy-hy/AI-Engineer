from dataclasses import dataclass, field

@dataclass(frozen=True)
class Document:
    """抽取结果——所有插件统一输出这个类型。"""
    text: str
    metadata: dict[str, str] = field(default_factory=dict, compare=False)