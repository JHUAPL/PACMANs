% Copyright 2022, The Johns Hopkins University Applied Physics Laboratory LLC
% All rights reserved.
% Distributed under the terms of the BSD 3-Clause License.

function [timeUTC, depth, Atlantic, Pacific] = zonalVTSrho0set(InputFiles)
% zonal averaging of CESM2 output files:
% zonalTSrho0 reads .nc T,S,V files by latitude, computes rho0, the potential
% density, using the gsw toolbox, averages zonally in the Atlantic and
% Pacific, and returns the time, depth, and  
% Atlantic and Pacific contain zonal-mean latitude (latT for tracers, 
% latV for velocities), longitude (lonT for tracers, latT for velocities),
% tracer volume (volumeT), velocity volume (volumeV), 
% northward velocity (velN), temperature (temp), salinity (salt), 
% potential density (rho0),
% and integrated density anomaly D0 (for pycnocline depth)

source = InputFiles.source; %'LE' from NCAR or 'CMIP' from llnl cmip archive
lowmemory = InputFiles.lowmemory; %1 for laptop, 0 for cluster

time_days_since_01Jan0000 = ncread(InputFiles.salt, 'time');
% time is number of days since 0000-01-01 00:00:00'
time_on_01Jan0000 = datenum(0000, 1, 1, 0, 0, 0); 
% = matlab time as datenum is number of days
timeUTC = time_on_01Jan0000 + (time_days_since_01Jan0000); 
% matlab time in days, i.e.datenum
nt = length(timeUTC);

switch source
    case 'LE'
        lat_degN_1 = ncread(InputFiles.salt, 'TLAT'); % nlon,nlat 320x384
        lon_degE_1 = ncread(InputFiles.salt, 'TLONG'); % nlon,nlat 320x384
        depth = ncread(InputFiles.salt, 'z_t') / 100; % depth (m)
        [ny, nx] = size(lat_degN_1);
        nz = length(depth);
        lat_degN_1v = ncread(InputFiles.velN, 'ULAT'); % nlon,nlat 320x384
        lon_degE_1v = ncread(InputFiles.velN, 'ULONG'); % nlon,nlat 320x384
    case 'CMIP'
        lat_degN_1 = ncread(InputFiles.salt, 'lat'); % nlon,nlat 320x384
        lon_degE_1 = ncread(InputFiles.salt, 'lon'); % nlon,nlat 320x384
        depth = ncread(InputFiles.salt, 'lev') / 100; % depth (m)
        [nx, ny] = size(lat_degN_1); %need to check order here!!!
        nz = length(depth);
        lat_degN_1v = ncread(InputFiles.velN, 'lat'); % nlon,nlat 320x384
        lon_degE_1v = ncread(InputFiles.velN, 'lon'); % nlon,nlat 320x384
end

dedge = depth(1:end-1) + 0.5 * diff(depth); %depth_m_1 is the cell center; 
% finding the edges to make dz
dedge = cat(1, 0, dedge, depth(end)+0.5*(depth(end) - depth(end-1)));
dz = diff(dedge.'); %m


regions = ncread(InputFiles.grid, 'REGION_MASK');
tarea = ncread(InputFiles.grid, 'TAREA') ./ 1e4; %cm^2-->m^2
uarea = ncread(InputFiles.grid, 'UAREA') ./ 1e4;

Atlantic.velN = zeros(ny, nz, nt);
Atlantic.salt = zeros(ny, nz, nt);
Atlantic.temp = zeros(ny, nz, nt);
Atlantic.rho0 = zeros(ny, nz, nt);
Atlantic.lonT = zeros(ny, nz);
Atlantic.latT = zeros(ny, nz);
Atlantic.volumeT = zeros(ny, nz);
Atlantic.lonV = zeros(ny, nz);
Atlantic.latV = zeros(ny, nz);
Atlantic.volumeV = zeros(ny, nz);
Pacific.velN = zeros(ny, nz, nt);
Pacific.salt = zeros(ny, nz, nt);
Pacific.temp = zeros(ny, nz, nt);
Pacific.rho0 = zeros(ny, nz, nt);
Pacific.lonT = zeros(ny, nz);
Pacific.latT = zeros(ny, nz);
Pacific.volumeT = zeros(ny, nz);
Pacific.lonV = zeros(ny, nz);
Pacific.latV = zeros(ny, nz);
Pacific.volumeV = zeros(ny, nz);

for ii = 1:ny
    ii %comment this out if you do not want to output ii to display/log
    start = [1, ii, 1, 1]; % [lon,lat,depth,monthly time], 
    % start location along each coordinate
    count = [Inf, 1, Inf, nt]; % read number of elements in each dimension.
    % INf = read until the end of each dimension
    stride = [1, 1, 1, 1]; 
    % read variable data at intervals specified in stride

    if ~lowmemory
        switch source
            case 'LE'
        hold_SAL_all = squeeze(ncread(InputFiles.salt, 'SALT', start, count, stride));
        % (lon, lat, depth, monthly time) 320x1x60x600
        hold_T_all = squeeze(ncread(InputFiles.temp, 'TEMP', start, count, stride));
        hold_V_all = squeeze(ncread(InputFiles.velN, 'VVEL', start, count, stride)) ./ 100; 
        %cm/s-->m/s
            case 'CMIP'
        hold_SAL_all = squeeze(ncread(InputFiles.salt, 'so', start, count, stride)); 
        % (lon, lat, depth, monthly time) 320x1x1x600
        hold_T_all = squeeze(ncread(InputFiles.temp, 'thetao', start, count, stride));
        hold_V_all = squeeze(ncread(InputFiles.velN, 'vo', start, count, stride));

        end
    end

    for jj = 1:nz
        if lowmemory
            count = [Inf, 1, 1, nt];
            switch source
                case 'CMIP'
            hold_SAL = squeeze(ncread(InputFiles.salt, 'so', start, count, stride)); 
            % (lon, lat, depth, monthly time) 320x1x1x600
            hold_T = squeeze(ncread(InputFiles.temp, 'thetao', start, count, stride));
            hold_V = squeeze(ncread(InputFiles.velN, 'vo', start, count, stride));
                case 'LE'
            hold_SAL = squeeze(ncread(InputFiles.salt, 'SALT', start, count, stride));
            % (lon, lat, depth, monthly time) 320x1x60x600
            hold_T = squeeze(ncread(InputFiles.temp, 'TEMP', start, count, stride));
            hold_V = squeeze(ncread(InputFiles.velN, 'VVEL', start, count, stride)) ./ 100; %cm/s-->m/s
            end
        else
            hold_SAL = squeeze(hold_SAL_all(:, jj, :));
            hold_T = squeeze(hold_T_all(:, jj, :));
            hold_V = squeeze(hold_V_all(:, jj, :));
        end

        hold_region = regions(:, ii);
        hold_lon = lon_degE_1(:, ii);
        hold_lonv = lon_degE_1v(:, ii);
        iwant = (hold_region == 6) | (hold_region == 8) | (hold_region == 9);
        iwantv = iwant;
        if sum(iwant) == 0
            iwant = hold_lon < 22.5 | hold_lon > 292.4;
            iwantv = hold_lonv < 22.5 | hold_lonv > 292.4;
        end
        iwant(hold_SAL == 0) = 0;
        iwant(isnan(hold_SAL)) = 0;

        iwantv(isnan(hold_V)) = 0;
        Atlantic.volumeT(ii, jj) = nansum(dz(jj)*tarea(iwant, ii));
        Atlantic.volumeV(ii, jj) = nansum(dz(jj)*uarea(iwantv, ii));
        Atlantic.velN(ii, jj, :) = nansum(hold_V(iwantv, :)*dz(jj).*...
            repmat(uarea(iwantv, ii), 1, count(4)), 1) ./ Atlantic.volumeV(ii, jj);
        Atlantic.salt(ii, jj, :) = nansum(hold_SAL(iwant, :)*dz(jj).*...
            repmat(tarea(iwant, ii), 1, count(4)), 1) ./ Atlantic.volumeT(ii, jj);
        Atlantic.temp(ii, jj, :) = nansum(hold_T(iwant, :)*dz(jj).*...
            repmat(tarea(iwant, ii), 1, count(4)), 1) ./ Atlantic.volumeT(ii, jj);
        Atlantic.latT(ii, jj) = nansum(lat_degN_1(iwant, ii).*...
            tarea(iwant, ii)) ./ nansum(tarea(iwant, ii));
        holdlon = lon_degE_1(iwant, ii);
        holdlon(holdlon < 180) = holdlon(holdlon < 180) + 360;
        Atlantic.lonT(ii, jj) = nansum(holdlon.*tarea(iwant, ii)) ./...
            nansum(tarea(iwant, ii));

        Atlantic.latV(ii, jj) = nansum(lat_degN_1v(iwantv, ii).*...
            tarea(iwantv, ii)) ./ nansum(tarea(iwantv, ii));
        holdlon = lon_degE_1v(iwantv, ii);
        holdlon(holdlon < 180) = holdlon(holdlon < 180) + 360;
        Atlantic.lonV(ii, jj) = nansum(holdlon.*tarea(iwantv, ii)) ...
            ./ nansum(tarea(iwantv, ii));

        %density
        P = gsw_p_from_z(-depth(jj)*ones(sum(iwant), 1), lat_degN_1(iwant, ii)); 
        % pressure(decibars); 1 decibar = 1 meter of seawater
        SA = gsw_SA_from_SP(hold_SAL(iwant, :), P, lon_degE_1(iwant, ii), ...
            lat_degN_1(iwant, ii)); 
        % Absolute Salinity (g/kg)
        CT = gsw_CT_from_pt(SA, hold_T(iwant, :)); 
        % Conservative Temperature (deg C)
         rho0 = gsw_rho(SA, CT, 0); %potential density
         Atlantic.rho0(ii, jj, :) = nansum(rho0*dz(jj).*...
             repmat(tarea(iwant, ii), 1, count(4)), 1) ./...
             Atlantic.volumeT(ii, jj); %potential density
        % code commented out for other versions of density
        % rho = gsw_rho(SA,CT,P); % Density (kg/m^3) insitu
        % rho2k = gsw_rho(SA,CT,2000); %density referenced to 2000m
        %insitu density
        % meanrho(ii,jj,:)=nansum(rho*dz(jj).*repmat(tarea(iwant,ii),1,count(4)),1)./volume1(ii,jj); 
        %density referenced to 2000m
        % meanrho2k(ii,jj,:)=nansum(rho2k*dz(jj).*repmat(tarea(iwant,ii),1,count(4)),1)./volume1(ii,jj); 
        

        %Pacific
        iwant = (hold_region == 1) | (hold_region == 2);
        iwantv = iwant;
        if sum(iwant) == 0
            iwant = hold_lon > 140 | hold_lon < 250;
            iwantv = hold_lonv > 140 | hold_lonv < 250;
        end
        iwant(hold_SAL == 0) = 0;
        iwant(isnan(hold_SAL)) = 0;

        iwantv(isnan(hold_V)) = 0;
        Pacific.volumeT(ii, jj) = nansum(dz(jj)*tarea(iwant, ii));
        Pacific.volumeV(ii, jj) = nansum(dz(jj)*uarea(iwantv, ii));
        Pacific.velN(ii, jj, :) = nansum(hold_V(iwantv, :)*dz(jj).*...
            repmat(tarea(iwantv, ii), 1, count(4)), 1) ./ Pacific.volumeV(ii, jj);
        Pacific.salt(ii, jj, :) = nansum(hold_SAL(iwant, :)*dz(jj).*...
            repmat(tarea(iwant, ii), 1, count(4)), 1) ./ Pacific.volumeT(ii, jj);
        Pacific.temp(ii, jj, :) = nansum(hold_T(iwant, :)*dz(jj).*...
            repmat(tarea(iwant, ii), 1, count(4)), 1) ./ Pacific.volumeT(ii, jj);
        Pacific.latT(ii, jj) = nansum(lat_degN_1(iwant, ii).*...
            tarea(iwant, ii)) ./ nansum(tarea(iwant, ii));
        holdlon = lon_degE_1(iwant, ii);
        holdlon(holdlon < 180) = holdlon(holdlon < 180) + 360;
        Pacific.lonT(ii, jj) = nansum(holdlon.*tarea(iwant, ii)) ./...
            nansum(tarea(iwant, ii));

        Pacific.latV(ii, jj) = nansum(lat_degN_1v(iwantv, ii).*...
            tarea(iwantv, ii)) ./ nansum(tarea(iwantv, ii));
        holdlon = lon_degE_1v(iwantv, ii);
        holdlon(holdlon < 180) = holdlon(holdlon < 180) + 360;
        Pacific.lonV(ii, jj) = nansum(holdlon.*tarea(iwantv, ii)) ./...
            nansum(tarea(iwantv, ii));

        %density
        P = gsw_p_from_z(-depth(jj)*ones(sum(iwant), 1), lat_degN_1(iwant, ii)); 
        % pressure(decibars); 1 decibar = 1 meter of seawater
        SA = gsw_SA_from_SP(hold_SAL(iwant, :), P, lon_degE_1(iwant, ii), ...
            lat_degN_1(iwant, ii)); 
        % Absolute Salinity (g/kg)
        CT = gsw_CT_from_pt(SA, hold_T(iwant, :)); 
        % Conservative Temperature (deg C)
        rho0 = gsw_rho(SA, CT, 0); %potential density
        Pacific.rho0(ii, jj, :) = nansum(rho0*dz(jj).*...
            repmat(tarea(iwant, ii), 1, count(4)), 1) ./ ...
            Pacific.volumeT(ii, jj); %density referenced to 2000m

    end

end

    Atlantic.D0 = squeeze(nansum((Atlantic.rho0 - max(Atlantic.rho0, [], 2)).*...
        repmat(dz.*-depth_m_1.', ny, 1), 2)./...
        nansum((Atlantic.rho0 - max(Atlantic.rho0, [], 2)).*...
        repmat(dz, ny, 1), 2)); %from potential density
    Pacific.D0 = squeeze(nansum((Pacific.rho0 - max(Pacific.rho0, [], 2)).*...
        repmat(dz.*-depth_m_1.', ny, 1), 2)./...
        nansum((Pacific.rho0 - max(Pacific.rho0, [], 2)).*...
        repmat(dz, ny, 1), 2)); %from potential density

end
