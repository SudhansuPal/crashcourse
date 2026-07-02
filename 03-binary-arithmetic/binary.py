"""
Binary representation of numbers — including negatives, via two's complement.

Computers store everything as bits (0/1), the on/off states of the transistors
from module 02. To do arithmetic we first need a way to represent *numbers* as
groups of bits, and a way to represent *negative* numbers so the same adder
hardware can also subtract. This file is that representation. adder.py then
wires our gates into circuits that operate on it.

We represent an n-bit number as a list of bits, written the way humans do:
MSB (most significant bit) first, LSB (least significant bit) last. So the
4-bit number six is [0, 1, 1, 0] = 0*8 + 1*4 + 1*2 + 0*1.

Everything here is built from scratch: we convert to/from binary with plain
arithmetic (division and remainder), not Python's bin()/int(x, 2) or format
strings, because those are exactly the "library that does the thing for us".
"""

from typing import List

Bit = int


def int_to_bits(value: int, width: int) -> List[Bit]:
    """
    Convert a non-negative integer to a width-bit list, MSB first.

    Method: repeatedly take the remainder mod 2 (the current lowest bit) and
    divide by 2, filling the list from the LSB end. This is long division in
    base 2 — the same trick you'd do by hand.
    """
    if value < 0:
        raise ValueError("int_to_bits is for non-negative values; "
                         "use to_twos_complement for negatives")
    bits = [0] * width
    for i in range(width - 1, -1, -1):  # fill LSB (rightmost) first
        bits[i] = value % 2
        value //= 2
    if value != 0:
        raise OverflowError(f"value does not fit in {width} bits")
    return bits


def bits_to_int(bits: List[Bit]) -> int:
    """
    Convert a bit list (MSB first) to a non-negative integer.

    Each position contributes bit * 2**power, where the rightmost bit is 2**0.
    """
    value = 0
    for bit in bits:            # walk MSB -> LSB
        value = value * 2 + bit  # shift left one place, then add this bit
    return value


def to_twos_complement(value: int, width: int) -> List[Bit]:
    """
    Encode a signed integer in width-bit two's complement.

    Two's complement is the scheme real CPUs use for signed integers. The idea:
    interpret the top bit as negative. In n bits it represents the range
    -2**(n-1) .. 2**(n-1)-1, and the encoding of a value v is simply
    v mod 2**n. That single rule makes addition "just work" for negatives too,
    which is why the same adder can add and subtract.
    """
    lo, hi = -(2 ** (width - 1)), 2 ** (width - 1) - 1
    if not (lo <= value <= hi):
        raise OverflowError(
            f"{value} is out of range for {width}-bit two's complement "
            f"[{lo}, {hi}]"
        )
    # Python's % already returns a non-negative result, giving the wrap-around
    # representation directly (e.g. -1 mod 16 == 15 == 1111).
    return int_to_bits(value % (2 ** width), width)


def from_twos_complement(bits: List[Bit]) -> int:
    """
    Decode a two's complement bit list (MSB first) back to a signed integer.

    Read it as an unsigned value; if the top (sign) bit is 1, subtract 2**n to
    account for the negative weight of that top bit.
    """
    width = len(bits)
    unsigned = bits_to_int(bits)
    if bits[0] == 1:  # sign bit set -> negative
        unsigned -= 2 ** width
    return unsigned


def format_bits(bits: List[Bit]) -> str:
    """Render a bit list as a compact string, e.g. [0,1,1,0] -> '0110'."""
    return "".join(str(b) for b in bits)
