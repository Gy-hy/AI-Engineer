from collections.abc import Hashable


class _Node:
    """双向链表节点。"""
    __slots__ = ("key", "value", "prev", "next")

    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.prev: "_Node | None" = None
        self.next: "_Node | None" = None


class LRUCache[K: Hashable, V]:
    """固定容量的 LRU（Least Recently Used）缓存。

    get/put 均为 O(1)：dict 负责 O(1) 按 key 查找节点，
    双向链表负责 O(1) 维护使用顺序（最近使用 → 最久未使用）。

    哨兵节点 self._head 和 self._tail 简化边界处理——
    所有真实的插入/删除都在两个哨兵之间进行，无需判断 None。
    """

    def __init__(self, capacity: int):
        if capacity <= 0:
            raise ValueError("capacity must be positive")
        self._capacity = capacity
        self._cache: dict[K, _Node] = {}

        # 哨兵节点——head ↔ tail，初始时互指
        self._head = _Node(None, None)  # type: ignore[arg-type]
        self._tail = _Node(None, None)  # type: ignore[arg-type]
        self._head.next = self._tail
        self._tail.prev = self._head

    # ── 内部链表操作（不碰 dict，纯指针操作）────────────────

    def _remove_node(self, node: _Node) -> None:
        """从双向链表中摘除 node。"""
        assert node.prev is not None
        assert node.next is not None
        node.prev.next = node.next
        node.next.prev = node.prev

    def _add_to_front(self, node: _Node) -> None:
        """把 node 插入到 head 哨兵之后——标记为"最近使用"。"""
        node.next = self._head.next
        node.prev = self._head
        assert self._head.next is not None
        self._head.next.prev = node
        self._head.next = node

    def _move_to_front(self, node: _Node) -> None:
        """把已存在的 node 移到链表头部——标记为"最近使用"。"""
        self._remove_node(node)
        self._add_to_front(node)

    def _pop_tail(self) -> _Node | None:
        """移除并返回最久未使用的节点（tail 哨兵之前的那个），链表空时返回 None。"""
        lru = self._tail.prev
        assert lru is not None
        if lru is self._head:   # 链表中没有实际节点
            return None
        self._remove_node(lru)
        return lru

    # ── 公开接口 ────────────────────────────────────────

    def get(self, key: K) -> V:
        """获取 key 对应的 value。key 不存在抛 KeyError。访问会更新使用时间。"""
        if key not in self._cache:
            raise KeyError(key)
        node = self._cache[key]
        self._move_to_front(node)       # 标记为最近使用
        return node.value

    def put(self, key: K, value: V) -> None:
        """插入或更新 key。若缓存满，淘汰最久未使用的 key。"""
        if key in self._cache:
            # 更新已有 key
            node = self._cache[key]
            node.value = value
            self._move_to_front(node)
            return

        # 新 key——如果满了先淘汰一个
        if len(self._cache) >= self._capacity:
            lru = self._pop_tail()
            if lru is not None:
                del self._cache[lru.key]

        node = _Node(key, value)
        self._cache[key] = node
        self._add_to_front(node)

    def __contains__(self, key: K) -> bool:
        """检查 key 是否在缓存中。不会更新使用顺序——查询存在性不算"使用"。"""
        return key in self._cache

    def __len__(self) -> int:
        return len(self._cache)

    def __repr__(self) -> str:
        items = []
        current = self._head.next
        assert current is not None
        while current is not self._tail:
            items.append(f"{current.key!r}: {current.value!r}")
            assert current.next is not None
            current = current.next
        return f"LRUCache(capacity={self._capacity}, {{{', '.join(items)}}})"