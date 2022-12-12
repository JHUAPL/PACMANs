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


"""
Ideas for this dataset
    1. Augment the dataset with questions that have VALUEs in it. By simply augmenting it, I'm not taking away from the
    whole dataset for question learning, but I'm adding the capability to consider values.
        - Perhaps augments should be like the questions I was generating before, where we expect values to be set. I 
            can add functions to do the parameter setting. 
    2. The GT should be programs, which are kind of included in the JSON, but I'll need to translate them somehow. From
    there, it is like another encoding that can use cross-entropy loss rather than needing REINFORCE, because I'm not
    learning from answers to the question, I'm just learning the encoding. 
    3. I could add answers to the GT, which might be similar to what we were talking about with the GAN. 
    4. Rule-parse concepts and values? This goes along with some of the original ideas, and may simplify some things.
        - Maybe transfer from learning on the whole dataset to rule-parsed concept replacement? 
    5. Architecture will essentially be a modified pac_encoder_decoder, with the decoder decoding to programs instead.
        - Could try the combination of both auto-encoding and program decoding? But probably after just trying decoding.
"""


class CLEVRTextProgDatasetConfig(PACDatasetConfig):
    VALID_MODES = ['train', 'test', 'val']

    def __init__(self, mode: str, path_to_clevr: str, vocab: Union[str, PacVocab], max_clevr_seq_len: int = None,
                 seed: int = None, set_data_transform: Callable = None, set_prog_transform: Callable = None):
        """
        :param mode: must be one of "train", "test", or "val"
        """
        if mode not in self.VALID_MODES:
            raise ValueError(f"Unknown mode. Allowed modes are {self.VALID_MODES}.")
        self.mode = mode
        self.path_to_clevr = path_to_clevr
        self.max_clevr_seq_len = max_clevr_seq_len if max_clevr_seq_len else torch.inf
        self.set_prog_transform = set_prog_transform
        super(CLEVRTextProgDatasetConfig, self).__init__(seed, set_data_transform, vocab=vocab)

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


class CLEVRTextProgDataset(PACDataset):
    CLEVR_TOKEN_CACHE = "CLEVR_PROG_TOKEN_CACHE.json"
    REMOVE = ['', ' ']

    def __init__(self, config: CLEVRTextProgDatasetConfig):
        self.path_to_clevr = config.path_to_clevr
        self.mode = config.mode
        self.programs = []
        self.max_clevr_seq_len = config.max_clevr_seq_len
        super().__init__(config)
        self.max_seq_length = torch.max(torch.tensor([len(self.programs[i]) for i in range(len(self.programs))])).item()
        self.prog_transform = config.set_prog_transform() if config.set_prog_transform is not None else None

    def _load_clevr(self):
        if self.mode == 'train':
            path_to_data = os.path.join(self.path_to_clevr, 'questions', 'CLEVR_train_questions.json')
        elif self.mode == 'test':
            path_to_data = os.path.join(self.path_to_clevr, 'questions', 'CLEVR_val_questions.json')
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
            # todo: Should we do any more manipulation to the question?
            q = torch.tensor([self.vocab[self.vocab.BOS]] + [self.vocab[s.lower()] for s in q]
                             + [self.vocab[self.vocab.EOS]])
            self.questions.append(q)
            self.values_list.append(None)
            self.concepts_list.append(None)

            prog = torch.tensor([self.vocab[self.vocab.BOS]] + self.return_input2(-1, d['program'])
                                + [self.vocab[self.vocab.EOS]])
            # Current program is a nested tuple, works well for trying to run the program
            # To get to use cross-entropy:
            #   - Could use tokens for ',' and for '(', and ')' and have one vector (current approach)
            #       - I see potentially for this to lead to the network to constantly predict parentheses...
            #       - The network would need to learn open and closing parentheses, but maybe decoding from the
            #           beginning and the end at the same time (attention) could do this?
            #   - Could just have a vector of func, and value tokens, and save a mapping for how many inputs each
            #       function takes to decode the vector into a readable/runnable format.
            #       - This form would have shorter vectors, but the network needs to learn the number of inputs for
            #           each function

            self.programs.append(prog)

    def return_input(self, idx, prog):
        """
        Return a nested tuple of tokens representing the function to be called and the arguments to the function.
        :param idx:
        :param prog:
        :return:
        """
        if len(prog[idx]['inputs']) != 0:
            func = self.vocab[prog[idx]['function']]
            vs = [self.vocab[v] for v in prog[idx]['value_inputs']]
            inps = [self.return_input(i, prog) for i in prog[idx]['inputs']]
            if len(vs) > 0:
                return tuple([func] + inps + vs)
            else:
                return tuple([func] + inps)
        else:
            return self.vocab[prog[idx]['function']]  # should always be self.vocab['scene']

    def return_input2(self, idx, prog):
        """
        Return a list of tokens that, when translated back to text, represent the function calls and their arguments.
        :param idx:
        :param prog:
        :return:
        """
        if len(prog[idx]['inputs']) != 0:
            func = self.vocab[prog[idx]['function']]
            vs = [self.vocab[v] for v in prog[idx]['value_inputs']]
            inps = [j for i in prog[idx]['inputs'] for j in self.return_input2(i, prog)]
            if len(vs) > 0:
                return [func, self.vocab["("]] + inps + [self.vocab[","]] + vs + [self.vocab[")"]]
            else:
                return [func, self.vocab["("]] + inps + [self.vocab[")"]]
        else:
            return [self.vocab[prog[idx]['function']]]

    def gen_data(self):
        self._load_clevr()

    def __getitem__(self, item):
        programs = self.programs[item]
        if self.prog_transform is not None:
            programs = self.prog_transform(programs)
        q, seq_len, v_list, c_list, gt_q, gt_sl, gt_v_list, gt_c_list = super().__getitem__(item)
        d = dict(questions=q, seq_lengths=seq_len, values=v_list, concepts=c_list, gt_questions=gt_q,
                 gt_sequence_lengths=gt_sl, gt_values=gt_v_list, gt_concepts=gt_c_list, programs=programs)
        return d
