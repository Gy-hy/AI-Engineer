from collections.abc import Iterator


class _Node[T]:
    __slots__ = ("value", "next")  # 是 tuple，不是 set

    def __init__(self, value: T):
        self.value = value
        self.next: _Node[T] | None = None


class LinkedList[T]:
    def __init__(self):
        self.head: _Node[T] | None = None
        self.tail: _Node[T] | None = None
        self.length: int = 0

    # ── 内部工具 ──────────────────────────────

    def _add_first_node(self, value: T) -> None:
        """插入链表的第一个节点——head 和 tail 指向同一个节点"""
        node = _Node(value)
        self.head = node
        self.tail = node
        self.length += 1

    # ── 公开方法 ──────────────────────────────

    def append(self, value: T) -> None:
        if self.head is None:
            self._add_first_node(value)
            return

        # head 不为 None → tail 也一定不为 None（链表不空时 head/tail 同时有效）
        assert self.tail is not None
        new_node = _Node(value)
        self.tail.next = new_node
        self.tail = new_node
        self.length += 1

    def prepend(self, value: T) -> None:
        if self.head is None:
            self._add_first_node(value)
        else:
            new_node = _Node(value)
            new_node.next = self.head
            self.head = new_node
            self.length += 1

    def insert(self, index: int, value: T) -> None:
        # 允许 index == self.length，等价于 append
        if index < 0 or index > self.length:
            raise IndexError(f"index {index} out of range [0, {self.length}]")

        if index == 0:
            self.prepend(value)
        elif index == self.length:
            self.append(value)
        else:
            current = self.head
            assert current is not None  # index > 0，链表至少有一个节点
            for _ in range(index - 1):
                current = current.next
                assert current is not None
            new_node = _Node(value)
            new_node.next = current.next
            current.next = new_node
            self.length += 1

    def delete(self, value: T) -> bool:
        if self.head is None:
            return False

        # 删除的是 head
        if self.head.value == value:
            self.head = self.head.next
            self.length -= 1
            if self.length == 0:
                self.tail = None       # ← 变成空链表，tail 也要清空
            return True

        # 删除的是 head 之后的某个节点
        current = self.head
        assert current is not None  # 上面已经保证 head 不是 None
        while current.next is not None:
            if current.next.value == value:
                if current.next is self.tail:
                    self.tail = current  # ← 删除的是 tail，更新 tail
                current.next = current.next.next
                self.length -= 1
                return True
            current = current.next
        return False

    def find(self, value: T) -> _Node[T] | None:
        current = self.head
        while current is not None:
            if current.value == value:
                return current
            current = current.next
        return None

    def __getitem__(self, index: int) -> T:
        """只接受 0 <= index < len，不支持负数索引"""
        if index < 0 or index >= self.length:
            raise IndexError(f"index {index} out of range [0, {self.length})")

        current = self.head
        assert current is not None  # 上面已验证 index < self.length，链表非空
        for _ in range(index):
            current = current.next
            assert current is not None
        return current.value

    def __len__(self) -> int:
        return self.length

    def __iter__(self) -> Iterator[T]:
        """从头到尾遍历。返回 generator，自动满足 Iterator 协议。"""
        current = self.head
        while current is not None:
            yield current.value
            current = current.next

    def __repr__(self) -> str:
        if self.head is None:
            return "LinkedList([])"
        items = ", ".join(repr(item) for item in self)
        return f"LinkedList([{items}])"