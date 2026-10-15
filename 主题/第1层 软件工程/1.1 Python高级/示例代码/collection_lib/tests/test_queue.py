import pytest
from collections import deque
from collection_lib import Queue


class TestQueue:
    """Queue（队列）单元测试——FIFO 行为、空队列异常、底层使用 deque。"""

    # ── enqueue / dequeue ──────────────────────

    def test_enqueue_and_dequeue_single(self):
        q = Queue[int]()
        q.enqueue(42)
        assert q.dequeue() == 42

    def test_enqueue_and_dequeue_multiple(self):
        q = Queue[int]()
        q.enqueue(1)
        q.enqueue(2)
        q.enqueue(3)
        assert q.dequeue() == 1
        assert q.dequeue() == 2
        assert q.dequeue() == 3

    def test_fifo_order(self):
        """先进先出——先 enqueue 的最先 dequeue。"""
        q = Queue[str]()
        for item in ["a", "b", "c", "d"]:
            q.enqueue(item)
        result = [q.dequeue() for _ in range(len(q))]
        assert result == ["a", "b", "c", "d"]

    # ── dequeue / peek on empty ────────────────

    def test_dequeue_empty_raises_index_error(self):
        q = Queue[int]()
        with pytest.raises(IndexError, match="dequeue from empty queue"):
            q.dequeue()

    def test_peek_empty_raises_index_error(self):
        q = Queue[int]()
        with pytest.raises(IndexError, match="peek from empty queue"):
            q.peek()

    # ── peek ───────────────────────────────────

    def test_peek_does_not_remove(self):
        q = Queue[int]()
        q.enqueue(1)
        q.enqueue(2)
        assert q.peek() == 1
        assert q.peek() == 1  # 再次 peek 还在
        assert len(q) == 2

    # ── is_empty / __len__ ─────────────────────

    def test_is_empty_new_queue(self):
        assert Queue().is_empty()

    def test_is_empty_after_enqueue(self):
        q = Queue[int]()
        q.enqueue(1)
        assert not q.is_empty()

    def test_is_empty_after_dequeue_all(self):
        q = Queue[int]()
        q.enqueue(1)
        q.dequeue()
        assert q.is_empty()

    def test_len(self):
        q = Queue[int]()
        assert len(q) == 0
        q.enqueue(1)
        q.enqueue(2)
        assert len(q) == 2
        q.dequeue()
        assert len(q) == 1

    # ── 底层验证 ──────────────────────────────

    def test_uses_deque_not_list(self):
        """Queue 必须用 deque 而不是 list 作为底层存储。"""
        q = Queue[int]()
        assert isinstance(q._items, deque), (
            f"Queue._items 应该是 deque，实际是 {type(q._items).__name__}"
        )

    # ── __iter__ ───────────────────────────────

    def test_iter_front_to_back(self):
        """遍历应该从队首到队尾。"""
        q = Queue[int]()
        q.enqueue(1)
        q.enqueue(2)
        q.enqueue(3)
        assert list(q) == [1, 2, 3]

    def test_iter_empty(self):
        assert list(Queue()) == []

    # ── __repr__ ───────────────────────────────

    def test_repr_empty(self):
        assert repr(Queue()) == "Queue([])"

    def test_repr_non_empty(self):
        q = Queue[int]()
        q.enqueue(1)
        q.enqueue(2)
        assert repr(q) == "Queue([1, 2])"

    # ── 泛型 ───────────────────────────────────

    def test_generic_string(self):
        q = Queue[str]()
        q.enqueue("hello")
        q.enqueue("world")
        assert q.dequeue() == "hello"
        assert q.dequeue() == "world"