% Copyright 2022, The Johns Hopkins University Applied Physics Laboratory LLC
% All rights reserved.
% Distributed under the terms of the BSD 3-Clause License.

function [Fws] = freshwaterfluxS(coordinates, depth, Pacific, dyu)
% freshwaterfluxS computes the freshwater flux from the northward salt flux
% across coordinates.latSouth
% using a depth-integral of Pacific.salt and Pacific.velN, which are
% zonally averaged Pacific values; expects volume and dyu in m^2 and m

siv = find(Pacific.latV(:, 1) < coordinates.latSouth, 1, 'last');
si = find(Pacific.latT(:, 1) > Pacific.latV(siv, 1), 1, 'first');

%depth is the cell center; finding the edges to make dz
dedge = depth(1:end-1) + 0.5 * diff(depth);
dedge = cat(1, 0, dedge, depth(end)+0.5*(depth(end) - depth(end-1)));
dz = diff(dedge.'); %m
[~, nz, nt] = size(Pacific.velN);

dz1(1, 1:nz, 1) = dz;
dz1(isnan(Pacific.velN(siv, :, 1))) = 0;


vbar = zeros([1, 1, nt]);
vbar(1, 1, :) = nansum(Pacific.velN(siv, :, :).*...
    repmat(dz1, [1, 1, nt]), 2) ./ sum(dz1);
vtransport = Pacific.velN(siv, :, :) - vbar;
%relies on matlab 2016b or later to expand dimensions of vbar

[~, ~, nt] = size(vtransport);
Fws = zeros(nt, 1);

holdS = 0.5 * squeeze(Pacific.salt(si-1, :, :)+Pacific.salt(si, :, :));
holdS(isnan(holdS)) = 0;
Fws(:, 1) = -(1 ./ 35) .* nansum(holdS.*squeeze(vtransport(1, :, :)).* ...
    repmat(squeeze(Pacific.volumeV(siv, :)).', [1, nt]), 1) ./...
    nanmean(dyu(:, siv));
% integrating dxdz, so the volume of each V cell divided by northward
% extent, dyu

end
