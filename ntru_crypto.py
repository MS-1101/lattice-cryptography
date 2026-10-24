# -*- coding: utf-8 -*-
"""ntru crypto.ipynb

"""

import random
from sympy import symbols, Poly, invert

# ============================================================
# NTRUEncrypt
# ============================================================

x = symbols("x")


# ------------------------------------------------------------
# Polynomial operations in
#
#       R = Z[x] / <x^N - 1>
#
# ------------------------------------------------------------

def convolution(a, b):
    """
    Cyclic convolution:

        a star b  in Z[x] / <x^N - 1>.

    Polynomials are represented by coefficient lists:
        [a_0, a_1, ..., a_{N-1}]
    """

    N = len(a)
    result = [0] * N

    for i in range(N):
        for j in range(N):
            result[(i + j) % N] += a[i] * b[j]

    return result


def add(a, b):
    """Add two polynomials."""
    return [u + v for u, v in zip(a, b)]


def multiply_scalar(c, a):
    """Multiply a polynomial by an integer c."""
    return [c * u for u in a]


def mod_poly(a, modulus):
    """Reduce every coefficient modulo modulus."""
    return [u % modulus for u in a]


def centre_lift(a, modulus):
    """
    Centre-lift coefficients modulo modulus.

    The representatives lie in

        (-modulus/2, modulus/2].
    """

    result = []

    for u in a:
        u = u % modulus

        if u > modulus / 2:
            u -= modulus

        result.append(u)

    return result


# ------------------------------------------------------------
# Ternary polynomials
# ------------------------------------------------------------

def ternary(d1, d2, N):
    """
    Generate a random polynomial in T(d1, d2).

    d1 coefficients are +1,
    d2 coefficients are -1,
    all remaining coefficients are 0.
    """

    if d1 + d2 > N:
        raise ValueError("d1 + d2 cannot exceed N.")

    coefficients = (
        [1] * d1
        + [-1] * d2
        + [0] * (N - d1 - d2)
    )

    random.shuffle(coefficients)

    return coefficients


# ------------------------------------------------------------
# Polynomial inverse
# ------------------------------------------------------------

def ntru_inverse(f, N, modulus):
    """
    Compute the inverse of f(x) in

        (Z/modulus Z)[x] / <x^N - 1>.

    That is, find F such that

        f star F = 1 (mod modulus).

    The polynomial f is given as a coefficient list.
    """

    # Convert coefficient list to SymPy polynomial
    f_poly = sum(
        coefficient * x**i
        for i, coefficient in enumerate(f)
    )

    # Polynomial x^N - 1
    ring_polynomial = x**N - 1

    # Compute the inverse over Z/modulus Z
    try:
        inverse = invert(
            Poly(f_poly, x, modulus=modulus),
            Poly(ring_polynomial, x, modulus=modulus)
        )
    except Exception as error:
        raise ValueError(
            f"f is not invertible modulo {modulus}."
        ) from error

    # Convert back to coefficient list
    inverse = inverse.as_expr()

    return [
        int(inverse.coeff(x, i)) % modulus
        for i in range(N)
    ]


# ------------------------------------------------------------
# Polynomial display
# ------------------------------------------------------------

def polynomial_string(a):
    """Convert a coefficient list into a readable polynomial."""

    terms = []

    for i, coefficient in enumerate(a):

        if coefficient == 0:
            continue

        absolute = abs(coefficient)

        # Construct the term
        if i == 0:
            term = str(absolute)

        elif i == 1:
            if absolute == 1:
                term = "x"
            else:
                term = f"{absolute}x"

        else:
            if absolute == 1:
                term = f"x^{i}"
            else:
                term = f"{absolute}x^{i}"

        # Add sign
        if not terms:
            if coefficient < 0:
                terms.append("-" + term)
            else:
                terms.append(term)

        else:
            if coefficient > 0:
                terms.append(" + " + term)
            else:
                terms.append(" - " + term)

    return "".join(terms) if terms else "0"


def print_polynomial(name, a):
    """Print a polynomial."""
    print(f"{name}(x) = {polynomial_string(a)}")

# ============================================================
# NTRU KEY GENERATION
# ============================================================

def generate_keys(N, p, q, d):
    """
    Generate an NTRU key pair.

    Returns

        f, g, Fp, Fq, h

    where

        f in T(d+1,d)
        g in T(d,d)

        Fp = f^(-1) mod p
        Fq = f^(-1) mod q

        h = Fq star g mod q
    """

    while True:

        f = ternary(d + 1, d, N)
        g = ternary(d, d, N)

        try:
            Fp = ntru_inverse(f, N, p)
            Fq = ntru_inverse(f, N, q)
            break

        except ValueError:
            # f was not invertible modulo p or q
            continue

    h = mod_poly(
        convolution(Fq, g),
        q
    )

    return f, g, Fp, Fq, h


# ============================================================
# NTRU ENCRYPTION
# ============================================================

def encrypt(m, r, h, p, q):
    """
    Encrypt

        e = p h star r + m mod q.
    """

    hr = convolution(h, r)

    e = add(
        multiply_scalar(p, hr),
        m
    )

    return mod_poly(e, q)


# ============================================================
# NTRU DECRYPTION
# ============================================================

def decrypt(e, f, Fp, p, q):
    """
    Decrypt an NTRU ciphertext.

    Step 1:
        a = f star e mod q

    Step 2:
        centre-lift a to a'

    Step 3:
        b = Fp star a' mod p

    Step 4:
        centre-lift b to recover m
    """

    # Step 1
    a = mod_poly(
        convolution(f, e),
        q
    )

    # Step 2
    a_prime = centre_lift(a, q)

    # Step 3
    b = mod_poly(
        convolution(Fp, a_prime),
        p
    )

    # Step 4
    m_recovered = centre_lift(b, p)

    return m_recovered, a, a_prime, b


# ============================================================
# VERIFICATION
# ============================================================

def verify_keys(f, g, Fp, Fq, h, p, q):
    """
    Verify the key identities:

        f star Fp = 1 mod p
        f star Fq = 1 mod q
        f star h  = g mod q
    """

    N = len(f)

    identity = [1] + [0] * (N - 1)

    check_Fp = mod_poly(
        convolution(f, Fp),
        p
    )

    check_Fq = mod_poly(
        convolution(f, Fq),
        q
    )

    check_h = mod_poly(
        convolution(f, h),
        q
    )

    check_g = mod_poly(g, q)

    return (
        check_Fp == identity
        and check_Fq == identity
        and check_h == check_g
    )

# ============================================================
# EXAMPLE
#
# Change ONLY this section when using another example.
# ============================================================

N = 7
p = 3
q = 41
d = 2


# Example 7.53:
#
# f(x) = x^6 - x^4 + x^3 + x^2 - 1
#
# coefficient order:
# [1, x, x^2, ..., x^6]

f = [
    -1,
     0,
     1,
     1,
    -1,
     0,
     1
]


# g(x) = x^6 + x^4 - x^2 - x

g = [
     0,
    -1,
    -1,
     0,
     1,
     0,
     1
]


# ------------------------------------------------------------
# Compute inverses
# ------------------------------------------------------------

Fp = ntru_inverse(f, N, p)
Fq = ntru_inverse(f, N, q)


# ------------------------------------------------------------
# Public key
# ------------------------------------------------------------

h = mod_poly(
    convolution(Fq, g),
    q
)


# ------------------------------------------------------------
# Bob's message
#
# m(x) = -x^5 + x^3 + x^2 - x + 1
# ------------------------------------------------------------

m = [
     1,
    -1,
     1,
     1,
     0,
    -1,
     0
]


# ------------------------------------------------------------
# Bob's random polynomial
#
# r(x) = x^6 - x^5 + x - 1
# ------------------------------------------------------------

r = [
    -1,
     1,
     0,
     0,
     0,
    -1,
     1
]


# ============================================================
# RUN NTRU
# ============================================================

print("=" * 65)
print("NTRUEncrypt")
print("=" * 65)

print("\nParameters:")
print(f"N = {N}")
print(f"p = {p}")
print(f"q = {q}")
print(f"d = {d}")

print("\nCorrectness condition:")
print(f"q > (6d+1)p")
print(f"{q} > {(6*d + 1)*p}")


# ------------------------------------------------------------
# Keys
# ------------------------------------------------------------

print("\n" + "-" * 65)
print("KEY GENERATION")
print("-" * 65)

print_polynomial("f", f)
print_polynomial("g", g)
print_polynomial("Fp", Fp)
print_polynomial("Fq", Fq)
print_polynomial("h", h)


# Verify keys
print("\nKey verification:")
print(
    "f star Fp = 1 mod p, "
    "f star Fq = 1 mod q, "
    "f star h = g mod q"
)

print(
    "All identities verified:",
    verify_keys(f, g, Fp, Fq, h, p, q)
)


# ------------------------------------------------------------
# Encryption
# ------------------------------------------------------------

print("\n" + "-" * 65)
print("ENCRYPTION")
print("-" * 65)

print_polynomial("m", m)
print_polynomial("r", r)

e = encrypt(
    m,
    r,
    h,
    p,
    q
)

print("\nCiphertext:")
print_polynomial("e", e)


# ------------------------------------------------------------
# Decryption
# ------------------------------------------------------------

print("\n" + "-" * 65)
print("DECRYPTION")
print("-" * 65)

m_recovered, a, a_prime, b = decrypt(
    e,
    f,
    Fp,
    p,
    q
)

print_polynomial("a", a)
print_polynomial("a'", a_prime)
print_polynomial("b", b)
print_polynomial("m recovered", m_recovered)


# ------------------------------------------------------------
# Final verification
# ------------------------------------------------------------

print("\n" + "-" * 65)
print("FINAL RESULT")
print("-" * 65)

print_polynomial("original m", m)
print_polynomial("recovered m", m_recovered)

print("\nSuccessful decryption:", m_recovered == m)