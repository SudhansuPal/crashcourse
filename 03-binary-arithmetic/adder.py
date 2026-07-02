"""
Adders — built from the logic gates of module 02.

This is where numbers get *computed*, not just represented. We wire the XOR,
AND, and OR gates from module 02 into circuits that add binary numbers. The
progression is exactly how real hardware is built up:

    half adder  ->  full adder  ->  ripple-carry adder (n bits)

And then, thanks to two's complement (binary.py), the very same adder does
subtraction with a tiny twist. No Python `+` on the numbers themselves: the
arithmetic emerges from gates operating on individual bits.
"""

import os
import sys
from typing import List, Tuple

# Reach up to the repo root and into module 02 so we can import its gates. This
# keeps the "each layer uses the one below it" promise literal: our adder runs
# on the exact gates we built from transistors.
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_REPO_ROOT, "02-logic-gates"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gates import XOR, AND, OR, NOT  # noqa: E402
from binary import to_twos_complement, from_twos_complement  # noqa: E402

Bit = int


def half_adder(a: Bit, b: Bit) -> Tuple[Bit, Bit]:
    """
    Add two single bits. Returns (sum, carry).

    Adding two bits can total 0, 1, or 2. In binary that's a 2-bit answer:
        0+0 = 00, 0+1 = 01, 1+0 = 01, 1+1 = 10
    The low bit (sum) is 1 when the inputs differ  -> XOR.
    The high bit (carry) is 1 only when both are 1 -> AND.
    That's the entire half adder: one XOR and one AND.
    """
    return XOR(a, b), AND(a, b)


def full_adder(a: Bit, b: Bit, carry_in: Bit) -> Tuple[Bit, Bit]:
    """
    Add three bits: a, b, and a carry coming in from the column to the right.
    Returns (sum, carry_out).

    Built from two half adders plus an OR:
        (s1, c1) = half_adder(a, b)          # add a and b
        (sum, c2) = half_adder(s1, carry_in) # then add the incoming carry
        carry_out = c1 OR c2                  # a carry out if either add carried
    Chaining full adders lets us add numbers of any width.
    """
    s1, c1 = half_adder(a, b)
    total, c2 = half_adder(s1, carry_in)
    carry_out = OR(c1, c2)
    return total, carry_out


def ripple_carry_add(
    a_bits: List[Bit], b_bits: List[Bit], carry_in: Bit = 0
) -> Tuple[List[Bit], Bit]:
    """
    Add two equal-width numbers, bit by bit, from LSB to MSB.
    Returns (sum_bits, carry_out), with sum_bits MSB first like the inputs.

    "Ripple carry" because each column's carry-out feeds the next column's
    carry-in, so the carry ripples leftward — exactly like grade-school
    addition, but in base 2 and made of gates.
    """
    if len(a_bits) != len(b_bits):
        raise ValueError("operands must have the same width")

    width = len(a_bits)
    result = [0] * width
    carry = carry_in
    for i in range(width - 1, -1, -1):  # start at the LSB (rightmost)
        result[i], carry = full_adder(a_bits[i], b_bits[i], carry)
    return result, carry


def invert_bits(bits: List[Bit]) -> List[Bit]:
    """Flip every bit using the NOT gate (the first step of negation)."""
    return [NOT(b) for b in bits]


def negate(bits: List[Bit]) -> Tuple[List[Bit], Bit]:
    """
    Two's complement negation: invert all bits, then add 1.

    This is why subtraction needs no separate circuit. -x is computed with the
    same NOT gates and the same adder we already have.
    """
    inverted = invert_bits(bits)
    one = [0] * (len(bits) - 1) + [1]
    return ripple_carry_add(inverted, one)


def ripple_carry_subtract(
    a_bits: List[Bit], b_bits: List[Bit]
) -> Tuple[List[Bit], Bit]:
    """
    Compute a - b using the adder: a - b == a + (NOT b) + 1.

    We invert b and feed a carry_in of 1 straight into the adder — that "+1" is
    the finishing touch of two's complement negation, folded into the add. One
    adder, both operations.
    """
    return ripple_carry_add(a_bits, invert_bits(b_bits), carry_in=1)


def add_ints(a: int, b: int, width: int = 8) -> int:
    """
    Convenience wrapper: add two signed Python ints by encoding them in two's
    complement, running them through the gate-level adder, and decoding back.
    Purely for demos/tests — the real work is in ripple_carry_add.
    """
    sum_bits, _ = ripple_carry_add(
        to_twos_complement(a, width), to_twos_complement(b, width)
    )
    return from_twos_complement(sum_bits)


def subtract_ints(a: int, b: int, width: int = 8) -> int:
    """Convenience wrapper for signed subtraction via the gate-level adder."""
    diff_bits, _ = ripple_carry_subtract(
        to_twos_complement(a, width), to_twos_complement(b, width)
    )
    return from_twos_complement(diff_bits)
