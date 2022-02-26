import numpy as np
import seawater as sw

# reindex these from 1-based (for Matlab) to 0-based for Python
NORTH_IDX, SOUTH_IDX, LOW_IDX, DEEP_IDX = 0, 1, 2, 3

ACC_GRAVITY = 9.8
D_LYSOCLINE = 3700  # todo: Is this the correct interpretation of this value?
L_X_SOUTH = 2.5e7  # length around the circumpolar region in km (L_x^S)
L_Y_SOUTH = 1e6  # length scale over which the pycnocline shallows in the Southern Ocean in km (L_y_S)
L_X_NORTH = 5e6  # Analogous to L_X_SOUTH but for the Northern Ocean
L_Y_NORTH = L_X_NORTH  # Analogous to L_Y_SOUTH but for the Northern Ocean
SECONDS_PER_YEAR = 365*24*60*60
WATER_PRESSURE = 0  # Used to compute density for various temperature and salinity values
v_T = 100 / SECONDS_PER_YEAR  # air–sea heat transfer velocity of 100 (m/yr); Equation A2b in paper


def box_model(N: int, Kv: float, AI: float, Mek: float, Aredi: float, M_s: float, D0: float, T0s: float, T0n: float,
              T0l: float, T0d: float, S0s: float, S0n: float, S0l: float, S0d: float, Fws: float, Fwn: float,
              epsilon: float,
              area: float = 3.6e14,
              area_low: float = 2e14,
              area_s: float = 1e14,
              area_n: float = 0.6e14,
              Dhigh: float = 100,
              timestep_size_in_years: float = 0.25
              ):
    """
    Run the Four-Box simulation from https://journals.ametsoc.org/view/journals/clim/31/22/jcli-d-18-0388.1.xml
    todo: add ranges and extended ranges
    :param N: Number of days to run the model
    :param Kv: Vertical diffusion coefficient
    :param AI: Interface height diffusion coefficient or Gent-McWilliams coefficient; A_{GM} in the paper
    :param Mek: Ekman flux from the southern ocean
    :param Aredi: Redi coefficient
    :param M_s: antarctic bottom water formation rate; M_{SD} in paper
    :param D0: Initial pycnocline/thermocline depth
    :param T0s: Initial Temperature of the South box
    :param T0n: Initial Temperature of the North box
    :param T0l: Initial Temperature of the Low box
    :param T0d: Initial Temperature of the Deep box
    :param S0s: Initial Salinity of the South box
    :param S0n: Initial Salinity of the North box
    :param S0l: Initial Salinity of the Low box
    :param S0d: Initial Salinity of the Deep box
    :param Fws: Fresh water flux (South)
    :param Fwn: Fresh water flux (North)
    :param epsilon: Resistance parameter
    :param area: Total area of the box model
    :param area_low: Surface area of the low-latitude box (Area_{Low})
    :param area_s: Area of the southern surface area layer box
    :param area_n: Area of the southern surface area layer box
    :param Dhigh: Depth of the northern and southern surface area boxes
    :param timestep_size_in_years: Size of the step taken at each iteration, in years; e.g. 0.25 ~= 3 months
    :return: [M_n M_upw M_eddy Dlow T S sigma0]
        M_n: Northern Hemisphere overturning
        M_upw: Upwelling from the deep ocean
        M_eddy: Advective eddy flux in the southern ocean
        Dlow: Thermocline depth of lower latitudes
        T: Temperature, degrees C
        S: Salinity
        sigma0: Density

    """
    dt = SECONDS_PER_YEAR * timestep_size_in_years  # Note: seconds in 1/4 year? Do we try to account for leap years?

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
    # sigma2 = np.zeros((N + 1, 4))  # todo: Not used? Is this how this should be initialized?

    for j in range(0, N):  # j=1:N, but change to zero indexing
        # Compute density
        sigma0[j, :] = np.real(sw.dens(S[j, :], T[j, :], 0))
        # sigma2[j, :] = sw.dens(S[j, :], T[j, :], 2000)  # todo: Not used?
        M_LS = Aredi * L_X_SOUTH * Dlow[j] / L_Y_SOUTH
        M_LN = Aredi * L_X_NORTH * Dlow[j] / L_Y_NORTH

        if sigma0[j, NORTH_IDX] > sigma0[j, LOW_IDX]:
            gprime = ACC_GRAVITY * (sigma0[j, NORTH_IDX] - sigma0[j, LOW_IDX]) / sigma0[j, NORTH_IDX]  # reduced gravity
            M_n[j] = gprime * Dlow[j] ** 2 / epsilon
            M_upw[j] = Kv * area_low / min(Dlow[j], D_LYSOCLINE - Dlow[j])
            M_eddy[j] = AI * Dlow[j] * L_X_SOUTH / L_Y_SOUTH
            Vdeep = D_LYSOCLINE * area - area_n * Dhigh - area_s * Dhigh - area_low * Dlow[j]
            Vlow = area_low * Dlow[j]
            # Sinitlow = S[j, LOW_IDX] * area_low * Dlow[j]  # todo: Not used?
            dVlow = (Mek - M_eddy[j] - M_n[j] + M_upw[j] - Fws - Fwn) * dt
            dVdeep = -dVlow
            Dlow[j + 1] = Dlow[j] + dVlow / area_low
            dSlow = (Mek * S[j, SOUTH_IDX] - M_eddy[j] * S[j, LOW_IDX] - M_n[j] * S[j, LOW_IDX]
                     + M_upw[j] * S[j, DEEP_IDX] + M_LS * (S[j, SOUTH_IDX] - S[j, LOW_IDX])
                     + M_LN * (S[j, NORTH_IDX] - S[j, LOW_IDX])) * dt
            dSSouth = ((M_eddy[j] + M_LS) * (S[j, LOW_IDX] - S[j, SOUTH_IDX])
                       + (Mek + M_s) * (S[j, DEEP_IDX] - S[j, SOUTH_IDX]) - Fws * S[j, SOUTH_IDX]) * dt
            dSDeep = (M_n[j] * S[j, NORTH_IDX] - (M_upw[j] + Mek + M_s) * S[j, DEEP_IDX]
                      + (M_eddy[j] + M_s) * S[j, SOUTH_IDX] + Fws * S[j, SOUTH_IDX] + Fwn * S[j, NORTH_IDX]) * dt
            dSNorth = ((M_n[j] + M_LN) * (S[j, LOW_IDX] - S[j, NORTH_IDX]) - Fwn * S[j, NORTH_IDX]) * dt
            dTlow = (Mek * T[j, SOUTH_IDX] - M_eddy[j] * T[j, LOW_IDX] - M_n[j] * T[j, LOW_IDX]
                     + M_upw[j] * T[j, DEEP_IDX] + M_LS * (T[j, SOUTH_IDX] - T[j, LOW_IDX])
                     + M_LN * (T[j, NORTH_IDX] - T[j, LOW_IDX])
                     + v_T * area_low * (T0l - T[j, LOW_IDX])) * dt
            dTSouth = ((M_eddy[j] + M_LS) * (T[j, LOW_IDX] - T[j, SOUTH_IDX])
                       + (Mek + M_s) * (T[j, DEEP_IDX] - T[j, SOUTH_IDX])
                       + v_T * area_s * (T0s - T[j, SOUTH_IDX])) * dt
            dTDeep = ((M_n[j] + Fwn) * T[j, NORTH_IDX] - (M_upw[j] + Mek + M_s) * T[j, DEEP_IDX]
                      + (M_eddy[j] + M_s + Fws) * T[j, SOUTH_IDX]) * dt
            dTNorth = ((M_n[j] + M_LN) * (T[j, LOW_IDX] - T[j, NORTH_IDX])
                       + v_T * area_n * (T0n - T[j, NORTH_IDX])) * dt
            S[j + 1, NORTH_IDX] = S[j, NORTH_IDX] + dSNorth / (Dhigh * area_n)
            S[j + 1, SOUTH_IDX] = S[j, SOUTH_IDX] + dSSouth / (Dhigh * area_s)
            S[j + 1, LOW_IDX] = (S[j, LOW_IDX] * Vlow + dSlow) / (Vlow + dVlow)
            S[j + 1, DEEP_IDX] = (S[j, DEEP_IDX] * Vdeep + dSDeep) / (Vdeep + dVdeep)
            T[j + 1, NORTH_IDX] = T[j, NORTH_IDX] + dTNorth / (Dhigh * area_n)
            T[j + 1, SOUTH_IDX] = T[j, SOUTH_IDX] + dTSouth / (Dhigh * area_s)
            T[j + 1, LOW_IDX] = (T[j, LOW_IDX] * Vlow + dTlow) / (Vlow + dVlow)
            T[j + 1, DEEP_IDX] = (T[j, DEEP_IDX] * Vdeep + dTDeep) / (Vdeep + dVdeep)

        elif sigma0[j, NORTH_IDX] <= sigma0[j, LOW_IDX]:
            gprime = ACC_GRAVITY * (sigma0[j, NORTH_IDX] - sigma0[j, LOW_IDX]) / sigma0[j, NORTH_IDX]  # reduced gravity
            M_n[j] = gprime * Dhigh ** 2 / epsilon
            M_upw[j] = Kv * area_low / min(Dlow[j], D_LYSOCLINE - Dlow[j])
            M_eddy[j] = AI * Dlow[j] * L_X_SOUTH / L_Y_SOUTH
            Vdeep = D_LYSOCLINE * area - area_n * Dhigh - area_s * Dhigh - area_low * Dlow[j]
            Vlow = area_low * Dlow[j]
            dVlow = (Mek - M_eddy[j] - M_n[j] + M_upw[j] - Fws - Fwn) * dt
            dVdeep = -dVlow
            Dlow[j + 1] = Dlow[j] + dVlow / area_low
            dSlow = (Mek * S[j, SOUTH_IDX] - M_eddy[j] * S[j, LOW_IDX] - M_n[j] * S[j, NORTH_IDX]
                     + M_upw[j] * S[j, DEEP_IDX] + M_LS * (S[j, SOUTH_IDX] - S[j, LOW_IDX])
                     + M_LN * (S[j, NORTH_IDX] - S[j, LOW_IDX])) * dt
            dSSouth = ((M_eddy[j] + M_LS) * (S[j, LOW_IDX] - S[j, SOUTH_IDX])
                       + Mek * (S[j, DEEP_IDX] - S[j, SOUTH_IDX]) + M_s * (S[j, DEEP_IDX] - S[j, SOUTH_IDX])
                       - Fws * S[j, SOUTH_IDX]) * dt
            dSDeep = (-(M_upw[j] + Mek + M_s - M_n[j]) * S[j, DEEP_IDX]
                      + (M_eddy[j] + M_s + Fws) * S[j, SOUTH_IDX] + Fwn * S[j, NORTH_IDX]) * dt
            dSNorth = (M_LN * (S[j, LOW_IDX] - S[j, NORTH_IDX]) - M_n[j] * (S[j, DEEP_IDX] - S[j, NORTH_IDX])
                       - Fwn * S[j, NORTH_IDX]) * dt
            dTlow = (Mek * T[j, SOUTH_IDX] - M_eddy[j] * T[j, LOW_IDX] - M_n[j] * T[j, NORTH_IDX]
                     + M_upw[j] * T[j, DEEP_IDX] + M_LS * (T[j, SOUTH_IDX] - T[j, LOW_IDX])
                     + M_LN * (T[j, NORTH_IDX] - T[j, LOW_IDX])
                     + v_T * area_low * (T0l - T[j, LOW_IDX])) * dt
            dTSouth = ((M_eddy[j] + M_LS) * (T[j, LOW_IDX] - T[j, SOUTH_IDX])
                       + (Mek + M_s) * (T[j, DEEP_IDX] - T[j, SOUTH_IDX])
                       + v_T * area_s * (T0s - T[j, SOUTH_IDX])) * dt
            dTDeep = (-(M_upw[j] + Mek + M_s - M_n[j]) * T[j, DEEP_IDX]
                      + (M_eddy[j] + M_s) * T[j, SOUTH_IDX]) * dt  # todo: why doesn't this need v_T?
            dTNorth = ((-M_n[j] + M_LN) * (T[j, LOW_IDX] - T[j, NORTH_IDX])
                       + v_T * area_n * (T0n - T[j, NORTH_IDX])) * dt
            S[j + 1, NORTH_IDX] = S[j, NORTH_IDX] + dSNorth / (area_n * Dhigh)
            S[j + 1, SOUTH_IDX] = S[j, SOUTH_IDX] + dSSouth / (area_s * Dhigh)
            S[j + 1, LOW_IDX] = (S[j, LOW_IDX] * Vlow + dSlow) / (Vlow + dVlow)
            S[j + 1, DEEP_IDX] = (S[j, DEEP_IDX] * Vdeep + dSDeep) / (Vdeep + dVdeep)
            T[j + 1, NORTH_IDX] = T[j, NORTH_IDX] + dTNorth / (Dhigh * area_n)
            T[j + 1, SOUTH_IDX] = T[j, SOUTH_IDX] + dTSouth / (Dhigh * area_s)
            T[j + 1, LOW_IDX] = (T[j, LOW_IDX] * Vlow + dTlow) / (Vlow + dVlow)
            T[j + 1, DEEP_IDX] = (T[j, DEEP_IDX] * Vdeep + dTDeep) / (Vdeep + dVdeep)
        else:
            raise ValueError("Unexpected condition: !(sigma0[j, NORTH_IDX] <= sigma0[j, LOW_IDX]) "
                             "and !(sigma0[j, NORTH_IDX] > sigma0[j, LOW_IDX])!")
    return M_n, M_upw, M_eddy, Dlow[:-1], T[:-1], S[:-1], sigma0[:-1]
