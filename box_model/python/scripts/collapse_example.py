# Copyright 2022, The Johns Hopkins University Applied Physics Laboratory LLC
# All rights reserved.
# Distributed under the terms of the BSD 3-Clause License.

"""
The primary purpose of this script is to replicate several results originally written in Matlab, verifying that
the Python box model produces the same results.

Each "sim" function represents an experiment over varying parameters of the box model and examining incremental
amounts of fresh water flux in the northern hemisphere. The last time step of the simulation results are plotted,
demonstrating a collapse in the AMOC for certain parameter values.
"""

import numpy as np
from matplotlib import pyplot as plt

from collapse_ex_utils import fba_run_n_steps, fba_run_n_steps_async
from pybamocs.box_model_args import (
    BoxModelBoxDimensions,
    BoxModelInitConditions,
    BoxModelParameters,
    BoxModelTimeStep
)


def sim1(num_procs=12):
    # Various default parameters
    # N=4000, K_v=1e-5, A_GM=1000, D_low0=400, epsilon=1.2e-4, Fws=1e6, T_north0=2, T_south0=4,
    # T_deep0=3, T_low0=17, S_north0=35, S_south0=36, S_deep0=34.5, S_low0=36, M_SD=15e6, A_Redi=1000

    n_steps = 31
    box_dims = BoxModelBoxDimensions()
    init_conditions = BoxModelInitConditions()
    box_params = BoxModelParameters(M_ek=15e6)
    time_step = BoxModelTimeStep()

    box_params.M_ek = 15e6
    out = fba_run_n_steps(n_steps, box_dims, init_conditions, box_params, time_step) if num_procs == 1 \
        else fba_run_n_steps_async(n_steps, box_dims, init_conditions, box_params, time_step, poolsize=num_procs)
    Mnsave15, Musave15, Meddysave15, dsigmasave15, Dlowsave15 = out

    box_params.M_ek = 25e6
    out = fba_run_n_steps(n_steps, box_dims, init_conditions, box_params, time_step) if num_procs == 1 \
        else fba_run_n_steps_async(n_steps, box_dims, init_conditions, box_params, time_step, poolsize=num_procs)
    Mnsave25, Musave25, Meddysave25, dsigmasave25, Dlowsave25 = out

    box_params.M_ek = 35e6
    out = fba_run_n_steps(n_steps, box_dims, init_conditions, box_params, time_step) if num_procs == 1 \
        else fba_run_n_steps_async(n_steps, box_dims, init_conditions, box_params, time_step, poolsize=num_procs)
    Mnsave35, Musave35, Meddysave35, dsigmasave35, Dlowsave35 = out

    # Redo for "off" state
    init_conditions.D_low0 = 100

    box_params.M_ek = 15e6
    out = fba_run_n_steps(n_steps, box_dims, init_conditions, box_params, time_step) if num_procs == 1 \
        else fba_run_n_steps_async(n_steps, box_dims, init_conditions, box_params, time_step, poolsize=num_procs)
    Mnsave15_low, Musave15_low, Meddysave15_low, dsigmasave15_low, Dlowsave15_low = out

    box_params.M_ek = 25e6
    out = fba_run_n_steps(n_steps, box_dims, init_conditions, box_params, time_step) if num_procs == 1 \
        else fba_run_n_steps_async(n_steps, box_dims, init_conditions, box_params, time_step, poolsize=num_procs)
    Mnsave25_low, Musave25_low, Meddysave25_low, dsigmasave25_low, Dlowsave25_low = out

    box_params.M_ek = 35e6
    out = fba_run_n_steps(n_steps, box_dims, init_conditions, box_params, time_step) if num_procs == 1 \
        else fba_run_n_steps_async(n_steps, box_dims, init_conditions, box_params, time_step, poolsize=num_procs)
    Mnsave35_low, Musave35_low, Meddysave35_low, dsigmasave35_low, Dlowsave35_low = out

    plt.figure(figsize=(18, 12))

    Fwflux = np.arange(0, n_steps) * 0.05

    plt.subplot(221)
    plt.plot(Fwflux, Mnsave15 / 1e6, '-+b', label='M_e_k=15 Sv')
    plt.plot(Fwflux, Mnsave25 / 1e6, '-xk', label='M_e_k=25 Sv')
    plt.plot(Fwflux, Mnsave35 / 1e6, '-or', label='M_e_k=35 Sv')
    plt.plot(Fwflux, Mnsave15_low / 1e6, '-+g', label='M_e_k=15 Sv Low')
    plt.plot(Fwflux, Mnsave25_low / 1e6, '-xc', label='M_e_k=25 Sv Low')
    plt.plot(Fwflux, Mnsave35_low / 1e6, '-oy', label='M_e_k=35 Sv Low')
    plt.xlabel('Freshwater flux in Sv')
    plt.ylabel('Overturning in Sv')
    plt.title('a:NH Overturning')
    plt.legend()
    plt.grid()

    plt.subplot(222)
    plt.plot(Fwflux, Meddysave15 / 1e6 - 15, '-+b', label='M_e_k=15 Sv')
    plt.plot(Fwflux, Meddysave25 / 1e6 - 25, '-xk', label='M_e_k=25 Sv')
    plt.plot(Fwflux, Meddysave35 / 1e6 - 35, '-or', label='M_e_k=35 Sv')
    plt.plot(Fwflux, Meddysave15_low / 1e6 - 15, '-+g', label='M_e_k=15 Sv Low')
    plt.plot(Fwflux, Meddysave25_low / 1e6 - 25, '-xc', label='M_e_k=25 Sv Low')
    plt.plot(Fwflux, Meddysave35_low / 1e6 - 35, '-oy', label='M_e_k=35 Sv Low')
    plt.xlabel('Freshwater flux in Sv')
    plt.ylabel('Overturning in Sv')
    plt.title('b:SH Overturning')
    plt.legend()
    plt.grid()

    plt.subplot(223)
    plt.plot(Fwflux, Dlowsave15, '-+b', label='M_e_k=15 Sv')
    plt.plot(Fwflux, Dlowsave25, '-xk', label='M_e_k=25 Sv')
    plt.plot(Fwflux, Dlowsave35, '-or', label='M_e_k=35 Sv')
    plt.plot(Fwflux, Dlowsave15_low, '-+g', label='M_e_k=15 Sv Low')
    plt.plot(Fwflux, Dlowsave25_low, '-xc', label='M_e_k=25 Sv Low')
    plt.plot(Fwflux, Dlowsave35_low, '-oy', label='M_e_k=35 Sv Low')
    plt.xlabel('Freshwater flux in Sv')
    plt.ylabel('Depth in m')
    plt.title('c:Low latitude thermocline depth')
    plt.legend()
    plt.grid()

    plt.subplot(224)
    plt.plot(Fwflux, dsigmasave15, '-+b', label='M_e_k=15 Sv')
    plt.plot(Fwflux, dsigmasave25, '-xk', label='M_e_k=25 Sv')
    plt.plot(Fwflux, dsigmasave35, '-or', label='M_e_k=35 Sv')
    plt.plot(Fwflux, dsigmasave15_low, '-+g', label='M_e_k=15 Sv Low')
    plt.plot(Fwflux, dsigmasave25_low, '-xc', label='M_e_k=25 Sv Low')
    plt.plot(Fwflux, dsigmasave35_low, '-oy', label='M_e_k=35 Sv Low')
    plt.xlabel('Freshwater flux in Sv')
    plt.ylabel('Density in kg/m^3')
    plt.title('d:Density difference N-Low')
    plt.legend()
    plt.grid()

    plt.tight_layout()
    plt.show()


def sim2(num_procs=12):
    # N=8000, K_v=1e-5, A_GM=1000, D_low0=400, epsilon=1.2e-4, Fws=1e6, T_north0=2, T_south0=4, T_deep0=3, T_low0=17,
    # S_north0=35, S_south0=36, S_deep0=34.5, S_low0=36, M_SD=15e6, Mek=25e6)

    n_steps = 31
    box_dims = BoxModelBoxDimensions()
    init_conditions = BoxModelInitConditions()
    box_params = BoxModelParameters()
    time_step = BoxModelTimeStep(n_steps=8000)

    box_params.A_Redi = 500
    out = fba_run_n_steps(n_steps, box_dims, init_conditions, box_params, time_step) if num_procs == 1 \
        else fba_run_n_steps_async(n_steps, box_dims, init_conditions, box_params, time_step, poolsize=num_procs)
    MnsaveA_Redi500, MusaveA_Redi500, MeddysaveA_Redi500, dsigmasaveA_Redi500, DlowsaveA_Redi500 = out

    box_params.A_Redi = 1000
    out = fba_run_n_steps(n_steps, box_dims, init_conditions, box_params, time_step) if num_procs == 1 \
        else fba_run_n_steps_async(n_steps, box_dims, init_conditions, box_params, time_step, poolsize=num_procs)
    MnsaveA_Redi1000, MusaveA_Redi1000, MeddysaveA_Redi1000, dsigmasaveA_Redi1000, DlowsaveA_Redi1000 = out

    box_params.A_Redi = 2000
    out = fba_run_n_steps(n_steps, box_dims, init_conditions, box_params, time_step) if num_procs == 1 \
        else fba_run_n_steps_async(n_steps, box_dims, init_conditions, box_params, time_step, poolsize=num_procs)
    MnsaveA_Redi2000, MusaveA_Redi2000, MeddysaveA_Redi2000, dsigmasaveA_Redi2000, DlowsaveA_Redi2000 = out

    # Map out low manifold
    init_conditions.D_low0 = 100

    box_params.A_Redi = 500
    out = fba_run_n_steps(n_steps, box_dims, init_conditions, box_params, time_step) if num_procs == 1 \
        else fba_run_n_steps_async(n_steps, box_dims, init_conditions, box_params, time_step, poolsize=num_procs)
    MnsaveA_Redi500_low, MusaveA_Redi500_low, MeddysaveA_Redi500_low, dsigmasaveA_Redi500_low, DlowsaveA_Redi500_low = \
        out

    box_params.A_Redi = 1000
    out = fba_run_n_steps(n_steps, box_dims, init_conditions, box_params, time_step) if num_procs == 1 \
        else fba_run_n_steps_async(n_steps, box_dims, init_conditions, box_params, time_step, poolsize=num_procs)
    MnsaveA_Redi1000_low, MusaveA_Redi1000_low, MeddysaveA_Redi1000_low, dsigmasaveA_Redi1000_low, \
        DlowsaveA_Redi1000_low = out

    box_params.A_Redi = 2000
    out = fba_run_n_steps(n_steps, box_dims, init_conditions, box_params, time_step) if num_procs == 1 \
        else fba_run_n_steps_async(n_steps, box_dims, init_conditions, box_params, time_step, poolsize=num_procs)
    MnsaveA_Redi2000_low, MusaveA_Redi2000_low, MeddysaveA_Redi2000_low, dsigmasaveA_Redi2000_low, \
        DlowsaveA_Redi2000_low = out

    plt.figure(figsize=(18, 12))
    Fwflux = np.arange(0, 31) * 0.05

    plt.subplot(221)
    plt.plot(Fwflux, MnsaveA_Redi500 / 1e6, '-+b', label='A_R_e_d_i=500')
    plt.plot(Fwflux, MnsaveA_Redi1000 / 1e6, '-xk', label='A_R_e_d_i=1000')
    plt.plot(Fwflux, MnsaveA_Redi2000 / 1e6, '-or', label='A_R_e_d_i=2000')
    plt.plot(Fwflux, MnsaveA_Redi500_low / 1e6, '-+g', label='A_R_e_d_i=500')
    plt.plot(Fwflux, MnsaveA_Redi1000_low / 1e6, '-xc', label='A_R_e_d_i=1000')
    plt.plot(Fwflux, MnsaveA_Redi2000_low / 1e6, '-oy', label='A_R_e_d_i=2000')
    plt.xlabel('Freshwater flux in Sv')
    plt.ylabel('Overturning in Sv')
    plt.title('a: NH Overturning')
    plt.grid()
    plt.legend()

    plt.subplot(222)
    plt.plot(Fwflux, MeddysaveA_Redi500 / 1e6 - 25, '-+b', label='A_R_e_d_i=500')
    plt.plot(Fwflux, MeddysaveA_Redi1000 / 1e6 - 25, '-xk', label='A_R_e_d_i=1000')
    plt.plot(Fwflux, MeddysaveA_Redi2000 / 1e6 - 25, '-or', label='A_R_e_d_i=2000')
    plt.plot(Fwflux, MeddysaveA_Redi500_low / 1e6 - 25, '-+g', label='A_R_e_d_i=500')
    plt.plot(Fwflux, MeddysaveA_Redi1000_low / 1e6 - 25, '-xc', label='A_R_e_d_i=1000')
    plt.plot(Fwflux, MeddysaveA_Redi2000_low / 1e6 - 25, '-oy', label='A_R_e_d_i=2000')
    plt.xlabel('Freshwater flux in Sv')
    plt.ylabel('Overturning in Sv')
    plt.title('b: SH Overturning')
    plt.grid()
    plt.legend()

    plt.subplot(223)
    plt.plot(Fwflux, DlowsaveA_Redi500, '-+b', label='A_R_e_d_i=500')
    plt.plot(Fwflux, DlowsaveA_Redi1000, '-xk', label='A_R_e_d_i=1000')
    plt.plot(Fwflux, DlowsaveA_Redi2000, '-or', label='A_R_e_d_i=2000')
    plt.plot(Fwflux, DlowsaveA_Redi500_low, '-+g', label='A_R_e_d_i=500')
    plt.plot(Fwflux, DlowsaveA_Redi1000_low, '-xc', label='A_R_e_d_i=1000')
    plt.plot(Fwflux, DlowsaveA_Redi2000_low, '-oy', label='A_R_e_d_i=2000')
    plt.xlabel('Freshwater flux in Sv')
    plt.ylabel('Depth in m')
    plt.title('c: Low latitude thermocline depth')
    plt.grid()
    plt.legend()

    plt.subplot(224)
    plt.plot(Fwflux, dsigmasaveA_Redi500, '-+b', label='A_R_e_d_i=500')
    plt.plot(Fwflux, dsigmasaveA_Redi1000, '-xk', label='A_R_e_d_i=1000')
    plt.plot(Fwflux, dsigmasaveA_Redi2000, '-or', label='A_R_e_d_i=2000')
    plt.plot(Fwflux, dsigmasaveA_Redi500_low, '-+g', label='A_R_e_d_i=500')
    plt.plot(Fwflux, dsigmasaveA_Redi1000_low, '-xc', label='A_R_e_d_i=1000')
    plt.plot(Fwflux, dsigmasaveA_Redi2000_low, '-oy', label='A_R_e_d_i=2000')
    plt.xlabel('Freshwater flux in Sv')
    plt.ylabel('Density in kg/m^3')
    plt.title('d: Density difference N-Low')
    plt.grid()
    plt.legend()
    plt.show()


def sim3(num_procs=12):
    # N=4000, K_v=1e-5, A_GM=1000, D_low0=400, epsilon=1.2e-4, Fws=1e6, T_north0=2, T_south0=4, T_deep0=3, T_low0=17,
    # S_north0=35, S_south0=36, S_deep0=34.5, S_low0=36, M_SD=15e6, Mek=25e6, A_Redi=1000)
    n_steps = 31
    box_dims = BoxModelBoxDimensions()
    init_conditions = BoxModelInitConditions()
    box_params = BoxModelParameters()
    time_step = BoxModelTimeStep()
    epsilon = 1.2e-4

    box_params.epsilon = epsilon / 2.0
    out = fba_run_n_steps(n_steps, box_dims, init_conditions, box_params, time_step) if num_procs == 1 \
        else fba_run_n_steps_async(n_steps, box_dims, init_conditions, box_params, time_step, poolsize=num_procs)
    Mnsaveepsxp5, Musaveepsxp5, Meddysaveepsxp5, dsigmasaveepsxp5, Dlowsaveepsxp5 = out

    box_params.epsilon = epsilon * 2
    out = fba_run_n_steps(n_steps, box_dims, init_conditions, box_params, time_step) if num_procs == 1 \
        else fba_run_n_steps_async(n_steps, box_dims, init_conditions, box_params, time_step, poolsize=num_procs)
    Mnsaveepsx2, Musaveepsx2, Meddysaveepsx2, dsigmasaveepsx2, Dlowsaveepsx2 = out

    # Map out low manifold
    init_conditions.D_low0 = 100

    box_params.epsilon = epsilon / 2.0
    out = fba_run_n_steps(n_steps, box_dims, init_conditions, box_params, time_step) if num_procs == 1 \
        else fba_run_n_steps_async(n_steps, box_dims, init_conditions, box_params, time_step, poolsize=num_procs)
    Mnsaveepsxp5_low, Musaveepsxp5_low, Meddysaveepsxp5_low, dsigmasaveepsxp5_low, Dlowsaveepsxp5_low = out

    box_params.epsilon = epsilon * 2
    out = fba_run_n_steps(n_steps, box_dims, init_conditions, box_params, time_step) if num_procs == 1 \
        else fba_run_n_steps_async(n_steps, box_dims, init_conditions, box_params, time_step, poolsize=num_procs)
    Mnsaveepsx2_low, Musaveepsx2_low, Meddysaveepsx2_low, dsigmasaveepsx2_low, Dlowsaveepsx2_low \
        = out

    # from sim1 and sim2
    # N=4000, K_v=1e-5, A_GM=1000, D_low0=400, epsilon=1.2e-4, Fws=1e6, T_north0=2, T_south0=4, T_deep0=3, T_low0=17,
    # S_north0=35, S_south0=36, S_deep0=34.5, S_low0=36, M_SD=15e6, A_Redi=1000, Mek=25e6)
    init_conditions.D_low0 = 400
    box_params.epsilon = epsilon

    out = fba_run_n_steps(n_steps, box_dims, init_conditions, box_params, time_step) if num_procs == 1 \
        else fba_run_n_steps_async(n_steps, box_dims, init_conditions, box_params, time_step, poolsize=num_procs)
    Mnsave25, Musave25, Meddysave25, dsigmasave25, Dlowsave25 = out

    init_conditions.D_low0 = 100

    out = fba_run_n_steps(n_steps, box_dims, init_conditions, box_params, time_step) if num_procs == 1 \
        else fba_run_n_steps_async(n_steps, box_dims, init_conditions, box_params, time_step, poolsize=num_procs)
    Mnsave25_low, Musave25_low, Meddysave25_low, dsigmasave25_low, Dlowsave25_low = out

    plt.figure(figsize=(18, 12))
    Fwflux = np.arange(0, 31) * 0.05
    plt.subplot(221)
    plt.plot(Fwflux, Mnsaveepsxp5 / 1e6, '-+b', label='epsilon=0.6e-4')
    plt.plot(Fwflux, Mnsave25 / 1e6, '-xk', label='epsilon=1.2e-4')
    plt.plot(Fwflux, Mnsaveepsx2 / 1e6, '-or', label='epsilon=2.4e-4')
    plt.plot(Fwflux, Mnsaveepsxp5_low / 1e6, '-+g', label='epsilon=0.6e-4')
    plt.plot(Fwflux, Mnsave25_low / 1e6, '-xc', label='epsilon=1.2e-4')
    plt.plot(Fwflux, Mnsaveepsx2_low / 1e6, '-oy', label='epsilon=2.4e-4')
    plt.xlabel('Freshwater flux in Sv')
    plt.ylabel('Overturning in Sv')
    plt.title('a: NH Overturning')
    plt.grid()
    plt.legend()

    plt.subplot(222)
    plt.plot(Fwflux, Meddysaveepsxp5 / 1e6 - 25, '-+b', label='epsilon=0.6e-4')
    plt.plot(Fwflux, Meddysave25 / 1e6 - 25, '-xk', label='epsilon=1.2e-4')
    plt.plot(Fwflux, Meddysaveepsx2 / 1e6 - 25, '-or', label='epsilon=2.4e-4')
    plt.plot(Fwflux, Meddysaveepsxp5_low / 1e6 - 25, '-+g', label='epsilon=0.6e-4')
    plt.plot(Fwflux, Meddysave25_low / 1e6 - 25, '-xc', label='epsilon=1.2e-4')
    plt.plot(Fwflux, Meddysaveepsx2_low / 1e6 - 25, '-oy', label='epsilon=2.4e-4')
    plt.xlabel('Freshwater flux in Sv')
    plt.ylabel('Overturning in Sv')
    plt.title('b: SH Overturning')
    plt.grid()
    plt.legend()

    plt.subplot(223)
    plt.plot(Fwflux, Dlowsaveepsxp5, '-+b', label='epsilon=0.6e-4')
    plt.plot(Fwflux, Dlowsave25, '-xk', label='epsilon=1.2e-4')
    plt.plot(Fwflux, Dlowsaveepsx2, '-or', label='epsilon=2.4e-4')
    plt.plot(Fwflux, Dlowsaveepsxp5_low, '-+g', label='epsilon=0.6e-4')
    plt.plot(Fwflux, Dlowsave25_low, '-xc', label='epsilon=1.2e-4')
    plt.plot(Fwflux, Dlowsaveepsx2_low, '-oy', label='epsilon=2.4e-4')
    plt.xlabel('Freshwater flux in Sv')
    plt.ylabel('Depth in m')
    plt.title('c: Low latitude thermocline depth')
    plt.legend()

    plt.subplot(224)
    plt.plot(Fwflux, dsigmasaveepsxp5, '-+b', label='epsilon=0.6e-4')
    plt.plot(Fwflux, dsigmasave25, '-xk', label='epsilon=1.2e-4')
    plt.plot(Fwflux, dsigmasaveepsx2, '-or', label='epsilon=2.4e-4')
    plt.plot(Fwflux, dsigmasaveepsxp5_low, '-+g', label='epsilon=0.6e-4')
    plt.plot(Fwflux, dsigmasave25_low, '-xc', label='epsilon=1.2e-4')
    plt.plot(Fwflux, dsigmasaveepsx2_low, '-oy', label='epsilon=2.4e-4')
    plt.xlabel('Freshwater flux in Sv')
    plt.ylabel('Density in kg/m^3')
    plt.title('d: Density difference N-Low')
    plt.grid()
    plt.legend()
    plt.show()


if __name__ == "__main__":
    sim1(12)
    sim2(12)
    sim3(12)
