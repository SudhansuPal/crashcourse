# 02 — Logic Gates

In module 01 we treated boolean operations as abstract truth tables. Now we go
one layer *down* and build those operations out of the physical thing computers
are actually made of: the **transistor**. Then we go one layer *up* and wire
transistors into **logic gates** — the reusable parts every later module
(arithmetic, ALU, memory, CPU) is assembled from.

## The concept in plain language

A **transistor** is an electrically controlled switch with three terminals:

- **gate** — the control input; a voltage here opens or closes the switch
- **source** — where current comes in
- **drain** — where current goes out

Apply the right voltage to the gate and current flows from source to drain;
otherwise it doesn't. There are two complementary types:

- **NMOS** conducts when its gate is **HIGH** (1)
- **PMOS** conducts when its gate is **LOW** (0)

A **logic gate** is a small arrangement of transistors whose output voltage
implements a boolean operation. Modern chips use **CMOS**, which pairs the two
transistor types so that for any input, one network pulls the output up to HIGH
and a complementary network pulls it down to LOW — never both, never neither.

## Why it matters

This is the bridge from physics to logic. A transistor knows nothing about
"true" or "false" — it's just a switch. But arrange a few of them and you get a
gate that computes `AND`, and from gates you get adders, memory cells, and
eventually a CPU. A modern processor is *billions* of these switches. Crucially,
because **NAND is universal** (module 01 proved every operation can be rebuilt
from it), a manufacturer can perfect essentially one gate and compose everything
else from it.

## How the code demonstrates it

**[`transistor.py`](transistor.py)** models the switch honestly. A conducting
transistor passes its source value; an *open* one drives nothing, which we
represent as `None` (a floating wire). This matters: it's what lets us wire a
pull-up and pull-down network together and have exactly one of them drive the
output. The `wire()` helper reads the output node and will loudly reject a
**floating output** (nobody driving) or a **short circuit** (HIGH fighting LOW)
— great for catching a mis-wired gate.

**[`gates.py`](gates.py)** builds only two gates directly from transistors:

- **`NOT`** — a CMOS inverter: one PMOS (pulls HIGH when input is 0) above one
  NMOS (pulls LOW when input is 1).
- **`NAND`** — two PMOS in **parallel** (pull-up) over two NMOS in **series**
  (pull-down). Series = "both switches on"; parallel = "either switch on".

Every remaining gate is then **derived from NAND** (and `NOT`), exactly as real
designs compose standard cells:

| Gate | Built from |
|------|------------|
| `AND`  | `NOT(NAND(a, b))` |
| `OR`   | `NAND(NOT a, NOT b)` (De Morgan) |
| `NOR`  | `NOT(OR(a, b))` |
| `XOR`  | four `NAND`s |
| `XNOR` | `NOT(XOR(a, b))` |

The demo confirms each gate's output matches the canonical boolean truth table
from module 01, checked exhaustively over every input.

## Run it

```bash
# from the repo root

# see transistor switching, every gate's truth table, and the proof
python 02-logic-gates/demo.py

# run the tests
pytest 02-logic-gates/
```

## Files

- `transistor.py` — NMOS/PMOS switch model with tri-state (floating) outputs and
  the `wire()` node resolver.
- `gates.py` — `NOT` and `NAND` from transistors; `AND/OR/NOR/XOR/XNOR` derived.
- `demo.py` — prints transistor behavior, all gate truth tables, and the proof
  that gates match their boolean definitions.
- `test_gates.py` — exhaustive gate tests plus transistor and wiring tests
  (including floating-output and short-circuit detection).

## What's next

**Module 03 — binary arithmetic**: represent numbers in binary and two's
complement, then wire the `XOR` and `AND` gates from this module into a
**half adder**, a **full adder**, and a multi-bit **ripple-carry adder** that
actually adds.
