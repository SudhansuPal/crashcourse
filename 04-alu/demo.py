"""
Runnable demonstration of the ALU.

Run from the repo root:

    python 04-alu/demo.py

Shows the multiplexer (the selection primitive), then runs every ALU operation
on sample operands and prints the result and status flags.
"""

import os
import sys

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_REPO_ROOT, "03-binary-arithmetic"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from binary import to_twos_complement, from_twos_complement, format_bits  # noqa: E402
from alu import (  # noqa: E402
    alu, mux2, mux8_bus, OP_NAMES,
    OP_ADD, OP_SUB, OP_AND, OP_OR, OP_XOR, OP_NOT, OP_SLT,
)


def show_mux() -> None:
    print("=" * 60)
    print("MULTIPLEXER  (mux2: sel picks input a or b)")
    print("=" * 60)
    print("  sel a b | out")
    print("  --------+----")
    for sel in (0, 1):
        for a in (0, 1):
            for b in (0, 1):
                print(f"   {sel}  {a} {b} |  {mux2(sel, a, b)}")
    print("\n  8-to-1 bus mux: select index 5 of eight 4-bit inputs")
    inputs = [to_twos_complement(v, 4) for v in range(8)]
    picked = mux8_bus(1, 0, 1, inputs)  # 101 = 5
    print(f"   selectors (s2,s1,s0)=(1,0,1) -> {format_bits(picked)} "
          f"= {from_twos_complement(picked)}")


def run_op(a: int, b: int, op: int, width: int = 8) -> None:
    abits = to_twos_complement(a, width)
    bbits = to_twos_complement(b, width)
    res, flags = alu(abits, bbits, op)
    val = from_twos_complement(res)
    fl = f"Z={flags.zero} N={flags.negative} C={flags.carry} V={flags.overflow}"
    print(f"  {OP_NAMES[op]:3}  {a:4},{b:4}  ->  {format_bits(res)} "
          f"({val:4})   [{fl}]")


def show_operations() -> None:
    print("\n" + "=" * 60)
    print("ALU OPERATIONS  (8-bit signed; flags Z=zero N=neg C=carry V=ovf)")
    print("=" * 60)
    print(" With a=12, b=10:")
    for op in (OP_ADD, OP_SUB, OP_AND, OP_OR, OP_XOR, OP_NOT, OP_SLT):
        run_op(12, 10, op)

    print("\n Flag showcases:")
    run_op(5, 5, OP_SUB)      # zero flag
    run_op(-3, -4, OP_ADD)    # negative result
    run_op(100, 50, OP_ADD)   # signed overflow (150 > 127)
    run_op(3, 9, OP_SLT)      # a < b -> 1
    run_op(9, 3, OP_SLT)      # a >= b -> 0


if __name__ == "__main__":
    show_mux()
    show_operations()
