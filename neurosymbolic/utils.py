# Copyright 2022, The Johns Hopkins University Applied Physics Laboratory LLC
# All rights reserved.
# Distributed under the terms of the BSD 3-Clause License.

# Approved for public release; distribution is unlimited.
# This material is based upon work supported by the Defense Advanced Research Projects Agency (DARPA) under Agreement
# No. HR00112290032.

import numpy as np
import torch


def program_to_tokens(program, max_iters=1000):
    tokens = []
    iters = 0
    idx = 0
    if program[idx] == '(':
        raise ValueError("First token of the program should be the name of a function. Given program is "
                         "\n{}".format(program))
    while len(program) > 0 and iters < max_iters:
        pl = program.find(')')
        pr = program.find('(')
        cma = program.find(',')
        pl = pl if pl >= 0 else np.inf
        pr = pr if pr >= 0 else np.inf
        cma = cma if cma >= 0 else np.inf
        idx = np.min([pl, pr, cma]).astype(int)
        if idx == 0:  # should happen when parentheses are the first idx
            idx += 1
        tkn = program[:idx]
        tokens.append(tkn)
        program = program[idx:]
        iters += 1
    return tokens


def ints_to_tokens(itos, sentence):
    tokens = [itos[int(s)] for s in sentence]
    return tokens


def tokens_to_str(tokens, program=False, bos="BOS", eos="EOS"):
    if program:
        return ''.join(tokens).replace(bos, bos + " ").replace(eos, " " + eos).replace(",", ", ")
    punctuation = [' ,', ' ?', ' .']
    out = ' '.join(tokens)
    for p in punctuation:
        out = out.replace(p, p[-1])
    return out


def logits_to_tokens(itos, logits):
    sentence = []
    for s in logits:
        tkn = torch.multinomial(torch.softmax(s, dim=0), 1).item()
        sentence.append(tkn)
    return ints_to_tokens(itos, sentence)


def insert_values(tokens, values, value_tok):
    v_idx = 0
    if len(values) == 0:
        values = [None]
    for i in range(len(tokens)):
        if tokens[i] == value_tok:
            tokens[i] = str(values[v_idx])
            v_idx = (v_idx + 1) % len(values)  # If more value tokens than values, just keep inserting the last one
    return tokens


def logits_to_text(itos, logits, program=False, values=None, value_tok='VALUE'):
    tokens = logits_to_tokens(itos, logits)
    if values is not None:
        tokens = insert_values(tokens, values, value_tok)
    return tokens_to_str(tokens, program=program)


def sequence_to_text(itos, sentence, program=False, values=None, value_tok='VALUE'):
    tokens = ints_to_tokens(itos, sentence)
    if values is not None:
        tokens = insert_values(tokens, values, value_tok)
    return tokens_to_str(tokens, program=program)


def custom_collate_d(x):
    keys = x[0].keys()
    d = dict([(k, []) for k in keys])
    for i in range(len(x)):
        for k in keys:
            d[k].append(x[i][k])
    return d


def is_str_float(string):
    try:
        float(string)
        return True
    except ValueError:
        return False
