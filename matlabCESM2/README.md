# Matlab CESM2 

# Introduction
This folder contains Matlab scripts for using CESM2 (Community Earth System Model, version 2) output data to create timeseries similar to the Gnanadesikan 4-box model for the Atlantic.
- Reference paper for the 4-box model: https://doi.org/10.1175/JCLI-D-18-0388.1 Gnanadesikan et al. (2018)<sup>1</sup>.
- Reference paper for CESM2: https://doi.org/10.1029/2019MS001916 Donabasoglu et al. (2019)<sup>2</sup>.


# Instructions 

## Data Download 
Data files in netcdf format are expected; these may be accessed for CESM2 through 
either: 
1. https://esgf-node.llnl.gov/search/cmip6/ (CMIP) or 
2. https://www.earthsystemgrid.org/dataset/ucar.cgd.cesm2le.ocn.proc.monthly_ave.html (LE)

These two sources have different variable naming conventions.

You must download a set of 4 files from the same timeperiod to get matching results. 

From the CMIP source, you want variables so, thetao, vo, msftmz. Searching on that site, try NCAR AND Omon AND so to see monthly salt files from NCAR, the modeling center that produces CESM2. You MUST also get one SALT or TEMP file from the LE source-- these contain grid information that is missing in the CMIP-sourced data files.

From the LE source, you want variables SALT, TEMP, VVEL, MOC. The link goes directly to the monthly ocean data.

In both cases, wget and curl scripts are available if you want to download many files or download onto your HPC system. We recommend putting these files into their own directory, which will be set in the configuration file along with their names.

## Libraries and Requirements
Matlab version 2017b or later is needed to run these codes, due to the ability to extend matrices to match dimensions for binary operations and the isfile() function.

Gibbs Sea Water Toolbox is required: https://www.teos-10.org/software.htm  McDougall and Barker (2011)<sup>3</sup>

YAML is also required: https://code.google.com/archive/p/yamlmatlab/  
YAML syntax: https://docs.ansible.com/ansible/latest/reference_appendices/YAMLSyntax.html

## Configuration 
This section describes the configuration file (\*.yaml, in the configs folder), which holds all paths, filenames, and parameters for running the code.
Using this will allow you to not change anything in the codes themselves, but simply set the 'configuration' and run.

Sample:

```buildoutcfg
# csem2to4box config
InputFiles:
    salt: b.e21.BHISTcmip6.f09_g17.LE2-1001.001.pop.h.SALT.185001-185912.nc
    temp: b.e21.BHISTcmip6.f09_g17.LE2-1001.001.pop.h.TEMP.185001-185912.nc
    velN: b.e21.BHISTcmip6.f09_g17.LE2-1001.001.pop.h.VVEL.185001-185912.nc
    MOC: b.e21.BHISTcmip6.f09_g17.LE2-1001.001.pop.h.MOC.185001-185912.nc
    grid: b.e21.BHISTcmip6.f09_g17.LE2-1001.001.pop.h.SALT.185001-185912.nc
    datapath: /path/to/above/files/
    gswLibraryPath: /path/toyour/gsw/
    source: LE
    lowmemory: 1
coordinates:
    latSouth: -45 
    latNorth1: 45 
    latNorth2: 65
    depthH: 200
parameters:
    diffusionGM: 3000
    diffusionRedi: 600
    diffusionVert: 0.16e-4
    epsilon: 1.4e-4
OutputFiles:
    matlab: zonalmeanBHISTcmip6LE2-1001-001-185001-185912.mat
    atlantic: zonalmeanABHISTcmip6LE2-1001-001-185001-185912.nc 
    pacific: zonalmeanPBHISTcmip6LE2-1001-001-185001-185912.nc
    box: boxBHISTcmip6LE2-1001-001-185001-185912.nc

```

### Input data: 
1. Files for salinity, temperature, northward velocity, overturning circulation, and one LE file to access grid variables not included in CMIP files. If you are using LE files, simply repeat your SALT or TEMP filename.  
2. The path to the input files.  
3. The path to your Gibbs Seawater Toolbox  
4. Parameters: source (CMIP or LE), lowmemory (true 1/false 0), diffusivities and time constant of the model (defaults are for CESM2), and limits of the high-latitude boxes (latSouth, latNorth (a southern and northern limit), depthH).  

### Output data: 
1. netcdf filenames to write zonal-mean temperature, salinity, potential density, northward velocity, and overturning circulation for the Atlantic and the Pacific,
where the Pacific includes the full Southern Ocean in its southernmost extent. 
2. A .mat filename to write out all variables in both of (1). 
3. A netcdf filename to write out the box-model timeseries (monthly values): temperature, salinity, and sigma (potential density) for the 4 boxes, 
pycnocline depth (D), Ekman (Mek) and deepwater formation (Ms) mass fluxes in the Southern Ocean, AMOC (Atlantic Meridional Overturning Circulation) as a mass flux (Mn),
and the freshwater fluxes for the northern and southern boxes (Fws, Fwn). 

Atlantic and Pacific contain zonal-mean latitude (latT for tracers,  latV for velocities), longitude (lonT for tracers, latT for velocities), tracer volume (volumeT), velocity volume (volumeV),  northward velocity (velN), temperature (temp), salinity (salt),  potential density (rho0), and integrated density anomaly D0 (for pycnocline depth)

### Coordinates
The limits of the high-latitude boxes: 
1. latSouth: latitude (negative for South) that is the northern limit of the southern box (-54 to -35 is reasonable) 
2. latNorth1: latitude (positive for North) that is the southern limit of the northern box (eg 45)
3. latNorth2: latitude (positive for North) that is the northern limit of the northern box (eg 65, 85)
4. depthH: the depth (in positive meters) below the surface that is the limit of the southern and northern boxes.

These are combined into a string that is a global attribute in the netcdf output file of the box-model timeseries.

### Parameters
1. diffusionGM: Gent-McWilliams diffusivity, 3000 in CESM2
2. diffusionRedi: Redi diffusivity, 600 in CESM2
3. diffusionVert: Vertical diffusivity, 0.16e-4 in CESM2
4. epsilon: Time constant (1/seconds) for the northern box. Estimated as 1.4e-4 in CESM2.

These are combined into a string that is a global attribute in the netcdf output file of the box-model timeseries. These are necessary inputs for the box model, but are not currently estimated from the model data.

## Running

First edit the configuration (config.yaml) file with the corresponding input and output file names and the limits you want for the Northern and Southern high-latitude boxes. Also edit the config filename and path in configReader.  The data folder contains single-month-average variables of both LE and CMIP type; associated configTest.yaml files in the configs folder are available to test that the code will run correctly in your system.  
In matlab, run configReader.  
Then run cesm2to4box.  


# Dependencies

This code uses zonalVTSrho0set to perform the zonal averaging and density computations.  
If you have a low-RAM environment, set lowmemory=1.  
It uses freshwaterfluxN and freshwaterfluxS to compute the freshwater fluxes.  
It uses zonal2box to compute the temperature, salinity, and sigma (potential density) for the 4 boxes, pycnocline depth,
Ekman and deepwater formation mass fluxes in the Southern Ocean, AMOC (Atlantic Meridional Overturning Circulation) as a mass flux.

## Acknowledgements

This code was produced under the DARPA AI-assisted Climate Tipping-point Modeling (ACTM) 
program, and in association with Johns Hopkins University. 

<sup>1</sup>Gnanadesikan, A., Kelson, R., & Sten, M. (2018). Flux Correction and Overturning Stability: 
Insights from a Dynamical Box Model, Journal of Climate, 31(22), 9335-9350. 
Retrieved Mar 30, 2022 from [https://journals.ametsoc.org/view/journals/clim/31/22/jcli-d-18-0388.1.xml](https://journals.ametsoc.org/view/journals/clim/31/22/jcli-d-18-0388.1.xml).

<sup>2</sup>Donabasoglu, G., Lamarque, J. F., Bacmeister, J., Bailey, D. A., DuVivier, A. K., & Edwards, J. The Commuity Earth System Model Version 2 (CESM2). J. Adv. Model. Earth. Sy, 12, e2019MS001916. Accessed Apr 20, 2022 via [https://doi.org/10.1029/2019MS001916 ](https://doi.org/10.1029/2019MS001916)

<sup>3</sup>McDougall, T.J. and P.M. Barker, 2011: Getting started with TEOS-10 and the Gibbs Seawater (GSW) Oceanographic Toolbox, 28pp., SCOR/IAPSO WG127, ISBN 978-0-646-55621-5.

# License
Copyright 2022, The Johns Hopkins University Applied Physics Laboratory LLC

All rights reserved.

Distributed under the terms of the BSD 3-Clause License.
