addpath '/scratch/tmp/brettge1/'
%files
InFileName_1s = sprintf('b.e21.BHISTcmip6.f09_g17.LE2-1001.001.pop.h.SALT.185001-185912.nc');%salinity (so or SALT)
InFileName_1t = sprintf('b.e21.BHISTcmip6.f09_g17.LE2-1001.001.pop.h.TEMP.185001-185912.nc');%temperature (thetao or TEMP)
InFileName_1v = sprintf('b.e21.BHISTcmip6.f09_g17.LE2-1001.001.pop.h.VVEL.185001-185912.nc');%v velocity (NVEL or VVEL)
InFileName_1 = sprintf('b.e21.BHISTcmip6.f09_g17.LE2-1001.001.pop.h.MOC.185001-185912.nc');%overturning (msftmz or MOC)
FileName_CESMLE='b.e21.BHISTcmip6.f09_g17.LE2-1001.001.pop.h.MOC.185001-185912.nc';%regions, tarea, uarea
CMIP=false;%got from llnl
LE=true;%got from NCAR
SaveZonalMat='zonalmeanBHISTcmip6LE2-1001-001-185001-185912.mat';
SaveZonalA='zonalmeanABHISTcmip6LE2-1001-001-185001-185912.nc';%atlantic
SaveZonalP='zonalmeanPBHISTcmip6LE2-1001-001-185001-185912.nc';%pacific
SaveBoxA='boxBHISTcmip6LE2-1001-001-185001-185912.nc';%atlantic, box style
%box limits
latSouth=-45; %54 drake, 35 aghulas
latNorth=[45 65];
depthH=200;
boxlimitstr='45S 45-65N 200m';
cesmparams='Agm=3000,Aredi=600,Kv=0.16e-4,epsilon=1.4e-4';

%% Add Paths

addpath /fps-nstd-delores/wrf/brettge1/gsw
addpath /fps-nstd-delores/wrf/brettge1/gsw/gsw_matlab_v3_06_11/
addpath /fps-nstd-delores/wrf/brettge1/gsw/gsw_matlab_v3_06_11/library/
addpath /fps-nstd-delores/wrf/brettge1/gsw/gsw_matlab_v3_06_11/thermodynamics_from_t/
 display('GSW Toolbox Paths Added');

%% compute zonal-mean T, S, potential density, pycnocline depth
%lat_degN_1 = ncread(InFileName_1s,'lat'); % nlon,nlat 320x384
%lon_degE_1 = ncread(InFileName_1s,'lon'); % nlon,nlat 320x384
if CMIP
[timeUTC,depth,meanlatTA,meanlonTA,volumeTA,meanlatVA,meanlonVA,volumeVA,meanVA,meanTA,meanSA,meanrho0A,D0A,meanlonTP,meanlatTP,volumeTP,meanlonVP,meanlatVP,volumeVP,meanVP,meanTP,meanSP,meanrho0P,D0P] = zonalVTSrho0(InFileName_1v,InFileName_1t,InFileName_1s,FileName_CESMLE);
elseif LE
[timeUTC,depth,meanlatTA,meanlonTA,volumeTA,meanlatVA,meanlonVA,volumeVA,meanVA,meanTA,meanSA,meanrho0A,D0A,meanlonTP,meanlatTP,volumeTP,meanlonVP,meanlatVP,volumeVP,meanVP,meanTP,meanSP,meanrho0P,D0P] = zonalVTSrho0LE(InFileName_1v,InFileName_1t,InFileName_1s);
end
%% load meridional overturning circulation
%load(SaveZonalMat)
if CMIP
msftmz_kgpersec_1 = ncread(InFileName_1,'msftmz'); % lat,lev,basin,time, Size:       395x61x3x600
depthMOC = ncread(InFileName_1,'lev')/100;
latMOC = ncread(InFileName_1,'lat');
AMOC_Sv = squeeze(msftmz_kgpersec_1(:,:,1,:)/1000000000); %(lat,depth,1=atl_arctic,months)
PMOC_Sv = squeeze(msftmz_kgpersec_1(:,:,2,:)/1000000000);
elseif LE
msftmz_sv_1 = ncread(InFileName_1,'MOC');
depthMOC = ncread(InFileName_1,'moc_z')/100;
latMOC = ncread(InFileName_1,'lat_aux_grid');
AMOC_Sv = squeeze(sum(msftmz_sv_1(:,:,:,2,:),3)); %(lat,depth,1=atl_arctic,months)
PMOC_Sv = squeeze(sum(msftmz_sv_1(:,:,:,1,:),3))-AMOC_Sv;
end
size(AMOC_Sv)
size(PMOC_Sv)
%AMOC_Sv = squeeze(msftmz_kgpersec_1(:,:,1,:)/1000000000); %(lat,depth,1=atl_arctic,months)
%PMOC_Sv = squeeze(msftmz_kgpersec_1(:,:,2,:)/1000000000);

%% save mat
save(SaveZonalMat)

%% save zonal-mean VTSrho0 information out to netcdf, Atlantic
%ncid = netcdf.create(SaveZonalA);%,'NOCLOBBER');
lat=meanlatTA(:,1);
nccreate(SaveZonalA, 'lat', ...
            'Dimensions', {'lat', length(lat)});
nccreate(SaveZonalA, 'time', ...
            'Dimensions', {'time', length(timeUTC)});
nccreate(SaveZonalA, 'depth', ...
            'Dimensions', {'depth', length(depth)});
nccreate(SaveZonalA, 'lon', ...
            'Dimensions', {'lat', length(lat)...
            'depth', length(depth)});
nccreate(SaveZonalA, 'lonV', ...
            'Dimensions', {'lat', length(lat)...
            'depth', length(depth)});
nccreate(SaveZonalA, 'latV', ...
            'Dimensions', {'latV', length(lat)...
            'depth', length(depth)});
nccreate(SaveZonalA, 'latMOC', ...
            'Dimensions', {'latMOC', length(latMOC)...
            'depth', length(depth)});
nccreate(SaveZonalA, 'volume', ...
            'Dimensions', {'lat', length(lat), ...
                       'depth', length(depth)});
nccreate(SaveZonalA, 'volumeV', ...
            'Dimensions', {'lat', length(lat), ...
                       'depth', length(depth)});
nccreate(SaveZonalA, 'meanlat', ...
            'Dimensions', {'lat', length(lat), ...
                       'depth', length(depth)});
nccreate(SaveZonalA, 'temperature', ...
            'Dimensions', {'lat', length(lat), ...
                       'depth', length(depth), ...
                       'time', length(timeUTC)});
nccreate(SaveZonalA, 'salinity', ...
            'Dimensions', {'lat', length(lat), ...
                       'depth', length(depth), ...
                       'time', length(timeUTC)});
nccreate(SaveZonalA, 'potentialDensity', ...
            'Dimensions', {'lat', length(lat), ...
                       'depth', length(depth), ...
                       'time', length(timeUTC)});
nccreate(SaveZonalA, 'velocity', ...
            'Dimensions', {'lat', length(lat), ...
                       'depth', length(depth), ...
                       'time', length(timeUTC)});
nccreate(SaveZonalA, 'MOC', ...
            'Dimensions', {'latMOC', length(latMOC), ...
                       'depth', length(depth), ...
                       'time', length(timeUTC)});
nccreate(SaveZonalA, 'pycnoclineDepth', ...
            'Dimensions', {'lat', length(lat), ...
                       'time', length(timeUTC)});
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
ncwriteatt(SaveZonalA, 'volumeV', 'units', 'm3')
ncwriteatt(SaveZonalA, 'volumeV', 'coordinates','lat depth')
ncwriteatt(SaveZonalA, 'lon', 'coordinates','lat depth')
ncwriteatt(SaveZonalA, 'meanlat', 'coordinates','lat depth')
ncwriteatt(SaveZonalA, 'meanlat', 'units', 'degree_north')
ncwriteatt(SaveZonalA, 'temperature', 'coordinates','lat depth time')
ncwriteatt(SaveZonalA, 'temperature', 'units', 'degrees Celsius')
ncwriteatt(SaveZonalA, 'salinity', 'coordinates','lat depth time')
ncwriteatt(SaveZonalA, 'salinity', 'units', 'psu')
ncwriteatt(SaveZonalA, 'potentialDensity', 'coordinates','lat depth time')
ncwriteatt(SaveZonalA, 'potentialDensity', 'units', 'kg per m3')
ncwriteatt(SaveZonalA, 'velocity', 'coordinates','lat depth time')
ncwriteatt(SaveZonalA, 'velocity', 'units', 'meters per second')
ncwriteatt(SaveZonalA, 'pycnoclineDepth', 'coordinates','lat time')
ncwriteatt(SaveZonalA, 'pycnoclineDepth', 'units', 'meters')

ncwrite(SaveZonalA, 'lon', meanlonTA);
ncwrite(SaveZonalA, 'lonV', meanlonVA);
ncwrite(SaveZonalA, 'time', timeUTC);
ncwrite(SaveZonalA, 'lat', meanlatTA(:,1));
ncwrite(SaveZonalA, 'meanlat', meanlatTA);
ncwrite(SaveZonalA, 'latV', meanlatVA);
ncwrite(SaveZonalA, 'volume', volumeTA);
ncwrite(SaveZonalA, 'volumeV', volumeVA);
ncwrite(SaveZonalA, 'temperature', meanTA);
ncwrite(SaveZonalA, 'salinity', meanSA);
ncwrite(SaveZonalA, 'velocity', meanVA);
ncwrite(SaveZonalA, 'potentialDensity', meanrho0A);
ncwrite(SaveZonalA, 'pycnoclineDepth', D0A);

%% write Pacific
%Read the variable, dimension, and group definitions from the file using ncinfo. This information defines the file's schema.
S = ncinfo(SaveZonalA);
%create pacific file with all the same formatting
ncwriteschema(SaveZonalP,S)
ncwrite(SaveZonalP, 'lon', meanlonTP);
ncwrite(SaveZonalP, 'lonV', meanlonVP);
ncwrite(SaveZonalP, 'time', timeUTC);
ncwrite(SaveZonalP, 'lat', meanlatTP(:,1));
ncwrite(SaveZonalP, 'meanlat', meanlatTP);
ncwrite(SaveZonalP, 'latV', meanlatVP);
ncwrite(SaveZonalP, 'volume', volumeTP);
ncwrite(SaveZonalP, 'volumeV', volumeVP);
ncwrite(SaveZonalP, 'temperature', meanTP);
ncwrite(SaveZonalP, 'salinity', meanSP);
ncwrite(SaveZonalP, 'velocity', meanVP);
ncwrite(SaveZonalP, 'potentialDensity', meanrho0P);
ncwrite(SaveZonalP, 'pycnoclineDepth', D0P);


%% zonal to box, Atlantic
[T4,S4,sigma4,D,Mn,Mek,Ms] = zonal2box(latNorth,latSouth,depthH,depth,meanlatTA,volumeTA,meanTA,meanSA,meanrho0A,D0A,AMOC_Sv);
dyu=ncread(FileName_CESMLE,'DYU')./100;%cm to meters, y-spacing
size(Mn)
size(Mek)
size(Ms)
%
[Fwn] = freshwaterfluxN(latNorth,depth,meanlatTA,meanSA,meanlatVA,volumeVA,meanVA,dyu);
[Fws] = freshwaterfluxS(latSouth,depth,meanlatTP,meanSP,meanlatVP,volumeVP,meanVP,dyu);

FwintoS=-Fws;
FwintoN=Fwn(:,1)-Fwn(:,2);
%% save box information out to netcdf
%ncid = netcdf.create(SaveBoxA,'NOCLOBBER');
time=timeUTC;
size(time)
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
nccreate(SaveBoxA, 'Dlow', ...
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
ncwriteatt(SaveBoxA, '/', 'box_limits', boxlimitstr);
ncwriteatt(SaveBoxA, '/', 'box_params', cesmparams);

ncwriteatt(SaveBoxA, 'box', 'long_name', 'box order N S L D')
ncwriteatt(SaveBoxA, 'time', 'units', 'days')
ncwriteatt(SaveBoxA, 'temperature', 'coordinates','box time')
ncwriteatt(SaveBoxA, 'temperature', 'units', 'degrees Celsius')
ncwriteatt(SaveBoxA, 'salinity', 'coordinates','box time')
ncwriteatt(SaveBoxA, 'salinity', 'units', 'psu')
ncwriteatt(SaveBoxA, 'density', 'coordinates','box time')
ncwriteatt(SaveBoxA, 'density', 'units', 'kg per m3 at surface')
ncwriteatt(SaveBoxA, 'Dlow', 'units', 'meters')
ncwriteatt(SaveBoxA, 'AMOC', 'coordinates', 'time')
ncwriteatt(SaveBoxA, 'Ekman', 'coordinates', 'time')
ncwriteatt(SaveBoxA, 'deepwaterS', 'coordinates', 'time')
ncwriteatt(SaveBoxA, 'Fwn', 'coordinates', 'latNorth time')
ncwriteatt(SaveBoxA, 'Fws', 'coordinates', 'time')
ncwriteatt(SaveBoxA, 'AMOC', 'units', 'Sv')
ncwriteatt(SaveBoxA, 'Ekman', 'units', 'Sv')
ncwriteatt(SaveBoxA, 'deepwaterS', 'units', 'Sv')
ncwriteatt(SaveBoxA, 'Fws', 'units', 'Sv')
ncwriteatt(SaveBoxA, 'Fwn', 'units', 'Sv')
%write
ncwrite(SaveBoxA, 'time', timeUTC);
ncwrite(SaveBoxA, 'temperature', T4.');
ncwrite(SaveBoxA, 'salinity', S4.');
ncwrite(SaveBoxA, 'density', sigma4.');
ncwrite(SaveBoxA, 'AMOC', Mn);
ncwrite(SaveBoxA, 'Dlow', D);
ncwrite(SaveBoxA, 'Ekman', Mek);
ncwrite(SaveBoxA, 'deepwaterS', Ms);
ncwrite(SaveBoxA, 'Fws', Fws);
ncwrite(SaveBoxA, 'Fwn', Fwn.');
%% done

