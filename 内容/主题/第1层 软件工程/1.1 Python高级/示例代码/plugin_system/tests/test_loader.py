"""loader 测试——动态加载、坏插件容错、幂等。

策略：用 tmp_path 建【临时插件包】，把包名注入 load_plugins(package=...)，
绝不往真实的 doc_extractor/plugins 目录里写测试文件。

三个坑及解法（都在 fixture 里集中处理）：
1. sys.modules 缓存：多个测试共用同名临时包时，第二次 import 会拿到
   第一个测试的旧模块（顶层代码不重跑 → 类没重新定义）。
   → teardown 里删除 testplugins 前缀的缓存项。
2. sys.path 是进程级全局状态：插进去不拔出来会污染同进程其他测试。
   → teardown 里恢复。
3. 注册表是进程级全局状态：本文件加载的 .tmp 插件会泄漏给其他测试文件。
   → autouse fixture 每个测试前后 clear（与 test_registry.py 同一姿势）。
"""

import sys

import pytest

from doc_extractor import Registry
from doc_extractor.core.loader import load_plugins

PKG = "testplugins"


@pytest.fixture(scope="module", autouse=True)
def _preserve_registry():
    """记住并恢复注册表原状——把本文件对全局注册表的污染关在文件内。

    本文件的每个测试都要 clear 注册表（坑 3），但测试文件按字母序执行，
    test_plugins（p > l）依赖真实插件在 import 时的注册——如果本文件
    清完不恢复，后面的文件会拿到一个被掏空的注册表。
    测试允许接触私有实现（_readers）：Registry 的公共 API 没有快照能力。
    """
    saved = dict(Registry._readers)
    yield
    Registry.clear()
    Registry._readers.update(saved)


@pytest.fixture(autouse=True)
def _clean_registry():
    """注册表隔离（坑 3）。文件级恢复由 _preserve_registry 负责。"""
    Registry.clear()
    yield
    Registry.clear()


@pytest.fixture
def plugins_pkg(tmp_path):
    """创建临时插件包，测试结束清缓存、恢复 sys.path（坑 1、坑 2）。"""
    pkg = tmp_path / PKG
    pkg.mkdir()
    (pkg / "__init__.py").write_text("")
    sys.path.insert(0, str(tmp_path))
    yield pkg
    for name in list(sys.modules):
        if name == PKG or name.startswith(PKG + "."):
            del sys.modules[name]
    sys.path.remove(str(tmp_path))


# 临时包里的"好插件"源码：定义 .tmp 格式的 reader
GOOD_PLUGIN = '''\
from typing import BinaryIO

from doc_extractor import Document, DocumentReader


class TmpReader(DocumentReader):
    extensions = (".tmp",)

    def read(self, stream: BinaryIO) -> Document:
        return Document(text=stream.read().decode("utf-8"))
'''

# "坏插件"源码：顶层直接炸——模拟 import 失败的模块（验收 8）
BAD_PLUGIN = 'raise RuntimeError("boom")'


class TestLoadPlugins:
    def test_load_registers_plugins(self, plugins_pkg):
        """正常插件：加载后进了注册表。"""
        (plugins_pkg / "good_plugin.py").write_text(GOOD_PLUGIN)

        loaded = load_plugins(PKG)

        assert len(loaded) == 1
        assert Registry.get(".tmp") is loaded[0].TmpReader

    def test_skips_bad_plugin(self, plugins_pkg):
        """坏插件容错（验收 8）：坏插件被跳过，好插件正常工作，加载不中断。"""
        (plugins_pkg / "good_plugin.py").write_text(GOOD_PLUGIN)
        (plugins_pkg / "bad_plugin.py").write_text(BAD_PLUGIN)

        loaded = load_plugins(PKG)   # 不抛异常本身就是断言的一部分

        assert Registry.get(".tmp") is not None
        assert len(loaded) == 1
        assert loaded[0].__name__ == f"{PKG}.good_plugin"

    def test_idempotent(self, plugins_pkg):
        """幂等：第二次加载没有任何模块被真正执行（import 缓存）。"""
        (plugins_pkg / "good_plugin.py").write_text(GOOD_PLUGIN)

        assert len(load_plugins(PKG)) == 1
        assert load_plugins(PKG) == []   # 全部命中 sys.modules 缓存

    def test_skips_underscore_modules(self, plugins_pkg):
        """命名约定：下划线开头的模块不是插件，连 import 都不会发生。"""
        (plugins_pkg / "good_plugin.py").write_text(GOOD_PLUGIN)
        # 如果 loader 错误地 import 了它，raise 会直接炸掉测试
        (plugins_pkg / "__bad__.py").write_text(BAD_PLUGIN)

        loaded = load_plugins(PKG)

        assert len(loaded) == 1
        assert Registry.get(".tmp") is not None

    def test_empty_package(self, plugins_pkg):
        """空包：什么都不加载，不抛。"""
        assert load_plugins(PKG) == []