"""
Copyright 2022, The Johns Hopkins University Applied Physics Laboratory LLC
All rights reserved.
Distributed under the terms of the BSD 3-Clause License.

Approved for public release; distribution is unlimited.
This material is based upon work supported by the Defense Advanced Research Projects Agency (DARPA) under Agreement No.
HR00112290032.

Implementation based on:
Ghosh, Arnab, Viveka Kulharia, Vinay P. Namboodiri, Philip HS Torr, and Puneet K. Dokania. "Multi-agent diverse generative adversarial networks." In Proceedings of the IEEE conference on computer vision and pattern recognition, pp. 8513-8521. 2018.

"""

import torch
from torch import nn


class MinibatchDiscrimination(nn.Module):
    def __init__(self, in_features, out_features, use_mean=False):
        super().__init__()
        self.in_features = in_features
        self.out_features = out_features
        self.use_mean = use_mean
        self.T = nn.Parameter(torch.Tensor(in_features, out_features))
        nn.init.normal_(self.T, 0, 1)

    def forward(self, x):
        # x is NxA
        # T is AxB
        matrices = x.mm(self.T)

        M = matrices.unsqueeze(0)  # 1xNxB
        M_T = M.permute(1, 0, 2)  # Nx1xB
        norm = torch.abs(M - M_T)  # NxNxB
        expnorm = torch.exp(-norm)
        o_b = (expnorm.sum(dim=0) - 1)  # NxB, subtract self distance
        if self.use_mean:
            o_b /= x.size(0) - 1

        x = torch.cat([x, o_b], axis=1)
        return x


class DiscriminatorBase(nn.Module):
    def __init__(self, in_size=4, h_sizes=[128, 128]):
        super(DiscriminatorBase, self).__init__()
        # Create base layers
        self.n_layers = len(h_sizes)

        for i, (in_sz, out_sz) in enumerate(zip([in_size] + h_sizes[:-1],
                                                h_sizes)):
            setattr(self, f"base_{i}", nn.Linear(in_sz, out_sz))
            setattr(self, f"elu_{i}", nn.ELU())

            # Initialize weights
            nn.init.xavier_normal_(getattr(self, f"base_{i}").weight)
            getattr(self, f"base_{i}").bias.data.fill_(0.01)

    def forward(self, x):
        for i in range(self.n_layers):
            x = getattr(self, f"base_{i}")(x)
            x = getattr(self, f"elu_{i}")(x)
        return x


class DiscriminatorMADClf(nn.Module):
    def __init__(self, disc_base, mb_disc_out, n_modes, n_classes, use_mean=False, h_sizes=[]):
        super(DiscriminatorMADClf, self).__init__()
        self.disc_base = disc_base

        self.n_hidden_layers = len(h_sizes)
        last_base_layer = getattr(self.disc_base, f"base_{self.disc_base.n_layers - 1}")
        prev_layer = last_base_layer
        for i, (in_sz, out_sz) in enumerate(zip([last_base_layer.out_features] + h_sizes[:-1],
                                                h_sizes[1:])):
            setattr(self, f"l_{i}", nn.Linear(in_sz, out_sz))
            prev_layer = getattr(self, f"l_{i}")
            setattr(self, f"elu_{i}", nn.ELU())

            nn.init.xavier_normal_(getattr(self, f"l_{i}").weight)
            getattr(self, f"l_{i}").bias.data.fill_(0.01)

        self.mb_disc = MinibatchDiscrimination(in_features=prev_layer.out_features, out_features=mb_disc_out,
                                               use_mean=use_mean)
        self.mad_head = nn.Linear(prev_layer.out_features + self.mb_disc.out_features, n_modes + 1)
        nn.init.xavier_normal_(self.mad_head.weight)
        self.mad_head.bias.data.fill_(0.01)

        self.clf_head = nn.Linear(prev_layer.out_features, n_classes)
        nn.init.xavier_normal_(self.clf_head.weight)
        self.clf_head.bias.data.fill_(0.01)

    def forward(self, x):
        x = self.disc_base(x)

        for i in range(self.n_hidden_layers):
            x = getattr(self, f"l_{i}")(x)
            x = getattr(self, f"elu_{i}")(x)

        # MAD-GAN discriminator
        x_sims = self.mb_disc(x)
        mad_logits = self.mad_head(x_sims)

        # Shut-off discriminator
        clf_logits = self.clf_head(x)
        return mad_logits, clf_logits



if __name__ == "__main__":
    in_size = 4
    mb_disc_out = 128
    disc_base = DiscriminatorBase(in_size=in_size)
    disc = DiscriminatorMADBinary(disc_base=disc_base, mb_disc_out=mb_disc_out, n_modes=4)

    # Create random tensor
    input = torch.randn(32, 4)

    mad_logits, clf_logits = disc(input)
    print(mad_logits.shape, clf_logits.shape)

# print("Number of zeros in similarities: ", zero_ct)
