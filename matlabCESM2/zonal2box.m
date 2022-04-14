% Copyright 2022, The Johns Hopkins University Applied Physics Laboratory LLC
% All rights reserved.
% Distributed under the terms of the BSD 3-Clause License.
function [T4, S4, sigma4, D, Mn, Mek, Ms] = zonal2box(coordinates, depth, Atlantic, Pacific, AMOCsv)
% zonal2box averages Atlantic and Pacific zonal-mean temperature, salinity,
% and potential density into 4 boxes as limited by the values in
% coordinates. It also computes the northern and southern mass fluxes from
% AMOCsv, making Mn, Mek, Ms. Finally, it uses the integrated density
% anomaly, Atlantic.D0, to compute the pycnocline depth, D.


ni = find(Atlantic.latT(:, 1) > coordinates.latNorth1, 1, 'first');
ni2 = find(Atlantic.latT(:, 1) < coordinates.latNorth2, 1, 'last');
si = find(Pacific.latT(:, 1) < coordinates.latSouth, 1, 'last');
hdi = find(depth < coordinates.depthH, 1, 'last');
[ny, nt] = size(Atlantic.D0);

Atlantic.salt(Atlantic.salt == 0) = NaN;
D0L = squeeze(nansum(Atlantic.D0(si+1:ni-1, :).*...
    repmat(sum(Atlantic.volumeT(si+1:ni-1, :), 2), [1, nt]), 1)) ./ ...
    sum(Atlantic.volumeT(si+1:ni-1, :), [1, 2]); %
salN = squeeze(nansum(Atlantic.salt(ni:ni2, 1:hdi, :).*...
    repmat(Atlantic.volumeT(ni:ni2, 1:hdi), [1, 1, nt]), [1, 2])) ./ ...
    sum(Atlantic.volumeT(ni:ni2, 1:hdi), [1, 2]); %north
tempN = squeeze(nansum(Atlantic.temp(ni:ni2, 1:hdi, :).*...
    repmat(Atlantic.volumeT(ni:ni2, 1:hdi), [1, 1, nt]), [1, 2])) ./ ...
    sum(Atlantic.volumeT(ni:ni2, 1:hdi), [1, 2]); %north
sigmaN = squeeze(nansum(Atlantic.rho0(ni:ni2, 1:hdi, :).*...
    repmat(Atlantic.volumeT(ni:ni2, 1:hdi), [1, 1, nt]), [1, 2])) ./ ...
    sum(Atlantic.volumeT(ni:ni2, 1:hdi), [1, 2]) - 1000; %north

salS = squeeze(nansum(Pacific.salt(1:si, 1:hdi, :).*...
    repmat(Pacific.volumeT(1:si, 1:hdi), [1, 1, nt]), [1, 2])) ./ ...
    sum(Pacific.volumeT(1:si, 1:hdi), [1, 2]); %south
tempS = squeeze(nansum(Pacific.temp(1:si, 1:hdi, :).*...
    repmat(Pacific.volumeT(1:si, 1:hdi), [1, 1, nt]), [1, 2])) ./ ...
    sum(Pacific.volumeT(1:si, 1:hdi), [1, 2]); %south
sigmaS = squeeze(nansum(Pacific.rho0(1:si, 1:hdi, :).*...
    repmat(Pacific.volumeT(1:si, 1:hdi), [1, 1, nt]), [1, 2])) ./ ...
    sum(Pacific.volumeT(1:si, 1:hdi), [1, 2]) - 1000; %south

%depth is the cell center; finding the edges
dedge = depth(1:end-1) + 0.5 * diff(depth); 
dedge = cat(1, 0, dedge, depth(end)+0.5*(depth(end) - depth(end-1)));


for timei = 1:nt
%the index for the cell center whose bottom edge is above the mean pycnocline depth
    ldi = find(-dedge > D0L(timei), 1, 'last') - 1; 
    if ldi < hdi
        ldi = hdi + 1;
    end


    salL(timei) = squeeze(nansum(Atlantic.salt(si+1:ni-1, 1:ldi, timei).*...
        Atlantic.volumeT(si+1:ni-1, 1:ldi), [1, 2])) ./ ...
        sum(Atlantic.volumeT(si+1:ni-1, 1:ldi), [1, 2]); %low lat
    tempL(timei) = squeeze(nansum(Atlantic.temp(si+1:ni-1, 1:ldi, timei).*...
        Atlantic.volumeT(si+1:ni-1, 1:ldi), [1, 2])) ./ ...
        sum(Atlantic.volumeT(si+1:ni-1, 1:ldi), [1, 2]); %low lat
    sigmaL(timei) = squeeze(nansum(Atlantic.rho0(si+1:ni-1, 1:ldi, timei).*...
        Atlantic.volumeT(si+1:ni-1, 1:ldi), [1, 2])) ./ ...
        sum(Atlantic.volumeT(si+1:ni-1, 1:ldi), [1, 2]) - 1000; %low lat

    % deep box via 3 portions
    % northern, depthH to bottom
    vd1 = sum(Atlantic.volumeT(ni:end, hdi+1:end), [1, 2]);
    sald1 = squeeze(nansum(Atlantic.salt(ni:end, hdi+1:end, timei).*...
        Atlantic.volumeT(ni:end, hdi+1:end), [1, 2])) ./ vd1; 
    td1 = squeeze(nansum(Atlantic.temp(ni:end, hdi+1:end, timei).*...
        Atlantic.volumeT(ni:end, hdi+1:end), [1, 2])) ./ vd1; 
    sd1 = squeeze(nansum(Atlantic.rho0(ni:end, hdi+1:end, timei).*...
        Atlantic.volumeT(ni:end, hdi+1:end), [1, 2])) ./ vd1 - 1000; 
    
    % southern, depthH to bottom
    vd2 = sum(Pacific.volumeT(1:si, hdi+1:end), [1, 2]);
    sald2 = squeeze(nansum(Pacific.salt(1:si, hdi+1:end, timei).*...
        Pacific.volumeT(1:si, hdi+1:end), [1, 2])) ./ vd2; 
    td2 = squeeze(nansum(Pacific.temp(1:si, hdi+1:end, timei).*...
        Pacific.volumeT(1:si, hdi+1:end), [1, 2])) ./ vd1; 
    sd2 = squeeze(nansum(Pacific.rho0(1:si, hdi+1:end, timei).*...
        Pacific.volumeT(1:si, hdi+1:end), [1, 2])) ./ vd1 - 1000; 

    % below low-latitude box
    vd3 = sum(Atlantic.volumeT(si+1:ni-1, ldi+1:end), [1, 2]);
    sald3 = squeeze(nansum(Atlantic.salt(si+1:ni-1, ldi+1:end, timei).*...
        Atlantic.volumeT(si+1:ni-1, ldi+1:end), [1, 2])) ./ vd3; 
    td3 = squeeze(nansum(Atlantic.temp(si+1:ni-1, ldi+1:end, timei).*...
        Atlantic.volumeT(si+1:ni-1, ldi+1:end), [1, 2])) ./ vd3;
    sd3 = squeeze(nansum(Atlantic.rho0(si+1:ni-1, ldi+1:end, timei).*...
        Atlantic.volumeT(si+1:ni-1, ldi+1:end), [1, 2])) ./ vd3 - 1000;

    salD(timei) = (sald1 .* vd1 + sald2 .* vd2 + sald3 .* vd3) / ...
        (vd1 + vd2 + vd3);
    tempD(timei) = (td1 .* vd1 + td2 .* vd2 + td3 .* vd3) / ...
        (vd1 + vd2 + vd3);
    sigmaD(timei) = (sd1 .* vd1 + sd2 .* vd2 + sd3 .* vd3) / ...
        (vd1 + vd2 + vd3);

end
clear sald1 td1 sd1 sald2 td2 sd2 sald3 sd3 td3

%maximum over depth at north box edge
Mn = squeeze(max(AMOCsv(ni, :, :), [], 2)); 
%maximum over depth at south box edge
Mek = squeeze(max(AMOCsv(si, :, :), [], 2));
%minimum over depth at south box edge
Ms = squeeze(abs(min(AMOCsv(si, :, :), [], 2)));

tempL = tempL.';
tempD = tempD.';
T4 = [tempN, tempS, tempL, tempD];
salD = salD.';
salL = salL.';
S4 = [salN, salS, salL, salD];
sigmaL = sigmaL.';
sigmaD = sigmaD.';
sigma4 = [sigmaN, sigmaS, sigmaL, sigmaD];
D = D0L;

end
