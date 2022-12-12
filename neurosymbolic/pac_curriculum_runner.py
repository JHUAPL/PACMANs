# Copyright 2022, The Johns Hopkins University Applied Physics Laboratory LLC
# All rights reserved.
# Distributed under the terms of the BSD 3-Clause License.

# Approved for public release; distribution is unlimited.
# This material is based upon work supported by the Defense Advanced Research Projects Agency (DARPA) under Agreement
# No. HR00112290032.

import os
import time

import numpy as np
import seaborn as sns
from matplotlib import pyplot as plt
from torch.utils.data import DataLoader

from .datasets.pac_dataset import PACDatasetConfig
from .pac_runner import PACRunner, DataCollect, get_correct_dataset
from .utils import custom_collate_d


class PACCurriculumRunnerConfig:
    def __init__(self, save_loc, dataset_configs: list, run_configs: list, final_test_dataset_config: PACDatasetConfig):
        self.save_loc = save_loc
        self.dataset_configs = dataset_configs
        self.run_configs = run_configs
        self.final_dataset_config = final_test_dataset_config
        if len(self.dataset_configs) != len(self.run_configs):
            raise ValueError(f"Must be the same number of datasets as run configs! Got {len(self.dataset_configs)}"
                             f"dataset configs and {len(self.run_configs)} configs.")


class PACCurriculumRunner:
    def __init__(self, config: PACCurriculumRunnerConfig):
        self.config = config
        self.save_loc = config.save_loc
        self.dataset_configs = config.dataset_configs
        self.run_configs = config.run_configs
        self.final_dataset_config = config.final_dataset_config

    def run(self):
        timer_start, dt_start = time.time(), time.localtime()
        str_start_time = time.strftime("%H:%M, %d/%m/%y", dt_start)
        print(f'Started curriculum at {str_start_time}')
        curriculum_data_collect = DataCollect()
        curriculum_data_collect.set("start_time", str_start_time)
        runner = None
        losses = []
        for c, (data_cfg, run_cfg) in enumerate(zip(self.dataset_configs, self.run_configs)):
            print(f'Running course {c}...')
            new_save_loc = os.path.join(self.save_loc, f"course_{c}/")
            os.makedirs(new_save_loc, exist_ok=True)
            runner = PACRunner(new_save_loc, data_cfg, run_cfg)
            best_loss, loss_vals = runner.run()
            losses.append(loss_vals)
            # save plots from simple_encoder_decoder_v2.py in new_save_loc

        train_time = time.time() - timer_start
        eval_start = time.time()
        curriculum_data_collect.set("train_time", train_time)
        print("Curriculum complete. Compiling results...")
        final_model = runner.model
        if self.final_dataset_config is None:
            print("No curriculum level test dataset provided, skipping curriculum evaluation.")
            final_test_dataset = None
        else:
            final_test_dataset = get_correct_dataset(self.final_dataset_config)

        plt.figure()
        idx1 = 0
        for i, ls in enumerate(losses):
            idx2 = idx1 + len(ls)
            plt.plot(np.arange(idx1, idx2), ls, label=f"course_{i}")
            idx1 += idx2
        plt.legend()
        plt.savefig(os.path.join(self.save_loc, 'loss.png'))

        if final_test_dataset is not None:
            final_test_dataloader = DataLoader(final_test_dataset, batch_size=1, shuffle=False,
                                               collate_fn=custom_collate_d, pin_memory=True)
            eq_scores, mean_eq, detailed_scores = final_model.eval_equal_acc(final_test_dataloader)
            curriculum_data_collect.set('eq_scores', eq_scores)
            curriculum_data_collect.set('mean_eq', mean_eq)
            plt.figure()
            d = {'item_id': [], 'value': []}
            for k, v in eq_scores.items():
                d['item_id'] += [k for _ in range(len(v))]
                d['value'] += [vi for vi in v]
            sns.barplot(data=d, x='item_id', y='value')
            plt.title(f"Mean of means: {np.mean([v for v in mean_eq.values() if not np.isnan(v)])}")
            plt.savefig(os.path.join(self.save_loc, 'eq_acc_by_seq_len.png'))
            plt.figure()
            x, y = [], []
            for k, v in eq_scores.items():
                x += [k for k in range(len(v))]
                y += v
            plt.scatter(x, y)
            plt.savefig(os.path.join(self.save_loc, 'eq_acc_scatter.png'))
        eval_time = time.time() - eval_start
        total_time = time.time() - timer_start
        curriculum_data_collect.set('eval_time', eval_time)
        curriculum_data_collect.set('total_time', total_time)
        curriculum_data_collect.save(os.path.join(self.save_loc, 'curriculum_data_collect.json'))
        print(f"Done. Train time: {train_time} s \nEval Time: {eval_time} s \nTotal time: {total_time} s")
