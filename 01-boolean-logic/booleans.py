"""
Boolean logic, from first principles.

This is layer zero of the whole project. Everything a computer does — adding
numbers, storing memory, running programs — is ultimately built out of the
handful of operations defined in this file. So we are careful here: we do NOT
lean on Python's built-in `and`, `or`, `not` keywords to define our logic.
Instead we start from the smallest possible foundation and *derive* everything
else from it.

A "bit" here is the integer 0 (false) or 1 (true). We use 0/1 rather than
Python's True/False on purpose: it keeps us close to the hardware mindset we'll
need in later modules, where a bit is literally a wire that is either off or on.

The foundation
--------------
We take exactly two operations as primitive, defined by their truth tables
(the exhaustive list of every input-to-output mapping):

    NOT : flips a bit
    AND : 1 only when *both* inputs are 1

From just these two, every other boolean operation can be constructed. We prove
that by building OR, XOR, NAND, NOR, XNOR, and IMPLIES out of nothing but NOT
and AND below.
"""

# A bit is 0 or 1. We validate inputs so mistakes surface loudly instead of
# silently producing nonsense two layers up the stack.
Bit = int


def _check(*bits: Bit) -> None:
    """
    Guard: every value flowing through our logic must be exactly the int 0 or 1.

    We check the *type* explicitly, not just the value. In Python `True == 1`
    and `1.0 == 1`, so a plain `b in (0, 1)` would quietly let a bool or float
    through. At layer zero we want to be pedantic: a bit is an int, on or off.
    """
    for b in bits:
        if type(b) is not int or b not in (0, 1):
            raise ValueError(f"expected a bit (int 0 or 1), got {b!r}")


# ---------------------------------------------------------------------------
# The two primitives, defined directly by their truth tables.
# A truth table is just a lookup from inputs to output. Nothing is assumed;
# we simply list what each operation *is*.
# ---------------------------------------------------------------------------

# NOT has one input, so its table has two rows.
_NOT_TABLE = {
    0: 1,
    1: 0,
}

# AND has two inputs, so its table has four rows (2 x 2 combinations).
_AND_TABLE = {
    (0, 0): 0,
    (0, 1): 0,
    (1, 0): 0,
    (1, 1): 1,
}


def NOT(a: Bit) -> Bit:
    """Invert a bit. NOT 0 = 1, NOT 1 = 0."""
    _check(a)
    return _NOT_TABLE[a]


def AND(a: Bit, b: Bit) -> Bit:
    """1 only when both inputs are 1."""
    _check(a, b)
    return _AND_TABLE[(a, b)]


# ---------------------------------------------------------------------------
# Everything below is DERIVED from NOT and AND only. No new truth tables, no
# Python `and`/`or`/`not`. This is the whole point: a tiny foundation is
# enough to express all of boolean logic.
# ---------------------------------------------------------------------------


def OR(a: Bit, b: Bit) -> Bit:
    """
    1 when *either* input is 1.

    Derived via De Morgan's law:  a OR b == NOT( (NOT a) AND (NOT b) )

    Intuition: "either is true" is the same as "it is not the case that both
    are false."
    """
    return NOT(AND(NOT(a), NOT(b)))


def NAND(a: Bit, b: Bit) -> Bit:
    """NOT-AND: 0 only when both inputs are 1. (The universal gate — see module 02.)"""
    return NOT(AND(a, b))


def NOR(a: Bit, b: Bit) -> Bit:
    """NOT-OR: 1 only when both inputs are 0."""
    return NOT(OR(a, b))


def XOR(a: Bit, b: Bit) -> Bit:
    """
    Exclusive OR: 1 when the inputs *differ*.

    Derived: (a AND NOT b) OR (NOT a AND b)

    Reads literally as "a but not b, or b but not a" — i.e. exactly one of them.
    XOR is the workhorse of binary addition, which we'll build in module 03.
    """
    return OR(AND(a, NOT(b)), AND(NOT(a), b))


def XNOR(a: Bit, b: Bit) -> Bit:
    """Exclusive NOR: 1 when the inputs are *equal*. The opposite of XOR."""
    return NOT(XOR(a, b))


def IMPLIES(a: Bit, b: Bit) -> Bit:
    """
    Logical implication "a -> b": false only when a is true but b is false.

    Derived: (NOT a) OR b
    """
    return OR(NOT(a), b)


# ---------------------------------------------------------------------------
# Helpers for exploring and proving properties of the operations above.
# ---------------------------------------------------------------------------

def truth_table(op, arity: int = 2):
    """
    Build the full truth table for a boolean operation.

    Returns a list of (inputs_tuple, output) rows covering every combination
    of inputs. Great for *seeing* what an operation does rather than trusting
    the code. `arity` is how many inputs the operation takes (1 or 2).
    """
    rows = []
    if arity == 1:
        for a in (0, 1):
            rows.append(((a,), op(a)))
    elif arity == 2:
        for a in (0, 1):
            for b in (0, 1):
                rows.append(((a, b), op(a, b)))
    else:
        raise ValueError("this helper supports arity 1 or 2")
    return rows


def format_truth_table(name: str, op, arity: int = 2) -> str:
    """Render a truth table as a readable string block."""
    inputs = "a" if arity == 1 else "a b"
    lines = [f"{name}", f"  {inputs} | out", f"  {'-' * (len(inputs) + 6)}"]
    for ins, out in truth_table(op, arity):
        shown = " ".join(str(i) for i in ins)
        lines.append(f"  {shown} |  {out}")
    return "\n".join(lines)
