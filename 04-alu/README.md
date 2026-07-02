# 04 — The ALU

The **Arithmetic Logic Unit** is the calculating core of a processor. Give it
two numbers and an **opcode** (a small code that says *which* operation to do),
and it produces a result plus a handful of status **flags**. This module wires
together everything we've built so far — the gates from module 02 and the adder
from module 03 — and adds one new building block, the **multiplexer**.

## The concept in plain language

An ALU is a single circuit that can perform *many* operations; the opcode
selects which. Ours handles:

| Opcode | Operation | Meaning |
|--------|-----------|---------|
| `ADD` | `a + b` | arithmetic addition |
| `SUB` | `a - b` | arithmetic subtraction |
| `AND` | `a & b` | bitwise AND |
| `OR`  | `a \| b` | bitwise OR |
| `XOR` | `a ^ b` | bitwise XOR |
| `NOT` | `~a` | bitwise NOT (ignores `b`) |
| `SLT` | `a < b` | set-less-than: result `1` if `a < b` (signed), else `0` |

Alongside the result it reports four **flags** every CPU relies on for branches
and comparisons:

- **Z (zero)** — the result is all zeros
- **N (negative)** — the result's sign bit is set
- **C (carry)** — the adder produced a carry-out
- **V (overflow)** — *signed* overflow occurred (the result's sign is wrong)

The new part is the **multiplexer (mux)** — a circuit that selects one of
several inputs based on control bits. It's the "router" that lets one ALU offer
many operations: compute them all, then mux out the one the opcode names.

## Why it matters

The ALU is the bridge from "we can add and AND bits" to "we can execute
instructions." When the CPU in module 06 runs `ADD R1, R2` or compares two
values to decide a branch, it's handing operands and an opcode to exactly this
unit and reading back the result and flags. The mux, meanwhile, is one of the
most reused patterns in all of hardware — it's how memory addressing, register
selection, and instruction decoding all work.

## How the code demonstrates it

**[`alu.py`](alu.py)** builds the mux from gates first:

- `mux2(sel, a, b)` = `(NOT sel AND a) OR (sel AND b)` — the two ANDs are
  switches only one control line can open; the OR merges the winner.
- `mux8_bus(...)` composes 2-to-1 muxes into an **8-to-1 tree** driven by the
  three bits of the opcode.

Then the ALU follows the real-hardware pattern: **compute every candidate result
in parallel**, then use the opcode's bits to `mux8_bus` the chosen one out.
Highlights:

- **One adder does ADD *and* SUB.** A mux picks `b` or `NOT b`, and the carry-in
  is set to the subtract control bit — that's `a - b == a + (NOT b) + 1` in
  hardware, reusing module 03's adder.
- **Overflow** is detected with gates: the inputs shared a sign but the result's
  sign flipped — `XNOR(a_sign, b_sign) AND XOR(a_sign, result_sign)`.
- **SLT** reuses the subtraction: `a < b` when the difference's sign, corrected
  for overflow, is negative.

No control flow branches on the opcode to do the math — the opcode only steers
the multiplexer, exactly as gates would.

## Run it

```bash
# from the repo root

# see the mux truth table + 8-to-1 selection, then every ALU op with flags
python 04-alu/demo.py

# run the tests
pytest 04-alu/
```

## Files

- `alu.py` — the mux (`mux2`, `mux2_bus`, `mux8_bus`) and the ALU with flags.
- `demo.py` — mux demonstration and every operation run with its flags.
- `test_alu.py` — exhaustive 4-bit checks of add/sub/logic/SLT against Python,
  mux selection for all 8 indices, and flag behavior.

## What's next

**Module 05 — registers & memory**: so far everything is *combinational* — pure
functions of the current inputs with no memory. Next we introduce **feedback**
to build a latch that *remembers* a bit, compose latches into registers, and
wire registers into addressable **RAM**. Then module 06 combines the ALU with
memory into a working CPU.
