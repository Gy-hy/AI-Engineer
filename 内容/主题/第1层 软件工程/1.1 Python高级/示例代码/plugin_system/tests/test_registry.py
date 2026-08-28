from typing import BinaryIO

import pytest
from doc_extractor import Document, DocumentReader, Registry


def _make_reader(ext: str):
    """按扩展名生成一个具体插件 stub——每次调用都是新类，独立注册。"""
    class _R(DocumentReader):
        extensions = (ext,)

        def read(self, stream: BinaryIO) -> Document:
            text = stream.read()
            return Document(text.decode("utf-8"))
    return _R


@pytest.fixture(autouse=True)
def _clean_registry():
    """每个测试前后清空注册表——注册表是进程级全局状态，必须隔离。"""
    Registry.clear()
    yield
    Registry.clear()


class TestRegistry:
    def test_register_and_get(self):
        """ 注册并取回：具体 stub 类定义后，get(ext) is Stub """
        Txt = _make_reader(".txt")
        assert Registry.get(".txt") is Txt

    def test_not_registered(self):
        """ 未注册：get(ext) is None """
        assert Registry.get(".nope") is None

    def test_no_register_abstract_class(self):
        """ 抽象中间类不注册 """
        class FooReader(DocumentReader):
            extensions: tuple[str, ...] = (".foo",)

        assert Registry.get(".foo") is None

    def test_register_duplicate(self):
        """ 重复注册 fail fast：第二个声明相同扩展名的类定义时报 ValueError """
        _make_reader(".dup")
        with pytest.raises(ValueError):
            _make_reader(".dup")

    def test_supported_formats(self):
        """ supported_formats() 返回已注册扩展名（顺带验证排序） """
        _make_reader(".txt")
        _make_reader(".md")
        assert Registry.supported_formats() == [".md", ".txt"]