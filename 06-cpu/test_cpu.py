"""
Unit tests for the CPU: individual instructions and whole programs.

Run from the repo root:

    pytest 06-cpu/
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cpu import (  # noqa: E402
    CPU, encode,
    HALT, LOADI, LOAD, STORE, ADD, SUB, JMP, JZ, OUT,
)


def run(program):
    cpu = CPU(program)
    cpu.run()
    return cpu


# ---- single instructions --------------------------------------------------

def test_loadi_and_out():
    cpu = run([encode(LOADI, 7), encode(OUT), encode(HALT)])
    assert cpu.output == [7]


def test_store_and_load():
    cpu = run([
        encode(LOADI, 9),
        encode(STORE, 15),
        encode(LOADI, 0),   # clobber the accumulator
        encode(LOAD, 15),   # read it back
        encode(OUT),
        encode(HALT),
    ])
    assert cpu.output == [9]


def test_add():
    cpu = run([
        encode(LOADI, 6),
        encode(STORE, 15),
        encode(LOADI, 4),
        encode(ADD, 15),    # 4 + 6
        encode(OUT),
        encode(HALT),
    ])
    assert cpu.output == [10]


def test_sub():
    cpu = run([
        encode(LOADI, 3),
        encode(STORE, 15),
        encode(LOADI, 9),
        encode(SUB, 15),    # 9 - 3
        encode(OUT),
        encode(HALT),
    ])
    assert cpu.output == [6]


def test_sub_sets_zero_flag():
    cpu = run([
        encode(LOADI, 5),
        encode(STORE, 15),
        encode(LOADI, 5),
        encode(SUB, 15),    # 5 - 5 = 0
        encode(HALT),
    ])
    assert cpu.zero_flag == 1


def test_add_clears_zero_flag_when_nonzero():
    cpu = run([
        encode(LOADI, 1),
        encode(STORE, 15),
        encode(LOADI, 2),
        encode(ADD, 15),    # 3, not zero
        encode(HALT),
    ])
    assert cpu.zero_flag == 0


# ---- control flow ---------------------------------------------------------

def test_jmp_skips_instructions():
    cpu = run([
        encode(JMP, 3),
        encode(LOADI, 1),   # skipped
        encode(OUT),        # skipped
        encode(LOADI, 8),   # jump lands here
        encode(OUT),
        encode(HALT),
    ])
    assert cpu.output == [8]


def test_jz_taken_and_not_taken():
    # zero flag set -> jump taken
    taken = run([
        encode(LOADI, 4),
        encode(STORE, 15),
        encode(LOADI, 4),
        encode(SUB, 15),    # 0 -> zero flag set
        encode(JZ, 7),
        encode(LOADI, 1),   # skipped
        encode(OUT),        # skipped
        encode(LOADI, 9),   # jump lands here
        encode(OUT),
        encode(HALT),
    ])
    assert taken.output == [9]

    # zero flag clear -> fall through
    not_taken = run([
        encode(LOADI, 1),
        encode(STORE, 15),
        encode(LOADI, 3),
        encode(SUB, 15),    # 2 -> zero flag clear
        encode(JZ, 8),
        encode(OUT),        # executed (A = 2)
        encode(HALT),
    ])
    assert not_taken.output == [2]


# ---- a whole program ------------------------------------------------------

def test_sum_1_to_5_loop():
    NEG1, I, SUM = 13, 14, 15
    program = [
        encode(LOADI, 5), encode(STORE, I),
        encode(LOADI, 0), encode(STORE, SUM),
        encode(LOAD, SUM), encode(ADD, I), encode(STORE, SUM),
        encode(LOAD, I), encode(ADD, NEG1), encode(STORE, I),
        encode(JZ, 12), encode(JMP, 4), encode(HALT),
        0xFF, 0x00, 0x00,
    ]
    cpu = run(program)
    assert cpu.memory_dump()[SUM] == 15


def test_countdown_emits_each_value():
    # Count down from 3 to 1, printing each. Uses OUT inside a loop.
    NEG1, N = 14, 15
    program = [
        encode(LOADI, 3),   # 0  A = 3
        encode(STORE, N),   # 1  N = 3
        encode(LOAD, N),    # 2  loop: A = N
        encode(OUT),        # 3  print A
        encode(ADD, NEG1),  # 4  A = N - 1
        encode(STORE, N),   # 5  N = A
        encode(JZ, 8),      # 6  if 0, done
        encode(JMP, 2),     # 7  loop
        encode(HALT),       # 8
        0, 0, 0, 0, 0,
        0xFF,               # 14 constant -1
        0x00,               # 15 N
    ]
    cpu = run(program)
    assert cpu.output == [3, 2, 1]


# ---- machinery ------------------------------------------------------------

def test_encode_packs_nibbles():
    assert encode(ADD, 14) == 0x4E
    assert encode(HALT) == 0x00


def test_encode_rejects_overflow():
    with pytest.raises(ValueError):
        encode(0x10, 0)
    with pytest.raises(ValueError):
        encode(ADD, 16)


def test_runaway_program_is_caught():
    # An infinite loop with no HALT must hit the safety limit.
    cpu = CPU([encode(JMP, 0)])
    with pytest.raises(RuntimeError):
        cpu.run(max_cycles=50)


def test_program_too_big():
    with pytest.raises(ValueError):
        CPU([0] * 17)  # only 16 words of memory
