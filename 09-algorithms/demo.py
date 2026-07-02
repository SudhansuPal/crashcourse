"""
Runnable demonstration of sorting, searching, and Big-O made visible.

Run from the repo root:

    python 09-algorithms/demo.py

The headline is the scaling table: we time an O(n^2) sort and an O(n log n) sort
on inputs that double in size, and print how the time grows. The O(n^2) sort's
time roughly quadruples each time n doubles; the O(n log n) sort's barely more
than doubles. That ratio *is* Big-O, measured.
"""

import os
import random
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sorting import SORTS, bubble_sort, merge_sort  # noqa: E402
from searching import linear_search, binary_search  # noqa: E402


def demo_correctness() -> None:
    print("=" * 60)
    print("SORTING  (every algorithm produces the same sorted list)")
    print("=" * 60)
    data = [5, 2, 9, 1, 5, 6, 3, 8, 3, 7]
    print(f"  input: {data}")
    for name, fn in SORTS.items():
        print(f"  {name:10} -> {fn(data)}")


def _time_sort(fn, data, trials: int = 3) -> float:
    """Best-of-N wall-clock time in milliseconds (best reduces noise)."""
    best = float("inf")
    for _ in range(trials):
        sample = list(data)
        start = time.perf_counter()
        fn(sample)
        best = min(best, time.perf_counter() - start)
    return best * 1000


def demo_scaling() -> None:
    print("\n" + "=" * 60)
    print("BIG-O, MEASURED  (time as input size doubles)")
    print("=" * 60)
    print("  bubble sort is O(n^2): time should ~4x when n doubles")
    print("  merge sort is O(n log n): time should ~2x when n doubles\n")
    print(f"  {'n':>5} | {'bubble ms':>10} {'x':>5} | {'merge ms':>10} {'x':>5}")
    print("  " + "-" * 46)

    sizes = [250, 500, 1000, 2000]
    prev_b = prev_m = None
    random.seed(0)
    for n in sizes:
        data = [random.randint(0, 10_000) for _ in range(n)]
        tb = _time_sort(bubble_sort, data)
        tm = _time_sort(merge_sort, data)
        rb = f"{tb/prev_b:.1f}" if prev_b else "  -"
        rm = f"{tm/prev_m:.1f}" if prev_m else "  -"
        print(f"  {n:>5} | {tb:>10.2f} {rb:>5} | {tm:>10.2f} {rm:>5}")
        prev_b, prev_m = tb, tm


def demo_searching() -> None:
    print("\n" + "=" * 60)
    print("SEARCHING  (linear vs binary on a sorted list of 1,000,000)")
    print("=" * 60)
    n = 1_000_000
    data = list(range(n))
    target = n - 1                     # worst case for linear: the last element
    _, lin_cmps = linear_search(data, target)
    _, bin_cmps = binary_search(data, target)
    print(f"  find {target} in {n:,} sorted items:")
    print(f"    linear search: {lin_cmps:>9,} comparisons   (O(n))")
    print(f"    binary search: {bin_cmps:>9,} comparisons   (O(log n))")
    print(f"    binary did the same job with ~{lin_cmps // bin_cmps:,}x fewer steps")


if __name__ == "__main__":
    demo_correctness()
    demo_scaling()
    demo_searching()
