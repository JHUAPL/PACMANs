# -*- coding: utf-8 -*-
"""
Four Box Model Use Tutorial
=============

* **ACTM Performer:** JHU-APL;
* **Author:** Chace Ashcraft (chace.ashcraft@jhuapl.edu)

PyBAMOCS Tutorial

PyBAMOCS uses a simplified box model to simulate the Atlantic meridional overturning circulation (AMOC). The
implementation is based on the paper by Gnanadesikan et al.
(https://journals.ametsoc.org/view/journals/clim/31/22/jcli-d-18-0388.1.xml), which examined the stability of the AMOC.
This tutorial assumes that you have downloaded the PyBAMOCs code from the PACMANs repository on GitHub and installed
PyBAMOCS into your Python environment. Installation instructions for the PyBAMOCS module is provided below. For
additional information about installing PyBAMOCS and the PyBAMOCS API, please see the PACMANS repository
(https://github.com/JHUAPL/PACMANs), and navigate to `box_model/python/`.

This tutorial is meant to be a tool for getting started using the PyBAMOCS package and the included `box_model`
functionality, and is not meant to be a comprehensive overview of all functions or capabilities of the included code.
For a more thorough understanding, please consider viewing the code itself, and the examples in the `scripts` folder.
There is also a more extensive tutorial in the form of a Jupyter Notebook in the `notebooks` directory of the PyBAMOCS
module.

# PyBAMOCS Installation

We recommend installing PyBAMOCS in its own environment using `venv`
(https://docs.python.org/3/library/venv.html) or `conda`
(https://conda.io/projects/conda/en/latest/user-guide/install/index.html). Once in your new environment (if desired),
perform the following steps to install the module.

* Clone the PACMANS repository (https://github.com/JHUAPL/PACMANs)
    * `git clone https://github.com/JHUAPL/PACMANs.git`
* Change directories to `box_model/python/`
    * `cd box_model/python/`
* Install locally using `pip`
    * `pip install -e .`

To execute the snippet:

**Step 1:** Follow the instructions above to install the PyBAMOCS module.

**Step 2:** The snippet itself may be run from the command line as follows:

```
% python pybamocs_tutorial.py
```

We encourage the interested user to examine the code below to identify the relevant objects and methods required to
implement their specific use case.

"""

# .............................................
# IMPORT STATEMENTS
# .............................................

import time
from matplotlib import pyplot as plt
from typing import Union

# Import the `box_model` function and its arguments
from pybamocs.box_model import box_model
from pybamocs.box_model import NORTH_IDX, SOUTH_IDX, LOW_IDX, DEEP_IDX
from pybamocs.box_model_args import (
    BoxModelBoxDimensions,
    BoxModelInitConditions,
    BoxModelTimeStep,
    BoxModelParameters,
)


# Convenience function
def print_box_model_argument_settings(argument: Union[BoxModelBoxDimensions, BoxModelInitConditions,
                                                      BoxModelTimeStep, BoxModelParameters]) -> None:
    """
    Print box model settings to console for a given box_model argument.
    :param argument: One of the box_model argument objects.
    """
    settings_dict = argument.to_dict()  # Get the settings as a python dictionary

    print("vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv")
    # Print each key, value pair in the dictionary
    for key, value in settings_dict.items():
        print(f"{key}={value}")
    print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
    print()


def main():
    print("Box model settings are divided into five groups:")
    # Each object represents a set of parameters to the model
    box_model_dimensions = BoxModelBoxDimensions()
    box_model_initial_conditions = BoxModelInitConditions()
    box_model_time_settings = BoxModelTimeStep()
    box_model_parameters = BoxModelParameters()

    # And there is one object for each group as shown above.
    print("------------------------------------------------------------")
    print("Box Dimensions:")
    print_box_model_argument_settings(box_model_dimensions)

    print("------------------------------------------------------------")
    print("Initial Conditions")
    print_box_model_argument_settings(box_model_initial_conditions)

    print("------------------------------------------------------------")
    print("Model Time Step Parameters:")
    print_box_model_argument_settings(box_model_time_settings)

    print("------------------------------------------------------------")
    print("Model Parameters")
    print_box_model_argument_settings(box_model_parameters)

    # To run the box model, simply call the `box_model` function with your argument objects
    print("Running the box model...")
    start = time.time()
    results = box_model(box_model_dimensions,
                        box_model_initial_conditions,
                        box_model_parameters,
                        box_model_time_settings)
    print(f"Run complete. Time: {time.time() - start} seconds.")

    # Note that the results are contained in a BoxModelResult object
    print("Box model output object:")
    print(results)
    print()

    # You can access specific results directly from the object
    print("Result details:")
    print("------------------------------------------------------")
    print("Shape of M_n for run:", results.M_n.shape)
    print()

    # or you can "unpack" them all at once
    M_n, M_upw, M_eddy, D_low, T, S, sigma0 = results.unpack()

    print("------------------------------------------------------")
    print("First 3 values of each output variable:")
    print("M_n:", M_n[:3])
    print("M_upw:", M_upw[:3])
    print("M_eddy:", M_eddy[:3])
    print("D_low:", D_low[:3])
    print("T_north:", T[NORTH_IDX, :3])
    print("T_south:", T[SOUTH_IDX, :3])
    print("T_low:", T[LOW_IDX, :3])
    print("T_deep:", T[DEEP_IDX, :3])
    print("S_north:", S[NORTH_IDX, :3])
    print("S_south:", S[SOUTH_IDX, :3])
    print("S_low:", S[LOW_IDX, :3])
    print("S_deep:", S[DEEP_IDX, :3])
    print("sigma0_north:", sigma0[NORTH_IDX, :3])
    print("sigma0_south:", sigma0[SOUTH_IDX, :3])
    print("sigma0_low:", sigma0[LOW_IDX, :3])
    print("sigma0_deep:", sigma0[DEEP_IDX, :3])

    print("Plotting results...")
    plt.plot(M_n, label='M_n')
    plt.plot(M_upw, label='M_upw')
    plt.plot(M_eddy, label='M_eddy')
    plt.plot(D_low, label='Dlow')
    plt.legend()
    plt.title("1D Box Model Outputs")

    fig, ax = plt.subplots(nrows=2, ncols=2)
    ax[0, 0].plot(T[NORTH_IDX], label='North')
    ax[0, 1].plot(T[SOUTH_IDX], label='South')
    ax[1, 0].plot(T[LOW_IDX], label='Low')
    ax[1, 1].plot(T[DEEP_IDX], label='Deep')
    ax[0, 0].legend()
    ax[0, 1].legend()
    ax[1, 0].legend()
    ax[1, 1].legend()
    plt.suptitle("Temperature in the 4 different boxes")
    plt.tight_layout()

    fig1, ax1 = plt.subplots(nrows=2, ncols=2)
    ax1[0, 0].plot(S[NORTH_IDX], label='North')
    ax1[0, 1].plot(S[SOUTH_IDX], label='South')
    ax1[1, 0].plot(S[LOW_IDX], label='Low')
    ax1[1, 1].plot(S[DEEP_IDX], label='Deep')
    ax1[0, 0].legend()
    ax1[0, 1].legend()
    ax1[1, 0].legend()
    ax1[1, 1].legend()
    plt.suptitle("Salinity in the 4 different boxes")
    plt.tight_layout()

    fig2, ax2 = plt.subplots(nrows=2, ncols=2)
    ax2[0, 0].plot(sigma0[NORTH_IDX], label='North')
    ax2[0, 1].plot(sigma0[SOUTH_IDX], label='South')
    ax2[1, 0].plot(sigma0[LOW_IDX], label='Low')
    ax2[1, 1].plot(sigma0[DEEP_IDX], label='Deep')
    ax2[0, 0].legend()
    ax2[0, 1].legend()
    ax2[1, 0].legend()
    ax2[1, 1].legend()
    plt.suptitle("Density in the 4 different boxes")
    plt.tight_layout()
    plt.show(block=False)

    # Consider an example of some data collection
    Fwn_values_to_test = [10000, 50000, 100000, 500000, 1000000]
    alternate_north_starting_temp = 4.0

    box_dims = BoxModelBoxDimensions()
    params = BoxModelParameters()
    time_step = BoxModelTimeStep()
    init = BoxModelInitConditions(T_north0=alternate_north_starting_temp)

    # Collect the data... (should take a few seconds)
    print(f"Generating data for alternate parameter settings: T_north={alternate_north_starting_temp}")
    start_time = time.time()
    results = []
    for fwn in Fwn_values_to_test:
        print(f"Fwn={fwn}")
        params.Fwn = fwn
        results.append(box_model(box_dims, init, params, time_step))
    time_to_collect_data = time.time() - start_time
    print(f"Total time to collect data: {time_to_collect_data} seconds")

    # Let's look at the difference in M_n for each run
    print("Plotting results...")
    plt.figure()
    for i in range(len(Fwn_values_to_test)):
        plt.plot(results[i].M_n, label=f"Fwn={Fwn_values_to_test[i]}")
    plt.title(f"M_n for different Northern Fluxes and T_north0={alternate_north_starting_temp}")
    plt.legend()
    plt.show()  # suspends script until plot windows are closed
    print("Done")


if __name__ == "__main__":
    main()
