"""
Huffman coding — give common symbols short codes, rare ones long codes.

Normally every character takes the same number of bits (a byte = 8 bits each).
But in real data some symbols are far more common than others — in English text,
'e' and space appear constantly while 'q' and 'z' are rare. Huffman coding
exploits this: it assigns a *variable-length* code to each symbol, short codes to
frequent symbols and longer codes to infrequent ones, so the total shrinks.

The genius is in two parts:

  1. Build an optimal code by repeatedly merging the two least-frequent symbols
     into a subtree, until one tree remains. Frequent symbols end up near the
     root (short paths = short codes); rare ones end up deep (long codes).

  2. Make the codes "prefix-free": no code is a prefix of another. That's
     automatic here because every symbol is a *leaf*, so decoding is unambiguous
     — you walk the tree bit by bit and always know exactly when a symbol ends.

Huffman coding is provably optimal among methods that code each symbol with a
whole number of bits, and it's a real part of ZIP, JPEG, PNG, and MP3. We build
the tree with our own repeated minimum-extraction — no priority-queue or
compression library.
"""

from typing import Dict, List, Optional, Tuple


class HuffNode:
    __slots__ = ("freq", "symbol", "left", "right")

    def __init__(self, freq: int, symbol: Optional[int] = None,
                 left: "Optional[HuffNode]" = None,
                 right: "Optional[HuffNode]" = None):
        self.freq = freq
        self.symbol = symbol      # a byte value at a leaf; None at internal nodes
        self.left = left
        self.right = right

    def is_leaf(self) -> bool:
        return self.symbol is not None


class HuffmanCoder:
    """Builds a Huffman code from data and encodes/decodes with it."""

    def __init__(self, tree: Optional[HuffNode], codes: Dict[int, str]):
        self._tree = tree
        self._codes = codes       # symbol (byte) -> bit-string like "010"

    @property
    def codes(self) -> Dict[int, str]:
        return dict(self._codes)

    @classmethod
    def build(cls, data: bytes) -> "HuffmanCoder":
        """Construct the optimal code for the given data from its frequencies."""
        freqs = cls._count(data)
        tree = cls._build_tree(freqs)
        codes: Dict[int, str] = {}
        cls._assign_codes(tree, "", codes)
        return cls(tree, codes)

    @staticmethod
    def _count(data: bytes) -> Dict[int, int]:
        """Tally how often each byte value occurs."""
        freqs: Dict[int, int] = {}
        for b in data:
            freqs[b] = freqs.get(b, 0) + 1
        return freqs

    @staticmethod
    def _build_tree(freqs: Dict[int, int]) -> Optional[HuffNode]:
        """
        Repeatedly merge the two lowest-frequency nodes until one remains.

        We keep the live nodes in a plain list and scan for the two minimums
        each round — a from-scratch stand-in for a priority queue. It's a little
        slower than a heap but makes the algorithm completely transparent.
        """
        if not freqs:
            return None
        nodes: List[HuffNode] = [HuffNode(f, sym) for sym, f in freqs.items()]

        # Special case: only one distinct symbol. Give it a one-node tree; the
        # code assignment below hands it the single-bit code "0".
        if len(nodes) == 1:
            return nodes[0]

        while len(nodes) > 1:
            a = HuffmanCoder._pop_min(nodes)
            b = HuffmanCoder._pop_min(nodes)
            # Merge: the parent's frequency is the sum; children are the two mins.
            nodes.append(HuffNode(a.freq + b.freq, None, a, b))
        return nodes[0]

    @staticmethod
    def _pop_min(nodes: List[HuffNode]) -> HuffNode:
        """Remove and return the lowest-frequency node (linear scan)."""
        min_i = 0
        for i in range(1, len(nodes)):
            if nodes[i].freq < nodes[min_i].freq:
                min_i = i
        return nodes.pop(min_i)

    @staticmethod
    def _assign_codes(node: Optional[HuffNode], prefix: str,
                      codes: Dict[int, str]) -> None:
        """Walk the tree, building each leaf's code from the path taken to it."""
        if node is None:
            return
        if node.is_leaf():
            # Left branches contributed '0', right branches '1'. A lone symbol
            # gets "0" so it still has a valid (1-bit) code.
            codes[node.symbol] = prefix or "0"
            return
        HuffmanCoder._assign_codes(node.left, prefix + "0", codes)
        HuffmanCoder._assign_codes(node.right, prefix + "1", codes)

    def encode(self, data: bytes) -> str:
        """Encode bytes into a string of '0'/'1' using the code table."""
        return "".join(self._codes[b] for b in data)

    def decode(self, bits: str) -> bytes:
        """
        Decode a bit-string back to bytes by walking the tree.

        Start at the root; for each bit go left ('0') or right ('1'); when you
        reach a leaf, emit its symbol and jump back to the root. Prefix-freeness
        guarantees there's never any ambiguity about where a symbol ends.
        """
        if self._tree is None:
            return b""
        out = bytearray()
        node = self._tree
        # Single-symbol tree: the root is itself a leaf; each bit is one symbol.
        if node.is_leaf():
            return bytes([node.symbol] * len(bits))
        for bit in bits:
            node = node.left if bit == "0" else node.right
            if node.is_leaf():
                out.append(node.symbol)
                node = self._tree
        return bytes(out)


# ---- helpers to pack a bit-string into real bytes (to measure true size) ----

def pack_bits(bits: str) -> Tuple[bytes, int]:
    """
    Pack a '0'/'1' string into bytes. Returns (packed, bit_length) so the
    trailing zero-padding of the final byte can be ignored on unpacking.
    """
    padded = bits + "0" * ((8 - len(bits) % 8) % 8)
    out = bytearray()
    for i in range(0, len(padded), 8):
        out.append(int(padded[i:i + 8], 2))
    return bytes(out), len(bits)


def unpack_bits(packed: bytes, bit_length: int) -> str:
    """Reverse pack_bits: expand bytes back into exactly bit_length characters."""
    bits = "".join(f"{byte:08b}" for byte in packed)
    return bits[:bit_length]
