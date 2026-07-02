"""
Runnable demonstration of boolean logic built from first principles.

Run it from the repo root:

    python 01-boolean-logic/demo.py

It prints the truth tables for every operation and then *proves*, by exhaustive
check, two famous laws of boolean algebra — showing that our derived operations
actually obey the rules real hardware relies on.
"""

# Allow running this file directly (`python 01-boolean-logic/demo.py`) by making
# the module's own folder importable regardless of the current directory.
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from booleans import (  # noqa: E402  (import after sys.path tweak, on purpose)
    NOT, AND, OR, NAND, NOR, XOR, XNOR, IMPLIES,
    format_truth_table,
)


def show_truth_tables() -> None:
    print("=" * 44)
    print("TRUTH TABLES  (0 = false, 1 = true)")
    print("=" * 44)
    print(format_truth_table("NOT  (primitive)", NOT, arity=1))
    print()
    print(format_truth_table("AND  (primitive)", AND))
    print()
    for name, op in [
        ("OR      = NOT(AND(NOT a, NOT b))", OR),
        ("NAND    = NOT(AND(a, b))", NAND),
        ("NOR     = NOT(OR(a, b))", NOR),
        ("XOR     = (a AND NOT b) OR (NOT a AND b)", XOR),
        ("XNOR    = NOT(XOR(a, b))", XNOR),
        ("IMPLIES = (NOT a) OR b", IMPLIES),
    ]:
        print(format_truth_table(name, op))
        print()


def prove_de_morgan() -> None:
    """
    De Morgan's laws relate AND and OR through NOT:

        NOT(a AND b) == (NOT a) OR (NOT b)
        NOT(a OR  b) == (NOT a) AND (NOT b)

    We check them for *every* possible input, which for two bits is only four
    cases — small enough to be a genuine proof, not just a spot check.
    """
    print("=" * 44)
    print("PROOF: De Morgan's laws (all 4 input cases)")
    print("=" * 44)
    ok = True
    for a in (0, 1):
        for b in (0, 1):
            law1 = NOT(AND(a, b)) == OR(NOT(a), NOT(b))
            law2 = NOT(OR(a, b)) == AND(NOT(a), NOT(b))
            ok = ok and law1 and law2
            print(f"  a={a} b={b} | NOT(a AND b)==(NOT a)OR(NOT b): {law1}"
                  f" | NOT(a OR b)==(NOT a)AND(NOT b): {law2}")
    print(f"\n  Both laws hold for every input: {ok}")


def prove_nand_is_universal() -> None:
    """
    A fun, foundational fact: NAND alone can reconstruct every other operation.
    Here we rebuild NOT, AND, and OR using *only* NAND, and confirm they match.
    This is why module 02 can build an entire computer's gates from one part.
    """
    print()
    print("=" * 44)
    print("PROOF: NAND is universal (rebuild NOT/AND/OR from NAND only)")
    print("=" * 44)

    def not_from_nand(a):
        return NAND(a, a)

    def and_from_nand(a, b):
        return not_from_nand(NAND(a, b))

    def or_from_nand(a, b):
        return NAND(not_from_nand(a), not_from_nand(b))

    ok = True
    for a in (0, 1):
        ok = ok and (not_from_nand(a) == NOT(a))
        for b in (0, 1):
            ok = ok and (and_from_nand(a, b) == AND(a, b))
            ok = ok and (or_from_nand(a, b) == OR(a, b))
    print(f"  NOT, AND, and OR rebuilt from NAND match the originals: {ok}")


if __name__ == "__main__":
    show_truth_tables()
    prove_de_morgan()
    prove_nand_is_universal()
