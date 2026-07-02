"""
Public-key cryptography — the idea that changed the world.

Classical ciphers share one fatal problem: both sides need the same secret key,
so how do you agree on it without meeting? Public-key crypto solves this with
math. Two milestones, both built here on our number-theory tools:

  DIFFIE-HELLMAN KEY EXCHANGE
    Two people who have never met derive a shared secret over a public channel
    an eavesdropper is fully listening to. They exchange g^a and g^b (mod p) in
    the open; each raises the other's value to their own secret, both landing on
    g^(a*b). The eavesdropper sees g^a and g^b but can't get g^(a*b) without
    solving the discrete logarithm — believed hard.

  RSA
    A genuine public/private key pair. Anyone can encrypt to you with your
    PUBLIC key, but only your PRIVATE key can decrypt. Its security rests on the
    difficulty of factoring the product of two large primes.

SECURITY WARNING: this is a *teaching* implementation with tiny keys, textbook
(unpadded) RSA, and predictable choices. It is NOT secure and must never protect
anything real. The point is to see *why* the math works, not to use it.
"""

import random
from typing import Tuple

from numbertheory import mod_exp, mod_inverse, gcd, is_prime, next_prime


# ---- Diffie-Hellman key exchange -----------------------------------------

def diffie_hellman(p: int, g: int, secret_a: int, secret_b: int) -> Tuple[int, int, int, int]:
    """
    Run one Diffie-Hellman exchange.

    Public parameters: a prime `p` and a base `g`. Alice's secret is `secret_a`,
    Bob's is `secret_b`. Returns (A_public, B_public, alice_shared, bob_shared),
    where the two shared values are equal — that's the agreed secret. Only the
    public values ever cross the wire.
    """
    A = mod_exp(g, secret_a, p)         # Alice sends A = g^a mod p
    B = mod_exp(g, secret_b, p)         # Bob sends   B = g^b mod p
    alice_shared = mod_exp(B, secret_a, p)   # Alice computes B^a = g^(ab)
    bob_shared = mod_exp(A, secret_b, p)     # Bob computes   A^b = g^(ab)
    return A, B, alice_shared, bob_shared


# ---- RSA ------------------------------------------------------------------

class RSAKey:
    """An RSA key: (exponent, modulus). Public uses e; private uses d."""

    def __init__(self, exponent: int, modulus: int):
        self.exponent = exponent
        self.modulus = modulus


def rsa_generate(p: int, q: int, e: int = 17) -> Tuple[RSAKey, RSAKey]:
    """
    Build an RSA key pair from two primes p and q.

        n   = p * q                     the modulus (public)
        phi = (p-1) * (q-1)             Euler's totient of n (kept secret)
        e   : public exponent, coprime to phi
        d   = e^-1 mod phi              private exponent (the trapdoor)

    Returns (public_key, private_key). Encrypting with e and decrypting with d
    are inverse operations because of Euler's theorem.
    """
    if not (is_prime(p) and is_prime(q)):
        raise ValueError("p and q must both be prime")
    if p == q:
        raise ValueError("p and q must be different primes")
    n = p * q
    phi = (p - 1) * (q - 1)
    if gcd(e, phi) != 1:
        raise ValueError(f"e={e} is not coprime with phi={phi}; pick another e")
    d = mod_inverse(e, phi)
    return RSAKey(e, n), RSAKey(d, n)


def rsa_generate_random(bits_each: int = 8, seed: int = None,
                        e: int = 17) -> Tuple[RSAKey, RSAKey]:
    """Generate a key pair from two random small primes (for demos)."""
    rng = random.Random(seed)
    lo, hi = 2 ** (bits_each - 1), 2 ** bits_each
    p = next_prime(rng.randrange(lo, hi))
    q = next_prime(rng.randrange(lo, hi))
    while q == p:
        q = next_prime(rng.randrange(lo, hi))
    # If our chosen e clashes with phi, nudge to the next workable odd exponent.
    phi = (p - 1) * (q - 1)
    while gcd(e, phi) != 1:
        e += 2
    return rsa_generate(p, q, e)


def rsa_encrypt_int(m: int, public: RSAKey) -> int:
    """Encrypt a single integer m (must be < modulus): c = m^e mod n."""
    if m >= public.modulus:
        raise ValueError("message integer must be smaller than the modulus")
    return mod_exp(m, public.exponent, public.modulus)


def rsa_decrypt_int(c: int, private: RSAKey) -> int:
    """Decrypt a single integer: m = c^d mod n."""
    return mod_exp(c, private.exponent, private.modulus)


def rsa_encrypt_bytes(data: bytes, public: RSAKey) -> list:
    """
    Encrypt bytes one at a time (each byte < 256 < modulus).

    Note: encrypting byte-by-byte is textbook RSA and is insecure (identical
    bytes give identical ciphertext). It's used here purely so we can encrypt a
    readable string and watch it round-trip.
    """
    return [rsa_encrypt_int(b, public) for b in data]


def rsa_decrypt_bytes(cipher: list, private: RSAKey) -> bytes:
    """Decrypt a list of ciphertext integers back to bytes."""
    return bytes(rsa_decrypt_int(c, private) for c in cipher)
