"""
Copyright 2022, The Johns Hopkins University Applied Physics Laboratory LLC
All rights reserved.
Distributed under the terms of the BSD 3-Clause License.

Approved for public release; distribution is unlimited.
This material is based upon work supported by the Defense Advanced Research Projects Agency (DARPA) under Agreement No.
HR00112290032.
"""

import numpy as np
import torch


def get_gen_hard_clf_labels(mb_size, device, label_id=1):
    return label_id * torch.ones(mb_size, dtype=torch.int64).to(device)


def get_gen_soft_clf_labels(mb_size, n_classes, device, label_probs=None):
    if label_probs != None:
        assert len(label_probs) == n_classes, "Number of label probabilities must match the number of classes."
        label_probs = torch.Tensor(label_probs).to(device)
    else:
        label_probs = torch.Tensor([1 / n_classes] * n_classes).to(device)
    return torch.ones((mb_size, 1), dtype=torch.int64).to(device) * label_probs


# Shutoff label function
def get_disc_clf_labels(arrs):
    def _find_sign_changes(arr):
        # Remove NaNs
        arr = arr[~np.isnan(arr)]
        asign = np.sign(arr)
        signchange = ((np.roll(asign, 1) - asign) != 0).astype(int)
        signchange[0] = 0  # don't check if first and last elements have sign change
        if signchange.any():
            return np.where(signchange == 1)[0]
        return None

    labels = []
    for arr in arrs[0]:  # for box model, M_n is the first nested array in arrs
        arr_lbl = _find_sign_changes(arr)
        if arr_lbl is not None:
            labels.append(1)
        else:
            labels.append(0)
    return np.array(labels)


def get_disc_clf_labels_three_class(arrs):
    def _find_sign_changes(arr):
        # Remove NaNs
        arr = arr[~np.isnan(arr)]
        asign = np.sign(arr)
        signchange = (np.roll(asign, 1) - asign).astype(int)
        signchange[0] = 0  # don't check if first and last elements have sign change

        # find shutoffs
        has_shutoff = signchange[signchange >= 1].size > 0

        # find recoveries
        has_recovery = signchange[signchange <= -1].size > 0

        # 0 = non-shutoff, 1 = shutoff, 2 = recovery
        if has_recovery:
            return 2
        if has_shutoff:
            return 1
        return 0

    labels = []
    for arr in arrs[0]:  # for box model, M_n is the first nested array in arrs
        arr_lbl = _find_sign_changes(arr)
        labels.append(arr_lbl)
    return np.array(labels)


def get_gen_mad_labels(mb_size, n_gens, device):
    return n_gens * torch.ones(mb_size, dtype=torch.int64).to(device)


def get_disc_mad_labels(mb_size, n_gens, device):
    labels = []
    for j in range(n_gens):
        labels.extend([j] * mb_size)
    labels.extend([int(n_gens)] * mb_size)
    labels = torch.LongTensor(labels).to(device)

    return labels
