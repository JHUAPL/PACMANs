# Copyright 2022, The Johns Hopkins University Applied Physics Laboratory LLC
# All rights reserved.
# Distributed under the terms of the BSD 3-Clause License.

# Approved for public release; distribution is unlimited.
# This material is based upon work supported by the Defense Advanced Research Projects Agency (DARPA) under Agreement
# No. HR00112290032.

# Variables to save in data generated
SAVED_VARS = ['M_n', 'M_upw', 'M_eddy', 'D_low',
              'S_north', 'S_south', 'S_low', 'S_deep',
              'T_north', 'T_south', 'T_low', 'T_deep',
              'sigma_0_north', 'sigma_0_south', 'sigma_0_low', 'sigma_0_deep'
              ]

# Parameters in the box model
PARAMS = ['N', 'K_v', 'A_GM', 'M_ek', 'A_Redi', 'M_SD', 'D_low0',
          'T_south0', 'T_north0', 'T_low0', 'T_deep0',
          'S_south0', 'S_north0', 'S_low0', 'S_deep0',
          'Fws', 'Fwn', 'epsilon',
          'area', 'area_low', 'area_s', 'area_n',
          'D_high', 'time_step_size_in_years',
          'rng_seed', 'noise_amplification'
          ]
