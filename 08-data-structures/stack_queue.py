"""
Stack and Queue — two disciplines for adding and removing elements.

These aren't new storage so much as new *rules* about order, built on the
structures we already have:

    Stack — Last In, First Out (LIFO). Like a stack of plates: you add and
            remove from the same end (the "top"). Powers function-call frames,
            undo, expression evaluation, backtracking.

    Queue — First In, First Out (FIFO). Like a line at a shop: you add at the
            back and remove from the front. Powers task scheduling, buffers, and
            breadth-first search (module 09).

Both are implemented so their core operations are O(1). The Stack rides on our
linked list's fast front; the Queue keeps its own head *and* tail pointers so
both ends are O(1) — a plain singly linked list only makes one end fast.
"""

from typing import Any, Optional

from linked_list import LinkedList, Node


class Stack:
    """LIFO stack. push/pop/peek are all O(1)."""

    def __init__(self):
        # Reuse the linked list: its fast front is exactly the stack "top".
        self._items = LinkedList()

    def __len__(self) -> int:
        return len(self._items)

    def is_empty(self) -> bool:
        return self._items.is_empty()

    def push(self, value: Any) -> None:
        """Put a value on top."""
        self._items.push_front(value)

    def pop(self) -> Any:
        """Remove and return the top value (the most recently pushed)."""
        if self.is_empty():
            raise IndexError("pop from empty stack")
        return self._items.pop_front()

    def peek(self) -> Any:
        """Look at the top value without removing it."""
        if self.is_empty():
            raise IndexError("peek at empty stack")
        return next(iter(self._items))

    def __repr__(self) -> str:
        return "Stack(top -> " + ", ".join(repr(x) for x in self._items) + ")"


class Queue:
    """
    FIFO queue with O(1) enqueue and dequeue.

    We hold pointers to both ends: enqueue appends at the tail, dequeue removes
    from the head. Keeping the tail pointer is the trick that makes appending
    O(1) instead of the O(n) walk a bare singly linked list would need.
    """

    def __init__(self):
        self._head: Optional[Node] = None  # front (dequeue end)
        self._tail: Optional[Node] = None  # back (enqueue end)
        self._size = 0

    def __len__(self) -> int:
        return self._size

    def is_empty(self) -> bool:
        return self._head is None

    def enqueue(self, value: Any) -> None:
        """Add to the back of the line."""
        node = Node(value)
        if self._tail is None:            # empty queue: node is both ends
            self._head = self._tail = node
        else:
            self._tail.next = node        # link old tail to new node
            self._tail = node             # new node becomes the tail
        self._size += 1

    def dequeue(self) -> Any:
        """Remove and return the value at the front of the line."""
        if self._head is None:
            raise IndexError("dequeue from empty queue")
        node = self._head
        self._head = node.next
        if self._head is None:            # queue became empty; clear the tail too
            self._tail = None
        self._size -= 1
        return node.value

    def peek(self) -> Any:
        """Look at the front value without removing it."""
        if self._head is None:
            raise IndexError("peek at empty queue")
        return self._head.value

    def __iter__(self):
        cur = self._head
        while cur is not None:
            yield cur.value
            cur = cur.next

    def __repr__(self) -> str:
        return "Queue(front -> " + ", ".join(repr(x) for x in self) + ")"
