import os
import json
import multiprocessing as mp

import numpy as np

from box_model import box_model


def run_and_save_box_run(box_args_dict, save_path, run_name, compressed=False):
    M_n, M_upw, M_eddy, Dlow, T, S, sigma0 = box_model(**box_args_dict)
    os.makedirs(os.path.join(save_path, run_name), exist_ok=True)
    json.dump(box_args_dict, open(os.path.join(save_path, run_name, 'args.json'), 'w'))
    if compressed:
        np.savez_compressed(os.path.join(save_path, run_name, 'results.npz'),
                            M_n=M_n, M_upw=M_upw, M_eddy=M_eddy, Dlow=Dlow, T=T, S=S, sigma0=sigma0)
    else:
        np.savez(os.path.join(save_path, run_name, 'results.npz'),
                 M_n=M_n, M_upw=M_upw, M_eddy=M_eddy, Dlow=Dlow, T=T, S=S, sigma0=sigma0)
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
