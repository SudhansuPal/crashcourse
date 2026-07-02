"""
Unit tests for latches, registers, the address decoder, and RAM.

Run from the repo root:

    pytest 05-registers-memory/
"""

import os
import sys

import pytest

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_REPO_ROOT, "03-binary-arithmetic"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from binary import int_to_bits, bits_to_int  # noqa: E402
from latch import DLatch  # noqa: E402
from memory import Register, RAM, address_decoder  # noqa: E402


# ---- D latch --------------------------------------------------------------

def test_latch_stores_when_enabled():
    latch = DLatch(0)
    assert latch.step(1, 1) == 1
    assert latch.step(0, 1) == 0


def test_latch_holds_when_disabled():
    latch = DLatch(0)
    latch.step(1, 1)                 # store 1
    assert latch.step(0, 0) == 1     # D=0 ignored, holds 1
    assert latch.step(1, 0) == 1     # still holding
    assert latch.step(0, 1) == 0     # now updates


def test_latch_output_and_complement_consistent():
    latch = DLatch(0)
    for d in (1, 0, 1, 1, 0):
        latch.step(d, 1)
        assert latch.q_bar == (0 if latch.q == 1 else 1)


# ---- register -------------------------------------------------------------

def test_register_write_read_roundtrip():
    reg = Register(8)
    for v in (0, 1, 42, 200, 255):
        reg.write(int_to_bits(v, 8), enable=1)
        assert bits_to_int(reg.read()) == v


def test_register_holds_when_disabled():
    reg = Register(8)
    reg.write(int_to_bits(42, 8), enable=1)
    reg.write(int_to_bits(99, 8), enable=0)  # ignored
    assert bits_to_int(reg.read()) == 42


def test_register_width_mismatch():
    reg = Register(8)
    with pytest.raises(ValueError):
        reg.write([1, 0, 1], enable=1)


# ---- address decoder ------------------------------------------------------

def test_decoder_is_one_hot():
    for a in range(4):
        lines = address_decoder(int_to_bits(a, 2))
        assert sum(lines) == 1          # exactly one line high
        assert lines[a] == 1            # the correct one


def test_decoder_3bit_all_addresses():
    for a in range(8):
        lines = address_decoder(int_to_bits(a, 3))
        assert lines[a] == 1
        assert sum(lines) == 1


# ---- RAM ------------------------------------------------------------------

def test_ram_write_read_all_words():
    ram = RAM(num_words=4, width=8)
    values = {0: 11, 1: 22, 2: 33, 3: 44}
    for addr, val in values.items():
        ram.write(int_to_bits(addr, 2), int_to_bits(val, 8))
    for addr, val in values.items():
        assert bits_to_int(ram.read(int_to_bits(addr, 2))) == val


def test_ram_write_enable_low_is_noop():
    ram = RAM(num_words=4, width=8)
    ram.write(int_to_bits(1, 2), int_to_bits(50, 8), write_enable=1)
    ram.write(int_to_bits(1, 2), int_to_bits(77, 8), write_enable=0)  # ignored
    assert bits_to_int(ram.read(int_to_bits(1, 2))) == 50


def test_ram_writes_are_isolated():
    """Writing one address must not disturb the others."""
    ram = RAM(num_words=8, width=8)
    for addr in range(8):
        ram.write(int_to_bits(addr, 3), int_to_bits(addr * 10, 8))
    # overwrite one word
    ram.write(int_to_bits(3, 3), int_to_bits(200, 8))
    for addr in range(8):
        expected = 200 if addr == 3 else addr * 10
        assert bits_to_int(ram.read(int_to_bits(addr, 3))) == expected


def test_ram_requires_power_of_two():
    with pytest.raises(ValueError):
        RAM(num_words=5, width=8)


def test_ram_address_width_checked():
    ram = RAM(num_words=4, width=8)
    with pytest.raises(ValueError):
        ram.read([1, 0, 1])  # 3 bits for a 2-bit address space
