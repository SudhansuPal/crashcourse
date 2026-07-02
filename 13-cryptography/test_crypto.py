"""
Unit tests for the cryptography module.

Run from the repo root:

    pytest 13-cryptography/
"""

import os
import random
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from classical import (  # noqa: E402
    caesar_encrypt, caesar_decrypt, caesar_break,
    vigenere_encrypt, vigenere_decrypt, xor_cipher,
)
from numbertheory import (  # noqa: E402
    gcd, extended_gcd, mod_inverse, mod_exp, is_prime, next_prime,
)
from publickey import (  # noqa: E402
    diffie_hellman, rsa_generate, rsa_generate_random,
    rsa_encrypt_bytes, rsa_decrypt_bytes, rsa_encrypt_int, rsa_decrypt_int,
)


# ---- classical ------------------------------------------------------------

def test_caesar_roundtrip():
    for shift in range(26):
        assert caesar_decrypt(caesar_encrypt("Hello, World!", shift), shift) == "Hello, World!"


def test_caesar_preserves_non_letters():
    assert caesar_encrypt("a-b 1", 1) == "b-c 1"


def test_caesar_break_contains_plaintext():
    enc = caesar_encrypt("attack at dawn", 7)
    assert "attack at dawn" in caesar_break(enc)


def test_vigenere_roundtrip():
    msg = "The quick brown fox!"
    assert vigenere_decrypt(vigenere_encrypt(msg, "key"), "key") == msg


def test_vigenere_differs_from_caesar():
    # Repeated letters should not all map the same way (that's the point).
    enc = vigenere_encrypt("aaaa", "abcd")
    assert len(set(enc)) > 1


def test_xor_is_its_own_inverse():
    data = b"secret message"
    key = b"pass"
    assert xor_cipher(xor_cipher(data, key), key) == data


def test_xor_empty_key_rejected():
    with pytest.raises(ValueError):
        xor_cipher(b"x", b"")


# ---- number theory --------------------------------------------------------

def test_gcd():
    assert gcd(48, 18) == 6
    assert gcd(17, 5) == 1
    assert gcd(0, 5) == 5


def test_extended_gcd_identity():
    for a, b in [(48, 18), (17, 5), (240, 46)]:
        g, x, y = extended_gcd(a, b)
        assert a * x + b * y == g
        assert g == gcd(a, b)


def test_mod_inverse():
    assert (17 * mod_inverse(17, 3120)) % 3120 == 1
    for a, m in [(3, 7), (10, 17), (17, 3120)]:
        assert (a * mod_inverse(a, m)) % m == 1


def test_mod_inverse_requires_coprime():
    with pytest.raises(ValueError):
        mod_inverse(4, 8)               # share a factor of 4


def test_mod_exp_matches_builtin():
    random.seed(13)
    for _ in range(100):
        base = random.randint(0, 1000)
        exp = random.randint(0, 1000)
        mod = random.randint(1, 1000)
        assert mod_exp(base, exp, mod) == pow(base, exp, mod)


def test_is_prime_small():
    primes = {2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47}
    for n in range(2, 50):
        assert is_prime(n) == (n in primes)


def test_is_prime_large_known():
    assert is_prime(1_000_003)          # known prime
    assert not is_prime(1_000_000)
    assert not is_prime(561)            # a Carmichael number: fools weaker tests


def test_next_prime():
    assert next_prime(13) == 17
    assert next_prime(100) == 101


# ---- Diffie-Hellman -------------------------------------------------------

def test_diffie_hellman_agrees():
    A, B, sa, sb = diffie_hellman(p=23, g=5, secret_a=6, secret_b=15)
    assert sa == sb                     # both parties derive the same secret


def test_diffie_hellman_various_secrets():
    p, g = 101, 2
    for a in range(1, 20):
        for b in range(1, 20):
            _, _, sa, sb = diffie_hellman(p, g, a, b)
            assert sa == sb


# ---- RSA ------------------------------------------------------------------

def test_rsa_int_roundtrip():
    public, private = rsa_generate(61, 53, e=17)
    for m in [0, 1, 42, 100, 3000]:
        assert rsa_decrypt_int(rsa_encrypt_int(m, public), private) == m


def test_rsa_bytes_roundtrip():
    public, private = rsa_generate(61, 53, e=17)
    msg = b"CRYPTO"
    assert rsa_decrypt_bytes(rsa_encrypt_bytes(msg, public), private) == msg


def test_rsa_rejects_message_too_large():
    public, _ = rsa_generate(11, 13, e=7)   # n = 143
    with pytest.raises(ValueError):
        rsa_encrypt_int(200, public)         # 200 > 143


def test_rsa_requires_primes():
    with pytest.raises(ValueError):
        rsa_generate(10, 13)             # 10 is not prime


def test_rsa_generated_keys_roundtrip():
    for seed in range(10):
        public, private = rsa_generate_random(bits_each=8, seed=seed)
        msg = b"hi!"
        assert rsa_decrypt_bytes(rsa_encrypt_bytes(msg, public), private) == msg


def test_rsa_public_and_private_are_inverses():
    public, private = rsa_generate(101, 103, e=7)
    # Encrypt then decrypt must be the identity across the whole byte range.
    for b in range(256):
        assert rsa_decrypt_int(rsa_encrypt_int(b, public), private) == b
