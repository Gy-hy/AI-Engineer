from dataclasses import FrozenInstanceError

import pytest
from doc_extractor import Document

class TestDocument:

    def test_init_document(self):
        """ 构造 """
        doc = Document("hello")
        assert doc.text == "hello"
        assert doc.metadata == {}
    
    def test_default_independent(self):
        """ 默认值独立 """
        doc1 = Document("hello")
        doc2 = Document("hello")
        doc1.metadata["author"] = "xiaoming"
        assert doc1.metadata == {"author": "xiaoming"}
        assert doc2.metadata == {}

    def test_values_are_equal(self):
        """ 值相等 """
        d1 = Document("hello")
        d2 = Document("hello")
        d3 = Document("world")
        assert d1.text == d2.text
        assert d1 == d2
        assert d1 != d3

    def test_metadata_not_participating(self):
        """ metadata 不参与相等 """
        d1 = Document("hello", metadata={"author": "xiaoming"})
        d2 = Document("hello", metadata={"author": "xiaohong"})
        assert d1 == d2

    def test_document_repr(self):
        """ repr """
        d = Document("hello")
        assert repr(d) == "Document(text='hello', metadata={})"

    def test_freeze_text(self):
        """ 冻结，text不可修改 """
        d = Document("hello")
        with pytest.raises(FrozenInstanceError):
            d.text = 'x'

    def test_shallow_freeze(self):
        """ 浅冻结（锁定文档化行为）"""
        d = Document("hello", metadata={'k':'s'})
        d.metadata["k"] = "v"
        assert d.metadata == {"k": "v"}

    def test_hash(self):
        """ hash """
        d1 = Document("a")
        d2 = Document("a")
        hash(d1)
        assert len({d1, d2}) == 1
        assert hash(d1) == hash(d2)

