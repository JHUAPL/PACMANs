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
import numpy as np
from torch import nn


class GeneratorBase(nn.Module):
    def __init__(self, z_size=64, h_sizes=[128, 128]):
        super(GeneratorBase, self).__init__()
        # Create base layers
        self.n_layers = len(h_sizes)

        for i, (in_sz, out_sz) in enumerate(zip([z_size] + h_sizes[:-1],
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


class GeneratorAdv(nn.Module):
    def __init__(self, gen_base, h_sizes=[], out_size=1):
        super(GeneratorAdv, self).__init__()
        self.gen_base = gen_base

        self.n_hidden_layers = len(h_sizes)
        last_base_layer = getattr(self.gen_base, f"base_{self.gen_base.n_layers - 1}")
        prev_layer = last_base_layer
        for i, (in_sz, out_sz) in enumerate(zip([last_base_layer.out_features] + h_sizes[:-1],
                                                h_sizes[1:])):
            setattr(self, f"l_{i}", nn.Linear(in_sz, out_sz))
            prev_layer = getattr(self, f"l_{i}")
            setattr(self, f"elu_{i}", nn.ELU())

            nn.init.xavier_normal_(getattr(self, f"l_{i}").weight)
            getattr(self, f"l_{i}").bias.data.fill_(0.01)

        self.head = nn.Linear(prev_layer.out_features, out_size)
        self.tanh = nn.Tanh()
        # self.sigmoid = nn.Sigmoid()

        nn.init.xavier_normal_(self.head.weight)
        self.head.bias.data.fill_(0.01)

    def forward(self, z):
        x = self.gen_base(z)

        for i in range(self.n_hidden_layers):
            x = getattr(self, f"l_{i}")(x)
            x = getattr(self, f"elu_{i}")(x)
        x = self.head(x)

        return self.tanh(x)
    # return self.sigmoid(x)


if __name__ == "__main__":
    x_size = 4
    z_size = 64
    gen_base = GeneratorBase(z_size=64)
    gen = GeneratorAdv(gen_base, out_size=x_size)
    print(gen)

    # Sample noise from uniform distribution
    z = torch.rand(32, 64).uniform_(-1, 1)

    # Output of generator
    out = gen(z)
# print(out.shape, out.min(), out.max())
