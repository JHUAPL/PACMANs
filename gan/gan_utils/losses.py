"""
Copyright 2022, The Johns Hopkins University Applied Physics Laboratory LLC
All rights reserved.
Distributed under the terms of the BSD 3-Clause License.

Approved for public release; distribution is unlimited.
This material is based upon work supported by the Defense Advanced Research Projects Agency (DARPA) under Agreement No.
HR00112290032.
"""

import torch


# MAD-GAN loss
def mad_gan_loss(logits, labels):
    return torch.nn.functional.cross_entropy(logits, labels)


# Classification loss
def off_state_clf_loss(logits, labels, class_wts=None):
    return torch.nn.functional.cross_entropy(logits, labels, weight=class_wts)


# MAD-CLF loss
def mad_clf_loss(gan_logits, gan_labels, clf_logits, clf_labels, class_wts=None, gan_wt=1.0):
    gan_loss = mad_gan_loss(gan_logits, gan_labels)
    clf_loss = off_state_clf_loss(clf_logits, clf_labels, class_wts=class_wts)

    return gan_wt * gan_loss + clf_loss
