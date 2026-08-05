import heapq
from itertools import count


class PriorityQueue[T]:
    """最小优先队列——每次 pop 返回优先级最小的元素。

    底层用 heapq 实现，push/pop 均为 O(log n)，peek 为 O(1)。
    内部使用 (priority, counter, item) 三元组防止 priority
    相同时去比较 item 本身（item 可能不支持 <）。
    """

    def __init__(self):
        self._heap: list[tuple[int, int, T]] = []
        self._counter = count()  # 递增计数器，保证三元组第二字段永不重复

    def push(self, item: T, priority: int) -> None:
        """压入元素，priority 越小越优先出队。"""
        heapq.heappush(self._heap, (priority, next(self._counter), item))

    def pop(self) -> T:
        """弹出并返回优先级最小的元素。"""
        if not self._heap:
            raise IndexError("pop from empty priority queue")
        return heapq.heappop(self._heap)[2]  # [2] 取出三元组中的 item

    def peek(self) -> T:
        """返回优先级最小的元素，不移除。"""
        if not self._heap:
            raise IndexError("peek from empty priority queue")
        return self._heap[0][2]  # 堆顶是最小元素

    def is_empty(self) -> bool:
        return len(self._heap) == 0

    def __len__(self) -> int:
        return len(self._heap)

    def __repr__(self) -> str:
        # 按优先级排序展示（不改变堆本身——先 copy 再逐一出队）
        items = sorted(self._heap, key=lambda x: x[0])
        pairs = [(item[2], item[0]) for item in items]  # (item, priority)
        return f"PriorityQueue({pairs})"