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
SECONDS_PER_YEAR = np.float64(365) * 24 * 60 * 60
WATER_PRESSURE = np.float64(0)  # Used to compute density for various temperature and salinity values
v_T = np.float64(100) / SECONDS_PER_YEAR  # air–sea heat transfer velocity of 100 (m/yr); Equation A2b in paper


def box_model(N: int, K_v: float, A_GM: float, M_ek: float, A_Redi: float, M_SD: float, D_low0: float, T_north0: float,
              T_south0: float, T_low0: float, T_deep0: float, S_north0: float, S_south0: float, S_low0: float,
              S_deep0: float, Fws: float, Fwn: float, epsilon: float, area: float = 3.6e14, area_low: float = 2e14,
              area_s: float = 1e14, area_n: float = 0.6e14, D_high: float = 100, time_step_size_in_years: float = 0.25
              ):
    """
    Run the Four-Box simulation from https://journals.ametsoc.org/view/journals/clim/31/22/jcli-d-18-0388.1.xml
    todo: add ranges and extended ranges
    Box notes: https://jhuapl.app.box.com/folder/156748842221
    :param N: Number of time steps to run the model
    :param K_v: Vertical diffusion coefficient
    :param A_GM: Interface height diffusion coefficient or Gent-McWilliams coefficient; A_{GM} in the paper
    :param M_ek: Ekman flux from the southern ocean
    :param A_Redi: Redi coefficient
    :param M_SD: antarctic bottom water formation rate; M_{SD} in paper
    :param D_low0: Initial pycnocline/thermocline depth
    :param T_north0: Initial Temperature of the North box
    :param T_south0: Initial Temperature of the South box
    :param T_low0: Initial Temperature of the Low box
    :param T_deep0: Initial Temperature of the Deep box
    :param S_north0: Initial Salinity of the North box
    :param S_south0: Initial Salinity of the South box
    :param S_low0: Initial Salinity of the Low box
    :param S_deep0: Initial Salinity of the Deep box
    :param Fws: Fresh water flux (South)
    :param Fwn: Fresh water flux (North)
    :param epsilon: Resistance parameter
    :param area: Total area of the box model
    :param area_low: Surface area of the low-latitude box (Area_{Low})
    :param area_s: Area of the southern surface area layer box
    :param area_n: Area of the southern surface area layer box
    :param D_high: Depth of the northern and southern surface area boxes
    :param time_step_size_in_years: Size of the step taken at each iteration, in years; e.g. 0.25 ~= 3 months
    :return: [M_n M_upw M_eddy D_low T S sigma_0]
        M_n: Northern Hemisphere overturning
        M_upw: Upwelling from the deep ocean
        M_eddy: Advective eddy flux in the southern ocean
        D_low: Thermocline depth of lower latitudes
        T: Temperature, degrees C
        S: Salinity
        sigma_0: Density

    """
    # TODO: Set up early stopping based on negative values for M_n
    # TODO: Add parameterized randomness to simulation

    dt = SECONDS_PER_YEAR * time_step_size_in_years

    T = np.zeros((N + 1, 4), dtype=np.float64)
    S = np.zeros((N + 1, 4), dtype=np.float64)
    M_n = np.zeros((N, 1), dtype=np.float64)
    M_upw = np.zeros((N, 1), dtype=np.float64)
    M_eddy = np.zeros((N, 1), dtype=np.float64)
    D_low = np.zeros((N + 1, 1), dtype=np.float64)

    # Set initial values
    D_low[0] = D_low0
    T[0, :] = np.array([T_north0, T_south0, T_low0, T_deep0])
    S[0, :] = np.array([S_north0, S_south0, S_low0, S_deep0])

    sigma_0 = np.zeros((N + 1, 4))

    for step in range(0, N):
        sigma_0[step, :] = np.real(sw.dens(S[step, :], T[step, :], 0))
        M_LS = A_Redi * L_X_SOUTH * D_low[step] / L_Y_SOUTH
        M_LN = A_Redi * L_X_NORTH * D_low[step] / L_Y_NORTH

        if sigma_0[step, NORTH_IDX] > sigma_0[step, LOW_IDX]:
            gprime = ACC_GRAVITY * (sigma_0[step, NORTH_IDX] - sigma_0[step, LOW_IDX]) / sigma_0[
                step, NORTH_IDX]  # reduced gravity
            M_n[step] = gprime * D_low[step] ** 2 / epsilon
            M_upw[step] = K_v * area_low / min(D_low[step], D_LYSOCLINE - D_low[step])
            M_eddy[step] = A_GM * D_low[step] * L_X_SOUTH / L_Y_SOUTH
            V_deep = D_LYSOCLINE * area - area_n * D_high - area_s * D_high - area_low * D_low[step]
            V_low = area_low * D_low[step]
            dV_low = (M_ek - M_eddy[step] - M_n[step] + M_upw[step] - Fws - Fwn) * dt
            dV_deep = -dV_low
            D_low[step + 1] = D_low[step] + dV_low / area_low
            dS_low = (M_ek * S[step, SOUTH_IDX] - M_eddy[step] * S[step, LOW_IDX] - M_n[step] * S[step, LOW_IDX]
                      + M_upw[step] * S[step, DEEP_IDX] + M_LS * (S[step, SOUTH_IDX] - S[step, LOW_IDX])
                      + M_LN * (S[step, NORTH_IDX] - S[step, LOW_IDX])) * dt
            dS_south = ((M_eddy[step] + M_LS) * (S[step, LOW_IDX] - S[step, SOUTH_IDX])
                        + (M_ek + M_SD) * (S[step, DEEP_IDX] - S[step, SOUTH_IDX]) - Fws * S[step, SOUTH_IDX]) * dt
            dS_deep = (M_n[step] * S[step, NORTH_IDX] - (M_upw[step] + M_ek + M_SD) * S[step, DEEP_IDX]
                       + (M_eddy[step] + M_SD) * S[step, SOUTH_IDX] + Fws * S[step, SOUTH_IDX]
                       + Fwn * S[step, NORTH_IDX]) * dt
            dS_north = ((M_n[step] + M_LN) * (S[step, LOW_IDX] - S[step, NORTH_IDX]) - Fwn * S[step, NORTH_IDX]) * dt
            dT_low = (M_ek * T[step, SOUTH_IDX] - M_eddy[step] * T[step, LOW_IDX] - M_n[step] * T[step, LOW_IDX]
                      + M_upw[step] * T[step, DEEP_IDX] + M_LS * (T[step, SOUTH_IDX] - T[step, LOW_IDX])
                      + M_LN * (T[step, NORTH_IDX] - T[step, LOW_IDX])
                      + v_T * area_low * (T_low0 - T[step, LOW_IDX])) * dt
            dT_south = ((M_eddy[step] + M_LS) * (T[step, LOW_IDX] - T[step, SOUTH_IDX])
                        + (M_ek + M_SD) * (T[step, DEEP_IDX] - T[step, SOUTH_IDX])
                        + v_T * area_s * (T_south0 - T[step, SOUTH_IDX])) * dt
            dT_deep = ((M_n[step] + Fwn) * T[step, NORTH_IDX] - (M_upw[step] + M_ek + M_SD) * T[step, DEEP_IDX]
                       + (M_eddy[step] + M_SD + Fws) * T[step, SOUTH_IDX]) * dt
            dT_north = ((M_n[step] + M_LN) * (T[step, LOW_IDX] - T[step, NORTH_IDX])
                        + v_T * area_n * (T_north0 - T[step, NORTH_IDX])) * dt
            S[step + 1, NORTH_IDX] = S[step, NORTH_IDX] + dS_north / (D_high * area_n)
            S[step + 1, SOUTH_IDX] = S[step, SOUTH_IDX] + dS_south / (D_high * area_s)
            S[step + 1, LOW_IDX] = (S[step, LOW_IDX] * V_low + dS_low) / (V_low + dV_low)
            S[step + 1, DEEP_IDX] = (S[step, DEEP_IDX] * V_deep + dS_deep) / (V_deep + dV_deep)
            T[step + 1, NORTH_IDX] = T[step, NORTH_IDX] + dT_north / (D_high * area_n)
            T[step + 1, SOUTH_IDX] = T[step, SOUTH_IDX] + dT_south / (D_high * area_s)
            T[step + 1, LOW_IDX] = (T[step, LOW_IDX] * V_low + dT_low) / (V_low + dV_low)
            T[step + 1, DEEP_IDX] = (T[step, DEEP_IDX] * V_deep + dT_deep) / (V_deep + dV_deep)

        elif sigma_0[step, NORTH_IDX] <= sigma_0[step, LOW_IDX]:
            gprime = ACC_GRAVITY * (sigma_0[step, NORTH_IDX] - sigma_0[step, LOW_IDX]) / sigma_0[
                step, NORTH_IDX]  # reduced gravity
            M_n[step] = gprime * D_high ** 2 / epsilon
            M_upw[step] = K_v * area_low / min(D_low[step], D_LYSOCLINE - D_low[step])
            M_eddy[step] = A_GM * D_low[step] * L_X_SOUTH / L_Y_SOUTH
            V_deep = D_LYSOCLINE * area - area_n * D_high - area_s * D_high - area_low * D_low[step]
            V_low = area_low * D_low[step]
            dV_low = (M_ek - M_eddy[step] - M_n[step] + M_upw[step] - Fws - Fwn) * dt
            dV_deep = -dV_low
            D_low[step + 1] = D_low[step] + dV_low / area_low
            dS_low = (M_ek * S[step, SOUTH_IDX] - M_eddy[step] * S[step, LOW_IDX] - M_n[step] * S[step, NORTH_IDX]
                      + M_upw[step] * S[step, DEEP_IDX] + M_LS * (S[step, SOUTH_IDX] - S[step, LOW_IDX])
                      + M_LN * (S[step, NORTH_IDX] - S[step, LOW_IDX])) * dt
            dS_south = ((M_eddy[step] + M_LS) * (S[step, LOW_IDX] - S[step, SOUTH_IDX])
                        + M_ek * (S[step, DEEP_IDX] - S[step, SOUTH_IDX]) + M_SD * (
                                    S[step, DEEP_IDX] - S[step, SOUTH_IDX])
                        - Fws * S[step, SOUTH_IDX]) * dt
            dS_deep = (-(M_upw[step] + M_ek + M_SD - M_n[step]) * S[step, DEEP_IDX]
                       + (M_eddy[step] + M_SD + Fws) * S[step, SOUTH_IDX] + Fwn * S[step, NORTH_IDX]) * dt
            dS_north = (M_LN * (S[step, LOW_IDX] - S[step, NORTH_IDX])
                        - M_n[step] * (S[step, DEEP_IDX] - S[step, NORTH_IDX])
                        - Fwn * S[step, NORTH_IDX]) * dt
            dT_low = (M_ek * T[step, SOUTH_IDX] - M_eddy[step] * T[step, LOW_IDX] - M_n[step] * T[step, NORTH_IDX]
                      + M_upw[step] * T[step, DEEP_IDX] + M_LS * (T[step, SOUTH_IDX] - T[step, LOW_IDX])
                      + M_LN * (T[step, NORTH_IDX] - T[step, LOW_IDX])
                      + v_T * area_low * (T_low0 - T[step, LOW_IDX])) * dt
            dT_south = ((M_eddy[step] + M_LS) * (T[step, LOW_IDX] - T[step, SOUTH_IDX])
                        + (M_ek + M_SD) * (T[step, DEEP_IDX] - T[step, SOUTH_IDX])
                        + v_T * area_s * (T_south0 - T[step, SOUTH_IDX])) * dt
            dT_deep = (-(M_upw[step] + M_ek + M_SD - M_n[step]) * T[step, DEEP_IDX]
                       + (M_eddy[step] + M_SD) * T[step, SOUTH_IDX]) * dt  # todo: why doesn't this need v_T?
            dT_north = ((-M_n[step] + M_LN) * (T[step, LOW_IDX] - T[step, NORTH_IDX])
                        + v_T * area_n * (T_north0 - T[step, NORTH_IDX])) * dt
            S[step + 1, NORTH_IDX] = S[step, NORTH_IDX] + dS_north / (area_n * D_high)
            S[step + 1, SOUTH_IDX] = S[step, SOUTH_IDX] + dS_south / (area_s * D_high)
            S[step + 1, LOW_IDX] = (S[step, LOW_IDX] * V_low + dS_low) / (V_low + dV_low)
            S[step + 1, DEEP_IDX] = (S[step, DEEP_IDX] * V_deep + dS_deep) / (V_deep + dV_deep)
            T[step + 1, NORTH_IDX] = T[step, NORTH_IDX] + dT_north / (D_high * area_n)
            T[step + 1, SOUTH_IDX] = T[step, SOUTH_IDX] + dT_south / (D_high * area_s)
            T[step + 1, LOW_IDX] = (T[step, LOW_IDX] * V_low + dT_low) / (V_low + dV_low)
            T[step + 1, DEEP_IDX] = (T[step, DEEP_IDX] * V_deep + dT_deep) / (V_deep + dV_deep)
        else:
            raise ValueError("Unexpected condition: !(sigma_0[j, NORTH_IDX] <= sigma_0[j, LOW_IDX]) "
                             "and !(sigma_0[j, NORTH_IDX] > sigma_0[j, LOW_IDX])!")
    # Remove extra data point where needed and reshape the variables to have the columns be time
    M_n = M_n.reshape((N,))
    M_upw = M_upw.reshape((N,))
    M_eddy = M_eddy.reshape((N,))
    D_low = D_low[:-1].reshape((N,))
    T = T[:-1].transpose()
    S = S[:-1].transpose()
    sigma_0 = sigma_0[:-1].transpose()
    return M_n, M_upw, M_eddy, D_low, T, S, sigma_0
