# Copyright 2022, The Johns Hopkins University Applied Physics Laboratory LLC
# All rights reserved.
# Distributed under the terms of the BSD 3-Clause License.

# Approved for public release; distribution is unlimited.
# This material is based upon work supported by the Defense Advanced Research Projects Agency (DARPA) under Agreement
# No. HR00112290032.

import datetime
import json
from typing import Union

import netCDF4
import numpy as np

from .constants import PARAMS, SAVED_VARS


def store_run(
        data: dict,
        netcdf4_file: str,
        run_id: str,
        when_generated: Union[str, datetime.datetime],
        from_run_id: str,
        run_parameters: dict,
        sign_change: Union[None, list, np.ndarray]
) -> None:
    """
    Store a run of Box model data in a NetCDF file.

    :param data: (dict) Dictionary object mapping the keys in SAVED_VARS, to the corresponding data values
    :param netcdf4_file: (str) Path to the NetCDF file. If one is not present, create a new one at this location
    :param run_id: (str) Identifier for the run
        NOTE: Nothing forces uniqueness of IDs between runs, but NetCDF will likely throw an error if one attempts to
            use the same run_id twice in a single group
    :param when_generated: (str or datetime.datetime) Some indicator of when the data was generated. Can simple set to
        the string "None" to indicate it is a base set of parameters
    :param from_run_id: (str) Run ID from which this run was generated, i.e. the run whose parameters were perturbed to
        generate this one
    :param run_parameters: (dict) Dictionary object mapping the keys in PARAMS, to the corresponding parameter values
    :param sign_change: (None, list, or numpy.ndarray) If there was a change in the sign of the M_n variable, this
        should be a list of indices denoting the time steps where the changes occurred. For example, if the value of
        this variable were
            [59, 491]
        then there is a change in the sign of M_n vector from step 58 to 59, and again from 490 to 491.
    """

    # validate data and params dictionaries
    for k, v in data.items():
        if k not in SAVED_VARS:
            raise ValueError(f"Unrecognized model variable: {k}. Variables are : {SAVED_VARS}")
    if set(data.keys()) != set(SAVED_VARS):
        raise ValueError("Missing required values in 'data': {}".format(set(SAVED_VARS).difference(data.keys())))
    if set(run_parameters.keys()) != set(PARAMS):
        raise ValueError("Missing required values, or extra values, in 'run_parameters': {}"
                         .format(set(PARAMS).symmetric_difference(set(run_parameters.keys()))))
    if sign_change is not None and not isinstance(sign_change, (np.ndarray, list)):
        raise TypeError("Argument 'sign_change' must be a numpy array or list of integers designating the indices in "
                        "the data where changes in sign occurred; or 'None' to indicate no change occurred.")

    try:
        root_group = netCDF4.Dataset(netcdf4_file, 'r+')
    except FileNotFoundError:
        root_group = netCDF4.Dataset(netcdf4_file, 'w')

    run = root_group.createGroup(run_id)
    # create attributes
    run.time_generated = str(when_generated)
    run.from_run = from_run_id
    run.perturbations = []
    run.mode_shift_detected = "False" if sign_change is None else "True"
    run.parameters = json.dumps(run_parameters)
    # create dimensions with unknown length
    if 'time_step' not in run.dimensions.keys():
        run.createDimension('time_step', None)
    # create variables
    variables = {}
    for v in SAVED_VARS:
        # NOTE: Could make files smaller by changing 'f8' to another dtype or using "significant_digits" kwarg
        variables[v] = run.createVariable(v, 'f8', ('time_step',), zlib=True)
    variables['mode_shift_indices'] = run.createVariable('mode_shift_indices', 'f8', ('time_step',), zlib=True)

    variables['M_n'][:] = data['M_n']
    variables['M_upw'][:] = data['M_upw']
    variables['M_eddy'][:] = data['M_eddy']
    variables['D_low'][:] = data['D_low']
    variables['S_north'][:] = data['S_north']
    variables['S_south'][:] = data['S_south']
    variables['S_low'][:] = data['S_low']
    variables['S_deep'][:] = data['S_deep']
    variables['T_north'][:] = data['T_north']
    variables['T_south'][:] = data['T_south']
    variables['T_low'][:] = data['T_low']
    variables['T_deep'][:] = data['T_deep']
    variables['sigma_0_north'][:] = data['sigma_0_north']
    variables['sigma_0_south'][:] = data['sigma_0_south']
    variables['sigma_0_low'][:] = data['sigma_0_low']
    variables['sigma_0_deep'][:] = data['sigma_0_deep']
    variables['mode_shift_indices'] = [] if sign_change is None else sign_change

    # aad pointer to this data to the run it was perturbed from
    if from_run_id != "None":
        root_group[from_run_id].perturbations = np.append(root_group[from_run_id].perturbations, run_id)

    root_group.close()
