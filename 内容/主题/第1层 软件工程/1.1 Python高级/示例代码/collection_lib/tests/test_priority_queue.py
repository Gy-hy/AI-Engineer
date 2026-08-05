import pytest
from collection_lib import PriorityQueue


class TestPriorityQueue:
    """PriorityQueue（优先级队列）单元测试——最小优先、三元组防比较。"""

    # ── push / pop ──────────────────────────────

    def test_push_and_pop_single(self):
        pq = PriorityQueue[str]()
        pq.push("task", priority=1)
        assert pq.pop() == "task"

    def test_pop_by_priority(self):
        """priority 小的先出。"""
        pq = PriorityQueue[str]()
        pq.push("low", priority=10)
        pq.push("high", priority=1)
        pq.push("medium", priority=5)
        assert pq.pop() == "high"
        assert pq.pop() == "medium"
        assert pq.pop() == "low"

    def test_same_priority_fifo(self):
        """相同 priority 时，先 push 的先出（FIFO）。"""
        pq = PriorityQueue[str]()
        pq.push("first", priority=1)
        pq.push("second", priority=1)
        pq.push("third", priority=1)
        assert pq.pop() == "first"
        assert pq.pop() == "second"
        assert pq.pop() == "third"

    # ── pop / peek on empty ────────────────────

    def test_pop_empty_raises_index_error(self):
        pq = PriorityQueue[str]()
        with pytest.raises(IndexError, match="pop from empty priority queue"):
            pq.pop()

    def test_peek_empty_raises_index_error(self):
        pq = PriorityQueue[str]()
        with pytest.raises(IndexError, match="peek from empty priority queue"):
            pq.peek()

    # ── peek ───────────────────────────────────

    def test_peek_does_not_remove(self):
        pq = PriorityQueue[str]()
        pq.push("task", priority=1)
        assert pq.peek() == "task"
        assert pq.peek() == "task"            # 再次 peek 还在
        assert len(pq) == 1

    def test_peek_returns_min_priority(self):
        pq = PriorityQueue[str]()
        pq.push("low", priority=100)
        pq.push("high", priority=0)
        assert pq.peek() == "high"            # 堆顶 = 最小 priority

    # ── is_empty / __len__ ─────────────────────

    def test_is_empty_new(self):
        assert PriorityQueue().is_empty()

    def test_is_empty_after_push(self):
        pq = PriorityQueue[str]()
        pq.push("x", priority=1)
        assert not pq.is_empty()

    def test_is_empty_after_pop_all(self):
        pq = PriorityQueue[str]()
        pq.push("x", priority=1)
        pq.pop()
        assert pq.is_empty()

    def test_len(self):
        pq = PriorityQueue[str]()
        assert len(pq) == 0
        pq.push("a", 1)
        pq.push("b", 2)
        assert len(pq) == 2
        pq.pop()
        assert len(pq) == 1

    # ── 自定义对象不报 TypeError ────────────────

    def test_items_without_comparison(self):
        """没有实现 < 的自定义对象不应该在 priority 相同时引发 TypeError。

        三元组 (priority, counter, item) 中 counter 保证唯一性，
        所以永远不会尝试比较 item。
        """

        class Task:
            def __init__(self, name):
                self.name = name

            def __repr__(self):
                return f"Task({self.name})"

        pq = PriorityQueue[Task]()
        t1 = Task("A")
        t2 = Task("B")
        t3 = Task("C")

        # 三个 task 的 priority 相同——但没有 counter 就会去比较 Task
        pq.push(t1, priority=1)
        pq.push(t2, priority=1)
        pq.push(t3, priority=1)

        # 应该按 push 顺序出——FIFO，不报错
        assert pq.pop() is t1
        assert pq.pop() is t2
        assert pq.pop() is t3

    # ── __repr__ ───────────────────────────────

    def test_repr_empty(self):
        pq = PriorityQueue[str]()
        assert "PriorityQueue" in repr(pq)

    def test_repr_non_empty(self):
        pq = PriorityQueue[str]()
        pq.push("task", priority=1)
        r = repr(pq)
        assert "task" in r
        assert "1" in r