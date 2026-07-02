"""
Runnable demonstration of the tiny file system.

Run from the repo root:

    python 10-file-systems/demo.py

Creates a directory tree, writes files, and shows how their data maps onto the
flat array of blocks — including fragmentation (a file's blocks needn't be
adjacent) and how deleting a file frees its blocks for reuse.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from block_device import BlockDevice  # noqa: E402
from filesystem import FileSystem  # noqa: E402


def show_disk(fs: FileSystem) -> None:
    used = set(fs.used_blocks())
    row = "".join("#" if i in used else "." for i in range(fs.device.num_blocks))
    print(f"  disk: [{row}]  ({fs.free_block_count()} free)  "
          f"('#'=used, '.'=free)")


def main() -> None:
    # Small disk so we can see everything: 32 blocks of 16 bytes each.
    device = BlockDevice(num_blocks=32, block_size=16)
    fs = FileSystem(device)

    print("=" * 62)
    print("BLOCK DEVICE: 32 blocks x 16 bytes (empty)")
    print("=" * 62)
    show_disk(fs)

    print("\n" + "=" * 62)
    print("BUILD A DIRECTORY TREE AND WRITE FILES")
    print("=" * 62)
    fs.mkdir("/docs")
    fs.mkdir("/docs/notes")
    fs.mkdir("/bin")
    fs.write_file("/readme.txt", b"crash course computer science, implemented!")
    fs.write_file("/docs/notes/todo.txt", b"build a file system from blocks")
    fs.write_file("/bin/hello", b"print hello world")

    print(fs.tree("/"))
    print()
    show_disk(fs)

    print("\n" + "=" * 62)
    print("INODES: a file is metadata + a list of blocks")
    print("=" * 62)
    for path in ("/readme.txt", "/docs/notes/todo.txt", "/bin/hello"):
        st = fs.stat(path)
        print(f"  {path:24} size={st['size']:>3}B  blocks={st['blocks']}")

    print("\n" + "=" * 62)
    print("READ BACK: reassemble bytes from scattered blocks")
    print("=" * 62)
    for path in ("/readme.txt", "/docs/notes/todo.txt"):
        print(f"  {path} -> {fs.read_file(path)!r}")

    print("\n" + "=" * 62)
    print("FRAGMENTATION: delete a middle file, then write a bigger one")
    print("=" * 62)
    print("  before delete (readme=[0,1,2], todo=[3,4], hello=[5,6]):")
    show_disk(fs)
    # Delete a file in the MIDDLE of the used region, leaving a gap.
    fs.remove("/docs/notes/todo.txt")
    print("  after deleting /docs/notes/todo.txt (frees blocks 3,4 -> a gap):")
    show_disk(fs)
    # A new 3-block file fills the gap (3,4) then spills to the next free block
    # (7) -> its blocks are non-contiguous. That's fragmentation.
    fs.write_file("/big.dat", b"A" * 40)
    print("  after writing /big.dat (40 bytes = 3 blocks): it fills the gap, then spills:")
    show_disk(fs)
    print(f"  /big.dat blocks = {fs.stat('/big.dat')['blocks']}  <- not contiguous")
    print(f"  /big.dat reads back correctly: "
          f"{fs.read_file('/big.dat') == b'A' * 40}")


if __name__ == "__main__":
    main()
