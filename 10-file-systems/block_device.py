"""
A simulated block device — the flat array of storage a disk really is.

Underneath every file and folder is a shockingly plain thing: a numbered array
of fixed-size **blocks**. A real disk or SSD can't store "a file"; it can only
store block #0, block #1, block #2, and so on, each the same size (say 4 KB).
Everything else — names, folders, sizes, the very idea of a "file" — is a data
structure the file system lays *on top* of this array. That's the whole lesson of
module 10, and this device is the foundation it stands on.

Our device is deliberately tiny (small blocks, few of them) so we can print the
entire disk and watch blocks get allocated and freed.
"""

from typing import List


class BlockDevice:
    """A fixed array of equal-size blocks. Read and write whole blocks only."""

    def __init__(self, num_blocks: int, block_size: int):
        self.num_blocks = num_blocks
        self.block_size = block_size
        # The "disk": each block is a fixed-size mutable byte buffer.
        self._blocks: List[bytearray] = [
            bytearray(block_size) for _ in range(num_blocks)
        ]
        self.reads = 0
        self.writes = 0

    def _check(self, index: int) -> None:
        if not (0 <= index < self.num_blocks):
            raise IndexError(f"block {index} out of range (0..{self.num_blocks-1})")

    def read_block(self, index: int) -> bytes:
        """Return a copy of the block's bytes."""
        self._check(index)
        self.reads += 1
        return bytes(self._blocks[index])

    def write_block(self, index: int, data: bytes) -> None:
        """
        Overwrite a whole block. Data shorter than a block is zero-padded;
        data longer than a block is an error — you can only write one block.
        """
        self._check(index)
        if len(data) > self.block_size:
            raise ValueError("data larger than one block")
        self.writes += 1
        block = bytearray(self.block_size)      # start zeroed (padding)
        block[:len(data)] = data
        self._blocks[index] = block

    def zero_block(self, index: int) -> None:
        """Wipe a block (used when freeing space)."""
        self._check(index)
        self._blocks[index] = bytearray(self.block_size)
