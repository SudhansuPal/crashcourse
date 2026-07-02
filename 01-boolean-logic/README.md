# 01 — Boolean Logic

**Layer zero.** Before a computer can add, remember, or run a program, it has to
represent and manipulate the simplest possible thing: a value that is either
*true* or *false*, *on* or *off*, *1* or *0*. This module builds the logic that
every later module — gates, arithmetic, the ALU, the CPU — stands on top of.

## The concept in plain language

Boolean logic (named after George Boole) is arithmetic for truth values. There
are only two values, `0` (false) and `1` (true), and a small set of operations
that combine them:

- **NOT** — flips a bit. `NOT 0 = 1`, `NOT 1 = 0`.
- **AND** — true only when *both* inputs are true.
- **OR** — true when *either* input is true.
- **XOR** ("exclusive or") — true when the inputs *differ*.
- plus **NAND, NOR, XNOR, IMPLIES**, which are combinations of the above.

The complete behavior of each operation fits in a tiny **truth table** — a list
of every possible input and its output. Because a bit has only two values,
these tables are small enough to list in full, which means we can *prove* things
about our logic by simply checking every case.

## Why it matters

Everything else in this repo is this idea, repeated and stacked:

- A **logic gate** (module 02) is one of these operations built from a physical
  switch (a transistor).
- **Binary addition** (module 03) is just XOR (the sum bit) and AND (the carry
  bit) wired together.
- **Memory** (module 05), the **ALU** (module 04), and the **CPU** (module 06)
  are all vast arrangements of these same operations.

If you understand this file, you understand the atom that the entire machine is
made of.

## How the code demonstrates it

The key move in [`booleans.py`](booleans.py) is that we **don't** define our
logic using Python's built-in `and` / `or` / `not`. Instead we:

1. Take just **two** operations as primitive — `NOT` and `AND` — defined
   directly by their truth tables (a plain lookup from inputs to output).
2. **Derive** every other operation from those two. For example:
   - `OR(a, b)  = NOT(AND(NOT a, NOT b))`  (De Morgan's law)
   - `XOR(a, b) = OR(AND(a, NOT b), AND(NOT a, b))`

This shows a foundational truth: a tiny starting point is enough to express all
of boolean logic. The demo goes one step further and rebuilds `NOT`, `AND`, and
`OR` out of **NAND alone** — proving NAND is a *universal* gate, which is why
module 02 can construct an entire computer's worth of gates from a single part.

## Run it

```bash
# from the repo root

# see every truth table and two proofs (De Morgan + NAND universality)
python 01-boolean-logic/demo.py

# run the exhaustive unit tests
pytest 01-boolean-logic/
```

## Files

- `booleans.py` — the operations, primitives first, then everything derived.
- `demo.py` — prints all truth tables and proves De Morgan's laws and NAND
  universality by exhaustive check.
- `test_booleans.py` — exhaustive truth-table tests plus algebraic-law tests.

## What's next

**Module 02 — logic gates**: we drop below the boolean and model the physical
**transistor** (a voltage-controlled switch), then wire transistors into the
very gates whose behavior we defined here.
