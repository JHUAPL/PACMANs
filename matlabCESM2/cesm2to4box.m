% Copyright 2022, The Johns Hopkins University Applied Physics Laboratory LLC
% All rights reserved.
% Distributed under the terms of the BSD 3-Clause License.

% This is the high-level code to process CESM2 to box model style
% timeseries. Run config_reader first. Requires zonalVTSrho0set,
% freshwaterfluxS, freshwaterfluxN, and zonal2box.

%% config structure parsing

InputFiles=ConfigStruct.InputFiles;
parameters=ConfigStruct.parameters;
coordinates=ConfigStruct.coordinates;
OutputFiles=ConfigStruct.OutputFiles;

% will generate e.g. '45S 45-65N 200m', the boxlimitstr, which is a global 
% attribute of OutputFiles.box
boxlimitstr = strcat(num2str(abs(coordinates.latSouth)), 'S,', ...
    num2str(coordinates.latNorth1), '-', num2str(coordinates.latNorth2), ...
    'N,', num2str(coordinates.depthH), 'm'); 

% will generate e.g. 'Agm=3000,Aredi=600,Kv=0.16e-4,epsilon=1.4e-4', the modelparamstr, 
% which is a global attribute of OutputFiles.box
modelparamsstr = strcat('Agm=', num2str(parameters.diffusionGM), ',Aredi=', ...
    num2str(parameters.diffusionRedi), ',Kv=', num2str(parameters.diffusionVert), ...
    ',epsilon=', num2str(parameters.epsilon));
    
% check for existing copies of OutputFiles and append date to differentiate 
% the new ones

if isfile(OutputFiles.matlab)
    oldName=OutputFiles.matlab;
    newName=strcat(OutputFiles.matlab(1:end-4),date,'.mat');
    display(strcat('Matlab output filename=',oldName,' existed'))
    display(strcat('Matlab output filename now is=',newName))
    OutputFiles.matlab=newName;
end

if isfile(OutputFiles.box)
    oldName=OutputFiles.box;
    newName=strcat(OutputFiles.box(1:end-4),date,'.mat');
    display(strcat('Box output filename=',oldName,' existed'))
    display(strcat('Box output filename now is=',newName))
    OutputFiles.box=newName;
end

if isfile(OutputFiles.atlantic)
    oldName=OutputFiles.atlantic;
    newName=strcat(OutputFiles.atlantic(1:end-4),date,'.mat');
    display(strcat('Atlantic output filename=',oldName,' existed'))
    display(strcat('Atlantic output filename now is=',newName))
    OutputFiles.atlantic=newName;
end

if isfile(OutputFiles.pacific)
    oldName=OutputFiles.pacific;
    newName=strcat(OutputFiles.pacific(1:end-4),date,'.mat');
    display(strcat('Pacific output filename=',oldName,' existed'))
    display(strcat('Pacific output filename now is=',newName))
    OutputFiles.pacific=newName;
end

%% Add Paths

addpath(genpath(InputFiles.gswLibraryPath))
display('GSW Toolbox Paths Added');
addpath(InputFiles.datapath)
display('Input file path added')

%% compute zonal-mean T, S, potential density, pycnocline depth

[timeUTC, depth, Atlantic, Pacific] = zonalVTSrho0set(InputFiles);

% Atlantic and Pacific contain zonal-mean latitude (latT for tracers, 
% latV for velocities), longitude (lonT for tracers, latT for velocities),
% tracer volume (volumeT), velocity volume (volumeV), 
% northward velocity (velN), temperature (temp), salinity (salt), 
% potential density (rho0),
% and integrated density anomaly D0 (for pycnocline depth)

%% load meridional overturning circulation

switch InputFiles.source
    case 'CMIP'
        msftmzKgpersec = ncread(InputFiles.MOC, 'msftmz');
        % dimensions latitude,levels (depth),basin,time,
        % Size:       395x61x3x600
        depthMOC = ncread(InFileName_1, 'lev') / 100; %cm-->m
        latMOC = ncread(InFileName_1, 'lat');
        AMOCsv = squeeze(msftmzKgpersec(:, :, 1, :)/1000000000); 
        %(lat,depth,1=atl_arctic,months)
        PMOCsv = squeeze(msftmzKgpersec(:, :, 2, :)/1000000000);
    case 'LE'
        msftmzSv = ncread(InputFiles.MOC, 'MOC'); %in Sverdrups
        depthMOC = ncread(InputFiles.MOC, 'moc_z') / 100; %cm-->m
        latMOC = ncread(InputFiles.MOC, 'lat_aux_grid');
        AMOCsv = squeeze(sum(msftmzSv(:, :, :, 2, :), 3)); 
        %(lat,depth,1=atl_arctic,months)
        PMOCsv = squeeze(sum(msftmzSv(:, :, :, 1, :), 3)) - AMOCsv;
end

%% save mat here- comment out if not wanted

save(OutputFiles.matlab)

%% save zonal-mean VTSrho0 information out to netcdf, Atlantic

lat = Atlantic.latT(:, 1);
nccreate(OutputFiles.atlantic, 'lat', ...
    'Dimensions', {'lat', length(lat)});
nccreate(OutputFiles.atlantic, 'time', ...
    'Dimensions', {'time', length(timeUTC)});
nccreate(OutputFiles.atlantic, 'depth', ...
    'Dimensions', {'depth', length(depth)});
nccreate(OutputFiles.atlantic, 'lon', ...
    'Dimensions', {'lat', length(lat), ...
    'depth', length(depth)});
nccreate(OutputFiles.atlantic, 'lonV', ...
    'Dimensions', {'lat', length(lat), ...
    'depth', length(depth)});
nccreate(OutputFiles.atlantic, 'latV', ...
    'Dimensions', {'latV', length(lat), ...
    'depth', length(depth)});
nccreate(OutputFiles.atlantic, 'latMOC', ...
    'Dimensions', {'latMOC', length(latMOC), ...
    'depth', length(depth)});
nccreate(OutputFiles.atlantic, 'volume', ...
    'Dimensions', {'lat', length(lat), ...
    'depth', length(depth)});
nccreate(OutputFiles.atlantic, 'volumeV', ...
    'Dimensions', {'lat', length(lat), ...
    'depth', length(depth)});
nccreate(OutputFiles.atlantic, 'meanlat', ...
    'Dimensions', {'lat', length(lat), ...
    'depth', length(depth)});
nccreate(OutputFiles.atlantic, 'temperature', ...
    'Dimensions', {'lat', length(lat), ...
    'depth', length(depth), ...
    'time', length(timeUTC)});
nccreate(OutputFiles.atlantic, 'salinity', ...
    'Dimensions', {'lat', length(lat), ...
    'depth', length(depth), ...
    'time', length(timeUTC)});
nccreate(OutputFiles.atlantic, 'potentialDensity', ...
    'Dimensions', {'lat', length(lat), ...
    'depth', length(depth), ...
    'time', length(timeUTC)});
nccreate(OutputFiles.atlantic, 'velocity', ...
    'Dimensions', {'lat', length(lat), ...
    'depth', length(depth), ...
    'time', length(timeUTC)});
nccreate(OutputFiles.atlantic, 'MOC', ...
    'Dimensions', {'latMOC', length(latMOC), ...
    'depth', length(depth), ...
    'time', length(timeUTC)});
nccreate(OutputFiles.atlantic, 'pycnoclineDepth', ...
    'Dimensions', {'lat', length(lat), ...
    'time', length(timeUTC)});
ncwriteatt(OutputFiles.atlantic, 'lon', 'long_name', 'longitude')
ncwriteatt(OutputFiles.atlantic, 'lon', 'units', 'degree_east')
ncwriteatt(OutputFiles.atlantic, 'lon', 'standard_name', 'longitude')

ncwriteatt(OutputFiles.atlantic, 'lat', 'long_name', 'latitude')
ncwriteatt(OutputFiles.atlantic, 'lat', 'units', 'degree_north')
ncwriteatt(OutputFiles.atlantic, 'lat', 'standard_name', 'latitude')
ncwriteatt(OutputFiles.atlantic, 'time', 'units', 'days')
ncwriteatt(OutputFiles.atlantic, '/', 'creation_date', datestr(now));
ncwriteatt(OutputFiles.atlantic, '/', 'model', ...
    'CESM2 1 Degree Global Model for CMIP');
ncwriteatt(OutputFiles.atlantic, 'volume', 'units', 'm3')
ncwriteatt(OutputFiles.atlantic, 'volume', 'coordinates', 'lat depth')
ncwriteatt(OutputFiles.atlantic, 'volumeV', 'units', 'm3')
ncwriteatt(OutputFiles.atlantic, 'volumeV', 'coordinates', 'lat depth')
ncwriteatt(OutputFiles.atlantic, 'lon', 'coordinates', 'lat depth')
ncwriteatt(OutputFiles.atlantic, 'meanlat', 'coordinates', 'lat depth')
ncwriteatt(OutputFiles.atlantic, 'meanlat', 'units', 'degree_north')
ncwriteatt(OutputFiles.atlantic, 'temperature', 'coordinates', 'lat depth time')
ncwriteatt(OutputFiles.atlantic, 'temperature', 'units', 'degrees Celsius')
ncwriteatt(OutputFiles.atlantic, 'salinity', 'coordinates', 'lat depth time')
ncwriteatt(OutputFiles.atlantic, 'salinity', 'units', 'psu')
ncwriteatt(OutputFiles.atlantic, 'potentialDensity', 'coordinates', 'lat depth time')
ncwriteatt(OutputFiles.atlantic, 'potentialDensity', 'units', 'kg per m3')
ncwriteatt(OutputFiles.atlantic, 'velocity', 'coordinates', 'lat depth time')
ncwriteatt(OutputFiles.atlantic, 'velocity', 'units', 'meters per second')
ncwriteatt(OutputFiles.atlantic, 'pycnoclineDepth', 'coordinates', 'lat time')
ncwriteatt(OutputFiles.atlantic, 'pycnoclineDepth', 'units', 'meters')

ncwrite(OutputFiles.atlantic, 'lon', Atlantic.lonT);
ncwrite(OutputFiles.atlantic, 'lonV', Atlantic.lonV);
ncwrite(OutputFiles.atlantic, 'time', timeUTC);
ncwrite(OutputFiles.atlantic, 'lat', Atlantic.latT(:, 1));
ncwrite(OutputFiles.atlantic, 'meanlat', Atlantic.latT);
ncwrite(OutputFiles.atlantic, 'latV', Atlantic.latV);
ncwrite(OutputFiles.atlantic, 'volume', Atlantic.volumeT);
ncwrite(OutputFiles.atlantic, 'volumeV', Atlantic.volumeV);
ncwrite(OutputFiles.atlantic, 'temperature', Atlantic.temp);
ncwrite(OutputFiles.atlantic, 'salinity', Atlantic.salt);
ncwrite(OutputFiles.atlantic, 'velocity', Atlantic.velN);
ncwrite(OutputFiles.atlantic, 'potentialDensity', Atlantic.rho0);
ncwrite(OutputFiles.atlantic, 'pycnoclineDepth', Atlantic.D0);

%% write Pacific

%Read the variable, dimension, and group definitions from the file using ncinfo.
% This information defines the file's schema.
S = ncinfo(OutputFiles.atlantic);
%create pacific file with all the same formatting
ncwriteschema(OutputFiles.pacific, S)
ncwrite(OutputFiles.pacific, 'lon', Pacific.lonT);
ncwrite(OutputFiles.pacific, 'lonV', Pacific.lonV);
ncwrite(OutputFiles.pacific, 'time', timeUTC);
ncwrite(OutputFiles.pacific, 'lat', Pacific.latT(:, 1));
ncwrite(OutputFiles.pacific, 'meanlat', Pacific.latT);
ncwrite(OutputFiles.pacific, 'latV', Pacific.latV);
ncwrite(OutputFiles.pacific, 'volume', Pacific.volumeT);
ncwrite(OutputFiles.pacific, 'volumeV', Pacific.volumeV);
ncwrite(OutputFiles.pacific, 'temperature', Pacific.temp);
ncwrite(OutputFiles.pacific, 'salinity', Pacific.salt);
ncwrite(OutputFiles.pacific, 'velocity', Pacific.velN);
ncwrite(OutputFiles.pacific, 'potentialDensity', Pacific.rho0);
ncwrite(OutputFiles.pacific, 'pycnoclineDepth', Pacific.D0);

%% zonal to box, Atlantic
[T4, S4, sigma4, D, Mn, Mek, Ms] = ...
    zonal2box(coordinates, depth, Atlantic, Pacific, AMOCsv);
% use Pacific for southern box, Atlantic for deep, low, north

dyu = ncread(InputFiles.grid, 'DYU') ./ 100; %cm to meters, y-spacing
[Fwn] = freshwaterfluxN(coordinates, depth, Atlantic, dyu);
[Fws] = freshwaterfluxS(coordinates, depth, Pacific, dyu);

FwintoS = -Fws;
FwintoN = Fwn(:, 1) - Fwn(:, 2);

%% save box information out to netcdf

time = timeUTC;

nccreate(OutputFiles.box, 'time', ...
    'Dimensions', {'time', length(timeUTC)});
nccreate(OutputFiles.box, 'box', ...
    'Dimensions', {'box', 4});
nccreate(OutputFiles.box, 'latNorth', ...
    'Dimensions', {'latNorth', 2});
nccreate(OutputFiles.box, 'temperature', ...
    'Dimensions', {'box', 4, ...
    'time', length(time)});
nccreate(OutputFiles.box, 'salinity', ...
    'Dimensions', {'box', 4, ...
    'time', length(time)});
nccreate(OutputFiles.box, 'density', ...
    'Dimensions', {'box', 4, ...
    'time', length(time)});
nccreate(OutputFiles.box, 'AMOC', ...
    'Dimensions', {'time', length(time)});
nccreate(OutputFiles.box, 'Dlow', ...
    'Dimensions', {'time', length(time)});
nccreate(OutputFiles.box, 'Ekman', ...
    'Dimensions', {'time', length(time)});
nccreate(OutputFiles.box, 'deepwaterS', ...
    'Dimensions', {'time', length(time)});
nccreate(OutputFiles.box, 'Fws', ...
    'Dimensions', {'time', length(time)});
nccreate(OutputFiles.box, 'Fwn', ...
    'Dimensions', {'latNorth', 2, 'time', length(time)});

ncwriteatt(OutputFiles.box, '/', 'creation_date', datestr(now));
ncwriteatt(OutputFiles.box, '/', 'model', ...
    'CESM2 1 Degree Global Model for CMIP');
ncwriteatt(OutputFiles.box, '/', 'box_limits', boxlimitstr);
ncwriteatt(OutputFiles.box, '/', 'box_params', modelparamsstr);

ncwriteatt(OutputFiles.box, 'box', 'long_name', 'box order N S L D')
ncwriteatt(OutputFiles.box, 'time', 'units', 'days')
ncwriteatt(OutputFiles.box, 'temperature', 'coordinates', 'box time')
ncwriteatt(OutputFiles.box, 'temperature', 'units', 'degrees Celsius')
ncwriteatt(OutputFiles.box, 'salinity', 'coordinates', 'box time')
ncwriteatt(OutputFiles.box, 'salinity', 'units', 'psu')
ncwriteatt(OutputFiles.box, 'density', 'coordinates', 'box time')
ncwriteatt(OutputFiles.box, 'density', 'units', 'kg per m3 at surface')
ncwriteatt(OutputFiles.box, 'Dlow', 'units', 'meters')
ncwriteatt(OutputFiles.box, 'AMOC', 'coordinates', 'time')
ncwriteatt(OutputFiles.box, 'Ekman', 'coordinates', 'time')
ncwriteatt(OutputFiles.box, 'deepwaterS', 'coordinates', 'time')
ncwriteatt(OutputFiles.box, 'Fwn', 'coordinates', 'latNorth time')
ncwriteatt(OutputFiles.box, 'Fws', 'coordinates', 'time')
ncwriteatt(OutputFiles.box, 'AMOC', 'units', 'Sv')
ncwriteatt(OutputFiles.box, 'Ekman', 'units', 'Sv')
ncwriteatt(OutputFiles.box, 'deepwaterS', 'units', 'Sv')
ncwriteatt(OutputFiles.box, 'Fws', 'units', 'Sv')
ncwriteatt(OutputFiles.box, 'Fwn', 'units', 'Sv')
%write
ncwrite(OutputFiles.box, 'time', timeUTC);
ncwrite(OutputFiles.box, 'temperature', T4.');
ncwrite(OutputFiles.box, 'salinity', S4.');
ncwrite(OutputFiles.box, 'density', sigma4.');
ncwrite(OutputFiles.box, 'AMOC', Mn);
ncwrite(OutputFiles.box, 'Dlow', D);
ncwrite(OutputFiles.box, 'Ekman', Mek);
ncwrite(OutputFiles.box, 'deepwaterS', Ms);
ncwrite(OutputFiles.box, 'Fws', Fws);
ncwrite(OutputFiles.box, 'Fwn', Fwn.');

%% done
