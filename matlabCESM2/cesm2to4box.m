
%files
InFileName_1s = sprintf('so_Omon_CESM2_ssp126-ssp370Lu_r3i1p1f1_gn_201501-206412.nc');
InFileName_1t = sprintf('thetao_Omon_CESM2_ssp126-ssp370Lu_r3i1p1f1_gn_201501-206412.nc');
InFileName_1v = sprintf('.nc');
InFileName_1 = sprintf('msftmz_Omon_CESM2_ssp126-ssp370Lu_r3i1p1f1_gn_201501-206412.nc');%amoc
FileName_CESMLE='b.e21.BHISTcmip6.f09_g17.LE2-1001.001.pop.h.MOC.185001-185912.nc';
SaveZonalA='zonalmeanAssp126-ssp370Lu_r3i1p1f1_gn_201501-206412.nc';
SaveZonalP='zonalmeanPssp126-ssp370Lu_r3i1p1f1_gn_201501-206412.nc';
SaveBoxA='boxssp126-ssp370Lu_r3i1p1f1_gn_201501-206412.nc';
%box limits
latSouth=-55;
latNorth=[45 65];
depthH=200;

% Add Paths
% addpath /fps-nstd-delores/wrf/brettge1/gsw
% addpath /fps-nstd-delores/wrf/brettge1/gsw/gsw_matlab_v3_06_11/
% addpath /fps-nstd-delores/wrf/brettge1/gsw/gsw_matlab_v3_06_11/library/
% addpath /fps-nstd-delores/wrf/brettge1/gsw/gsw_matlab_v3_06_11/thermodynamics_from_t/

root_dir = '\\dom1\Core\Dept\FPS\Groups\KTF\Brett\PACMANS\Mar_11\RHO_2015_2100\';
addpath(fullfile(root_dir,'functions','gsw_matlab_v3_06_11'));
addpath(fullfile(root_dir,'functions','gsw_matlab_v3_06_11','library'));
addpath(fullfile(root_dir,'functions','gsw_matlab_v3_06_11','thermodynamics_from_t'));
 display('GSW Toolbox Paths Added');

%% compute zonal-mean T, S, potential density, pycnocline depth
lat_degN_1 = ncread(InFileName_1s,'lat'); % nlon,nlat 320x384
lon_degE_1 = ncread(InFileName_1s,'lon'); % nlon,nlat 320x384

[timeUTC,depth,meanlatA,meanlonA,volumeA,meanTA,meanSA,meanrho0A,D0A,meanlonP,meanlatP,volumeP,meanTP,meanSP,meanrho0P,D0P] = zonalTSrho0(InFileName_1t,InFileName_1s,FileName_CESMLE);


%% save zonal-mean TSrho0 information out to netcdf
ncid = netcdf.create(SaveZonalA,'NOCLOBBER');
nccreate(SaveZonalA, 'lat', ...
             'Dimensions', {'lat', length(meanlatA)});
nccreate(SaveZonalA, 'time', ...
             'Dimensions', {'time', length(timeUTC)});
nccreate(SaveZonalA, 'depth', ...
             'Dimensions', {'depth', length(depth)});
nccreate(SaveZonalA, 'lon', ...
             'Dimensions', {'lat', length(meanlatA)...
             'depth', length(depth)});
nccreate(SaveZonalA, 'volume', ...
             'Dimensions', {'lat', length(lat), ...
                        'depth', length(depth)});
nccreate(SaveZonalA, 'meanlat', ...
             'Dimensions', {'lat', length(lat), ...
                        'depth', length(depth)});
nccreate(SaveZonalA, 'temperature', ...
             'Dimensions', {'lat', length(lat), ...
                        'depth', length(depth)
                        'time', length(time)});
nccreate(SaveZonalA, 'salinity', ...
             'Dimensions', {'lat', length(lat), ...
                        'depth', length(depth)
                        'time', length(time)});
nccreate(SaveZonalA, 'potentialDensity', ...
             'Dimensions', {'lat', length(lat), ...
                        'depth', length(depth)
                        'time', length(time)});
nccreate(SaveZonalA, 'pycnoclineDepth', ...
             'Dimensions', {'lat', length(lat), ...
                        'depth', length(depth)});
ncwriteatt(SaveZonalA, 'lon', 'long_name', 'longitude')
ncwriteatt(SaveZonalA, 'lon', 'units', 'degree_east')
ncwriteatt(SaveZonalA, 'lon', 'standard_name', 'longitude')

ncwriteatt(SaveZonalA, 'lat', 'long_name', 'latitude')
ncwriteatt(SaveZonalA, 'lat', 'units', 'degree_north')
ncwriteatt(SaveZonalA, 'lat', 'standard_name', 'latitude')
ncwriteatt(SaveZonalA, 'time', 'units', 'days')
ncwriteatt(SaveZonalA, '/', 'creation_date', datestr(now));
ncwriteatt(SaveZonalA, '/', 'model', ...
           'CESM2 1 Degree Global Model for CMIP');
ncwriteatt(SaveZonalA, 'volume', 'units', 'm3')
ncwriteatt(SaveZonalA, 'volume', 'coordinates','lat depth')
ncwriteatt(SaveZonalA, 'lon', 'coordinates','lat depth')
ncwriteatt(SaveZonalA, 'meanlat', 'coordinates','lat depth')
ncwriteatt(SaveZonalA, 'meanlat', 'units', 'degree_north')
ncwriteatt(SaveZonalA, 'temperature', 'coordinates','lat depth time')
ncwriteatt(SaveZonalA, 'temperature', 'units', 'degrees Celsius')
ncwriteatt(SaveZonalA, 'salinity', 'coordinates','lat depth time')
ncwriteatt(SaveZonalA, 'salinity', 'units', 'psu')
ncwriteatt(SaveZonalA, 'potentialDensity', 'coordinates','lat depth time')
ncwriteatt(SaveZonalA, 'potentialDensity', 'units', 'kg per m3')
ncwriteatt(SaveZonalA, 'pycnoclineDepth', 'coordinates','lat time')
ncwriteatt(SaveZonalA, 'pycnoclineDepth', 'units', 'meters')

ncwrite(SaveZonalA, 'lon', meanlonA);
ncwrite(SaveZonalA, 'time', timeUTC);
ncwrite(SaveZonalA, 'lat', meanlatA(:,1));
ncwrite(SaveZonalA, 'meanlat', meanlatA);
ncwrite(SaveZonalA, 'volume', volumeA);
ncwrite(SaveZonalA, 'temperature', meanTA);
ncwrite(SaveZonalA, 'salinity', meanSA);
ncwrite(SaveZonalA, 'potentialDensity', meanrho0A);
ncwrite(SaveZonalA, 'pycnoclineDepth', D0A);

%Read the variable, dimension, and group definitions from the file using ncinfo. This information defines the file's schema.
S = ncinfo(SaveZonalA);
%create pacific file with all the same formatting
ncwriteschema(SaveZonalP,S)
ncwrite(SaveZonalP, 'lon', meanlonP);
ncwrite(SaveZonalP, 'time', timeUTC);
ncwrite(SaveZonalP, 'lat', meanlatP(:,1));
ncwrite(SaveZonalP, 'meanlat', meanlatP);
ncwrite(SaveZonalP, 'volume', volumeP);
ncwrite(SaveZonalP, 'temperature', meanTP);
ncwrite(SaveZonalP, 'salinity', meanSP);
ncwrite(SaveZonalP, 'potentialDensity', meanrho0P);
ncwrite(SaveZonalP, 'pycnoclineDepth', D0P);
%% compute zonal-mean northward velocities and load MOC
[timeUTCv,depthv,meanlatAv,meanlonAv,volumeAv,meanVA,meanlonPv,meanlatPv,volumePv,meanVP] = zonalV(InFileName_1v,FileName_CESMLE);
msftmz_kgpersec_1 = ncread(InFileName_1,'msftmz'); % lat,lev,basin,time, Size:       395x61x3x600
AMOC_Sv = squeeze(msftmz_kgpersec_1(:,:,1,:)/1000000000); %(lat,depth,1=atl_arctic,months)
PMOC_Sv = squeeze(msftmz_kgpersec_1(:,:,2,:)/1000000000);
depthMOC = ncread(InFileName_1,'lev')/100;
latMOC = ncread(InFileName_1,'lat');

%% save zonal-mean northward velocities to netcdf

%% zonal to box, Atlantic
[T4,S4,sigma4,D,Mn,Mek,Ms] = zonal2box(latNorth,latSouth,depthH,depth,meanlatA,volumeA,meanTA,meanSA,meanrho0A,D0A,AMOC_Sv);
[Fws,Fwn] = freshwaterflux(latNorth,latSouth,depthH,depth,meanlatA,volumeA,meanSA,meanlatAv,meanVA);
%% save box information out to netcdf
ncid = netcdf.create(SaveBoxA,'NOCLOBBER');
nccreate(SaveBoxA, 'time', ...
             'Dimensions', {'time', length(timeUTC)});
nccreate(SaveBoxA, 'box', ...
             'Dimensions', {'box', 4});
nccreate(SaveBoxA, 'latNorth', ...
             'Dimensions', {'latNorth', 2});
nccreate(SaveBoxA, 'temperature', ...
             'Dimensions', {'box', 4, ...
                        'time', length(time)});
nccreate(SaveBoxA, 'salinity', ...
             'Dimensions', {'box', 4, ...
                        'time', length(time)});
nccreate(SaveBoxA, 'density', ...
             'Dimensions', {'box', 4, ...
                        'time', length(time)});
nccreate(SaveBoxA, 'AMOC', ...
             'Dimensions', {'time', length(time)});
nccreate(SaveBoxA, 'Ekman', ...
             'Dimensions', {'time', length(time)});
nccreate(SaveBoxA, 'deepwaterS', ...
             'Dimensions', {'time', length(time)});
nccreate(SaveBoxA, 'Fws', ...
             'Dimensions', {'time', length(time)});
nccreate(SaveBoxA, 'Fwn', ...
             'Dimensions', {'latNorth',2,'time', length(time)});

ncwriteatt(SaveBoxA, '/', 'creation_date', datestr(now));
ncwriteatt(SaveBoxA, '/', 'model', ...
           'CESM2 1 Degree Global Model for CMIP');

ncwriteatt(SaveBoxA, 'box', 'long_name', 'box order N S L D')
ncwriteatt(SaveBoxA, 'time', 'units', 'days')
ncwriteatt(SaveBoxA, 'temperature', 'coordinates','box time')
ncwriteatt(SaveBoxA, 'temperature', 'units', 'degrees Celsius')
ncwriteatt(SaveBoxA, 'salinity', 'coordinates','box time')
ncwriteatt(SaveBoxA, 'salinity', 'units', 'psu')
ncwriteatt(SaveBoxA, 'potentialDensity', 'coordinates','box time')
ncwriteatt(SaveBoxA, 'potentialDensity', 'units', 'kg per m3')
ncwriteatt(SaveBoxA, 'AMOC', 'units', 'Sv')
ncwriteatt(SaveBoxA, 'Ekman', 'units', 'Sv')
ncwriteatt(SaveBoxA, 'deepwaterS', 'units', 'Sv')
ncwriteatt(SaveBoxA, 'Fws', 'units', 'Sv')
ncwriteatt(SaveBoxA, 'Fwn', 'units', 'Sv')

ncwrite(SaveBoxA, 'time', timeUTC);
ncwrite(SaveBoxA, 'temperature', T4);
ncwrite(SaveBoxA, 'salinity', S4);
ncwrite(SaveBoxA, 'potentialDensity', sigma4);
ncwrite(SaveBoxA, 'AMOC', Mn);
ncwrite(SaveBoxA, 'Ekman', Mek);
ncwrite(SaveBoxA, 'deepwaterS', Ms);
ncwrite(SaveBoxA, 'Fws', Mn);
ncwrite(SaveBoxA, 'Fwn', Fwn);
%% done