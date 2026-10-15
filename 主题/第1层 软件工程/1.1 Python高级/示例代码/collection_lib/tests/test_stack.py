import pytest
from collection_lib import Stack


class TestStack:
    """Stack（栈）单元测试——LIFO 行为、空栈异常、协议方法。"""

    # ── push / pop ──────────────────────────────

    def test_push_and_pop_single(self):
        s = Stack[int]()
        s.push(42)
        assert s.pop() == 42

    def test_push_and_pop_multiple(self):
        s = Stack[int]()
        s.push(1)
        s.push(2)
        s.push(3)
        assert s.pop() == 3
        assert s.pop() == 2
        assert s.pop() == 1

    def test_lifo_order(self):
        """后进先出——最后 push 的最先 pop。"""
        s = Stack[str]()
        for item in ["a", "b", "c", "d"]:
            s.push(item)
        result = [s.pop() for _ in range(len(s))]
        assert result == ["d", "c", "b", "a"]

    # ── pop / peek on empty ────────────────────

    def test_pop_empty_raises_index_error(self):
        s = Stack[int]()
        with pytest.raises(IndexError, match="pop from empty stack"):
            s.pop()

    def test_peek_empty_raises_index_error(self):
        s = Stack[int]()
        with pytest.raises(IndexError, match="peek from empty stack"):
            s.peek()

    # ── peek ───────────────────────────────────

    def test_peek_does_not_remove(self):
        s = Stack[int]()
        s.push(1)
        s.push(2)
        assert s.peek() == 2
        assert s.peek() == 2  # 再次 peek 还在
        assert len(s) == 2    # 长度不变

    # ── is_empty / __len__ ─────────────────────

    def test_is_empty_new_stack(self):
        assert Stack().is_empty()

    def test_is_empty_after_push(self):
        s = Stack[int]()
        s.push(1)
        assert not s.is_empty()

    def test_is_empty_after_pop_all(self):
        s = Stack[int]()
        s.push(1)
        s.pop()
        assert s.is_empty()

    def test_len(self):
        s = Stack[int]()
        assert len(s) == 0
        s.push(1)
        s.push(2)
        assert len(s) == 2
        s.pop()
        assert len(s) == 1

    # ── __iter__ ───────────────────────────────

    def test_iter_top_to_bottom(self):
        """遍历应该从栈顶到栈底。"""
        s = Stack[int]()
        s.push(1)
        s.push(2)
        s.push(3)
        assert list(s) == [3, 2, 1]  # 栈顶（3）最先出现

    def test_iter_empty(self):
        assert list(Stack()) == []

    # ── __repr__ ───────────────────────────────

    def test_repr_empty(self):
        assert repr(Stack()) == "Stack([])"

    def test_repr_non_empty(self):
        s = Stack[int]()
        s.push(1)
        s.push(2)
        assert repr(s) == "Stack([2, 1])"  # 从栈顶到栈底

    # ── 泛型 ───────────────────────────────────

    def test_generic_string(self):
        s = Stack[str]()
        s.push("hello")
        s.push("world")
        assert s.pop() == "world"
        assert s.pop() == "hello"

    def test_generic_mixed(self):
        s = Stack[int | str]()
        s.push(1)
        s.push("two")
        assert s.pop() == "two"
        assert s.pop() == 1