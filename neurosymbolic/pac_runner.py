# Copyright 2022, The Johns Hopkins University Applied Physics Laboratory LLC
# All rights reserved.
# Distributed under the terms of the BSD 3-Clause License.

# Approved for public release; distribution is unlimited.
# This material is based upon work supported by the Defense Advanced Research Projects Agency (DARPA) under Agreement
# No. HR00112290032.

import copy
import json
import os
from typing import Union

import numpy as np
import torch
from matplotlib import pyplot as plt
from torch.utils.data import Subset, ConcatDataset, DataLoader

from .datasets.clevr_text_dataset import CLEVRTextDatasetConfig, CLEVRTextDataset
from .datasets.clevr_text_program_dataset import CLEVRTextProgDatasetConfig, CLEVRTextProgDataset
from .datasets.mini_mod_clevr_dataset import MiniModCLEVRDatasetConfig, MiniModCLEVRDataset
from .datasets.mod_clevr_text_dataset import ModCLEVRTextDatasetConfig, ModCLEVRTextDataset
from .datasets.pac_dataset import PACDatasetConfig
from .pac_joint_text_prog_model import PACJointTextProgModel, PACJointTextProgModelConfig
from .pac_model_checkpointer import PACModelCheckpointer
from .utils import custom_collate_d


class DataCollect:
    """Simple data storage object"""
    def __init__(self):
        self.store = {}

    def set(self, key, value):
        self.store[key] = value

    def append(self, key, value):
        if key not in self.store.keys():
            self.store[key] = []
        self.store[key].append(value)

    def to_json(self):
        return self.store

    def save(self, path):
        with open(path, 'w') as f:
            json.dump(self.to_json(), f)


def split_dataset(dataset, amount, rng=None):
    size = len(dataset)
    indices = np.arange(0, size)
    rng = rng if rng is not None else np.random.RandomState()
    rng.shuffle(indices)
    cut = int(amount * size)
    d1 = Subset(dataset, indices[:cut])
    # don't add noise to the data for eval, copy so not to set d1 data transform to None as well
    d2 = copy.deepcopy(Subset(dataset, indices[cut:]))  # test_data or val_data
    d2.dataset.data_transform = None
    return d1, d2


def get_correct_dataset(cfg: PACDatasetConfig):
    # Note: Some datasets may be obsolete
    if isinstance(cfg, CLEVRTextDatasetConfig):
        return CLEVRTextDataset(cfg)
    elif isinstance(cfg, CLEVRTextProgDatasetConfig):
        return CLEVRTextProgDataset(cfg)
    elif isinstance(cfg, ModCLEVRTextDatasetConfig):
        return ModCLEVRTextDataset(cfg)
    elif isinstance(cfg, MiniModCLEVRDatasetConfig):
        return MiniModCLEVRDataset(cfg)
    else:
        raise TypeError("Unknown data config type: {}".format(type(cfg)))


class PACRunConfig:
    def __init__(self, batch_size, epochs, learning_rate=0.001, min_lr=1e-6, sample_for_eval=False, test_dataset=None,
                 val_eval_epochs=10, val_dataset=None, val_eval_strat='eq_score', device=None, abs_max_seq_len=None,
                 model_cfg=None, steps_checkpoint=None, epoch_checkpoint=None, start_checkpoint=None,
                 batch_bar_update=10):
        self.batch_size = batch_size
        self.epochs = epochs
        self.learning_rate = learning_rate
        self.min_lr = min_lr
        self.sample_for_eval = sample_for_eval
        self.test_dataset = test_dataset
        self.val_eval_epochs = val_eval_epochs
        self.val_dataset = val_dataset
        self.val_eval_strat = val_eval_strat
        self.device = device
        self.abs_max_seq_len = abs_max_seq_len  # If None, use max_seq_len from training dataset
        self.model_cfg = model_cfg
        self.steps_checkpoint = steps_checkpoint
        self.epoch_checkpoint = epoch_checkpoint
        self.start_checkpoint = start_checkpoint
        self.batch_bar_update = batch_bar_update

    def to_dict(self):
        return dict(batch_size=self.batch_size, epochs=self.epochs, learning_rate=self.learning_rate,
                    min_lr=self.min_lr, sample_for_eval=self.sample_for_eval, test_dataset=self.test_dataset,
                    val_eval_epochs=self.val_eval_epochs, val_dataset=self.val_dataset,
                    val_eval_strat=self.val_eval_strat, device=self.device, model_cfg=self.model_cfg,
                    steps_checkpoint=self.steps_checkpoint, epoch_checkpoint=self.epoch_checkpoint,
                    start_checkpoint=self.start_checkpoint, batch_bar_update=self.batch_bar_update)

    def to_json(self):
        d = self.to_dict()
        d['test_dataset'] = d['test_dataset'].to_json() if d['test_dataset'] is not None else None
        d['val_dataset'] = d['val_dataset'].to_json() if d['val_dataset'] is not None else None
        d['model_cfg'] = d['model_cfg'].to_json() if d['model_cfg'] is not None else None
        d['start_checkpoint'] = None  # todo: figure out how best to set this for a JSON file
        return d


class PACRunner:
    """Object for running PAC experiments, collecting performance results and saving to disk"""
    def __init__(self, save_loc: str, data_config: Union[PACDatasetConfig, list], run_config: PACRunConfig):
        os.makedirs(save_loc, exist_ok=True)
        self.save_loc = save_loc
        self.data_config = data_config
        self.run_config = run_config
        self.model = None
        self.data = None
        self.train_data = None
        self.test_data = None
        self.val_data = None

    def run(self):
        data_collect = DataCollect()
        if isinstance(self.data_config, list):
            train_data = ConcatDataset([get_correct_dataset(cfg) for cfg in self.data_config])
        else:
            train_data = get_correct_dataset(self.data_config)
        print('num_samples in train dataset:', len(train_data))
        data_collect.set("train_dataset_size", len(train_data))
        if self.run_config.test_dataset is not None:
            if isinstance(self.run_config.test_dataset, list):
                test_data = ConcatDataset([get_correct_dataset(cfg) for cfg in self.run_config.test_dataset])
            else:
                test_data = get_correct_dataset(self.run_config.test_dataset)
            print(f'num_samples in test data: {len(test_data)}')
            data_collect.set("test_dataset_size", len(test_data))
        else:
            test_data = train_data
            print("No test data provided")
            data_collect.set("test_dataset_size", 0)

        val_data = None
        if self.run_config.val_dataset is not None:
            if isinstance(self.run_config.val_dataset, list):
                val_data = ConcatDataset([get_correct_dataset(cfg) for cfg in self.run_config.val_dataset])
            else:
                val_data = get_correct_dataset(self.run_config.val_dataset)
            print(f'num_samples in val data: {len(val_data)}')
            data_collect.set("val_dataset_size", len(val_data))
        else:
            print("No validation data provided")
            data_collect.set('val_dataset_size', 0)

        self.train_data = train_data
        self.val_data = val_data
        self.test_data = test_data

        if self.run_config.abs_max_seq_len is not None:
            # may be important if one can expect test sequences longer than that in training, or for curriculum learning
            max_seq = self.run_config.abs_max_seq_len
        else:
            max_seq = train_data.get_max_seq_length()  # assuming data is ordered by length
        voc = train_data.get_vocab()
        data_collect.set('max_seq_len', max_seq)
        data_collect.set('vocab_len', len(voc))
        if self.run_config.model_cfg:
            self.run_config.model_cfg = self.run_config.model_cfg(voc, max_seq, voc.VALUE_TOKEN,
                                                                  voc.BOS, voc.EOS,
                                                                  device=self.run_config.device)
            model = PACJointTextProgModel(self.run_config.model_cfg)
        else:
            cfg = PACJointTextProgModelConfig(voc, max_seq, voc.VALUE_TOKEN,
                                              voc.BOS, voc.EOS,
                                              device=self.run_config.device)
            model = PACJointTextProgModel(cfg)

        # save the run config
        with open(os.path.join(self.save_loc, "run_config.json"), 'w') as f:
            json.dump(self.run_config.to_json(), f)

        # make checkpointer
        checkpoint_dir = os.path.join(self.save_loc, 'checkpoints')
        os.makedirs(checkpoint_dir, exist_ok=True)
        checkpointer = PACModelCheckpointer(checkpoint_dir=checkpoint_dir,
                                            step_checkpoint=self.run_config.steps_checkpoint,
                                            epoch_checkpoint=self.run_config.epoch_checkpoint)

        torch.save(voc, os.path.join(self.save_loc, 'vocab.pt'))
        # train
        best_model, best_loss, best_epoch, mean_loss_vals, all_loss_vals = model.train_everything(
            train_data,
            self.run_config.epochs,
            self.run_config.batch_size,
            lr=self.run_config.learning_rate,
            min_lr=self.run_config.min_lr,
            val_dataset=val_data,
            eval_freq=self.run_config.val_eval_epochs,
            eval_strat=self.run_config.val_eval_strat,
            checkpointer=checkpointer,
            checkpoint=self.run_config.start_checkpoint,
            batch_bar_update=self.run_config.batch_bar_update
        )
        print("Training complete", "\nBuilding plots...")

        # save the model ASAP in case anything else fails
        torch.save(best_model, os.path.join(self.save_loc, 'model.pt'))

        plt.plot(mean_loss_vals)
        plt.title("Mean loss per epoch; best={}".format(best_loss))
        plt.show()
        plt.savefig(os.path.join(self.save_loc, 'mean_per_epoch_loss.png'))

        plt.plot(all_loss_vals)
        plt.title("All losses")
        plt.show()
        plt.savefig(os.path.join(self.save_loc, 'all_loss.png'))

        model.load_model_params(best_model)
        print("Some encoding/decoding examples:")
        test_data = DataLoader(self.test_data, batch_size=1, shuffle=False,
                               collate_fn=custom_collate_d, pin_memory=True)
        model.print_decodings(test_data, use_logits=self.run_config.sample_for_eval, max_out=10)
        bleu_scores = model.blue_eval(test_data, use_logits=self.run_config.sample_for_eval)
        eq_scores, eq_means, eq_detailed = model.eval_equal_acc(test_data, get_detailed_scores=True)
        lev_scores, lev_means, lev_detailed = model.eval_lev_dist(test_data, get_detailed_scores=True)
        self.model = model

        print("Storing course data...")
        data_collect.set('mean_loss_per_epoch', mean_loss_vals)
        data_collect.set('all_losses', all_loss_vals)
        data_collect.set('best_loss', best_loss)
        data_collect.set('best_epoch', best_epoch)
        data_collect.set('bleu_scores', bleu_scores)
        data_collect.set('eq_scores', eq_scores)
        data_collect.set('eq_means', eq_means)
        data_collect.set('eq_detailed_scores', eq_detailed)
        data_collect.set('lev_scores', lev_scores)
        data_collect.set('lev_means', lev_means)
        data_collect.set('lev_detailed_scores', lev_detailed)
        data_collect.set('end_seq_len', tuple(model.word_pos_embedding.weight.shape))
        detailed_means = {
            'text_to_text': self.mean_of_all_seq_lens(eq_detailed['text_to_text']),
            'text_to_program': self.mean_of_all_seq_lens(eq_detailed['text_to_program']),
            'program_to_text': self.mean_of_all_seq_lens(eq_detailed['program_to_text'])
        }
        lev_detailed_means = {
            'text_to_text': self.mean_of_all_seq_lens(lev_detailed['text_to_text']),
            'text_to_program': self.mean_of_all_seq_lens(lev_detailed['text_to_program']),
            'program_to_text': self.mean_of_all_seq_lens(lev_detailed['program_to_text'])
        }
        data_collect.set('detailed_means', detailed_means)
        data_collect.set('lev_detailed_means', lev_detailed_means)
        data_collect.save(os.path.join(self.save_loc, 'data_collect.json'))
        print("Done")

        print("Performance Results:")
        print('text_to_text', detailed_means['text_to_text'])
        print('text_to_program', detailed_means['text_to_program'])
        print('program_to_text', detailed_means['program_to_text'])
        print('Lev text_to_text', lev_detailed_means['text_to_text'])
        print('Lev text_to_program', lev_detailed_means['text_to_program'])
        print('Lev program_to_text', lev_detailed_means['program_to_text'])

        return best_loss, mean_loss_vals

    @staticmethod
    def mean_of_all_seq_lens(score_dict):
        return np.mean(np.concatenate([scores for scores in score_dict.values()]))
