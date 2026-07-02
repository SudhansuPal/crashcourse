"""
Unit tests for packets, checksums, the channel, and the reliable protocol.

Run from the repo root:

    pytest 12-networking/
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from packet import Packet, checksum  # noqa: E402
from channel import UnreliableChannel  # noqa: E402
from protocol import send_reliably, _split  # noqa: E402


# ---- checksum & packet ----------------------------------------------------

def test_checksum_deterministic():
    assert checksum(b"hello") == checksum(b"hello")


def test_checksum_changes_with_data():
    assert checksum(b"hello") != checksum(b"hellp")


def test_packet_valid_when_intact():
    p = Packet(3, "data", b"payload")
    assert p.is_valid()


def test_packet_detects_corruption():
    p = Packet(3, "data", b"payload")
    p.flip_bit()
    assert not p.is_valid()


def test_ack_corruption_detected():
    p = Packet(1, "ack")            # empty payload
    p.flip_bit()                    # corrupts the checksum field
    assert not p.is_valid()


def test_clone_preserves_sent_checksum():
    p = Packet(5, "data", b"abc")
    c = p.clone()
    assert c.is_valid() and c.checksum == p.checksum


# ---- channel --------------------------------------------------------------

def test_channel_perfect_delivers_intact():
    ch = UnreliableChannel(drop_prob=0.0, corrupt_prob=0.0, seed=1)
    p = Packet(0, "data", b"hi")
    got = ch.transmit(p)
    assert got is not None and got.is_valid()
    assert got.payload == b"hi"


def test_channel_always_drops():
    ch = UnreliableChannel(drop_prob=1.0, seed=1)
    assert ch.transmit(Packet(0, "data", b"x")) is None
    assert ch.dropped == 1


def test_channel_always_corrupts():
    ch = UnreliableChannel(drop_prob=0.0, corrupt_prob=1.0, seed=1)
    got = ch.transmit(Packet(0, "data", b"x"))
    assert got is not None and not got.is_valid()


def test_channel_does_not_mutate_original():
    ch = UnreliableChannel(corrupt_prob=1.0, seed=1)
    p = Packet(0, "data", b"abc")
    ch.transmit(p)
    assert p.is_valid()             # the original is untouched


# ---- reliable protocol ----------------------------------------------------

def test_split():
    assert _split(b"abcdef", 2) == [b"ab", b"cd", b"ef"]
    assert _split(b"abcde", 2) == [b"ab", b"cd", b"e"]
    assert _split(b"", 4) == [b""]


def test_perfect_channel_transfers_exactly():
    fwd = UnreliableChannel(seed=1)
    bwd = UnreliableChannel(seed=2)
    msg = b"hello, reliable world"
    received, stats = send_reliably(msg, fwd, bwd, chunk_size=4)
    assert received == msg
    assert stats["retransmissions"] == 0


@pytest.mark.parametrize("seed", range(15))
def test_lossy_channel_still_delivers(seed):
    """Across many random channels, the message must always arrive intact."""
    fwd = UnreliableChannel(drop_prob=0.3, corrupt_prob=0.2, seed=seed)
    bwd = UnreliableChannel(drop_prob=0.3, corrupt_prob=0.2, seed=seed + 100)
    msg = b"the network is unreliable but delivery is not"
    received, stats = send_reliably(msg, fwd, bwd, chunk_size=8)
    assert received == msg


def test_heavy_loss_requires_retransmissions():
    fwd = UnreliableChannel(drop_prob=0.5, corrupt_prob=0.2, seed=7)
    bwd = UnreliableChannel(drop_prob=0.5, corrupt_prob=0.2, seed=8)
    msg = b"lots of loss here"
    received, stats = send_reliably(msg, fwd, bwd, chunk_size=4)
    assert received == msg
    assert stats["retransmissions"] > 0        # loss forced resends
    assert stats["transmissions"] > stats["retransmissions"]


def test_no_duplicate_delivery():
    """A lost ACK causes a resend; the duplicate must not be delivered twice."""
    # Perfect forward, but the first ACK is dropped, forcing one retransmit.
    fwd = UnreliableChannel(seed=1)
    bwd = UnreliableChannel(drop_prob=0.4, seed=5)
    msg = b"abcdefgh"
    received, stats = send_reliably(msg, fwd, bwd, chunk_size=4)
    assert received == msg          # exactly the message, no doubled chunks


def test_empty_message():
    fwd = UnreliableChannel(seed=1)
    bwd = UnreliableChannel(seed=2)
    received, _ = send_reliably(b"", fwd, bwd)
    assert received == b""
