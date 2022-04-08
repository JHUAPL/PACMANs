function [Fws] = freshwaterfluxS(latSouth,depth,meanlatP,meanSP,meanlatVP,volumeVP,meanVP,dyu)
%freshwaterflux Summary of this function goes here
%   meanVA is zonally averaged northward velocity in m/s 
%   volume and dyu in m^2 and m

siv=find(meanlatVP(:,1)<latSouth,1,'last');
si=find(meanlatP(:,1)>meanlatVP(siv,1),1,'first');


dedge=depth(1:end-1)+0.5*diff(depth); %depth_m_1 is the cell center; finding the edges to make dz
dedge=cat(1,0,dedge,depth(end)+0.5*(depth(end)-depth(end-1)));
dz=diff(dedge.');%m
[~,nz,nt]=size(meanVP);

dz1(1,1:nz,1)=dz; dz1(isnan(meanVP(siv,:,1)))=0;


vbar=zeros([1 1 nt]);
vbar(1,1,:)=nansum(meanVP(siv,:,:).*repmat(dz1,[1 1 nt]),2)./sum(dz1);
vtransport=meanVP(siv,:,:)-vbar; %relies on matlab 2016b or later to expand dimensions of vbar

[~,~,nt]=size(vtransport);
Fws=zeros(nt,1);

    holdS=0.5*squeeze(meanSP(si-1,:,:)+meanSP(si,:,:));
    holdS(isnan(holdS))=0;
    Fws(:,1)=-(1./35).*nansum(holdS.*squeeze(vtransport(1,:,:)).*repmat(squeeze(volumeVP(siv,:)).',[1 nt]),1)./nanmean(dyu(:,siv));%volume of each V cell divided by northward extent

end
