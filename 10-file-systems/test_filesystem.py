"""
Unit tests for the block device and the file system.

Run from the repo root:

    pytest 10-file-systems/
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from block_device import BlockDevice  # noqa: E402
from filesystem import FileSystem  # noqa: E402


def new_fs(num_blocks=32, block_size=16):
    return FileSystem(BlockDevice(num_blocks, block_size))


# ---- block device ---------------------------------------------------------

def test_block_read_write_roundtrip():
    dev = BlockDevice(4, 8)
    dev.write_block(2, b"hello")
    assert dev.read_block(2) == b"hello" + b"\x00" * 3   # zero-padded


def test_block_out_of_range():
    dev = BlockDevice(4, 8)
    with pytest.raises(IndexError):
        dev.read_block(4)


def test_block_too_large():
    dev = BlockDevice(4, 8)
    with pytest.raises(ValueError):
        dev.write_block(0, b"x" * 9)


# ---- files ----------------------------------------------------------------

def test_write_and_read_file():
    fs = new_fs()
    data = b"the quick brown fox"
    fs.write_file("/a.txt", data)
    assert fs.read_file("/a.txt") == data


def test_file_spanning_multiple_blocks():
    fs = new_fs(block_size=8)
    data = bytes(range(30))                 # needs 4 blocks of 8
    fs.write_file("/big", data)
    assert len(fs.stat("/big")["blocks"]) == 4
    assert fs.read_file("/big") == data


def test_overwrite_frees_old_blocks():
    fs = new_fs(block_size=8)
    fs.write_file("/f", b"x" * 24)          # 3 blocks
    assert fs.free_block_count() == 32 - 3
    fs.write_file("/f", b"y" * 8)           # 1 block; old 3 should be freed
    assert fs.free_block_count() == 32 - 1
    assert fs.read_file("/f") == b"y" * 8


def test_empty_file():
    fs = new_fs()
    fs.create("/empty")
    assert fs.read_file("/empty") == b""
    assert fs.stat("/empty")["blocks"] == []


# ---- directories ----------------------------------------------------------

def test_mkdir_and_listdir():
    fs = new_fs()
    fs.mkdir("/docs")
    fs.mkdir("/bin")
    fs.write_file("/docs/a.txt", b"hi")
    assert fs.listdir("/") == ["bin", "docs"]
    assert fs.listdir("/docs") == ["a.txt"]


def test_nested_paths():
    fs = new_fs()
    fs.mkdir("/a")
    fs.mkdir("/a/b")
    fs.mkdir("/a/b/c")
    fs.write_file("/a/b/c/deep.txt", b"found me")
    assert fs.read_file("/a/b/c/deep.txt") == b"found me"


def test_missing_path_raises():
    fs = new_fs()
    with pytest.raises(FileNotFoundError):
        fs.read_file("/nope.txt")
    with pytest.raises(FileNotFoundError):
        fs.mkdir("/missing/child")


def test_duplicate_raises():
    fs = new_fs()
    fs.mkdir("/x")
    with pytest.raises(FileExistsError):
        fs.mkdir("/x")


def test_relative_path_rejected():
    fs = new_fs()
    with pytest.raises(ValueError):
        fs.mkdir("relative")


# ---- deletion and space reclamation --------------------------------------

def test_remove_file_frees_blocks():
    fs = new_fs(block_size=8)
    before = fs.free_block_count()
    fs.write_file("/f", b"z" * 16)          # 2 blocks
    assert fs.free_block_count() == before - 2
    fs.remove("/f")
    assert fs.free_block_count() == before
    with pytest.raises(FileNotFoundError):
        fs.read_file("/f")


def test_remove_nonempty_dir_rejected():
    fs = new_fs()
    fs.mkdir("/d")
    fs.write_file("/d/f", b"hi")
    with pytest.raises(OSError):
        fs.remove("/d")
    fs.remove("/d/f")
    fs.remove("/d")                          # now empty, OK
    assert fs.listdir("/") == []


def test_blocks_are_reused_after_free():
    fs = new_fs(block_size=8)
    fs.write_file("/a", b"a" * 8)
    blocks_a = fs.stat("/a")["blocks"]
    fs.remove("/a")
    fs.write_file("/b", b"b" * 8)
    # The freed block should be handed back out (first-free allocation).
    assert fs.stat("/b")["blocks"] == blocks_a


def test_disk_full():
    fs = new_fs(num_blocks=4, block_size=8)
    with pytest.raises(OSError):
        fs.write_file("/toobig", b"x" * 100)   # more blocks than exist
