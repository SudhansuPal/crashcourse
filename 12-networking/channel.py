"""
An unreliable channel — the messy reality networks must cope with.

A perfect wire would deliver every packet, intact and in order. Real networks do
no such thing: packets get **dropped** (lost entirely), **corrupted** (bits flip
in transit), delayed, or reordered. Any protocol that wants reliable delivery has
to be built on top of this unreliability — it can't wish it away.

This channel models the two failures that matter most for our protocol — loss
and corruption — with tunable probabilities and a seeded random generator so runs
are reproducible.
"""

import random
from typing import Optional

from packet import Packet


class UnreliableChannel:
    """Transmits packets, sometimes dropping or corrupting them."""

    def __init__(self, drop_prob: float = 0.0, corrupt_prob: float = 0.0,
                 seed: Optional[int] = None):
        self.drop_prob = drop_prob
        self.corrupt_prob = corrupt_prob
        self._rng = random.Random(seed)
        # Counters so callers can report what the channel did to their traffic.
        self.delivered = 0
        self.dropped = 0
        self.corrupted = 0

    def transmit(self, packet: Packet) -> Optional[Packet]:
        """
        Send one packet. Returns the packet that arrives (possibly corrupted),
        or None if it was dropped in transit. The original is never mutated —
        we damage a clone, just as a real network damages the copy on the wire.
        """
        if self._rng.random() < self.drop_prob:
            self.dropped += 1
            return None                    # lost: the receiver hears nothing

        arriving = packet.clone()
        if self._rng.random() < self.corrupt_prob:
            arriving.flip_bit()            # bits flipped in transit
            self.corrupted += 1
        self.delivered += 1
        return arriving
