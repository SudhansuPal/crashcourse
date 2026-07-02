"""
The hash map — near-instant lookup by key, built from scratch.

Arrays give O(1) access by *integer index*. But we usually want to look things
up by *key* — a name, a word, an id. A hash map bridges the two: a **hash
function** turns any key into an integer, which we reduce (mod the number of
buckets) into an array index. Store the key/value pair there, and later we can
jump straight back to it. Average-case lookup, insert, and delete are all O(1).

Two keys can hash to the same bucket — a **collision**. We resolve collisions by
**separate chaining**: each bucket holds a small list of pairs, and we scan that
short list. As long as the buckets stay lightly loaded, those lists stay tiny, so
operations stay effectively constant time. We keep them light by **resizing**
(rehashing into more buckets) when the load factor climbs.

We build the hash function ourselves and never touch Python's dict — that would
be the "library that does the thing for us."
"""

from typing import Any, Iterator, List, Optional, Tuple


def hash_key(key: Any) -> int:
    """
    Turn a key into a non-negative integer.

    For strings we use a classic polynomial rolling hash: treat the characters
    as digits in base 31 (a small prime that spreads values well) and evaluate
    the polynomial. For ints we use the value directly; other types fall back to
    hashing their string form. The goal is to scatter keys evenly across buckets.
    """
    if isinstance(key, int):
        return key if key >= 0 else -key
    if not isinstance(key, str):
        key = repr(key)
    h = 0
    for ch in key:
        h = h * 31 + ord(ch)   # Horner's method: ((c0)*31 + c1)*31 + c2 ...
    return h


class HashMap:
    """A dict-like map using separate chaining and automatic resizing."""

    def __init__(self, num_buckets: int = 8):
        self._buckets: List[List[Tuple[Any, Any]]] = [[] for _ in range(num_buckets)]
        self._size = 0
        # Resize once the table averages this many entries per bucket.
        self._max_load_factor = 0.75

    def __len__(self) -> int:
        return self._size

    def _index_for(self, key: Any, num_buckets: Optional[int] = None) -> int:
        """Map a key to a bucket index: hash, then fold into the table size."""
        n = num_buckets if num_buckets is not None else len(self._buckets)
        return hash_key(key) % n

    def put(self, key: Any, value: Any) -> None:
        """Insert or update key -> value. Amortized O(1)."""
        bucket = self._buckets[self._index_for(key)]
        for i, (k, _) in enumerate(bucket):
            if k == key:
                bucket[i] = (key, value)     # key exists: update in place
                return
        bucket.append((key, value))          # new key: add to the chain
        self._size += 1
        if self._size / len(self._buckets) > self._max_load_factor:
            self._resize(len(self._buckets) * 2)

    def get(self, key: Any, default: Any = None) -> Any:
        """Return the value for key, or `default` if absent."""
        bucket = self._buckets[self._index_for(key)]
        for k, v in bucket:
            if k == key:
                return v
        return default

    def contains(self, key: Any) -> bool:
        bucket = self._buckets[self._index_for(key)]
        return any(k == key for k, _ in bucket)

    def remove(self, key: Any) -> None:
        """Delete a key. Raises KeyError if it isn't present."""
        bucket = self._buckets[self._index_for(key)]
        for i, (k, _) in enumerate(bucket):
            if k == key:
                bucket.pop(i)
                self._size -= 1
                return
        raise KeyError(key)

    def _resize(self, new_num_buckets: int) -> None:
        """
        Grow the table and re-file every entry.

        Because a key's bucket depends on the number of buckets, growing the
        table means recomputing every key's home — a full rehash. It's O(n), but
        it happens rarely (only on doubling), so it doesn't spoil the amortized
        O(1) of put.
        """
        new_buckets: List[List[Tuple[Any, Any]]] = [[] for _ in range(new_num_buckets)]
        for bucket in self._buckets:
            for key, value in bucket:
                new_buckets[self._index_for(key, new_num_buckets)].append((key, value))
        self._buckets = new_buckets

    def keys(self) -> Iterator[Any]:
        for bucket in self._buckets:
            for k, _ in bucket:
                yield k

    def items(self) -> Iterator[Tuple[Any, Any]]:
        for bucket in self._buckets:
            for pair in bucket:
                yield pair

    # Dict-style sugar so the map is pleasant to use.
    def __getitem__(self, key: Any) -> Any:
        if not self.contains(key):
            raise KeyError(key)
        return self.get(key)

    def __setitem__(self, key: Any, value: Any) -> None:
        self.put(key, value)

    def __contains__(self, key: Any) -> bool:
        return self.contains(key)

    def __repr__(self) -> str:
        return "HashMap({" + ", ".join(f"{k!r}: {v!r}" for k, v in self.items()) + "})"
