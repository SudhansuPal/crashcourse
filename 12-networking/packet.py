"""
Packets and checksums — the envelope data travels in, and how we detect damage.

Networks don't send "a message"; they send **packets** — small, self-contained
chunks, each labeled with enough information to be routed, ordered, and checked.
Our packet carries four things:

    seq      : a sequence number, so the receiver can order packets and spot
               duplicates (crucial when we retransmit lost ones)
    kind     : "data" or "ack" (acknowledgement)
    payload  : the actual bytes being carried
    checksum : a small number computed from the other fields, used to detect
               corruption in transit

The **checksum** is the key idea here. Wires and radios are noisy; bits flip. The
sender computes a checksum over the packet's contents and includes it. The
receiver recomputes it from what arrived: if the two disagree, the packet was
corrupted and must be discarded. We implement the classic "Internet checksum" (a
16-bit one's-complement sum), the same family used by IP, TCP, and UDP.
"""

from typing import List


def checksum(data: bytes) -> int:
    """
    The Internet checksum: a 16-bit one's-complement sum of 16-bit words.

    Add up the data two bytes at a time, folding any overflow (carry) back into
    the low 16 bits, then take the one's complement (bitwise NOT). It's cheap to
    compute and catches the great majority of real-world bit errors.
    """
    if len(data) % 2 == 1:
        data = data + b"\x00"              # pad to a whole number of 16-bit words
    total = 0
    for i in range(0, len(data), 2):
        word = (data[i] << 8) | data[i + 1]
        total += word
        total = (total & 0xFFFF) + (total >> 16)   # fold carries back in
    return (~total) & 0xFFFF               # one's complement, kept to 16 bits


class Packet:
    """A network packet with a self-describing checksum."""

    def __init__(self, seq: int, kind: str, payload: bytes = b""):
        assert kind in ("data", "ack")
        self.seq = seq
        self.kind = kind
        self.payload = payload
        self.checksum = self._compute_checksum()
        self.corrupted = False            # a flag the channel sets for reporting

    def _fields_bytes(self) -> bytes:
        """The bytes the checksum is computed over: seq, kind, and payload."""
        return bytes([self.seq & 0xFF]) + self.kind.encode() + self.payload

    def _compute_checksum(self) -> int:
        return checksum(self._fields_bytes())

    def is_valid(self) -> bool:
        """Recompute the checksum and compare — did this packet arrive intact?"""
        return self._compute_checksum() == self.checksum

    def clone(self) -> "Packet":
        """A deep-ish copy, so the channel can damage a copy in flight."""
        p = Packet(self.seq, self.kind, self.payload)
        p.checksum = self.checksum        # preserve the *sent* checksum exactly
        return p

    def flip_bit(self) -> None:
        """
        Simulate corruption: flip one bit of the payload (or the checksum if the
        payload is empty, as with an ACK). Leaves the stored checksum in place,
        so is_valid() will now fail — exactly what a real bit error looks like.
        """
        if self.payload:
            data = bytearray(self.payload)
            data[0] ^= 0x01               # flip the low bit of the first byte
            self.payload = bytes(data)
        else:
            self.checksum ^= 0x01         # corrupt the checksum field instead
        self.corrupted = True

    def __repr__(self) -> str:
        body = self.payload if self.kind == "data" else b""
        return f"Packet(seq={self.seq}, {self.kind}, payload={body!r})"
