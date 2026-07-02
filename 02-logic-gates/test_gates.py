"""
Unit tests for transistors and the gates built from them.

Every gate has at most two 1-bit inputs, so we test each one exhaustively
against its canonical truth table. We also test the transistor primitives and
the wiring helpers (floating and short-circuit detection).

Run from the repo root:

    pytest 02-logic-gates/
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from transistor import HIGH, LOW, nmos, pmos, wire  # noqa: E402
from gates import (  # noqa: E402
    NOT, NAND, AND, OR, NOR, XOR, XNOR, BINARY_GATES,
)


# ---- transistors ----------------------------------------------------------

def test_nmos_conducts_only_when_gate_high():
    assert nmos(HIGH, 1) == 1        # closed: passes source
    assert nmos(HIGH, 0) == 0        # closed: passes source
    assert nmos(LOW, 1) is None      # open: floats
    assert nmos(LOW, 0) is None      # open: floats


def test_pmos_conducts_only_when_gate_low():
    assert pmos(LOW, 1) == 1         # closed: passes source
    assert pmos(LOW, 0) == 0         # closed: passes source
    assert pmos(HIGH, 1) is None     # open: floats
    assert pmos(HIGH, 0) is None     # open: floats


def test_nmos_floating_source_stays_floating():
    # Enables series chaining: no input current -> no output current.
    assert nmos(HIGH, None) is None


def test_wire_reads_single_driver():
    assert wire(1, None) == 1
    assert wire(None, 0) == 0
    assert wire(None, None, 1) == 1


def test_wire_allows_agreeing_drivers():
    assert wire(1, 1) == 1
    assert wire(0, 0, None) == 0


def test_wire_rejects_floating_output():
    with pytest.raises(ValueError):
        wire(None, None)


def test_wire_rejects_short_circuit():
    with pytest.raises(ValueError):
        wire(1, 0)


# ---- gates (exhaustive truth tables) --------------------------------------

EXPECTED = {
    "NAND": [1, 1, 1, 0],
    "AND": [0, 0, 0, 1],
    "OR": [0, 1, 1, 1],
    "NOR": [1, 0, 0, 0],
    "XOR": [0, 1, 1, 0],
    "XNOR": [1, 0, 0, 1],
}


def test_not():
    assert NOT(0) == 1
    assert NOT(1) == 0


@pytest.mark.parametrize("name", list(EXPECTED))
def test_binary_gate_truth_table(name):
    op = BINARY_GATES[name]
    got = [op(a, b) for a in (0, 1) for b in (0, 1)]
    assert got == EXPECTED[name]


# ---- cross-checks / algebraic identities ----------------------------------

def test_and_is_inverted_nand():
    for a in (0, 1):
        for b in (0, 1):
            assert AND(a, b) == NOT(NAND(a, b))


def test_de_morgan_via_gates():
    for a in (0, 1):
        for b in (0, 1):
            assert NAND(a, b) == OR(NOT(a), NOT(b))
            assert NOR(a, b) == AND(NOT(a), NOT(b))


def test_xor_xnor_are_complements():
    for a in (0, 1):
        for b in (0, 1):
            assert XOR(a, b) == NOT(XNOR(a, b))


def test_not_equivalent_to_nand_self():
    """A NAND with both inputs tied together is an inverter."""
    for a in (0, 1):
        assert NOT(a) == NAND(a, a)


def test_gates_reject_invalid_bits():
    with pytest.raises(ValueError):
        NAND(2, 0)
    with pytest.raises(ValueError):
        NOT(None)
