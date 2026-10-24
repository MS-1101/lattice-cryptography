# -*- coding: utf-8 -*-
"""Gaussian LRA dim2.ipynb

"""

import numpy as np

#general guassian lattice reduction
def gauss_reduce(v1, v2):
    v1 = np.array(v1, dtype=object)
    v2 = np.array(v2, dtype=object)

    while True:
        # Ensure ||v1|| <= ||v2||
        if np.dot(v2, v2) < np.dot(v1, v1):
            v1, v2 = v2, v1

        # Compute the nearest integer multiplier
        m = round(np.dot(v1, v2) / np.dot(v1, v1))

        # The basis is Gauss-reduced
        if m == 0:
            break

        # Reduce v2
        v2 = v2 - m * v1

    return v1, v2


v1 = (66586820, 65354729)
v2 = (6513996, 6393464)

v1_reduced, v2_reduced = gauss_reduce(v1, v2)

print(v1_reduced)
print(v2_reduced)

#gaussian with each steps
def show_gauss_steps(v1, v2):
    v1 = np.array(v1, dtype=object)
    v2 = np.array(v2, dtype=object)

    step = 1

    while True:
        # Make v1 the shorter vector
        if np.dot(v2, v2) < np.dot(v1, v1):
            v1, v2 = v2, v1

        # Compute m
        m = round(np.dot(v1, v2) / np.dot(v1, v1))

        print(f"Step {step}:")
        print(f"  v1 = {tuple(v1)}")
        print(f"  v2 = {tuple(v2)}")
        print(f"  m  = {m}")
        print()

        # Stop when m = 0
        if m == 0:
            break

        # Reduce v2
        v2 = v2 - m * v1
        step += 1

v1 = (66586820, 65354729)
v2 = (6513996, 6393464)

show_gauss_steps(v1, v2)