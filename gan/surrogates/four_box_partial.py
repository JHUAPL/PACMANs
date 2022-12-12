"""
Copyright 2022, The Johns Hopkins University Applied Physics Laboratory LLC
All rights reserved.
Distributed under the terms of the BSD 3-Clause License.

Approved for public release; distribution is unlimited.
This material is based upon work supported by the Defense Advanced Research Projects Agency (DARPA) under Agreement No.
HR00112290032.
"""
import os
import time
from copy import deepcopy
from typing import Optional, Iterable
from itertools import repeat
from multiprocessing import Pool

import numpy as np
from pybamocs.four_box_model.box_model import box_model
from pybamocs.four_box_model.box_model_args import box_args_from_dict
from pybamocs.four_box_model.constants import PARAMS

ARGS_DICT = {
    "box_dimensions": ["area", "area_low", "area_s", "area_n", "D_high"],
    "init_conditions": ["D_low0", "T_north0", "T_south0", "T_low0", "T_deep0", "S_north0", "S_south0", "S_low0", "S_deep0"],
    "box_params": ["K_v", "A_GM", "M_ek", "A_Redi", "M_SD", "Fws", "Fwn" ,"epsilon"],
    "time_step": ["N", ""],
    "randomization": ["rng_seed", "noise_amplification"]}

class FourBoxPartialModel(object):
	def __init__(self, perturb_vars: Iterable, constants_dict: dict, perturb_min: Iterable, perturb_max: Iterable,
		N_values: Optional[Iterable] = None,
		ts_values: Optional[Iterable] = None, 
		n_jobs: int = 12):

		self.perturb_vars = perturb_vars
		self.constants_dict = constants_dict
		self.perturb_min = perturb_min
		self.perturb_max = perturb_max

		# Categories for N, time_step_size
		self.N_cats = N_values
		self.step_size_cats = ts_values
		self.n_jobs = n_jobs

	def __call__(self, x_perturb, debug=False):
		# Set up iter_seeds
		n = x_perturb.shape[0]
		box_dims, init_conditions, box_params, time_steps, rands = [], [], [], [], []

		for i in range(n):
			# Create perturbation w/ constants
			# todo: handle N and time_step_size_in_years after
			i_dict = {k:v for k,v in zip(self.perturb_vars, x_perturb[i, :])}
			i_dict.update(self.constants_dict)

			# Get dict of box_args, update arrays
			i_dict = box_args_from_dict(i_dict)
			box_dims.append(i_dict["box_dimensions"])
			init_conditions.append(i_dict["init_conditions"])
			box_params.append(i_dict["box_params"])
			time_steps.append(i_dict["time_step"])
			rands.append(i_dict["randomization"])

		iter_seeds = zip(box_dims, init_conditions, box_params, time_steps, rands)

		# Call the model and solve equations
		if debug:
			print("Number of processes: ", self.n_jobs)
			start_t = time.time()

		# num_jobs = min(x_perturb.shape[0], 12)
		n_jobs = min(self.n_jobs, x_perturb.shape[0])

		if n_jobs == 1:
			results = [box_model(*args) for args in iter_seeds]
		else:
			with Pool(processes=n_jobs) as pool:
				results = pool.starmap_async(
					box_model,
					iterable=iter_seeds,
					chunksize=n // n_jobs
				)
				results = results.get()
				pool.close()
				pool.join()

		if debug:
			end_t = time.time()
			print("Time elapsed (min.): ", (end_t - start_t)/60.)

		# Get maximum output length
		max_out_len = max([r.M_n.shape[0] for r in results])

		# Unpack each result
		M_n_results, M_upw_results, M_eddy_results, \
			D_low_results, T_results, S_results, sigma0_results = map(list, zip(*[r.unpack() for r in results]))


		# Pad each input to max_out_len
		for i, r in enumerate(results):
			r_shape = r.M_n.shape[0]
			r_pad = max_out_len - r.M_n.shape[0]
			M_n_results[i] = np.pad(M_n_results[i], pad_width=(r_pad, 0), mode="constant", constant_values=(np.nan, np.nan))
			M_upw_results[i] = np.pad(M_upw_results[i], pad_width=(r_pad, 0), mode="constant", constant_values=(np.nan, np.nan))
			M_eddy_results[i] = np.pad(M_eddy_results[i], pad_width=(r_pad, 0), mode="constant", constant_values=(np.nan, np.nan))
			D_low_results[i] = np.pad(D_low_results[i], pad_width=(r_pad, 0), mode="constant", constant_values=(np.nan, np.nan))
			T_results[i] = np.pad(T_results[i], pad_width=((0, 0), (r_pad, 0)), mode="constant", constant_values=((np.nan, np.nan), (np.nan, np.nan)))
			S_results[i] = np.pad(S_results[i], pad_width=((0, 0), (r_pad, 0)), mode="constant", constant_values=((np.nan, np.nan), (np.nan, np.nan)))
			sigma0_results[i] = np.pad(sigma0_results[i], pad_width=((0, 0), (r_pad, 0)), mode="constant", constant_values=((np.nan, np.nan), (np.nan, np.nan)))

		# Aggregate all results from each process (if applicable), and return ALL MODEL OUTPUTS
		M_n_results = np.stack(M_n_results, axis=0)
		M_upw_results = np.stack(M_upw_results, axis=0)
		M_eddy_results = np.stack(M_eddy_results, axis=0)
		D_low_results = np.stack(D_low_results, axis=0)
		T_results = np.stack(T_results, axis=0)
		S_results = np.stack(S_results, axis=0)
		sigma0_results = np.stack(sigma0_results, axis=0)

		return M_n_results, M_upw_results, M_eddy_results, \
			D_low_results, T_results, S_results, sigma0_results

	def get_discrete_values(self, array: np.ndarray,
		values: Iterable = np.array([1/12, 1/4, 1/2, 1.0])):
		# get probabilities for each category
		probs = np.linspace(-1, 1, len(values)+1)

		# map each idx to the discrete value
		idx_array = []
		for i in range(len(values)):
			idxs = np.argwhere((probs[i] <= array) & (array < probs[i+1])).flatten()
			idx_array.append(idxs)
		for idxs, val in zip(idx_array, values):
			array[idxs] = val

		return array
