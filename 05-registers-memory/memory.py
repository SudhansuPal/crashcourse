"""
Registers and RAM — from single latches to addressable memory.

A single latch (latch.py) stores one bit. Stack a row of them and you get a
**register** that stores a whole number. Build an array of registers, add a way
to pick one by an **address**, and you get **RAM** (random-access memory): the
grid of storage a CPU reads from and writes to.

The one new idea here is the **address decoder**: a gate circuit that turns an
n-bit address into "one-hot" select lines — exactly one line high, the one
naming the chosen word. Reading then uses those select lines to gate the right
word's bits onto the output (a decoder + OR mux). This is how a memory chip
knows which of its millions of cells you mean.

Built entirely on module 02's gates and the D latch from latch.py.
"""

import os
import sys
from typing import List

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_REPO_ROOT, "02-logic-gates"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gates import AND, OR, NOT  # noqa: E402
from latch import DLatch  # noqa: E402

Bit = int


class Register:
    """
    An n-bit register: a bank of D latches sharing one write-enable line.

        write(bits, enable=1) : if enable, store all bits at once
        read()                : return the stored bits (MSB first)
    """

    def __init__(self, width: int, initial: int = 0):
        self.width = width
        # One latch per bit. We initialize from the given value, MSB first.
        init_bits = [(initial >> (width - 1 - i)) & 1 for i in range(width)]
        self.latches = [DLatch(b) for b in init_bits]

    def write(self, bits: List[Bit], enable: Bit = 1) -> None:
        if len(bits) != self.width:
            raise ValueError("data width mismatch")
        for latch, b in zip(self.latches, bits):
            latch.step(b, enable)  # enable=0 -> each latch holds its value

    def read(self) -> List[Bit]:
        return [latch.read() for latch in self.latches]


def _and_reduce(bits: List[Bit]) -> Bit:
    """Multi-input AND: 1 only if every input is 1 (chain of 2-input ANDs)."""
    acc = 1
    for b in bits:
        acc = AND(acc, b)
    return acc


def address_decoder(addr_bits: List[Bit]) -> List[Bit]:
    """
    Decode an n-bit address into 2**n one-hot select lines.

    Line k is high only when the address equals k. We build each line as an AND
    of the address bits in their required polarity: for line k, a bit that is 1
    in k must be high, a bit that is 0 in k must be low (so we feed NOT of it).
    Exactly one line ends up high — the selected word.
    """
    n = len(addr_bits)
    lines = []
    for k in range(2 ** n):
        # For address bit i (MSB first), decide whether line k wants it 1 or 0.
        literals = []
        for i, a in enumerate(addr_bits):
            want_one = (k >> (n - 1 - i)) & 1
            literals.append(a if want_one else NOT(a))
        lines.append(_and_reduce(literals))
    return lines


class RAM:
    """
    Addressable memory: an array of registers selected by an address decoder.

        write(addr_bits, data_bits, write_enable=1)
        read(addr_bits) -> data_bits

    Writing decodes the address to one-hot lines and ANDs each with the global
    write-enable, so only the addressed word's latches actually capture the data.
    Reading gates every word's bits with its select line and ORs them together —
    a decoder-driven multiplexer, all from gates.
    """

    def __init__(self, num_words: int, width: int):
        # num_words must be a power of two so the address bits address it exactly.
        n = (num_words - 1).bit_length()
        if 2 ** n != num_words:
            raise ValueError("num_words must be a power of two")
        self.addr_bits = n
        self.width = width
        self.words = [Register(width) for _ in range(num_words)]

    def write(self, addr_bits: List[Bit], data_bits: List[Bit],
              write_enable: Bit = 1) -> None:
        if len(addr_bits) != self.addr_bits:
            raise ValueError("address width mismatch")
        if len(data_bits) != self.width:
            raise ValueError("data width mismatch")
        select = address_decoder(addr_bits)
        for line, word in zip(select, self.words):
            # This word captures data only if it's selected AND we're writing.
            word.write(data_bits, AND(line, write_enable))

    def read(self, addr_bits: List[Bit]) -> List[Bit]:
        if len(addr_bits) != self.addr_bits:
            raise ValueError("address width mismatch")
        select = address_decoder(addr_bits)
        # Output bit j = OR over all words of (select_line AND word_bit_j).
        out = [0] * self.width
        for line, word in zip(select, self.words):
            bits = word.read()
            for j in range(self.width):
                out[j] = OR(out[j], AND(line, bits[j]))
        return out
