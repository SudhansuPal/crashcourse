"""
Runnable demonstration of binary arithmetic built from gates.

Run from the repo root:

    python 03-binary-arithmetic/demo.py

Shows binary/two's-complement representation, the half- and full-adder truth
tables, a worked multi-bit addition with the carry rippling, and subtraction
done by the same adder via two's complement.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from binary import (  # noqa: E402
    int_to_bits, bits_to_int, to_twos_complement, from_twos_complement,
    format_bits,
)
from adder import (  # noqa: E402
    half_adder, full_adder, ripple_carry_add, ripple_carry_subtract,
    negate, add_ints, subtract_ints,
)


def show_representation() -> None:
    print("=" * 56)
    print("REPRESENTATION")
    print("=" * 56)
    print("Unsigned 4-bit:")
    for v in range(0, 16, 3):
        bits = int_to_bits(v, 4)
        print(f"  {v:2}  ->  {format_bits(bits)}  ->  {bits_to_int(bits)}")
    print("\nSigned 4-bit (two's complement); note the top bit is the sign:")
    for v in [0, 1, 7, -1, -8, -5]:
        bits = to_twos_complement(v, 4)
        print(f"  {v:3}  ->  {format_bits(bits)}  ->  {from_twos_complement(bits)}")


def show_adders() -> None:
    print("\n" + "=" * 56)
    print("HALF ADDER  (sum = XOR, carry = AND)")
    print("=" * 56)
    print("  a b | sum carry")
    print("  ----+----------")
    for a in (0, 1):
        for b in (0, 1):
            s, c = half_adder(a, b)
            print(f"  {a} {b} |  {s}    {c}")

    print("\n" + "=" * 56)
    print("FULL ADDER  (adds a, b, and carry-in)")
    print("=" * 56)
    print("  a b cin | sum cout")
    print("  --------+---------")
    for a in (0, 1):
        for b in (0, 1):
            for cin in (0, 1):
                s, c = full_adder(a, b, cin)
                print(f"  {a} {b}  {cin}  |  {s}    {c}")


def show_ripple_addition() -> None:
    print("\n" + "=" * 56)
    print("RIPPLE-CARRY ADDITION  (8-bit): 23 + 42")
    print("=" * 56)
    a, b = 23, 42
    abits = to_twos_complement(a, 8)
    bbits = to_twos_complement(b, 8)
    total, carry = ripple_carry_add(abits, bbits)
    print(f"   {format_bits(abits)}   ({a})")
    print(f" + {format_bits(bbits)}   ({b})")
    print(f"   --------")
    print(f"   {format_bits(total)}   ({from_twos_complement(total)}), carry-out={carry}")


def show_subtraction() -> None:
    print("\n" + "=" * 56)
    print("SUBTRACTION via two's complement: 42 - 23  ==  42 + (-23)")
    print("=" * 56)
    a, b = 42, 23
    abits = to_twos_complement(a, 8)
    bbits = to_twos_complement(b, 8)
    neg_b, _ = negate(bbits)
    print(f"   b            = {format_bits(bbits)}   ({b})")
    print(f"   negate(b)    = {format_bits(neg_b)}   ({from_twos_complement(neg_b)})")
    diff, _ = ripple_carry_subtract(abits, bbits)
    print(f"   42 - 23      = {format_bits(diff)}   ({from_twos_complement(diff)})")


def show_signed_roundtrip() -> None:
    print("\n" + "=" * 56)
    print("SAME ADDER HANDLES SIGNS: a few signed cases (8-bit)")
    print("=" * 56)
    # kept within 8-bit signed range so no result wraps (overflow is real!)
    cases = [(23, 42), (-5, 8), (60, -40), (-40, -50)]
    for a, b in cases:
        print(f"  {a:4} + {b:4} = {add_ints(a, b):5}   |   "
              f"{a:4} - {b:4} = {subtract_ints(a, b):5}")


if __name__ == "__main__":
    show_representation()
    show_adders()
    show_ripple_addition()
    show_subtraction()
    show_signed_roundtrip()
