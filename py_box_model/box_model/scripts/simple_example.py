from matplotlib import pyplot as plt

from box_model import box_model


def run_simple_example():
    fourbox_args = dict(
        N=4000, K_v=1e-5, A_GM=1000, M_ek=25e6,
        A_Redi=1000, M_SD=15e6, D_low0=400,
        T_north0=2, T_south0=4, T_low0=17, T_deep0=3,
        S_north0=35, S_south0=36, S_low0=36, S_deep0=34.5,
        Fws=1e6, Fwn=0.05e6, epsilon=1.2e-4
    )
    M_n, M_upw, M_eddy, D_low, T, S, sigma0 = box_model(**fourbox_args)
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

