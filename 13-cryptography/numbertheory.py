"""
Number theory — the mathematics modern cryptography is built on.

Public-key cryptography (Diffie-Hellman, RSA) doesn't rely on secret shuffling;
it relies on arithmetic that is *easy to do forwards and believed hard to
reverse*. A handful of number-theory tools make it work, and we build each from
scratch here:

    gcd / extended gcd : the greatest common divisor, and the coefficients that
                         let us find modular inverses.
    modular inverse    : the "division" of modular arithmetic — undoing a
                         multiply mod m. RSA's private key is one of these.
    modular exponent.  : compute base^exp mod m efficiently (square-and-multiply)
                         even for huge exponents. This is the workhorse of both
                         Diffie-Hellman and RSA.
    primality testing  : decide whether a big number is prime (Miller-Rabin).
                         RSA's security rests on multiplying two large primes.

The asymmetry — multiplying primes is easy, factoring their product is hard — is
the trapdoor the whole edifice stands on.
"""

from typing import Tuple


def gcd(a: int, b: int) -> int:
    """Greatest common divisor via Euclid's algorithm: gcd(a,b)=gcd(b, a mod b)."""
    while b:
        a, b = b, a % b
    return abs(a)


def extended_gcd(a: int, b: int) -> Tuple[int, int, int]:
    """
    Return (g, x, y) such that a*x + b*y = g = gcd(a, b).

    The extra coefficients x, y are what let us compute modular inverses: if
    a*x + m*y = 1, then x is the inverse of a modulo m.
    """
    if b == 0:
        return a, 1, 0
    g, x1, y1 = extended_gcd(b, a % b)
    return g, y1, x1 - (a // b) * y1


def mod_inverse(a: int, m: int) -> int:
    """
    The modular inverse of a mod m: the number x with (a*x) mod m == 1.

    It exists only when gcd(a, m) == 1. This is modular "division" and is exactly
    how RSA derives the private exponent d from the public exponent e.
    """
    g, x, _ = extended_gcd(a % m, m)
    if g != 1:
        raise ValueError(f"{a} has no inverse mod {m} (they share a factor)")
    return x % m


def mod_exp(base: int, exp: int, mod: int) -> int:
    """
    Compute base**exp mod m by square-and-multiply, in O(log exp) multiplies.

    Naively raising to a huge power would produce astronomically large numbers;
    here we reduce mod m at every step and use the binary expansion of the
    exponent, so it stays fast and small even for cryptographic sizes.
    """
    if mod == 1:
        return 0
    result = 1
    base %= mod
    while exp > 0:
        if exp & 1:                     # this bit of the exponent is set
            result = (result * base) % mod
        base = (base * base) % mod      # square for the next bit
        exp >>= 1
    return result


# Small primes for a quick first sieve before the heavier test.
_SMALL_PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]


def is_prime(n: int) -> bool:
    """
    Miller-Rabin primality test. Deterministic for all n < 3.3 * 10^24 with the
    fixed set of bases below — plenty for our purposes.

    Idea: for a prime n, certain equations in modular arithmetic must hold for
    every base a. If any base violates them, n is definitely composite; if all
    the chosen bases pass, n is prime (for numbers in the range these bases
    cover).
    """
    if n < 2:
        return False
    for p in _SMALL_PRIMES:
        if n % p == 0:
            return n == p               # divisible by a small prime -> prime iff equal

    # Write n-1 as d * 2^r with d odd.
    d, r = n - 1, 0
    while d % 2 == 0:
        d //= 2
        r += 1

    for a in _SMALL_PRIMES:
        if a >= n:
            continue
        x = mod_exp(a, d, n)
        if x == 1 or x == n - 1:
            continue                    # this base is happy
        for _ in range(r - 1):
            x = mod_exp(x, 2, n)
            if x == n - 1:
                break
        else:
            return False                # no square hit n-1 -> composite
    return True


def next_prime(n: int) -> int:
    """Smallest prime strictly greater than n (used for small-key generation)."""
    candidate = n + 1
    while not is_prime(candidate):
        candidate += 1
    return candidate
