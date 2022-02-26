## Overview
Python module for running the fourbox model. 

## Getting Started


### Python
If you are unfamiliar with Python, I recommend downloading Anaconda from 
[here](https://www.anaconda.com/products/individual). Follow the instructions to install Anaconda, and then create a 
new conda environment (or virtual environment if not using Anaconda) by running

```
$ conda create -n <environment name> python==3.9
```

It should ask permission to install the python environment and some packages, give permission, and let it install. 
You will likely have to activate the environment once it finishes installing. It will tell you how, but for reference,
to activate the environment input the following into the console:

```commandline
$ conda activate <environment name>
```

The name of your environment should be in front of your command line, e.g. 

```commandline
(myenv) $ 
```

### PACMANs

Assuming you have the code pulled from the repository, navigate to the `box_model` directory and run

```
$ pip install -e .
```

This should install the required packages to run the fourbox model code in your Python environment. Once it is done, you should be able to run `scripts/def_sims.py`, which contains ported examples from `run_fourbox_Aredi.m`, or import and call functions from that file. 
View its contents for more details.

**NOTE**: Not all the examples from `run_fourbox_Aredi.m` have been fully ported. Also, the plots shown in the Matlab version that show the progress of the simulation are not currently shown in the Python version. 

**NOTE**: The code has been altered to use multiprocessing for faster simulation computation. This may affect debugging from an IDE, and may make the code less straightforward to read. See `scripts/script_utils.py` to get more intuition about what is happening in `scripts/def_sims.py`.

## Repository Organization

## Acknowledgements
