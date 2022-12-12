import json
import os

import numpy as np

from pybamocs.four_box_model.box_model import box_model
from pybamocs.four_box_model.box_model_args import dict_from_box_args


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