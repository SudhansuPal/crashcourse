"""
An assembler: the bridge from human-readable code to machine code.

In module 06 we hand-encoded instructions as raw bytes like 0x4E and had to
count memory addresses by hand to know where to jump. That's how the first
programmers worked — and it's miserable and error-prone. An **assembler** fixes
this: it lets us write instructions with names (`ADD I`) and use **labels**
(`loop:`, `done:`) instead of numeric addresses, then it translates that text
into the exact bytes the CPU from module 06 executes.

This is the boundary between hardware and software. Below it: gates, wires, a
control unit. Above it: language, ever more expressive, all the way up to Python.
The assembler is the very first rung of that ladder.

How it works: two passes
------------------------
The tricky part is a *forward reference* — `JMP loop` when `loop:` is defined
later, or `ADD SUM` when `SUM:` hasn't appeared yet. The classic fix is two
passes over the source:

    Pass 1: walk the program counting one word per instruction/data item, and
            record the address of every label in a symbol table.
    Pass 2: walk again and emit bytes, now able to look up any label's address.

The output is a list of byte values ready to load into the CPU's memory.
"""

import os
import sys
from typing import Dict, List, Tuple

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_REPO_ROOT, "06-cpu"))

from cpu import (  # noqa: E402
    encode, HALT, LOADI, LOAD, STORE, ADD, SUB, JMP, JZ, OUT, MEM_WORDS,
)

# Mnemonic -> (opcode, takes_an_operand?). This defines the assembly language.
MNEMONICS: Dict[str, Tuple[int, bool]] = {
    "LOADI": (LOADI, True),
    "LOAD": (LOAD, True),
    "STORE": (STORE, True),
    "ADD": (ADD, True),
    "SUB": (SUB, True),
    "JMP": (JMP, True),
    "JZ": (JZ, True),
    "OUT": (OUT, False),
    "HALT": (HALT, False),
}

# A pseudo-instruction that places a raw data byte in memory (not executed as
# code unless the program flows into it). Handy for constants and variables.
DATA_DIRECTIVE = "DB"


class AssemblyError(Exception):
    """Raised for any problem in the assembly source, with a line number."""


def _strip_comment(line: str) -> str:
    """Everything after a ';' is a comment."""
    return line.split(";", 1)[0].rstrip()


def _parse_int(token: str, lineno: int) -> int:
    """Parse a numeric literal: decimal (42) or hex (0x2A)."""
    try:
        return int(token, 0)  # base 0 auto-detects 0x / 0o / 0b / decimal
    except ValueError:
        raise AssemblyError(f"line {lineno}: '{token}' is not a number or "
                            f"known label")


def _tokenize(source: str) -> List[Tuple[int, str, List[str]]]:
    """
    First lexing stage: return (lineno, label_or_None, [tokens]) for each
    meaningful line, splitting off any leading `label:`.
    """
    parsed = []
    for lineno, raw in enumerate(source.splitlines(), start=1):
        line = _strip_comment(raw).strip()
        if not line:
            continue

        label = None
        # A label is a name ending in ':' at the start of the line. There may or
        # may not be an instruction after it on the same line.
        if ":" in line:
            name, _, rest = line.partition(":")
            label = name.strip()
            if not label.isidentifier():
                raise AssemblyError(f"line {lineno}: invalid label '{label}'")
            line = rest.strip()

        tokens = line.split() if line else []
        parsed.append((lineno, label, tokens))
    return parsed


def assemble(source: str) -> List[int]:
    """
    Translate assembly source text into a list of machine-code byte values.

    Two passes: first resolve every label to an address, then emit bytes.
    """
    lines = _tokenize(source)

    # --- Pass 1: assign an address to each item and record labels. ---
    symbols: Dict[str, int] = {}
    address = 0
    # We keep the "items" (lines that actually produce a word) for pass 2.
    items: List[Tuple[int, List[str]]] = []
    for lineno, label, tokens in lines:
        if label is not None:
            if label in symbols:
                raise AssemblyError(f"line {lineno}: duplicate label '{label}'")
            symbols[label] = address
        if not tokens:
            continue  # a label on its own line — points at the next item
        items.append((lineno, tokens))
        address += 1  # every instruction and every DB occupies exactly one word

    if address > MEM_WORDS:
        raise AssemblyError(f"program needs {address} words but memory has "
                            f"only {MEM_WORDS}")

    # --- Pass 2: emit bytes, resolving operands (numbers or labels). ---
    machine_code: List[int] = []
    for lineno, tokens in items:
        mnemonic = tokens[0].upper()

        if mnemonic == DATA_DIRECTIVE:
            if len(tokens) != 2:
                raise AssemblyError(f"line {lineno}: DB needs exactly one value")
            value = _resolve(tokens[1], symbols, lineno)
            if not (0 <= value <= 0xFF):
                raise AssemblyError(f"line {lineno}: DB value {value} out of "
                                    f"byte range 0..255")
            machine_code.append(value)
            continue

        if mnemonic not in MNEMONICS:
            raise AssemblyError(f"line {lineno}: unknown instruction "
                                f"'{tokens[0]}'")
        opcode, takes_operand = MNEMONICS[mnemonic]

        if takes_operand:
            if len(tokens) != 2:
                raise AssemblyError(f"line {lineno}: {mnemonic} needs an operand")
            operand = _resolve(tokens[1], symbols, lineno)
            if not (0 <= operand <= 0xF):
                raise AssemblyError(f"line {lineno}: operand {operand} does not "
                                    f"fit in 4 bits (0..15)")
        else:
            if len(tokens) != 1:
                raise AssemblyError(f"line {lineno}: {mnemonic} takes no operand")
            operand = 0

        machine_code.append(encode(opcode, operand))

    return machine_code


def _resolve(token: str, symbols: Dict[str, int], lineno: int) -> int:
    """An operand is either a known label or a numeric literal."""
    if token in symbols:
        return symbols[token]
    return _parse_int(token, lineno)


def assemble_file(path: str) -> List[int]:
    """Convenience: read a .asm file and assemble it."""
    with open(path, "r") as f:
        return assemble(f.read())
