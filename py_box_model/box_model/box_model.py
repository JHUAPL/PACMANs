import numpy as np
import seawater as sw

# reindex these from 1-based (for Matlab) to 0-based for Python
NORTH_IDX, SOUTH_IDX, LOW_IDX, DEEP_IDX = 0, 1, 2, 3

ACC_GRAVITY = np.float64(9.8)
D_LYSOCLINE = np.float64(3700)  # todo: Is this the correct interpretation of this value?
L_X_SOUTH = np.float64(2.5e7)  # length around the circumpolar region in km (L_x^S)
L_Y_SOUTH = np.float64(1e6)  # length scale over which the pycnocline shallows in the Southern Ocean in km (L_y_S)
L_X_NORTH = np.float64(5e6)  # Analogous to L_X_SOUTH but for the Northern Ocean
L_Y_NORTH = np.float64(1e6)  # Analogous to L_Y_SOUTH but for the Northern Ocean
SECONDS_PER_YEAR = np.float64(365)*24*60*60
WATER_PRESSURE = np.float64(0)  # Used to compute density for various temperature and salinity values
v_T = np.float64(100) / SECONDS_PER_YEAR  # air–sea heat transfer velocity of 100 (m/yr); Equation A2b in paper


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
    Box notes: https://jhuapl.app.box.com/folder/156748842221
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
    # TODO: Set up early stopping based on negative values for M_n

    # Set all values to float64, todo: check if this is needed
    # Kv = np.float64(Kv)
    # AI = np.float64(AI)
    # Mek = np.float64(Mek)
    # Aredi = np.float64(Aredi)
    # M_s = np.float64(M_s)
    # D0 = np.float64(D0)
    # T0s = np.float64(T0s)
    # T0n = np.float64(T0n)
    # T0l = np.float64(T0l)
    # T0d = np.float64(T0d)
    # S0s = np.float64(S0s)
    # S0n = np.float64(S0n)
    # S0l = np.float64(S0l)
    # S0d = np.float64(S0d)
    # Fws = np.float64(Fws)
    # Fwn = np.float64(Fwn)
    # epsilon = np.float64(epsilon)
    # area = np.float64(area)
    # area_low = np.float64(area_low)
    # area_s = np.float64(area_s)
    # area_n = np.float64(area_n)
    # Dhigh = np.float64(Dhigh)
    # timestep_size_in_years = np.float64(timestep_size_in_years)

    dt = SECONDS_PER_YEAR * timestep_size_in_years

    T = np.zeros((N + 1, 4), dtype=np.float64)
    S = np.zeros((N + 1, 4), dtype=np.float64)
    M_n = np.zeros((N, 1), dtype=np.float64)
    M_upw = np.zeros((N, 1), dtype=np.float64)
    M_eddy = np.zeros((N, 1), dtype=np.float64)
    Dlow = np.zeros((N + 1, 1), dtype=np.float64)

    # Set initial values
    Dlow[0] = D0
    T[0, :] = np.array([T0n, T0s, T0l, T0d])
    S[0, :] = np.array([S0n, S0s, S0l, S0d])

    sigma0 = np.zeros((N + 1, 4))

    for step in range(0, N):
        sigma0[step, :] = np.real(sw.dens(S[step, :], T[step, :], 0))
        M_LS = Aredi * L_X_SOUTH * Dlow[step] / L_Y_SOUTH
        M_LN = Aredi * L_X_NORTH * Dlow[step] / L_Y_NORTH

        if sigma0[step, NORTH_IDX] > sigma0[step, LOW_IDX]:
            gprime = ACC_GRAVITY * (sigma0[step, NORTH_IDX] - sigma0[step, LOW_IDX]) / sigma0[step, NORTH_IDX]  # reduced gravity
            M_n[step] = gprime * Dlow[step] ** 2 / epsilon
            M_upw[step] = Kv * area_low / min(Dlow[step], D_LYSOCLINE - Dlow[step])
            M_eddy[step] = AI * Dlow[step] * L_X_SOUTH / L_Y_SOUTH
            Vdeep = D_LYSOCLINE * area - area_n * Dhigh - area_s * Dhigh - area_low * Dlow[step]
            Vlow = area_low * Dlow[step]
            dVlow = (Mek - M_eddy[step] - M_n[step] + M_upw[step] - Fws - Fwn) * dt
            dVdeep = -dVlow
            Dlow[step + 1] = Dlow[step] + dVlow / area_low
            dSlow = (Mek * S[step, SOUTH_IDX] - M_eddy[step] * S[step, LOW_IDX] - M_n[step] * S[step, LOW_IDX]
                     + M_upw[step] * S[step, DEEP_IDX] + M_LS * (S[step, SOUTH_IDX] - S[step, LOW_IDX])
                     + M_LN * (S[step, NORTH_IDX] - S[step, LOW_IDX])) * dt
            dSSouth = ((M_eddy[step] + M_LS) * (S[step, LOW_IDX] - S[step, SOUTH_IDX])
                       + (Mek + M_s) * (S[step, DEEP_IDX] - S[step, SOUTH_IDX]) - Fws * S[step, SOUTH_IDX]) * dt
            dSDeep = (M_n[step] * S[step, NORTH_IDX] - (M_upw[step] + Mek + M_s) * S[step, DEEP_IDX]
                      + (M_eddy[step] + M_s) * S[step, SOUTH_IDX] + Fws * S[step, SOUTH_IDX]
                      + Fwn * S[step, NORTH_IDX]) * dt
            dSNorth = ((M_n[step] + M_LN) * (S[step, LOW_IDX] - S[step, NORTH_IDX]) - Fwn * S[step, NORTH_IDX]) * dt
            dTlow = (Mek * T[step, SOUTH_IDX] - M_eddy[step] * T[step, LOW_IDX] - M_n[step] * T[step, LOW_IDX]
                     + M_upw[step] * T[step, DEEP_IDX] + M_LS * (T[step, SOUTH_IDX] - T[step, LOW_IDX])
                     + M_LN * (T[step, NORTH_IDX] - T[step, LOW_IDX])
                     + v_T * area_low * (T0l - T[step, LOW_IDX])) * dt
            dTSouth = ((M_eddy[step] + M_LS) * (T[step, LOW_IDX] - T[step, SOUTH_IDX])
                       + (Mek + M_s) * (T[step, DEEP_IDX] - T[step, SOUTH_IDX])
                       + v_T * area_s * (T0s - T[step, SOUTH_IDX])) * dt
            dTDeep = ((M_n[step] + Fwn) * T[step, NORTH_IDX] - (M_upw[step] + Mek + M_s) * T[step, DEEP_IDX]
                      + (M_eddy[step] + M_s + Fws) * T[step, SOUTH_IDX]) * dt
            dTNorth = ((M_n[step] + M_LN) * (T[step, LOW_IDX] - T[step, NORTH_IDX])
                       + v_T * area_n * (T0n - T[step, NORTH_IDX])) * dt
            S[step + 1, NORTH_IDX] = S[step, NORTH_IDX] + dSNorth / (Dhigh * area_n)
            S[step + 1, SOUTH_IDX] = S[step, SOUTH_IDX] + dSSouth / (Dhigh * area_s)
            S[step + 1, LOW_IDX] = (S[step, LOW_IDX] * Vlow + dSlow) / (Vlow + dVlow)
            S[step + 1, DEEP_IDX] = (S[step, DEEP_IDX] * Vdeep + dSDeep) / (Vdeep + dVdeep)
            T[step + 1, NORTH_IDX] = T[step, NORTH_IDX] + dTNorth / (Dhigh * area_n)
            T[step + 1, SOUTH_IDX] = T[step, SOUTH_IDX] + dTSouth / (Dhigh * area_s)
            T[step + 1, LOW_IDX] = (T[step, LOW_IDX] * Vlow + dTlow) / (Vlow + dVlow)
            T[step + 1, DEEP_IDX] = (T[step, DEEP_IDX] * Vdeep + dTDeep) / (Vdeep + dVdeep)

        elif sigma0[step, NORTH_IDX] <= sigma0[step, LOW_IDX]:
            gprime = ACC_GRAVITY * (sigma0[step, NORTH_IDX] - sigma0[step, LOW_IDX]) / sigma0[step, NORTH_IDX]  # reduced gravity
            M_n[step] = gprime * Dhigh ** 2 / epsilon
            M_upw[step] = Kv * area_low / min(Dlow[step], D_LYSOCLINE - Dlow[step])
            M_eddy[step] = AI * Dlow[step] * L_X_SOUTH / L_Y_SOUTH
            Vdeep = D_LYSOCLINE * area - area_n * Dhigh - area_s * Dhigh - area_low * Dlow[step]
            Vlow = area_low * Dlow[step]
            dVlow = (Mek - M_eddy[step] - M_n[step] + M_upw[step] - Fws - Fwn) * dt
            dVdeep = -dVlow
            Dlow[step + 1] = Dlow[step] + dVlow / area_low
            dSlow = (Mek * S[step, SOUTH_IDX] - M_eddy[step] * S[step, LOW_IDX] - M_n[step] * S[step, NORTH_IDX]
                     + M_upw[step] * S[step, DEEP_IDX] + M_LS * (S[step, SOUTH_IDX] - S[step, LOW_IDX])
                     + M_LN * (S[step, NORTH_IDX] - S[step, LOW_IDX])) * dt
            dSSouth = ((M_eddy[step] + M_LS) * (S[step, LOW_IDX] - S[step, SOUTH_IDX])
                       + Mek * (S[step, DEEP_IDX] - S[step, SOUTH_IDX]) + M_s * (S[step, DEEP_IDX] - S[step, SOUTH_IDX])
                       - Fws * S[step, SOUTH_IDX]) * dt
            dSDeep = (-(M_upw[step] + Mek + M_s - M_n[step]) * S[step, DEEP_IDX]
                      + (M_eddy[step] + M_s + Fws) * S[step, SOUTH_IDX] + Fwn * S[step, NORTH_IDX]) * dt
            dSNorth = (M_LN * (S[step, LOW_IDX] - S[step, NORTH_IDX])
                       - M_n[step] * (S[step, DEEP_IDX] - S[step, NORTH_IDX])
                       - Fwn * S[step, NORTH_IDX]) * dt
            dTlow = (Mek * T[step, SOUTH_IDX] - M_eddy[step] * T[step, LOW_IDX] - M_n[step] * T[step, NORTH_IDX]
                     + M_upw[step] * T[step, DEEP_IDX] + M_LS * (T[step, SOUTH_IDX] - T[step, LOW_IDX])
                     + M_LN * (T[step, NORTH_IDX] - T[step, LOW_IDX])
                     + v_T * area_low * (T0l - T[step, LOW_IDX])) * dt
            dTSouth = ((M_eddy[step] + M_LS) * (T[step, LOW_IDX] - T[step, SOUTH_IDX])
                       + (Mek + M_s) * (T[step, DEEP_IDX] - T[step, SOUTH_IDX])
                       + v_T * area_s * (T0s - T[step, SOUTH_IDX])) * dt
            dTDeep = (-(M_upw[step] + Mek + M_s - M_n[step]) * T[step, DEEP_IDX]
                      + (M_eddy[step] + M_s) * T[step, SOUTH_IDX]) * dt  # todo: why doesn't this need v_T?
            dTNorth = ((-M_n[step] + M_LN) * (T[step, LOW_IDX] - T[step, NORTH_IDX])
                       + v_T * area_n * (T0n - T[step, NORTH_IDX])) * dt
            S[step + 1, NORTH_IDX] = S[step, NORTH_IDX] + dSNorth / (area_n * Dhigh)
            S[step + 1, SOUTH_IDX] = S[step, SOUTH_IDX] + dSSouth / (area_s * Dhigh)
            S[step + 1, LOW_IDX] = (S[step, LOW_IDX] * Vlow + dSlow) / (Vlow + dVlow)
            S[step + 1, DEEP_IDX] = (S[step, DEEP_IDX] * Vdeep + dSDeep) / (Vdeep + dVdeep)
            T[step + 1, NORTH_IDX] = T[step, NORTH_IDX] + dTNorth / (Dhigh * area_n)
            T[step + 1, SOUTH_IDX] = T[step, SOUTH_IDX] + dTSouth / (Dhigh * area_s)
            T[step + 1, LOW_IDX] = (T[step, LOW_IDX] * Vlow + dTlow) / (Vlow + dVlow)
            T[step + 1, DEEP_IDX] = (T[step, DEEP_IDX] * Vdeep + dTDeep) / (Vdeep + dVdeep)
        else:
            raise ValueError("Unexpected condition: !(sigma0[j, NORTH_IDX] <= sigma0[j, LOW_IDX]) "
                             "and !(sigma0[j, NORTH_IDX] > sigma0[j, LOW_IDX])!")
    return M_n, M_upw, M_eddy, Dlow[:-1], T[:-1], S[:-1], sigma0[:-1]
