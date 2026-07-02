"""
The transistor: the physical switch underneath all of computing.

Module 01 defined boolean operations as abstract truth tables. But where do
those operations actually *come from* in a real computer? The answer is the
transistor — a tiny electronic switch with no moving parts. Every logic gate in
every chip is built from transistors, and everything above (adders, memory,
CPUs) is built from gates. This file models that switch so that in gates.py we
can build gates the way hardware really does: out of transistors, not out of
Python's `and` / `or`.

How a (MOSFET) transistor works, in plain terms
-----------------------------------------------
A transistor has three connections:

    - gate   : the control input (a voltage that opens or closes the switch)
    - source : where current comes in
    - drain  : where current goes out

When the right voltage is on the GATE, a channel opens between SOURCE and DRAIN
and current flows (source appears at the drain). Otherwise the channel is closed
and the drain is left *floating* — not driven to any value at all.

There are two complementary flavors, and real chips (CMOS) use both together:

    - NMOS: conducts when the gate is HIGH (1). "On when told 1."
    - PMOS: conducts when the gate is LOW  (0). "On when told 0." (inverted)

Modeling floating with None
---------------------------
A voltage on a wire is a bit: 1 = HIGH, 0 = LOW. But an *open* switch drives
nothing, so we model a floating (undriven) wire as `None`. This is the key to
building gates honestly: a CMOS gate arranges a "pull-up" network (to HIGH) and
a "pull-down" network (to LOW) so that for every input, exactly one network
conducts and drives the output — never both, never neither. `wire()` below is
how we join those networks at a single output node.
"""

from typing import Optional

Bit = int
Signal = Optional[int]  # 1 (HIGH), 0 (LOW), or None (floating / undriven)

HIGH: Bit = 1  # a high voltage level
LOW: Bit = 0   # a low voltage level (ground)


def _check_gate(gate: Bit) -> None:
    """The gate terminal is a control input: it must be a real bit, 0 or 1."""
    if type(gate) is not int or gate not in (0, 1):
        raise ValueError(f"gate must be a bit (int 0 or 1), got {gate!r}")


def _check_signal(sig: Signal) -> None:
    """A source/drain signal may be HIGH, LOW, or floating (None)."""
    if sig is not None and (type(sig) is not int or sig not in (0, 1)):
        raise ValueError(f"signal must be 0, 1, or None, got {sig!r}")


def nmos(gate: Bit, source: Signal) -> Signal:
    """
    An NMOS transistor: connects source -> drain only when the gate is HIGH.

      - gate HIGH (1): switch closed  -> drain = source (pass it through)
      - gate LOW  (0): switch open    -> drain floats  -> None

    If the source itself is floating (None), there's nothing to pass, so the
    drain floats too. This lets us chain transistors in series (module below).
    """
    _check_gate(gate)
    _check_signal(source)
    return source if gate == HIGH else None


def pmos(gate: Bit, source: Signal) -> Signal:
    """
    A PMOS transistor: connects source -> drain only when the gate is LOW.
    The mirror image of NMOS.

      - gate LOW  (0): switch closed -> drain = source
      - gate HIGH (1): switch open   -> drain floats -> None
    """
    _check_gate(gate)
    _check_signal(source)
    return source if gate == LOW else None


def wire(*drivers: Signal) -> Bit:
    """
    Join several transistor outputs at one output node and read its voltage.

    In a correctly designed CMOS gate, for any input exactly one network drives
    the node. So among the drivers we expect:

      - exactly one (or more) non-floating values, and
      - if several drive it, they must AGREE (no HIGH fighting LOW).

    Two disagreeing drivers would be a short circuit; no driver at all would be
    a floating output. We treat both as bugs and raise, which is a great way to
    catch a mis-wired gate.
    """
    driven = [d for d in drivers if d is not None]
    if not driven:
        raise ValueError("floating output: no transistor is driving this node")
    if any(d != driven[0] for d in driven):
        raise ValueError("short circuit: node driven HIGH and LOW at once")
    return driven[0]
