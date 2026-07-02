"""
Runnable demonstration of packets, checksums, and reliable delivery.

Run from the repo root:

    python 12-networking/demo.py

Shows a checksum catching corruption, then sends a message across a channel that
drops and corrupts ~30% of packets — and reconstructs it perfectly, reporting how
many retransmissions that reliability cost.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from packet import Packet, checksum  # noqa: E402
from channel import UnreliableChannel  # noqa: E402
from protocol import send_reliably  # noqa: E402


def demo_checksum() -> None:
    print("=" * 60)
    print("CHECKSUM  (detecting corruption)")
    print("=" * 60)
    p = Packet(0, "data", b"hello world")
    print(f"  packet     : {p}")
    print(f"  checksum   : {p.checksum:#06x}")
    print(f"  is_valid   : {p.is_valid()}   (intact)")
    p.flip_bit()   # simulate a bit flipping in transit
    print(f"  after 1 bit flips in transit:")
    print(f"  is_valid   : {p.is_valid()}   (corruption detected!)")


def demo_reliable_transfer() -> None:
    print("\n" + "=" * 60)
    print("RELIABLE DELIVERY over a lossy, corrupting channel")
    print("=" * 60)
    message = b"Networking: reliable delivery from unreliable parts."
    forward = UnreliableChannel(drop_prob=0.3, corrupt_prob=0.15, seed=42)
    backward = UnreliableChannel(drop_prob=0.3, corrupt_prob=0.15, seed=99)

    print(f"  message ({len(message)} bytes): {message!r}")
    print(f"  channel: 30% drop, 15% corrupt (each direction)\n")

    received, stats = send_reliably(message, forward, backward, chunk_size=8)

    n_chunks = (len(message) + 7) // 8
    print(f"  chunks to deliver : {n_chunks}")
    print(f"  total transmissions: {stats['transmissions']}  "
          f"(of which {stats['retransmissions']} were retransmissions)")
    print(f"  data lost/corrupt  : {stats['data_dropped']} dropped, "
          f"{stats['data_corrupted']} corrupted")
    print(f"  acks lost/corrupt  : {stats['ack_dropped']} dropped, "
          f"{stats['ack_corrupted']} corrupted")
    print()
    print(f"  received: {received!r}")
    print(f"  PERFECT RECONSTRUCTION: {received == message}")
    print("\n  Despite losing/corrupting many packets, the message arrived")
    print("  intact — bought with retransmissions. That's the TCP bargain.")


if __name__ == "__main__":
    demo_checksum()
    demo_reliable_transfer()
