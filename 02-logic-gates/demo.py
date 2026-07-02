"""
Runnable demonstration of logic gates built from transistors.

Run from the repo root:

    python 02-logic-gates/demo.py

It prints each gate's truth table (computed by pushing bits through simulated
transistors), shows the raw transistor switching behavior, and proves that our
transistor-built NAND matches the abstract NAND from module 01.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from transistor import nmos, pmos  # noqa: E402
from gates import (  # noqa: E402
    NOT, NAND, AND, OR, NOR, XOR, XNOR, UNARY_GATES, BINARY_GATES,
)


def show_transistors() -> None:
    print("=" * 52)
    print("TRANSISTORS  (the switch: gate controls source -> drain)")
    print("=" * 52)
    print("NMOS conducts when gate is HIGH; None means the drain floats.")
    print("  gate source | drain")
    print("  ------------+------")
    for g in (0, 1):
        for s in (0, 1):
            print(f"   {g}    {s}     |  {nmos(g, s)}")
    print("\nPMOS conducts when gate is LOW (the mirror image).")
    print("  gate source | drain")
    print("  ------------+------")
    for g in (0, 1):
        for s in (0, 1):
            print(f"   {g}    {s}     |  {pmos(g, s)}")


def show_gate_tables() -> None:
    print("\n" + "=" * 52)
    print("GATES  (built from the transistors above)")
    print("=" * 52)
    for name, op in UNARY_GATES.items():
        print(f"\n{name}  (CMOS inverter: 1 PMOS + 1 NMOS)")
        print("  a | out")
        print("  --+----")
        for a in (0, 1):
            print(f"  {a} |  {op(a)}")

    labels = {
        "NAND": "2 PMOS parallel + 2 NMOS series  (built from transistors)",
        "AND": "NOT(NAND(a,b))",
        "OR": "NAND(NOT a, NOT b)",
        "NOR": "NOT(OR(a,b))",
        "XOR": "four NANDs",
        "XNOR": "NOT(XOR(a,b))",
    }
    for name, op in BINARY_GATES.items():
        print(f"\n{name}  ({labels[name]})")
        print("  a b | out")
        print("  ----+----")
        for a in (0, 1):
            for b in (0, 1):
                print(f"  {a} {b} |  {op(a, b)}")


def prove_against_definitions() -> None:
    """
    Confirm our transistor-built gates match the canonical truth tables from
    boolean algebra (the same ones module 01 defined). Exhaustive over all
    inputs, so this is a proof, not a spot check.
    """
    print("\n" + "=" * 52)
    print("PROOF: gates match their boolean definitions (all inputs)")
    print("=" * 52)
    expected = {
        "NAND": [1, 1, 1, 0],
        "AND": [0, 0, 0, 1],
        "OR": [0, 1, 1, 1],
        "NOR": [1, 0, 0, 0],
        "XOR": [0, 1, 1, 0],
        "XNOR": [1, 0, 0, 1],
    }
    all_ok = NOT(0) == 1 and NOT(1) == 0
    for name, op in BINARY_GATES.items():
        got = [op(a, b) for a in (0, 1) for b in (0, 1)]
        ok = got == expected[name]
        all_ok = all_ok and ok
        print(f"  {name:5} -> {got}  matches {expected[name]}: {ok}")
    print(f"\n  Every gate matches its definition: {all_ok}")


if __name__ == "__main__":
    show_transistors()
    show_gate_tables()
    prove_against_definitions()
