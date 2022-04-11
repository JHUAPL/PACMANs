function [Fwn] = freshwaterfluxN(latNorth,depth,meanlatA,meanSA,meanlatVA,volumeVA,meanVA,dyu)
%freshwaterflux Summary of this function goes here
%   meanVA is zonally averaged northward velocity in m/s 
%   volume and dyu in m^2 and m

    if length(latNorth)==1
        ni2=length(meanlatA(:,1));
        niv=find(meanlatVA(:,1)>latNorth,1,'first');
        ni=find(meanlatA(:,1)>meanlatVA(niv,1),1,'first');
        ni2v=length(meanlatVA(:,1));
    elseif length(latNorth)==2
        niv=find(meanlatVA(:,1)>latNorth(1),1,'first');
        ni=find(meanlatA(:,1)>meanlatVA(niv,1),1,'first');
        ni2v=find(meanlatVA(:,1)<latNorth(2),1,'last');
        ni2=find(meanlatA(:,1)>meanlatVA(ni2v,1),1,'first');
    end


dedge=depth(1:end-1)+0.5*diff(depth); %depth_m_1 is the cell center; finding the edges to make dz
dedge=cat(1,0,dedge,depth(end)+0.5*(depth(end)-depth(end-1)));
dz=diff(dedge.');%m
[~,nz,nt]=size(meanVA);

%dz1(1,1:nz,1)=dz; dz1(isnan(meanVA(siv,:,1)))=0;
dz1(1,1:nz,1)=dz; dz1(isnan(meanVA(niv,:,1)))=0;
dz2(1,1:nz,1)=dz; dz2(isnan(meanVA(ni2v,:,1)))=0;

vbar=zeros([2 1 nt]);
vbar(1,1,:)=nansum(meanVA(niv,:,:).*repmat(dz1,[1 1 nt]),2)./sum(dz1);
vbar(2,1,:)=nansum(meanVA(ni2v,:,:).*repmat(dz2,[1 1 nt]),2)./sum(dz2);
vtransport=meanVA([niv,ni2v],:,:)-vbar; %relies on matlab 2016b or later to expand dimensions of vbar

[~,~,nt]=size(vtransport);
Fwn=zeros(nt,2);

%north 1
    holdS=0.5*squeeze(meanSA(ni-1,:,:)+meanSA(ni,:,:));
    holdS(isnan(holdS))=0;
    Fwn(:,1)=-(1./35).*nansum(holdS.*squeeze(vtransport(1,:,:)).*repmat(squeeze(volumeVA(niv,:)).',[1 nt]),1)./nanmean(dyu(:,niv));%volume of each V cell divided by northward extent

%north 2
    holdS=0.5*squeeze(meanSA(ni2-1,:,:)+meanSA(ni2,:,:));
    holdS(isnan(holdS))=0;
    Fwn(:,2)=-(1./35).*nansum(holdS.*squeeze(vtransport(2,:,:)).*repmat(squeeze(volumeVA(ni2v,:)).',[1 nt]),1)./nanmean(dyu(:,ni2v));%volume of each V cell divided by northward extent


end
