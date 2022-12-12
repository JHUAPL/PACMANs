# Copyright 2022, The Johns Hopkins University Applied Physics Laboratory LLC
# All rights reserved.
# Distributed under the terms of the BSD 3-Clause License.

# Approved for public release; distribution is unlimited.
# This material is based upon work supported by the Defense Advanced Research Projects Agency (DARPA) under Agreement
# No. HR00112290032.

import numpy as np

from .constants import PARAMS


class BoxModelBoxDimensions:
    def __init__(self,
                 area: float = 3.6e14,
                 area_low: float = 2e14,
                 area_s: float = 1e14,
                 area_n: float = 0.6e14,
                 D_high: float = 100
                 ):
        """
        :param area: Total area of the box model
        :param area_low: Surface area of the low-latitude box (Area_{Low})
        :param area_s: Area of the southern surface area layer box
        :param area_n: Area of the southern surface area layer box
        :param D_high: Depth of the northern and southern surface area boxes
        """
        self.area = area
        self.area_low = area_low
        self.area_s = area_s
        self.area_n = area_n
        self.D_high = D_high

    def to_dict(self) -> dict:
        return dict(area=self.area, area_low=self.area_low, area_s=self.area_s, area_n=self.area_n, D_high=self.D_high)

    def copy(self):
        return BoxModelBoxDimensions(**self.to_dict())


class BoxModelInitConditions:
    def __init__(self,
                 D_low0: float = 400.,
                 T_north0: float = 2.,
                 T_south0: float = 4.,
                 T_low0: float = 17.,
                 T_deep0: float = 3.,
                 S_north0: float = 35.,
                 S_south0: float = 36.,
                 S_low0: float = 36.,
                 S_deep0: float = 34.5
                 ):
        """
        :param D_low0: Initial pycnocline/thermocline depth
        :param T_north0: Initial Temperature of the North box
        :param T_south0: Initial Temperature of the South box
        :param T_low0: Initial Temperature of the Low box
        :param T_deep0: Initial Temperature of the Deep box
        :param S_north0: Initial Salinity of the North box
        :param S_south0: Initial Salinity of the South box
        :param S_low0: Initial Salinity of the Low box
        :param S_deep0: Initial Salinity of the Deep box
        """
        self.D_low0 = D_low0
        self.T_north0 = T_north0
        self.T_south0 = T_south0
        self.T_low0 = T_low0
        self.T_deep0 = T_deep0
        self.S_north0 = S_north0
        self.S_south0 = S_south0
        self.S_low0 = S_low0
        self.S_deep0 = S_deep0

    def to_dict(self) -> dict:
        return dict(
            D_low0=self.D_low0,
            T_north0=self.T_north0,
            T_south0=self.T_south0,
            T_low0=self.T_low0,
            T_deep0=self.T_deep0,
            S_north0=self.S_north0,
            S_south0=self.S_south0,
            S_low0=self.S_low0,
            S_deep0=self.S_deep0
        )

    def copy(self):
        return BoxModelInitConditions(**self.to_dict())

    def get_T_init_conditions(self) -> tuple:
        return self.T_north0, self.T_south0, self.T_low0, self.T_deep0

    def get_S_init_conditions(self) -> tuple:
        return self.S_north0, self.S_south0, self.S_low0, self.S_deep0


class BoxModelParameters:
    def __init__(self,
                 K_v: float = 1e-5,
                 A_GM: float = 1000.,
                 M_ek: float = 25e6,
                 A_Redi: float = 1000.,
                 M_SD: float = 15e6,
                 Fws: float = 1e6,
                 Fwn: float = 0.05e6,
                 epsilon: float = 1.2e-4
                 ):
        """
        :param K_v: Vertical diffusion coefficient
        :param A_GM: Interface height diffusion coefficient or Gent-McWilliams coefficient; A_{GM} in the paper
        :param M_ek: Ekman flux from the southern ocean
        :param A_Redi: Redi coefficient
        :param M_SD: antarctic bottom water formation rate; M_{SD} in paper
        :param Fws: Fresh water flux (South)
        :param Fwn: Fresh water flux (North)
        :param epsilon: Resistance parameter
        """
        self.K_v = K_v
        self.A_GM = A_GM
        self.M_ek = M_ek
        self.A_Redi = A_Redi
        self.M_SD = M_SD
        self.Fws = Fws
        self.Fwn = Fwn
        self.epsilon = epsilon

    def to_dict(self) -> dict:
        return dict(
            K_v=self.K_v,
            A_GM=self.A_GM,
            M_ek=self.M_ek,
            A_Redi=self.A_Redi,
            M_SD=self.M_SD,
            Fws=self.Fws,
            Fwn=self.Fwn,
            epsilon=self.epsilon
        )

    def copy(self):
        return BoxModelParameters(**self.to_dict())


class BoxModelTimeStep:
    def __init__(self,
                 n_steps: int = 4000,
                 time_step_size_in_years: float = 0.25
                 ):
        """
        :param n_steps: Number of time steps to run the model
        :param time_step_size_in_years:Size of the step taken at each iteration, in years; e.g. 0.25 ~= 3 months
        """
        self.N = n_steps
        self.time_step_size_in_years = time_step_size_in_years

    def to_dict(self) -> dict:
        return dict(
            N=self.N,
            time_step_size_in_years=self.time_step_size_in_years
        )

    def copy(self):
        return BoxModelTimeStep(**self.to_dict())


class BoxModelRandomization:
    def __init__(self, rng_seed: int = 0, noise_amplification: float = 0):
        """
        Creates and holds a Numpy RandomState object initialized with the given rng_seed. Use is as follows:
            normal_sample = randomization_param.sample()  # returns a value drawn from Norm(0, 1)
        Could be further developed to draw from different distributions or with a different mean/variance.
        :param rng_seed: Seed for the random number generator; set to None to simply return 0 always
        :param noise_amplification: How much to amplify the magnitude of the drawn sample. Set to 0 to turn off
            randomness in the six box model. Default is 0 (i.e. always return 0)
        """
        self.rng_seed = rng_seed
        self.noise_amp = noise_amplification
        self._rng = np.random.RandomState(self.rng_seed)

    @property
    def RNG(self):
        return self._rng

    def sample(self) -> float:
        return self._rng.normal() * self.noise_amp

    def to_dict(self) -> dict:
        return dict(rng_seed=self.rng_seed, noise_amplification=self.noise_amp)

    def copy(self):
        return BoxModelRandomization(**self.to_dict())


class BoxModelResult:
    def __init__(self,
                 M_n: np.ndarray,
                 M_upw: np.ndarray,
                 M_eddy: np.ndarray,
                 D_low: np.ndarray,
                 T: np.ndarray,
                 S: np.ndarray,
                 sigma_0: np.ndarray
                 ):
        """
        :param M_n: Northern Hemisphere overturning
        :param M_upw: Upwelling from the deep ocean
        :param M_eddy: Advective eddy flux in the southern ocean
        :param D_low: Thermocline depth of lower latitudes
        :param T: Temperature, degrees C
        :param S: Salinity
        :param sigma_0: Density
        """
        self.M_n = M_n
        self.M_upw = M_upw
        self.M_eddy = M_eddy
        self.D_low = D_low
        self.T = T
        self.S = S
        self.sigma_0 = sigma_0

    def unpack(self) -> tuple:
        return self.M_n, self.M_upw, self.M_eddy, self.D_low, self.T, self.S, self.sigma_0

    def to_dict(self) -> dict:
        return dict(
            M_n=self.M_n,
            M_upw=self.M_upw,
            M_eddy=self.M_eddy,
            D_low=self.D_low,
            T=self.T,
            S=self.S,
            sigma_0=self.sigma_0
        )

    def copy(self):
        return BoxModelResult(**self.to_dict())


def box_args_from_dict(args_dict) -> dict:
    """
    Convert a dictionary of box model parameters into box model arguments. Useful for backwards compatibility of older
        scripts.
    :param args_dict: (dict) Mapping of keys in PARAMS (box model parameters) to corresponding values
    :return: (dict) Dictionary with the box model argument names as keys and BoxModelBoxDimensions,
       BoxModelInitConditions, BoxModelParameters, and BoxModelTimeStep objects as values.
    """
    if set(args_dict.keys()) != set(PARAMS):
        raise ValueError("Missing required values, or extra values, in 'run_parameters': {}"
                         .format(set(PARAMS).symmetric_difference(set(args_dict.keys()))))
    return {
        "box_dimensions": BoxModelBoxDimensions(
            area=args_dict['area'],
            area_low=args_dict['area_low'],
            area_s=args_dict['area_s'],
            area_n=args_dict['area_n'],
            D_high=args_dict['D_high']
        ),
        "init_conditions": BoxModelInitConditions(
            D_low0=args_dict['D_low0'],
            T_north0=args_dict['T_north0'],
            T_south0=args_dict['T_south0'],
            T_low0=args_dict['T_low0'],
            T_deep0=args_dict['T_deep0'],
            S_north0=args_dict['S_north0'],
            S_south0=args_dict['S_south0'],
            S_low0=args_dict['S_low0'],
            S_deep0=args_dict['S_deep0']
        ),
        "box_params": BoxModelParameters(
            K_v=args_dict['K_v'],
            A_GM=args_dict['A_GM'],
            M_ek=args_dict['M_ek'],
            A_Redi=args_dict['A_Redi'],
            M_SD=args_dict['M_SD'],
            Fws=args_dict['Fws'],
            Fwn=args_dict['Fwn'],
            epsilon=args_dict['epsilon']
        ),
        "time_step": BoxModelTimeStep(
            n_steps=args_dict['N'],
            time_step_size_in_years=args_dict['time_step_size_in_years']
        ),
        "randomization": BoxModelRandomization(
            rng_seed=args_dict['rng_seed'],
            noise_amplification=args_dict['noise_amplification'])
    }


def dict_from_box_args(box_dimensions: BoxModelBoxDimensions, init_conditions: BoxModelInitConditions,
                       box_params: BoxModelParameters, time_step: BoxModelTimeStep,
                       randomization: BoxModelRandomization) -> dict:
    """
    Given box model arguments, convert them into a dictionary with box model parameter names as keys and the parameter
        values as the dictionary values. Useful for backwards compatibility of older scripts.
    :param box_dimensions: (BoxModelBoxDimensions) Parameters for the dimensions of the box model
    :param init_conditions: (BoxModelInitConditions) Box model initial conditions
    :param box_params: (BoxModelParameters) Model parameters related to water fluxes
    :param time_step: (BoxModelTimeStep) Time step settings
    :param randomization: (BoxModelRandomization) Random number generation settings
    :return: (dict) Dictionary of box model parameters
    """
    d = box_dimensions.to_dict()
    d.update(init_conditions.to_dict())
    d.update(box_params.to_dict())
    d.update(time_step.to_dict())
    d.update(randomization.to_dict())
    return d
