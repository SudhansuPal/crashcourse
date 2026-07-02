"""
Logic gates, built from transistors.

In module 01 we defined boolean operations as truth tables. Here we build the
real thing: physical gates wired from the transistor switches in transistor.py.
We construct just two gates directly from transistors —

    NOT  : a CMOS inverter (1 PMOS + 1 NMOS)
    NAND : a CMOS NAND     (2 PMOS + 2 NMOS)

— and then *derive every other gate* from NAND. We can do that because NAND is
"universal": module 01 already proved NOT, AND, and OR can be rebuilt from NAND
alone. That's not a coding trick; it's why a chip foundry can etch billions of
copies of essentially one gate and get a whole computer.

CMOS design pattern
-------------------
Every CMOS gate has two halves that share one output node:
    - a PULL-UP network of PMOS transistors, connecting the output to HIGH
    - a PULL-DOWN network of NMOS transistors, connecting the output to LOW
They are complementary: for any input, exactly one half conducts. Transistors
in SERIES conduct only if all are on (logical AND of switches); transistors in
PARALLEL conduct if any is on (logical OR of switches).
"""

from transistor import HIGH, LOW, nmos, pmos, wire

Bit = int


def NOT(a: Bit) -> Bit:
    """
    A CMOS inverter: one PMOS on top, one NMOS on the bottom.

        - PMOS(gate=a, source=HIGH): pulls output HIGH when a is LOW
        - NMOS(gate=a, source=LOW) : pulls output LOW  when a is HIGH

    For a=0 the PMOS conducts (output HIGH); for a=1 the NMOS conducts (output
    LOW). Exactly one drives the node, so wire() reads a clean value: NOT a.
    """
    pull_up = pmos(a, HIGH)   # drives HIGH when a == 0
    pull_down = nmos(a, LOW)  # drives LOW  when a == 1
    return wire(pull_up, pull_down)


def NAND(a: Bit, b: Bit) -> Bit:
    """
    A CMOS NAND gate: the fundamental building block.

    Pull-up (to HIGH): two PMOS in PARALLEL. Either one conducting pulls the
        output HIGH, so the output is HIGH whenever a is LOW OR b is LOW.
    Pull-down (to LOW): two NMOS in SERIES. Both must conduct to reach LOW, so
        the output is LOW only when a is HIGH AND b is HIGH.

    Result: LOW only when both inputs are HIGH  ==  NOT(a AND b)  ==  NAND.
    """
    # Parallel PMOS pull-up: two transistors driving the same node from HIGH.
    pull_up = wire_parallel(pmos(a, HIGH), pmos(b, HIGH))
    # Series NMOS pull-down: b's transistor takes its source from a's drain, so
    # current only reaches LOW if BOTH are conducting.
    pull_down = nmos(b, nmos(a, LOW))
    return wire(pull_up, pull_down)


def wire_parallel(*drivers):
    """
    Combine parallel transistors into a single sub-network output.

    Unlike the final output node, a parallel network is allowed to have *no*
    driver (all its transistors are off) — that just means this half of the gate
    isn't driving, which is fine. So we return the driven value if any, else
    None (floating), and let the final wire() at the output node sort it out.
    """
    driven = [d for d in drivers if d is not None]
    if not driven:
        return None
    if any(d != driven[0] for d in driven):
        raise ValueError("short circuit inside parallel network")
    return driven[0]


# ---------------------------------------------------------------------------
# Everything below is derived from NAND (and NOT) only — no transistors, no
# Python and/or. This mirrors how real designs compose a few standard cells.
# ---------------------------------------------------------------------------

def AND(a: Bit, b: Bit) -> Bit:
    """AND is a NAND followed by an inverter."""
    return NOT(NAND(a, b))


def OR(a: Bit, b: Bit) -> Bit:
    """
    OR from NAND, via De Morgan:  a OR b == NAND(NOT a, NOT b).
    (Invert both inputs, then NAND them.)
    """
    return NAND(NOT(a), NOT(b))


def NOR(a: Bit, b: Bit) -> Bit:
    """NOR is an OR followed by an inverter."""
    return NOT(OR(a, b))


def XOR(a: Bit, b: Bit) -> Bit:
    """
    XOR from four NAND gates — the classic textbook construction.

        n1 = NAND(a, b)
        n2 = NAND(a, n1)
        n3 = NAND(b, n1)
        out = NAND(n2, n3)

    XOR (1 when inputs differ) is the heart of binary addition: it produces the
    sum bit, while AND produces the carry. We wire that up in module 03.
    """
    n1 = NAND(a, b)
    n2 = NAND(a, n1)
    n3 = NAND(b, n1)
    return NAND(n2, n3)


def XNOR(a: Bit, b: Bit) -> Bit:
    """XNOR (1 when inputs are equal) is an inverted XOR."""
    return NOT(XOR(a, b))


# A convenient registry so the demo and tests can iterate over every gate.
UNARY_GATES = {"NOT": NOT}
BINARY_GATES = {
    "NAND": NAND,
    "AND": AND,
    "OR": OR,
    "NOR": NOR,
    "XOR": XOR,
    "XNOR": XNOR,
}
