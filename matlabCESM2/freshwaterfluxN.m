% Copyright 2022, The Johns Hopkins University Applied Physics Laboratory LLC
% All rights reserved.
% Distributed under the terms of the BSD 3-Clause License.
function [Fwn] = freshwaterfluxN(coordinates, depth, Atlantic, dyu)
% freshwaterfluxN computes the freshwater flux from the northward salt flux
% across coordinates.latNorth 1 and 2
% using a depth-integral of Atlantic.salt and Atlantic.velN, which are
% zonally averaged Atlantic values; expects volume and dyu in m^2 and m


niv = find(Atlantic.latV(:, 1) > coordinates.latNorth1, 1, 'first');
ni = find(Atlantic.latT(:, 1) > Atlantic.latV(niv, 1), 1, 'first');
ni2v = find(Atlantic.latV(:, 1) < coordinates.latNorth2, 1, 'last');
ni2 = find(Atlantic.latT(:, 1) > Atlantic.latV(ni2v, 1), 1, 'first');


%depth is the cell center; finding the edges to make dz
dedge = depth(1:end-1) + 0.5 * diff(depth);
dedge = cat(1, 0, dedge, depth(end)+0.5*(depth(end) - depth(end-1)));
dz = diff(dedge.'); %m
[~, nz, nt] = size(Atlantic.velN);

dz1(1, 1:nz, 1) = dz;
dz1(isnan(Atlantic.velN(niv, :, 1))) = 0;
dz2(1, 1:nz, 1) = dz;
dz2(isnan(Atlantic.velN(ni2v, :, 1))) = 0;

vbar = zeros([2, 1, nt]);
vbar(1, 1, :) = nansum(Atlantic.velN(niv, :, :).*...
    repmat(dz1, [1, 1, nt]), 2) ./ sum(dz1);
vbar(2, 1, :) = nansum(Atlantic.velN(ni2v, :, :).*...
    repmat(dz2, [1, 1, nt]), 2) ./ sum(dz2);
vtransport = Atlantic.velN([niv, ni2v], :, :) - vbar; 
%relies on matlab 2016b or later to expand dimensions of vbar

[~, ~, nt] = size(vtransport);
Fwn = zeros(nt, 2);

%north 1
holdS = 0.5 * squeeze(Atlantic.salt(ni-1, :, :)+Atlantic.salt(ni, :, :));
holdS(isnan(holdS)) = 0;
Fwn(:, 1) = -(1 ./ 35) .* nansum(holdS.*squeeze(vtransport(1, :, :))...
    .*repmat(squeeze(Atlantic.volumeV(niv, :)).', [1, nt]), 1) ./ ...
    nanmean(dyu(:, niv));
% integrating dxdz, so the volume of each V cell divided by northward
% extent, dyu

%north 2
holdS = 0.5 * squeeze(Atlantic.salt(ni2-1, :, :)+Atlantic.salt(ni2, :, :));
holdS(isnan(holdS)) = 0;
Fwn(:, 2) = -(1 ./ 35) .* nansum(holdS.*squeeze(vtransport(2, :, :)).*...
    repmat(squeeze(Atlantic.volumeV(ni2v, :)).', [1, nt]), 1) ./ ...
    nanmean(dyu(:, ni2v));


end
