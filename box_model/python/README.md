## Python Box model 

The Box model is a simplified representation of the Atlantic meridional 
overturning circulation (AMOC) simulation, used by Gnadfad et al.<sup>1</sup> 
to examine the stability of the AMOC. This code facilitates experimenting with 
the box model, including:

 * Documented API for running individual box model simulations
 * Generating data from many box model simulations
 * Storing box model data in NetCDF format

## Requirements

versions

## Getting Started

## running the code section



### Python
If you are unfamiliar with Python, we recommend downloading Anaconda from 
[here](https://www.anaconda.com/products/individual). Follow the instructions to install Anaconda, and then create a 
new conda environment (or virtual environment if not using Anaconda) by running

```commandline
$ conda create -n <environment name> python==3.9
```

Follow the prompts to finish creating the new environment. 
Once finished, activate the environment via the following command:

```commandline
$ conda activate <environment name>
```

The name of your environment should be in front of your command line, for example
if you named your environment "myenv", it should appear as follows:

```commandline
(myenv) $ 
```

### Python Box Model

Assuming you have the code pulled from the repository, navigate to the `box_model` directory and run

```commandline
$ pip install -e .
```

This should install the required packages to run the Box model code in your Python environment. 
Once installed, you should be able to run the follow scripts from the [scripts](box_model/scripts) directory:

  * [simple_example.py](box_model/scripts/simple_example.py): An example of how to run a single 
      box model simulation. Also creates plots of the results.
  * [collapse_example.py](box_model/scripts/collapse_example.py): Several examples of AMOC collapse 
      with plotted results.
  * [store_example_npz.py](box_model/scripts/store_example_npz.py): An example of how one might save box model data 
      as Numpy `.npz` files. 
  * [store_example_netcdf.py](box_model/scripts/store_example_netcdf.py): An example of how one might save box model 
      data in NetCDF format. 
  * [datagen_simulation.py](box_model/scripts/datagen_simulation.py): A script simulating a 
      parameter space exploration experiment using small random perturbations on box 
      model variables. Each simulation result is stored in NetCDF format.

## Organization

```
py_box_model
|   setup.py - Script to install trojai module into Python environment
│   scripts - Location for local code examples and other useful scripts
│   notebooks - Location for Jupyter Notebooks
└───core - Top level Python module
|   box_model.py - file containing code for the box model
    └───test - top level scripts directory
        └───TODO
```


## For Developers

Unit tests (how to run), developer notes, git reminders

## Acknowledgements

This code was produced under the DARPA AI-assisted Climate Tipping-point Modeling (ACTM) 
program, and in association with Johns Hopkins University. 

<sup>1</sup>Gnanadesikan, A., Kelson, R., & Sten, M. (2018). Flux Correction and Overturning Stability: 
Insights from a Dynamical Box Model, Journal of Climate, 31(22), 9335-9350. 
Retrieved Mar 30, 2022 from [https://journals.ametsoc.org/view/journals/clim/31/22/jcli-d-18-0388.1.xml](https://journals.ametsoc.org/view/journals/clim/31/22/jcli-d-18-0388.1.xml).