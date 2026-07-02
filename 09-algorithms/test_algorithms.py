"""
Unit tests for the sorting and searching algorithms.

Every sort is checked against Python's built-in sorted() on many random inputs,
and every edge case (empty, single, duplicates, reverse-sorted). Searches are
checked for hits, misses, and the log-scaling of binary search.

Run from the repo root:

    pytest 09-algorithms/
"""

import os
import random
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sorting import SORTS  # noqa: E402
from searching import linear_search, binary_search  # noqa: E402


SORT_NAMES = list(SORTS)


@pytest.mark.parametrize("name", SORT_NAMES)
def test_sort_empty_and_single(name):
    fn = SORTS[name]
    assert fn([]) == []
    assert fn([42]) == [42]


@pytest.mark.parametrize("name", SORT_NAMES)
def test_sort_known_cases(name):
    fn = SORTS[name]
    assert fn([3, 1, 2]) == [1, 2, 3]
    assert fn([5, 4, 3, 2, 1]) == [1, 2, 3, 4, 5]        # reverse sorted
    assert fn([1, 1, 1]) == [1, 1, 1]                    # all equal
    assert fn([2, 3, 3, 1, 2]) == [1, 2, 2, 3, 3]        # duplicates


@pytest.mark.parametrize("name", SORT_NAMES)
def test_sort_matches_python_random(name):
    fn = SORTS[name]
    random.seed(hash(name) % 10_000)
    for _ in range(50):
        data = [random.randint(-50, 50) for _ in range(random.randint(0, 60))]
        assert fn(data) == sorted(data)


@pytest.mark.parametrize("name", SORT_NAMES)
def test_sort_does_not_mutate_input(name):
    fn = SORTS[name]
    data = [3, 1, 2]
    original = list(data)
    fn(data)
    assert data == original            # caller's list untouched


def test_sort_handles_strings():
    for fn in SORTS.values():
        assert fn(["banana", "apple", "cherry"]) == ["apple", "banana", "cherry"]


# ---- searching ------------------------------------------------------------

def test_linear_search_hit_and_miss():
    data = [4, 2, 7, 1, 9]
    idx, _ = linear_search(data, 7)
    assert idx == 2
    idx, _ = linear_search(data, 100)
    assert idx == -1


def test_binary_search_hit_and_miss():
    data = list(range(0, 100, 2))      # even numbers 0..98, sorted
    idx, _ = binary_search(data, 50)
    assert data[idx] == 50
    idx, _ = binary_search(data, 51)   # odd number, not present
    assert idx == -1


def test_binary_search_matches_linear_on_sorted():
    random.seed(7)
    for _ in range(100):
        data = sorted(random.randint(0, 100) for _ in range(random.randint(1, 40)))
        target = random.randint(0, 100)
        lin_idx, _ = linear_search(data, target)
        bin_idx, _ = binary_search(data, target)
        # Both agree on presence (indices may differ when duplicates exist).
        assert (lin_idx == -1) == (bin_idx == -1)
        if bin_idx != -1:
            assert data[bin_idx] == target


def test_binary_search_is_logarithmic():
    """Binary search must never exceed ~log2(n)+1 comparisons."""
    import math
    for n in (1000, 100_000, 1_000_000):
        data = list(range(n))
        _, cmps = binary_search(data, n - 1)   # worst-ish case
        assert cmps <= math.log2(n) + 1


def test_binary_search_empty():
    idx, cmps = binary_search([], 5)
    assert idx == -1 and cmps == 0
