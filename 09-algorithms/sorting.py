"""
Sorting algorithms — the classic ways to put data in order.

Sorting is the canonical playground for studying algorithms, because the *same
task* has many solutions with wildly different efficiency. Here we implement five
from scratch and, crucially, understand *why* their running times differ. That
"why" is what Big-O notation captures.

Big-O in one paragraph: it describes how an algorithm's work grows as the input
size n grows, ignoring constant factors and small terms. O(n^2) means doubling n
roughly quadruples the work; O(n log n) means doubling n a bit more than doubles
it. For large n that gap is enormous — the difference between a program that
finishes and one that doesn't.

    algorithm        best        average      worst       extra space
    ---------        ----        -------      -----       -----------
    bubble sort      O(n)        O(n^2)       O(n^2)      O(1)
    insertion sort   O(n)        O(n^2)       O(n^2)      O(1)
    selection sort   O(n^2)      O(n^2)       O(n^2)      O(1)
    merge sort       O(n log n)  O(n log n)   O(n log n)  O(n)
    quick sort       O(n log n)  O(n log n)   O(n^2)*     O(log n)
    * worst case is rare with reasonable pivot choice
"""

from typing import List


def bubble_sort(data: List) -> List:
    """
    Repeatedly walk the list swapping adjacent out-of-order pairs, so the
    largest element "bubbles" to the end each pass. Simple but O(n^2).

    Optimization: if a full pass makes no swaps, the list is already sorted and
    we stop — which is what makes the *best* case (sorted input) O(n).
    """
    a = list(data)                      # work on a copy; don't mutate the caller's
    n = len(a)
    for i in range(n):
        swapped = False
        # After i passes, the last i elements are already in place.
        for j in range(0, n - i - 1):
            if a[j] > a[j + 1]:
                a[j], a[j + 1] = a[j + 1], a[j]
                swapped = True
        if not swapped:
            break
    return a


def insertion_sort(data: List) -> List:
    """
    Build the sorted portion one element at a time: take the next element and
    slide it left into its correct spot among the already-sorted prefix.

    This is how most people sort a hand of cards. Great on small or nearly
    sorted inputs (best case O(n)); O(n^2) in general.
    """
    a = list(data)
    for i in range(1, len(a)):
        key = a[i]
        j = i - 1
        while j >= 0 and a[j] > key:    # shift bigger elements right
            a[j + 1] = a[j]
            j -= 1
        a[j + 1] = key                  # drop key into the gap
    return a


def selection_sort(data: List) -> List:
    """
    Each pass selects the smallest element from the unsorted part and swaps it
    into place. Always O(n^2) — even on sorted input — but does the fewest
    swaps of the three quadratic sorts (one per pass).
    """
    a = list(data)
    n = len(a)
    for i in range(n):
        min_idx = i
        for j in range(i + 1, n):
            if a[j] < a[min_idx]:
                min_idx = j
        a[i], a[min_idx] = a[min_idx], a[i]
    return a


def merge_sort(data: List) -> List:
    """
    Divide and conquer: split the list in half, sort each half (recursively),
    then MERGE the two sorted halves into one. The merge is the clever bit — two
    already-sorted lists combine in a single linear pass.

    The splitting forms log n levels; each level does O(n) merging work, giving
    a guaranteed O(n log n). It needs O(n) extra space for the merges.
    """
    a = list(data)
    if len(a) <= 1:
        return a
    mid = len(a) // 2
    left = merge_sort(a[:mid])
    right = merge_sort(a[mid:])
    return _merge(left, right)


def _merge(left: List, right: List) -> List:
    """Combine two sorted lists into one sorted list. O(len(left)+len(right))."""
    merged: List = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:         # <= keeps the sort STABLE (ties keep order)
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1
    merged.extend(left[i:])             # one side is exhausted; append the rest
    merged.extend(right[j:])
    return merged


def quick_sort(data: List) -> List:
    """
    Divide and conquer a different way: pick a PIVOT, partition the list into
    "less than pivot" and "greater than pivot", and recurse on each side.

    On average O(n log n) and very fast in practice. Its worst case is O(n^2)
    (e.g. an already-sorted list with a bad pivot); we pick the middle element
    as the pivot to make that case unlikely on ordinary data.
    """
    a = list(data)
    if len(a) <= 1:
        return a
    pivot = a[len(a) // 2]
    less = [x for x in a if x < pivot]
    equal = [x for x in a if x == pivot]
    greater = [x for x in a if x > pivot]
    return quick_sort(less) + equal + quick_sort(greater)


# A registry so demos and tests can iterate over every algorithm by name.
SORTS = {
    "bubble": bubble_sort,
    "insertion": insertion_sort,
    "selection": selection_sort,
    "merge": merge_sort,
    "quick": quick_sort,
}
