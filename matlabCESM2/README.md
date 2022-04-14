# Matlab CESM2 

# Intro
This folder contains Matlab scripts for using CESM2 (Community Earth System Model, version 2) output data to create timeseries similar to the Gnanadesikan 4-box model for the Atlantic.
- Reference paper for the 4-box model: https://doi.org/10.1175/JCLI-D-18-0388.1
- Reference paper for CESM2: https://doi.org/10.1029/2019MS001916

#License
Copyright 2022, The Johns Hopkins University Applied Physics Laboratory LLC
All rights reserved.
Distributed under the terms of the BSD 3-Clause License.

## Download 
Data files in netcdf format are expected; these may be accessed for CESM2 through 
either: 
1. https://esgf-node.llnl.gov/search/cmip6/ (CMIP) or 
2. https://www.earthsystemgrid.org/dataset/ucar.cgd.cesm2le.ocn.proc.monthly_ave.html (LE)

These two sources have different variable naming conventions.
You must download a set of 4 files from the same timeperiod to get matching results.
From the CMIP source, you want variables so, thetao, vo, msftmz. Searching on that site, try NCAR AND Omon AND so to see monthly salt files from NCAR, the modeling center that produces CESM2.
From the LE source, you want variables SALT, TEMP, VVEL, MOC. The link goes directly to the monthly ocean data.

## Format

# Instructions 
## Libraries (or prereqs to run )
Matlab version 2016b or later is needed to run these codes, due to the ability to extend matrices to match dimensions for binary operations.
Gibbs Sea Water Toolbox is also required.
So is YAML.

## Configuration 
This section will describe the configuration file, which holds all paths, filenames, and parameters for running the code.
Using this will allow you to not change anything in the codes themselves, but simply set the 'configuration' and run.

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

- Input data: 
1. Files for salinity, temperature, northward velocity, overturning circulation, and one LE file to access grid variables not included in CMIP files. 
2. The path to the input files.
3. The path to your Gibbs Seawater Toolbox
4. Parameters: source (CMIP or LE), lowmemory (true 1/false 0), diffusivities and time constant of the model (defaults are for CESM2), and limits of the high-latitude boxes (latSouth, latNorth (a southern and northern limit), depthH).

- Output data: 
1. netcdf filenames to write zonal-mean temperature, salinity, potential density, northward velocity, and overturning circulation for the Atlantic (A) and the Pacific (P),
where the Pacific includes the full Southern Ocean in its southernmost extent. 
2. A .mat filename to write out all variables in both of (1). 
3. A netcdf filename to write out the box-model timeseries (monthly values): temperature, salinity, and sigma (potential density) for the 4 boxes, 
pycnocline depth (D), Ekman (Mek) and deepwater formation (Ms) mass fluxes in the Southern Ocean, AMOC (Atlantic Meridional Overturning Circulation) as a mass flux (Mn),
and the freshwater fluxes for the northern and southern boxes (Fws, Fwn). The additional parameters needed to run the 4-box model,diffusivities and time constant of the model,
 are noted as a string global parameter; and the limits of the high-latitude boxes are noted as another.

## Running

First edit the configuration file with the corresponding input and output file names. 
In matlab, run config_reader. 
Then run cesm2to4boxCorrect.



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

# old version of this README
This document notes the use of files in this folder. 
All are matlab codes, for using CESM2 (Community Earth System Model, version 2) output data, to create timeseries similar to the Gnanadesikan 4-box model for the Atlantic.
Reference paper for the 4-box model: https://doi.org/10.1175/JCLI-D-18-0388.1
Reference paper for CESM2: https://doi.org/10.1029/2019MS001916

Data files in netcdf format are expected; these may be accessed for CESM2 through 
either https://esgf-node.llnl.gov/search/cmip6/ (CMIP) or https://www.earthsystemgrid.org/dataset/ucar.cgd.cesm2le.ocn.proc.monthly_ave.html (LE)
These two sources have different variable naming conventions.

The top-level code to use is cesm2to4boxNewFw. 
Edit the top section for the data filenames you have and the filenames you want data saved to. 
Input: files for salinty, temperature, northward velocity, overturning circulation, and one LE file to access grid variables not included in CMIP files.
Output: netcdf files of zonal-mean temperature, salinity, potential density, northward velocity, and overturning circulation for the Atlantic (A) and the Pacific (P),
where the Pacific includes the full Southern Ocean in its southernmost extent. A .mat file containing all variables in both of those. 
And finally, a netcdf file containing the box-model timeseries (monthly values): temperature, salinity, and sigma (potential density) for the 4 boxes, 
pycnocline depth (D), Ekman (Mek) and deepwater formation (Ms) mass fluxes in the Southern Ocean, AMOC (Atlantic Meridional Overturning Circulation) as a mass flux (Mn),
and the freshwater fluxes for the northern and southern boxes (Fws, Fwn). The additional parameters needed to run the 4-box model are notes as a string global parameter; 
these are mixing parameters and a time constant for the northern box.

This code uses zonalVTSrho0 (for CMIP data) or zonalVTSrho0LE (for LE data) to perform the zonal averaging and density computations. 
If you have a low-RAM environment, choose zonalVTSrho0lowmemory (for CMIP data) or zonalVTSrho0LElowmemory (for LE data) instead.
It uses freshwaterfluxN and freshwaterfluxS to compute the freshwater fluxes.
It uses zonal2box to compute the temperature, salinity, and sigma (potential density) for the 4 boxes, pycnocline depth,
Ekman and deepwater formation mass fluxes in the Southern Ocean, AMOC (Atlantic Meridional Overturning Circulation) as a mass flux.

Deprecated codes:
zonalV, zonalTSrho0, now combined into the zonalVTSrho0 series
cesm2to4box, replaced by cesm2to4boxNewFw, which calculates freshwater fluxes differently, now replaced by cesm2to4boxCorrect which has better variable names
