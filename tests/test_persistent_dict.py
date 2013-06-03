import pytest

from optimizer.utils import PersistentDict


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

    def test_setitem_matching_hash(self):
        pd = PersistentDict().setitem(HashKey(0, "a"), 10).setitem(HashKey(0, "b"), 20).setitem(HashKey(0, "c"), 30)
        assert pd.getitem(HashKey(0, "a")) == 10
        assert pd.getitem(HashKey(0, "b")) == 20
        assert pd.getitem(HashKey(0, "c")) == 30

    def test_setitem_many(self):
        pd = PersistentDict()
        for i in xrange(25):
            pd = pd.setitem(i, i)
        for i in xrange(25):
            assert i in pd

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

    def test_iteritems(self):
        pd = PersistentDict().setitem("a", 3).setitem("b", 4)
        assert list(pd.iteritems()) == [("a", 3), ("b", 4)]