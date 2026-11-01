"""QUBO construction for the fleet go / stop / ask problem.

Variable order (qubit k = variable k, Qiskit little-endian bit k of a basis index):
    a_0 .. a_{N-1}, s_0 .. s_{N-1}, z_0 .. z_{K-1}   (z = budget slack bits, slack encoding only)

Encodings of the budget sum(a) <= B:
    "slack"      : lam_b * (sum a + sum c_k z_k - B)^2 with bounded binary slack
    "unbalanced" : -lam_1 * eta + lam_2 * eta^2,  eta = B - sum a   (Montanez-Barrera et al.)
Both add the exclusion penalty lam_x * a_i * s_i.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .instances import Instance, GO, STOP, ASK


class QuboBuilder:
    def __init__(self, n: int):
        self.n = n
        self.const = 0.0
        self.lin = np.zeros(n)
        self.quad = {}  # (i, j) with i < j -> coefficient

    def add_const(self, c):
        self.const += c

    def add_lin(self, i, c):
        self.lin[i] += c

    def add_quad(self, i, j, c):
        if i == j:  # x^2 = x for binaries
            self.lin[i] += c
            return
        key = (i, j) if i < j else (j, i)
        self.quad[key] = self.quad.get(key, 0.0) + c

    def add_square(self, terms, target):
        """Add (sum_j u_j x_j - target)^2 for terms = [(var, u_j), ...]."""
        self.add_const(target ** 2)
        for idx, (vi, ui) in enumerate(terms):
            self.add_lin(vi, ui * ui - 2.0 * target * ui)
            for vj, uj in terms[idx + 1:]:
                self.add_quad(vi, vj, 2.0 * ui * uj)


@dataclass
class Qubo:
    n: int
    N: int
    const: float
    lin: np.ndarray
    quad: dict
    encoding: str
    slack_coeffs: list

    def energy(self, x) -> float:
        x = np.asarray(x, dtype=float)
        e = self.const + float(self.lin @ x)
        for (i, j), c in self.quad.items():
            e += c * x[i] * x[j]
        return e

    def energies_all(self, chunk: int = 1 << 20) -> np.ndarray:
        """Energy of every basis state, index bit k = variable k (float64, 2^n)."""
        n = self.n
        out = np.empty(1 << n)
        for start in range(0, 1 << n, chunk):
            idx = np.arange(start, min(start + chunk, 1 << n), dtype=np.int64)
            bits = [((idx >> k) & 1).astype(np.float64) for k in range(n)]
            e = np.full(idx.shape, self.const)
            for k in range(n):
                if self.lin[k] != 0.0:
                    e += self.lin[k] * bits[k]
            for (i, j), c in self.quad.items():
                e += c * bits[i] * bits[j]
            out[start:start + len(idx)] = e
        return out

    def max_abs_coeff(self) -> float:
        vals = list(np.abs(self.lin)) + [abs(c) for c in self.quad.values()]
        return max(vals) if vals else 1.0


def slack_coefficients(B: int) -> list:
    """Bounded binary expansion representing exactly 0..B."""
    if B <= 0:
        return []
    K = int(np.ceil(np.log2(B + 1)))
    coeffs = [2 ** k for k in range(K - 1)]
    coeffs.append(B - (2 ** (K - 1) - 1))
    return coeffs


def default_penalties(inst: Instance) -> dict:
    """Penalty weights large enough that any constraint violation costs more than
    the largest possible objective change from flipping one variable."""
    U = inst.unary_costs()
    span = float(U.max() - U.min())
    # a single flip of a_i changes the queue term by at most q * (N - 1)
    couple = sum(inst.Ec.values()) + sum(inst.En.values()) + inst.q * (inst.N - 1)
    big = span + couple + 1.0
    return {"lam_x": 2.0 * big, "lam_b": big, "lam_1": 1.0, "lam_2": 1.0}


def build_qubo(inst: Instance, encoding: str = "slack", pen: dict | None = None) -> Qubo:
    N = inst.N
    pen = {**default_penalties(inst), **(pen or {})}
    coeffs = slack_coefficients(inst.B) if encoding == "slack" and inst.B < N else []
    n = 2 * N + len(coeffs)
    a = lambda i: i
    s = lambda i: N + i
    q = QuboBuilder(n)

    U = inst.unary_costs()  # columns: go, stop, ask
    for i in range(N):
        # C p (1 - a - s) + stop_cost * s + ask_cost * a
        q.add_const(U[i, GO])
        q.add_lin(a(i), U[i, ASK] - U[i, GO])
        q.add_lin(s(i), U[i, STOP] - U[i, GO])
        q.add_quad(a(i), s(i), pen["lam_x"])          # cannot ask and stop

    for (i, j), w in inst.Ec.items():                 # w * h_i * h_j
        for u in (a(i), s(i)):
            for v_ in (a(j), s(j)):
                q.add_quad(u, v_, w)
    for (i, j), v in inst.En.items():                 # v * (1-a_i-s_i)(1-a_j-s_j)
        q.add_const(v)
        for u in (a(i), s(i), a(j), s(j)):
            q.add_lin(u, -v)
        for u in (a(i), s(i)):
            for v_ in (a(j), s(j)):
                q.add_quad(u, v_, v)

    for i in range(N):                                # operator queue: q * a_i * a_j
        for j in range(i + 1, N):
            if inst.q:
                q.add_quad(a(i), a(j), inst.q)

    if inst.B >= N:                                   # budget cannot bind: no penalty
        pass
    elif encoding == "slack":
        terms = [(a(i), 1.0) for i in range(N)]
        terms += [(2 * N + k, float(c)) for k, c in enumerate(coeffs)]
        lam_b = pen["lam_b"]
        sub = QuboBuilder(n)
        sub.add_square(terms, float(inst.B))
        q.add_const(lam_b * sub.const)
        q.lin += lam_b * sub.lin
        for key, c in sub.quad.items():
            q.add_quad(*key, lam_b * c)
    elif encoding == "unbalanced":
        # -lam_1 * eta + lam_2 * eta^2, eta = B - sum a
        l1, l2, B = pen["lam_1"], pen["lam_2"], float(inst.B)
        q.add_const(-l1 * B)
        for i in range(N):
            q.add_lin(a(i), l1)
        sub = QuboBuilder(n)
        sub.add_square([(a(i), -1.0) for i in range(N)], -B)  # (B - sum a)^2
        q.add_const(l2 * sub.const)
        q.lin += l2 * sub.lin
        for key, c in sub.quad.items():
            q.add_quad(*key, l2 * c)
    else:
        raise ValueError(encoding)

    return Qubo(n=n, N=N, const=q.const, lin=q.lin, quad=q.quad,
                encoding=encoding, slack_coeffs=coeffs)


# --------------------------------------------------------------------------- #
# Decoding
# --------------------------------------------------------------------------- #
INVALID = -1


def decode_index(idx: int, N: int) -> np.ndarray:
    a = np.array([(idx >> i) & 1 for i in range(N)])
    s = np.array([(idx >> (N + i)) & 1 for i in range(N)])
    return actions_from_bits(a, s)


def actions_from_bits(a, s) -> np.ndarray:
    a = np.asarray(a); s = np.asarray(s)
    act = np.full(a.shape, GO)
    act[(a == 1) & (s == 0)] = ASK
    act[(a == 0) & (s == 1)] = STOP
    act[(a == 1) & (s == 1)] = INVALID
    return act


def decode_all(N: int, n: int) -> tuple[np.ndarray, np.ndarray]:
    """For every basis index return (action code per robot as base-3 key, valid mask).
    Key encodes the decoded action vector so states sharing (a, s) map together."""
    idx = np.arange(1 << n, dtype=np.int64)
    key = np.zeros(idx.shape, dtype=np.int64)
    valid = np.ones(idx.shape, dtype=bool)
    for i in range(N):
        ai = (idx >> i) & 1
        si = (idx >> (N + i)) & 1
        valid &= ~((ai == 1) & (si == 1))
        code = np.where(ai == 1, ASK, np.where(si == 1, STOP, GO))
        key += code * (3 ** i)
    return key, valid
