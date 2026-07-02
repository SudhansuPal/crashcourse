"""
Unit tests for binary representation and the gate-level adders.

Run from the repo root:

    pytest 03-binary-arithmetic/
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from binary import (  # noqa: E402
    int_to_bits, bits_to_int, to_twos_complement, from_twos_complement,
)
from adder import (  # noqa: E402
    half_adder, full_adder, ripple_carry_add, ripple_carry_subtract,
    negate, invert_bits, add_ints, subtract_ints,
)


# ---- representation -------------------------------------------------------

def test_unsigned_roundtrip_all_4bit():
    for v in range(16):
        assert bits_to_int(int_to_bits(v, 4)) == v


def test_int_to_bits_known_values():
    assert int_to_bits(6, 4) == [0, 1, 1, 0]
    assert int_to_bits(0, 4) == [0, 0, 0, 0]
    assert int_to_bits(15, 4) == [1, 1, 1, 1]


def test_int_to_bits_overflow():
    with pytest.raises(OverflowError):
        int_to_bits(16, 4)


def test_int_to_bits_rejects_negative():
    with pytest.raises(ValueError):
        int_to_bits(-1, 4)


def test_twos_complement_known_values():
    assert to_twos_complement(-1, 4) == [1, 1, 1, 1]
    assert to_twos_complement(-8, 4) == [1, 0, 0, 0]
    assert to_twos_complement(7, 4) == [0, 1, 1, 1]


def test_twos_complement_roundtrip_full_range():
    for v in range(-8, 8):  # full signed range for 4 bits
        assert from_twos_complement(to_twos_complement(v, 4)) == v


def test_twos_complement_out_of_range():
    with pytest.raises(OverflowError):
        to_twos_complement(8, 4)   # max is 7
    with pytest.raises(OverflowError):
        to_twos_complement(-9, 4)  # min is -8


# ---- adders (exhaustive where small) --------------------------------------

def test_half_adder_truth_table():
    assert half_adder(0, 0) == (0, 0)
    assert half_adder(0, 1) == (1, 0)
    assert half_adder(1, 0) == (1, 0)
    assert half_adder(1, 1) == (0, 1)  # 1+1 = binary 10


def test_full_adder_matches_arithmetic_exhaustively():
    for a in (0, 1):
        for b in (0, 1):
            for cin in (0, 1):
                s, c = full_adder(a, b, cin)
                total = a + b + cin
                assert s == total % 2       # sum bit
                assert c == total // 2       # carry bit


def test_ripple_add_all_pairs_4bit():
    """Exhaustively check every 4-bit unsigned addition against Python."""
    for a in range(16):
        for b in range(16):
            bits, carry = ripple_carry_add(int_to_bits(a, 4), int_to_bits(b, 4))
            got = carry * 16 + bits_to_int(bits)  # include carry as the 5th bit
            assert got == a + b


def test_ripple_add_width_mismatch():
    with pytest.raises(ValueError):
        ripple_carry_add([0, 1], [1, 0, 1])


def test_invert_and_negate():
    assert invert_bits([1, 0, 1, 0]) == [0, 1, 0, 1]
    # negate(3) in 4-bit two's complement should be -3
    neg, _ = negate(to_twos_complement(3, 4))
    assert from_twos_complement(neg) == -3
    # negate(0) is 0
    neg0, _ = negate(to_twos_complement(0, 4))
    assert from_twos_complement(neg0) == 0


def test_subtraction_via_twos_complement():
    diff, _ = ripple_carry_subtract(to_twos_complement(5, 8),
                                    to_twos_complement(3, 8))
    assert from_twos_complement(diff) == 2


def test_signed_add_and_subtract_wrappers():
    # all chosen so both a+b and a-b stay within 8-bit signed range [-128, 127]
    cases = [(23, 42), (-5, 8), (60, -40), (-40, -50), (0, 0), (100, 20)]
    for a, b in cases:
        assert add_ints(a, b) == a + b
        assert subtract_ints(a, b) == a - b


def test_signed_arithmetic_full_range_4bit():
    """Every in-range signed add/subtract must match Python arithmetic."""
    for a in range(-8, 8):
        for b in range(-8, 8):
            if -8 <= a + b <= 7:
                assert add_ints(a, b, width=4) == a + b
            if -8 <= a - b <= 7:
                assert subtract_ints(a, b, width=4) == a - b
