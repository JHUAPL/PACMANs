# Copyright 2022, The Johns Hopkins University Applied Physics Laboratory LLC
# All rights reserved.
# Distributed under the terms of the BSD 3-Clause License.

# Approved for public release; distribution is unlimited.
# This material is based upon work supported by the Defense Advanced Research Projects Agency (DARPA) under Agreement
# No. HR00112290032.

import numpy as np
from pybamocs.four_box_model.box_model import box_model, NORTH_IDX, SOUTH_IDX, DEEP_IDX, LOW_IDX
from pybamocs.four_box_model.box_model_args import (
    BoxModelBoxDimensions,
    BoxModelInitConditions,
    BoxModelParameters,
    BoxModelTimeStep,
    BoxModelRandomization,
    BoxModelResult
)
from pybamocs.four_box_model.constants import PARAMS, SAVED_VARS


def combine_dicts(list_of_dicts: list):
    out = {}
    for d in list_of_dicts:
        out.update(d)
    return out


def get_box_model_comparison_values(new_box_result: BoxModelResult, variable_name: str):
    base_box_model_out = box_model(BoxModelBoxDimensions(), BoxModelInitConditions(), BoxModelParameters(),
                                   BoxModelTimeStep(), BoxModelRandomization())
    base_box_model_out_comp_var = base_box_model_out.__getattribute__(variable_name)
    new_box_model_out_comp_var = new_box_result.__getattribute__(variable_name)
    return base_box_model_out_comp_var, new_box_model_out_comp_var


# Domain Specific Language (DSL) functions  ----------------------------------------------------------------------
def ChangeSign(arr: np.ndarray):
    return (arr >= 0).any() and (arr < 0).any()


def FinalValue(arr: np.ndarray):
    return arr[-1]


def SetTo(mapping, param_idx, value):
    mapping[param_idx] = value


def Equal(a, b):
    return a == b


def Define(token):
    """Return a definition of a token... not implemented, but here for reference"""
    return f"Definitions for {token} currently unimplemented"


def AMOC(token):
    """Returns True if the token is an AMOC variable, False otherwise, not fully implemented"""
    global CONCEPTS
    return token in CONCEPTS


def IncreaseBy(mapping, param, value):
    mapping[param] += value


def DecreaseBy(mapping, param, value):
    mapping[param] -= value


def IncreaseOf(new_box_model_res: BoxModelResult, var_name: str):
    # Note: I'm not sure this is the correct interpretation of this function
    base_box_val, new_box_val = get_box_model_comparison_values(new_box_model_res, var_name)
    return np.sum(new_box_val) > np.sum(base_box_val)


def DecreaseOf(new_box_model_res: BoxModelResult, var_name: str):
    # Note: I'm not sure this is the correct interpretation of this function
    base_box_val, new_box_val = get_box_model_comparison_values(new_box_model_res, var_name)
    return np.sum(new_box_val) < np.sum(base_box_val)


BMI_FUNCTIONS = {'SetTo': SetTo, "DecreaseBy": DecreaseBy, "IncreaseBy": IncreaseBy}
BMO_FUNCTIONS = {'ChangeSign': ChangeSign, 'FinalValue': FinalValue, "IncreaseOf": IncreaseOf, "DecreaseOf": DecreaseOf}
OTHER_FUNCTIONS = {"Equal": Equal, "Define": Define, "AMOC": AMOC}
FUNCTIONS = combine_dicts([BMI_FUNCTIONS, BMO_FUNCTIONS, OTHER_FUNCTIONS])
CONCEPT_WORDS = list(FUNCTIONS.keys()) + PARAMS + SAVED_VARS
DEFAULT_MAPPING = combine_dicts([BoxModelParameters().to_dict(),
                                 BoxModelInitConditions().to_dict(),
                                 BoxModelTimeStep().to_dict(),
                                 BoxModelBoxDimensions().to_dict()]
                                )
