# -*- coding: utf-8 -*-
''' Soiling Module

This module is for analyzing soiling trends in performance index (PI) data/

'''

import numpy as np
import cvxpy as cvx

def soiling_seperation_algorithm_v2(observed, iterations=5, weights=None, known_set=None, lmbda1=500, lmbda2=0.1,
                                 lmbda3=1e-5):
    if weights is None:
        weights =  np.ones_like(observed)
    if known_set is None:
        known_set = ~np.isnan(observed)
    data = np.ones_like(observed) * np.nan
    data[known_set] = np.log10(observed[known_set])
    w = np.ones(len(observed) - 2)
    zero_set = np.zeros(len(observed) - 1, dtype=np.bool)
    eps = 1e-5
    lmbda1 = cvx.Parameter(value=lmbda1, nonneg=True)
    lmbda2 = cvx.Parameter(value=lmbda2, nonneg=True)
    for i in range(iterations):
        n = len(observed)
        s1 = cvx.Variable(n) # error
        s2 = cvx.Variable(n) # seasonal
        s3 = cvx.Variable(n) # soiling
        s4 = cvx.Variable(n) # long term deg
        cost = cvx.norm(cvx.multiply(s1, weights), p=2) \
            + lmbda1 * cvx.sum_squares(cvx.diff(s2, k=2)) \
            + lmbda2 * cvx.norm(cvx.multiply(w, cvx.diff(s3, k=2)), p=1) \
            + lmbda3 * cvx.norm1(s3)
        objective = cvx.Minimize(cost)
        constraints = [
            data[known_set] == s1[known_set] + s2[known_set] + s3[known_set] + s4[known_set],
            #cvx.diff(s1, k=1) >= -1e-3,
            s2[365:] - s2[:-365] == 0,
            cvx.sum(s2[:365]) == 0,
            s3 <= 0,
            cvx.diff(s4, k=2) == 0,
            s4[0] == 0
        ]
#         if np.sum(zero_set) > 0:
#             constraints.append(cvx.diff(s1, k=1)[zero_set] == 0)
        problem = cvx.Problem(objective, constraints)
        problem.solve(solver='MOSEK')
        w = 1 / (eps + np.abs(cvx.diff(s1, k=2).value))   # Reweight the L1 penalty
#         zero_set = np.abs(cvx.diff(s1, k=1).value) <= 5e-5     # Make nearly flat regions exactly flat (sparse 1st diff)
    return s1.value, s2.value, s3.value, s4.value

def soiling_seperation(observed, index_set=None, degradation_term=False,
                       tau=0.85, c1=2, c2=1e-2, c3=100, iterations=5,
                       soiling_max=1.0, solver='MOSEK'):
    """
    Apply signal decomposition framework to Performance Index soiling estimation
    problem. The PI signal is a daily performance index, typically daily energy
    normalized by modeled or expected energy. PI signal assumed to contain
    components corresponding to

    (1) a soiling loss trend (sparse 1st-order differences)
    (2) a seasonal term (smooth, yearly periodic)
    (3) linear degradation
    (4) residual

    :param observed:
    :param index_set:
    :param degradation_term:
    :param tau:
    :param c1: PWL weight - soiling term
    :param c2: sparseness weight - soiling term
    :param c3: smoothness weight - seasonal term
    :param iterations:
    """
    if index_set is None:
        index_set = ~np.isnan(observed)
    else:
        index_set = np.logical_and(index_set, ~np.isnan(observed))
    zero_set = np.zeros(len(observed) - 1, dtype=np.bool)
    eps = .01
    n = len(observed)
    s1 = cvx.Variable(n)            # soiling
    s2 = cvx.Variable(max(n, 367))  # seasonal
    s3 = cvx.Variable(n)            # degradation
    sr = cvx.Variable(n)            # residual
    # z = cvx.Variable(2)
    # T = len(observed)
    # M = np.c_[np.ones(T), np.arange(T)]
    w = cvx.Parameter(n - 2, nonneg=True)
    w.value = np.ones(len(observed) - 2)
    for i in range(iterations):
        # cvx.norm(cvx.multiply(s3, weights), p=2) \

        cost = cvx.sum(tau * cvx.pos(sr) +(1 - tau) * cvx.neg(sr)) \
               + c3 * cvx.norm(cvx.diff(s2[:n], k=2), p=2) \
               + c1 * cvx.norm(cvx.multiply(w, cvx.diff(s1, k=2)), p=1) \
               + c2 * cvx.sum(1 - s1)
        objective = cvx.Minimize(cost)
        constraints = [
            observed[index_set] == (s1 + s2[:n] + s3 + sr)[index_set],
            s2[365:] - s2[:-365] == 0,
            cvx.sum(s2[:365]) == 0,
            s1 <= soiling_max
        ]
        if degradation_term:
            constraints.extend([
                cvx.diff(s3, k=2) == 0,
                s3[0] == 0
            ])
        else:
            constraints.append(
                s3 == 0
            )
        if np.sum(zero_set) > 0:
            constraints.append(cvx.diff(s1, k=1)[zero_set] == 0)
        if n < 0.75 * 365:
            constraints.append(s2 == 0)
        problem = cvx.Problem(objective, constraints)
        problem.solve(solver=solver)
        w.value = 1 / (eps + 1e2* np.abs(cvx.diff(s1, k=2).value))   # Reweight the L1 penalty
        zero_set = np.abs(cvx.diff(s1, k=1).value) <= 5e-5     # Make nearly flat regions exactly flat (sparse 1st diff)
    return s1.value, s2.value[:n], s3.value, sr.value