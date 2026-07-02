"""
Unit tests for the assembler.

Run from the repo root:

    pytest 07-instructions/
"""

import os
import sys

import pytest

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.dirname(_HERE)
sys.path.insert(0, os.path.join(_REPO_ROOT, "06-cpu"))
sys.path.insert(0, _HERE)

from cpu import CPU, encode, LOADI, ADD, JMP, HALT  # noqa: E402
from assembler import assemble, assemble_file, AssemblyError  # noqa: E402


# ---- basic translation ----------------------------------------------------

def test_simple_program_bytes():
    code = assemble("LOADI 5\nOUT\nHALT")
    assert code == [encode(LOADI, 5), encode(0x8, 0), encode(HALT)]


def test_comments_and_blank_lines_ignored():
    src = """
        ; this is a comment
        LOADI 1     ; inline comment

        HALT
    """
    assert assemble(src) == [encode(LOADI, 1), encode(HALT)]


def test_hex_and_decimal_operands():
    # DB accepts full bytes; both notations should parse.
    assert assemble("DB 255") == [255]
    assert assemble("DB 0xFF") == [0xFF]
    assert assemble("LOADI 0x0F") == [encode(LOADI, 15)]


# ---- labels ---------------------------------------------------------------

def test_forward_and_backward_labels():
    src = """
            JMP start
    mid:    HALT
    start:  JMP mid
    """
    # addresses: JMP start ->0, mid: HALT ->1, start: JMP mid ->2
    code = assemble(src)
    assert code == [encode(JMP, 2), encode(HALT), encode(JMP, 1)]


def test_label_on_its_own_line():
    src = """
    top:
            JMP top
    """
    assert assemble(src) == [encode(JMP, 0)]


def test_data_label_resolves_to_address():
    src = """
            LOAD value
            HALT
    value:  DB 42
    """
    code = assemble(src)
    assert code[0] == encode(0x2, 2)   # LOAD from address 2
    assert code[2] == 42


# ---- error handling -------------------------------------------------------

def test_unknown_instruction():
    with pytest.raises(AssemblyError):
        assemble("FOO 1")


def test_unknown_label():
    with pytest.raises(AssemblyError):
        assemble("JMP nowhere\nHALT")


def test_duplicate_label():
    with pytest.raises(AssemblyError):
        assemble("x: HALT\nx: HALT")


def test_operand_out_of_range():
    with pytest.raises(AssemblyError):
        assemble("LOADI 16")   # only 0..15 fit in the operand nibble


def test_missing_operand():
    with pytest.raises(AssemblyError):
        assemble("ADD")


def test_operand_on_operandless_instruction():
    with pytest.raises(AssemblyError):
        assemble("HALT 3")


def test_program_too_large():
    with pytest.raises(AssemblyError):
        assemble("\n".join(["HALT"] * 17))


# ---- end to end: assemble the shipped programs and run them ---------------

def test_sum_program_runs_to_15():
    code = assemble_file(os.path.join(_HERE, "programs", "sum.asm"))
    cpu = CPU(code)
    cpu.run()
    assert cpu.memory_dump()[15] == 15


def test_countdown_program_output():
    code = assemble_file(os.path.join(_HERE, "programs", "countdown.asm"))
    cpu = CPU(code)
    cpu.run()
    assert cpu.output == [3, 2, 1]


def test_assembled_sum_matches_hand_encoding():
    """The assembler must reproduce module 06's hand-built bytes exactly."""
    code = assemble_file(os.path.join(_HERE, "programs", "sum.asm"))
    NEG1, I, SUM = 13, 14, 15
    hand = [
        encode(LOADI, 5), encode(0x3, I),
        encode(LOADI, 0), encode(0x3, SUM),
        encode(0x2, SUM), encode(ADD, I), encode(0x3, SUM),
        encode(0x2, I), encode(ADD, NEG1), encode(0x3, I),
        encode(JZ := 0x7, 12), encode(JMP, 4), encode(HALT),
        0xFF, 0x00, 0x00,
    ]
    assert code == hand
