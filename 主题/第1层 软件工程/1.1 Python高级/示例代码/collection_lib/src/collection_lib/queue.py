from collections.abc import Iterator
from collections import deque


class Queue[T]:
    def __init__(self):
        self._items: deque[T] = deque()

    def enqueue(self, item: T) -> None:
        self._items.append(item)

    def dequeue(self) -> T:
        if not self._items:
            raise IndexError("dequeue from empty queue")
        return self._items.popleft()

    def peek(self) -> T:
        if not self._items:
            raise IndexError("peek from empty queue")
        return self._items[0]

    def is_empty(self) -> bool:
        return len(self._items) == 0

    def __len__(self) -> int:
        return len(self._items)

    def __repr__(self) -> str:
        return f"Queue([{', '.join(repr(item) for item in self)}])"

    def __iter__(self) -> Iterator[T]:
        """从队首到队尾遍历。"""
        return iter(self._items)