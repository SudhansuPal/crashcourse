"""
Runnable demonstration of run-length encoding and Huffman coding.

Run from the repo root:

    python 11-compression/demo.py

Shows RLE on run-heavy vs. run-poor data (and how it can backfire), then Huffman
coding on English text — printing the variable-length code table and the real
compression achieved.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rle import rle_encode, rle_decode  # noqa: E402
from huffman import HuffmanCoder, pack_bits, unpack_bits  # noqa: E402


def demo_rle() -> None:
    print("=" * 60)
    print("RUN-LENGTH ENCODING")
    print("=" * 60)
    runny = b"AAAAAAAAAABBBBBBWWWWWWWWWWWW"
    packed = rle_encode(runny)
    print(f"  run-heavy input : {runny!r}  ({len(runny)} bytes)")
    print(f"  encoded         : {packed!r}  ({len(packed)} bytes)")
    print(f"  round-trips ok  : {rle_decode(packed) == runny}")
    print(f"  -> compressed to {len(packed)/len(runny):.0%} of original\n")

    noisy = b"ABCDEFGHIJ"
    packed2 = rle_encode(noisy)
    print(f"  run-poor input  : {noisy!r}  ({len(noisy)} bytes)")
    print(f"  encoded         : {packed2!r}  ({len(packed2)} bytes)")
    print(f"  -> RLE EXPANDED it to {len(packed2)/len(noisy):.0%}: no free lunch")


def demo_huffman() -> None:
    print("\n" + "=" * 60)
    print("HUFFMAN CODING")
    print("=" * 60)
    text = (b"the quick brown fox jumps over the lazy dog. "
            b"the dog barks and the fox runs. eee aaa ooo the the the.")
    coder = HuffmanCoder.build(text)

    print("  Variable-length codes (frequent symbols get shorter codes):")
    # Show a few representative symbols sorted by code length.
    items = sorted(coder.codes.items(), key=lambda kv: (len(kv[1]), kv[1]))
    for sym, code in items[:4] + items[-3:]:
        ch = chr(sym)
        shown = "space" if ch == " " else repr(ch)
        print(f"    {shown:>7} -> {code}")

    bits = coder.encode(text)
    packed, bit_len = pack_bits(bits)

    original_bits = len(text) * 8
    print(f"\n  original : {len(text):>4} bytes = {original_bits} bits "
          f"(8 bits/symbol)")
    print(f"  huffman  : {len(bits):>4} bits = {len(packed)} packed bytes "
          f"({len(bits)/len(text):.2f} bits/symbol)")
    print(f"  -> {len(bits)/original_bits:.0%} of the original size "
          f"(code table not counted)")

    restored = coder.decode(unpack_bits(packed, bit_len))
    print(f"  lossless round-trip: {restored == text}")


if __name__ == "__main__":
    demo_rle()
    demo_huffman()
