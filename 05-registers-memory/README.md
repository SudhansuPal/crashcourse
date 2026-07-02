# 05 — Registers & Memory

Everything so far has been **combinational**: outputs depend only on the current
inputs, so the circuit has no past. A computer, though, must *remember* — hold a
number while it works on the next one, keep a program in memory. That requires a
genuinely new ingredient: **feedback**. This module uses feedback to build a bit
of storage, stacks bits into a **register**, and arrays registers into
addressable **RAM**.

## The concept in plain language

Loop a gate's output back to its own input and something remarkable happens: the
circuit can hold a value even after the input that set it disappears. That loop
is how a **latch** stores one bit.

- **SR latch** — two cross-coupled NAND gates. One input *sets* the stored bit
  to 1, the other *resets* it to 0; otherwise it holds.
- **D latch** — a friendlier wrapper with a **D** (data) input and an **E**
  (enable) input: when `E = 1` it stores whatever is on `D`; when `E = 0` it
  ignores `D` and holds.
- **Register** — a row of D latches sharing one enable line, so it stores a
  whole *number* at once.
- **RAM** — an array of registers plus an **address decoder** that picks which
  one you mean. The decoder turns an n-bit address into `2ⁿ` "one-hot" lines
  (exactly one high), which select the word to read or write.

## Why it matters

This is the difference between a calculator and a computer. The ALU can compute,
but without storage it forgets everything instantly. Registers hold the operands
and results the CPU is working on *right now*; RAM holds the program and its
data. In module 06 the CPU's program counter, instruction register, and general
registers are all built from exactly these parts, and it fetches instructions
from a RAM just like this one.

## How the code demonstrates it

**[`latch.py`](latch.py)** builds a D latch from the NAND gates of module 02.
Our gates are pure functions, but a latch is a *loop* (Q depends on Q_bar depends
on Q). We model that honestly: the stored `(Q, Q_bar)` is kept as state, and each
update re-evaluates the gate equations until they **settle** to a stable value —
the same thing that happens in silicon in a fraction of a nanosecond.

**[`memory.py`](memory.py)** builds up from there:

- `Register` — a bank of D latches; `write(bits, enable)` captures all bits when
  enabled, holds them when not.
- `address_decoder` — from gates: line *k* is an AND of the address bits in the
  right polarity, so exactly one line goes high for each address.
- `RAM` — writing ANDs each decoder line with the global write-enable, so **only
  the addressed word captures data**; reading gates every word's bits with its
  select line and ORs them together (a decoder-driven multiplexer). The tests
  confirm writes are isolated — touching one address never disturbs another.

## Run it

```bash
# from the repo root

# latch hold/store, a register, the decoder's one-hot output, and a live RAM
python 05-registers-memory/demo.py

# run the tests
pytest 05-registers-memory/
```

## Files

- `latch.py` — the D latch (NAND SR latch with settling feedback).
- `memory.py` — `Register`, `address_decoder`, and `RAM`, all from gates.
- `demo.py` — latch hold/store timeline, register enable behavior, decoder
  truth table, and a RAM written and read back.
- `test_memory.py` — latch hold/store, register roundtrips, one-hot decoding,
  and RAM read/write isolation.

## What's next

**Module 06 — the CPU**: we finally have all the pieces — an ALU (module 04) and
memory (this module). Module 06 wires them together with a **program counter**
and a **control unit** that runs the **fetch → decode → execute** cycle, turning
stored numbers into a running program.
