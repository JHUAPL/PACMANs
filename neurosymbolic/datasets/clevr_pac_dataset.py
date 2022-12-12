# Copyright 2022, The Johns Hopkins University Applied Physics Laboratory LLC
# All rights reserved.
# Distributed under the terms of the BSD 3-Clause License.

# Approved for public release; distribution is unlimited.
# This material is based upon work supported by the Defense Advanced Research Projects Agency (DARPA) under Agreement
# No. HR00112290032.

import json
import os
from typing import Callable, Union

import numpy as np
import torch
from tqdm import tqdm

from .amoc_question_forms import ALL_QUESTIONS
from .pac_dataset import PACDatasetConfig, PACDataset
from .pac_vocab import PacVocab
from ..utils import program_to_tokens, is_str_float


class CLEVRPacDatasetConfig(PACDatasetConfig):
    VALID_MODES = ['train', 'test', 'val']

    def __init__(self, mode: str, path_to_clevr: str, vocab: Union[str, PacVocab], max_clevr_seq_len: int = None,
                 pac_only: bool = False, num_clevr_samples: int = None, seed: int = None,
                 set_data_transform: Callable = None, set_prog_transform: Callable = None):
        """
        :param mode: must be one of "train", "test", or "val"
        """
        if mode not in self.VALID_MODES:
            raise ValueError(f"Unknown mode. Allowed modes are {self.VALID_MODES}.")
        self.mode = mode
        self.path_to_clevr = path_to_clevr
        self.max_clevr_seq_len = max_clevr_seq_len if max_clevr_seq_len else torch.inf
        self.set_prog_transform = set_prog_transform
        self.pac_only = pac_only
        self.num_clevr_samples = num_clevr_samples
        super(CLEVRPacDatasetConfig, self).__init__(seed, set_data_transform, vocab)

    def to_dict(self):
        d = self.get_base_dict()
        d.update(dict(mode=self.mode, path_to_clevr=self.path_to_clevr, max_clevr_seq_len=self.max_clevr_seq_len,
                      pac_only=self.pac_only, num_clevr_samples=self.num_clevr_samples))
        return d

    def to_json(self):
        d = self.to_dict()
        d['set_data_transform'] = str(self.set_data_transform)
        d['seed'] = str(self.seed)
        if not isinstance(d['vocab'], str):
            d['vocab'] = d['vocab'].to_json()
        return d


class CLEVRPacDataset(PACDataset):
    CLEVR_TOKEN_CACHE = "CLEVR_PROG_TOKEN_CACHE.json"
    REMOVE = ['', ' ']

    def __init__(self, config: CLEVRPacDatasetConfig):
        self.path_to_clevr = config.path_to_clevr
        self.mode = config.mode
        self.pac_only = config.pac_only
        self.num_clevr_samples = config.num_clevr_samples
        self.programs = []
        self.prog_values = []
        self.max_clevr_seq_len = config.max_clevr_seq_len
        super().__init__(config)
        self.max_seq_length = np.max([len(p) for p in self.programs] + [len(q) for q in self.questions])
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

        questions = []
        values_list = []
        concepts_list = []
        prog_values = []
        programs = []
        for d in tqdm(data['questions'], desc="Loading CLEVR questions"):
            q = self.vocab.tokenizer(d['question'])
            if len(q) > self.max_clevr_seq_len:
                continue
            for t in self.REMOVE:
                if t in q:
                    q.remove(t)
            q = torch.tensor([self.vocab[self.vocab.BOS]] + [self.vocab[s.lower()] for s in q]
                             + [self.vocab[self.vocab.EOS]])
            questions.append(q)
            values_list.append([])
            concepts_list.append(None)
            prog_values.append([])

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

            programs.append(prog)

        if self.num_clevr_samples is not None:
            select_questions = self.rng.choice(range(len(questions)), size=self.num_clevr_samples, replace=False)
            questions = [questions[s] for s in select_questions]
            programs = [programs[s] for s in select_questions]
        self.questions += questions
        self.programs += programs
        self.values_list += values_list
        self.concepts_list += concepts_list
        self.prog_values += prog_values

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

    def _sentence_to_indices(self, sentence, program=False):
        values = []
        tkns = []
        if program:
            tokenized = program_to_tokens(sentence)
        else:
            tokenized = self.vocab.tokenizer(sentence)
        for tkn in tokenized:
            if str.isnumeric(tkn):
                v = int(tkn)
                values.append(v)
                tkns.append(self.vocab.VALUE_TOKEN)
            elif is_str_float(tkn):
                v = float(tkn)
                values.append(v)
                tkns.append(self.vocab.VALUE_TOKEN)
            else:
                tkns.append(tkn.lower() if tkn not in self.do_not_lowercase else tkn)
        return torch.tensor([self.vocab[self.vocab.BOS]] + [self.vocab[tkn] for tkn in tkns]
                            + [self.vocab[self.vocab.EOS]]), values

    def _load_pac_questions(self):
        de = "Generating PACMANS questions"
        question_funcs = ALL_QUESTIONS
        qp_map = {}
        for func in tqdm(question_funcs, desc=de):
            qp_map[func.__name__] = []
            for q, p in func(self.rng):
                q_tkns, values = self._sentence_to_indices(q)
                p_tkns, prog_values = self._sentence_to_indices(p, program=True)
                qp_map[func.__name__].append((q_tkns, p_tkns, values, prog_values))
        if not os.path.isfile("train_test_set.json"):
            print("Building train/test split...")
            qp_train_split = dict([(k, []) for k in qp_map.keys()])
            qp_test_split = dict([(k, []) for k in qp_map.keys()])
            for k, v in qp_map.items():
                qp_train_split[k] = self.rng.choice(range(len(v)), replace=False, size=int(0.9*len(v))).tolist()
                qp_test_split[k] = [i for i in range(len(v)) if i not in qp_train_split[k]]
            print("Dumping train/test splits to JSON...")
            with open("train_test_set.json", 'w') as f:
                json.dump({"train": qp_train_split, "test": qp_test_split}, f)
            print("Done.")
        else:
            with open("train_test_set.json", 'r') as f:
                split = json.load(f)
            qp_train_split = split['train']
            qp_test_split = split['test']
        if self.mode == 'train':
            split = qp_train_split
        else:
            split = qp_test_split
        func_data_sizes = {}
        for func in question_funcs:
            func_data_sizes[func.__name__] = len(split[func.__name__])
            print(f"Size of {func.__name__}: {func_data_sizes[func.__name__]}")
        # avg_size = int(np.mean(list(func_data_sizes.values())))
        # print("Avg question set size:", avg_size)
        # for func in tqdm(question_funcs, desc=de):
        #     idxes = split[func.__name__][:avg_size]
        #     for idx in idxes:
        #         q_tkns, p_tkns, values, prog_values = qp_map[func.__name__][idx]
        #         self.questions.append(q_tkns)
        #         self.programs.append(p_tkns)
        #         self.concepts_list.append(None)
        #         self.values_list.append(values)
        #         self.prog_values.append(prog_values)
        idx = 0
        # Note: Better to make these configurable. These were somewhat arbitrarily chosen
        dataset_size = 250000 if self.mode == 'train' else 25000
        while len(self.questions) < dataset_size:
            for func in question_funcs:
                size = len(split[func.__name__])
                q_tkns, p_tkns, values, prog_values = qp_map[func.__name__][idx % size]
                self.questions.append(q_tkns)
                self.programs.append(p_tkns)
                self.concepts_list.append(None)
                self.values_list.append(values)
                self.prog_values.append(prog_values)
            idx += 1

    def gen_data(self):
        if len(self.questions) > 0:
            raise RuntimeError("Tried to add data to an already initialized dataset")
        if not self.pac_only:
            self._load_clevr()
        self._load_pac_questions()

    def __getitem__(self, item):
        programs = self.programs[item]
        if self.prog_transform is not None:
            programs = self.prog_transform(programs)
        prog_values = self.prog_values[item]
        q, seq_len, v_list, c_list, gt_q, gt_sl, gt_v_list, gt_c_list = super().__getitem__(item)
        d = dict(questions=q, seq_lengths=seq_len, values=v_list, concepts=c_list, gt_questions=gt_q,
                 gt_sequence_lengths=gt_sl, gt_values=gt_v_list, gt_concepts=gt_c_list, programs=programs,
                 program_values=prog_values)
        return d
