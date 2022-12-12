# Copyright 2022, The Johns Hopkins University Applied Physics Laboratory LLC
# All rights reserved.
# Distributed under the terms of the BSD 3-Clause License.

# Approved for public release; distribution is unlimited.
# This material is based upon work supported by the Defense Advanced Research Projects Agency (DARPA) under Agreement
# No. HR00112290032.

import json
import os
from typing import Callable, Union

import torch
from tqdm import tqdm

from .pac_dataset import PACDatasetConfig, PACDataset
from .pac_vocab import PacVocab


REPLACEMENTS = {"cube": "M_n", 'cubes': "M_ns", 'block': 'M_n', 'blocks': 'M_ns',
                'cylinder': 'M_upw', 'cylinders': 'M_upws', 'sphere': 'M_eddy', 'spheres': 'M_eddys',
                'ball': 'M_eddy', 'balls': "M_eddys", 'shape': "output",
                'material': 'time_variable', 'metal': 'N', 'rubber': 'time_step_in_years', 'shiny': 'N',
                'metallic': 'N', 'matte': 'time_step_in_years',
                'color': 'input', 'gray': 'K_v', 'red': 'A_GM', 'yellow': 'M_ek', 'blue': 'A_Redi', 'brown': "M_SD",
                'green': 'Fws', 'cyan': 'Fwn', 'purple': 'epsilon',
                'size': 'box', 'tiny': 'area_n', 'small': 'area_s', 'big': 'area_low', 'large': 'D_high',
                'thing': 'model'}


def replace(sentence):
    # assumes items in sentence are lower case
    for i, s in enumerate(sentence):
        if s in REPLACEMENTS.keys():
            sentence[i] = REPLACEMENTS[s]
    return sentence


class ModCLEVRTextDatasetConfig(PACDatasetConfig):
    VALID_MODES = ['train', 'test', 'val']

    def __init__(self, mode: str, path_to_clevr: str, vocab: Union[str, PacVocab], max_clevr_seq_len: int = None,
                 seed: int = None, set_data_transform: Callable = None):
        """
        :param mode: must be one of "train", "test", or "val"
        """
        if mode not in self.VALID_MODES:
            raise ValueError(f"Unknown mode. Allowed modes are {self.VALID_MODES}.")
        self.mode = mode
        self.path_to_clevr = path_to_clevr
        self.max_clevr_seq_len = max_clevr_seq_len if max_clevr_seq_len else torch.inf
        super().__init__(seed, set_data_transform, vocab)

    def to_dict(self):
        d = self.get_base_dict()
        d.update(dict(mode=self.mode, path_to_clevr=self.path_to_clevr, max_clevr_seq_len=self.max_clevr_seq_len))
        return d

    def to_json(self):
        d = self.to_dict()
        d['set_data_transform'] = str(self.set_data_transform)
        d['seed'] = str(self.seed)
        if not isinstance(d['vocab'], str):
            d['vocab'] = d['vocab'].to_json()
        return d


class ModCLEVRTextDataset(PACDataset):
    CLEVR_TOKEN_CACHE = "CLEVR_TOKEN_CACHE.json"
    REMOVE = ['', ' ']

    def __init__(self, config: ModCLEVRTextDatasetConfig):
        self.path_to_clevr = config.path_to_clevr
        self.mode = config.mode
        self.max_clevr_seq_len = config.max_clevr_seq_len
        super().__init__(config)

    def _load_clevr(self):
        if self.mode == 'train':
            path_to_data = os.path.join(self.path_to_clevr, 'questions', 'CLEVR_train_questions.json')
        elif self.mode == 'test':
            path_to_data = os.path.join(self.path_to_clevr, 'questions', 'CLEVR_test_questions.json')
        else:
            path_to_data = os.path.join(self.path_to_clevr, 'questions', 'CLEVR_val_questions.json')
        with open(path_to_data, 'r') as f:
            data = json.load(f)
        for d in tqdm(data['questions'], desc="Loading CLEVR questions"):
            q = self.vocab.tokenizer(d['question'])
            if len(q) > self.max_clevr_seq_len:
                continue
            for t in self.REMOVE:
                if t in q:
                    q.remove(t)
            q = torch.tensor([self.vocab[self.vocab.BOS]] + [self.vocab[s] for s in replace([t.lower() for t in q])]
                             + [self.vocab[self.vocab.EOS]])
            self.questions.append(q)
            self.values_list.append(None)
            self.concepts_list.append(None)

            if torch.rand(1) < 0.1:
                import numpy as np
                var = np.choice(["K_v", "M_ek"])
                bmo_func = np.choice(['ChangeSign', 'FinalValue'])
                saved_var = np.choice(['M_n', 'M_eddy'])
                val = np.random.uniform(0, 10)
                q2 = "BOS When {} is VALUE what is the output of {} on {}? EOS".format(var, bmo_func, saved_var)
                q2 = torch.tensor([self.vocab[self.vocab.BOS]] + [self.vocab[s] for s in self.vocab.tokenizer(q2)]
                                  + [self.vocab[self.vocab.EOS]])
                self.questions.append(q2)
                self.values_list.append([val])
                self.concepts_list.append(None)

    def gen_data(self):
        self._load_clevr()