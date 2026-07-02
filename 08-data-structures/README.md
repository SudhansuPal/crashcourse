# 08 — Data Structures

Modules 01–07 built a computer. Now we change altitude completely and start on
the **software** side: the ways we organize data in memory so programs can work
with it efficiently. Every data structure is a different answer to the same
question — *how should we lay out data so the operations we care about are fast?*
— and each is a trade-off. This module builds the essential ones from scratch.

## The concept in plain language

| Structure | Idea | Fast at | Slow at |
|-----------|------|---------|---------|
| **Dynamic array** | one growable contiguous block | index by position, append | insert/delete in the middle |
| **Linked list** | nodes chained by pointers | insert/remove at the front | jumping to index *i* |
| **Stack** | Last-In-First-Out discipline | push/pop at one end | — |
| **Queue** | First-In-First-Out discipline | enqueue back / dequeue front | — |
| **Hash map** | key → bucket via a hash function | lookup/insert/delete by key | ordered traversal |
| **BST** | keys ordered left `<` node `<` right | search + keep data sorted | degrades if unbalanced |

The recurring theme is **trade-offs**. An array gives instant indexing but pays
to insert in the middle; a linked list flips that. A hash map gives near-instant
lookup by key but loses ordering; a search tree keeps order but is a bit slower.
There is no "best" structure — only the best fit for what your code does most.

## Why it matters

Choosing the right data structure is often the single biggest factor in whether
a program is fast or slow. These six are the workhorses behind almost everything:
dynamic arrays back most "list" types; hash maps back dictionaries, sets, and
database indexes; stacks run every function call (the *call stack*); queues drive
schedulers and the breadth-first search we'll write in module 09; trees underlie
ordered maps, filesystems, and databases. Understanding their costs is the
vocabulary of module 09's Big-O analysis.

## How the code demonstrates it

Everything is built from first principles — **no Python `dict` for the hash map,
no reliance on `list`'s growth for the concept**:

- **[`dynamic_array.py`](dynamic_array.py)** — treats a fixed `[None] * capacity`
  block as raw memory and grows by **doubling**, giving *amortized* O(1) append.
  The demo prints the capacity jumping 2 → 4 → 8 as it fills.
- **[`linked_list.py`](linked_list.py)** — a singly linked list with O(1)
  `push_front`, splice-based delete, and an in-place `reverse` that flips each
  node's pointer with a three-pointer walk.
- **[`stack_queue.py`](stack_queue.py)** — a `Stack` riding on the linked list's
  fast front, and a `Queue` that keeps **both head and tail pointers** so both
  ends are O(1).
- **[`hash_map.py`](hash_map.py)** — a hand-written polynomial hash function,
  **separate chaining** for collisions, and automatic **resize/rehash** when the
  load factor exceeds 0.75.
- **[`bst.py`](bst.py)** — a binary search tree with search, min/max, height, an
  in-order traversal that emits keys **sorted**, and deletion handling all three
  cases (leaf, one child, two children via in-order successor).

The tests include **randomized cross-checks**: the dynamic array is compared to a
Python list, the hash map to a `dict`, and the BST to a sorted `set` over
thousands of random operations, so correctness isn't just spot-checked.

## Run it

```bash
# from the repo root

# see all six structures in action
python 08-data-structures/demo.py

# run the tests (incl. randomized comparisons to Python's built-ins)
pytest 08-data-structures/
```

## Files

- `dynamic_array.py`, `linked_list.py`, `stack_queue.py`, `hash_map.py`, `bst.py`
- `demo.py` — each structure demonstrated end to end.
- `test_data_structures.py` — unit tests plus randomized reference comparisons.

## What's next

**Module 09 — algorithms**: with these structures in hand, we implement the
classic **sorting** and **searching** algorithms from scratch and measure how
their running times grow — making **Big-O notation** something you can *see* in a
timing table, not just read about.
