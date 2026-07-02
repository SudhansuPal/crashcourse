"""
A tiny file system — turning a flat block array into files and folders.

The block device (block_device.py) only knows numbered blocks. A **file system**
is the set of data structures that make those blocks usable as named files in a
directory tree. The three classic pieces:

  1. FREE-SPACE MAP (a bitmap): which blocks are in use vs. available. Allocating
     a file means finding free blocks and marking them used.

  2. INODES ("index nodes"): one per file or directory, holding its metadata —
     type, size, and the list of block numbers that hold its data. Notice a file
     is just an inode plus a *list of blocks*; those blocks need NOT be next to
     each other on disk. That non-contiguous layout is called fragmentation, and
     it's why the inode keeps an explicit block list.

  3. DIRECTORIES: an inode whose data is a table mapping names -> inode numbers.
     A path like /docs/notes.txt is resolved by starting at the root directory,
     looking up "docs" to get its inode, then looking up "notes.txt" inside it.

Design note: file *data* genuinely lives in device blocks and is governed by the
real free-space bitmap, so allocation, fragmentation, and freeing are all real
and observable. To keep the code focused, the inode table and directory tables
are held as in-memory objects — the in-RAM form of what a real FS also serializes
into reserved blocks. The concepts (inodes, directories, allocation) are intact.
"""

from typing import Dict, List, Optional


class Inode:
    """Metadata for one file or directory."""

    def __init__(self, kind: str):
        assert kind in ("file", "dir")
        self.kind = kind
        self.size = 0                       # bytes (files only)
        self.blocks: List[int] = []         # data block numbers (files only)
        self.entries: Dict[str, int] = {}   # name -> inode id (dirs only)


class FileSystem:
    """A hierarchical file system over a BlockDevice."""

    def __init__(self, device):
        self.device = device
        # Free-space bitmap: True means the block is in use. All free at format.
        self._used = [False] * device.num_blocks
        # Inode table. Inode 0 is always the root directory.
        self._inodes: List[Inode] = [Inode("dir")]
        self.ROOT = 0

    # -- free-space management ---------------------------------------------
    def _alloc_block(self) -> int:
        """Find the first free block, mark it used, and return its number."""
        for i, used in enumerate(self._used):
            if not used:
                self._used[i] = True
                return i
        raise OSError("no free blocks: disk is full")

    def _free_block(self, index: int) -> None:
        self._used[index] = False
        self.device.zero_block(index)

    def free_block_count(self) -> int:
        return self._used.count(False)

    def used_blocks(self) -> List[int]:
        return [i for i, u in enumerate(self._used) if u]

    # -- path resolution ----------------------------------------------------
    @staticmethod
    def _split(path: str) -> List[str]:
        """Break an absolute path into its components: '/a/b' -> ['a', 'b']."""
        if not path.startswith("/"):
            raise ValueError("paths must be absolute (start with '/')")
        return [p for p in path.split("/") if p]

    def _resolve(self, path: str) -> int:
        """Return the inode id for a path, walking the directory tree."""
        node = self.ROOT
        for part in self._split(path):
            inode = self._inodes[node]
            if inode.kind != "dir":
                raise NotADirectoryError(f"not a directory: {part}")
            if part not in inode.entries:
                raise FileNotFoundError(path)
            node = inode.entries[part]
        return node

    def _parent_and_name(self, path: str):
        """Split a path into (parent directory inode id, final name)."""
        parts = self._split(path)
        if not parts:
            raise ValueError("cannot operate on the root itself")
        name = parts[-1]
        parent_path = "/" + "/".join(parts[:-1])
        parent = self._resolve(parent_path)
        if self._inodes[parent].kind != "dir":
            raise NotADirectoryError(parent_path)
        return parent, name

    def _new_inode(self, kind: str) -> int:
        self._inodes.append(Inode(kind))
        return len(self._inodes) - 1

    # -- directory operations ----------------------------------------------
    def mkdir(self, path: str) -> None:
        """Create a new directory."""
        parent, name = self._parent_and_name(path)
        if name in self._inodes[parent].entries:
            raise FileExistsError(path)
        self._inodes[parent].entries[name] = self._new_inode("dir")

    def listdir(self, path: str) -> List[str]:
        """List the names in a directory, sorted."""
        node = self._resolve(path)
        if self._inodes[node].kind != "dir":
            raise NotADirectoryError(path)
        return sorted(self._inodes[node].entries)

    # -- file operations ----------------------------------------------------
    def create(self, path: str) -> None:
        """Create an empty file."""
        parent, name = self._parent_and_name(path)
        if name in self._inodes[parent].entries:
            raise FileExistsError(path)
        self._inodes[parent].entries[name] = self._new_inode("file")

    def write_file(self, path: str, data: bytes) -> None:
        """
        Write bytes to a file, (re)allocating blocks as needed.

        We free any blocks the file already held, then chop the data into
        block-size chunks and allocate a fresh block for each. Because
        _alloc_block hands out the first free block, chunks can land on
        non-adjacent blocks — real fragmentation, visible in the demo.
        """
        try:
            node = self._resolve(path)
        except FileNotFoundError:
            self.create(path)
            node = self._resolve(path)
        inode = self._inodes[node]
        if inode.kind != "file":
            raise IsADirectoryError(path)

        # Release the old contents first.
        for b in inode.blocks:
            self._free_block(b)
        inode.blocks = []

        # Split into block-size chunks and store each in a freshly allocated block.
        bs = self.device.block_size
        for offset in range(0, len(data), bs):
            chunk = data[offset:offset + bs]
            block = self._alloc_block()
            self.device.write_block(block, chunk)
            inode.blocks.append(block)
        inode.size = len(data)

    def read_file(self, path: str) -> bytes:
        """Reassemble a file's bytes from its blocks, trimmed to its size."""
        node = self._resolve(path)
        inode = self._inodes[node]
        if inode.kind != "file":
            raise IsADirectoryError(path)
        out = bytearray()
        for b in inode.blocks:
            out.extend(self.device.read_block(b))
        return bytes(out[:inode.size])     # drop zero padding in the last block

    def remove(self, path: str) -> None:
        """Delete a file (freeing its blocks) or an empty directory."""
        parent, name = self._parent_and_name(path)
        entries = self._inodes[parent].entries
        if name not in entries:
            raise FileNotFoundError(path)
        node = entries[name]
        inode = self._inodes[node]
        if inode.kind == "dir" and inode.entries:
            raise OSError("directory not empty")
        for b in inode.blocks:             # free file data blocks
            self._free_block(b)
        del entries[name]                  # unlink from its parent

    def stat(self, path: str) -> dict:
        """Return metadata about a path (kind, size, block list)."""
        node = self._resolve(path)
        inode = self._inodes[node]
        return {"kind": inode.kind, "size": inode.size, "blocks": list(inode.blocks)}

    def tree(self, path: str = "/", _prefix: str = "") -> str:
        """Render the directory tree as text (for the demo)."""
        node = self._resolve(path)
        inode = self._inodes[node]
        lines = []
        names = sorted(inode.entries)
        for i, name in enumerate(names):
            child = inode.entries[name]
            child_inode = self._inodes[child]
            branch = "`-- " if i == len(names) - 1 else "|-- "
            suffix = "/" if child_inode.kind == "dir" else f"  ({child_inode.size}B)"
            lines.append(_prefix + branch + name + suffix)
            if child_inode.kind == "dir":
                extension = "    " if i == len(names) - 1 else "|   "
                child_path = (path.rstrip("/") + "/" + name)
                sub = self.tree(child_path, _prefix + extension)
                if sub:
                    lines.append(sub)
        return "\n".join(lines)
