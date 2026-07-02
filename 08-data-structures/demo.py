"""
Runnable demonstration of the from-scratch data structures.

Run from the repo root:

    python 08-data-structures/demo.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dynamic_array import DynamicArray  # noqa: E402
from linked_list import LinkedList  # noqa: E402
from stack_queue import Stack, Queue  # noqa: E402
from hash_map import HashMap, hash_key  # noqa: E402
from bst import BST  # noqa: E402


def demo_dynamic_array() -> None:
    print("=" * 58)
    print("DYNAMIC ARRAY  (grows by doubling; watch the capacity)")
    print("=" * 58)
    arr = DynamicArray(capacity=2)
    for x in range(1, 6):
        arr.append(x * 10)
        print(f"  append {x*10:2} -> {arr}  (size={len(arr)}, cap={arr.capacity})")
    arr.insert(0, 5)
    print(f"  insert 5 at front -> {arr}")
    arr.delete(2)
    print(f"  delete index 2   -> {arr}")
    print(f"  arr[1] = {arr[1]}, arr[-1] = {arr[-1]}")


def demo_linked_list() -> None:
    print("\n" + "=" * 58)
    print("LINKED LIST  (O(1) front ops; in-place reverse)")
    print("=" * 58)
    ll = LinkedList()
    for x in [3, 2, 1]:
        ll.push_front(x)
    ll.push_back(4)
    print(f"  built            -> {ll}")
    ll.delete(2)
    print(f"  delete value 2   -> {ll}")
    ll.reverse()
    print(f"  reverse          -> {ll}")
    print(f"  find 4? {ll.find(4)}   find 9? {ll.find(9)}")


def demo_stack_queue() -> None:
    print("\n" + "=" * 58)
    print("STACK (LIFO)  and  QUEUE (FIFO)")
    print("=" * 58)
    st = Stack()
    for x in [1, 2, 3]:
        st.push(x)
    print(f"  stack after push 1,2,3 -> {st}")
    print(f"  pop -> {st.pop()}, pop -> {st.pop()}   (last in, first out)")

    q = Queue()
    for x in [1, 2, 3]:
        q.enqueue(x)
    print(f"  queue after enqueue 1,2,3 -> {q}")
    print(f"  dequeue -> {q.dequeue()}, dequeue -> {q.dequeue()}   (first in, first out)")


def demo_hash_map() -> None:
    print("\n" + "=" * 58)
    print("HASH MAP  (custom hash + separate chaining)")
    print("=" * 58)
    print(f"  hash_key('cat')  = {hash_key('cat')}")
    print(f"  hash_key('dog')  = {hash_key('dog')}")
    hm = HashMap(num_buckets=4)
    for word in "the quick brown fox the lazy the".split():
        hm[word] = hm.get(word, 0) + 1     # word-frequency count
    print(f"  word counts -> {dict(hm.items())}")
    print(f"  hm['the'] = {hm['the']}, 'fox' in hm = {'fox' in hm}")
    hm.remove("the")
    print(f"  after remove('the') -> 'the' in hm = {'the' in hm}")


def demo_bst() -> None:
    print("\n" + "=" * 58)
    print("BINARY SEARCH TREE  (in-order traversal = sorted)")
    print("=" * 58)
    tree = BST()
    for k in [5, 3, 8, 1, 4, 7, 9, 2]:
        tree.insert(k)
    print(f"  inserted 5,3,8,1,4,7,9,2")
    print(f"  in-order (sorted) -> {tree.in_order()}")
    print(f"  min={tree.min_key()}, max={tree.max_key()}, height={tree.height()}")
    print(f"  search 7? {7 in tree}   search 6? {6 in tree}")
    tree.delete(5)  # delete the root (two-children case)
    print(f"  after delete(5)   -> {tree.in_order()}")


if __name__ == "__main__":
    demo_dynamic_array()
    demo_linked_list()
    demo_stack_queue()
    demo_hash_map()
    demo_bst()
