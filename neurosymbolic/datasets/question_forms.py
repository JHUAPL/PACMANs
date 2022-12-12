# Copyright 2022, The Johns Hopkins University Applied Physics Laboratory LLC
# All rights reserved.
# Distributed under the terms of the BSD 3-Clause License.

# Approved for public release; distribution is unlimited.
# This material is based upon work supported by the Defense Advanced Research Projects Agency (DARPA) under Agreement
# No. HR00112290032.

import numpy as np
from itertools import combinations

from ..definitions import DEFAULT_MAPPING


def get_perturbed_value(param, rng):
    if param not in DEFAULT_MAPPING:
        return rng.random()
    cur_value = DEFAULT_MAPPING[param]
    mag = np.log10(cur_value)
    new_value = cur_value + rng.normal() * 10 ** (mag - 1)
    if param in ['N', 'time_step_in_years']:
        new_value = int(new_value)
    return new_value


def question_form0(perturb_vars, bmo_func, saved_var, rng):
    token_list = ['if', 'one', 'sets', 'to', 'and', ',', 'will', 'on', '?', 'i', 'you', 'set', 'what', 'is',
                  'the', 'output', 'of', 'be', 'let', 'assume', 'then', 'when']
    return " ".join(rng.choice(token_list, size=rng.randint(1, 4)))


def question_form0_1(perturb_vars, bmo_func, saved_var, rng):
    return f"BOS What is the box output of {saved_var}? EOS"


def question_form0_2(perturb_vars, bmo_func, saved_var, rng):
    return f"BOS Set {perturb_vars[0]} to VALUE. EOS"


def question_form0_3(perturb_vars, bmo_func, saved_var, rng):
    return f"BOS What is {bmo_func} of VALUE? EOS"


def question_form0_4(perturb_vars, bmo_func, saved_var, rng):
    return f"BOS Value of {saved_var} of VALUE? EOS"


def question_form1_1(perturb_vars, bmo_func, saved_var, rng):
    param_entry = "{} to {} "
    mid = "{} to {}".format(perturb_vars[0], get_perturbed_value(perturb_vars[0], rng))
    if len(perturb_vars) > 1:
        mid += "".join(["and " + param_entry.format(pv, get_perturbed_value(pv, rng)) for pv in perturb_vars[1:]])
    mid += ', '
    return "BOS If one sets " + mid + "will {} on {}? EOS".format(bmo_func, saved_var)


def question_form1_2(perturb_vars, bmo_func, saved_var, rng):
    param_entry = "{} to {} "
    mid = "{} to {}".format(perturb_vars[0], get_perturbed_value(perturb_vars[0], rng))
    if len(perturb_vars) > 1:
        mid += "".join(["and " + param_entry.format(pv, get_perturbed_value(pv, rng)) for pv in perturb_vars[1:]])
    mid += ', '
    return "BOS Set " + mid + "will {} on {}? EOS".format(bmo_func, saved_var)


def question_form1_3(perturb_vars, bmo_func, saved_var, rng):
    param_entry = "{} to {} "
    mid = "{} to {}".format(perturb_vars[0], get_perturbed_value(perturb_vars[0], rng))
    if len(perturb_vars) > 1:
        mid += "".join(["and " + param_entry.format(pv, get_perturbed_value(pv, rng)) for pv in perturb_vars[1:]])
    mid += ', '
    return "BOS If you set " + mid + "will {} on {}? EOS".format(bmo_func, saved_var)


def question_form1_4(perturb_vars, bmo_func, saved_var, rng):
    param_entry = "{} to {} "
    mid = "{} to {}".format(perturb_vars[0], get_perturbed_value(perturb_vars[0], rng))
    if len(perturb_vars) > 1:
        mid += "".join(["and " + param_entry.format(pv, get_perturbed_value(pv, rng)) for pv in perturb_vars[1:]])
    mid += ', '
    return "BOS If I set " + mid + "will {} on {}? EOS".format(bmo_func, saved_var)


def question_form2_1(perturb_vars, bmo_func, saved_var, rng):
    param_entry = "{} is {} "
    mid = "{} is {}".format(perturb_vars[0], get_perturbed_value(perturb_vars[0], rng))
    if len(perturb_vars) > 1:
        mid += "".join(["and " + param_entry.format(pv, get_perturbed_value(pv, rng)) for pv in perturb_vars[1:]])
    mid += ', '
    return "BOS When " + mid + "what is the output of {} of {}? EOS".format(bmo_func, saved_var)


def question_form2_2(perturb_vars, bmo_func, saved_var, rng):
    param_entry = "{} is {} "
    mid = "{} is {}".format(perturb_vars[0], get_perturbed_value(perturb_vars[0], rng))
    if len(perturb_vars) > 1:
        mid += "".join(["and " + param_entry.format(pv) for pv in perturb_vars[1:]])
    mid += ', '
    return "BOS Assume that " + mid + "what is the output of {} of {}? EOS".format(bmo_func, saved_var)


def question_form2_3(perturb_vars, bmo_func, saved_var, rng):
    param_entry = "{} is {} "
    mid = "{} is {}".format(perturb_vars[0], get_perturbed_value(perturb_vars[0], rng))
    if len(perturb_vars) > 1:
        mid += "".join(["and " + param_entry.format(pv) for pv in perturb_vars[1:]])
    mid += ', '
    return "BOS When " + mid + "what is the output of {} of {} EOS?".format(bmo_func, saved_var)


def question_form2_4(perturb_vars, bmo_func, saved_var, rng):
    # "Given that param is VALUE (and param is VALUE...), what is the output of func on BMO?"
    param_entry = "{} is {} "
    mid = "{} is {}".format(perturb_vars[0], get_perturbed_value(perturb_vars[0], rng))
    if len(perturb_vars) > 1:
        mid += "".join(["and " + param_entry.format(pv) for pv in perturb_vars[1:]])
    mid += ', '
    return "BOS Given that " + mid + "what is the output of {} of {} EOS?".format(bmo_func, saved_var)


def question_form3_1(perturb_vars, bmo_func, saved_var, rng):
    # "Let BMI be VALUE (, BMI be VALUE...), then what is func of BMO?"
    param_entry = "{} be {}, "
    mid = "{} be {}, ".format(perturb_vars[0], get_perturbed_value(perturb_vars[0], rng))
    if len(perturb_vars) > 1:
        mid += "".join([param_entry.format(pv, get_perturbed_value(perturb_vars[0], rng)) for pv in perturb_vars[1:]])
    return "BOS Let " + mid + "then what is {} of {}? EOS".format(bmo_func, saved_var)


def question_form3_2(perturb_vars, bmo_func, saved_var, rng):
    # "Let BMI be VALUE (, BMI be VALUE...), then what is func of BMO?"
    param_entry = "{} be {}, "
    mid = "{} be {}, ".format(perturb_vars[0], get_perturbed_value(perturb_vars[0], rng))
    if len(perturb_vars) > 1:
        mid += "".join([param_entry.format(pv, get_perturbed_value(perturb_vars[0], rng)) for pv in perturb_vars[1:]])
    return "BOS Let " + mid + "will {} on {}? EOS".format(bmo_func, saved_var)


def question_form3_3(perturb_vars, bmo_func, saved_var, rng):
    # "Let BMI be VALUE (, BMI be VALUE...), then what is func of BMO?"
    param_entry = "{} be {}, "
    mid = "{} be {}, ".format(perturb_vars[0], get_perturbed_value(perturb_vars[0], rng))
    if len(perturb_vars) > 1:
        mid += "".join([param_entry.format(pv, get_perturbed_value(perturb_vars[0], rng)) for pv in perturb_vars[1:]])
    return "BOS Let " + mid + "what is the output of {} of {} EOS?".format(bmo_func, saved_var)


ALL_QUESTION_FUNCS = [question_form0, question_form0_1, question_form1_1, question_form1_2, question_form1_3,
                      question_form1_4, question_form2_1, question_form2_2, question_form2_3, question_form2_4,
                      question_form3_1, question_form3_2, question_form3_3]


def mini_question1_gen(rng):
    perturb_vars = ['Fwn', 'M_ek', 'D_low0', 'epsilon', 'K_v', 'A_Redi', 'A_GM', 'M_SD', 'T_north0',
                    'T_south0', 'T_low0', 'T_deep0', 'S_north0', 'S_south0', 'S_low0', 'S_deep0',
                    'Fws', 'area', 'area_low', 'area_s', 'area_n', 'D_high', 'time_step_size_in_years',
                    'blue', 'green', 'cylinder', 'red', 'rubber', 'purple', 'large', 'metal', 'matte']
    for perturb_var in perturb_vars:
        val = get_perturbed_value(perturb_var, rng)
        question = f"Is there a collapse when {perturb_var} is {val}?"
        program = f"ChangeSign(box_model(SetTo({perturb_var},{val})),M_n)"
        yield question, program


def mini_question2_gen(rng):
    perturb_vars = ['Fwn', 'M_ek', 'D_low0', 'epsilon', 'K_v', 'A_Redi', 'A_GM', 'M_SD', 'T_north0',
                    'T_south0', 'T_low0', 'T_deep0', 'S_north0', 'S_south0', 'S_low0', 'S_deep0',
                    'Fws', 'area', 'area_low', 'area_s', 'area_n', 'D_high', 'time_step_size_in_years'
                    'blue', 'green', 'cylinder', 'cube', 'rubber', 'metal', 'small', 'metallic', 'matte']
    for perturb_var in perturb_vars:
        val = get_perturbed_value(perturb_var, rng)
        n_val = get_perturbed_value("N", rng)
        question = f"What is the value of M_n at time step {n_val} if {perturb_var} is {val}?"
        program = f"FinalValue(box_model(SetTo(N,{n_val}),SetTo({perturb_var},{val}),M_n)"
        yield question, program


def mini_question3_gen(rng):
    perturb_vars = ['Fwn', 'M_ek', 'D_low0', 'epsilon', 'K_v', 'A_Redi', 'A_GM', 'M_SD', 'T_north0',
                    'T_south0', 'T_low0', 'T_deep0', 'S_north0', 'S_south0', 'S_low0', 'S_deep0',
                    'Fws', 'area', 'area_low', 'area_s', 'area_n', 'D_high', 'time_step_size_in_years']
    for perturb_var1, perturb_var2 in combinations(perturb_vars, 2):
        val1 = get_perturbed_value(perturb_var1, rng)
        val2 = get_perturbed_value(perturb_var2, rng)
        question = f"If {perturb_var1} is {val1} and {perturb_var2} is {val2}, does the AMOC collapse?"
        program = f"ChangeSign(box_model(SetTo({perturb_var1},{val1}),SetTo({perturb_var2},{val2})),M_n)"
        yield question, program


def mini_question4_gen(rng):
    perturb_vars = ['Fwn', 'M_ek', 'D_low0', 'epsilon', 'K_v', 'A_Redi', 'A_GM', 'M_SD',
                    'T_south0', 'T_low0', 'T_deep0', 'S_north0', 'S_south0', 'S_low0', 'S_deep0',
                    'Fws', 'area', 'area_low', 'area_s', 'area_n', 'D_high', 'time_step_size_in_years']
    for perturb_var in perturb_vars:
        val = get_perturbed_value(perturb_var, rng)
        question = f"What is the final value of the AMOC when {perturb_var} is {val}?"
        program = f"FinalValue(box_model(SetTo({perturb_var},{val})),M_n)"
        yield question, program


def mini_question5_gen(rng):
    perturb_vars = ['Fwn', 'M_ek', 'D_low0', 'epsilon', 'K_v', 'A_Redi', 'A_GM', 'M_SD',
                    'T_south0', 'T_low0', 'T_deep0', 'S_north0', 'S_south0', 'S_low0', 'S_deep0',
                    'Fws', 'area', 'area_low', 'area_s', 'area_n', 'D_high', 'time_step_size_in_years',
                    'blue', 'red', 'green', 'cylinder', 'cube', 'rubber', 'metal', 'large', 'gray']
    for perturb_var in perturb_vars:
        question = f"What is {perturb_var}?"
        program = f"is({perturb_var})"
        yield question, program


def mini_question6_gen(rng):
    perturb_vars = ['Fwn', 'M_ek', 'D_low0', 'epsilon', 'K_v', 'A_Redi', 'A_GM', 'M_SD', 'T_north0',
                    'T_south0', 'T_low0', 'T_deep0', 'S_north0', 'S_south0', 'S_low0', 'S_deep0',
                    'Fws', 'area', 'area_low', 'area_s', 'area_n', 'D_high', 'time_step_size_in_years',
                    'blue', 'red', 'green', 'cylinder', 'cube', 'rubber', 'metal', 'large', 'gray', 'cyan',
                    'sphere', 'block', 'shiny', 'matte']
    for perturb_var1, perturb_var2 in combinations(perturb_vars, 2):
        question = f"Is {perturb_var1} equal to {perturb_var2}?"
        program = f"equal({perturb_var1},{perturb_var2})"
        yield question, program


def mini_question7_gen(rng):
    perturb_vars = ['Fwn', 'M_ek', 'D_low0', 'epsilon', 'K_v', 'A_Redi', 'A_GM', 'M_SD', 'T_north0',
                    'T_south0', 'T_low0', 'T_deep0', 'S_north0', 'S_south0', 'S_low0', 'S_deep0',
                    'Fws', 'area', 'area_low', 'area_s', 'area_n', 'D_high',
                    'blue', 'green', 'cylinder', 'red', 'rubber', 'purple', 'large', 'metal', 'matte']
    for perturb_var in perturb_vars:
        val = get_perturbed_value(perturb_var, rng)
        question = f"Does {perturb_var} collapse the AMOC at {val}?"
        program = f"ChangeSign(box_model(SetTo({perturb_var},{val})),M_n)"
        yield question, program


def mini_question8_gen(rng):
    perturb_vars = ['Fwn', 'M_ek', 'D_low0', 'epsilon', 'K_v', 'A_Redi', 'A_GM', 'M_SD', 'T_north0',
                    'T_south0', 'T_low0', 'T_deep0', 'S_north0', 'S_south0', 'S_low0', 'S_deep0',
                    'Fws', 'area', 'area_low', 'area_s', 'area_n', 'D_high', 'time_step_size_in_years',
                    'blue', 'red', 'green', 'shape', 'cube', 'sphere', 'rubber', 'metal', 'large']
    for perturb_var in perturb_vars:
        question = f"Is {perturb_var} related to the AMOC?"
        program = f"AMOC({perturb_var})"
        yield question, program


def mini_question9_gen(rng):
    perturb_vars = ['Fwn', 'M_ek', 'D_low0', 'epsilon', 'K_v', 'A_Redi', 'A_GM', 'M_SD', 'T_north0',
                    'T_south0', 'T_low0', 'T_deep0', 'S_north0', 'S_south0', 'S_low0', 'S_deep0',
                    'Fws', 'D_high']
    for perturb_var in perturb_vars:
        val = get_perturbed_value(perturb_var, rng)
        question = f"The AMOC state changed after {perturb_var} is set to {val}, did {perturb_var} cause this?"
        program = f"ChangeSign(box_model(SetTo({perturb_var},{val})),M_n)"
        yield question, program


if __name__ == "__main__":
    rng1 = np.random.RandomState()
    all_tokens = set()
    for f in ALL_QUESTION_FUNCS:
        param_vars = ('Fwn',)
        bmo_f = 'ChangeSign'
        bmo = 'M_n'
        print(f(param_vars, bmo_f, bmo, rng1))

