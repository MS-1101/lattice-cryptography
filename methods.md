# Methods and interpretation

[Back to the project](README.md)

## Basis convention and quality

Basis vectors are stored as rows. A lattice vector is an integer row vector multiplied by the basis matrix, and a unimodular row transformation preserves the lattice. For a square, full-rank basis B with n rows, the code uses

$$
H(B)=\left(\frac{\lvert\det B\rvert}{\prod_{i=1}^{n}\lVert b_i\rVert}\right)^{1/n}.
$$

A value closer to one indicates a more nearly orthogonal basis under this measure. It is not a cryptographic security estimate. The reported shortest basis-vector norm is the minimum row norm; it is not a general certificate for the lattice's shortest nonzero vector.

## Gaussian and LLL reduction

The Gaussian example starts from `(66586820, 65354729)` and `(6513996, 6393464)`. The script prints six reduction stages and returns `(2280, -1001)` and `(-1324, -2376)`.

The LLL implementation recomputes Gram–Schmidt data after integer row operations. It size-reduces a row against earlier rows, tests the Lovász condition, and swaps adjacent rows when the condition fails. It returns the reduced basis, a swap count, and the sequence of row indices visited.

The saved six-dimensional experiment compares the original order, reversed order, and several Lovász parameter values. Its 49-point parameter sweep is retained in the executed notebook. A higher parameter changes the constraints and computational work, but need not improve the particular Hadamard-ratio value of the basis returned on this matrix.

The implementation uses NumPy fixed-width integers for basis operations and floating-point Gram–Schmidt calculations. It is intended for the small supplied matrices. Large coefficients, dependent rows, and poorly conditioned inputs require a more robust implementation; changing a parameter does not establish correctness for those cases.

## GGH: encryption and basis-dependent rounding

The fixed example constructs a public basis W from a private basis V using an integer unimodular matrix U, with `W = U @ V`. For message m and small perturbation r, encryption computes

$$
e=mW+r.
$$

Decryption solves for the real coordinates of e in V, rounds those coordinates, reconstructs a lattice point, and expresses that point in W. This is the coordinate-rounding version of Babai's method used by the notes. It does not use a successive Gram–Schmidt nearest-plane procedure, and it need not return the exact closest lattice point.

The fixed example uses `m = (86, -35, -32)` and `r = (-4, -3, 2)`. The private-basis calculation recovers m; direct coordinate rounding in the public basis fails for this ciphertext. The notes then discuss LLL reduction of W followed by the same rounding operation (pp. 90–91).

The randomized scripts use the same small private basis. Their random generators are ordinary Python/NumPy generators and their arithmetic uses floating-point matrix solves. The text interface preserves the original string length to remove padding. The extension's `error_bound` argument controls the perturbation size in the published code.

## NTRUEncrypt and candidate validation

Coefficient lists are ordered from the constant term upward. Multiplication is cyclic convolution modulo `x^N - 1`. The fixed example uses `(N, p, q, d) = (7, 3, 41, 2)`, computes inverses of f modulo p and q, checks the key identities, encrypts the supplied ternary message, and centre-lifts during decryption.

The notes construct a 14-dimensional lattice with row basis `[I H; 0 qI]`, where the rows of H are cyclic shifts of the public polynomial h. The reported reduction improves the Hadamard ratio from approximately 0.1184 to 0.8574 (pp. 91–93). This repository retains that report result; the standalone NTRU script demonstrates encryption and decryption rather than the lattice attack.

**Correction to the candidate-test discussion on p. 93:** every vector `(a, b)` in this constructed lattice already satisfies `a * h = b (mod q)`. In particular, the all-minus-one first half with zero second half satisfies the relation in this example, because the coefficient sum of h is zero modulo q. The public relation alone cannot reject that row or establish that a short row is a working private key. Candidate validation must additionally check the required polynomial invertibility, key structure, and successful decryption. A signed cyclic rotation of the known private pair is an equivalent key in this toy example; an arbitrary short lattice row need not be one.

The successful low-dimensional examples do not imply an attack on realistic parameter sets. Statements in these learning notes about large-dimensional hardness should be read as motivation, not as a proof of security.
