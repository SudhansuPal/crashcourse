"""
The binary search tree (BST) — keeping data sorted for fast lookup.

A linked list is one-dimensional: to find something you walk past everything
before it. A **binary search tree** branches instead. Each node has a key and up
to two children, with an ironclad rule:

    every key in the LEFT subtree  < node's key < every key in the RIGHT subtree

That ordering means searching is like binary search: at each node you go left or
right, halving the remaining possibilities. In a balanced tree that's O(log n)
for search, insert, and delete. And an **in-order traversal** (left, node, right)
visits the keys in sorted order — the tree keeps your data sorted for free.

(Our tree isn't self-balancing, so adversarial insert orders can degrade it to a
list; self-balancing trees like red-black or AVL fix that. The ordering idea is
the foundation they all share.)
"""

from typing import Any, Iterator, List, Optional


class BSTNode:
    __slots__ = ("key", "value", "left", "right")

    def __init__(self, key: Any, value: Any = None):
        self.key = key
        self.value = value
        self.left: Optional[BSTNode] = None
        self.right: Optional[BSTNode] = None


class BST:
    """An ordered map keyed by comparable keys."""

    def __init__(self):
        self._root: Optional[BSTNode] = None
        self._size = 0

    def __len__(self) -> int:
        return self._size

    def insert(self, key: Any, value: Any = None) -> None:
        """Add a key (or update its value), descending left/right by the rule."""
        if self._root is None:
            self._root = BSTNode(key, value)
            self._size += 1
            return
        node = self._root
        while True:
            if key == node.key:
                node.value = value          # key already present: update
                return
            if key < node.key:
                if node.left is None:
                    node.left = BSTNode(key, value)
                    self._size += 1
                    return
                node = node.left
            else:
                if node.right is None:
                    node.right = BSTNode(key, value)
                    self._size += 1
                    return
                node = node.right

    def search(self, key: Any) -> Optional[BSTNode]:
        """Find the node with this key, or None. O(height)."""
        node = self._root
        while node is not None:
            if key == node.key:
                return node
            node = node.left if key < node.key else node.right
        return None

    def __contains__(self, key: Any) -> bool:
        return self.search(key) is not None

    def min_key(self) -> Any:
        """Smallest key = walk left as far as possible."""
        if self._root is None:
            raise ValueError("empty tree")
        node = self._root
        while node.left is not None:
            node = node.left
        return node.key

    def max_key(self) -> Any:
        """Largest key = walk right as far as possible."""
        if self._root is None:
            raise ValueError("empty tree")
        node = self._root
        while node.right is not None:
            node = node.right
        return node.key

    def height(self) -> int:
        """Longest root-to-leaf path (edges). Empty tree is -1, single node 0."""
        def _h(node: Optional[BSTNode]) -> int:
            if node is None:
                return -1
            return 1 + max(_h(node.left), _h(node.right))
        return _h(self._root)

    def delete(self, key: Any) -> bool:
        """
        Remove a key. Returns True if it was present.

        The classic three cases:
          - leaf: just detach it
          - one child: replace the node with that child
          - two children: replace the node's key/value with its in-order
            successor (the smallest key in the right subtree), then delete that
            successor (which has at most one child, reducing to an easy case).
        """
        self._root, removed = self._delete(self._root, key)
        if removed:
            self._size -= 1
        return removed

    def _delete(self, node: Optional[BSTNode], key: Any):
        if node is None:
            return None, False
        if key < node.key:
            node.left, removed = self._delete(node.left, key)
            return node, removed
        if key > node.key:
            node.right, removed = self._delete(node.right, key)
            return node, removed

        # Found it.
        if node.left is None:
            return node.right, True         # 0 or 1 (right) child
        if node.right is None:
            return node.left, True          # 1 (left) child

        # Two children: find in-order successor (min of right subtree).
        succ = node.right
        while succ.left is not None:
            succ = succ.left
        node.key, node.value = succ.key, succ.value
        node.right, _ = self._delete(node.right, succ.key)
        return node, True

    def in_order(self) -> List[Any]:
        """Keys in sorted order (left, node, right)."""
        result: List[Any] = []

        def _walk(node: Optional[BSTNode]) -> None:
            if node is None:
                return
            _walk(node.left)
            result.append(node.key)
            _walk(node.right)

        _walk(self._root)
        return result

    def __iter__(self) -> Iterator[Any]:
        return iter(self.in_order())

    def __repr__(self) -> str:
        return "BST(" + repr(self.in_order()) + ")"
