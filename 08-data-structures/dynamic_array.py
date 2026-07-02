"""
The dynamic array — a growable list built on a fixed block of "memory".

A computer's memory (module 05) is a fixed grid of numbered cells. A raw array
is just a contiguous run of those cells: fast to index (address = base + i) but
fixed in size. So how does a "list" that grows on demand — Python's list, Java's
ArrayList — actually work? It keeps a fixed block and, when full, allocates a
bigger block and copies everything over. That's what we build here.

To stay honest about "from scratch," we treat a fixed-capacity Python list
(`[None] * capacity`) as our raw memory block — a stand-in for a real contiguous
allocation whose size can't change. All the growable behavior on top is ours.
"""

from typing import Any, Iterator


class DynamicArray:
    """
    A growable, index-addressable sequence.

    Backed by a fixed block that we replace with a larger one when it fills up.
    Doubling the capacity on each growth makes `append` run in *amortized* O(1)
    time: most appends are a single store, and the occasional expensive copy is
    paid off across the many cheap appends that follow.
    """

    def __init__(self, capacity: int = 4):
        self._capacity = max(1, capacity)      # size of the backing block
        self._size = 0                         # how many slots are in use
        self._store = self._make_block(self._capacity)

    @staticmethod
    def _make_block(capacity: int) -> list:
        """Allocate a fixed block of raw 'memory' (our stand-in for an array)."""
        return [None] * capacity

    def __len__(self) -> int:
        return self._size

    @property
    def capacity(self) -> int:
        return self._capacity

    def _check_index(self, i: int) -> int:
        """Support negative indices and bounds-check, like a real sequence."""
        if i < 0:
            i += self._size
        if not (0 <= i < self._size):
            raise IndexError("index out of range")
        return i

    def __getitem__(self, i: int) -> Any:
        return self._store[self._check_index(i)]

    def __setitem__(self, i: int, value: Any) -> None:
        self._store[self._check_index(i)] = value

    def _resize(self, new_capacity: int) -> None:
        """Move every element into a fresh, larger (or smaller) block."""
        new_store = self._make_block(new_capacity)
        for i in range(self._size):
            new_store[i] = self._store[i]
        self._store = new_store
        self._capacity = new_capacity

    def append(self, value: Any) -> None:
        """Add to the end, growing the block (doubling) if it's full."""
        if self._size == self._capacity:
            self._resize(self._capacity * 2)
        self._store[self._size] = value
        self._size += 1

    def pop(self) -> Any:
        """Remove and return the last element; shrink if we're using little."""
        if self._size == 0:
            raise IndexError("pop from empty array")
        self._size -= 1
        value = self._store[self._size]
        self._store[self._size] = None  # let the old reference be collected
        # Shrink when only a quarter full, to keep memory proportional to size
        # without thrashing (the gap between 1/4 and full avoids oscillation).
        if 0 < self._size <= self._capacity // 4:
            self._resize(self._capacity // 2)
        return value

    def insert(self, i: int, value: Any) -> None:
        """Insert before index i, shifting later elements right. O(n)."""
        if not (0 <= i <= self._size):
            raise IndexError("index out of range")
        if self._size == self._capacity:
            self._resize(self._capacity * 2)
        for j in range(self._size, i, -1):     # shift right to open a gap
            self._store[j] = self._store[j - 1]
        self._store[i] = value
        self._size += 1

    def delete(self, i: int) -> Any:
        """Remove the element at index i, shifting later elements left. O(n)."""
        i = self._check_index(i)
        value = self._store[i]
        for j in range(i, self._size - 1):     # shift left to close the gap
            self._store[j] = self._store[j + 1]
        self._size -= 1
        self._store[self._size] = None
        return value

    def __iter__(self) -> Iterator[Any]:
        for i in range(self._size):
            yield self._store[i]

    def __repr__(self) -> str:
        return "DynamicArray([" + ", ".join(repr(x) for x in self) + "])"
