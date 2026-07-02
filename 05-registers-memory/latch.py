"""
Latches — the first circuit that can *remember*.

Everything up to now has been "combinational": the output depends only on the
current inputs. Such a circuit has no past — it can compute, but it cannot
store. Memory needs something new: **feedback**, where a gate's output loops
back to its own input. That loop lets a circuit hold a value after the input
that set it has gone away. This is the birth of the *bit of storage*.

We build the classic SR ("set/reset") latch from two cross-coupled NAND gates,
then wrap it into a gated **D latch** that stores whatever bit is on its D
("data") input whenever its E ("enable") input is high.

A note on simulating feedback
-----------------------------
Our gates from module 02 are pure functions, but a real latch is a loop: Q
depends on Q_bar, which depends on Q. We model that honestly by keeping the
stored (Q, Q_bar) as state and, on each update, re-evaluating the gate equations
until they stop changing — i.e. until the loop *settles* to a stable state.
That settling is exactly what happens in silicon in a fraction of a nanosecond.
"""

import os
import sys

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_REPO_ROOT, "02-logic-gates"))

from gates import NAND, NOT  # noqa: E402

Bit = int


class DLatch:
    """
    A gated D latch built from a NAND SR latch.

        E = 0 : the latch HOLDS its stored bit (input ignored)
        E = 1 : the latch stores D (Q becomes D)

    Internally:
        s_bar = NAND(D, E)         # active-low "set"
        r_bar = NAND(NOT D, E)     # active-low "reset"
        Q     = NAND(s_bar, Q_bar) # cross-coupled...
        Q_bar = NAND(r_bar, Q)     # ...feedback pair
    """

    def __init__(self, initial: Bit = 0):
        # Start in a valid, stable state where Q and Q_bar are complementary.
        self.q: Bit = initial
        self.q_bar: Bit = NOT(initial)

    def step(self, d: Bit, enable: Bit) -> Bit:
        """
        Apply inputs and let the feedback loop settle. Returns the new Q.

        We iterate the gate equations until (Q, Q_bar) stops changing. For a
        well-formed latch this converges in a couple of passes; we cap the
        iterations so a pathological input can't loop forever.
        """
        s_bar = NAND(d, enable)
        r_bar = NAND(NOT(d), enable)
        for _ in range(10):  # settle the cross-coupled loop
            new_q = NAND(s_bar, self.q_bar)
            new_q_bar = NAND(r_bar, self.q)
            if new_q == self.q and new_q_bar == self.q_bar:
                break  # stable
            self.q, self.q_bar = new_q, new_q_bar
        return self.q

    def read(self) -> Bit:
        """Read the stored bit without changing it."""
        return self.q
