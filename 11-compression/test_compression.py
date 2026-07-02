"""
Unit tests for RLE and Huffman coding.

The central property of lossless compression is that decode(encode(x)) == x for
*every* input, so most tests are round-trip checks over varied and random data.

Run from the repo root:

    pytest 11-compression/
"""

import os
import random
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rle import rle_encode, rle_decode  # noqa: E402
from huffman import HuffmanCoder, pack_bits, unpack_bits  # noqa: E402


# ---- RLE ------------------------------------------------------------------

def test_rle_roundtrip_basic():
    data = b"AAAABBBCCD"
    assert rle_decode(rle_encode(data)) == data


def test_rle_compresses_runs():
    data = b"A" * 100
    encoded = rle_encode(data)
    assert len(encoded) < len(data)
    assert rle_decode(encoded) == data


def test_rle_run_longer_than_255_splits():
    data = b"X" * 300
    encoded = rle_encode(data)
    # 300 = 255 + 45 -> two pairs -> 4 bytes
    assert len(encoded) == 4
    assert rle_decode(encoded) == data


def test_rle_empty():
    assert rle_encode(b"") == b""
    assert rle_decode(b"") == b""


def test_rle_decode_rejects_odd_length():
    with pytest.raises(ValueError):
        rle_decode(b"\x03")


def test_rle_roundtrip_random():
    random.seed(11)
    for _ in range(200):
        n = random.randint(0, 100)
        # Bias toward repeats so we exercise runs.
        data = bytes(random.choice([65, 65, 66, random.randint(0, 255)])
                     for _ in range(n))
        assert rle_decode(rle_encode(data)) == data


# ---- Huffman --------------------------------------------------------------

def test_huffman_roundtrip_text():
    text = b"the quick brown fox jumps over the lazy dog"
    coder = HuffmanCoder.build(text)
    bits = coder.encode(text)
    assert coder.decode(bits) == text


def test_huffman_prefix_free_codes():
    text = b"abracadabra abracadabra"
    coder = HuffmanCoder.build(text)
    codes = list(coder.codes.values())
    # No code may be a prefix of another (what makes decoding unambiguous).
    for a in codes:
        for b in codes:
            if a is not b and len(a) < len(b):
                assert not b.startswith(a)


def test_huffman_frequent_symbol_not_longer_than_rare():
    # In "aaaaab", 'a' is far more frequent, so its code must be <= 'b' length.
    text = b"aaaaa b"
    coder = HuffmanCoder.build(text)
    assert len(coder.codes[ord("a")]) <= len(coder.codes[ord("b")])


def test_huffman_single_symbol():
    text = b"zzzzzz"
    coder = HuffmanCoder.build(text)
    bits = coder.encode(text)
    assert coder.decode(bits) == text
    assert coder.codes[ord("z")] == "0"       # single symbol -> 1-bit code


def test_huffman_empty():
    coder = HuffmanCoder.build(b"")
    assert coder.encode(b"") == ""
    assert coder.decode("") == b""


def test_huffman_actually_compresses_skewed_data():
    # Highly skewed distribution should beat 8 bits/symbol comfortably.
    text = b"a" * 900 + b"bcd" * 10
    coder = HuffmanCoder.build(text)
    bits = coder.encode(text)
    assert len(bits) < len(text) * 8


def test_pack_unpack_roundtrip():
    for bits in ["", "1", "101", "11111111", "1010101010101"]:
        packed, length = pack_bits(bits)
        assert unpack_bits(packed, length) == bits


def test_huffman_full_pipeline_random():
    """build -> encode -> pack -> unpack -> decode == original, on random data."""
    random.seed(12)
    for _ in range(100):
        n = random.randint(1, 200)
        # A restricted alphabet gives interesting (non-uniform) frequencies.
        data = bytes(random.choice(b"abcdeXYZ ") for _ in range(n))
        coder = HuffmanCoder.build(data)
        bits = coder.encode(data)
        packed, length = pack_bits(bits)
        assert coder.decode(unpack_bits(packed, length)) == data
