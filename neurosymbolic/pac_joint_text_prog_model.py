# Copyright 2022, The Johns Hopkins University Applied Physics Laboratory LLC
# All rights reserved.
# Distributed under the terms of the BSD 3-Clause License.

# Approved for public release; distribution is unlimited.
# This material is based upon work supported by the Defense Advanced Research Projects Agency (DARPA) under Agreement
# No. HR00112290032.

import copy
import warnings

import numpy as np
import torch
import torch.nn as nn
# from rapidfuzz.string_metric import levenshtein  # choose between this or the next line's version
from rapidfuzz.string_metric import normalized_levenshtein
from torch.nn import Embedding
from torch.optim.lr_scheduler import ReduceLROnPlateau
from torch.utils.data import DataLoader
from torchtext.data.metrics import bleu_score
from tqdm import tqdm

from .pac_model_checkpointer import PACModelCheckpointer
from .pos_embedding import LearnedPositionalEmbedding
from .utils import logits_to_text, sequence_to_text, ints_to_tokens, logits_to_tokens, \
    custom_collate_d


class PACJointTextProgModelConfig:
    """Configuration object for PACMANS model"""
    def __init__(self,
                 vocab,
                 max_seq_len,
                 value_token,
                 begin_sentence_token,
                 end_sentence_token,
                 device=None,
                 rng=None):
        self.vocab = vocab
        self.max_seq_len = max_seq_len
        self.value_token = value_token
        self.begin_sentence_token = begin_sentence_token
        self.end_sentence_token = end_sentence_token
        self.device = device
        self.begin_sentence_token_idx = vocab[begin_sentence_token]
        self.rng = rng

    def to_dict(self):
        return self.__dict__

    def to_json(self):
        d = self.to_dict()
        d['vocab'] = str(self.vocab.get_itos())
        d['rng'] = str(self.rng)


class PACJointTextProgModel(nn.Module):
    """PACMANS Joint text-to-text, text-to-program, and program-to-text model"""
    def __init__(self, config: PACJointTextProgModelConfig):
        super().__init__()
        self.config = config
        self.vocab = config.vocab
        self.vocab_size = len(self.vocab)
        self.itos = self.vocab.get_itos()
        self.max_seq_len = config.max_seq_len
        self.value_token = config.value_token
        self.begin_sentence_token = config.begin_sentence_token
        self.end_sentence_token = config.end_sentence_token
        self.value_token_idx = self.vocab[config.value_token]
        self.begin_sentence_token_idx = self.vocab[config.begin_sentence_token]
        self.end_sentence_token_idx = self.vocab[config.end_sentence_token]
        self.rng = config.rng if config.rng is not None else np.random.RandomState()

        # configure what device to use based on 'device' argument
        if config.device is not None:
            self.device = config.device
        else:
            self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print(f'attempting to use device: {self.device}')  # todo: pass to a logger?

        self.encoder_hidden_state = None
        self.prog_encoder_hidden_state = None

        # This is currently set arbitrarily to keep the loss from the sequence length difference small
        self.len_diff_const = 0.001

        # set network dimensions and parameters
        self.embedding_dim = 512
        self.pos_embedding_dim = 128
        self.encoder_hidden_dim = 512
        self.encoder_num_layers = 2  # changing requires editing the encoder code
        self.decoder_num_layers = 1
        self.decoder_hidden_size = 2 * self.encoder_hidden_dim
        self.decoder_bidirectional = False
        #   program decoder version
        self.prog_decoder_num_layers = 1
        self.prog_decoder_hidden_size = 2 * self.encoder_hidden_dim
        self.prog_decoder_bidirectional = False

        # set up ANNs
        self.word_embedding = Embedding(self.vocab_size, self.embedding_dim)
        self.word_pos_embedding = LearnedPositionalEmbedding(self.max_seq_len, self.pos_embedding_dim,
                                                             padding_idx=0, left_pad=False)
        self.encoder = nn.GRU(input_size=self.embedding_dim + self.pos_embedding_dim,
                              hidden_size=self.encoder_hidden_dim, num_layers=self.encoder_num_layers,
                              bidirectional=True)
        self.text_decoder_gru = nn.GRU(input_size=self.encoder_hidden_dim + self.pos_embedding_dim,  # + self.vocab_size
                                       hidden_size=self.decoder_hidden_size, num_layers=self.decoder_num_layers,
                                       bidirectional=self.decoder_bidirectional, batch_first=True)
        self.decoder_to_logits_mid_size = int(self.decoder_hidden_size / 2)
        self.text_decoder_out_to_logits = nn.Sequential(
            torch.nn.Linear(self.decoder_hidden_size + self.decoder_hidden_size * self.decoder_bidirectional,
                            self.decoder_to_logits_mid_size),
            torch.nn.LeakyReLU(),
            torch.nn.Linear(self.decoder_to_logits_mid_size, self.vocab_size),
        )

        # At this time, this is essentially a replica of the text decoder
        self.prog_encoder = nn.GRU(input_size=self.embedding_dim + self.pos_embedding_dim,
                                   hidden_size=self.encoder_hidden_dim, num_layers=self.encoder_num_layers,
                                   bidirectional=True)
        self.prog_decoder_gru = nn.GRU(input_size=self.encoder_hidden_dim + self.pos_embedding_dim,
                                       hidden_size=self.prog_decoder_hidden_size,
                                       num_layers=self.prog_decoder_num_layers,
                                       bidirectional=self.prog_decoder_bidirectional, batch_first=True)
        self.prog_decoder_to_logits_mid_size = int(self.prog_decoder_hidden_size / 2)
        self.prog_decoder_out_to_logits = nn.Sequential(
            torch.nn.Linear(self.prog_decoder_hidden_size
                            + self.prog_decoder_hidden_size * self.prog_decoder_bidirectional,
                            self.prog_decoder_to_logits_mid_size),
            torch.nn.LeakyReLU(),
            torch.nn.Linear(self.prog_decoder_to_logits_mid_size, self.vocab_size),
        )

        # final cleanup
        self._init_weights()
        self.to(self.device)

    def set_encoder_hidden_state(self, batch_size):
        # encoder is bidirectional
        self.encoder_hidden_state = torch.zeros(self.encoder_num_layers * 2, batch_size,
                                                self.encoder_hidden_dim, device=self.device)

    def set_prog_encoder_hidden_state(self, batch_size):
        # encoder is bidirectional
        self.prog_encoder_hidden_state = torch.zeros(self.encoder_num_layers * 2, batch_size,
                                                     self.encoder_hidden_dim, device=self.device)

    def _init_weights(self):
        for m in self.modules():
            if isinstance(m, nn.Embedding):
                torch.nn.init.uniform_(m.weight, -0.001, 0.001)
            elif isinstance(m, nn.Linear):
                torch.nn.init.xavier_uniform_(m.weight)
                m.bias.data.fill_(0.01)

    def store_model_params(self):
        model = {
            'word_embedding': copy.deepcopy(self.word_embedding.state_dict()),
            'word_pos_embedding': copy.deepcopy(self.word_pos_embedding.state_dict()),
            'encoder': copy.deepcopy(self.encoder.state_dict()),
            'text_decoder_gru': copy.deepcopy(self.text_decoder_gru.state_dict()),
            'text_decoder_out_to_logits': copy.deepcopy(self.text_decoder_out_to_logits.state_dict()),
            'prog_encoder': copy.deepcopy(self.prog_encoder.state_dict()),
            'prog_decoder_gru': copy.deepcopy(self.prog_decoder_gru.state_dict()),
            'prog_decoder_out_to_logits': copy.deepcopy(self.prog_decoder_out_to_logits.state_dict())
        }
        return model

    def load_model_params(self, checkpoint):
        self.word_embedding.load_state_dict(checkpoint['word_embedding'])
        self.word_pos_embedding.load_state_dict(checkpoint['word_pos_embedding'])
        self.encoder.load_state_dict(checkpoint['encoder'])
        self.text_decoder_gru.load_state_dict(checkpoint['text_decoder_gru'])
        self.text_decoder_out_to_logits.load_state_dict(checkpoint['text_decoder_out_to_logits'])
        self.prog_encoder.load_state_dict(checkpoint['prog_encoder'])
        self.prog_decoder_gru.load_state_dict(checkpoint['prog_decoder_gru'])
        self.prog_decoder_out_to_logits.load_state_dict(checkpoint['prog_decoder_out_to_logits'])

    def compute_loss_w_prog(self, loss_func, text_logits, text_true, prog_logits, prog_true, prog_to_text_logits):
        combined_loss = []
        for i in range(len(text_logits)):
            end = min(len(text_logits[i]), len(text_true[i]))
            diff = abs(len(text_logits[i]) - len(text_true[i]))
            diff_loss = torch.tensor(diff).float().to(self.device) * self.len_diff_const
            text_loss = (loss_func(text_logits[i][:end], text_true[i][:end]) - diff_loss).unsqueeze(0)

            end = min(len(prog_logits[i]), len(prog_true[i]))
            diff = abs(len(prog_logits[i]) - len(prog_true[i]))
            diff_loss = torch.tensor(diff).float().to(self.device) * self.len_diff_const
            prog_loss = (loss_func(prog_logits[i][:end], prog_true[i][:end]) - diff_loss).unsqueeze(0)

            end = min(len(prog_to_text_logits[i]), len(text_true[i]))
            diff = abs(len(prog_to_text_logits[i]) - len(text_true[i]))
            diff_loss = torch.tensor(diff).float().to(self.device) * self.len_diff_const
            prog_to_text_loss = (loss_func(prog_to_text_logits[i][:end], text_true[i][:end]) - diff_loss).unsqueeze(0)
            combined_loss.append(text_loss + prog_loss + prog_to_text_loss)
        return torch.mean(torch.cat(combined_loss, dim=0))

    def _val(self, eval_strat, val_dataloader):
        with torch.no_grad():
            if eval_strat == 'bleu':
                scores, mean_score = self.blue_eval(val_dataloader)
            else:
                scores, mean_score, _ = self.eval_equal_acc(val_dataloader)
                mean_score = np.mean([v for v in mean_score.values() if not np.isnan(v)])
        self.train()
        return scores, mean_score

    def train_everything(self, dataset, epochs, batch_size, lr=0.001, weight_decay=0.0, min_lr=1e-6, val_dataset=None,
                         eval_freq=1, eval_strat='eq_score', checkpointer=None, checkpoint=None, batch_bar_update=100):

        if eval_strat not in ['eq_score', 'bleu']:
            raise ValueError(f"Parameter 'eval_strat' must by in {['eq_score', 'bleu']}")
        if eval_strat == 'bleu':
            warnings.warn("Program performance is not computed for BLEU score.")
        if checkpointer is None:
            checkpointer = PACModelCheckpointer()  # does nothing by default

        best_loss = np.inf
        best_model = None
        best_epoch = 0

        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True, collate_fn=custom_collate_d,
                                pin_memory=True)
        if val_dataset is not None:
            val_dataloader = DataLoader(val_dataset, batch_size=1, shuffle=False, collate_fn=custom_collate_d,
                                        pin_memory=True)
        else:
            val_dataloader = None
        optimizer = torch.optim.Adam(self.parameters(), lr=lr, weight_decay=weight_decay)
        lr_schedule = ReduceLROnPlateau(optimizer, patience=20, threshold=1e-4, min_lr=min_lr)
        # lr_schedule is currently set to reduce by epoch, which doesn't do anything with as few epochs as we train,
        #   we could instead update by batch
        loss_func = torch.nn.CrossEntropyLoss()
        self.train()
        loss_avgs = []
        scores, mean_score = np.nan, np.nan
        all_losses = []

        if checkpoint:
            ckpt = torch.load(checkpoint)
            max_seq_len = ckpt['model_ckpt']['word_pos_embedding']['weight'].shape[0]
            if self.word_pos_embedding.weight.shape[0] != max_seq_len:
                self.word_pos_embedding = LearnedPositionalEmbedding(max_seq_len, self.pos_embedding_dim, 
                        padding_idx=0, left_pad=False).to(self.device)
            self.load_model_params(ckpt['model_ckpt'])
            if ckpt['optim_state'] is not None and ckpt['lr_schedule_state'] is not None:
                # if checkpoint was built from just a model file, these don't apply
                optimizer.load_state_dict(ckpt['optim_state'])
                lr_schedule.load_state_dict(ckpt['lr_schedule_state'])
                loss_avgs, all_losses = ckpt['loss_avgs'], ckpt['all_losses']
                best_loss, best_model = ckpt['best_loss'], ckpt['best_model']

        if val_dataloader is not None:
            scores, mean_score = self._val(eval_strat, val_dataloader)

        for e in range(epochs):
            temp_losses = []
            num_batches = int(len(dataset) / batch_size) + 1
            with tqdm(total=num_batches) as batch_bar:
                tmp_loss = all_losses[-1] if len(all_losses) > 0 else np.nan
                batch_bar.set_description(f'Epoch: {e}, batch: {0}, loss: {tmp_loss}')
                for batch_id, batch in enumerate(dataloader):
                    sentences = batch['questions']
                    seq_lengths = batch['seq_lengths']
                    true_sentences = batch['gt_questions']
                    programs = batch['programs']
                    self.set_encoder_hidden_state(len(sentences))
                    self.set_prog_encoder_hidden_state(len(sentences))
                    optimizer.zero_grad()
                    sentences_sort = sorted(range(len(sentences)), key=lambda t: sentences[t].shape[0],
                                            reverse=True)
                    sentences = [sentences[idx].to(self.device) for idx in sentences_sort]
                    true_sentences = [true_sentences[idx].to(self.device) for idx in sentences_sort]
                    seq_lengths = [seq_lengths[idx].to(self.device) for idx in sentences_sort]
                    programs = [programs[idx].to(self.device) for idx in sentences_sort]
                    encoded = self.encode(sentences)
                    logits, decoded = self.decode(encoded, seq_lengths)
                    prog_logits, prog_decoded = self.decode_program(encoded)
                    prog_encoded = self.encode_prog(programs)
                    prog_to_text_logits, prog_to_text_decoded = self.decode(prog_encoded, None)
                    loss = self.compute_loss_w_prog(loss_func, logits, true_sentences, prog_logits, programs,
                                                    prog_to_text_logits)
                    # todo: add value difference to loss?
                    loss.backward()
                    temp_losses.append(loss.unsqueeze(0))
                    all_losses.append(temp_losses[-1].item())
                    optimizer.step()
                    if (batch_id + 1) % batch_bar_update == 0 or (batch_id + 1) == num_batches:
                        batch_bar.update(batch_bar_update)
                        batch_bar.set_description(f'Epoch: {e + 1}, batch: {batch_id + 1}, loss: {all_losses[-1]}')

                    checkpointer.step(self, optimizer, lr_schedule, e, batch_id, all_losses, loss_avgs, best_model,
                                      best_loss, best_epoch, scores, mean_score, checkpoint, self.vocab)

            loss_avgs.append(torch.mean(torch.cat(temp_losses)).item())

            # best model tracking
            if loss_avgs[-1] < best_loss:
                best_loss = loss_avgs[-1]
                best_model = self.store_model_params()
                best_epoch = e + 1  # offset due to 0 indexing
            lr_schedule.step(loss_avgs[-1])

            if val_dataloader is not None and (e + 1) % eval_freq == 0:
                scores, mean_score = self._val(eval_strat, val_dataloader)

            checkpointer.epoch(self, optimizer, lr_schedule, e, batch_id, all_losses, loss_avgs, best_model, best_loss,
                               best_epoch, scores, mean_score, checkpoint, self.vocab)

            desc = f"last avg loss: {np.round(loss_avgs[-1], 4)}, avg {eval_strat}: {np.round(mean_score, 4)}"
            print('\n' + desc + '\n')
        return best_model, best_loss, best_epoch, loss_avgs, all_losses

    def encode(self, sequence):
        hidden = self.encoder_hidden_state
        sequence = [torch.cat([self.word_embedding(s), self.word_pos_embedding(s.unsqueeze(0)).squeeze(0)],
                              dim=-1) for s in sequence]
        sequence = torch.nn.utils.rnn.pack_sequence(sequence)
        out, h_t = self.encoder(sequence, hidden)
        return h_t[-2:, :, :]

    def encode_prog(self, program):
        hidden = self.prog_encoder_hidden_state
        sequence = [torch.cat([self.word_embedding(s), self.word_pos_embedding(s.unsqueeze(0)).squeeze(0)],
                              dim=-1) for s in program]
        sequence = torch.nn.utils.rnn.pack_sequence(sequence, enforce_sorted=False)
        out, h_t = self.prog_encoder(sequence, hidden)
        return h_t[-2:, :, :]

    def decode(self, encoding, seq_lens):
        batch_size = encoding.shape[1]
        inps = torch.cat([torch.tensor(
            [self.vocab['BOS']]).to(self.device) for _ in range(batch_size)]
                         ).reshape(batch_size, 1)
        logit_list = []
        sentences = []
        for i in range(batch_size):
            hidden = encoding[:, i, :].reshape(1, self.encoder_hidden_dim * 2)
            inp = torch.cat(
                [self.word_embedding(inps[i]), self.word_pos_embedding(inps[i].unsqueeze(0)).squeeze(0)],
                dim=-1)
            logits = []
            sentence = []
            iters = seq_lens[i] if seq_lens else self.max_seq_len
            for j in range(iters):
                out, hidden = self.text_decoder_gru(inp, hidden)
                lg = self.text_decoder_out_to_logits(out)
                logits.append(lg)
                tok_idx = torch.argmax(lg, dim=1)
                sentence.append(tok_idx)
                if tok_idx == self.end_sentence_token_idx:
                    break
                wp_embedding = self.word_pos_embedding(torch.cat(sentence, dim=0).unsqueeze(0))[:, -1, :]
                inp = torch.cat([self.word_embedding(tok_idx), wp_embedding], dim=-1).float()
            logits = torch.cat(logits, dim=0)
            logit_list.append(logits)
            sentences.append(torch.cat(sentence))
        return logit_list, sentences

    def decode_program(self, encoding):
        batch_size = encoding.shape[1]
        inps = torch.cat([torch.tensor(
            [self.vocab['BOS']]).to(self.device) for _ in range(batch_size)]
                         ).reshape(batch_size, 1)
        logit_list = []
        sentences = []
        for i in range(batch_size):
            hidden = encoding[:, i, :].reshape(1, self.encoder_hidden_dim * 2)
            inp = torch.cat(
                [self.word_embedding(inps[i]), self.word_pos_embedding(inps[i].unsqueeze(0)).squeeze(0)],
                dim=-1)
            logits = []
            sentence = []
            itr = 0
            for j in range(self.max_seq_len):
                out, hidden = self.prog_decoder_gru(inp, hidden)
                lg = self.prog_decoder_out_to_logits(out)
                logits.append(lg)
                tok_idx = torch.argmax(lg, dim=1)
                sentence.append(tok_idx)
                if tok_idx == self.end_sentence_token_idx:
                    break
                wp_embedding = self.word_pos_embedding(torch.cat(sentence, dim=0).unsqueeze(0))[:, -1, :]
                inp = torch.cat([self.word_embedding(tok_idx), wp_embedding], dim=-1).float()
                itr += 1
            logits = torch.cat(logits, dim=0)
            logit_list.append(logits)
            sentences.append(torch.cat(sentence))
        return logit_list, sentences

    def print_decodings(self, dataloader, max_out=10, use_logits=False):
        """Helper function for converting decoded vector representations into readable text"""
        self.eval()
        for batch_id, batch in enumerate(dataloader):
            sentences = batch['questions']
            seq_lengths = batch['seq_lengths']
            true_sentences = batch['gt_questions']
            if batch_id > max_out - 1:
                break
            sentences = [s.to(self.device) for s in sentences]
            seq_lengths = [s.to(self.device) for s in seq_lengths]
            true_sentences = [s.to(self.device) for s in true_sentences]
            self.set_encoder_hidden_state(len(sentences))
            self.set_prog_encoder_hidden_state(len(sentences))
            encoded = self.encode(sentences)
            logits, decoded = self.decode(encoded, seq_lengths)
            if use_logits:
                text = logits_to_text(self.itos, logits[0], values=batch['values'][0], value_tok=self.value_token)
                print(f"Predicted text: {text}")
            else:
                text = sequence_to_text(self.itos, decoded[0], values=batch['values'][0], value_tok=self.value_token)
                print(f"Predicted text: {text}")
            text = sequence_to_text(self.itos, true_sentences[0], values=batch['values'][0], value_tok=self.value_token)
            print(f"Ground Truth Text: {text}")
            logits, decoded = self.decode_program(encoded)
            if use_logits:
                text = logits_to_text(self.itos, logits[0], program=True, values=batch['values'][0],
                                      value_tok=self.value_token)
                print(f"Predicted program: {text}")
            else:
                text = sequence_to_text(self.itos, decoded[0], program=True, values=batch['values'][0],
                                        value_tok=self.value_token)
                print(f"Predicted program: {text}")
            text = sequence_to_text(self.itos, batch['programs'][0], program=True, values=batch['values'][0],
                                    value_tok=self.value_token)
            print(f"Ground Truth program: {text}")
            programs = [s.to(self.device) for s in batch['programs']]
            prog_encoded = self.encode_prog(programs)
            prog_to_text_logits, prog_to_text_decoded = self.decode(prog_encoded, None)
            if use_logits:
                text = logits_to_text(self.itos, prog_to_text_logits[0], values=batch['values'][0],
                                      value_tok=self.value_token)
                print(f"Predicted text from program: {text}")
            else:
                text = sequence_to_text(self.itos, prog_to_text_decoded[0], values=batch['values'][0],
                                        value_tok=self.value_token)
                print(f"Predicted text from program: {text}")

            print()

    def blue_eval(self, dataloader, use_logits=False):
        """Evaluation function for evaluation using BLEU score"""
        self.eval()
        scores = []
        total = int(len(dataloader.dataset) / dataloader.batch_size)
        for batch_id, batch in tqdm(enumerate(dataloader), total=total, desc="Bleu score"):
            sentences = batch['questions']
            seq_lengths = batch['seq_lengths']
            true_sentences = batch['gt_questions']
            self.set_encoder_hidden_state(len(sentences))
            self.set_prog_encoder_hidden_state(len(sentences))
            sentences = [s.to(self.device) for s in sentences]
            seq_lengths = [s.to(self.device) for s in seq_lengths]
            true_sentences = [s.to(self.device) for s in true_sentences]
            encoded = self.encode(sentences)
            logits, decoded = self.decode(encoded, seq_lengths)
            if use_logits:
                tokens_cand = logits_to_tokens(self.itos, logits[0])
                tokens_ref = ints_to_tokens(self.itos, true_sentences[0])
                score = bleu_score([tokens_cand], [[tokens_ref]], max_n=2, weights=[0.5, 0.5])
            else:
                tokens_cand = ints_to_tokens(self.itos, decoded[0])
                tokens_ref = ints_to_tokens(self.itos, true_sentences[0])
                score = bleu_score([tokens_cand], [[tokens_ref]], max_n=2, weights=[0.5, 0.5])
            scores.append(score)
        return scores, np.mean(scores)

    def _equal_acc(self, t1, t2):
        batch_size = len(t1)
        l = []
        for i in range(batch_size):
            end = min(len(t1[i]), len(t2[i]))
            diff = torch.tensor(abs(len(t1[i]) - len(t2[i]))).float().to(self.device) * self.len_diff_const
            l.append(((torch.sum(t1[i][:end] == t2[i][:end]) / len(t2[i])).item() - diff).unsqueeze(0))
        return l

    def eval_equal_acc(self, dataloader, get_detailed_scores=False):
        """Evaluation function checking if each token in each sequence is the same"""
        # Note: setting batch_size > 1 might violate assumptions later on in the function...
        self.eval()
        scores = dict()
        detailed_scores = {"text_to_text": {}, "text_to_program": {}, "program_to_text": {}}
        # Note: if also decoding programs, programs of different lengths are simply aggregated to the scores. Might be
        #   be better to report them disjointly in the future.
        total = int(len(dataloader.dataset) / dataloader.batch_size)
        for batch_id, batch in tqdm(enumerate(dataloader), total=total, desc="Eq_score"):
            sentences = batch['questions']
            seq_lengths = torch.LongTensor([it.shape[0] for it in sentences])
            true_sentences = batch['gt_questions']
            self.set_encoder_hidden_state(len(sentences))
            self.set_prog_encoder_hidden_state(len(sentences))

            sentences_sort = sorted(range(len(sentences)), key=lambda t: sentences[t].shape[0], reverse=True)
            sentences = [sentences[idx].to(self.device) for idx in sentences_sort]
            true_sentences = [true_sentences[idx].to(self.device) for idx in sentences_sort]
            seq_lengths = [seq_lengths[idx].to(self.device) for idx in sentences_sort]

            encoding = self.encode(sentences)
            logits, decoded = self.decode(encoding, seq_lengths)
            score = self._equal_acc(decoded, true_sentences)
            if len(true_sentences[0]) not in scores.keys():
                scores[len(true_sentences[0])] = []
            scores[len(true_sentences[0])] += [s.item() for s in score]
            if get_detailed_scores:
                if len(true_sentences[0]) not in detailed_scores["text_to_text"].keys():
                    detailed_scores["text_to_text"][len(true_sentences[0])] = []
                detailed_scores["text_to_text"][len(true_sentences[0])] += [s.item() for s in score]

            programs = batch['programs']
            programs = [programs[idx].to(self.device) for idx in sentences_sort]
            logits, decoded = self.decode_program(encoding)
            score = self._equal_acc(decoded, programs)
            if batch['programs'][0].shape[0] not in scores.keys():  # should be the length of the sequence
                scores[batch['programs'][0].shape[0]] = []
            scores[batch['programs'][0].shape[0]] += [s.item() for s in score]
            if get_detailed_scores:
                if batch['programs'][0].shape[0] not in detailed_scores["text_to_program"].keys():
                    detailed_scores["text_to_program"][batch['programs'][0].shape[0]] = []
                detailed_scores["text_to_program"][batch['programs'][0].shape[0]] += [s.item() for s in score]

            prog_encoded = self.encode_prog(programs)
            prog_to_text_logits, prog_to_text_decoded = self.decode(prog_encoded, None)
            score = self._equal_acc(prog_to_text_decoded, true_sentences)
            scores[len(true_sentences[0])] += [s.item() for s in score]
            if get_detailed_scores:
                if batch['programs'][0].shape[0] not in detailed_scores["program_to_text"].keys():
                    detailed_scores["program_to_text"][batch['programs'][0].shape[0]] = []
                detailed_scores["program_to_text"][batch['programs'][0].shape[0]] += [s.item() for s in score]

        mean_scores = dict((k, np.mean(v)) for k, v in scores.items() if len(v) > 0)
        return scores, mean_scores, detailed_scores

    def _lev_dist(self, gt, pred, values, value_tok, program=False):
        """
        where gt and pred are lists of ground truth and predicted output tensors respectively
        """
        gt_text = sequence_to_text(self.itos, gt, values=values, program=program, value_tok=value_tok)
        pred_text = sequence_to_text(self.itos, pred, values=values, program=program, value_tok=value_tok)
        lev = normalized_levenshtein(gt_text, pred_text)
        # lev = levenshtein(gt_text, pred_text)
        return lev
            
    def eval_lev_dist(self, dataloader, get_detailed_scores=True):
        """Performance measure using Levenshtein distance"""
        assert dataloader.batch_size == 1  # required for this code to run
        self.eval()
        scores = dict()
        detailed_dist = {"text_to_text": {}, "text_to_program": {}, "program_to_text": {}}
        total = int(len(dataloader.dataset) / dataloader.batch_size)
        for batch_id, batch in tqdm(enumerate(dataloader), total=total, desc="Lev distance"):
            sentences = batch['questions']
            seq_lengths = torch.LongTensor([it.shape[0] for it in sentences])
            true_sentences = batch['gt_questions']
            self.set_encoder_hidden_state(len(sentences))
            self.set_prog_encoder_hidden_state(len(sentences))

            sentences_sort = sorted(range(len(sentences)), key=lambda t: sentences[t].shape[0], reverse=True)
            sentences = [sentences[idx].to(self.device) for idx in sentences_sort]
            true_sentences = [true_sentences[idx].to(self.device) for idx in sentences_sort]
            seq_lengths = [seq_lengths[idx].to(self.device) for idx in sentences_sort]

            encoding = self.encode(sentences)
            logits, decoded = self.decode(encoding, seq_lengths)
            score = self._lev_dist(true_sentences[0], decoded[0], values=batch['values'][0], value_tok=self.value_token)
            if len(true_sentences[0]) not in scores.keys():
                scores[len(true_sentences[0])] = []
            scores[len(true_sentences[0])].append(score)
            if get_detailed_scores:
                k = len(decoded[0])
                if k not in detailed_dist['text_to_text']:
                    detailed_dist['text_to_text'][k] = []
                detailed_dist['text_to_text'][k].append(score)

            programs = batch['programs']
            programs = [programs[idx].to(self.device) for idx in sentences_sort]
            logits, decoded = self.decode_program(encoding)
            score = self._lev_dist(programs[0], decoded[0], values=batch['values'][0], value_tok=self.value_token,
                                   program=True)
            if batch['programs'][0].shape[0] not in scores.keys():  # should be the length of the sequence
                scores[batch['programs'][0].shape[0]] = []
            scores[batch['programs'][0].shape[0]].append(score)
            if get_detailed_scores:
                k = len(decoded[0])
                if k not in detailed_dist['text_to_program']:
                    detailed_dist['text_to_program'][k] = []
                detailed_dist['text_to_program'][k].append(score)
            prog_encoded = self.encode_prog(programs)
            prog_to_text_logits, prog_to_text_decoded = self.decode(prog_encoded, None)
            score = self._lev_dist(true_sentences[0], prog_to_text_decoded[0], values=batch['values'][0],
                                   value_tok=self.value_token)
            scores[len(true_sentences[0])].append(score)
            if get_detailed_scores:
                k = len(prog_to_text_decoded[0])
                if k not in detailed_dist['program_to_text']:
                    detailed_dist['program_to_text'][k] = []
                detailed_dist['program_to_text'][k].append(score)
        mean_scores = dict((k, np.mean(v)) for k, v in scores.items() if len(v) > 0)  # this is like a mean of means
        return scores, mean_scores, detailed_dist    

