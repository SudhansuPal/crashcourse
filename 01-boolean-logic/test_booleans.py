"""
Unit tests for the boolean operations.

Because each operation has at most two 1-bit inputs, every operation has at
most four possible input combinations. That means we can test each one
*exhaustively* against its known truth table — these aren't samples, they cover
every case that can ever occur.

Run from the repo root:

    pytest 01-boolean-logic/
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from booleans import (  # noqa: E402
    NOT, AND, OR, NAND, NOR, XOR, XNOR, IMPLIES, truth_table,
)


# Each expected table is the canonical definition of the operation.
def test_not():
    assert NOT(0) == 1
    assert NOT(1) == 0


def test_and():
    assert [out for _, out in truth_table(AND)] == [0, 0, 0, 1]


def test_or():
    assert [out for _, out in truth_table(OR)] == [0, 1, 1, 1]


def test_nand():
    assert [out for _, out in truth_table(NAND)] == [1, 1, 1, 0]


def test_nor():
    assert [out for _, out in truth_table(NOR)] == [1, 0, 0, 0]


def test_xor():
    # 1 exactly when the inputs differ.
    assert [out for _, out in truth_table(XOR)] == [0, 1, 1, 0]


def test_xnor():
    # 1 exactly when the inputs are equal.
    assert [out for _, out in truth_table(XNOR)] == [1, 0, 0, 1]


def test_implies():
    # a -> b is false only for a=1, b=0.
    assert [out for _, out in truth_table(IMPLIES)] == [1, 1, 0, 1]


def test_de_morgan_laws_hold_exhaustively():
    for a in (0, 1):
        for b in (0, 1):
            assert NOT(AND(a, b)) == OR(NOT(a), NOT(b))
            assert NOT(OR(a, b)) == AND(NOT(a), NOT(b))


def test_double_negation():
    for a in (0, 1):
        assert NOT(NOT(a)) == a


def test_nand_is_universal():
    """NOT, AND, OR rebuilt from only NAND must match the originals."""
    not_n = lambda a: NAND(a, a)
    and_n = lambda a, b: not_n(NAND(a, b))
    or_n = lambda a, b: NAND(not_n(a), not_n(b))
    for a in (0, 1):
        assert not_n(a) == NOT(a)
        for b in (0, 1):
            assert and_n(a, b) == AND(a, b)
            assert or_n(a, b) == OR(a, b)


@pytest.mark.parametrize("bad", [-1, 2, "1", 1.0, None, True])
def test_invalid_bits_rejected(bad):
    """Anything that isn't exactly int 0 or 1 must be rejected loudly."""
    # Note: True/1.0 are excluded because `True == 1` in Python; we require the
    # value to be a genuine 0/1 int, so bool and float are rejected too.
    if bad in (0, 1) and type(bad) is int:
        pytest.skip("valid bit")
    with pytest.raises(ValueError):
        AND(bad, 0)
