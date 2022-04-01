# Copyright 2022, The Johns Hopkins University Applied Physics Laboratory LLC
# All rights reserved.
# Distributed under the terms of the BSD 3-Clause License.

"""
An example of how to generate and store data produced from the box model in NetCDF format.
"""

import argparse
import datetime
from copy import deepcopy

import numpy as np

from py_box_model.box_model import box_model, NORTH_IDX, SOUTH_IDX, LOW_IDX, DEEP_IDX
from py_box_model.box_model_args import box_args_from_dict, dict_from_box_args
from py_box_model.box_storage import store_run


def box_output_to_storage_dict(M_n, M_upw, M_eddy, D_low, T, S, sigma_0):
    variables = {
        'M_n': M_n, 'M_upw': M_upw, 'M_eddy': M_eddy, 'D_low': D_low,
        'S_north': S[:, NORTH_IDX], 'S_south': S[:, SOUTH_IDX], 'S_low': S[:, LOW_IDX], 'S_deep': S[:, DEEP_IDX],
        'T_north': T[:, NORTH_IDX], 'T_south': T[:, SOUTH_IDX], 'T_low': T[:, LOW_IDX], 'T_deep': T[:, DEEP_IDX],
        'sigma_0_north': sigma_0[:, NORTH_IDX], 'sigma_0_south': sigma_0[:, SOUTH_IDX],
        'sigma_0_low': sigma_0[:, LOW_IDX], 'sigma_0_deep': sigma_0[:, DEEP_IDX]}
    return variables


def update_base_params(base_params, updates):
    d = deepcopy(base_params)
    d.update(updates)
    return d


def find_sign_changes(arr):
    asign = np.sign(arr)
    signchange = ((np.roll(asign, 1) - asign) != 0).astype(int)
    signchange[0] = 0  # don't check if first and last elements have sign change
    if signchange.any():
        return np.where(signchange == 1)[0]
    return None


def run_and_save_box_run(box_args, netcdf_file, run_id, base_id):
    results = box_model(**box_args)
    M_n, M_upw, M_eddy, D_low, T, S, sigma_0 = results.unpack()
    data = box_output_to_storage_dict(M_n, M_upw, M_eddy, D_low, T, S, sigma_0)
    when_generated = datetime.datetime.now()
    params = dict_from_box_args(**box_args)
    store_run(data, netcdf_file, run_id, when_generated, base_id, params, find_sign_changes(M_n))
    return True


def main(netcdf_fp):
    BOX_ARGS_BASE = dict(N=4000, K_v=1e-5, A_GM=1000, M_ek=25e6, A_Redi=1000, M_SD=15e6, D_low0=400,
                         T_north0=2, T_south0=4, T_low0=17, T_deep0=3,
                         S_north0=35, S_south0=36, S_low0=36, S_deep0=34.5,
                         Fws=1e6, Fwn=0.05e6, epsilon=1.2e-4, area=3.6e14, area_low=2e14,
                         area_s=1e14, area_n=0.6e14, D_high=100, time_step_size_in_years=0.25
                         )

    perturbations = [{'M_ek': 15e6},
                     {'M_ek': 35e6},
                     {'D_low0': 100},
                     {'M_ek': 35e6, 'D_low0': 100},
                     {'M_ek': 15e6, 'D_low0': 100},
                     # sim 2
                     {'N': 8000, 'A_Redi': 500},
                     {'N': 8000, 'A_Redi': 2000},
                     {'N': 8000, 'A_Redi': 500, 'D_low0': 100},
                     {'N': 8000, 'A_Redi': 2000, 'D_low0': 100},
                     # sim 3
                     {'epsilon': BOX_ARGS_BASE['epsilon'] / 2},
                     {'epsilon': BOX_ARGS_BASE['epsilon'] * 2},
                     {'epsilon': BOX_ARGS_BASE['epsilon'] / 2, 'D_low0': 100},
                     {'epsilon': BOX_ARGS_BASE['epsilon'] * 2, 'D_low0': 100},
                     # sim 4
                     {'N': 8000, 'A_GM': 500},
                     {'N': 8000, 'A_GM': 2000},
                     {'N': 8000, 'A_GM': 500, 'D_low0': 100},
                     {'N': 8000, 'A_GM': 2000, 'D_low0': 100},
                     # sim 5
                     {'N': 8000, 'K_v': 0},
                     {'N': 8000, 'K_v': 05e-5},
                     {'N': 8000, 'K_v': 0, 'D_low0': 100},
                     {'N': 8000, 'K_v': 05e-5, 'D_low0': 100}
                     ]

    run_and_save_box_run(box_args_from_dict(BOX_ARGS_BASE), netcdf_fp, 'base', 'None'),

    for i, p in enumerate(perturbations):
        box_args = box_args_from_dict(update_base_params(BOX_ARGS_BASE, p))
        run_and_save_box_run(box_args, netcdf_fp, 'example' + str(i), 'base')


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Generate and save Box Model example data")
    parser.add_argument('file_loc', type=str, help="Path to the desired NetCDF file.")

    args = parser.parse_args()
    main(args.file_loc)
