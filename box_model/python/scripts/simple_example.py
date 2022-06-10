# Copyright 2022, The Johns Hopkins University Applied Physics Laboratory LLC
# All rights reserved.
# Distributed under the terms of the BSD 3-Clause License.

"""
A basic example of how to generate one run of box model data. Results are plotted for convenience and to facilitate
understanding of the box model outputs.
"""

from matplotlib import pyplot as plt

from pybamocs.box_model import box_model
from pybamocs.box_model_args import (
    BoxModelBoxDimensions,
    BoxModelInitConditions,
    BoxModelParameters,
    BoxModelTimeStep
)


def run_simple_example():
    # See argument objects' definitions for default settings
    box_dims = BoxModelBoxDimensions()
    box_init = BoxModelInitConditions()
    box_params = BoxModelParameters(M_ek=15e6)
    box_time_step = BoxModelTimeStep()
    M_n, M_upw, M_eddy, D_low, T, S, sigma0 = box_model(box_dims, box_init, box_params, box_time_step).unpack()
    plt.plot(M_n, label='M_n')
    plt.plot(M_upw, label='M_upw')
    plt.plot(M_eddy, label='M_eddy')
    plt.plot(D_low, label='Dlow')
    plt.legend()
    plt.show()
    fig, ax = plt.subplots(nrows=2, ncols=2)
    ax[0, 0].plot(T[0], label='T_n')
    ax[0, 1].plot(T[1], label='T_s')
    ax[1, 0].plot(T[2], label='T_l')
    ax[1, 1].plot(T[3], label='T_d')
    ax[0, 0].legend()
    ax[0, 1].legend()
    ax[1, 0].legend()
    ax[1, 1].legend()
    plt.show()
    fig1, ax1 = plt.subplots(nrows=2, ncols=2)
    ax1[0, 0].plot(S[0], label='S_n')
    ax1[0, 1].plot(S[1], label='S_s')
    ax1[1, 0].plot(S[2], label='S_l')
    ax1[1, 1].plot(S[3], label='S_d')
    ax1[0, 0].legend()
    ax1[0, 1].legend()
    ax1[1, 0].legend()
    ax1[1, 1].legend()
    plt.show()
    fig2, ax2 = plt.subplots(nrows=2, ncols=2)
    ax2[0, 0].plot(sigma0[0], label='sigma0_n')
    ax2[0, 1].plot(sigma0[1], label='sigma0_s')
    ax2[1, 0].plot(sigma0[2], label='sigma0_l')
    ax2[1, 1].plot(sigma0[3], label='sigma0_d')
    ax2[0, 0].legend()
    ax2[0, 1].legend()
    ax2[1, 0].legend()
    ax2[1, 1].legend()
    plt.show()


if __name__ == '__main__':
    run_simple_example()

