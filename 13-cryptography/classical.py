"""
Classical ciphers — the first 2000 years of keeping secrets.

Cryptography starts simply: rearrange or shift letters by a rule only you and
your correspondent know. These ciphers are all breakable today (some trivially),
but they introduce the vocabulary — plaintext, ciphertext, key, encryption,
decryption — and each one teaches an idea that survives into modern crypto.

    Caesar   : shift every letter by a fixed amount. One tiny key (0-25).
               Teaches: substitution. Breaks: only 26 keys to try.

    Vigenere : shift by a repeating keyword, so the same letter can encrypt
               differently depending on position. Teaches: a longer key defeats
               naive frequency analysis. Breaks: the key repeats.

    XOR      : combine each byte with a key byte using XOR. Symmetric (the same
               operation decrypts). Teaches: the core of stream ciphers and the
               one *unbreakable* cipher — the one-time pad — when the key is
               truly random and as long as the message.
"""

from typing import List

ALPHABET_SIZE = 26


def caesar_encrypt(text: str, shift: int) -> str:
    """Shift each letter forward by `shift`, wrapping around; leave others as-is."""
    result: List[str] = []
    for ch in text:
        if "a" <= ch <= "z":
            result.append(chr((ord(ch) - ord("a") + shift) % ALPHABET_SIZE + ord("a")))
        elif "A" <= ch <= "Z":
            result.append(chr((ord(ch) - ord("A") + shift) % ALPHABET_SIZE + ord("A")))
        else:
            result.append(ch)          # spaces, punctuation, digits pass through
    return "".join(result)


def caesar_decrypt(text: str, shift: int) -> str:
    """Decrypt by shifting the other way."""
    return caesar_encrypt(text, -shift)


def caesar_break(ciphertext: str) -> List[str]:
    """
    Brute-force every possible Caesar key. Because there are only 26, we can
    just list all 26 candidate plaintexts — this is *why* the Caesar cipher is
    hopelessly weak.
    """
    return [caesar_decrypt(ciphertext, shift) for shift in range(ALPHABET_SIZE)]


def vigenere_encrypt(text: str, key: str) -> str:
    """
    Encrypt with a repeating-keyword shift. The i-th letter is shifted by the
    key letter that lines up with it, so identical plaintext letters can become
    different ciphertext letters — the improvement over Caesar.
    """
    key = key.lower()
    result: List[str] = []
    k = 0                               # advances only on actual letters
    for ch in text:
        if ch.isalpha():
            shift = ord(key[k % len(key)]) - ord("a")
            result.append(caesar_encrypt(ch, shift))
            k += 1
        else:
            result.append(ch)
    return "".join(result)


def vigenere_decrypt(text: str, key: str) -> str:
    """Reverse the keyword shifts."""
    key = key.lower()
    result: List[str] = []
    k = 0
    for ch in text:
        if ch.isalpha():
            shift = ord(key[k % len(key)]) - ord("a")
            result.append(caesar_decrypt(ch, shift))
            k += 1
        else:
            result.append(ch)
    return "".join(result)


def xor_cipher(data: bytes, key: bytes) -> bytes:
    """
    XOR each byte with a repeating key. This function is its own inverse:
    applying it twice with the same key returns the original data, because
    (x XOR k) XOR k == x. With a random key as long as the message, this is the
    one-time pad — provably unbreakable. Reusing a short key is what makes it
    breakable in practice.
    """
    if not key:
        raise ValueError("key must not be empty")
    return bytes(b ^ key[i % len(key)] for i, b in enumerate(data))
