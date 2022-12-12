# Copyright 2022, The Johns Hopkins University Applied Physics Laboratory LLC
# All rights reserved.
# Distributed under the terms of the BSD 3-Clause License.

# Approved for public release; distribution is unlimited.
# This material is based upon work supported by the Defense Advanced Research Projects Agency (DARPA) under Agreement
# No. HR00112290032.

from torch.utils.data import Dataset
import torch
import numpy as np
from .pac_vocab import PacVocab


class PACDatasetConfig:
    def __init__(self, seed, set_data_transform, vocab=None):
        self.seed = seed
        self.set_data_transform = set_data_transform
        self.vocab = vocab

    def get_base_dict(self):
        return {'seed': self.seed, 'set_data_transform': self.set_data_transform, 'vocab': self.vocab}

    def to_dict(self):
        raise NotImplementedError("Must be implemented in subclass!")

    def to_json(self):
        raise NotImplementedError("Must be implemented in subclass!")


class PACDataset(Dataset):

    def __init__(self, config: PACDatasetConfig):
        self.function_words = None
        self.param_words = None
        self.out_words = None
        self.max_seq_length = None
        self.questions = []
        self.values_list = []
        self.concepts_list = []
        if config.vocab is not None:
            if isinstance(config.vocab, str):
                self.vocab = PacVocab()
                self.vocab.load(config.vocab)  # loads mapping to cpu by default
            else:
                self.vocab = config.vocab
        self.do_not_lowercase = self.vocab.do_not_lowercase
        self.rng = np.random.RandomState(config.seed) if config.seed is not None else np.random.RandomState()
        self.data_transform = None
        if config.set_data_transform is not None:
            self.data_transform = config.set_data_transform(self.rng, self.function_words, self.param_words,
                                                            self.out_words)
        self.config = config
        self.gen_data()
        self._set_sequence_lens()

    def _set_sequence_lens(self):
        self.seq_lengths = torch.LongTensor([it.shape[0] for it in self.questions])

    def get_vocab(self):
        return self.vocab

    def get_vocab_size(self):
        return len(self.vocab)

    def get_max_seq_length(self):
        if self.max_seq_length is None:
            self.max_seq_length = torch.max(self.seq_lengths).item()
        return self.max_seq_length

    def __len__(self):
        return len(self.questions)

    def __getitem__(self, item):
        if self.data_transform is not None:
            questions, seq_lens, values, concepts = self.data_transform(self.questions[item], self.seq_lengths[item],
                                                                        self.values_list[item],
                                                                        self.concepts_list[item])
            return (questions, seq_lens, values, concepts, self.questions[item], self.seq_lengths[item],
                    self.values_list[item], self.concepts_list[item])
        return (self.questions[item], self.seq_lengths[item], self.values_list[item], self.concepts_list[item],
                self.questions[item], self.seq_lengths[item], self.values_list[item], self.concepts_list[item])

    def gen_data(self):
        raise NotImplementedError("Must implement 'get_data' function in subclass!")
