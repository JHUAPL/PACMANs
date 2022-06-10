# Copyright 2022, The Johns Hopkins University Applied Physics Laboratory LLC
# All rights reserved.
# Distributed under the terms of the BSD 3-Clause License.

"""
An example of how to generate and store data produced from the box model in Numpy's npz format.
"""

import argparse
import json
import multiprocessing as mp
import os
import time
from copy import deepcopy

import numpy as np

from pybamocs.box_model import box_model
from pybamocs.box_model_args import dict_from_box_args, box_args_from_dict

BOX_ARGS_BASE = dict(N=4000, K_v=1e-5, A_GM=1000, M_ek=25e6, A_Redi=1000, M_SD=15e6, D_low0=400,
                     T_north0=2, T_south0=4, T_low0=17, T_deep0=3,
                     S_north0=35, S_south0=36, S_low0=36, S_deep0=34.5,
                     Fws=1e6, Fwn=0.05e6, epsilon=1.2e-4, area=3.6e14, area_low=2e14,
                     area_s=1e14, area_n=0.6e14, D_high=100, time_step_size_in_years=0.25
                     )

PARAM_ORDER = ['K_v', 'A_GM', 'M_ek', 'A_Redi', 'M_SD', 'D_low0', 'T_south0', 'T_north0', 'T_low0', 'T_deep0',
               'S_south0', 'S_north0', 'S_low0', 'S_deep0', 'Fws',
               'Fwn', 'epsilon', 'N']
DEFAULT_PARAMS = ['area=3.6e14', 'area_low=2e14', 'area_s=1e14', 'area_n=0.6e14', 'D_high=100',
                  'time_step_size_in_years=0.25']
RUN_COUNTER = -1


def copy_merge_dicts(d1, d2):
    d = deepcopy(d1)
    d.update(d2)
    return d


def make_save_dirs(d, res_dir):
    dir_names = [p + '=' + str(d[p]) for p in PARAM_ORDER]
    new_dir_path = os.path.join(res_dir, *dir_names)
    os.makedirs(new_dir_path, exist_ok=True)
    return new_dir_path


def make_gen_and_save_args(d, res_dir):
    global RUN_COUNTER
    new_dict = box_args_from_dict(copy_merge_dicts(BOX_ARGS_BASE, d))
    RUN_COUNTER += 1
    return new_dict, res_dir, os.path.join(res_dir, 'run_' + str(RUN_COUNTER)), False


def run_and_save_box_run(box_args, save_path, run_name, compressed=False):
    M_n, M_upw, M_eddy, D_Low, T, S, sigma_0 = box_model(**box_args).unpack()
    os.makedirs(os.path.join(save_path, run_name), exist_ok=True)
    params = dict_from_box_args(**box_args)
    json.dump(params, open(os.path.join(save_path, run_name, 'args.json'), 'w'))
    if compressed:
        np.savez_compressed(os.path.join(save_path, run_name, 'results.npz'),
                            M_n=M_n, M_upw=M_upw, M_eddy=M_eddy, D_Low=D_Low, T=T, S=S, sigma_0=sigma_0)
    else:
        np.savez(os.path.join(save_path, run_name, 'results.npz'),
                 M_n=M_n, M_upw=M_upw, M_eddy=M_eddy, D_Low=D_Low, T=T, S=S, sigma_0=sigma_0)
    return True


def gen_and_save_box_runs(run_specs: list, asynchronous=True, pool_size=12):
    if asynchronous:
        pool = mp.Pool(pool_size)
        res = pool.starmap_async(run_and_save_box_run, run_specs)
        res = res.get()
        pool.close()
        pool.join()
        if not all(res):
            print("Some runs failed? Finished: {}".format(res))
    else:
        for box_args, save_path, run_name, compressed in run_specs:
            run_and_save_box_run(box_args, save_path, run_name, compressed=compressed)


def main(results_directory):
    run_specs = [
        # box model args, path to results directory, save subdir name, compress
        make_gen_and_save_args({'M_ek': 15e6}, results_directory),
        make_gen_and_save_args({}, results_directory),
        make_gen_and_save_args({'M_ek': 35e6}, results_directory),
        make_gen_and_save_args({'D_low0': 100}, results_directory),
        make_gen_and_save_args({'M_ek': 35e6, 'D_low0': 100}, results_directory),
        make_gen_and_save_args({'M_ek': 15e6, 'D_low0': 100}, results_directory),
        # sim 2
        make_gen_and_save_args({'N': 8000, 'A_Redi': 500}, results_directory),
        make_gen_and_save_args({'N': 8000, 'A_Redi': 2000}, results_directory),
        make_gen_and_save_args({'N': 8000, 'A_Redi': 500, 'D_low0': 100}, results_directory),
        make_gen_and_save_args({'N': 8000, 'A_Redi': 2000, 'D_low0': 100}, results_directory),
        # sim 3
        make_gen_and_save_args({'epsilon': BOX_ARGS_BASE['epsilon'] / 2}, results_directory),
        make_gen_and_save_args({'epsilon': BOX_ARGS_BASE['epsilon'] * 2}, results_directory),
        make_gen_and_save_args({'epsilon': BOX_ARGS_BASE['epsilon'] / 2, 'D_low0': 100}, results_directory),
        make_gen_and_save_args({'epsilon': BOX_ARGS_BASE['epsilon'] * 2, 'D_low0': 100}, results_directory),
        # sim 4
        make_gen_and_save_args({'N': 8000, 'A_GM': 500}, results_directory),
        make_gen_and_save_args({'N': 8000, 'A_GM': 2000}, results_directory),
        make_gen_and_save_args({'N': 8000, 'A_GM': 500, 'D_low0': 100}, results_directory),
        make_gen_and_save_args({'N': 8000, 'A_GM': 2000, 'D_low0': 100}, results_directory),
        # sim 5
        make_gen_and_save_args({'N': 8000, 'K_v': 0}, results_directory),
        make_gen_and_save_args({'N': 8000, 'K_v': 05e-5}, results_directory),
        make_gen_and_save_args({'N': 8000, 'K_v': 0, 'D_low0': 100}, results_directory),
        make_gen_and_save_args({'N': 8000, 'K_v': 05e-5, 'D_low0': 100}, results_directory),
    ]

    start = time.time()
    gen_and_save_box_runs(run_specs, asynchronous=True, pool_size=12)
    print('time to generate and save {} specs: {} s'.format(len(run_specs), time.time() - start))


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Generate and save Box Model example data")
    parser.add_argument('save_dir', type=str, help="Path to directory where the data should be saved.")

    args = parser.parse_args()
    main(args.save_dir)
