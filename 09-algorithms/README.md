# 09 — Algorithms

An algorithm is a precise recipe for solving a problem. The deep question isn't
just "does it work?" but "how does its cost grow as the input grows?" — because
an algorithm that's fine on 100 items can be hopeless on 100 million. This module
implements the classic **sorting** and **searching** algorithms from scratch and
makes their growth rates something you can *watch*, not just read about.

## The concept in plain language

**Big-O notation** describes how an algorithm's work scales with input size `n`,
ignoring constant factors:

- **O(1)** — constant; doesn't depend on n
- **O(log n)** — halve the problem each step (binary search)
- **O(n)** — look at each item once (linear search)
- **O(n log n)** — the best general-purpose sorting (merge, quick)
- **O(n²)** — a nested loop over the data (bubble, insertion, selection)

The gap is dramatic. When `n` doubles, an O(n²) algorithm does **4×** the work,
while an O(n log n) one does only a bit more than **2×**. Do that a few times and
O(n²) is thousands of times slower.

**Sorting** is the classic showcase: one task, many algorithms, very different
costs.

| Algorithm | Idea | Average | Worst |
|-----------|------|---------|-------|
| Bubble | swap adjacent out-of-order pairs | O(n²) | O(n²) |
| Insertion | slide each item into a sorted prefix | O(n²) | O(n²) |
| Selection | repeatedly pick the smallest | O(n²) | O(n²) |
| Merge | split, sort halves, merge | O(n log n) | O(n log n) |
| Quick | partition around a pivot, recurse | O(n log n) | O(n²)\* |

\* Quick sort's worst case is rare with a reasonable pivot.

**Searching** shows the payoff of sorted structure: **linear search** checks
every item — O(n) — and works on any list; **binary search** halves the range
each step — O(log n) — but requires the list to be sorted.

## Why it matters

Algorithmic complexity is often the difference between instant and unusable. No
amount of faster hardware saves an O(n²) algorithm at scale — but switching to
O(n log n) does. Big-O is the shared language engineers use to reason about this
*before* writing a line of code, and sorting/searching are the examples every
programmer learns it through. This is also where the module 08 structures pay
off: binary search needs the ordered layout an array or BST provides.

## How the code demonstrates it

- **[`sorting.py`](sorting.py)** — five sorts from scratch, each commented with
  *why* it has the complexity it does. Bubble stops early on sorted input (best
  case O(n)); merge's linear-time merge over log n levels gives its guaranteed
  O(n log n); quick sort partitions around a middle pivot.
- **[`searching.py`](searching.py)** — linear and binary search, each returning
  the number of comparisons it made so the difference is measurable.
- **[`demo.py`](demo.py)** — the centerpiece is a **measured** Big-O table: it
  times bubble vs merge on inputs that double, printing the time *ratio*. You'll
  see bubble's time ~4× each doubling and merge's ~2×. Then it finds the last
  element of a million-item sorted list: linear takes 1,000,000 comparisons,
  binary takes **20**.

## Run it

```bash
# from the repo root

# correctness, the measured Big-O scaling table, and linear vs binary search
python 09-algorithms/demo.py

# run the tests
pytest 09-algorithms/
```

## Files

- `sorting.py` — bubble, insertion, selection, merge, quick.
- `searching.py` — linear and binary search (with comparison counts).
- `demo.py` — correctness, the scaling table, and the search comparison.
- `test_algorithms.py` — every sort vs Python's `sorted()` on random inputs and
  edge cases; search hits/misses; a check that binary search stays within
  `log2(n)+1` comparisons.

## What's next

**Module 10 — file systems**: we return to systems software and build a tiny
**file system** on a simulated block device — inodes, directories, and a
free-space map — showing how named files and folders are really just data
structures laid over a flat array of fixed-size blocks.
