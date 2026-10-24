# -*- coding: utf-8 -*-
"""GGH crypto .ipynb

"""

import numpy as np
import random

#calculate hadamard ratio
def hadamard_ratio(B):

    n = len(B) #dimension of L

    det = abs(np.linalg.det(B)) #determinant of L

    norms = np.linalg.norm(B,axis=1) #norms of each basis vector of L

    return (det / np.prod(norms))**(1/n)

#generate U randomly from GL(Z,n)
def generate_unimodular(n, operations=20, bound=5):

    U = np.eye(n, dtype=int)


    for _ in range(operations):

        operation = random.choice(
            ["swap", "add", "negate"]
        )


        if operation == "swap":

            i, j = random.sample(range(n),2)

            U[[i,j]] = U[[j,i]]


        elif operation == "add":

            i, j = random.sample(range(n),2)

            k = random.randint(-bound,bound)

            U[i] += k*U[j]


        elif operation == "negate":

            i = random.randint(0,n-1)

            U[i] *= -1


    return U

#generate the public key of Alice
def generate_public_key(V, target_ratio=0.01):

    while True:

        U = generate_unimodular(len(V))

        W = U @ V

        if hadamard_ratio(W)<target_ratio:
            return U,W

#baiba's algorithm
def babai(B, target):

    """
    Babai Closest Vertex Algorithm

    Input:
        B      : lattice basis matrix
        target : target vector w

    Algorithm:
        Solve:
            target = t1*v1 + ... + tn*vn

        Round:
            ai = round(ti)

        Return:
            a1*v1 + ... + an*vn
    """

    # Find coefficients t
    coeff_real = np.linalg.solve(B.T, target)

    # Round coefficients
    coeff = np.round(coeff_real).astype(int)

    # Closest lattice vector
    closest = coeff @ B

    return closest, coeff

# =====================================================
# Alice: Key Generation
# =====================================================

# Alice chooses a good private basis

V = np.array([
    [-97, 19, 19],
    [-36, 30, 86],
    [-184, -64, 78]
])


# Generate a bad public basis

U, W = generate_public_key(V)


print("==============================")
print("Alice's Key Generation")
print("==============================")

print("\nPrivate basis V:")
print(V)

print("\nHadamard ratio of V:")
print(round(hadamard_ratio(V),5))


print("\nUnimodular matrix U:")
print(U)

print("\ndet(U):")
print(round(np.linalg.det(U)))


print("\nPublic basis W:")
print(W)


print("\nHadamard ratio of W:")
print(round(hadamard_ratio(W),5))

# =====================================================
# Bob: Encryption
# =====================================================


def generate_message(n, bound=50):

    return np.random.randint(
        -bound,
        bound+1,
        size=n
    )


def generate_error(n, bound=5):

    return np.random.randint(
        -bound,
        bound+1,
        size=n
    )



m = generate_message(3)

r = generate_error(3)


# ciphertext

e = m @ W + r


print("\n==============================")
print("Bob's Encryption")
print("==============================")


print("\nMessage m:")
print(m)


print("\nError vector r:")
print(r)


print("\nCiphertext e:")
print(e)

# =====================================================
# Alice: Decryption
# =====================================================


closest, coeff = babai(V,e)


m_recovered = closest @ np.linalg.inv(W)

m_recovered = np.round(
    m_recovered
).astype(int)



print("\n==============================")
print("Alice's Decryption")
print("==============================")


print("\nBabai coefficients:")
print(coeff)


print("\nClosest lattice point:")
print(closest)


print("\nRecovered message:")
print(m_recovered)


print("\nSuccessful decryption:")
print(np.all(m_recovered==m))

# =====================================================
# Final Report
# =====================================================

print("\n\n======================================")
print("          GGH Cryptosystem Report")
print("======================================")

print("\n--------------------------------------")
print("1. Key Generation")
print("--------------------------------------")


print("\nPrivate good basis V:")
print(V)


print("\nHadamard ratio of private basis:")
print(round(hadamard_ratio(V),5))


print("\nUnimodular matrix U:")
print(U)


print("\ndet(U):")
print(round(np.linalg.det(U)))


print("\nPublic bad basis W = UV:")
print(W)


print("\nHadamard ratio of public basis:")
print(round(hadamard_ratio(W),5))


print("\nComparison:")
print(
    "Private basis H(V) =",
    round(hadamard_ratio(V),5),
    " (good basis)"
)

print(
    "Public basis H(W) =",
    round(hadamard_ratio(W),5),
    " (bad basis)"
)


print("\n--------------------------------------")
print("2. Encryption")
print("--------------------------------------")


print("\nMessage m:")
print(m)


print("\nError vector r:")
print(r)


print("\nCiphertext:")
print(e)


print("\nEncryption formula:")
print("e = mW + r")


print("\n--------------------------------------")
print("3. Decryption")
print("--------------------------------------")


print("\nBabai coefficients:")
print(coeff)


print("\nClosest lattice point:")
print(closest)


print("\nRecovered message:")
print(m_recovered)


print("\nDecryption successful:")
print(np.all(m_recovered==m))

# =====================================================
# Additional Experiments and Verification
# =====================================================


print("\n\n======================================")
print("     Additional Experiments")
print("======================================")


# -----------------------------------------------------
# 1. Verify that V and W generate the same lattice
# -----------------------------------------------------

print("\n--------------------------------------")
print("1. Same Lattice Verification")
print("--------------------------------------")


det_V = abs(round(np.linalg.det(V)))
det_W = abs(round(np.linalg.det(W)))


print("det(V) =", det_V)
print("det(W) =", det_W)


print(
    "Same lattice determinant:",
    abs(det_V) == abs(det_W)
)


# -----------------------------------------------------
# 2. Compare Babai using good and bad basis
# -----------------------------------------------------

print("\n--------------------------------------")
print("2. Good Basis vs Bad Basis")
print("--------------------------------------")


# Babai using private good basis V

closest_good, coeff_good = babai(V,e)


# Babai using public bad basis W

closest_bad, coeff_bad = babai(W,e)



distance_good = np.linalg.norm(
    e - closest_good
)


distance_bad = np.linalg.norm(
    e - closest_bad
)

print("\nUsing private good basis V:")

print("Closest lattice point:")
print(closest_good)

print("Distance to ciphertext:")
print(distance_good)



print("\nUsing public bad basis W:")

print("Closest lattice point:")
print(closest_bad)

print("Distance to ciphertext:")
print(distance_bad)


print("""
The private basis V is reduced and nearly orthogonal,
so Babai's algorithm can find the correct lattice point.

The public basis W is intentionally bad, therefore
Babai's algorithm is much less reliable.
""")


# -----------------------------------------------------
# 3. Effect of error size
# -----------------------------------------------------

print("\n--------------------------------------")
print("3. Effect of Error Size")
print("--------------------------------------")


error_sizes = [
    1,
    5,
    10,
    50,
    100,
    500,
    1000
]


for size in error_sizes:


    r_test = np.array(
        [size,size,size]
    )


    # encryption

    e_test = m @ W + r_test


    # decryption

    closest_test, _ = babai(
        V,
        e_test
    )


    recovered_test = np.round(
        closest_test @ np.linalg.inv(W)
    ).astype(int)



    success = np.all(
        recovered_test == m
    )


    print(
        "Error size:",
        size,
        " | Success:",
        success
    )

#check for several trials
for i in range(30):

    U = generate_unimodular(3)

    W = U @ V

    m = generate_message(3)

    r = generate_error(3,bound=3)

    e = m @ W + r


    closest,coeff=babai(V,e)


    recovered=np.round(
        closest @ np.linalg.inv(W)
    ).astype(int)


    print(
        "Trial",
        i+1,
        ":",
        np.all(recovered==m)
    )

#strings to number
def string_to_numbers(message):

    return np.array(
        [ord(c) for c in message]
    )

#make the array fit into 3 dimensional: output a list of vectors
def split_message(numbers, dimension):

    blocks=[]

    for i in range(0,len(numbers),dimension):

        block=numbers[i:i+dimension]

        if len(block)<dimension:

            block=np.pad(
                block,
                (0,dimension-len(block))
            )

        blocks.append(block)

    return blocks

#encrytp messages
def encrypt(messages, W, error_bound=5):
    """
    GGH encryption

    Input:
        messages: list of message vectors
        W: public basis
        error_bound: size of error

    Output:
        ciphertext list
    """

    ciphertext=[]

    n=len(W)


    for m in messages:

        r=generate_error(n, bound=error_bound)


        e=m@W+r

        ciphertext.append(e)


    return ciphertext

def numbers_to_string(vectors):

    numbers = []

    for vector in vectors:

        for x in vector:

            x = int(x)

            # remove padding zeros
            if x != 0:
                numbers.append(x)


    return ''.join(
        chr(x)
        for x in numbers
    )


def decrypt(ciphertexts, V, W):

    recovered=[]


    for e in ciphertexts:


        closest, coeff = babai(
            V,
            e
        )


        m = closest @ np.linalg.inv(W)


        m=np.round(m).astype(int)


        recovered.append(m)


    return recovered

messages = split_message(
    string_to_numbers("Lattice-Based Cryptography"),
    3
)

print(messages)

#good basis
V = np.array([
    [-97, 19, 19],
    [-36, 30, 86],
    [-184, -64, 78]
])


# Generate a bad public basis

U, W = generate_public_key(V)

ciphertexts = encrypt(messages,W)


for c in ciphertexts:
    print(c)

numbers = decrypt(
    ciphertexts,
    V,
    W
)

print(numbers)


plaintext = numbers_to_string(numbers)


print(plaintext)

print("Original Message:")
print("Lattice-Based Cryptography")
print("--------------------------------------")

print("The array of message (input):")
print(messages)
print("--------------------------------------")

print("Encrypted ciphertext:")
print(ciphertexts)
print("--------------------------------------")

print("Decrypted result:")
print(numbers)
print("--------------------------------------")

print("Plaintext:")
print(plaintext)