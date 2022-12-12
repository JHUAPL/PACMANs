# Copyright 2022, The Johns Hopkins University Applied Physics Laboratory LLC
# All rights reserved.
# Distributed under the terms of the BSD 3-Clause License.

# Approved for public release; distribution is unlimited.
# This material is based upon work supported by the Defense Advanced Research Projects Agency (DARPA) under Agreement
# No. HR00112290032.

import json
import os

import torch


def _make_full_ckpt(model_ckpt, optim_state, lr_schedule_state, all_losses, loss_avgs, best_model,
                    best_loss, vocab):
    return {'model_ckpt': model_ckpt, 'optim_state': optim_state, 'lr_schedule_state': lr_schedule_state,
            'all_losses': all_losses, 'loss_avgs': loss_avgs, 'best_model': best_model, 'best_loss': best_loss,
            'vocab': vocab}


def _make_json_info(epoch, batch_id, all_losses, loss_avgs, best_loss, best_epoch, scores, mean_score,
                    from_checkpoint):
    return {'epoch': epoch, 'batch': batch_id,
            'all_losses': all_losses, 'loss_avgs': loss_avgs,
            'best_loss': best_loss, "best_epoch": best_epoch, 'scores': scores,
            "mean_score": mean_score, "from_checkpoint": from_checkpoint}


class PACModelCheckpointer:
    def __init__(self, checkpoint_dir=None, step_checkpoint=None, epoch_checkpoint=None):
        self.ckpt_dir = checkpoint_dir
        self.step_ckpt = step_checkpoint
        self.epoch_ckpt = epoch_checkpoint
        self.step_count = 0
        self.epoch_count = 0

    def _store(self, f_name, model, optimizer, lr_schedule, epoch, batch_id, all_losses, loss_avgs, best_model,
               best_loss, best_epoch, scores, mean_score, from_checkpoint, vocab):
        ckpt = model.store_model_params()
        optim_state = optimizer.state_dict()
        lr_schedule_state = lr_schedule.state_dict()
        save_info = _make_full_ckpt(ckpt, optim_state, lr_schedule_state, all_losses, loss_avgs,
                                    best_model, best_loss, vocab)
        torch.save(save_info, os.path.join(self.ckpt_dir, f_name + '.pt'))
        json_info = _make_json_info(epoch, batch_id, all_losses, loss_avgs, best_loss, best_epoch, scores,
                                    mean_score, from_checkpoint)
        with open(os.path.join(self.ckpt_dir, f_name + ".json"), 'w') as f:
            json.dump(json_info, f)

    def step(self, model, optimizer, lr_schedule, epoch, batch_id, all_losses, loss_avgs, best_model, best_loss,
             best_epoch, scores, mean_score, from_checkpoint, vocab):
        """
        Stores model checkpoint and info on the correct step. If no checkpoint directory or step info is provided, then
        it does nothing.
        """
        self.step_count += 1
        if self.step_ckpt and self.step_count % self.step_ckpt == 0:
            if self.ckpt_dir:
                self._store(f"step-{self.step_count}-checkpoint", model, optimizer, lr_schedule, epoch, batch_id,
                            all_losses, loss_avgs, best_model, best_loss, best_epoch, scores, mean_score,
                            from_checkpoint, vocab)

    def epoch(self, model, optimizer, lr_schedule, epoch, batch_id, all_losses, loss_avgs, best_model, best_loss,
              best_epoch, scores, mean_score, from_checkpoint, vocab):
        """
        Stores model checkpoint and info on the correct epoch. If no checkpoint directory or step info is provided, then
        it does nothing.
        """
        self.epoch_count += 1
        if self.epoch_ckpt and self.epoch_count % self.epoch_ckpt == 0:
            if self.ckpt_dir:
                self._store(f"epoch-{self.epoch_count}-checkpoint", model, optimizer, lr_schedule, epoch, batch_id,
                            all_losses, loss_avgs, best_model, best_loss, best_epoch, scores, mean_score,
                            from_checkpoint, vocab)


def convert_model_to_checkpoint(path_to_model, path_to_vocab):
    model_ckpt = torch.load(path_to_model)
    vocab = torch.load(path_to_vocab)
    new_cktp = _make_full_ckpt(model_ckpt, None, None, [], [], model_ckpt, 0, vocab)
    torch.save(new_cktp, path_to_model)
