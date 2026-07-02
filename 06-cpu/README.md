# 06 — The CPU

This is the summit of the hardware climb. We have an ALU that computes
(module 04) and memory that remembers (module 05), both built from gates
(module 02) built from transistors. A **CPU** is what you get when you connect
them with a **program counter** and a **control unit** that repeats one cycle
forever:

> **fetch → decode → execute → advance**, billions of times a second.

That loop is the whole idea of a stored-program computer. This module builds a
small but genuinely complete one and runs a real program on it.

## The concept in plain language

The control unit keeps a **program counter (PC)** — the address of the next
instruction. Each cycle it:

1. **Fetch** — reads the instruction byte at the PC from RAM.
2. **Decode** — splits it into an **opcode** (what to do) and an **operand**
   (what to do it to).
3. **Execute** — runs it: compute in the ALU, move data to/from RAM, or change
   the PC to jump.
4. **Advance** — moves the PC to the next instruction (unless a jump already
   changed it), and repeats.

Because instructions live in the same memory as data (a **stored-program**, or
von Neumann, machine), changing the numbers in memory changes the program the
CPU runs. That's the leap from "a fixed circuit" to "a programmable computer."

## The instruction set

Ours is a compact **accumulator** machine: one working register `A` that
everything flows through. Each instruction is a single byte — high nibble
opcode, low nibble operand (a 4-bit address or immediate):

| Instr | Meaning |
|-------|---------|
| `LOADI n` | `A = n` (immediate) |
| `LOAD addr` | `A = memory[addr]` |
| `STORE addr` | `memory[addr] = A` |
| `ADD addr` | `A = A + memory[addr]` — sets the **zero flag** |
| `SUB addr` | `A = A - memory[addr]` — sets the **zero flag** |
| `JMP addr` | jump: `PC = addr` |
| `JZ addr` | jump if the zero flag is set |
| `OUT` | emit `A` to the output log |
| `HALT` | stop |

Only `ADD`/`SUB` update the zero flag — which is exactly what lets a program
**loop until a counter reaches zero**.

## Why it matters

Everything you've ever run — an operating system, a browser, this repo's own
Python — is ultimately a stream of instructions like these being fetched,
decoded, and executed by a control unit. The machine here is tiny, but the cycle
is the *real* cycle. Grasp it and you understand what a processor fundamentally
*is*: a program counter, a place to compute, a place to remember, and a loop.

## How the code demonstrates it

**[`cpu.py`](cpu.py)** wires the real components together: the accumulator and
program counter are `Register`s from module 05, memory is the gate-built `RAM`
from module 05, arithmetic goes through the `alu` from module 04, and even the
PC increment uses the ripple-carry adder from module 03. The control unit —
`step()` — is plain Python, which is the honest picture: a control unit is a
finite state machine that *steers* the datapath, and `step()` is that state
machine.

**[`demo.py`](demo.py)** hand-assembles a program that sums 1..5 in a loop and
prints a full execution trace — every cycle's PC, instruction, accumulator, zero
flag, and the counter/sum in memory — so you can watch the loop run and halt with
`15` in memory.

## Run it

```bash
# from the repo root

# assemble and trace the sum-1..5 program cycle by cycle
python 06-cpu/demo.py

# run the tests (individual instructions + whole programs)
pytest 06-cpu/
```

## Files

- `cpu.py` — opcodes, the `encode()` assembler helper, and the `CPU` class with
  the fetch/decode/execute `step()` and a `run()` loop (with a runaway guard).
- `demo.py` — the sum-1..5 program and a cycle-by-cycle trace.
- `test_cpu.py` — each instruction, control flow (`JMP`/`JZ` taken and not),
  and whole programs (looped sum, looped countdown).

## What's next

**Module 07 — instructions & assembly**: we've been hand-encoding bytes like
`0x4E`. Next we build a proper **assembler** — a program that turns readable
assembly (`ADD I`, labels, comments) into machine code for *this* CPU — and a
richer set of example programs. That's the boundary between hardware and
software.
