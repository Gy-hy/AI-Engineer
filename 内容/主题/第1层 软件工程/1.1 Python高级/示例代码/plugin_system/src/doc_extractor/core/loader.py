"""动态加载插件——全项目唯一 import 具体插件的地方。

core/ 的其余模块只认 DocumentReader（Port），从不 import 具体插件——
这就是"新增格式 = 丢一个文件进 plugins/，core 与 CLI 零修改"（验收 1）
的机制来源：插件对 core 的可见性由本模块在运行时建立。
"""

import importlib
import logging
import pkgutil
import sys
from types import ModuleType

logger = logging.getLogger(__name__)


def load_plugins(package: str = "doc_extractor.plugins") -> list[ModuleType]:
    """扫描插件包并导入全部插件模块，返回本次真正加载的模块列表。

    加载链：import 模块 → 执行顶层代码 → class 语句 →
    __init_subclass__ → Registry.register——注册是 import 的副作用，
    所以插件文件里不需要（也不应该）出现 import Registry 的代码。

    容错（验收 8）：某个插件模块 import 失败时跳过并告警，绝不静默，
    也不中断其余插件的加载——"一个坏插件拖垮整个系统"比"少一个插件"
    严重得多。（验收 9 的 fail fast 防线在直接 import 路径，各管各的入口。）

    幂等：来自 import 系统的缓存。第二次调用时模块已在 sys.modules，
    顶层代码不会重跑、类不会重复定义、注册不会重复发生——所以这里
    一行幂等代码都不用写。import 的语义就是"执行且只执行一次"。

    参数化包名（DIP）：默认值是真实插件包；测试注入临时包名，
    从而不污染真实的 plugins 目录。
    """
    pkg = importlib.import_module(package)  # 导入插件包本身
    loaded: list[ModuleType] = []  # 加载的插件模块

    # pkgutil.iter_modules 按"模块发现"的语义列出包的直接子模块，
    # name 已带前缀（如 "doc_extractor.plugins.pdf_reader"），
    # __init__ 天然不会被列出。
    for info in pkgutil.iter_modules(pkg.__path__, prefix=package + "."):  # 模块发现 API：沿着 pkg.__path__ 用 finder 列出直接子模块
        name = info.name  # 带前缀的完整模块名
        # 命名约定：下划线开头的模块是私有模块（如 __bad__.py），不是插件
        if name.rsplit(".", 1)[-1].startswith("_"):
            continue
        if name in sys.modules:
            continue    # 已在缓存——幂等：不重复执行模块顶层代码
        try:
            loaded.append(importlib.import_module(name))
        except Exception as e:
            # 容错但留下痕迹——坏插件被跳过这件事必须可观测
            logger.warning("跳过插件 %s: %s", name, e)
    return loaded