"""
Run-length encoding (RLE) — the simplest lossless compression there is.

Idea: replace a "run" of the same value repeated many times with a single copy
plus a count. "AAAAAAA" (7 bytes) becomes "7A" (2 bytes). It's *lossless* — you
can perfectly reconstruct the original — and it shines on data with long runs:
simple graphics, icons, scanned black-and-white pages, fax transmissions.

Its weakness is just as instructive: on data with few runs, RLE can make things
*bigger* (each lone byte costs a count byte too). No compressor beats every
input — a fundamental limit we'll see again with Huffman coding next door.

We encode a stream of bytes as pairs (count, value), with each count capped at
255 so it fits in a single byte; longer runs split into multiple pairs.
"""


def rle_encode(data: bytes) -> bytes:
    """Compress bytes into (count, value) pairs. Runs longer than 255 split."""
    out = bytearray()
    i = 0
    n = len(data)
    while i < n:
        value = data[i]
        run = 1
        # Extend the run while the next byte matches and we're under the cap.
        while i + run < n and data[i + run] == value and run < 255:
            run += 1
        out.append(run)     # count byte
        out.append(value)   # value byte
        i += run
    return bytes(out)


def rle_decode(data: bytes) -> bytes:
    """Reverse rle_encode: expand each (count, value) pair back into a run."""
    if len(data) % 2 != 0:
        raise ValueError("RLE data must be pairs of (count, value)")
    out = bytearray()
    for i in range(0, len(data), 2):
        count, value = data[i], data[i + 1]
        out.extend([value] * count)
    return bytes(out)
