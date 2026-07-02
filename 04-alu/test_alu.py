"""
Unit tests for the ALU and its multiplexer building block.

The logic/arithmetic operations are checked exhaustively over all 4-bit signed
operand pairs against Python's own operators, and the flags against their
definitions.

Run from the repo root:

    pytest 04-alu/
"""

import os
import sys

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "03-binary-arithmetic"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from binary import to_twos_complement, from_twos_complement, bits_to_int  # noqa: E402
from alu import (  # noqa: E402
    alu, mux2, mux2_bus, mux8_bus,
    OP_ADD, OP_SUB, OP_AND, OP_OR, OP_XOR, OP_NOT, OP_SLT,
)

W = 4  # test width
LO, HI = -(2 ** (W - 1)), 2 ** (W - 1) - 1  # signed range for W bits


def _signed(a, b, op):
    res, flags = alu(to_twos_complement(a, W), to_twos_complement(b, W), op)
    return from_twos_complement(res), flags


# ---- multiplexer ----------------------------------------------------------

def test_mux2_selects():
    for a in (0, 1):
        for b in (0, 1):
            assert mux2(0, a, b) == a
            assert mux2(1, a, b) == b


def test_mux2_bus():
    assert mux2_bus(0, [1, 0, 1], [0, 1, 0]) == [1, 0, 1]
    assert mux2_bus(1, [1, 0, 1], [0, 1, 0]) == [0, 1, 0]


def test_mux8_selects_each_index():
    inputs = [to_twos_complement(v, W) for v in range(8)]
    for idx in range(8):
        s2, s1, s0 = (idx >> 2) & 1, (idx >> 1) & 1, idx & 1
        assert bits_to_int(mux8_bus(s2, s1, s0, inputs)) == idx


# ---- arithmetic (exhaustive, in-range) ------------------------------------

def test_add_matches_python():
    for a in range(LO, HI + 1):
        for b in range(LO, HI + 1):
            if LO <= a + b <= HI:
                val, _ = _signed(a, b, OP_ADD)
                assert val == a + b


def test_sub_matches_python():
    for a in range(LO, HI + 1):
        for b in range(LO, HI + 1):
            if LO <= a - b <= HI:
                val, _ = _signed(a, b, OP_SUB)
                assert val == a - b


# ---- bitwise logic (exhaustive, unsigned patterns) ------------------------

def test_bitwise_ops_match_python():
    for a in range(16):
        for b in range(16):
            abits, bbits = to_twos_complement(a - 8, W), to_twos_complement(b - 8, W)
            # compare raw bit patterns instead of signed values
            and_res, _ = alu(abits, bbits, OP_AND)
            or_res, _ = alu(abits, bbits, OP_OR)
            xor_res, _ = alu(abits, bbits, OP_XOR)
            ai, bi = bits_to_int(abits), bits_to_int(bbits)
            assert bits_to_int(and_res) == (ai & bi)
            assert bits_to_int(or_res) == (ai | bi)
            assert bits_to_int(xor_res) == (ai ^ bi)


def test_not_ignores_b():
    res, _ = alu(to_twos_complement(5, W), to_twos_complement(3, W), OP_NOT)
    # NOT of 0101 is 1010
    assert bits_to_int(res) == 0b1010


# ---- set-less-than (signed) ------------------------------------------------

def test_slt_matches_signed_comparison():
    for a in range(LO, HI + 1):
        for b in range(LO, HI + 1):
            val, _ = _signed(a, b, OP_SLT)
            assert val == (1 if a < b else 0)


# ---- flags ----------------------------------------------------------------

def test_zero_flag():
    _, flags = _signed(5, 5, OP_SUB)
    assert flags.zero == 1
    _, flags = _signed(5, 4, OP_SUB)
    assert flags.zero == 0


def test_negative_flag():
    _, flags = _signed(3, 7, OP_SUB)  # 3 - 7 = -4
    assert flags.negative == 1
    _, flags = _signed(7, 3, OP_SUB)  # 7 - 3 = 4
    assert flags.negative == 0


def test_overflow_flag_on_signed_overflow():
    # 4-bit signed max is 7; 5 + 4 = 9 overflows
    _, flags = _signed(5, 4, OP_ADD)
    assert flags.overflow == 1
    # no overflow for an in-range add
    _, flags = _signed(2, 3, OP_ADD)
    assert flags.overflow == 0


def test_width_mismatch_rejected():
    import pytest
    with pytest.raises(ValueError):
        alu([0, 1], [1, 0, 1], OP_ADD)
