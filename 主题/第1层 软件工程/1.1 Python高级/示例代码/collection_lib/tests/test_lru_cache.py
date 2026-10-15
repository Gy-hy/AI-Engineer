import pytest
from collection_lib import LRUCache


class TestLRUCache:
    """LRUCache（最近最少使用缓存）单元测试。"""

    # ── 构造 ────────────────────────────────────

    def test_capacity_positive(self):
        c = LRUCache[str, int](capacity=3)
        assert len(c) == 0

    def test_capacity_zero_raises(self):
        with pytest.raises(ValueError, match="capacity must be positive"):
            LRUCache[str, int](capacity=0)

    def test_capacity_negative_raises(self):
        with pytest.raises(ValueError, match="capacity must be positive"):
            LRUCache[str, int](capacity=-1)

    # ── put / get ───────────────────────────────

    def test_put_and_get_single(self):
        c = LRUCache[str, int](capacity=3)
        c.put("a", 1)
        assert c.get("a") == 1

    def test_get_non_existent_raises(self):
        c = LRUCache[str, int](capacity=3)
        with pytest.raises(KeyError):
            c.get("nonexistent")

    def test_put_update_existing_key(self):
        """put 已存在的 key 只更新值，不增加元素数。"""
        c = LRUCache[str, str](capacity=3)
        c.put("k", "v1")
        c.put("k", "v2")
        assert c.get("k") == "v2"
        assert len(c) == 1

    # ── 容量与淘汰 ──────────────────────────────

    def test_evicts_lru_when_full(self):
        """缓存满时淘汰最久未使用的 key。"""
        c = LRUCache[str, int](capacity=2)
        c.put("a", 1)                         # [a]
        c.put("b", 2)                         # [b, a]  (b 最近使用)
        c.put("c", 3)                         # 满，淘汰 a   → [c, b]
        with pytest.raises(KeyError):
            c.get("a")
        assert c.get("b") == 2
        assert c.get("c") == 3

    def test_get_updates_usage_order(self):
        """get 会将被访问的 key 标记为最近使用——阻止淘汰。"""
        c = LRUCache[str, int](capacity=2)
        c.put("a", 1)
        c.put("b", 2)                         # [b, a]
        c.get("a")                            # [a, b]——a 变成最近使用
        c.put("c", 3)                         # 满，淘汰 b（a 被 get 拯救了）
        with pytest.raises(KeyError):
            c.get("b")
        assert c.get("a") == 1
        assert c.get("c") == 3

    def test_put_on_existing_updates_usage_order(self):
        """put 已存在的 key 也更新使用顺序。"""
        c = LRUCache[str, int](capacity=2)
        c.put("a", 1)
        c.put("b", 2)                         # [b, a]
        c.put("a", 10)                        # 更新 a → [a, b]
        c.put("c", 3)                         # 满，淘汰 b
        assert c.get("a") == 10
        with pytest.raises(KeyError):
            c.get("b")
        assert c.get("c") == 3

    # ── capacity=1 边界 ─────────────────────────

    def test_capacity_one(self):
        c = LRUCache[str, int](capacity=1)
        c.put("a", 1)
        assert c.get("a") == 1
        c.put("b", 2)                         # 淘汰 a
        with pytest.raises(KeyError):
            c.get("a")
        assert c.get("b") == 2
        assert len(c) == 1

    def test_capacity_one_update_same_key(self):
        c = LRUCache[str, int](capacity=1)
        c.put("a", 1)
        c.put("a", 2)                         # 更新——不应淘汰自己
        assert c.get("a") == 2
        assert len(c) == 1

    # ── __contains__ ────────────────────────────

    def test_contains_existing(self):
        c = LRUCache[str, int](capacity=3)
        c.put("a", 1)
        assert "a" in c

    def test_contains_non_existent(self):
        c = LRUCache[str, int](capacity=3)
        assert "x" not in c

    def test_contains_does_not_change_order(self):
        """__contains__ 查询存在性不应该更新使用顺序。"""
        c = LRUCache[str, int](capacity=2)
        c.put("a", 1)
        c.put("b", 2)                         # [b, a]
        assert "a" in c                       # 查询——不算使用
        # a 仍然是最久未使用
        c.put("c", 3)                         # 淘汰 a（如果 contains 更新了顺序，就会淘汰 b）
        with pytest.raises(KeyError):
            c.get("a")
        assert c.get("b") == 2
        assert c.get("c") == 3

    # ── __len__ ────────────────────────────────

    def test_len(self):
        c = LRUCache[str, int](capacity=10)
        assert len(c) == 0
        c.put("a", 1)
        c.put("b", 2)
        assert len(c) == 2
        c.get("a")                            # 不影响长度
        assert len(c) == 2

    # ── 复杂访问序列 ────────────────────────────

    def test_complex_access_pattern(self):
        """LRU 算法综合验证。"""
        c = LRUCache[str, int](capacity=3)
        c.put("a", 1)                         # [a]
        c.put("b", 2)                         # [b, a]
        c.put("c", 3)                         # [c, b, a]
        c.get("a")                            # [a, c, b]——a 最近使用
        c.get("b")                            # [b, a, c]
        c.put("d", 4)                         # 满，淘汰 c（最久未使用）
        assert set(c._cache.keys()) == {"a", "b", "d"}
        with pytest.raises(KeyError):
            c.get("c")
        c.get("a")                            # [a, b, d]
        c.put("e", 5)                         # 满，淘汰 b
        assert c.get("a") == 1
        assert c.get("d") == 4
        assert c.get("e") == 5
        with pytest.raises(KeyError):
            c.get("b")

    # ── __repr__ ───────────────────────────────

    def test_repr_empty(self):
        c = LRUCache[str, int](capacity=3)
        r = repr(c)
        assert "capacity=3" in r

    def test_repr_non_empty(self):
        c = LRUCache[str, int](capacity=2)
        c.put("name", 42)
        r = repr(c)
        assert "name" in r
        assert "42" in r