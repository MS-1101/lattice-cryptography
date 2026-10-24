# -*- coding: utf-8 -*-
"""GGH cryptosystem_ex .ipynb

"""

import numpy as np

#store the private key-good lattice
V = np.array([
    [-97, 19, 19],
    [-36, 30, 86],
    [-184, -64, 78]
])

print(V)

#calculate hadamard ratio of V
def hadamard_ratio(B):

    n = len(B) #dimension of L

    det = abs(np.linalg.det(B)) #determinant of L

    norms = np.linalg.norm(B,axis=1) #norms of each basis vector of L

    return (det / np.prod(norms))**(1/n)

print(hadamard_ratio(V))

#generate U and bad basis matrix
U = np.array([
    [4327, -15447, 23454],
    [3297, -11770, 17871],
    [5464, -19506, 29617]
], dtype=int)
print(round(np.linalg.det(U)))

W = U @ V
print(W)
print(hadamard_ratio(W))

m = np.array([86, -35, -32]) #plaintext
r = np.array([-4, -3, 2]) #small perturbation

#encryption
e = m @ W + r

print("Message:", m)
print("\nError:", r)
print("\nCiphertext:", e)

# babai's algorithm
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

#Decryptionn
closest, coeff = babai(V,e)
print(closest== m @ W)
print("Babai coefficients:", coeff)
print("Closest lattice point:", closest)

m_recovered = closest @ np.linalg.inv(W)

m_recovered = np.round(m_recovered).astype(int)

print("Recovered message:", m_recovered)

print("Success:", np.all(m_recovered==m))

# Babai using private good basis V
closest_good, coeff_good =babai(V,e)


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


m_recovered_bad = closest_bad @ np.linalg.inv(W)

m_recovered_bad = np.round(m_recovered_bad).astype(int)

print("Recovered message by Eve:", m_recovered_bad)

print("Success (Eve) :", np.all(m_recovered_bad==m))

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