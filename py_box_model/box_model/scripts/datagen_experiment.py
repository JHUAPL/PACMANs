import argparse
import datetime
from copy import deepcopy

import numpy as np

from box_model import box_model, NORTH_IDX, SOUTH_IDX, LOW_IDX, DEEP_IDX
from box_storage import store_run


def box_output_to_storage_dict(M_n, M_upw, M_eddy, D_low, T, S, sigma_0):
    variables = {'M_n': M_n, 'M_upw': M_upw, 'M_eddy': M_eddy, 'D_low': D_low, 'S_north': S[:, NORTH_IDX],
                 'S_south': S[:, SOUTH_IDX], 'S_low': S[:, LOW_IDX], 'S_deep': S[:, DEEP_IDX],
                 'T_north': T[:, NORTH_IDX], 'T_south': T[:, SOUTH_IDX], 'T_low': T[:, LOW_IDX],
                 'T_deep': T[:, DEEP_IDX], 'sigma_0_north': sigma_0[:, NORTH_IDX],
                 'sigma_0_south': sigma_0[:, SOUTH_IDX], 'sigma_0_low': sigma_0[:, LOW_IDX],
                 'sigma_0_deep': sigma_0[:, DEEP_IDX]}
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


def run_and_save_box_run(box_args_dict, netcdf_file, run_id, base_id):
    M_n, M_upw, M_eddy, D_low, T, S, sigma_0 = box_model(**box_args_dict)
    data = box_output_to_storage_dict(M_n, M_upw, M_eddy, D_low, T, S, sigma_0)
    when_generated = datetime.datetime.now()
    store_run(data, netcdf_file, run_id, when_generated, base_id, box_args_dict, find_sign_changes(M_n))
    return True


def main(netcdf_fp):
    BOX_ARGS_BASE = dict(N=4000, K_v=1e-5, A_GM=1000, M_ek=25e6, A_Redi=1000, M_SD=15e6, D_low0=400,
                         T_north0=2, T_south0=4, T_low0=17, T_deep0=3,
                         S_north0=35, S_south0=36, S_low0=36, S_deep0=34.5,
                         Fws=1e6, Fwn=0.05e6, epsilon=1.2e-4, area=3.6e14, area_low=2e14,
                         area_s=1e14, area_n=0.6e14, D_high=100, time_step_size_in_years=0.25
                         )

    perturbable = list(BOX_ARGS_BASE.keys())
    # remove variables that we don't want perturbed from the list of perturbable variables
    perturbable.remove('N')
    perturbable.remove('time_step_size_in_years')

    run_and_save_box_run(BOX_ARGS_BASE, netcdf_fp, 'base', 'None'),

    args_dict = {'base': BOX_ARGS_BASE}
    current_base_ids = ['base']
    iterations = 0
    max_iterations = 100
    run_idx = 0

    for i in range(10):
        num_samples = np.random.randint(1, 5)
        sample_indices = np.random.choice(np.arange(len(current_base_ids)), size=num_samples, replace=True)
        for idx in sample_indices:
            base_id = current_base_ids[idx]
            run_id = base_id + "_to_example_" + str(run_idx)
            run_idx += 1

            perturb_var = np.random.choice(perturbable)
            cur_value = args_dict[base_id][perturb_var]
            mag = np.log10(cur_value)
            new_value = cur_value + np.random.normal() * 10**(mag - 1)
            new_params = update_base_params(args_dict[base_id], {perturb_var: new_value})

            if len(current_base_ids) < 10 and np.random.uniform(0., 1.) < 0.25:
                current_base_ids.append(run_id)
                args_dict[run_id] = new_params

            run_and_save_box_run(new_params, netcdf_fp, run_id, base_id)
            iterations += 1

            if iterations > max_iterations:
                return

            if len(current_base_ids) > 6:
                pop_id = current_base_ids.pop(np.random.randint(0, len(current_base_ids)))
                args_dict.pop(pop_id)


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Generate and save Box Model example data")
    parser.add_argument('file_loc', type=str, help="Path to the desired NetCDF file.")

    args = parser.parse_args()
    main(args.file_loc)
