import multiprocessing as mp

import numpy as np

from box_model import box_model


def last_point_aredi(N, K_v, A_GM, M_ek, A_Redi, M_SD, D_low0, T_north0, T_south0, T_low0, T_deep0,
                     S_north0, S_south0, S_low0, S_deep0, Fws, Fwn, epsilon):
    """
    Run the four box model for N steps, and then get the Nth entry of the following variables:
       M_n, M_u, M_eddy, sigma0 - sigma0, Dlow
     Primarily used for running multiprocessing
    """
    M_n, M_u, M_eddy, Dlow, T, S, sigma0 = \
        box_model(N, K_v, A_GM, M_ek, A_Redi, M_SD, D_low0, T_north0, T_south0, T_low0, T_deep0,
                  S_north0, S_south0, S_low0, S_deep0, Fws, Fwn, epsilon)
    return M_n[-1], M_u[-1], M_eddy[-1], sigma0[0, -1] - sigma0[2, -1], Dlow[-1]


def fba_run_n_steps(n_steps, fourbox_args):
    # todo: docstring
    Mnsave = np.zeros((n_steps, 1))
    Musave = np.zeros((n_steps, 1))
    Meddysave = np.zeros((n_steps, 1))
    dsigmasave = np.zeros((n_steps, 1))
    Dlowsave = np.zeros((n_steps, 1))
    for k in range(n_steps):
        Fwn = k * 0.05e6  # change to "k" due to reindexing to 0-based
        fourbox_args['Fwn'] = Fwn
        M_n, M_u, M_eddy, Dlow, T, S, sigma0 = box_model(**fourbox_args)
        # Note: the "N-1" is used instead of "-1" because the arrays need to be 1 value longer than N for the loop in
        #   box_model() to work
        Mnsave[k] = M_n[-1]
        Musave[k] = M_u[-1]
        Meddysave[k] = M_eddy[-1]
        dsigmasave[k] = sigma0[0, -1] - sigma0[2, -1]
        Dlowsave[k] = Dlow[-1]
    return Mnsave, Musave, Meddysave, dsigmasave, Dlowsave


def fba_run_n_steps_async(n_steps, fourbox_args, poolsize=12):
    # todo: docstring
    Mnsave = np.zeros((n_steps, 1))
    Musave = np.zeros((n_steps, 1))
    Meddysave = np.zeros((n_steps, 1))
    dsigmasave = np.zeros((n_steps, 1))
    Dlowsave = np.zeros((n_steps, 1))
    async_args = [
        (fourbox_args['N'], fourbox_args['K_v'], fourbox_args['A_GM'], fourbox_args['M_ek'], fourbox_args['A_Redi'],
         fourbox_args['M_SD'], fourbox_args['D_low0'],
         fourbox_args['T_north0'], fourbox_args['T_south0'], fourbox_args['T_low0'], fourbox_args['T_deep0'],
         fourbox_args['S_north0'], fourbox_args['S_south0'], fourbox_args['S_low0'], fourbox_args['S_deep0'],
         fourbox_args['Fws'], Fwn, fourbox_args['epsilon']) for Fwn in
        np.arange(n_steps) * 0.05e6]
    pool = mp.Pool(poolsize)
    res = pool.starmap_async(last_point_aredi, async_args)
    res = res.get()
    pool.close()
    pool.join()
    for k in range(n_steps):
        Mnsave[k], Musave[k], Meddysave[k], dsigmasave[k], Dlowsave[k] = res[k]
    return Mnsave, Musave, Meddysave, dsigmasave, Dlowsave
