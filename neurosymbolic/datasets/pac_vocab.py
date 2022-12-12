# Copyright 2022, The Johns Hopkins University Applied Physics Laboratory LLC
# All rights reserved.
# Distributed under the terms of the BSD 3-Clause License.

# Approved for public release; distribution is unlimited.
# This material is based upon work supported by the Defense Advanced Research Projects Agency (DARPA) under Agreement
# No. HR00112290032.

import json
import os
import warnings
from collections import Counter, OrderedDict
from copy import deepcopy

import torch
import torchtext
from torchtext.data import get_tokenizer
from torchtext.vocab import Vocab
from tqdm import tqdm

from ..definitions import CONCEPT_WORDS
from .amoc_question_forms import ALL_QUESTIONS
from ..utils import program_to_tokens, is_str_float


class PacVocab:
    UNK = 'UNK'
    VALUE_TOKEN = 'VALUE'
    EOS = 'EOS'
    BOS = 'BOS'
    PAD = 'PAD'
    BMI_CONCEPT_TOKEN = 'BMI'
    FUNC_CONCEPT_TOKEN = 'FUNC'
    BMO_CONCEPT_TOKEN = 'BMO'
    TOKEN_LIST = deepcopy(CONCEPT_WORDS)
    # add seemingly missing tokens or tokens desired but not included in build here (or add just in case)
    TOKEN_LIST += ['if', 'one', 'sets', 'to', 'and', ',', 'will', 'on', '?', 'i', 'you', 'set', 'what', 'is',
                   'the', 'output', 'of', 'be', 'let', 'assume', 'then', 'when', '.', 'value', 'AMOC', 'collapse',
                   'final', 'box_model', 'at', 'does', 'time', 'step', 'fall', 'drop', 'rise', 'raise', 'he', 'she',
                   'they', 'was', 'for', 'with', 'from', 'had', 'but', 'not', 'no', 'all', 'were', 'can', 'each',
                   'their', 'up', 'down', 'about', 'them', 'some', 'so', 'get', 'did', 'water', 'first', 'could',
                   'would']
    TOKEN_LIST = list(set(TOKEN_LIST))
    DEFAULT_IDX = 1
    CLEVR_TOKEN_CACHE = "CLEVR_TOKEN_CACHE.json"
    AMOC_QUESTIONS_TOKEN_CACHE = "AMOC_QUESTIONS_TOKEN_CACHE.json"
    REMOVE = ['', ' ']

    def __init__(self, path_to_clevr=None, vocab_ordered_dict=None, no_load_from_cache=False):
        # Note that `vocab_ordered_dict` takes precedence over `path_to_clever` in terms of what vocab is loaded
        if vocab_ordered_dict is not None and (not no_load_from_cache or path_to_clevr):
            warnings.warn("Setting an 'vocab_ordered_dict' takes precedence over loading from cache or building the"
                          "vocabulary from data, all other arguments will be ignored.")
        self._vocab_obj = None
        self.path_to_clevr = path_to_clevr
        self.vocab_ordered_dict = vocab_ordered_dict
        self.no_load_from_cache = no_load_from_cache
        self.tokenizer = get_tokenizer('spacy', language='en_core_web_sm')
        self.do_not_lowercase = set(CONCEPT_WORDS).union({self.PAD, self.UNK, self.BOS, self.EOS, self.VALUE_TOKEN,
                                                          self.BMI_CONCEPT_TOKEN, self.FUNC_CONCEPT_TOKEN,
                                                          self.BMO_CONCEPT_TOKEN, 'AMOC'})
        self._build_vocab()

    def _case(self, token: str):
        return token.lower() if token not in self.do_not_lowercase else token

    def _get_clevr_vocab_token_set(self):
        cache_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), self.CLEVR_TOKEN_CACHE)
        if not os.path.isfile(cache_file) and self.path_to_clevr is None:
            raise ValueError("No CLEVR cache found, and cannot build CLEVR tokens without path to CLEVR DATA")
        if self.no_load_from_cache and self.path_to_clevr is None:
            raise ValueError("Cannot build CLEVR tokens without path to CLEVR DATA")
        if not os.path.isfile(cache_file) or self.no_load_from_cache:
            tokens = set()
            print("Building token set...")
            for fl in ['CLEVR_train_questions.json', 'CLEVR_val_questions.json', 'CLEVR_test_questions.json']:
                path_to_data = os.path.join(self.path_to_clevr, 'questions', fl)
                with open(path_to_data, 'r') as f:
                    data = json.load(f)
                for d in tqdm(data['questions'], desc=f"Getting Clevr tokens from: {fl}"):
                    q = self.tokenizer(d['question'])
                    q = [self._case(t) for t in q]
                    if fl != 'CLEVR_test_questions.json':
                        # if we aren't in the test set, also grab the tokens from programs (no programs in test set)
                        q += [p['function'] for p in d['program']]
                    tokens.update(q)
            for t in self.REMOVE:
                if t in tokens:
                    tokens.remove(t)
            with open(cache_file, 'w') as f:
                json.dump(list(tokens), f)
            print("Done")
        else:
            print(f"Loading CLEVR tokens from cache: {cache_file}")
            with open(cache_file, 'r') as f:
                tokens = set(json.load(f))
        return tokens

    def _get_amoc_questions_token_set(self):
        cache_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), self.AMOC_QUESTIONS_TOKEN_CACHE)
        if not os.path.isfile(cache_file) or self.no_load_from_cache:
            tokens = set()
            print("Building AMOC questions token set...")
            for q_func in ALL_QUESTIONS:
                print(f"Getting tokens from {q_func.__name__}")
                # Note the no RNG is needed for the question function because numeric values will be discarded during
                #   tokenization
                for question, program in tqdm(q_func(), desc=f"progress on {q_func.__name__}"):
                    q = self.tokenizer(question)
                    tkns = [self._case(t) for t in q if not str.isnumeric(t) and not is_str_float(t)]
                    program_tokenized = program_to_tokens(program)
                    tkns += [self._case(t) for t in program_tokenized if not str.isnumeric(t) and not is_str_float(t)]
                    tokens.update(tkns)
            for t in self.REMOVE:
                if t in tokens:
                    tokens.remove(t)
            with open(cache_file, 'w') as f:
                json.dump(list(tokens), f)
            print("Done")
        else:
            print(f"Loading AMOC questions tokens data from cache: {cache_file}")
            with open(cache_file, 'r') as f:
                tokens = set(json.load(f))
        return tokens

    def _build_vocab(self):
        if self.vocab_ordered_dict is not None:
            ordered_dict = self.vocab_ordered_dict
        else:
            tokens = set(self.TOKEN_LIST)
            tokens.update(self._get_clevr_vocab_token_set())
            tokens.update(self._get_amoc_questions_token_set())
            tokens.update(['(', ')'])
            counter = Counter(tokens)
            sorted_by_freq_tuples = sorted(counter.items(), key=lambda x: x[1], reverse=True)
            ordered_dict = OrderedDict(sorted_by_freq_tuples)
        vocab = torchtext.vocab.vocab(ordered_dict, specials=[self.PAD, self.UNK, self.BOS, self.EOS, self.VALUE_TOKEN,
                                                              self.BMO_CONCEPT_TOKEN, self.FUNC_CONCEPT_TOKEN,
                                                              self.BMI_CONCEPT_TOKEN])
        vocab.set_default_index(self.DEFAULT_IDX)
        self._vocab_obj = vocab

    def __len__(self):
        return len(self.vocab)

    def __getitem__(self, item):
        return self.vocab[item]

    def get_itos(self):
        return self._vocab_obj.get_itos()

    @property
    def vocab(self):
        return self._vocab_obj

    @vocab.setter
    def vocab(self, new_vocab):
        assert isinstance(new_vocab, Vocab)  # must be a torchtext Vocab object
        self._vocab_obj = new_vocab

    @vocab.getter
    def vocab(self):
        return self._vocab_obj

    def store(self, path):
        torch.save(self, path)

    def load(self, path, map_location='cpu'):
        saved = torch.load(path, map_location=map_location)
        self.vocab = saved.vocab

    def to_json(self):
        return {
            "UNK": self.UNK, "VALUE_TOKEN": self.VALUE_TOKEN, 'EOS': self.EOS, 'BOS': self.BOS, 'PAD': self.PAD,
            "BMI_CONCEPT_TOKEN": self.BMI_CONCEPT_TOKEN, "FUNC_CONCEPT_TOKEN": self.FUNC_CONCEPT_TOKEN,
            "BMO_CONCEPT_TOKEN": self.BMI_CONCEPT_TOKEN,
            "TOKEN_LIST": self.TOKEN_LIST,
            "DEFAULT_IDX": self.DEFAULT_IDX,
            'itos': self.get_itos(),
            'vocab_ordered_dict': self.vocab_ordered_dict
        }
