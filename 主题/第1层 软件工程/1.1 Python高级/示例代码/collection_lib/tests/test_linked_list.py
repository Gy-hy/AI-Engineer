import pytest
from collection_lib import LinkedList


class TestLinkedList:
    """LinkedList（单向链表）单元测试。"""

    # ── append ──────────────────────────────────

    def test_append_to_empty(self):
        ll = LinkedList[int]()
        ll.append(1)
        assert ll.head is not None
        assert ll.tail is not None
        assert ll.head is ll.tail           # 第一个节点 head==tail
        assert ll.head.value == 1
        assert len(ll) == 1

    def test_append_multiple(self):
        ll = LinkedList[int]()
        ll.append(1)
        ll.append(2)
        ll.append(3)
        assert list(ll) == [1, 2, 3]
        assert ll.tail.value == 3           # tail 正确更新
        assert len(ll) == 3

    # ── prepend ─────────────────────────────────

    def test_prepend_to_empty(self):
        ll = LinkedList[int]()
        ll.prepend(1)
        assert ll.head is ll.tail
        assert ll.head.value == 1
        assert len(ll) == 1

    def test_prepend_multiple(self):
        ll = LinkedList[int]()
        ll.append(2)
        ll.append(3)
        ll.prepend(1)
        assert list(ll) == [1, 2, 3]         # 1 在最前面
        assert ll.head.value == 1
        assert ll.tail.value == 3
        assert len(ll) == 3

    # ── insert ─────────────────────────────────

    def test_insert_at_beginning(self):
        ll = LinkedList[int]()
        ll.append(2)
        ll.append(3)
        ll.insert(0, 1)
        assert list(ll) == [1, 2, 3]

    def test_insert_at_end(self):
        ll = LinkedList[int]()
        ll.append(1)
        ll.append(2)
        ll.insert(2, 3)                      # index == len → append
        assert list(ll) == [1, 2, 3]

    def test_insert_in_middle(self):
        ll = LinkedList[int]()
        ll.append(1)
        ll.append(3)
        ll.insert(1, 2)
        assert list(ll) == [1, 2, 3]

    def test_insert_negative_index_raises(self):
        ll = LinkedList[int]()
        with pytest.raises(IndexError):
            ll.insert(-1, 1)

    def test_insert_out_of_bounds_raises(self):
        ll = LinkedList[int]()
        ll.append(1)
        with pytest.raises(IndexError):
            ll.insert(2, 99)                 # index > len

    def test_insert_into_empty_at_zero(self):
        ll = LinkedList[int]()
        ll.insert(0, 1)
        assert list(ll) == [1]

    # ── delete ──────────────────────────────────

    def test_delete_head(self):
        ll = LinkedList[int]()
        ll.append(1)
        ll.append(2)
        assert ll.delete(1) is True
        assert list(ll) == [2]
        assert ll.head.value == 2

    def test_delete_tail(self):
        ll = LinkedList[int]()
        ll.append(1)
        ll.append(2)
        assert ll.delete(2) is True
        assert list(ll) == [1]
        assert ll.tail.value == 1             # tail 正确更新

    def test_delete_middle(self):
        ll = LinkedList[int]()
        ll.append(1)
        ll.append(2)
        ll.append(3)
        assert ll.delete(2) is True
        assert list(ll) == [1, 3]

    def test_delete_single_element(self):
        ll = LinkedList[int]()
        ll.append(1)
        assert ll.delete(1) is True
        assert ll.head is None
        assert ll.tail is None                # 变为空链表
        assert len(ll) == 0

    def test_delete_non_existent(self):
        ll = LinkedList[int]()
        ll.append(1)
        assert ll.delete(99) is False
        assert len(ll) == 1                   # 长度不变

    def test_delete_from_empty(self):
        ll = LinkedList[int]()
        assert ll.delete(1) is False

    def test_delete_first_occurrence_only(self):
        """只删除第一个匹配的节点。"""
        ll = LinkedList[int]()
        ll.append(1)
        ll.append(2)
        ll.append(2)                          # 重复值
        ll.append(3)
        ll.delete(2)
        assert list(ll) == [1, 2, 3]          # 只删了第一个 2

    # ── find ────────────────────────────────────

    def test_find_existing(self):
        ll = LinkedList[int]()
        ll.append(1)
        ll.append(2)
        node = ll.find(2)
        assert node is not None
        assert node.value == 2

    def test_find_non_existent(self):
        ll = LinkedList[int]()
        ll.append(1)
        assert ll.find(99) is None

    def test_find_empty_list(self):
        ll = LinkedList[int]()
        assert ll.find(1) is None

    # ── __getitem__ ─────────────────────────────

    def test_getitem(self):
        ll = LinkedList[int]()
        ll.append(1)
        ll.append(2)
        ll.append(3)
        assert ll[0] == 1
        assert ll[1] == 2
        assert ll[2] == 3

    def test_getitem_out_of_bounds(self):
        ll = LinkedList[int]()
        ll.append(1)
        with pytest.raises(IndexError):
            _ = ll[1]
        with pytest.raises(IndexError):
            _ = ll[-1]                       # 不支持负数索引

    # ── __len__ / __iter__ ──────────────────────

    def test_len_empty(self):
        assert len(LinkedList()) == 0

    def test_len_after_operations(self):
        ll = LinkedList[int]()
        ll.append(1)
        ll.prepend(0)
        assert len(ll) == 2
        ll.delete(1)
        assert len(ll) == 1

    def test_iter(self):
        ll = LinkedList[int]()
        ll.append(1)
        ll.append(2)
        ll.append(3)
        assert list(ll) == [1, 2, 3]

    def test_iter_empty(self):
        assert list(LinkedList()) == []

    # ── __repr__ ────────────────────────────────

    def test_repr_empty(self):
        assert repr(LinkedList()) == "LinkedList([])"

    def test_repr_non_empty(self):
        ll = LinkedList[int]()
        ll.append(1)
        ll.append(2)
        assert "1" in repr(ll) and "2" in repr(ll)

    # ── tail 一致性 ─────────────────────────────

    def test_tail_consistency_after_append(self):
        ll = LinkedList[int]()
        for i in range(5):
            ll.append(i)
        assert ll.tail.value == 4

    def test_tail_consistency_after_prepend(self):
        ll = LinkedList[int]()
        ll.append(1)                          # tail=1
        ll.prepend(0)                         # head 变了 tail 不变
        assert ll.tail.value == 1

    def test_head_and_tail_same_for_single_element(self):
        ll = LinkedList[int]()
        ll.append(42)
        assert ll.head is ll.tail
        ll.delete(42)
        ll.prepend(42)
        assert ll.head is ll.tail