# 12 — Networking

The internet is built on an uncomfortable truth: the underlying network is
**unreliable**. Packets get lost, bits flip, order scrambles. Yet somehow this
page arrives on your screen byte-for-byte correct. This module builds the
machinery that performs that magic — **packets**, a **checksum**, and a
**reliable delivery protocol** — and runs it over a deliberately hostile channel
to prove it works.

## The concept in plain language

Data doesn't travel as one big stream; it travels as **packets** — small chunks,
each labeled so it can be checked and ordered. Reliable delivery over an
unreliable network rests on four ideas working together:

1. **Checksum** — a small number computed from a packet's contents. The receiver
   recomputes it; if it doesn't match, the packet was corrupted in transit and is
   thrown away. We use the classic **Internet checksum** (a 16-bit one's-
   complement sum), the same family IP/TCP/UDP use.
2. **Acknowledgements (ACKs)** — the receiver tells the sender "got it."
3. **Timeouts & retransmission** — if no valid ACK comes back (the data *or* the
   ACK was lost/corrupted), the sender resends.
4. **Sequence numbers** — so the receiver can tell a fresh packet from a
   **retransmitted duplicate** and never deliver the same data twice.

Together these turn a lossy channel into a reliable one. This is the essence of
**TCP**, distilled to a stop-and-wait protocol.

## Why it matters

This is one of computing's most important ideas: **reliability is a property you
build, not one you're given.** The network makes no promises, so the endpoints
make the promises instead — with checksums, ACKs, and retransmission. Every file
download, message, and video call rides on this bargain. The demo makes the cost
visible too: reliability isn't free, it's *paid for* in retransmissions, which is
exactly why a bad connection feels slow rather than simply broken.

## How the code demonstrates it

- **[`packet.py`](packet.py)** — the `Packet` (seq, kind, payload, checksum) and
  the Internet `checksum`. `is_valid()` recomputes the checksum to detect
  damage; `flip_bit()` simulates a bit error in transit.
- **[`channel.py`](channel.py)** — an `UnreliableChannel` that drops and corrupts
  packets with tunable probabilities (seeded for reproducibility). It damages a
  *clone*, never the caller's original — just like a real wire.
- **[`protocol.py`](protocol.py)** — `send_reliably` implements stop-and-wait
  ARQ: send a chunk, wait for its ACK, retransmit on loss/corruption, and use
  sequence numbers to drop duplicates while still re-ACKing them. It returns the
  reconstructed message and detailed stats.

The demo sends a 52-byte message over a channel dropping 30% and corrupting 15%
of packets *each way*. It reconstructs the message **perfectly**, and reports the
damage the protocol had to route around (e.g. ~7 chunks needing ~21
transmissions). The tests hammer it with 15 different random channels and confirm
intact delivery every time, plus that lost ACKs never cause duplicate delivery.

## Run it

```bash
# from the repo root

# checksum detection, then reliable transfer over a lossy channel
python 12-networking/demo.py

# run the tests
pytest 12-networking/
```

## Files

- `packet.py` — packets and the Internet checksum.
- `channel.py` — the drop/corrupt unreliable channel.
- `protocol.py` — stop-and-wait reliable delivery with ACKs, retransmission, and
  sequence numbers.
- `demo.py` — corruption detection and a reliable transfer with stats.
- `test_networking.py` — checksum/packet/channel behavior and reliable delivery
  across many random lossy channels (including no-duplicate-delivery).

## What's next

**Module 13 — cryptography**: how do you keep a message *secret* and verify *who
sent it*? We climb from the Caesar and Vigenère ciphers through XOR to the
breakthrough of public-key cryptography — Diffie–Hellman key exchange and a toy
RSA — built from the number theory up.
