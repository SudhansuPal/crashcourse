"""
Runnable demonstration of latches, registers, and RAM.

Run from the repo root:

    python 05-registers-memory/demo.py

Shows a D latch holding and updating a bit, a register storing a number, an
address decoder producing one-hot lines, and a small RAM being written and read.
"""

import os
import sys

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_REPO_ROOT, "03-binary-arithmetic"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from binary import int_to_bits, bits_to_int, format_bits  # noqa: E402
from latch import DLatch  # noqa: E402
from memory import Register, RAM, address_decoder  # noqa: E402


def show_latch() -> None:
    print("=" * 58)
    print("D LATCH  (E=1 stores D; E=0 holds)")
    print("=" * 58)
    latch = DLatch(0)
    print("  step  D  E | stored Q   note")
    print("  ----------+---------------------")
    script = [(1, 1, "store 1"), (0, 0, "hold (ignore D=0)"),
              (1, 0, "hold (ignore D=1)"), (0, 1, "store 0"),
              (1, 1, "store 1"), (1, 0, "hold")]
    for i, (d, e, note) in enumerate(script):
        q = latch.step(d, e)
        print(f"   {i:2}   {d}  {e} |    {q}       {note}")


def show_register() -> None:
    print("\n" + "=" * 58)
    print("REGISTER  (8-bit; a bank of latches with one enable)")
    print("=" * 58)
    reg = Register(8)
    print(f"  initial            -> {format_bits(reg.read())} "
          f"({bits_to_int(reg.read())})")
    reg.write(int_to_bits(42, 8), enable=1)
    print(f"  write 42, E=1      -> {format_bits(reg.read())} "
          f"({bits_to_int(reg.read())})")
    reg.write(int_to_bits(99, 8), enable=0)
    print(f"  write 99, E=0 (no) -> {format_bits(reg.read())} "
          f"({bits_to_int(reg.read())})   [held]")
    reg.write(int_to_bits(99, 8), enable=1)
    print(f"  write 99, E=1      -> {format_bits(reg.read())} "
          f"({bits_to_int(reg.read())})")


def show_decoder() -> None:
    print("\n" + "=" * 58)
    print("ADDRESS DECODER  (2-bit address -> 4 one-hot lines)")
    print("=" * 58)
    print("  addr | select lines (word0 word1 word2 word3)")
    print("  -----+---------------------------------------")
    for a in range(4):
        bits = int_to_bits(a, 2)
        lines = address_decoder(bits)
        print(f"   {format_bits(bits)}  |   {'    '.join(str(x) for x in lines)}")


def show_ram() -> None:
    print("\n" + "=" * 58)
    print("RAM  (4 words x 8 bits): write values, then read them back")
    print("=" * 58)
    ram = RAM(num_words=4, width=8)
    data = {0: 11, 1: 22, 2: 33, 3: 44}
    for addr, val in data.items():
        ram.write(int_to_bits(addr, 2), int_to_bits(val, 8), write_enable=1)
        print(f"  write addr {addr} <- {val}")
    print("  read back:")
    for addr in range(4):
        out = ram.read(int_to_bits(addr, 2))
        print(f"    addr {addr} -> {format_bits(out)} ({bits_to_int(out)})")

    print("\n  overwrite addr 2 with 77, leave others untouched:")
    ram.write(int_to_bits(2, 2), int_to_bits(77, 8), write_enable=1)
    for addr in range(4):
        out = ram.read(int_to_bits(addr, 2))
        print(f"    addr {addr} -> {bits_to_int(out)}")


if __name__ == "__main__":
    show_latch()
    show_register()
    show_decoder()
    show_ram()
