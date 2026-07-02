# 11 — Compression

How do you make data smaller without throwing any of it away? **Lossless
compression** exploits the fact that real data is rarely random — it has
patterns and skewed frequencies — and encodes those regularities more compactly.
This module builds the two foundational techniques from scratch: **run-length
encoding** and **Huffman coding**, the ideas behind ZIP, PNG, JPEG, and more.

## The concept in plain language

**Run-length encoding (RLE)** replaces a "run" of one repeated value with a
single copy plus a count: `AAAAAAAAAA` → `10 A`. It's brilliant on data with long
runs (icons, simple graphics, fax pages) and — instructively — *counterproductive*
on data without them, since each lone byte now costs a count byte too.

**Huffman coding** attacks a different redundancy: not every symbol is equally
common. In English, space and `e` appear constantly; `q` and `z` rarely. Instead
of giving every symbol the same 8 bits, Huffman gives **frequent symbols short
codes and rare symbols long codes**, so the total shrinks. It builds these codes
by repeatedly merging the two least-frequent symbols into a tree; frequent
symbols end up near the root (short codes), rare ones end up deep (long codes).
The codes are **prefix-free** (no code is a prefix of another), which makes
decoding unambiguous — you walk the tree bit by bit and always know when a symbol
ends.

## Why it matters

Compression is everywhere: it makes the web fast, storage cheap, and streaming
possible. These two algorithms are the bedrock — Huffman coding is literally a
stage inside DEFLATE (ZIP, gzip, PNG) and JPEG. Just as important is the *lesson*
the demo drives home: **no compressor can shrink every input.** RLE visibly
doubles run-poor data. That's not a bug; it's a mathematical inevitability
(there are more possible long messages than short ones, so something must get
bigger). Understanding *why* compression works — and when it can't — is the point.

## How the code demonstrates it

- **[`rle.py`](rle.py)** — `rle_encode`/`rle_decode` over `(count, value)` pairs,
  with counts capped at 255 so long runs split cleanly. The demo shows it
  compressing to 21% on run-heavy input and *expanding* to 200% on run-poor
  input.
- **[`huffman.py`](huffman.py)** — the full pipeline from scratch:
  - count byte frequencies,
  - build the Huffman tree by **repeated minimum-extraction** (a transparent,
    from-scratch stand-in for a priority queue — no `heapq`, no compression lib),
  - assign each leaf a code from its root-to-leaf path,
  - `encode`/`decode` (decoding by walking the tree), plus `pack_bits`/
    `unpack_bits` to turn the bit-string into real bytes so the *true* size can
    be measured. Edge cases (empty input, a single distinct symbol) are handled.

The demo prints the variable-length code table (space → `00`, rare letters → 7
bits) and reports Huffman getting English text down to **~4.16 bits/symbol**,
about half the original — and confirms a lossless round-trip.

## Run it

```bash
# from the repo root

# RLE (win and loss) and Huffman on English text with the code table
python 11-compression/demo.py

# run the tests
pytest 11-compression/
```

## Files

- `rle.py` — run-length encode/decode.
- `huffman.py` — frequency counting, tree building, code assignment, encode/
  decode, and bit-packing helpers.
- `demo.py` — RLE on run-heavy vs run-poor data; Huffman on text with the code
  table and measured compression.
- `test_compression.py` — round-trip correctness over random data, prefix-free
  code checks, frequency/length relationship, and edge cases.

## What's next

**Module 12 — networking**: how does data travel reliably across an unreliable
network? We build **packets**, a **checksum** for detecting corruption, and a
tiny simulation of the acknowledgement/retransmission dance that protocols like
TCP use to deliver data intact over a lossy channel.
