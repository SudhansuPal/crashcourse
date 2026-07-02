"""
A CPU — where memory and the ALU become a machine that runs programs.

We now have every part we need:
    - an ALU that computes (module 04)
    - registers and RAM that remember (module 05)
    - which are themselves built from gates (02) and transistors (02)

A CPU is what happens when you put them together and add a **control unit** that
repeats one relentless cycle:

    FETCH   : read the instruction that the Program Counter points to
    DECODE  : split it into an operation (opcode) and an operand
    EXECUTE : do it — compute in the ALU, move data to/from RAM, or jump
    then advance the Program Counter and do it all again.

That loop, running billions of times a second, is a computer. This module builds
a small but complete one and runs a real program on it.

The instruction set (a tiny accumulator machine)
------------------------------------------------
To keep the whole machine legible, ours is an *accumulator* architecture: a
single working register `A` (the accumulator) that every operation flows through.
Each instruction is one 8-bit byte: the high nibble is the opcode, the low nibble
is a 4-bit operand (a memory address or a small immediate value).

    HALT           stop
    LOADI n        A = n                (immediate)
    LOAD  addr     A = memory[addr]
    STORE addr     memory[addr] = A
    ADD   addr     A = A + memory[addr]  (updates the zero flag)
    SUB   addr     A = A - memory[addr]  (updates the zero flag)
    JMP   addr     jump: PC = addr
    JZ    addr     jump if the zero flag is set
    OUT            emit A to the output log (so we can watch it work)

Only ADD/SUB touch the zero flag, exactly like a real CPU — that's what lets a
program loop "until a counter hits zero."
"""

import os
import sys
from typing import List

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_REPO_ROOT, "03-binary-arithmetic"))
sys.path.insert(0, os.path.join(_REPO_ROOT, "04-alu"))
sys.path.insert(0, os.path.join(_REPO_ROOT, "05-registers-memory"))

from binary import int_to_bits, bits_to_int  # noqa: E402
from adder import ripple_carry_add  # noqa: E402
from alu import alu, OP_ADD, OP_SUB  # noqa: E402
from memory import RAM, Register  # noqa: E402

# ---- Opcodes (the high nibble of each instruction byte) --------------------
HALT = 0x0
LOADI = 0x1
LOAD = 0x2
STORE = 0x3
ADD = 0x4
SUB = 0x5
JMP = 0x6
JZ = 0x7
OUT = 0x8

OPCODE_NAMES = {
    HALT: "HALT", LOADI: "LOADI", LOAD: "LOAD", STORE: "STORE",
    ADD: "ADD", SUB: "SUB", JMP: "JMP", JZ: "JZ", OUT: "OUT",
}

WORD_BITS = 8   # data/instruction width
ADDR_BITS = 4   # 16 words of memory; also the operand width
MEM_WORDS = 2 ** ADDR_BITS


def encode(opcode: int, operand: int = 0) -> int:
    """Pack an opcode (high nibble) and operand (low nibble) into one byte."""
    if not (0 <= opcode <= 0xF) or not (0 <= operand <= 0xF):
        raise ValueError("opcode and operand must each fit in 4 bits")
    return (opcode << 4) | operand


class CPU:
    """
    A minimal but real CPU: RAM + accumulator + program counter + control unit.

    The datapath uses the actual ALU (module 04) and RAM/registers (module 05).
    The control unit — the fetch/decode/execute sequencing — is plain Python,
    which is the honest picture: a control unit is a finite state machine that
    steers the datapath. Here that state machine is `step()`.
    """

    def __init__(self, program: List[int]):
        if len(program) > MEM_WORDS:
            raise ValueError(f"program too big for {MEM_WORDS} words of memory")

        self.ram = RAM(MEM_WORDS, WORD_BITS)      # real gate-built memory
        self.acc = Register(WORD_BITS)            # the accumulator (real latches)
        self.pc = Register(ADDR_BITS)             # the program counter
        self.zero_flag = 0
        self.halted = False
        self.output: List[int] = []               # values printed by OUT
        self.cycles = 0

        # Load the program (and any embedded data) into memory, word by word.
        for addr, word in enumerate(program):
            self.ram.write(int_to_bits(addr, ADDR_BITS),
                           int_to_bits(word & 0xFF, WORD_BITS),
                           write_enable=1)

    # -- helpers to move between our bit-lists and plain ints ---------------
    def _pc_value(self) -> int:
        return bits_to_int(self.pc.read())

    def _set_pc(self, value: int) -> None:
        self.pc.write(int_to_bits(value % MEM_WORDS, ADDR_BITS), enable=1)

    def _increment_pc(self) -> None:
        """PC = PC + 1, using the ripple-carry adder from module 03."""
        new_pc, _ = ripple_carry_add(self.pc.read(), int_to_bits(1, ADDR_BITS))
        self.pc.write(new_pc, enable=1)

    def _acc_value(self) -> int:
        return bits_to_int(self.acc.read())

    def _mem_read(self, addr: int) -> List[int]:
        return self.ram.read(int_to_bits(addr, ADDR_BITS))

    # -- the fetch/decode/execute cycle -------------------------------------
    def step(self) -> None:
        """Execute exactly one instruction."""
        if self.halted:
            return
        self.cycles += 1

        # FETCH: read the instruction at PC.
        instruction = self._mem_read(self._pc_value())

        # DECODE: high nibble = opcode, low nibble = operand.
        opcode = bits_to_int(instruction[:4])
        operand = bits_to_int(instruction[4:])

        # By default the next instruction is the following one; jumps override.
        advance = True

        # EXECUTE.
        if opcode == HALT:
            self.halted = True
            advance = False

        elif opcode == LOADI:
            # Load the 4-bit immediate into the accumulator (zero-extended).
            self.acc.write(int_to_bits(operand, WORD_BITS), enable=1)

        elif opcode == LOAD:
            self.acc.write(self._mem_read(operand), enable=1)

        elif opcode == STORE:
            self.ram.write(int_to_bits(operand, ADDR_BITS),
                           self.acc.read(), write_enable=1)

        elif opcode == ADD:
            result, flags = alu(self.acc.read(), self._mem_read(operand), OP_ADD)
            self.acc.write(result, enable=1)
            self.zero_flag = flags.zero

        elif opcode == SUB:
            result, flags = alu(self.acc.read(), self._mem_read(operand), OP_SUB)
            self.acc.write(result, enable=1)
            self.zero_flag = flags.zero

        elif opcode == JMP:
            self._set_pc(operand)
            advance = False

        elif opcode == JZ:
            if self.zero_flag == 1:
                self._set_pc(operand)
                advance = False

        elif opcode == OUT:
            self.output.append(self._acc_value())

        else:
            raise ValueError(f"unknown opcode {opcode:#x}")

        if advance:
            self._increment_pc()

    def run(self, max_cycles: int = 10_000) -> None:
        """Run until HALT (or a safety limit, to catch runaway programs)."""
        while not self.halted and self.cycles < max_cycles:
            self.step()
        if not self.halted:
            raise RuntimeError("program did not halt within max_cycles")

    def memory_dump(self) -> List[int]:
        """Read every memory word back as a list of ints (for inspection)."""
        return [bits_to_int(self._mem_read(a)) for a in range(MEM_WORDS)]
