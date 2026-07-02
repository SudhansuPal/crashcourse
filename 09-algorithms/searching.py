"""
Searching algorithms — finding a value, slowly vs. cleverly.

Searching shows the payoff of structure in the starkest possible terms. On
unsorted data you have no choice but to check items one by one. But if the data
is *sorted*, you can halve the search space with every comparison — the
difference between O(n) and O(log n), between checking a million items and
checking twenty.

Each function returns the index of the target, or -1 if it isn't present. Both
also report how many comparisons they made, so the demo can show the gap.
"""

from typing import List, Tuple


def linear_search(data: List, target) -> Tuple[int, int]:
    """
    Check each element in turn. Works on ANY list (sorted or not). O(n).

    Returns (index, comparisons). index is -1 if not found.
    """
    comparisons = 0
    for i, value in enumerate(data):
        comparisons += 1
        if value == target:
            return i, comparisons
    return -1, comparisons


def binary_search(data: List, target) -> Tuple[int, int]:
    """
    Search a SORTED list by repeatedly halving the range.

    Look at the middle element. If it's the target, done. If the target is
    smaller, it can only be in the left half; if larger, the right half. Each
    comparison discards half of what's left, so at most about log2(n)
    comparisons are ever needed.

    Returns (index, comparisons). index is -1 if not found.
    Precondition: `data` must be sorted ascending.
    """
    lo, hi = 0, len(data) - 1
    comparisons = 0
    while lo <= hi:
        mid = (lo + hi) // 2            # middle of the current range
        comparisons += 1
        if data[mid] == target:
            return mid, comparisons
        if data[mid] < target:
            lo = mid + 1               # target is in the right half
        else:
            hi = mid - 1               # target is in the left half
    return -1, comparisons


SEARCHES = {
    "linear": linear_search,
    "binary": binary_search,
}
