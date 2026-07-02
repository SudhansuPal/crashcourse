# 13 — Cryptography

How do you keep a message secret from everyone but its intended reader — and
prove who sent it? This module climbs the history of that question, from ciphers
you could break by hand to the public-key breakthrough that secures the modern
internet. Crucially, we build the **number theory** underneath it all from
scratch, so the "magic" of RSA becomes plain arithmetic.

> ⚠️ **Educational only.** The keys here are tiny and the schemes are textbook
> (unpadded). This code is for *understanding*, not protecting real secrets.

## The concept in plain language

**Classical ciphers** share one secret key between both sides:

- **Caesar** — shift every letter by a fixed amount. Only 26 keys, so you break
  it by trying them all (the demo does).
- **Vigenère** — shift by a repeating keyword, so the same letter encrypts
  differently by position. Stronger, but the repeating key is its weakness.
- **XOR** — combine each byte with a key byte. It's its own inverse, and with a
  truly random key as long as the message it becomes the **one-time pad** — the
  only *provably unbreakable* cipher.

**Public-key cryptography** removes the need to share a secret in advance:

- **Diffie–Hellman** — two strangers agree on a shared secret *over a channel an
  eavesdropper is watching*. They exchange `g^a` and `g^b mod p` in the open;
  each raises the other's value to their own secret, both reaching `g^(ab)`. The
  eavesdropper can't get there without solving the **discrete logarithm** — hard.
- **RSA** — a real public/private key pair. Anyone encrypts to you with your
  **public** key; only your **private** key decrypts. Security rests on the fact
  that **multiplying two big primes is easy but factoring the product is hard.**

## Why it matters

This is what makes the internet trustworthy: HTTPS, messaging apps, software
signatures, and cryptocurrencies all stand on Diffie–Hellman and RSA (and their
elliptic-curve descendants). The pivotal insight — a **one-way/trapdoor
function**, easy forwards and hard to reverse *unless* you hold a secret — is one
of the most consequential ideas in computer science. Seeing RSA reduce to
`m^e mod n` and `c^d mod n`, with `d` recovered by a modular inverse, turns that
mystery into something you can compute by hand.

## How the code demonstrates it

- **[`classical.py`](classical.py)** — Caesar (with a brute-force breaker),
  Vigenère, and the XOR cipher, all with round-trip encrypt/decrypt.
- **[`numbertheory.py`](numbertheory.py)** — the engine, from scratch: Euclid's
  `gcd`, the `extended_gcd` behind modular inverses, `mod_inverse`, fast
  `mod_exp` (square-and-multiply), and Miller–Rabin `is_prime` (which the tests
  confirm even catches Carmichael numbers like 561).
- **[`publickey.py`](publickey.py)** — `diffie_hellman` key exchange and full
  RSA: key generation (`n = pq`, `phi`, `d = e⁻¹ mod phi`), integer and
  byte-level encrypt/decrypt.

The demo runs the textbook RSA example (p=61, q=53 → n=3233, d=2753), encrypts
`b"CRYPTO"`, and decrypts it back; Diffie–Hellman has Alice and Bob both arrive
at the secret `2` while an eavesdropper sees only the public values.

## Run it

```bash
# from the repo root

# classical ciphers, number theory, Diffie-Hellman, and RSA
python 13-cryptography/demo.py

# run the tests
pytest 13-cryptography/
```

## Files

- `classical.py` — Caesar (+ breaker), Vigenère, XOR.
- `numbertheory.py` — gcd, extended gcd, modular inverse, modular exponentiation,
  Miller–Rabin primality.
- `publickey.py` — Diffie–Hellman and RSA (key gen, encrypt, decrypt).
- `demo.py` — the full climb from Caesar to RSA.
- `test_crypto.py` — round-trips, `mod_exp` vs Python's `pow`, primality
  (including Carmichael 561), key agreement, and full byte-range RSA inversion.

## What's next

**Module 14 — machine learning**: the final module. We leave explicit rules
behind and build a **perceptron** that *learns* from examples via **gradient
descent** — from scratch, no ML library — closing the course from a single
transistor all the way to a program that improves itself.
