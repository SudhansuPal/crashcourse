"""
The singly linked list — data connected by pointers instead of by position.

A dynamic array stores elements in one contiguous block, so indexing is instant
but inserting at the front means shifting everything. A **linked list** takes the
opposite trade: each element ("node") holds its value and a reference to the next
node. Nodes can live anywhere in memory, strung together like a paper chain.

The payoff: adding or removing at the front is O(1) — just repoint a reference.
The cost: there's no "jump to index i"; to reach the i-th node you must walk the
chain from the head, so indexing is O(n). This trade-off — contiguous vs. linked
— is one of the most fundamental in all of computing.
"""

from typing import Any, Iterator, Optional


class Node:
    """One link in the chain: a value plus a pointer to the next node."""

    __slots__ = ("value", "next")

    def __init__(self, value: Any, nxt: "Optional[Node]" = None):
        self.value = value
        self.next = nxt


class LinkedList:
    """A singly linked list with O(1) front operations."""

    def __init__(self):
        self._head: Optional[Node] = None
        self._size = 0

    def __len__(self) -> int:
        return self._size

    def is_empty(self) -> bool:
        return self._head is None

    def push_front(self, value: Any) -> None:
        """Add to the front — the linked list's signature O(1) move."""
        self._head = Node(value, self._head)
        self._size += 1

    def pop_front(self) -> Any:
        """Remove and return the front value. O(1)."""
        if self._head is None:
            raise IndexError("pop from empty list")
        node = self._head
        self._head = node.next
        self._size -= 1
        return node.value

    def push_back(self, value: Any) -> None:
        """Add to the end. O(n) because we must walk to the tail."""
        new = Node(value)
        if self._head is None:
            self._head = new
        else:
            cur = self._head
            while cur.next is not None:
                cur = cur.next
            cur.next = new
        self._size += 1

    def find(self, value: Any) -> bool:
        """Is `value` present? A linear walk of the chain. O(n)."""
        cur = self._head
        while cur is not None:
            if cur.value == value:
                return True
            cur = cur.next
        return False

    def delete(self, value: Any) -> bool:
        """
        Remove the first node equal to `value`. Returns True if one was removed.

        We keep a `prev` pointer so we can splice a node out by repointing its
        predecessor's `next` past it — the essence of linked-list deletion.
        """
        prev: Optional[Node] = None
        cur = self._head
        while cur is not None:
            if cur.value == value:
                if prev is None:            # removing the head
                    self._head = cur.next
                else:
                    prev.next = cur.next    # splice cur out
                self._size -= 1
                return True
            prev, cur = cur, cur.next
        return False

    def reverse(self) -> None:
        """
        Reverse the list in place by flipping each node's `next` pointer.

        Walk the chain carrying three pointers (prev, cur, next), turning each
        link around as we go. O(n) time, O(1) extra space.
        """
        prev: Optional[Node] = None
        cur = self._head
        while cur is not None:
            nxt = cur.next    # remember where we were going
            cur.next = prev   # flip this link backward
            prev = cur        # advance the window
            cur = nxt
        self._head = prev

    def __iter__(self) -> Iterator[Any]:
        cur = self._head
        while cur is not None:
            yield cur.value
            cur = cur.next

    def __repr__(self) -> str:
        return "LinkedList([" + " -> ".join(repr(x) for x in self) + "])"
