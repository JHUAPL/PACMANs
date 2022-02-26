import time
import argparse

from utils import gen_and_save_box_runs
from copy import deepcopy


def copy_merge_dicts(d1, d2):
    d = deepcopy(d1)
    d.update(d2)
    return d


def main(results_directory):
    box_args_base = dict(N=4000, Kv=1e-5, AI=1000, Mek=25e6, Aredi=1000, M_s=15e6, D0=400,
                         T0s=4, T0n=2, T0l=17, T0d=3, S0s=36, S0n=35, S0l=36, S0d=34.5,
                         Fws=1e6, Fwn=0.05e6, epsilon=1.2e-4
                         )
    run_specs = [
        # box model args, path to results directory, save subdir name, compress
        (copy_merge_dicts(box_args_base, {'Mek': 15e6}), results_directory, 'Mek=15e6', True),
        (deepcopy(box_args_base), results_directory, 'base_run_Mek=25e6', True),
        (copy_merge_dicts(box_args_base, {'Mek': 35e6}), results_directory, 'Mek=15e6', True),
        (copy_merge_dicts(box_args_base, {'Mek': 15e6}), results_directory, 'Mek=15e6', True),
        (copy_merge_dicts(box_args_base, {'Mek': 15e6, 'D0': 100}), results_directory, 'D0=100_Mek=15e6', True),
        (copy_merge_dicts(box_args_base, {'D0': 100}), results_directory, 'D0=100_Mek=25e6', True),
        (copy_merge_dicts(box_args_base, {'Mek': 35e6, 'D0': 100}), results_directory, 'D0=100_Mek=25e6', True),
        (copy_merge_dicts(box_args_base, {'Mek': 15e6}), results_directory, 'Mek=15e6', True),
        (copy_merge_dicts(box_args_base, {'Mek': 15e6}), results_directory, 'Mek=15e6', True),
    ]

    start = time.time()
    gen_and_save_box_runs(run_specs, asynchronous=True, pool_size=12)
    print('time to generate and save {} specs: {} s'.format(len(run_specs), time.time()-start))


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Generate and save Box Model example data")
    parser.add_argument('save_dir', type=str, help="Path to directory where the data should be saved.")

    args = parser.parse_args()
    main(args.save_dir)
