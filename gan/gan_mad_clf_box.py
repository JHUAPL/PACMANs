"""
Copyright 2022, The Johns Hopkins University Applied Physics Laboratory LLC
All rights reserved.
Distributed under the terms of the BSD 3-Clause License.

Approved for public release; distribution is unlimited.
This material is based upon work supported by the Defense Advanced Research Projects Agency (DARPA) under Agreement No.
HR00112290032.
"""
import sys
import json
import pickle

import numpy as np

from gan_mad_clf import GANTrainer
from surrogates.four_box_partial import FourBoxPartialModel
from gan_utils.label_funcs import get_gen_mad_labels, get_disc_mad_labels, get_gen_soft_clf_labels, get_disc_clf_labels, get_disc_clf_labels_three_class
from gan_utils.losses import mad_clf_loss

if __name__ == "__main__":

	# Loss functions
	gen_loss_func = mad_clf_loss
	disc_loss_func = mad_clf_loss

    # Retrieve save directory, data directory, cuda visible device
	save_dir, save_subdir, load_data_path, device, n_gens, sim_config_file, chkpt_idx, \
		n_jobs, n_classes = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5]), sys.argv[6], int(sys.argv[7]), int(sys.argv[8]), int(sys.argv[9])


	# Labelling functions
	gen_mad_label_func, disc_mad_label_func = get_gen_mad_labels, get_disc_mad_labels
	gen_clf_label_func = get_gen_soft_clf_labels
	if n_classes == 3:
		disc_clf_label_func = get_disc_clf_labels_three_class
		class_names = ["No shutoff", "Shutoff", "Recovery"]
	else:
		disc_clf_label_func = get_disc_clf_labels
		class_names = ["No shutoff", "Shutoff"]

	# Set up surrogate model
	with open(sim_config_file, "r") as f:
		surrogate_kwargs = json.load(f)
	surrogate_kwargs.pop("n_samples")
	surrogate_model = FourBoxPartialModel(n_jobs=n_jobs, **surrogate_kwargs)

	# n_gens = 2
	x_size = len(surrogate_model.perturb_vars)
	z_size = 64

	gan = GANTrainer(n_gens, x_size, class_names, z_size, surrogate_model=surrogate_model,
					gen_loss_func=gen_loss_func, disc_loss_func=disc_loss_func,
					gen_mad_label_func=gen_mad_label_func, disc_mad_label_func=disc_mad_label_func,
					gen_clf_label_func=gen_clf_label_func, disc_clf_label_func=disc_clf_label_func,
					mb_disc_out=128, device=device, save_dir=save_dir, save_subdir=save_subdir, load_data_path=load_data_path,
					chkpt_idx=chkpt_idx, chkpt_freq=10)

	# # Test training loop
	# gan.train(n_iterations=1000, gen_mb_size=128, real_mb_size=128, debug=False)
	gan.train(n_iterations=500, gen_mb_size=32, real_mb_size=32, debug=False)
	# gan.train(n_iterations=1, gen_mb_size=12, real_mb_size=12, debug=True)