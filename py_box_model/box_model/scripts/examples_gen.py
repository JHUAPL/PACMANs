import argparse
import os
import time
from copy import deepcopy

from utils import gen_and_save_box_runs

BOX_ARGS_BASE = dict(N=4000, Kv=1e-5, AI=1000, Mek=25e6, Aredi=1000, M_s=15e6, D0=400,
                     T0s=4, T0n=2, T0l=17, T0d=3, S0s=36, S0n=35, S0l=36, S0d=34.5,
                     Fws=1e6, Fwn=0.05e6, epsilon=1.2e-4
                     )

PARAM_ORDER = ['Kv', 'AI', 'Mek', 'Aredi', 'M_s', 'D0', 'T0s', 'T0n', 'T0l', 'T0d', 'S0s', 'S0n', 'S0l', 'S0d', 'Fws',
               'Fwn', 'epsilon', 'N']
DEFAULT_PARAMS = ['area=3.6e14', 'area_low=2e14', 'area_s=1e14', 'area_n=0.6e14', 'Dhigh=100',
                  'timestep_size_in_years=0.25']
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


def make_gen_and_save_args_complex(d, res_dir):
    """
    DEPRECATED. Here for reference as needed for current time. Will delete once sure it
        is no longer useful.
    """
    new_dict = copy_merge_dicts(BOX_ARGS_BASE, d)
    return new_dict, res_dir, make_save_dirs(new_dict, res_dir), False


def make_gen_and_save_args(d, res_dir):
    global RUN_COUNTER
    new_dict = copy_merge_dicts(BOX_ARGS_BASE, d)
    RUN_COUNTER += 1
    return new_dict, res_dir, os.path.join(res_dir, 'run_' + str(RUN_COUNTER)), False


def main(results_directory):
    run_specs = [
        # box model args, path to results directory, save subdir name, compress
        make_gen_and_save_args({'Mek': 15e6}, results_directory),
        make_gen_and_save_args({}, results_directory),
        make_gen_and_save_args({'Mek': 35e6}, results_directory),
        make_gen_and_save_args({'D0': 100}, results_directory),
        make_gen_and_save_args({'Mek': 35e6, 'D0': 100}, results_directory),
        make_gen_and_save_args({'Mek': 15e6, 'D0': 100}, results_directory),
        # sim 2
        make_gen_and_save_args({'N': 8000, 'Aredi': 500}, results_directory),
        make_gen_and_save_args({'N': 8000, 'Aredi': 2000}, results_directory),
        make_gen_and_save_args({'N': 8000, 'Aredi': 500, 'D0': 100}, results_directory),
        make_gen_and_save_args({'N': 8000, 'Aredi': 2000, 'D0': 100}, results_directory),
        # sim 3
        make_gen_and_save_args({'epsilon': BOX_ARGS_BASE['epsilon'] / 2}, results_directory),
        make_gen_and_save_args({'epsilon': BOX_ARGS_BASE['epsilon'] * 2}, results_directory),
        make_gen_and_save_args({'epsilon': BOX_ARGS_BASE['epsilon'] / 2, 'D0': 100}, results_directory),
        make_gen_and_save_args({'epsilon': BOX_ARGS_BASE['epsilon'] * 2, 'D0': 100}, results_directory),
        # sim 4
        make_gen_and_save_args({'N': 8000, 'AI': 500}, results_directory),
        make_gen_and_save_args({'N': 8000, 'AI': 2000}, results_directory),
        make_gen_and_save_args({'N': 8000, 'AI': 500, 'D0': 100}, results_directory),
        make_gen_and_save_args({'N': 8000, 'AI': 2000, 'D0': 100}, results_directory),
        # sim 5
        make_gen_and_save_args({'N': 8000, 'Kv': 0}, results_directory),
        make_gen_and_save_args({'N': 8000, 'Kv': 05e-5}, results_directory),
        make_gen_and_save_args({'N': 8000, 'Kv': 0, 'D0': 100}, results_directory),
        make_gen_and_save_args({'N': 8000, 'Kv': 05e-5, 'D0': 100}, results_directory),
    ]

    start = time.time()
    gen_and_save_box_runs(run_specs, asynchronous=True, pool_size=12)
    print('time to generate and save {} specs: {} s'.format(len(run_specs), time.time()-start))


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Generate and save Box Model example data")
    parser.add_argument('save_dir', type=str, help="Path to directory where the data should be saved.")

    args = parser.parse_args()
    main(args.save_dir)
