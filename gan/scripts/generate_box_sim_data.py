"""
Copyright 2022, The Johns Hopkins University Applied Physics Laboratory LLC
All rights reserved.
Distributed under the terms of the BSD 3-Clause License.

Approved for public release; distribution is unlimited.
This material is based upon work supported by the Defense Advanced Research Projects Agency (DARPA) under Agreement No.
HR00112290032.
"""

import sys
import os
import time
import argparse
import json
import pickle
from multiprocessing import Pool
from itertools import repeat

import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split

if ".." not in sys.path:
    sys.path.append("..")
from surrogates.four_box_partial import FourBoxPartialModel
from gan_utils.label_funcs import get_disc_clf_labels_three_class


def gen_data(*iter_args):
    if iter_args[0] % 10 == 0:
        print(f"Running idx {iter_args[0]}...")
    return box_model(*iter_args[1:])


if __name__ == "__main__":
    # Generate argument parser
    args_order = ["N", "K_v", "A_GM", "M_ek", "A_Redi", "M_SD", "D_low0",
                  "T_north0", "T_south0", "T_low0", "T_deep0",
                  "S_north0", "S_south0", "S_low0", "S_deep0",
                  "Fws", "Fwn", "epsilon", "area", "area_low",
                  "area_s", "area_n", "D_high", "time_step_size_in_years"]
    parser = argparse.ArgumentParser()
    parser.add_argument("config_file", type=str, help="path to simulation config file.")
    parser.add_argument("save_file", type=str, help="Location to save off simulation data.")
    parser.add_argument("n_jobs", type=int, help="Number of jobs to launch.", default=3)
    parser.add_argument("slice_size", type=int, help="Number of configs to generate per array job.", default=10000)
    args = parser.parse_args()

    # Load sim config_file
    with open(args.config_file, "r") as f:
        cfg = json.loads(f.read())

    # Set up
    feature_range = (-1., 1.)
    ic_param_scaler = MinMaxScaler(feature_range=feature_range)
    ic_param_scaler.data_min_ = np.array(cfg["perturb_min"])
    ic_param_scaler.data_max_ = np.array(cfg["perturb_max"])
    ic_param_scaler.scale_ = (feature_range[1] - feature_range[0]) / (
                ic_param_scaler.data_max_ - ic_param_scaler.data_min_)
    ic_param_scaler.min_ = feature_range[0] - ic_param_scaler.data_min_ * ic_param_scaler.scale_

    # Sample from uniform normal distribution
    n_samples = cfg["n_samples"]
    # n_samples = 50
    n_vars = len(cfg["perturb_vars"])
    np.random.seed(0)
    rand_seeds = np.random.uniform(-1, 1, (n_samples, n_vars))

    # Use slurm array task_id to slice into array
    slurm_array_task_id = int(os.environ["SLURM_ARRAY_TASK_ID"])
    slice_start_idx = args.slice_size * (slurm_array_task_id - 1)
    slice_end_idx = args.slice_size * slurm_array_task_id
    print(f"Running configs: {slice_start_idx} to {slice_end_idx}.")

    # Inverse transform
    X = ic_param_scaler.inverse_transform(rand_seeds[slice_start_idx:slice_end_idx])

    # Create box partial model
    print("Number of available CPU cores: ", os.cpu_count())
    with open(args.config_file, "r") as f:
        surrogate_kwargs = json.load(f)
    surrogate_kwargs.pop("n_samples")
    box_surrogate = FourBoxPartialModel(n_jobs=args.n_jobs, **surrogate_kwargs)

    M_n_results, M_upw_results, M_eddy_results, \
    D_low_results, T_results, S_results, sigma0_results = box_surrogate(X, debug=True)

    # Get labels
    label_func = get_disc_clf_labels_three_class
    result_labels = label_func(
        (M_n_results, M_upw_results, M_eddy_results, D_low_results, T_results, S_results, sigma0_results))
    last_M_n = M_n_results[:, -1]

    # Handle class imbalance
    n_shutoffs = result_labels[result_labels == 1].size
    n_non_shutoffs = result_labels[result_labels == 0].size
    n_rec_shutoffs = result_labels[result_labels == 2].size
    print("Number of classes: ", np.unique(result_labels))

    print("Number of shutoffs: ", n_shutoffs)
    print("Number of non-shutoffs: ", n_non_shutoffs)
    print("Number of recoveries: ", n_rec_shutoffs)

    X_save = X
    save_labels = result_labels
    save_M_n = last_M_n
    print("Size of saved dataset: ", X_save.shape)
    print("Number of shutoffs: ", save_labels.sum())

    # Train-test split
    if X_save.shape[0] > 0:
        X_train, X_test, y_train, y_test = train_test_split(X_save, save_labels, test_size=0.2, random_state=0)
        print("Training set size: ", X_train.shape[0])
        print("Test set size: ", X_test.shape[0])
        print()
    else:
        print("No shutoffs found in this slice...")
        exit(0)

    # Save data_dict
    data_dict = dict(sample=X_save, labels=save_labels, scaler=ic_param_scaler, last_M_n=save_M_n,
                     train_sample=X_train, train_labels=y_train, test_sample=X_test, test_labels=y_test)
    with open(args.save_file, "wb") as f:
        pickle.dump(data_dict, f, protocol=pickle.HIGHEST_PROTOCOL)
