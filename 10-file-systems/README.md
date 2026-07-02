# 10 — File Systems

Files and folders feel fundamental, but they're an illusion — a convenient
fiction the **file system** paints over something far plainer: a flat, numbered
array of fixed-size **blocks**. This module builds a small but real file system
on a simulated block device, revealing that a "file" is just an inode plus a list
of block numbers, and a "folder" is just a table of names.

## The concept in plain language

A disk can't store a file; it can only store block #0, block #1, and so on, each
the same size. A file system adds three data structures to turn that into
something usable:

1. **Free-space map** — a bitmap tracking which blocks are used vs. free.
   Allocating storage means finding free blocks and marking them taken.
2. **Inodes** ("index nodes") — one per file/directory, holding metadata: its
   type, its size, and **the list of blocks that hold its data**. Because the
   inode stores an explicit list, a file's blocks need not be next to each other
   — that scattering is **fragmentation**.
3. **Directories** — an inode whose data is a table mapping **names → inode
   numbers**. A path like `/docs/notes.txt` is resolved by starting at the root
   directory, looking up `docs` to get its inode, then looking up `notes.txt`
   inside that.

## Why it matters

This is one of the great "it's just data structures" reveals in computing. Every
time you save a file, the OS is finding free blocks in a bitmap, recording their
numbers in an inode, and adding a name→inode entry to a directory. Understanding
this demystifies a lot: why deleting a file is instant (you just unlink it and
free its blocks — the data isn't wiped), why disks fragment, why there's a limit
on filename lengths and file counts, and how "undelete" tools work. Databases,
too, are elaborate structures over the same flat block storage.

## How the code demonstrates it

- **[`block_device.py`](block_device.py)** — the "disk": a fixed array of
  equal-size byte blocks you can only read and write a whole block at a time.
- **[`filesystem.py`](filesystem.py)** — the file system proper:
  - a real **free-space bitmap** with first-free allocation,
  - **inodes** carrying each file's size and block list,
  - **directories** as name→inode tables, with full **path resolution** through
    nested folders,
  - `write_file` chops data into block-size chunks and allocates a block per
    chunk; `read_file` reassembles them and trims the last block's padding;
    `remove` frees blocks back to the bitmap.

File **data genuinely lives in device blocks** governed by the real bitmap, so
the demo can print the whole disk (`#` used, `.` free) and you can watch it fill,
free, and reuse blocks. The demo deletes a file in the *middle* of the used
region and writes a new one that **fills the gap then spills** — landing on
blocks `[3, 4, 7]`, visibly non-contiguous. That's fragmentation, live.

> Design note: to keep the code focused, the inode table and directory tables are
> in-memory objects (the in-RAM form of structures a real FS also serializes into
> reserved blocks). Allocation, inodes, directories, and fragmentation are all
> real and observable.

## Run it

```bash
# from the repo root

# build a tree, write files, inspect inodes/blocks, and watch fragmentation
python 10-file-systems/demo.py

# run the tests
pytest 10-file-systems/
```

## Files

- `block_device.py` — the flat block array (the "disk").
- `filesystem.py` — bitmap, inodes, directories, path resolution, and file ops.
- `demo.py` — a directory tree, inode/block inspection, and a fragmentation demo.
- `test_filesystem.py` — files spanning blocks, overwrite/delete freeing blocks,
  nested paths, block reuse, and disk-full handling.

## What's next

**Module 11 — compression**: how do you make data *smaller* without losing any of
it? We build **run-length encoding** and **Huffman coding** from scratch — the
lossless techniques behind ZIP, PNG, and more — and measure the compression they
achieve.
