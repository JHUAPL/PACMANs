# Copyright 2022, The Johns Hopkins University Applied Physics Laboratory LLC
# All rights reserved.
# Distributed under the terms of the BSD 3-Clause License.

"""
Various utility functions for running the AMOC collapse examples.
"""

import multiprocessing as mp

import numpy as np

from pybamocs.box_model import box_model


def last_point_aredi(box_dims, box_init, box_params, box_ts):
    """
    Run the four box model for N steps, and then get the Nth entry of the following variables:
       M_n, M_u, M_eddy, sigma0 - sigma0, Dlow
     Primarily used for running multiprocessing
    """
    M_n, M_u, M_eddy, Dlow, T, S, sigma0 = box_model(box_dims, box_init, box_params, box_ts).unpack()
    return M_n[-1], M_u[-1], M_eddy[-1], sigma0[0, -1] - sigma0[2, -1], Dlow[-1]


def fba_run_n_steps(n_steps, box_dims, box_init, box_params, box_ts):
    Mnsave = np.zeros((n_steps, 1))
    Musave = np.zeros((n_steps, 1))
    Meddysave = np.zeros((n_steps, 1))
    dsigmasave = np.zeros((n_steps, 1))
    Dlowsave = np.zeros((n_steps, 1))
    for k in range(n_steps):
        Fwn = k * 0.05e6  # change to "k" due to reindexing to 0-based
        new_box_params = box_params.copy()
        new_box_params.Fwn = Fwn
        M_n, M_u, M_eddy, Dlow, T, S, sigma0 = box_model(box_dims, box_init, box_params, box_ts).unpack()
        Mnsave[k] = M_n[-1]
        Musave[k] = M_u[-1]
        Meddysave[k] = M_eddy[-1]
        dsigmasave[k] = sigma0[0, -1] - sigma0[2, -1]
        Dlowsave[k] = Dlow[-1]
    return Mnsave, Musave, Meddysave, dsigmasave, Dlowsave


def fba_run_n_steps_async(n_steps, box_dims, box_init, box_params, box_ts, poolsize=12):
    Mnsave = np.zeros((n_steps, 1))
    Musave = np.zeros((n_steps, 1))
    Meddysave = np.zeros((n_steps, 1))
    dsigmasave = np.zeros((n_steps, 1))
    Dlowsave = np.zeros((n_steps, 1))
    async_args = []
    for Fwn in np.arange(n_steps) * 0.05e6:
        new_box_params = box_params.copy()
        new_box_params.Fwn = Fwn
        async_args.append((box_dims, box_init, new_box_params, box_ts))
    pool = mp.Pool(poolsize)
    res = pool.starmap_async(last_point_aredi, async_args)
    res = res.get()
    pool.close()
    pool.join()
    for k in range(n_steps):
        Mnsave[k], Musave[k], Meddysave[k], dsigmasave[k], Dlowsave[k] = res[k]
    return Mnsave, Musave, Meddysave, dsigmasave, Dlowsave
