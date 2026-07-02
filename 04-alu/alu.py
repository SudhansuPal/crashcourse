"""
The ALU — Arithmetic Logic Unit.

This is the calculating heart of a CPU. An ALU takes two numbers and a small
control code (an "opcode") that says *which* operation to perform, then produces
a result plus a few status **flags** (was the result zero? negative? did it
overflow?). Every instruction a processor runs — add, subtract, compare, bitwise
AND/OR — ultimately flows through the ALU.

We build it entirely from the layers below:
    - the logic gates from module 02 (AND, OR, XOR, NOT)
    - the ripple-carry adder from module 03

...and one new building block introduced here: the **multiplexer** (mux), a
gate circuit that *selects* one of several inputs based on control bits. The mux
is how the ALU picks which operation's result to output. Compute everything,
then route the chosen answer out — that's how real ALUs work.
"""

import os
import sys
from typing import Dict, List, NamedTuple, Tuple

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_REPO_ROOT, "02-logic-gates"))
sys.path.insert(0, os.path.join(_REPO_ROOT, "03-binary-arithmetic"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gates import AND, OR, XOR, NOT  # noqa: E402
from adder import ripple_carry_add, invert_bits  # noqa: E402

Bit = int

# ---------------------------------------------------------------------------
# Opcodes: the control code that selects the operation. Chosen as 0..7 so a
# 3-bit selector can address all of them through the mux tree below.
# ---------------------------------------------------------------------------
OP_ADD = 0  # a + b
OP_SUB = 1  # a - b
OP_AND = 2  # bitwise a AND b
OP_OR = 3   # bitwise a OR b
OP_XOR = 4  # bitwise a XOR b
OP_NOT = 5  # bitwise NOT a (b ignored)
OP_SLT = 6  # set-less-than: result is 1 if a < b (signed), else 0
# opcode 7 is unused -> outputs zero

OP_NAMES = {
    OP_ADD: "ADD", OP_SUB: "SUB", OP_AND: "AND", OP_OR: "OR",
    OP_XOR: "XOR", OP_NOT: "NOT", OP_SLT: "SLT",
}


class Flags(NamedTuple):
    """Status bits the ALU reports alongside its result."""
    zero: Bit      # 1 if every result bit is 0
    negative: Bit  # 1 if the result's sign bit (MSB) is set
    carry: Bit     # carry-out of the adder (meaningful for ADD/SUB)
    overflow: Bit  # signed overflow occurred (meaningful for ADD/SUB)


# ---------------------------------------------------------------------------
# The multiplexer: select between inputs using control bits. Built from gates.
# ---------------------------------------------------------------------------

def mux2(sel: Bit, a: Bit, b: Bit) -> Bit:
    """
    2-to-1 multiplexer for a single bit:
        sel = 0  -> output a
        sel = 1  -> output b

    Wired as  (NOT sel AND a) OR (sel AND b): the two AND gates act as switches
    that only one control line can open, and the OR merges the winner.
    """
    return OR(AND(NOT(sel), a), AND(sel, b))


def mux2_bus(sel: Bit, bus_a: List[Bit], bus_b: List[Bit]) -> List[Bit]:
    """A 2-to-1 mux applied to every bit of two equal-width buses."""
    return [mux2(sel, x, y) for x, y in zip(bus_a, bus_b)]


def mux8_bus(s2: Bit, s1: Bit, s0: Bit, inputs: List[List[Bit]]) -> List[Bit]:
    """
    8-to-1 bus multiplexer built as a tree of 2-to-1 muxes, selected by the
    three bits (s2, s1, s0) — the binary encoding of which input to pass.

    Layer by layer we halve the choices: s0 picks within pairs, s1 picks within
    the survivors, s2 picks the final one. This is exactly how a wide mux is
    constructed in hardware.
    """
    assert len(inputs) == 8, "mux8 needs exactly 8 inputs"
    # s0 selects within each adjacent pair (4 survivors)
    l0 = [mux2_bus(s0, inputs[i], inputs[i + 1]) for i in (0, 2, 4, 6)]
    # s1 selects within the survivors (2 survivors)
    l1 = [mux2_bus(s1, l0[0], l0[1]), mux2_bus(s1, l0[2], l0[3])]
    # s2 selects the final result
    return mux2_bus(s2, l1[0], l1[1])


# ---------------------------------------------------------------------------
# Helpers for whole-bus logic operations (bit-parallel gates).
# ---------------------------------------------------------------------------

def _bus(op, a: List[Bit], b: List[Bit]) -> List[Bit]:
    return [op(x, y) for x, y in zip(a, b)]


def _is_zero(bits: List[Bit]) -> Bit:
    """Zero flag: OR all bits together, then invert. 1 only if every bit is 0."""
    acc = 0
    for bit in bits:
        acc = OR(acc, bit)
    return NOT(acc)


# ---------------------------------------------------------------------------
# The ALU itself.
# ---------------------------------------------------------------------------

def alu(a: List[Bit], b: List[Bit], op: int) -> Tuple[List[Bit], Flags]:
    """
    Compute one ALU operation. Inputs a and b are equal-width bit lists (MSB
    first); op is one of the OP_* opcodes. Returns (result_bits, flags).

    Design (mirrors real hardware): compute *all* candidate results in parallel,
    then use the opcode to mux out the one we want. Nothing branches on the
    opcode to do the math — the opcode only steers the selector.
    """
    if len(a) != len(b):
        raise ValueError("operands must have the same width")
    width = len(a)

    # --- Arithmetic unit: one adder does both ADD and SUB. ---
    # For subtraction (and for SLT, which needs a - b), feed NOT b and a
    # carry-in of 1: a - b == a + (NOT b) + 1. A mux picks b vs NOT b.
    use_sub = 1 if op in (OP_SUB, OP_SLT) else 0
    b_operand = mux2_bus(use_sub, b, invert_bits(b))
    arith, carry_out = ripple_carry_add(a, b_operand, carry_in=use_sub)

    # Signed overflow: the operands had the same sign but the result's sign
    # flipped. XNOR(a_sign, b_sign) AND XOR(a_sign, result_sign).
    a_sign, b_sign, r_sign = a[0], b_operand[0], arith[0]
    same_input_signs = NOT(XOR(a_sign, b_sign))       # XNOR
    result_sign_changed = XOR(a_sign, r_sign)
    overflow = AND(same_input_signs, result_sign_changed)

    # --- Logic unit: bit-parallel gate operations. ---
    and_res = _bus(AND, a, b)
    or_res = _bus(OR, a, b)
    xor_res = _bus(XOR, a, b)
    not_res = invert_bits(a)  # NOT ignores b

    # --- Set-less-than: a < b (signed) is true when the subtraction's sign,
    # corrected for overflow, is negative. Result is 0...0 or 0...1. ---
    less = XOR(r_sign, overflow)
    slt_res = [0] * (width - 1) + [less]

    zeros = [0] * width

    # Candidate results indexed by opcode; slot 7 is unused -> zeros.
    candidates: List[List[Bit]] = [
        arith,    # 0 ADD
        arith,    # 1 SUB (arith already computed a - b when use_sub)
        and_res,  # 2 AND
        or_res,   # 3 OR
        xor_res,  # 4 XOR
        not_res,  # 5 NOT
        slt_res,  # 6 SLT
        zeros,    # 7 unused
    ]

    # Decode the opcode into its 3 selector bits and mux out the chosen result.
    s2, s1, s0 = (op >> 2) & 1, (op >> 1) & 1, op & 1
    result = mux8_bus(s2, s1, s0, candidates)

    flags = Flags(
        zero=_is_zero(result),
        negative=result[0],
        carry=carry_out,
        overflow=overflow,
    )
    return result, flags


# Convenience registry for demos/tests.
ALL_OPS: Dict[int, str] = OP_NAMES
