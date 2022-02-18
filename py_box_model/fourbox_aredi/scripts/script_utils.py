import numpy as np
from copy import deepcopy
from matplotlib import pyplot as plt
import multiprocessing as mp
from fourbox_aredi import fourbox_Aredi


def last_point_Aredi(N, Kv, AI, Mek, Aredi, M_s, D0, T0s, T0n, T0l, T0d, S0s, S0n, S0l, S0d, Fws, Fwn, epsilon):
    """
    Run the four box model for N steps, and then get the Nth entry of the following variables:
       M_n, M_u, M_eddy, sigma0 - sigma0, Dlow

    Primarily used for running multiprocessing
    :param N:
    :param Kv:
    :param AI:
    :param Mek:
    :param Aredi:
    :param M_s:
    :param D0:
    :param T0s:
    :param T0n:
    :param T0l:
    :param T0d:
    :param S0s:
    :param S0n:
    :param S0l:
    :param S0d:
    :param Fws:
    :param Fwn:
    :param epsilon:
    :return: list(np.array, np.array, np.array, np.array, np.array)
    """
    M_n, M_u, M_eddy, Dlow, T, S, sigma0 = \
        fourbox_Aredi(N, Kv, AI, Mek, Aredi, M_s, D0, T0s, T0n, T0l, T0d, S0s, S0n, S0l, S0d, Fws, Fwn, epsilon)
    return M_n[N - 1], M_u[N - 1], M_eddy[N - 1], sigma0[N - 1, 1] - sigma0[N - 1, 3], Dlow[N - 1]


def fba_run_n_steps(n_steps, fourbox_args):
    # todo: docstring
    Mnsave = np.zeros((n_steps, 1))
    Musave = np.zeros((n_steps, 1))
    Meddysave = np.zeros((n_steps, 1))
    dsigmasave = np.zeros((n_steps, 1))
    Dlowsave = np.zeros((n_steps, 1))
    N = fourbox_args['N']
    for k in range(n_steps):
        Fwn = k * 0.05e6  # change to "k" due to reindexing to 0-based
        fourbox_args['Fwn'] = Fwn
        M_n, M_u, M_eddy, Dlow, T, S, sigma0 = fourbox_Aredi(**fourbox_args)
        # Note: the "N-1" is used instead of "-1" because the arrays need to be 1 value longer than N for the loop in
        #   fourbox_Aredi() to work
        Mnsave[k] = M_n[N-1]
        Musave[k] = M_u[N-1]
        Meddysave[k] = M_eddy[N - 1]
        dsigmasave[k] = sigma0[N - 1, 1] - sigma0[N - 1, 3]
        Dlowsave[k] = Dlow[N - 1]
    return Mnsave, Musave, Meddysave, dsigmasave, Dlowsave


def fba_run_n_steps_async(n_steps, fourbox_args, poolsize=12):
    # todo: docstring
    Mnsave = np.zeros((n_steps, 1))
    Musave = np.zeros((n_steps, 1))
    Meddysave = np.zeros((n_steps, 1))
    dsigmasave = np.zeros((n_steps, 1))
    Dlowsave = np.zeros((n_steps, 1))
    async_args = [(fourbox_args['N'], fourbox_args['Kv'], fourbox_args['AI'], fourbox_args['Mek'], fourbox_args['Aredi'],
             fourbox_args['M_s'], fourbox_args['D0'], fourbox_args['T0s'], fourbox_args['T0n'], fourbox_args['T0l'],
             fourbox_args['T0d'], fourbox_args['S0s'], fourbox_args['S0n'], fourbox_args['S0l'], fourbox_args['S0d'],
             fourbox_args['Fws'], Fwn, fourbox_args['epsilon']) for Fwn in
                np.arange(n_steps) * 0.05e6]
    pool = mp.Pool(poolsize)
    res = pool.starmap_async(last_point_Aredi, async_args)
    res = res.get()
    pool.close()
    pool.join()
    for k in range(n_steps):
        Mnsave[k], Musave[k], Meddysave[k], dsigmasave[k], Dlowsave[k] = res[k]
    return Mnsave, Musave, Meddysave, dsigmasave, Dlowsave