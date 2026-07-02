"""
Unit tests for the from-scratch data structures.

Run from the repo root:

    pytest 08-data-structures/
"""

import os
import random
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dynamic_array import DynamicArray  # noqa: E402
from linked_list import LinkedList  # noqa: E402
from stack_queue import Stack, Queue  # noqa: E402
from hash_map import HashMap, hash_key  # noqa: E402
from bst import BST  # noqa: E402


# ---- DynamicArray ---------------------------------------------------------

def test_array_append_and_index():
    arr = DynamicArray(capacity=1)
    for i in range(20):
        arr.append(i)
    assert len(arr) == 20
    assert [arr[i] for i in range(20)] == list(range(20))
    assert arr[-1] == 19


def test_array_grows_by_doubling():
    arr = DynamicArray(capacity=2)
    caps = []
    for i in range(9):
        arr.append(i)
        caps.append(arr.capacity)
    # capacity should double as it fills: 2,2,4,4,8,8,8,8,16
    assert caps == [2, 2, 4, 4, 8, 8, 8, 8, 16]


def test_array_pop_and_shrink():
    arr = DynamicArray(capacity=1)
    for i in range(16):
        arr.append(i)
    for _ in range(14):
        arr.pop()
    assert len(arr) == 2
    assert arr.capacity < 16  # should have shrunk


def test_array_insert_and_delete():
    arr = DynamicArray()
    for x in [1, 2, 3]:
        arr.append(x)
    arr.insert(1, 99)
    assert list(arr) == [1, 99, 2, 3]
    assert arr.delete(1) == 99
    assert list(arr) == [1, 2, 3]


def test_array_index_errors():
    arr = DynamicArray()
    arr.append(1)
    with pytest.raises(IndexError):
        _ = arr[5]
    with pytest.raises(IndexError):
        DynamicArray().pop()


def test_array_matches_reference_under_random_ops():
    arr = DynamicArray()
    ref = []
    random.seed(1)
    for _ in range(500):
        if not ref or random.random() < 0.6:
            v = random.randint(0, 99)
            arr.append(v)
            ref.append(v)
        else:
            assert arr.pop() == ref.pop()
    assert list(arr) == ref


# ---- LinkedList -----------------------------------------------------------

def test_linked_list_front_ops():
    ll = LinkedList()
    ll.push_front(1)
    ll.push_front(2)
    assert list(ll) == [2, 1]
    assert ll.pop_front() == 2
    assert list(ll) == [1]


def test_linked_list_push_back_and_delete():
    ll = LinkedList()
    for x in [1, 2, 3, 2]:
        ll.push_back(x)
    assert ll.delete(2) is True         # removes the first 2
    assert list(ll) == [1, 3, 2]
    assert ll.delete(99) is False


def test_linked_list_reverse():
    ll = LinkedList()
    for x in [1, 2, 3, 4]:
        ll.push_back(x)
    ll.reverse()
    assert list(ll) == [4, 3, 2, 1]


def test_linked_list_find_and_len():
    ll = LinkedList()
    for x in range(5):
        ll.push_back(x)
    assert len(ll) == 5
    assert ll.find(3) and not ll.find(9)


# ---- Stack / Queue --------------------------------------------------------

def test_stack_is_lifo():
    st = Stack()
    for x in [1, 2, 3]:
        st.push(x)
    assert st.peek() == 3
    assert [st.pop(), st.pop(), st.pop()] == [3, 2, 1]
    assert st.is_empty()
    with pytest.raises(IndexError):
        st.pop()


def test_queue_is_fifo():
    q = Queue()
    for x in [1, 2, 3]:
        q.enqueue(x)
    assert q.peek() == 1
    assert [q.dequeue(), q.dequeue(), q.dequeue()] == [1, 2, 3]
    assert q.is_empty()
    with pytest.raises(IndexError):
        q.dequeue()


def test_queue_interleaved_ops():
    q = Queue()
    q.enqueue(1)
    q.enqueue(2)
    assert q.dequeue() == 1
    q.enqueue(3)
    assert list(q) == [2, 3]
    assert q.dequeue() == 2
    assert q.dequeue() == 3
    assert q.is_empty()


# ---- HashMap --------------------------------------------------------------

def test_hash_key_deterministic():
    assert hash_key("cat") == hash_key("cat")
    assert hash_key(42) == 42
    assert hash_key(-7) == 7


def test_hash_map_put_get_update():
    hm = HashMap()
    hm["a"] = 1
    hm["b"] = 2
    assert hm["a"] == 1 and hm["b"] == 2
    hm["a"] = 10                      # update
    assert hm["a"] == 10
    assert len(hm) == 2


def test_hash_map_contains_and_remove():
    hm = HashMap()
    hm["x"] = 1
    assert "x" in hm
    hm.remove("x")
    assert "x" not in hm
    with pytest.raises(KeyError):
        hm.remove("x")
    with pytest.raises(KeyError):
        _ = hm["missing"]


def test_hash_map_resizes_and_keeps_all_entries():
    hm = HashMap(num_buckets=2)
    for i in range(100):
        hm[f"key{i}"] = i
    assert len(hm) == 100
    for i in range(100):
        assert hm[f"key{i}"] == i
    assert len(hm._buckets) > 2       # it grew


def test_hash_map_matches_dict_under_random_ops():
    hm = HashMap(num_buckets=4)
    ref = {}
    random.seed(2)
    for _ in range(1000):
        k = f"k{random.randint(0, 50)}"
        if random.random() < 0.7:
            v = random.randint(0, 999)
            hm[k] = v
            ref[k] = v
        elif k in ref:
            hm.remove(k)
            del ref[k]
    assert len(hm) == len(ref)
    assert dict(hm.items()) == ref


# ---- BST ------------------------------------------------------------------

def test_bst_in_order_is_sorted():
    tree = BST()
    keys = [5, 3, 8, 1, 4, 7, 9, 2, 6]
    for k in keys:
        tree.insert(k)
    assert tree.in_order() == sorted(keys)
    assert len(tree) == len(keys)


def test_bst_search_min_max():
    tree = BST()
    for k in [5, 3, 8, 1, 9]:
        tree.insert(k)
    assert 8 in tree and 6 not in tree
    assert tree.min_key() == 1
    assert tree.max_key() == 9


def test_bst_insert_updates_value():
    tree = BST()
    tree.insert(1, "a")
    tree.insert(1, "b")
    assert len(tree) == 1
    assert tree.search(1).value == "b"


def test_bst_delete_all_three_cases():
    tree = BST()
    for k in [5, 3, 8, 1, 4, 7, 9]:
        tree.insert(k)
    assert tree.delete(1) is True       # leaf
    assert tree.delete(8) is True       # one child (right: 7,9 -> two? 8 has 7 and 9)
    assert tree.delete(5) is True       # two children (root)
    assert tree.in_order() == [3, 4, 7, 9]
    assert tree.delete(999) is False


def test_bst_matches_sorted_set_under_random_ops():
    tree = BST()
    ref = set()
    random.seed(3)
    for _ in range(1000):
        k = random.randint(0, 100)
        if random.random() < 0.7:
            tree.insert(k)
            ref.add(k)
        else:
            expected = k in ref
            assert tree.delete(k) == expected
            ref.discard(k)
    assert tree.in_order() == sorted(ref)
