# Copyright 2022, The Johns Hopkins University Applied Physics Laboratory LLC
# All rights reserved.
# Distributed under the terms of the BSD 3-Clause License.

# Approved for public release; distribution is unlimited.
# This material is based upon work supported by the Defense Advanced Research Projects Agency (DARPA) under Agreement
# No. HR00112290032.

import numpy as np
from itertools import combinations

from ..definitions import DEFAULT_MAPPING

var_equivalencies = {'Fwn': ["the north freshwater flux", "the northern freshwater flux",
                             "the freshwater flux in the north box",
                             "the freshwater flux in the northern box",
                             "the freshwater flux in the north latitude",
                             "the freshwater flux in the northern latitude"],
                     'M_ek': ["the ekman flux"],
                     'D_low0': ["the thermocline depth of lower latitudes", "the lower latitude thermocline depth",
                                "the thermocline depth"],
                     'epsilon': [],
                     'K_v': [],
                     'A_Redi': [],
                     'A_GM': [],
                     'M_SD': [],
                     'T_north0': [],
                     'T_south0': [],
                     'T_low0': [],
                     'T_deep0': [],
                     'S_north0': [],
                     'S_south0': [],
                     'S_low0': [],
                     'S_deep0': [],
                     'Fws': [],
                     'area': [],
                     'area_low': [],
                     'area_s': [],
                     'area_n': [],
                     'D_high': [],
                     'time_step_size_in_years': [],
                     'M_n': ['the overturning in the northern latitudes', 'the overturning in the north latitudes'],
                     'M_eddy': ['the eddy flux']
                     }


def get_perturb_amount(cur_value, rng):
    if rng is None:
        # Allows for questions to be generated without providing an RNG, but takes away reproducabilty
        rng = np.random.RandomState()
    mag = np.log10(cur_value)
    new_value = rng.normal() * 10 ** (mag - 1)
    return new_value


def get_perturbed_value(param, rng):
    if rng is None:
        # Allows for questions to be generated without providing an RNG, but takes away reproducabilty
        rng = np.random.RandomState()
    if param not in DEFAULT_MAPPING:
        return rng.random()
    cur_value = DEFAULT_MAPPING[param]
    new_value = cur_value + get_perturb_amount(cur_value, rng)
    if param in ['N', 'time_step_in_years']:
        new_value = int(new_value)
    return new_value


def set_to_str(param, val):
    return f"SetTo({param}, {val})"


def augment_perturb_vars(perturb_val):
    return [perturb_val] + var_equivalencies[perturb_val]


def question1_gen(rng=None):
    perturb_vars = ['Fwn', 'M_ek', 'D_low0', 'epsilon', 'K_v', 'A_Redi', 'A_GM', 'M_SD', 'T_north0',
                    'T_south0', 'T_low0', 'T_deep0', 'S_north0', 'S_south0', 'S_low0', 'S_deep0',
                    'Fws', 'area', 'area_low', 'area_s', 'area_n', 'D_high', 'time_step_size_in_years',
                    'blue', 'green', 'cylinder', 'cube', 'rubber', 'metal', 'small', 'metallic', 'matte']
    for perturb_var in perturb_vars:
        val = get_perturbed_value(perturb_var, rng)
        n_val = get_perturbed_value("N", rng)
        question = f"What is the value of M_n at time step {n_val} if {perturb_var} is {val}?"
        program = f"FinalValue(box_model(SetTo(N,{n_val}),SetTo({perturb_var},{val}),M_n)"
        yield question, program


def question2_gen(rng=None):
    perturb_vars = ['Fwn', 'M_ek', 'D_low0', 'epsilon', 'K_v', 'A_Redi', 'A_GM', 'M_SD', 'T_north0',
                    'T_south0', 'T_low0', 'T_deep0', 'S_north0', 'S_south0', 'S_low0', 'S_deep0',
                    'Fws', 'area', 'area_low', 'area_s', 'area_n', 'D_high', 'time_step_size_in_years']
    for perturb_var1, perturb_var2 in combinations(perturb_vars, 2):
        val1 = get_perturbed_value(perturb_var1, rng)
        val2 = get_perturbed_value(perturb_var2, rng)
        question = f"If {perturb_var1} is {val1} and {perturb_var2} is {val2}, does the AMOC collapse?"
        program = f"ChangeSign(box_model(SetTo({perturb_var1},{val1}),SetTo({perturb_var2},{val2})),M_n)"
        yield question, program


def question3_gen(rng=None):
    perturb_vars = ['Fwn', 'M_ek', 'D_low0', 'epsilon', 'K_v', 'A_Redi', 'A_GM', 'M_SD',
                    'T_south0', 'T_low0', 'T_deep0', 'S_north0', 'S_south0', 'S_low0', 'S_deep0',
                    'Fws', 'area', 'area_low', 'area_s', 'area_n', 'D_high', 'time_step_size_in_years']
    for perturb_var in perturb_vars:
        val = get_perturbed_value(perturb_var, rng)
        question = f"What is the final value of the AMOC when {perturb_var} is {val}?"
        program = f"FinalValue(box_model(SetTo({perturb_var},{val})),M_n)"
        yield question, program


def question4_gen(rng=None):
    perturb_vars = ['Fwn', 'M_ek', 'D_low0', 'epsilon', 'K_v', 'A_Redi', 'A_GM', 'M_SD',
                    'T_south0', 'T_low0', 'T_deep0', 'S_north0', 'S_south0', 'S_low0', 'S_deep0',
                    'Fws', 'area', 'area_low', 'area_s', 'area_n', 'D_high', 'time_step_size_in_years',
                    'blue', 'red', 'green', 'cylinder', 'cube', 'rubber', 'metal', 'large', 'gray']
    for perturb_var in perturb_vars:
        question = f"What is {perturb_var}?"
        program = f"Define({perturb_var})"
        yield question, program


def question5_gen(rng=None):
    perturb_vars = ['Fwn', 'M_ek', 'D_low0', 'epsilon', 'K_v', 'A_Redi', 'A_GM', 'M_SD', 'T_north0',
                    'T_south0', 'T_low0', 'T_deep0', 'S_north0', 'S_south0', 'S_low0', 'S_deep0',
                    'Fws', 'area', 'area_low', 'area_s', 'area_n', 'D_high', 'time_step_size_in_years',
                    'blue', 'red', 'green', 'cylinder', 'cube', 'rubber', 'metal', 'large', 'gray', 'cyan',
                    'sphere', 'block', 'shiny', 'matte']
    for perturb_var1, perturb_var2 in combinations(perturb_vars, 2):
        question = f"Is {perturb_var1} equal to {perturb_var2}?"
        program = f"Equal({perturb_var1},{perturb_var2})"
        yield question, program


def question6_gen(rng=None):
    perturb_vars = ['Fwn', 'M_ek', 'D_low0', 'epsilon', 'K_v', 'A_Redi', 'A_GM', 'M_SD', 'T_north0',
                    'T_south0', 'T_low0', 'T_deep0', 'S_north0', 'S_south0', 'S_low0', 'S_deep0',
                    'Fws', 'area', 'area_low', 'area_s', 'area_n', 'D_high',
                    'blue', 'green', 'cylinder', 'red', 'rubber', 'purple', 'large', 'metal', 'matte']
    for perturb_var in perturb_vars:
        val = get_perturbed_value(perturb_var, rng)
        question = f"Does {perturb_var} collapse the AMOC at {val}?"
        program = f"ChangeSign(box_model(SetTo({perturb_var},{val})),M_n)"
        yield question, program


def question7_gen(rng=None):
    perturb_vars = ['Fwn', 'M_ek', 'D_low0', 'epsilon', 'K_v', 'A_Redi', 'A_GM', 'M_SD', 'T_north0',
                    'T_south0', 'T_low0', 'T_deep0', 'S_north0', 'S_south0', 'S_low0', 'S_deep0',
                    'Fws', 'area', 'area_low', 'area_s', 'area_n', 'D_high', 'time_step_size_in_years',
                    'blue', 'red', 'green', 'shape', 'cube', 'sphere', 'rubber', 'metal', 'large']
    for perturb_var in perturb_vars:
        question = f"Is {perturb_var} related to the AMOC?"
        program = f"AMOC({perturb_var})"
        yield question, program


# New questions from Jennifer  ------------------------------------------------------------------------

setting_prefixes = ["If I set", "If we set", "By setting"]
increase_prefixes = ["If I increase", "If we increase", "By increasing"]
decrease_prefixes = ["If I decrease", "If we decrease", "By decreasing"]


def question8_gen(rng=None):
    perturb_vars = ['Fwn', 'M_ek', 'D_low0', 'epsilon', 'K_v', 'A_Redi', 'A_GM', 'M_SD', 'T_north0',
                    'T_south0', 'T_low0', 'T_deep0', 'S_north0', 'S_south0', 'S_low0', 'S_deep0',
                    'Fws', 'area', 'area_low', 'area_s', 'area_n', 'D_high', 'time_step_size_in_years']
    for perturb_var1 in perturb_vars:
        for perturb_var2 in perturb_vars:
            for perturb_var3 in perturb_vars:
                if perturb_var1 == perturb_var2 or perturb_var1 == perturb_var3 or perturb_var2 == perturb_var3:
                    continue
                v1 = get_perturbed_value(perturb_var1, rng)
                v2 = get_perturbed_value(perturb_var2, rng)
                v3 = get_perturbed_value(perturb_var3, rng)
                for p1 in augment_perturb_vars(perturb_var1):
                    for p2 in augment_perturb_vars(perturb_var2):
                        for p3 in augment_perturb_vars(perturb_var3):
                            for inc_or_dec in ["increase", "decrease"]:
                                for c in augment_perturb_vars("M_n"):
                                    for pref in setting_prefixes:
                                        question = f"{pref} {p1} to {v1}, {p2} to {v2}, and {p3} to {v3}, " \
                                                   f"will {c} {inc_or_dec}?"
                                        s1 = set_to_str(perturb_var1, v1)
                                        s2 = set_to_str(perturb_var2, v2)
                                        s3 = set_to_str(perturb_var3, v3)
                                        if inc_or_dec == "increase":
                                            program = f"IncreaseOf(box_model({s1},{s2},{s3}),M_n)"
                                        else:
                                            program = f"DecreaseOf(box_model({s1},{s2},{s3}),M_n)"
                                        yield question, program


def question9_gen(rng=None):
    perturb_vars = ['Fwn', 'M_ek', 'D_low0', 'epsilon', 'K_v', 'A_Redi', 'A_GM', 'M_SD', 'T_north0',
                    'T_south0', 'T_low0', 'T_deep0', 'S_north0', 'S_south0', 'S_low0', 'S_deep0',
                    'Fws', 'area', 'area_low', 'area_s', 'area_n', 'D_high', 'time_step_size_in_years']
    for perturb_var in perturb_vars:
        cur_value = DEFAULT_MAPPING[perturb_var]
        v1 = abs(get_perturb_amount(cur_value, rng))  # want to always be positive values
        for p1 in augment_perturb_vars(perturb_var):
            tuples = []
            for dir_of in ["IncreaseOf", "DecreaseOf"]:
                for dir_by in ["IncreaseBy", "DecreaseBy"]:
                    if dir_of == 'IncreaseOf':
                        for p in increase_prefixes:
                            tuples.append((dir_of, "increase", p, dir_by))
                    else:
                        for p in decrease_prefixes:
                            tuples.append((dir_of, "decrease", p, dir_by))
            for dir_of, direction, prefix, dir_by in tuples:
                for c in ["M_n", "M_eddy"]:
                    for c_a in augment_perturb_vars(c):
                        question = f"{prefix} {p1} by {v1}, will {c_a} {direction}?"
                        program = f"{dir_of}(box_model({dir_by}({perturb_var},{v1})),{c})"
                        yield question, program


def question10_gen(rng=None):
    POS_VARS = ['S', 'T', 'sigma_0']
    POS_VAR_MAP = {'S': "salinity", 'T': 'temperature', 'sigma_0': 'density'}
    perturb_vars = ['Fwn', 'M_ek', 'D_low0', 'epsilon', 'K_v', 'A_Redi', 'A_GM', 'M_SD', 'T_north0',
                    'T_south0', 'T_low0', 'T_deep0', 'S_north0', 'S_south0', 'S_low0', 'S_deep0',
                    'Fws', 'area', 'area_low', 'area_s', 'area_n', 'D_high', 'time_step_size_in_years']
    north_suffix = ["in the northern box", "in the north", "in the northern latitudes"]
    south_suffix = ["in the southern box", "in the south", "in the southern latitudes"]
    low_suffix = ["in the low latitude box", "in the low latitudes"]
    deep_suffix = ["in the deep box", "in the deep"]
    for perturb_var in perturb_vars:
        cur_value = DEFAULT_MAPPING[perturb_var]
        v1 = abs(get_perturb_amount(cur_value, rng))  # want to always be positive values
        for p1 in augment_perturb_vars(perturb_var):
            tuples = []
            for out_dir_of in ["IncreaseOf", "DecreaseOf"]:
                direction = "increase" if out_dir_of == "IncreaseOf" else "decrease"
                for param_by in ["IncreaseBy", "DecreaseBy"]:
                    prefixes = increase_prefixes if param_by == 'IncreaseBy' else decrease_prefixes
                    for p in prefixes:
                        tuples.append((out_dir_of, direction, p, param_by))
            for dir_of, direction, prefix, dir_by in tuples:
                for c in POS_VARS:
                    for loc, suffixes in [('north', north_suffix), ('south', south_suffix), ('low', low_suffix),
                                          ('deep', deep_suffix)]:
                        c_loc = c + "_" + loc
                        for s in suffixes:
                            question = f"{prefix} {p1} by {v1}, will {POS_VAR_MAP[c]} {s} {direction}?"
                            program = f"{dir_of}(box_model({dir_by}({perturb_var},{v1})),{c_loc})"
                            yield question, program


ALL_QUESTIONS = [question1_gen, question2_gen, question3_gen, question4_gen, question5_gen, question6_gen,
                 question7_gen, question8_gen, question9_gen, question10_gen]


if __name__ == "__main__":
    my_rng = np.random.RandomState()
    mq10 = question10_gen(my_rng)
    questions = [q for q in mq10]
    print(len(questions))
    my_rng.shuffle(questions)
    for q in questions[:25]:
        print(q)
