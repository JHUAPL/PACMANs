import numpy as np
import seawater as sw


def fourbox_Aredi(N, Kv, AI, Mek, Aredi, M_s, D0, T0s, T0n, T0l, T0d, S0s, S0n, S0l, S0d, Fws, Fwn, epsilon):
    """
    return [M_n M_upw M_eddy Dlow T S sigma0]
    """
    area = 3.6e14
    area_low = 2e14
    area_s = 1e14
    area_n = 0.6e14
    Dhigh = 100
    dt = 365 * 86400 / 4  # Note: seconds in 1/4 year? Do we try to account for leap years?

    # reindex these from 1-based (for Matlab) to 0-based for Python
    inorth = 0
    isouth = 1
    ilow = 2
    ideep = 3

    T = np.zeros((N + 1, 4))  # account for Matlab being able to append to arrays, and having a j+1 in the loop
    S = np.zeros((N + 1, 4))  # account for Matlab being able to append to arrays, and having a j+1 in the loop
    # V = np.zeros((N, 4))  # todo: Not used?
    M_n = np.zeros((N, 1))
    M_upw = np.zeros((N, 1))
    M_eddy = np.zeros((N, 1))
    Dlow = np.zeros((N + 1, 1))  # account for Matlab being able to append to arrays, and having a j+1 in the loop

    # Set initial values in the arrays
    Dlow[0] = D0
    T[0, :] = np.array([T0n, T0s, T0l, T0d])
    S[0, :] = np.array([S0s, S0n, S0l, S0d])

    sigma0 = np.zeros((N + 1, 4))  # Is this how this should be initialized?
    sigma2 = np.zeros((N + 1, 4))  # Is this how this should be initialized?

    for j in range(0, N):  # j=1:N, but change to zero indexing
        # Compute density
        sigma0[j, :] = np.real(sw.dens(S[j, :], T[j, :], 0))
        sigma2[j, :] = sw.dens(S[j, :], T[j, :], 2000)
        M_LS = Aredi * 2.5e7 * Dlow[j] / 1e6
        M_LN = Aredi * 5e6 * Dlow[j] / 1e6

        if sigma0[j, inorth] > sigma0[j, ilow]:
            gprime = 9.8 * (sigma0[j, inorth] - sigma0[j, ilow]) / sigma0[j, inorth]
            M_n[j] = gprime * Dlow[j] ** 2 / epsilon
            M_upw[j] = Kv * area_low / min(Dlow[j], 3700 - Dlow[j])
            M_eddy[j] = AI * Dlow[j] * 2.5e7 / 1e6
            Vdeep = 3700 * area - area_n * Dhigh - area_s * Dhigh - area_low * Dlow[j]
            Vlow = area_low * Dlow[j]
            # Sinitlow = S[j, ilow] * area_low * Dlow[j]  # todo: Not used?
            dVlow = (Mek - M_eddy[j] - M_n[j] + M_upw[j] - Fws - Fwn) * dt
            dVdeep = -dVlow
            Dlow[j + 1] = Dlow[j] + dVlow / area_low
            dSlow = (Mek * S[j, isouth] - M_eddy[j] * S[j, ilow] - M_n[j] * S[j, ilow]
                     + M_upw[j] * S[j, ideep] + M_LS * (S[j, isouth] - S[j, ilow])
                     + M_LN * (S[j, inorth] - S[j, ilow])) * dt
            dSSouth = ((M_eddy[j] + M_LS) * (S[j, ilow] - S[j, isouth])
                       + (Mek + M_s) * (S[j, ideep] - S[j, isouth]) - Fws * S[j, isouth]) * dt
            dSDeep = (M_n[j] * S[j, inorth] - (M_upw[j] + Mek + M_s) * S[j, ideep]
                      + (M_eddy[j] + M_s) * S[j, isouth] + Fws * S[j, isouth] + Fwn * S[j, inorth]) * dt
            dSNorth = ((M_n[j] + M_LN) * (S[j, ilow] - S[j, inorth]) - Fwn * S[j, inorth]) * dt
            dTlow = (Mek * T[j, isouth] - M_eddy[j] * T[j, ilow] - M_n[j] * T[j, ilow]
                     + M_upw[j] * T[j, ideep] + M_LS * (T[j, isouth] - T[j, ilow])
                     + M_LN * (T[j, inorth] - T[j, ilow]) + area_low * 100 * (T0l - T[j, ilow]) / 365 / 86400) * dt
            dTSouth = ((M_eddy[j] + M_LS) * (T[j, ilow] - T[j, isouth])
                       + (Mek + M_s) * (T[j, ideep] - T[j, isouth])
                       + area_s * 100 * (T0s - T[j, isouth]) / 365 / 86400) * dt
            dTDeep = ((M_n[j] + Fwn) * T[j, inorth] - (M_upw[j] + Mek + M_s) * T[j, ideep]
                      + (M_eddy[j] + M_s + Fws) * T[j, isouth]) * dt
            dTNorth = ((M_n[j] + M_LN) * (T[j, ilow] - T[j, inorth])
                       + area_n * 100 * (T0n - T[j, inorth]) / 365 / 86400) * dt
            S[j + 1, inorth] = S[j, inorth] + dSNorth / (Dhigh * area_n)
            S[j + 1, isouth] = S[j, isouth] + dSSouth / (Dhigh * area_s)
            S[j + 1, ilow] = (S[j, ilow] * Vlow + dSlow) / (Vlow + dVlow)
            S[j + 1, ideep] = (S[j, ideep] * Vdeep + dSDeep) / (Vdeep + dVdeep)
            T[j + 1, inorth] = T[j, inorth] + dTNorth / (Dhigh * area_n)
            T[j + 1, isouth] = T[j, isouth] + dTSouth / (Dhigh * area_s)
            T[j + 1, ilow] = (T[j, ilow] * Vlow + dTlow) / (Vlow + dVlow)
            T[j + 1, ideep] = (T[j, ideep] * Vdeep + dTDeep) / (Vdeep + dVdeep)

        elif sigma0[j, inorth] <= sigma0[j, ilow]:
            gprime = 9.8 * (sigma0[j, inorth] - sigma0[j, ilow]) / sigma0[j, inorth]
            M_n[j] = gprime * Dhigh ** 2 / epsilon
            M_upw[j] = Kv * area_low / min(Dlow[j], 3700 - Dlow[j])
            M_eddy[j] = AI * Dlow[j] * 2.5e7 / 1e6
            Vdeep = 3700 * area - area_n * Dhigh - area_s * Dhigh - area_low * Dlow[j]
            Vlow = area_low * Dlow[j]
            dVlow = (Mek - M_eddy[j] - M_n[j] + M_upw[j] - Fws - Fwn) * dt
            dVdeep = -dVlow
            Dlow[j + 1] = Dlow[j] + dVlow / area_low
            dSlow = (Mek * S[j, isouth] - M_eddy[j] * S[j, ilow] - M_n[j] * S[j, inorth]
                     + M_upw[j] * S[j, ideep] + M_LS * (S[j, isouth] - S[j, ilow])
                     + M_LN * (S[j, inorth] - S[j, ilow])) * dt
            dSSouth = ((M_eddy[j] + M_LS) * (S[j, ilow] - S[j, isouth])
                       + Mek * (S[j, ideep] - S[j, isouth]) + M_s * (S[j, ideep] - S[j, isouth])
                       - Fws * S[j, isouth]) * dt
            dSDeep = (-(M_upw[j] + Mek + M_s - M_n[j]) * S[j, ideep]
                      + (M_eddy[j] + M_s + Fws) * S[j, isouth] + Fwn * S[j, inorth]) * dt
            dSNorth = (M_LN * (S[j, ilow] - S[j, inorth]) - M_n[j] * (S[j, ideep] - S[j, inorth])
                       - Fwn * S[j, inorth]) * dt
            dTlow = (Mek * T[j, isouth] - M_eddy[j] * T[j, ilow] - M_n[j] * T[j, inorth]
                     + M_upw[j] * T[j, ideep] + M_LS * (T[j, isouth] - T[j, ilow])
                     + M_LN * (T[j, inorth] - T[j, ilow]) + area_low * 100 * (T0l - T[j, ilow]) / 365 / 86400) * dt
            dTSouth = ((M_eddy[j] + M_LS) * (T[j, ilow] - T[j, isouth])
                       + (Mek + M_s) * (T[j, ideep] - T[j, isouth])
                       + area_s * 100 * (T0s - T[j, isouth]) / 365 / 86400) * dt
            dTDeep = (-(M_upw[j] + Mek + M_s - M_n[j]) * T[j, ideep]
                      + (M_eddy[j] + M_s) * T[j, isouth]) * dt
            dTNorth = ((-M_n[j] + M_LN) * (T[j, ilow] - T[j, inorth])
                       + area_n * 100 * (T0n - T[j, inorth]) / 365 / 86400) * dt
            S[j + 1, inorth] = S[j, inorth] + dSNorth / (area_n * Dhigh)
            S[j + 1, isouth] = S[j, isouth] + dSSouth / (area_s * Dhigh)
            S[j + 1, ilow] = (S[j, ilow] * Vlow + dSlow) / (Vlow + dVlow)
            S[j + 1, ideep] = (S[j, ideep] * Vdeep + dSDeep) / (Vdeep + dVdeep)
            T[j + 1, inorth] = T[j, inorth] + dTNorth / (Dhigh * area_n)
            T[j + 1, isouth] = T[j, isouth] + dTSouth / (Dhigh * area_s)
            T[j + 1, ilow] = (T[j, ilow] * Vlow + dTlow) / (Vlow + dVlow)
            T[j + 1, ideep] = (T[j, ideep] * Vdeep + dTDeep) / (Vdeep + dVdeep)
        else:
            raise ValueError("Unexpected condition: !(sigma0[j, inorth] <= sigma0[j, ilow]) "
                             "and !(sigma0[j, inorth] > sigma0[j, ilow])!")
    return M_n, M_upw, M_eddy, Dlow, T, S, sigma0
