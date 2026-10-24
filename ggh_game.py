# -*- coding: utf-8 -*-
"""GGH_game.ipynb


**Interactive GGH Cryptosystem Demonstration**
Educational implementation of the GGH cryptosystem.
The program lets you choose to play as Alice or Bob.

Alice:
1. Generates a private and public key.
2. Gives the public key to Bob.
3. Receives a ciphertext from Bob.
4. Decrypts the ciphertext and recovers the message.

Bob:
1. Enters Alice's public key.
2. Enters a message.
3. Encrypts the message using the public key.
4. Gives the ciphertext to Alice.

This is for mathematical/educational demonstration only. It is NOT a secure modern cryptographic implementation.
"""

import numpy as np
import random

# ============================================================
# 1. Lattice functions
# ============================================================

def hadamard_ratio(B):
    """Calculate the Hadamard ratio of a basis B."""
    n = len(B)
    det = abs(np.linalg.det(B))
    norms = np.linalg.norm(B, axis=1)
    return (det / np.prod(norms)) ** (1 / n)


def generate_unimodular(n, operations=20, bound=5):
    """
    Generate a random unimodular integer matrix using elementary
    row operations.
    """
    U = np.eye(n, dtype=int)

    for _ in range(operations):
        operation = random.choice(["swap", "add", "negate"])

        if operation == "swap":
            i, j = random.sample(range(n), 2)
            U[[i, j]] = U[[j, i]]

        elif operation == "add":
            i, j = random.sample(range(n), 2)
            k = random.randint(-bound, bound)
            U[i] += k * U[j]

        elif operation == "negate":
            i = random.randint(0, n - 1)
            U[i] *= -1

    return U


def generate_public_key(V, target_ratio=0.01):
    """Generate a bad public basis W = U V."""
    while True:
        U = generate_unimodular(len(V))
        W = U @ V

        if hadamard_ratio(W) < target_ratio:
            return U, W

# ============================================================
# 2. Babai's Closest Vertex Algorithm
# ============================================================

def babai(B, target):
    """
    Babai's Closest Vertex Algorithm.

    Write:
        target = t1*v1 + ... + tn*vn

    Round:
        ai = round(ti)

    Return:
        a1*v1 + ... + an*vn
    """

    # Find the real coefficients t
    coeff_real = np.linalg.solve(B.T, target)

    # Round the coefficients to integers
    coeff = np.round(coeff_real).astype(int)

    # Construct the corresponding lattice point
    closest = coeff @ B

    return closest, coeff

# ============================================================
# 3. String <-> integer/vector conversion
# ============================================================

def string_to_numbers(message):
    """Convert a string to ASCII/Unicode code-point integers."""
    return np.array([ord(c) for c in message], dtype=int)


def split_message(numbers, dimension):
    """
    Split the integer message into blocks of length 'dimension'.
    Zero-pad the final block if necessary.
    """
    blocks = []

    for i in range(0, len(numbers), dimension):
        block = numbers[i:i + dimension]

        if len(block) < dimension:
            block = np.pad(
                block,
                (0, dimension - len(block))
            )

        blocks.append(block)

    return blocks


def numbers_to_string(vectors, original_length=None):
    """
    Convert decrypted integer vectors back to a string.

    original_length is used to remove only the padding added
    to the final block.
    """
    numbers = []

    for vector in vectors:
        for x in vector:
            numbers.append(int(x))

    if original_length is not None:
        numbers = numbers[:original_length]

    return ''.join(chr(x) for x in numbers)

# ============================================================
# 4. Encryption / Decryption
# ============================================================

def encrypt(messages, W, error_bound=5):
    """
    Encrypt a list of message vectors using the public basis W.

        e = mW + r

    where r is a small error vector.
    """
    ciphertext = []
    n = len(W)

    for m in messages:
        r = np.random.randint(
            -error_bound,
            error_bound + 1,
            size=n
        )

        e = m @ W + r
        ciphertext.append(e)

    return ciphertext


def decrypt(ciphertexts, V, W):
    """
    Decrypt ciphertexts using Alice's private good basis V.
    """
    recovered = []

    for e in ciphertexts:

        # Find the closest lattice point using the private basis
        closest, coeff = babai(V, e)

        # Recover the message from closest = mW
        m = closest @ np.linalg.inv(W)
        m = np.round(m).astype(int)

        recovered.append(m)

    return recovered

# ============================================================
# 5. Key / ciphertext text formats
# ============================================================

def matrix_to_text(A):
    """Convert an integer matrix to a compact copy-and-paste string."""
    rows = [' '.join(str(int(x)) for x in row) for row in A]
    return ';'.join(rows)


def text_to_matrix(text):
    """Convert a matrix string produced by matrix_to_text back to numpy."""
    rows = text.strip().split(';')
    return np.array(
        [[int(x) for x in row.split()] for row in rows],
        dtype=int
    )


def ciphertext_to_text(ciphertexts):
    """Convert ciphertext vectors to a copy-and-paste string."""
    return ';'.join(
        ' '.join(str(int(x)) for x in c)
        for c in ciphertexts
    )


def text_to_ciphertext(text):
    """Convert a ciphertext string back to numpy vectors."""
    rows = text.strip().split(';')
    return [
        np.array([int(x) for x in row.split()], dtype=int)
        for row in rows
    ]

# ============================================================
# 6. Fixed private basis used in the project
# ============================================================

V = np.array([
    [-97, 19, 19],
    [-36, 30, 86],
    [-184, -64, 78]
], dtype=int)

# ============================================================
# 7. Main game execution (Sequential 3-Step Mode)
# ============================================================

def main():
    print("=" * 60)
    print("                 GGH CRYPTOSYSTEM GAME")
    print("=" * 60)

    # ------------------------------------------------------------
    # STEP 1: Key Generation (Alice)
    # ------------------------------------------------------------
    print("\n[STEP 1] Alice generates keys...")
    U, W = generate_public_key(V)

    print("\nPrivate key V (Good basis):")
    print(V)
    print("\nPublic key W (Bad basis, W = U @ V):")
    print(W)

    print(f"\nHadamard ratio (V): {round(hadamard_ratio(V), 5)}")
    print(f"Hadamard ratio (W): {round(hadamard_ratio(W), 5)}")

    # ------------------------------------------------------------
    # STEP 2: Encryption (Bob)
    # ------------------------------------------------------------
    print("\n" + "-" * 60)
    print("[STEP 2] Bob receives W and encrypts a message...")
    print("-" * 60)

    message = input("\nEnter the message for Bob to encrypt:\n> ")
    if not message:
        message = "Hello GGH!"
        print(f"Using default message: '{message}'")

    numbers = string_to_numbers(message)
    messages = split_message(numbers, len(W))

    # Automatic error bound set to 5
    error_bound = 5
    ciphertexts = encrypt(messages, W, error_bound=error_bound)

    print("\nMessage blocks (m):")
    print(messages)
    print(f"\nComputed Ciphertext blocks (e = m @ W + r, error bound = {error_bound}):")
    print(ciphertexts)

    # ------------------------------------------------------------
    # STEP 3: Decryption (Alice)
    # ------------------------------------------------------------
    print("\n" + "-" * 60)
    print("[STEP 3] Alice receives ciphertext and decrypts...")
    print("-" * 60)

    recovered = decrypt(ciphertexts, V, W)
    plaintext = numbers_to_string(recovered, original_length=len(message))

    print("\nApplying Babai(V, e) to find lattice points and solving m = closest @ W^(-1)...")
    print("\nRecovered Message Blocks (m):")
    print(recovered)
    print("\nRecovered Plaintext String:")
    print(plaintext)

    print("\n" + "=" * 60)
    print("               GAME COMPLETED SUCCESSFULLY")
    print("=" * 60)


if __name__ == "__main__":
    main()