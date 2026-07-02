"""
Runnable demonstration of cryptography from classical ciphers to public key.

Run from the repo root:

    python 13-cryptography/demo.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from classical import (  # noqa: E402
    caesar_encrypt, caesar_decrypt, caesar_break,
    vigenere_encrypt, vigenere_decrypt, xor_cipher,
)
from numbertheory import mod_exp, mod_inverse, is_prime, gcd  # noqa: E402
from publickey import (  # noqa: E402
    diffie_hellman, rsa_generate, rsa_encrypt_bytes, rsa_decrypt_bytes,
)


def demo_classical() -> None:
    print("=" * 62)
    print("CLASSICAL CIPHERS")
    print("=" * 62)
    msg = "Attack at dawn"
    enc = caesar_encrypt(msg, 3)
    print(f"  Caesar (shift 3): {msg!r} -> {enc!r} -> {caesar_decrypt(enc, 3)!r}")
    print("  Caesar is trivially broken — just try all 26 shifts:")
    for shift, guess in enumerate(caesar_break(enc)):
        if shift in (1, 3, 5):
            marker = "  <-- readable!" if shift == 3 else ""
            print(f"    shift {shift:2}: {guess!r}{marker}")

    venc = vigenere_encrypt(msg, "lemon")
    print(f"\n  Vigenere (key 'lemon'): {msg!r} -> {venc!r} -> "
          f"{vigenere_decrypt(venc, 'lemon')!r}")

    data = b"secret"
    x = xor_cipher(data, b"KEY")
    print(f"\n  XOR (key b'KEY'): {data!r} -> {x!r} -> {xor_cipher(x, b'KEY')!r}")
    print("  (XOR is its own inverse; a random full-length key = one-time pad)")


def demo_numbertheory() -> None:
    print("\n" + "=" * 62)
    print("NUMBER THEORY  (the tools public-key crypto needs)")
    print("=" * 62)
    print(f"  mod_exp(7, 256, 13)   = {mod_exp(7, 256, 13)}   "
          f"(7^256 mod 13, computed fast)")
    print(f"  mod_inverse(17, 3120) = {mod_inverse(17, 3120)}   "
          f"(so 17 * that = 1 mod 3120)")
    print(f"  is_prime(61)={is_prime(61)}  is_prime(1000003)={is_prime(1000003)}  "
          f"is_prime(1000000)={is_prime(1000000)}")


def demo_diffie_hellman() -> None:
    print("\n" + "=" * 62)
    print("DIFFIE-HELLMAN  (agree on a secret over a public channel)")
    print("=" * 62)
    p, g = 23, 5                        # public parameters
    a, b = 6, 15                        # Alice's and Bob's private secrets
    A, B, alice_shared, bob_shared = diffie_hellman(p, g, a, b)
    print(f"  public: p={p}, g={g}")
    print(f"  Alice picks secret a={a}, sends A = g^a mod p = {A}")
    print(f"  Bob   picks secret b={b}, sends B = g^b mod p = {B}")
    print(f"  Alice computes B^a mod p = {alice_shared}")
    print(f"  Bob   computes A^b mod p = {bob_shared}")
    print(f"  --> shared secret agreed: {alice_shared == bob_shared} "
          f"(both got {alice_shared})")
    print(f"  An eavesdropper sees only p, g, A={A}, B={B} — not the secret.")


def demo_rsa() -> None:
    print("\n" + "=" * 62)
    print("RSA  (public-key encryption)")
    print("=" * 62)
    p, q = 61, 53                       # two primes
    public, private = rsa_generate(p, q, e=17)
    print(f"  primes p={p}, q={q}  ->  n = p*q = {public.modulus}, "
          f"phi = {(p-1)*(q-1)}")
    print(f"  public key  (e, n) = ({public.exponent}, {public.modulus})")
    print(f"  private key (d, n) = ({private.exponent}, {private.modulus})")

    message = b"CRYPTO"
    cipher = rsa_encrypt_bytes(message, public)
    back = rsa_decrypt_bytes(cipher, private)
    print(f"\n  message   : {message!r}")
    print(f"  encrypted : {cipher}")
    print(f"  decrypted : {back!r}")
    print(f"  round-trip ok: {back == message}")
    print("\n  WARNING: tiny keys + textbook RSA = insecure. Educational only.")


if __name__ == "__main__":
    demo_classical()
    demo_numbertheory()
    demo_diffie_hellman()
    demo_rsa()
