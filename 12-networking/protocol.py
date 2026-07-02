"""
Reliable delivery over an unreliable channel — the heart of TCP, in miniature.

Given a channel that drops and corrupts packets (channel.py), how do you deliver
a message perfectly and in order? The answer is a **stop-and-wait ARQ** protocol
(Automatic Repeat reQuest), the essential mechanism underneath TCP:

    - The sender sends one data packet and waits for an ACK before sending the
      next.
    - The receiver checks each packet's checksum. If it's intact and the one it
      expected, it hands the payload up and ACKs it. Corrupt packets are simply
      dropped (stay silent).
    - If the sender doesn't get a valid ACK (because the data or the ACK was lost
      or corrupted), it **times out and retransmits**.
    - **Sequence numbers** let the receiver recognize a retransmitted duplicate
      (an ACK that got lost, so the sender resent) and avoid delivering it twice
      — while still re-ACKing it so the sender can move on.

Put together, these four ideas — checksums, acknowledgements, timeouts/
retransmission, and sequence numbers — turn a lossy channel into a reliable one.
That's the whole trick, and it's what lets this file arrive on your screen intact.
"""

from typing import Dict, List, Tuple

from channel import UnreliableChannel
from packet import Packet


def send_reliably(
    message: bytes,
    forward: UnreliableChannel,
    backward: UnreliableChannel,
    chunk_size: int = 8,
    max_transmissions: int = 10_000,
) -> Tuple[bytes, Dict[str, int]]:
    """
    Reliably transfer `message` across two unreliable channels (data goes over
    `forward`, ACKs come back over `backward`). Returns the bytes the receiver
    reconstructed (which will equal `message`) and a stats dictionary.

    We model sender and receiver in one loop for clarity: each iteration is one
    send attempt and, if the data arrives intact, one ACK attempt.
    """
    chunks = _split(message, chunk_size)
    received = bytearray()
    expected_seq = 0                       # the next in-order chunk the receiver wants

    stats = {"transmissions": 0, "retransmissions": 0,
             "data_dropped": 0, "data_corrupted": 0,
             "ack_dropped": 0, "ack_corrupted": 0}

    for index, chunk in enumerate(chunks):
        seq = index
        acked = False
        attempt = 0
        while not acked:
            attempt += 1
            stats["transmissions"] += 1
            if attempt > 1:
                stats["retransmissions"] += 1
            if stats["transmissions"] > max_transmissions:
                raise RuntimeError("gave up: too many transmissions")

            # --- Sender -> forward channel -> Receiver ---
            arrived = forward.transmit(Packet(seq, "data", chunk))
            if arrived is None:
                stats["data_dropped"] += 1
                continue                   # lost data: timeout, resend
            if not arrived.is_valid():
                stats["data_corrupted"] += 1
                continue                   # corrupt data: receiver stays silent -> resend

            # --- Receiver logic ---
            if arrived.seq == expected_seq:
                received.extend(arrived.payload)   # new, in-order: deliver once
                expected_seq += 1
            # else: a duplicate (its seq < expected). Don't deliver again, but do
            # ACK it below so the sender learns it got through.

            # --- Receiver -> backward channel -> Sender (the ACK) ---
            ack_back = backward.transmit(Packet(arrived.seq, "ack"))
            if ack_back is None:
                stats["ack_dropped"] += 1
                continue                   # lost ACK: sender times out, resends
            if not ack_back.is_valid():
                stats["ack_corrupted"] += 1
                continue                   # corrupt ACK: ignore, resend
            if ack_back.seq == seq:
                acked = True               # confirmed! move to the next chunk

    return bytes(received), stats


def _split(data: bytes, chunk_size: int) -> List[bytes]:
    """Break a message into fixed-size chunks (the last may be shorter)."""
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    return [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)] or [b""]
