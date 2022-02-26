import numpy as np
from matplotlib import pyplot as plt

from script_utils import fba_run_n_steps, fba_run_n_steps_async


def sim1(num_procs=12):
    # todo: docstring
    # Note: consider turning 'fourbox_args' into a config object?
    fourbox_args = dict(N=4000, Kv=1e-5, AI=1000, D0=400, epsilon=1.2e-4, Fws=1e6, T0n=2, T0s=4, T0d=3, T0l=17,
                        S0n=35, S0s=36, S0d=34.5, S0l=36, M_s=15e6, Aredi=1000)
    n_steps = 30

    fourbox_args['Mek'] = 15e6
    out = fba_run_n_steps(n_steps, fourbox_args) if num_procs == 1 \
        else fba_run_n_steps_async(n_steps, fourbox_args, poolsize=num_procs)
    Mnsave15, Musave15, Meddysave15, dsigmasave15, Dlowsave15 = out

    fourbox_args['Mek'] = 25e6
    out = fba_run_n_steps(n_steps, fourbox_args) if num_procs == 1 \
        else fba_run_n_steps_async(n_steps, fourbox_args, poolsize=num_procs)
    Mnsave25, Musave25, Meddysave25, dsigmasave25, Dlowsave25 = out

    fourbox_args['Mek'] = 35e6
    out = fba_run_n_steps(n_steps, fourbox_args) if num_procs == 1 \
        else fba_run_n_steps_async(n_steps, fourbox_args, poolsize=num_procs)
    Mnsave35, Musave35, Meddysave35, dsigmasave35, Dlowsave35 = out

    # % Redo for "off" state
    fourbox_args['D0'] = 100

    fourbox_args['Mek'] = 15e6
    out = fba_run_n_steps(n_steps, fourbox_args) if num_procs == 1 \
        else fba_run_n_steps_async(n_steps, fourbox_args, poolsize=num_procs)
    Mnsave15_low, Musave15_low, Meddysave15_low, dsigmasave15_low, Dlowsave15_low = out

    fourbox_args['Mek'] = 25e6
    out = fba_run_n_steps(n_steps, fourbox_args) if num_procs == 1 \
        else fba_run_n_steps_async(n_steps, fourbox_args, poolsize=num_procs)
    Mnsave25_low, Musave25_low, Meddysave25_low, dsigmasave25_low, Dlowsave25_low = out

    fourbox_args['Mek'] = 35e6
    out = fba_run_n_steps(n_steps, fourbox_args) if num_procs == 1 \
        else fba_run_n_steps_async(n_steps, fourbox_args, poolsize=num_procs)
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

    # plt.legend('M_e_k=15 Sv', 'M_e_k=25 Sv', 'M_e_k=35 Sv', 'Location', 'northeast')
    plt.tight_layout()
    plt.show()


def sim2(num_procs=12):
    # todo: docstring
    fourbox_args = dict(N=8000, Kv=1e-5, AI=1000, D0=400, epsilon=1.2e-4, Fws=1e6, T0n=2, T0s=4, T0d=3, T0l=17,
                        S0n=35, S0s=36, S0d=34.5, S0l=36, M_s=15e6, Mek=25e6)
    n_steps = 30

    fourbox_args['Aredi'] = 500
    out = fba_run_n_steps(n_steps, fourbox_args) if num_procs == 1 \
        else fba_run_n_steps_async(n_steps, fourbox_args, poolsize=num_procs)
    MnsaveAredi500, MusaveAredi500, MeddysaveAredi500, dsigmasaveAredi500, DlowsaveAredi500 = out

    fourbox_args['Aredi'] = 1000
    out = fba_run_n_steps(n_steps, fourbox_args) if num_procs == 1 \
        else fba_run_n_steps_async(n_steps, fourbox_args, poolsize=num_procs)
    MnsaveAredi1000, MusaveAredi1000, MeddysaveAredi1000, dsigmasaveAredi1000, DlowsaveAredi1000 = out

    fourbox_args['Aredi'] = 2000
    out = fba_run_n_steps(n_steps, fourbox_args) if num_procs == 1 \
        else fba_run_n_steps_async(n_steps, fourbox_args, poolsize=num_procs)
    MnsaveAredi2000, MusaveAredi2000, MeddysaveAredi2000, dsigmasaveAredi2000, DlowsaveAredi2000 = out

    # % Map out low manifold
    fourbox_args['D0'] = 100

    fourbox_args['Aredi'] = 500
    out = fba_run_n_steps(n_steps, fourbox_args) if num_procs == 1 \
        else fba_run_n_steps_async(n_steps, fourbox_args, poolsize=num_procs)
    MnsaveAredi500_low, MusaveAredi500_low, MeddysaveAredi500_low, dsigmasaveAredi500_low, DlowsaveAredi500_low = out

    fourbox_args['Aredi'] = 1000
    out = fba_run_n_steps(n_steps, fourbox_args) if num_procs == 1 \
        else fba_run_n_steps_async(n_steps, fourbox_args, poolsize=num_procs)
    MnsaveAredi1000_low, MusaveAredi1000_low, MeddysaveAredi1000_low, dsigmasaveAredi1000_low, DlowsaveAredi1000_low \
        = out

    fourbox_args['Aredi'] = 2000
    out = fba_run_n_steps(n_steps, fourbox_args) if num_procs == 1 \
        else fba_run_n_steps_async(n_steps, fourbox_args, poolsize=num_procs)
    MnsaveAredi2000_low, MusaveAredi2000_low, MeddysaveAredi2000_low, dsigmasaveAredi2000_low, DlowsaveAredi2000_low \
        = out

    plt.figure(figsize=(18, 12))
    Fwflux = np.arange(0, 30) * 0.05

    plt.subplot(221)
    plt.plot(Fwflux, MnsaveAredi500 / 1e6, '-+b', 'A_R_e_d_i=500')
    plt.plot(Fwflux, MnsaveAredi1000 / 1e6, '-xk', 'A_R_e_d_i=1000')
    plt.plot(Fwflux, MnsaveAredi2000 / 1e6, '-or', 'A_R_e_d_i=2000')
    plt.plot(Fwflux, MnsaveAredi500_low / 1e6, '-+g', 'A_R_e_d_i=500')
    plt.plot(Fwflux, MnsaveAredi1000_low / 1e6, '-xc', 'A_R_e_d_i=1000')
    plt.plot(Fwflux, MnsaveAredi2000_low / 1e6, '-oy', 'A_R_e_d_i=2000')
    plt.xlabel('Freshwater flux in Sv')
    plt.ylabel('Overturning in Sv')
    plt.title('a: NH Overturning')
    plt.grid()
    plt.legend()

    plt.subplot(222)
    plt.plot(Fwflux, MeddysaveAredi500 / 1e6 - 25, '-+b', 'A_R_e_d_i=500')
    plt.plot(Fwflux, MeddysaveAredi1000 / 1e6 - 25, '-xk', 'A_R_e_d_i=1000')
    plt.plot(Fwflux, MeddysaveAredi2000 / 1e6 - 25, '-or', 'A_R_e_d_i=2000')
    plt.plot(Fwflux, MeddysaveAredi500_low / 1e6 - 25, '-+g', 'A_R_e_d_i=500')
    plt.plot(Fwflux, MeddysaveAredi1000_low / 1e6 - 25, '-xc', 'A_R_e_d_i=1000')
    plt.plot(Fwflux, MeddysaveAredi2000_low / 1e6 - 25, '-oy', 'A_R_e_d_i=2000')
    plt.xlabel('Freshwater flux in Sv')
    plt.ylabel('Overturning in Sv')
    plt.title('b: SH Overturning')
    plt.grid()
    plt.legend()

    plt.subplot(223)
    plt.plot(Fwflux, DlowsaveAredi500, '-+b', 'A_R_e_d_i=500')
    plt.plot(Fwflux, DlowsaveAredi1000, '-xk', 'A_R_e_d_i=1000')
    plt.plot(Fwflux, DlowsaveAredi2000, '-or', 'A_R_e_d_i=2000')
    plt.plot(Fwflux, DlowsaveAredi500_low, '-+g', 'A_R_e_d_i=500')
    plt.plot(Fwflux, DlowsaveAredi1000_low, '-xc', 'A_R_e_d_i=1000')
    plt.plot(Fwflux, DlowsaveAredi2000_low, '-oy', 'A_R_e_d_i=2000')
    plt.xlabel('Freshwater flux in Sv')
    plt.ylabel('Depth in m')
    plt.title('c: Low latitude thermocline depth')
    plt.grid()
    plt.legend()

    plt.subplot(224)
    plt.plot(Fwflux, dsigmasaveAredi500, '-+b', 'A_R_e_d_i=500')
    plt.plot(Fwflux, dsigmasaveAredi1000, '-xk', 'A_R_e_d_i=1000')
    plt.plot(Fwflux, dsigmasaveAredi2000, '-or', 'A_R_e_d_i=2000')
    plt.plot(Fwflux, dsigmasaveAredi500_low, '-+g', 'A_R_e_d_i=500')
    plt.plot(Fwflux, dsigmasaveAredi1000_low, '-xc', 'A_R_e_d_i=1000')
    plt.plot(Fwflux, dsigmasaveAredi2000_low, '-oy', 'A_R_e_d_i=2000')
    plt.xlabel('Freshwater flux in Sv')
    plt.ylabel('Density in kg/m^3')
    plt.title('d: Density difference N-Low')
    plt.grid()
    plt.legend()
    plt.show()
    # legend('A_R_e_d_i=500', 'A_R_e_d_i=1000', 'A_R_e_d_i=2000', 'Location', 'northeast')


def sim3(num_procs=12):
    fourbox_args = dict(N=4000, Kv=1e-5, AI=1000, D0=400, epsilon=1.2e-4, Fws=1e6, T0n=2, T0s=4, T0d=3, T0l=17,
                        S0n=35, S0s=36, S0d=34.5, S0l=36, M_s=15e6, Mek=25e6, Aredi=1000)
    n_steps = 30
    epsilon = 1.2e-4

    fourbox_args['epsilon'] = epsilon / 2.0
    out = fba_run_n_steps(n_steps, fourbox_args) if num_procs == 1 \
        else fba_run_n_steps_async(n_steps, fourbox_args, poolsize=num_procs)
    Mnsaveepsxp5, Musaveepsxp5, Meddysaveepsxp5, dsigmasaveepsxp5, Dlowsaveepsxp5 = out

    fourbox_args['epsilon'] = epsilon * 2
    out = fba_run_n_steps(n_steps, fourbox_args) if num_procs == 1 \
        else fba_run_n_steps_async(n_steps, fourbox_args, poolsize=num_procs)
    Mnsaveepsx2, Musaveepsx2, Meddysaveepsx2, dsigmasaveepsx2, Dlowsaveepsx2 = out

    # % Map out low manifold
    fourbox_args['D0'] = 100

    fourbox_args['epsilon'] = epsilon / 2.0
    out = fba_run_n_steps(n_steps, fourbox_args) if num_procs == 1 \
        else fba_run_n_steps_async(n_steps, fourbox_args, poolsize=num_procs)
    Mnsaveepsxp5_low, Musaveepsxp5_low, Meddysaveepsxp5_low, dsigmasaveepsxp5_low, Dlowsaveepsxp5_low = out

    fourbox_args['epsilon'] = epsilon * 2
    out = fba_run_n_steps(n_steps, fourbox_args) if num_procs == 1 \
        else fba_run_n_steps_async(n_steps, fourbox_args, poolsize=num_procs)
    Mnsaveepsx2_low, Musaveepsx2_low, Meddysaveepsx2_low, dsigmasaveepsx2_low, Dlowsaveepsx2_low \
        = out

    # from sim1 and sim2
    fourbox_args = dict(N=4000, Kv=1e-5, AI=1000, D0=400, epsilon=1.2e-4, Fws=1e6, T0n=2, T0s=4, T0d=3, T0l=17,
                        S0n=35, S0s=36, S0d=34.5, S0l=36, M_s=15e6, Aredi=1000, Mek=25e6)
    out = fba_run_n_steps(n_steps, fourbox_args) if num_procs == 1 \
        else fba_run_n_steps_async(n_steps, fourbox_args, poolsize=num_procs)
    Mnsave25, Musave25, Meddysave25, dsigmasave25, Dlowsave25 = out
    fourbox_args['D0'] = 100
    out = fba_run_n_steps(n_steps, fourbox_args) if num_procs == 1 \
        else fba_run_n_steps_async(n_steps, fourbox_args, poolsize=num_procs)
    Mnsave25_low, Musave25_low, Meddysave25_low, dsigmasave25_low, Dlowsave25_low = out

    plt.figure(figsize=(18, 12))
    Fwflux = np.arange(0, 30) * 0.05
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
    # '\epsilon=0.6e-4', '\epsilon=1.2e-4', '\epsilon=2.4e-4'

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
    # plt.legend('\epsilon=0.6e-4', '\epsilon=1.2e-4', '\epsilon=2.4e-4')


if __name__ == "__main__":
    sim1(12)
    # sim2(12)
    # sim3(12)

# for k=1:31
# Fwn = (k - 1) * 0.05e6;
# [M_n M_u M_eddy Dlow T S sigma0] = ...
# box_model(N, Kv, 500, Meks, Aredi, M_s, D0, T0s, T0n, T0l, T0d, S0s, S0n, S0l, S0d, Fws, Fwn, epsilon);
# pause(0.1);
# MnsaveAGM500(k) = M_n(N);
# MusaveAGM500(k) = M_u(N);
# MeddysaveAGM500(k) = M_eddy(N);
# dsigmasaveAGM500(k) = sigma0(N, 1) - sigma0(N, 3);
# DlowsaveAGM500(k) = Dlow(N);
# end
#
# for k=1:31
# Fwn = (k - 1) * 0.05e6;
# [M_n M_u M_eddy Dlow T S sigma0] = ...
# box_model(N, Kv, 2000, Meks, Aredi, M_s, D0, T0s, T0n, T0l, T0d, S0s, S0n, S0l, S0d, Fws, Fwn, epsilon);
# pause(0.1);
# MnsaveAGM2000(k) = M_n(N);
# MusaveAGM2000(k) = M_u(N);
# MeddysaveAGM2000(k) = M_eddy(N);
# dsigmasaveAGM2000(k) = sigma0(N, 1) - sigma0(N, 3);
# DlowsaveAGM2000(k) = Dlow(N);
# end
#
# D0 = 100;
#
# for k=1:31
# Fwn = (k - 1) * 0.05e6;
# [M_n M_u M_eddy Dlow T S sigma0] = ...
# box_model(N, Kv, 500, Meks, Aredi, M_s, D0, T0s, T0n, T0l, T0d, S0s, S0n, S0l, S0d, Fws, Fwn, epsilon);
# pause(0.1);
# MnsaveAGM500_low(k) = M_n(N);
# MusaveAGM500_low(k) = M_u(N);
# MeddysaveAGM500_low(k) = M_eddy(N);
# dsigmasaveAGM500_low(k) = sigma0(N, 1) - sigma0(N, 3);
# DlowsaveAGM500_low(k) = Dlow(N);
# end
#
# for k=1:31
# Fwn = (k - 1) * 0.05e6;
# [M_n M_u M_eddy Dlow T S sigma0] = ...
# box_model(N, Kv, 2000, Meks, Aredi, M_s, D0, T0s, T0n, T0l, T0d, S0s, S0n, S0l, S0d, Fws, Fwn, epsilon);
# pause(0.1);
# MnsaveAGM2000_low(k) = M_n(N);
# MusaveAGM2000_low(k) = M_u(N);
# MeddysaveAGM2000_low(k) = M_eddy(N);
# dsigmasaveAGM2000_low(k) = sigma0(N, 1) - sigma0(N, 3);
# DlowsaveAGM2000_low(k) = Dlow(N);
# end
#
# figure(5)
# Fwflux = (0:30) * 0.05;
# subplot(221)
# plot(Fwflux, MnsaveAGM500 / 1e6, '-+b', Fwflux, Mnsave25 / 1e6, '-xk', Fwflux, MnsaveAGM2000 / 1e6, '-or')
# hold
# on
# plot(Fwflux, MnsaveAGM500_low / 1e6, '-+b', Fwflux, Mnsave25_low / 1e6, '-xk', Fwflux, MnsaveAGM2000_low / 1e6, '-or')
# hold
# off
# xlabel('Freshwater flux in Sv')
# ylabel('Overturning in Sv')
# title('a: NH Overturning')
# grid
# on
# subplot(222)
# plot(Fwflux, MeddysaveAGM500 / 1e6 - 25, '-+b', Fwflux, Meddysave25 / 1e6 - 25, '-xk', Fwflux,
#      MeddysaveAGM2000 / 1e6 - 25, '-or')
# hold
# on
# plot(Fwflux, MeddysaveAGM500_low / 1e6 - 25, '-+b', Fwflux, Meddysave25_low / 1e6 - 25, '-xk', Fwflux,
#      MeddysaveAGM2000_low / 1e6 - 25, '-or')
# hold
# off
# xlabel('Freshwater flux in Sv')
# ylabel('Overturning in Sv')
# title('b: SH Overturning')
# grid
# on
# subplot(223)
# plot(Fwflux, DlowsaveAGM500, '-+b', Fwflux, Dlowsave25, '-xk', Fwflux, DlowsaveAGM2000, '-or')
# hold
# on
# plot(Fwflux, DlowsaveAGM500_low, '-+b', Fwflux, Dlowsave25_low, '-xk', Fwflux, DlowsaveAGM2000_low, '-or')
# hold
# off
# xlabel('Freshwater flux in Sv')
# ylabel('Depth in m')
# title('c: Low latitude thermocline depth')
# grid
# on
# subplot(224)
# plot(Fwflux, dsigmasaveAGM500, '-+b', Fwflux, dsigmasave25, '-xk', Fwflux, dsigmasaveAGM2000, '-or')
# hold
# on
# plot(Fwflux, dsigmasaveAGM500_low, '-+b', Fwflux, dsigmasave25_low, '-xk', Fwflux, dsigmasaveAGM2000_low, '-or')
# hold
# off
# xlabel('Freshwater flux in Sv')
# ylabel('Density in kg/m^3')
# title('d: Density difference N-Low')
# legend('A_G_M=500', 'A_G_M=1000', 'A_G_M=2000')
# grid
# on
#
# N = 8000;
# AI = 1000;
# D0 = 400;
# epsilon = 1.2e-4;
# Fws = 1e6;
# T0n = 2;
# T0s = 4;
# T0d = 3;
# T0l = 17;
# Aredi = 1000;
# Agm = 1000;
# S0n = 35;
# S0s = 36;
# S0d = 34.5;
# S0l = 36;
# M_s = 15e6;
# Meks = 25e6;
#
# for k=1:31
# Fwn = (k - 1) * 0.05e6;
# [M_n M_u M_eddy Dlow T S sigma0] = ...
# box_model(N, 0, Agm, Meks, Aredi, M_s, D0, T0s, T0n, T0l, T0d, S0s, S0n, S0l, S0d, Fws, Fwn, epsilon);
# pause(0.1);
# MnsaveKv0(k) = M_n(N);
# MusaveKv0(k) = M_u(N);
# MeddysaveKv0(k) = M_eddy(N);
# dsigmasaveKv0(k) = sigma0(N, 1) - sigma0(N, 3);
# DlowsaveKv0(k) = Dlow(N);
# end
#
# for k=1:31
# Fwn = (k - 1) * 0.05e6;
# [M_n M_u M_eddy Dlow T S sigma0] = ...
# box_model(N, 5e-5, Agm, Meks, Aredi, M_s, D0, T0s, T0n, T0l, T0d, S0s, S0n, S0l, S0d, Fws, Fwn, epsilon);
# pause(0.1);
# MnsaveKv05(k) = M_n(N);
# MusaveKv05(k) = M_u(N);
# MeddysaveKv05(k) = M_eddy(N);
# dsigmasaveKv05(k) = sigma0(N, 1) - sigma0(N, 3);
# DlowsaveKv05(k) = Dlow(N);
# end
#
# D0 = 100;
#
# for k=1:31
# Fwn = (k - 1) * 0.05e6;
# [M_n M_u M_eddy Dlow T S sigma0] = ...
# box_model(N, 0, Agm, Meks, Aredi, M_s, D0, T0s, T0n, T0l, T0d, S0s, S0n, S0l, S0d, Fws, Fwn, epsilon);
# pause(0.1);
# MnsaveKv0_low(k) = M_n(N);
# MusaveKv0_low(k) = M_u(N);
# MeddysaveKv0_low(k) = M_eddy(N);
# dsigmasaveKv0_low(k) = sigma0(N, 1) - sigma0(N, 3);
# DlowsaveKv0_low(k) = Dlow(N);
# end
#
# for k=1:31
# Fwn = (k - 1) * 0.05e6;
# [M_n M_u M_eddy Dlow T S sigma0] = ...
# box_model(N, 5e-5, Agm, Meks, Aredi, M_s, D0, T0s, T0n, T0l, T0d, S0s, S0n, S0l, S0d, Fws, Fwn, epsilon);
# pause(0.1);
# MnsaveKv05_low(k) = M_n(N);
# MusaveKv05_low(k) = M_u(N);
# MeddysaveKv05_low(k) = M_eddy(N);
# dsigmasaveKv05_low(k) = sigma0(N, 1) - sigma0(N, 3);
# DlowsaveKv05_low(k) = Dlow(N);
# end
#
# figure(6)
# Fwflux = (0:30) * 0.05;
# subplot(221)
# plot(Fwflux, MnsaveKv0 / 1e6, '-+b', Fwflux, Mnsave25 / 1e6, '-xk', Fwflux, MnsaveKv05 / 1e6, '-or')
# hold
# on
# plot(Fwflux, MnsaveKv0_low / 1e6, '-+b', Fwflux, Mnsave25_low / 1e6, '-xk', Fwflux, MnsaveKv05_low / 1e6, '-or')
# hold
# off
# xlabel('Freshwater flux in Sv')
# ylabel('Overturning in Sv')
# title('a: NH Overturning')
# grid
# on
# subplot(222)
# plot(Fwflux, MeddysaveKv0 / 1e6 - 25, '-+b', Fwflux, Meddysave25 / 1e6 - 25, '-xk', Fwflux, MeddysaveKv05 / 1e6 - 25,
#      '-or')
# hold
# on
# plot(Fwflux, MeddysaveKv0_low / 1e6 - 25, '-+b', Fwflux, Meddysave25_low / 1e6 - 25, '-xk', Fwflux,
#      MeddysaveKv05_low / 1e6 - 25, '-or')
# hold
# off
# xlabel('Freshwater flux in Sv')
# ylabel('Overturning in Sv')
# title('b: SH Overturning')
# grid
# on
# subplot(223)
# plot(Fwflux, DlowsaveKv0, '-+b', Fwflux, Dlowsave25, '-xk', Fwflux, DlowsaveKv05, '-or')
# hold
# on
# plot(Fwflux, DlowsaveKv0_low, '-+b', Fwflux, Dlowsave25_low, '-xk', Fwflux, DlowsaveKv05_low, '-or')
# hold
# off
# xlabel('Freshwater flux in Sv')
# ylabel('Depth in m')
# title('c: Low latitude thermocline depth')
# grid
# on
# subplot(224)
# plot(Fwflux, dsigmasaveKv0, '-+b', Fwflux, dsigmasave25, '-xk', Fwflux, dsigmasaveKv05, '-or')
# hold
# on
# plot(Fwflux, dsigmasaveKv0_low, '-+b', Fwflux, dsigmasave25_low, '-xk', Fwflux, dsigmasaveKv05_low, '-or')
# hold
# off
# xlabel('Freshwater flux in Sv')
# ylabel('Density in kg/m^3')
# title('d: Density difference N-Low')
# grid
# on
# legend('K_v=0', 'K_v=1e-5', 'K_v=5e-5', 'Location', 'southwest')
#
# figure(7)
# subplot(322)
# plot(dsigmasave15, Mnsave15 / 1e6, '-+b', dsigmasave25, Mnsave25 / 1e6, '-xk', dsigmasave35, Mnsave35 / 1e6, '-or')
# hold
# on
# plot(dsigmasave15_low, Mnsave15_low / 1e6, '-+b', dsigmasave25_low, Mnsave25_low / 1e6, '-xk', dsigmasave35_low,
#      Mnsave35_low / 1e6, '-or')
# hold
# off
# title('b:M_n vs. \Delta\rho, Varying M_e_k')
# ylabel('Overturning in Sv')
# % xlabel('Density difference in kg/m^3')
# axis([-4 3 - 5 40]);
# grid
# on
# h = gca;
# set(h, 'Xtick', (-5:5))
# legend('M_e_k^s=15', 'M_e_k^s=25', 'M_e_k^s=35', 'Location', 'northwest')
#
# subplot(324)
# plot(dsigmasaveAredi500, MnsaveAredi500 / 1e6, '-+b', dsigmasave25, Mnsave25 / 1e6, '-xk', dsigmasaveAredi2000,
#      MnsaveAredi2000 / 1e6, '-or')
# hold
# on
# plot(dsigmasaveAredi500_low, MnsaveAredi500_low / 1e6, '-+b', dsigmasave25_low, Mnsave25_low / 1e6, '-xk',
#      dsigmasaveAredi2000_low, MnsaveAredi2000_low / 1e6, '-or')
# hold
# off
# title('d:M_n vs \Delta\rho, Varying A_R_e_d_i')
# ylabel('Overturning in Sv')
# xlabel('Density difference in kg/m^3')
# axis([-4 3 - 5 40]);
# grid
# on
# h = gca;
# set(h, 'Xtick', (-5:5))
# legend('A_R_e_d_i=500', 'A_R_e_d_i=1000', 'A_R_e_d_i=2000', 'Location', 'northwest')
#
# subplot(325)
# plot(dsigmasaveepsxp5, Mnsaveepsxp5 / 1e6, '-+b', dsigmasave25, Mnsave25 / 1e6, '-xk', dsigmasaveepsx2,
#      Mnsaveepsx2 / 1e6, '-or')
# hold
# on
# plot(dsigmasaveepsxp5_low, Mnsaveepsxp5_low / 1e6, '-+b', dsigmasave25_low, Mnsave25_low / 1e6, '-xk',
#      dsigmasaveepsx2_low, Mnsaveepsx2_low / 1e6, '-or')
# hold
# off
# title('e:M_n vs \Delta\rho, Varying \epsilon')
# ylabel('Overturning in Sv')
# xlabel('Density difference in kg/m^3')
# axis([-4 3 - 5 40]);
# grid
# on
# h = gca;
# set(h, 'Xtick', (-5:5))
# legend('\epsilon=0.6e-4', '\epsilon=1.2e-4', '\epsilon=2.4e-4', 'Location', 'northwest')
#
# subplot(323)
# plot(dsigmasaveAGM500, MnsaveAGM500 / 1e6, '-+b', dsigmasave25, Mnsave25 / 1e6, '-xk', dsigmasaveAGM2000,
#      MnsaveAGM2000 / 1e6, '-or')
# hold
# on
# plot(dsigmasaveAGM500_low, MnsaveAGM500_low / 1e6, '-+b', dsigmasave25_low, Mnsave25_low / 1e6, '-xk',
#      dsigmasaveAGM2000_low, MnsaveAGM2000_low / 1e6, '-or')
# hold
# off
# title('c:M_n vs \Delta\rho, Varying A_G_M')
# axis([-4 3 - 5 40]);
# grid
# on
# legend('A_G_M=500', 'A_G_M=1000', 'A_G_M=2000', 'Location', 'northwest')
# ylabel('Overturning in Sv')
# % xlabel('Density difference in kg/m^3')
# h = gca;
# set(h, 'Xtick', (-5:5))
#
# subplot(321)
# plot(dsigmasaveKv0, MnsaveKv0 / 1e6, '-+b', dsigmasave25, Mnsave25 / 1e6, '-xk', dsigmasaveKv05, MnsaveKv05 / 1e6,
#      '-or')
# hold
# on
# plot(dsigmasaveKv0_low, MnsaveKv0_low / 1e6, '-+b', dsigmasave25_low, Mnsave25_low / 1e6, '-xk', dsigmasaveKv05_low,
#      MnsaveKv05_low / 1e6, '-or')
# hold
# off
# title('a:M_n vs \Delta\rho, Varying K_v')
# axis([-4 3 - 5 40]);
# grid
# on
# legend('K_v=0', 'K_v=1e-5', 'K_v=5e-5', 'Location', 'northwest')
# ylabel('Overturning in Sv')
# % xlabel('Density difference in kg/m^3')
# h = gca;
# set(h, 'Xtick', (-5:5))
#
# figure(8)
# subplot(221)
# plot(Fwflux + 0.075, dsigmasaveKv0, '-+b', Fwflux, dsigmasave25, '-xk', Fwflux - 0.15, dsigmasaveKv05, '-or')
# hold
# on
# plot(Fwflux + 0.075, dsigmasaveKv0_low, '-+b', Fwflux, dsigmasave25_low, '-xk', Fwflux - 0.15, dsigmasaveKv05_low,
#      '-or')
# plot(0.5, 1.5, 'og', 'MarkerSize', 10, 'LineWidth', 3)
# hold
# off
# title('a:Density difference vs. Adjusted F_w^n, Varying K_v')
# axis([-0.25 1.75 - 4 3]);
# grid
# on
# legend('K_v=0', 'K_v=1e-5', 'K_v=5e-5', 'Location', 'southwest')
# ylabel('Density difference in kg/m^3')
# xlabel('Total Freshwater flux-Flux adjustment')
# h = gca;
# set(h, 'Ytick', (-5:5))
#
# subplot(222)
# plot(Fwflux + 0.12, dsigmasave15, '-+b', Fwflux, dsigmasave25, '-xk', Fwflux - 0.1, dsigmasave35, '-or')
# hold
# on
# plot(Fwflux + 0.12, dsigmasave15_low, '-+b', Fwflux, dsigmasave25_low, '-xk', Fwflux - 0.1, dsigmasave35_low, '-or')
# plot(0.5, 1.5, 'og', 'MarkerSize', 10, 'LineWidth', 3)
# hold
# off
# title('b:Density difference vs. Adjusted F_w^n, Varying M_e_k')
# axis([-0.25 1.75 - 4 3]);
# grid
# on
# legend('M_e_k=15 Sv', 'M_e_k=25 Sv', 'M_e_k=35 Sv', 'Location', 'southwest')
# ylabel('Density difference in kg/m^3')
# xlabel('Total Freshwater flux-Flux adjustment')
# h = gca;
# set(h, 'Ytick', (-5:5))
#
# subplot(223)
# plot(Fwflux - 0.1, dsigmasaveAGM500, '-+b', Fwflux, dsigmasave25, '-xk', Fwflux + 0.12, dsigmasaveAGM2000, '-or')
# hold
# on
# plot(Fwflux - 0.1, dsigmasaveAGM500_low, '-+b', Fwflux, dsigmasave25_low, '-xk', Fwflux + 0.12, dsigmasaveAGM2000_low,
#      '-or')
# plot(0.5, 1.5, 'og', 'MarkerSize', 10, 'LineWidth', 3)
# hold
# off
# title('c:Density difference vs. Adjusted F_w^n, Varying A_G_M')
# axis([-0.25 1.75 - 4 3]);
# grid
# on
# legend('A_G_M=500', 'A_G_M=1000', 'A_G_M=2000', 'Location', 'southwest')
# ylabel('Density difference in kg/m^3')
# xlabel('Total Freshwater flux-Flux adjustment')
# h = gca;
# set(h, 'Ytick', (-5:5))
#
# subplot(224)
# plot(Fwflux - 0.08, dsigmasaveepsxp5, '-+b', Fwflux, dsigmasave25, '-xk', Fwflux + 0.07, dsigmasaveepsx2, '-or')
# hold
# on
# plot(Fwflux - 0.08, dsigmasaveepsxp5_low, '-+b', Fwflux, dsigmasave25_low, '-xk', Fwflux + 0.07, dsigmasaveepsx2_low,
#      '-or')
# plot(0.5, 1.5, 'og', 'MarkerSize', 10, 'LineWidth', 3)
# hold
# off
# title('d:Density difference vs. Adjusted F_w^n, Varying \epsilon')
# axis([-0.25 1.75 - 4 3]);
# grid
# on
# legend('\epsilon=0.6e-4', '\epsilon=1.2e-4', '\epsilon=2.4e-4', 'Location', 'southwest')
# ylabel('Density difference in kg/m^3')
# xlabel('Total Freshwater flux-Flux adjustment')
# h = gca;
# set(h, 'Ytick', (-5:5))
