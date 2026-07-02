"""
Runnable demonstration of the CPU.

Run from the repo root:

    python 06-cpu/demo.py

We hand-assemble a small program that sums the integers 1..5 in a loop, run it
on the CPU one fetch/decode/execute cycle at a time, and watch the accumulator
and memory change until it halts with the answer (15) in memory.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cpu import (  # noqa: E402
    CPU, encode, OPCODE_NAMES,
    HALT, LOADI, LOAD, STORE, ADD, JZ, JMP, OUT,
)

# Memory layout:
#   addresses 0..12  program
#   address 13       constant -1  (0xFF in 8-bit two's complement)
#   address 14       counter I    (starts at 5)
#   address 15       accumulator SUM (starts at 0)
NEG1, I, SUM = 13, 14, 15

# Sum 1..5:  SUM = 0; I = 5;  loop: SUM += I; I += (-1); if I==0 stop.
PROGRAM = [
    encode(LOADI, 5),    # 0  A = 5
    encode(STORE, I),    # 1  I = 5
    encode(LOADI, 0),    # 2  A = 0
    encode(STORE, SUM),  # 3  SUM = 0
    # loop starts at address 4:
    encode(LOAD, SUM),   # 4  A = SUM
    encode(ADD, I),      # 5  A = SUM + I
    encode(STORE, SUM),  # 6  SUM = A
    encode(LOAD, I),     # 7  A = I
    encode(ADD, NEG1),   # 8  A = I - 1   (adds 0xFF; sets zero flag at 0)
    encode(STORE, I),    # 9  I = A
    encode(JZ, 12),      # 10 if I == 0, jump to HALT
    encode(JMP, 4),      # 11 else loop
    encode(HALT),        # 12 stop
    0xFF,                # 13 constant -1
    0x00,                # 14 I  (set by the program)
    0x00,                # 15 SUM (set by the program)
]


def disassemble(word: int) -> str:
    op = OPCODE_NAMES.get(word >> 4, "?")
    return f"{op} {word & 0xF}"


def main() -> None:
    print("=" * 60)
    print("PROGRAM  (sum 1..5)")
    print("=" * 60)
    for addr, word in enumerate(PROGRAM):
        tag = "  <- data" if addr >= NEG1 else ""
        print(f"  [{addr:2}] {word:#04x}  {disassemble(word):12}{tag}")

    cpu = CPU(PROGRAM)

    print("\n" + "=" * 60)
    print("EXECUTION TRACE  (one line per instruction)")
    print("=" * 60)
    print("  cyc  PC  instr        ->  ACC   Z   I  SUM")
    print("  ---------------------------------------------")
    while not cpu.halted:
        pc = cpu._pc_value()
        word = cpu.memory_dump()[pc]
        cpu.step()
        mem = cpu.memory_dump()
        print(f"  {cpu.cycles:3}  {pc:2}  {disassemble(word):12} ->  "
              f"{cpu._acc_value():3}   {cpu.zero_flag}  {mem[I]:2}  {mem[SUM]:3}")

    print("\n" + "=" * 60)
    print(f"HALTED after {cpu.cycles} cycles. "
          f"SUM (memory[{SUM}]) = {cpu.memory_dump()[SUM]}")
    print("=" * 60)
    assert cpu.memory_dump()[SUM] == 15
    print("  Correct: 1+2+3+4+5 = 15")


if __name__ == "__main__":
    main()
