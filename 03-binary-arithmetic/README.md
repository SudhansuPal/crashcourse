# 03 — Binary Arithmetic

We can now build switches (module 02) that compute boolean operations. Time to
make them do *math*. This module represents numbers as bits — including negative
numbers via **two's complement** — and then wires the `XOR`, `AND`, and `OR`
gates from module 02 into circuits that **add and subtract**.

## The concept in plain language

**Binary** is base-2: every number is a sum of powers of two, so it can be
written with just the digits 0 and 1 — perfect for transistors that are only
ever off or on. The 4-bit pattern `0110` means `0·8 + 1·4 + 1·2 + 0·1 = 6`.

**Two's complement** is the trick that lets the same hardware handle negative
numbers. In *n* bits you interpret the top bit as *negative*, giving the range
−2ⁿ⁻¹ … 2ⁿ⁻¹−1. The encoding of a value is simply `value mod 2ⁿ`, so `-1` in
4 bits is `1111`. The payoff: **addition just works for negatives too**, so one
adder can both add and subtract.

**Adding** binary numbers is grade-school column addition in base 2:

- **Half adder** — adds two bits. Sum is `XOR` (1 when they differ); carry is
  `AND` (1 only when both are 1).
- **Full adder** — adds two bits *plus a carry-in* from the previous column.
  It's two half adders and an `OR`.
- **Ripple-carry adder** — a row of full adders, each column's carry-out feeding
  the next. The carry "ripples" left, just like carrying the 1 by hand.

## Why it matters

This is the first time the machine does something recognizably useful. Every
integer operation a CPU performs — loop counters, array indices, pointer math,
the arithmetic in the ALU we build next — rests on these adders and on two's
complement. And notice the economy: **subtraction needs no new circuit.** Since
`a − b == a + (NOT b) + 1`, we reuse the adder with the inputs inverted and a
carry-in of 1. That elegance is why two's complement won.

## How the code demonstrates it

**[`binary.py`](binary.py)** converts between integers and bit lists using plain
arithmetic — repeated `% 2` and `// 2`, not `bin()` or `int(x, 2)` or format
strings (those would be the "library that does the thing for us"). It encodes and
decodes two's complement and range-checks every value.

**[`adder.py`](adder.py)** imports the actual gates from module 02 and wires them
up: `half_adder` → `full_adder` → `ripple_carry_add`. Negation (`invert_bits`
then add 1) and `ripple_carry_subtract` show subtraction falling out of the same
adder. No Python `+` touches the numbers themselves — the arithmetic emerges
from gates operating bit by bit.

**Overflow is real:** results are computed in a fixed width, so e.g. `100 + 40`
in 8-bit signed arithmetic wraps around, exactly as it would on real hardware.
The tests deliberately stay in range, and check *every* 4-bit case exhaustively
against Python's arithmetic.

## Run it

```bash
# from the repo root

# representation, adder truth tables, a rippling addition, and subtraction
python 03-binary-arithmetic/demo.py

# run the tests
pytest 03-binary-arithmetic/
```

## Files

- `binary.py` — int ↔ bits, two's complement encode/decode, from scratch.
- `adder.py` — half/full/ripple-carry adders wired from module 02's gates, plus
  negation and subtraction.
- `demo.py` — representation, adder tables, a worked 8-bit addition, and
  subtraction via two's complement.
- `test_binary.py` — exhaustive 4-bit representation and arithmetic tests
  (checked against Python), plus adder truth tables.

## What's next

**Module 04 — the ALU**: combine the adder with the logic gates into an
**Arithmetic Logic Unit** — a single circuit that takes two numbers and an
*opcode* and computes add, subtract, AND, OR, XOR, comparisons, and more. It's
the calculating heart of the CPU we build in module 06.
