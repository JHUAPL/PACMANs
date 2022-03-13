import os
import json
import multiprocessing as mp

import numpy as np
import pandas as pd

from box_model import box_model


def run_and_save_box_run(box_args_dict, save_path, run_name, compressed=False):
    M_n, M_upw, M_eddy, D_low, T, S, sigma_0 = box_model(**box_args_dict)
    os.makedirs(os.path.join(save_path, run_name), exist_ok=True)
    json.dump(box_args_dict, open(os.path.join(save_path, run_name, 'args.json'), 'w'))
    if compressed:
        np.savez_compressed(os.path.join(save_path, run_name, 'results.npz'),
                            M_n=M_n, M_upw=M_upw, M_eddy=M_eddy, D_low=D_low, T=T, S=S, sigma_0=sigma_0)
    else:
        # np.savez(os.path.join(save_path, run_name, 'results.npz'),
        #          M_n=M_n, M_upw=M_upw, M_eddy=M_eddy, Dlow=Dlow, T=T, S=S, sigma0=sigma0)
        d = dict(
            M_n=M_n.reshape(-1), M_upw=M_upw.reshape(-1), M_eddy=M_eddy.reshape(-1), Dlow=D_low.reshape(-1),
            Tn=T[:, 0], Ts=T[:, 1], Tl=T[:, 2], Td=T[:, 3],
            Sn=S[:, 0], Ss=S[:, 1], Sl=S[:, 2], Sd=S[:, 3],
            sigma0n=sigma_0[:, 0], sigma0s=sigma_0[:, 1], sigma0l=sigma_0[:, 2], sigma0d=sigma_0[:, 3]
        )
        df = pd.DataFrame(d)
        df.to_csv(os.path.join(save_path, run_name, 'results.csv'))
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
