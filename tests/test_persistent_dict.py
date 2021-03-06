import pytest

from optimizer.utils.persistent_dict import PersistentDict


class HashKey(object):
    def __init__(self, hash, value):
        super(HashKey, self).__init__()
        self.hash = hash
        self.value = value

    def __hash__(self):
        return self.hash

    def __eq__(self, other):
        return self.value == other

    def __ne__(self, other):
        return self.value != other


class TestPersistentDict(object):
    def test_init(self):
        assert PersistentDict() is not None

    def test_setitem(self):
        pd = PersistentDict()
        pd = pd.setitem("abc", 3)

    def test_setitem_same_key(self):
        pd = PersistentDict().setitem("abc", 3).setitem("abc", 10)
        assert pd.getitem("abc") == 10

    def test_setitem_hash_collision(self):
        pd = PersistentDict().setitem(HashKey(0, "a"), 10).setitem(HashKey(0, "b"), 20).setitem(HashKey(0, "c"), 30).setitem(HashKey(0, "a"), 10)
        assert pd.getitem(HashKey(0, "a")) == 10
        assert pd.getitem(HashKey(0, "b")) == 20
        assert pd.getitem(HashKey(0, "c")) == 30
        with pytest.raises(KeyError):
            pd.getitem(HashKey(0, "d"))

    def test_setitem_many(self):
        pd = PersistentDict()
        for i in xrange(25):
            pd = pd.setitem(i, i)
        for i in xrange(25):
            assert i in pd

    def test_setitem_many_collision(self):
        pd = PersistentDict()
        for i in xrange(25):
            pd = pd.setitem(HashKey(0, i), i)
        for i in xrange(25):
            assert HashKey(0, i) in pd
        for i in xrange(25):
            pd = pd.delitem(HashKey(0, i))
        assert len(pd) == 0

    def test_setitem_hash_window_collision(self):
        pd = PersistentDict().setitem(HashKey(0x17, "a"), 1).setitem(HashKey(0x37, "b"), 2)
        assert len(pd) == 2
        assert HashKey(0x17, "a") in pd
        assert HashKey(0x37, "b") in pd
        assert HashKey(0x17, "c") not in pd
        assert HashKey(0x37, "c") not in pd

    def test_setitem_same_value(self):
        pd = PersistentDict().setitem("abc", 3).setitem("abc", 3)
        assert pd.getitem("abc") == 3

    def test_getitem_missing(self):
        pd = PersistentDict()
        with pytest.raises(KeyError):
            pd.getitem("abc")
        pd = pd.setitem("abc", 10)
        with pytest.raises(KeyError):
            pd.getitem("def")

    def test_getitem(self):
        pd = PersistentDict()
        pd = pd.setitem("abc", 3)
        assert pd.getitem("abc") == 3

    def test_none_key(self):
        pd = PersistentDict()
        with pytest.raises(KeyError):
            pd.getitem(None)
        pd = pd.setitem(None, 3)
        assert pd.getitem(None) == 3
        pd = pd.setitem(None, 3)
        assert pd.getitem(None) == 3
        pd = pd.delitem(None)
        with pytest.raises(KeyError):
            pd.delitem(None)

    def test_bool(self):
        assert not PersistentDict()
        assert PersistentDict().setitem("a", 1)

    def test_get(self):
        pd = PersistentDict().setitem("a", 1)
        assert pd.get("a") == 1
        assert pd.get("b") is None
        assert pd.get("c", 3) == 3

    def test_contains(self):
        pd = PersistentDict().setitem("a", 3)
        assert "a" in pd
        assert "b" not in pd

    def test_iter(self):
        pd = PersistentDict()
        itr = iter(pd)
        with pytest.raises(StopIteration):
            itr.next()
        pd = pd.setitem("a", 3)
        itr = iter(pd)
        assert itr.next() == "a"

    def test_iteritems(self):
        pd = PersistentDict().setitem("a", 3).setitem("b", 4)
        assert list(pd.iteritems()) == [("a", 3), ("b", 4)]

        pd = PersistentDict().setitem(HashKey(0, "a"), 3).setitem(HashKey(0, "b"), 4)
        assert list(pd.iteritems()) == [(HashKey(0, "a"), 3), (HashKey(0, "b"), 4)]

    def test_keys(self):
        pd = PersistentDict()
        assert pd.keys() == []
        assert pd.setitem("a", 3).keys() == ["a"]

    def test_values(self):
        pd = PersistentDict()
        assert pd.values() == []
        assert pd.setitem("a", 3).values() == [3]

    def test_items(self):
        pd = PersistentDict()
        assert pd.items() == []
        assert pd.setitem("a", 3).items() == [("a", 3)]

    def test_iterkeys(self):
        pd = PersistentDict()
        assert list(pd.iterkeys()) == []
        assert list(pd.setitem("a", 3).iterkeys()) == ["a"]

    def test_itervalues(self):
        pd = PersistentDict()
        assert list(pd.itervalues()) == []
        assert list(pd.setitem("a", 3).itervalues()) == [3]

    def test_delitem(self):
        pd = PersistentDict()
        with pytest.raises(KeyError):
            pd.delitem("abc")
        pd = pd.setitem("abc", 3)
        pd = pd.delitem("abc")
        assert "abc" not in pd

        pd = PersistentDict().setitem(HashKey(0, "a"), 3).setitem(HashKey(0, "b"), 4)
        pd = pd.delitem(HashKey(0, "a")).delitem(HashKey(0, "b"))
        assert HashKey(0, "a") not in pd
        assert HashKey(0, "b") not in pd

        pd = PersistentDict().setitem("a", 1).setitem("b", 3).delitem("a")
        assert "a" not in pd
        assert "b" in pd

    def test_delitem_hash_window_collision(self):
        pd = PersistentDict().setitem(HashKey(0x17, "a"), 2)
        with pytest.raises(KeyError):
            pd.delitem(HashKey(0x37, "b"))

    def test_delitem_many(self):
        pd = PersistentDict()
        for i in xrange(25):
            pd = pd.setitem(i, i)
        with pytest.raises(KeyError):
            pd.delitem(26)
        for i in xrange(25):
            pd = pd.delitem(i)
        for i in xrange(25):
            assert i not in pd
