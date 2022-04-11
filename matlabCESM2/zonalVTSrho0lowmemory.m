function [timeUTC,depth,meanlatTA,meanlonTA,volumeTA,meanlatVA,meanlonVA,volumeVA,meanVA,meanTA,meanSA,meanrho0A,D0A,meanlonTP,meanlatTP,volumeTP,meanlonVP,meanlatVP,volumeVP,meanVP,meanTP,meanSP,meanrho0P,D0P] = zonalVTSrho0lowmemory(fileV,fileT,fileS)
%zonalTSrho0 reads .nc T,S files by latitude, computes rho0, the potential 
% density, using the gsw toolbox, averages zonally in the Atlantic and
% Pacific, and returns the zonally-averaged t, s, and rho0 and pycnocline
% depth, A for atlantic, P for pacific
% fileGrid contains the regions and TAREA values for CESM2

time_days_since_01Jan0000 = ncread(fileS,'time'); % time is number of days since 0000-01-01 00:00:00'
time_on_01Jan0000 = datenum(0000,1,1,0,0,0); % = matlab time as datenum is number of days
timeUTC = time_on_01Jan0000 + (time_days_since_01Jan0000); % matlab time in days, i.e.datenum 
nt=length(timeUTC);

lat_degN_1 = ncread(fileS,'lat'); % nlon,nlat 320x384
lon_degE_1 = ncread(fileS,'lon'); % nlon,nlat 320x384
depth = ncread(fileS,'lev')/100; % depth (m)
[nx,ny]=size(lat_degN_1);
nz=length(depth);
lat_degN_1v = ncread(fileV,'lat'); % nlon,nlat 320x384
lon_degE_1v = ncread(fileV,'lon'); % nlon,nlat 320x384

dedge=depth(1:end-1)+0.5*diff(depth); %depth_m_1 is the cell center; finding the edges to make dz
dedge=cat(1,0,dedge,depth(end)+0.5*(depth(end)-depth(end-1)));
dz=diff(dedge.');

regions=ncread(fileGrid,'REGION_MASK');
tarea=ncread(fileGrid,'TAREA');

meanVA=zeros(ny,nz,nt);
meanSA=zeros(ny,nz,nt);
meanTA=zeros(ny,nz,nt);
meanrho0A=zeros(ny,nz,nt);
meanlonTA=zeros(ny,nz);
meanlatTA=zeros(ny,nz);
volumeTA=zeros(ny,nz);
meanlonVA=zeros(ny,nz);
meanlatVA=zeros(ny,nz);
volumeVA=zeros(ny,nz);
meanSP=zeros(ny,nz,nt);
meanTP=zeros(ny,nz,nt);
meanrho0P=zeros(ny,nz,nt);
meanlonTP=zeros(ny,nz);
meanlatTP=zeros(ny,nz);
volumeTP=zeros(ny,nz);

for ii=1:ny


    for jj=1:nz
        start = [1 ii jj 1]; % [lon,lat,depth,monthly time], start location along each coordinate
    count = [Inf 1 1 nt];    % read number of elements in each dimension....INf = read until the end of each dimension
    stride = [1 1 1 1];   % read variable data at intervals specified in stride
    hold_SAL = squeeze(ncread(fileS,'so',start,count,stride)); % (lon, lat, depth, monthly time) 320x1x1x600
    hold_T = squeeze(ncread(fileT,'thetao',start,count,stride));
    hold_V = squeeze(ncread(fileV,'vo',start,count,stride));

        hold_region=regions(:,ii);
        hold_lon=lon_degE_1(:,ii);
        hold_lonv=lon_degE_1v(:,ii);
        iwant=(hold_region==6)|(hold_region==8)|(hold_region==9);
        iwantv=iwant;
        if sum(iwant)==0
            iwant=hold_lon<22.5 |hold_lon>292.4;
            iwantv=hold_lonv<22.5 |hold_lonv>292.4;
        end
        iwant(hold_SAL==0)=0;
        iwant(isnan(hold_SAL))=0;
        iwantv(hold_V==0)=0;
        iwantv(isnan(hold_V))=0;
        volumeTA(ii,jj)=nansum(dz(jj)*tarea(iwant,ii));
        volumeVA(ii,jj)=nansum(dz(jj)*tarea(iwantv,ii));
        meanVA(ii,jj,:)=nansum(hold_V(iwant,:)*dz(jj).*repmat(tarea(iwant,ii),1,count(4)),1)./volumeA(ii,jj);
        meanSA(ii,jj,:)=nansum(hold_SAL(iwant,:)*dz(jj).*repmat(tarea(iwant,ii),1,count(4)),1)./volumeTA(ii,jj);
        meanTA(ii,jj,:)=nansum(hold_T(iwant,:)*dz(jj).*repmat(tarea(iwant,ii),1,count(4)),1)./volumeTA(ii,jj);
        meanlatTA(ii,jj)=nansum(lat_degN_1(iwant,ii).*tarea(iwant,ii))./nansum(tarea(iwant,ii));
        holdlon=lon_degE_1(iwant,ii); holdlon(holdlon<180)=holdlon(holdlon<180)+360;
        meanlonTA(ii,jj)=nansum(holdlon.*tarea(iwant,ii))./nansum(tarea(iwant,ii));

        meanlatVA(ii,jj)=nansum(lat_degN_1v(iwantv,ii).*tarea(iwantv,ii))./nansum(tarea(iwantv,ii));
        holdlon=lon_degE_1v(iwantv,ii); holdlon(holdlon<180)=holdlon(holdlon<180)+360;
        meanlonVA(ii,jj)=nansum(holdlon.*tarea(iwantv,ii))./nansum(tarea(iwantv,ii));
    
        %density
        P = gsw_p_from_z(-depth_m_1(jj)*ones(sum(iwant),1),lat_degN_1(iwant,ii)); % pressure(decibars); 1 decibar = 1 meter of seawater
        SA = gsw_SA_from_SP(hold_SAL(iwant,:),P,lon_degE_1(iwant,ii),lat_degN_1(iwant,ii)); % Absolute Salinity (g/kg)
        CT = gsw_CT_from_pt(SA,hold_T(iwant,:)); % Conservative Temperature (deg C)  
%         rho = gsw_rho(SA,CT,P); % Density (kg/m^3) insitu
%         rho2k = gsw_rho(SA,CT,2000);
        rho0 = gsw_rho(SA,CT,0); %potential density
%         meanrho(ii,jj,:)=nansum(rho*dz(jj).*repmat(tarea(iwant,ii),1,count(4)),1)./volume1(ii,jj); %insitu density
%         meanrho2k(ii,jj,:)=nansum(rho2k*dz(jj).*repmat(tarea(iwant,ii),1,count(4)),1)./volume1(ii,jj); %potential density
        meanrho0A(ii,jj,:)=nansum(rho0*dz(jj).*repmat(tarea(iwant,ii),1,count(4)),1)./volumeTA(ii,jj); %density referenced to 2000m

        %Pacific
        iwant=(hold_region==1)|(hold_region==2);
        iwantv=iwant;
        if sum(iwant)==0
            iwant=hold_lon>140 |hold_lon<250;
            iwantv=hold_lonv>140 |hold_lonv<250;
        end
        iwant(hold_SAL==0)=0;
        iwant(isnan(hold_SAL))=0;
        iwantv(hold_V==0)=0;
        iwantv(isnan(hold_V))=0;
        volumeTP(ii,jj)=nansum(dz(jj)*tarea(iwant,ii));
        volumeVA(ii,jj)=nansum(dz(jj)*tarea(iwantv,ii));
        meanVA(ii,jj,:)=nansum(hold_V(iwantv,:)*dz(jj).*repmat(tarea(iwantv,ii),1,count(4)),1)./volumeVA(ii,jj);
        meanSP(ii,jj,:)=nansum(hold_SAL(iwant,:)*dz(jj).*repmat(tarea(iwant,ii),1,count(4)),1)./volumeTP(ii,jj);
        meanTP(ii,jj,:)=nansum(hold_T(iwant,:)*dz(jj).*repmat(tarea(iwant,ii),1,count(4)),1)./volumeTP(ii,jj);
        meanlatTP(ii,jj)=nansum(lat_degN_1(iwant,ii).*tarea(iwant,ii))./nansum(tarea(iwant,ii));
        holdlon=lon_degE_1(iwant,ii); holdlon(holdlon<180)=holdlon(holdlon<180)+360;
        meanlonTP(ii,jj)=nansum(holdlon.*tarea(iwant,ii))./nansum(tarea(iwant,ii));

        meanlatVA(ii,jj)=nansum(lat_degN_1v(iwantv,ii).*tarea(iwant,ii))./nansum(tarea(iwantv,ii));
        holdlon=lon_degE_1v(iwant,ii); holdlon(holdlon<180)=holdlon(holdlon<180)+360;
        meanlonVA(ii,jj)=nansum(holdlon.*tarea(iwantv,ii))./nansum(tarea(iwantv,ii));

        %density
        P = gsw_p_from_z(-depth_m_1(jj)*ones(sum(iwant),1),lat_degN_1(iwant,ii)); % pressure(decibars); 1 decibar = 1 meter of seawater
        SA = gsw_SA_from_SP(hold_SAL(iwant,:),P,lon_degE_1(iwant,ii),lat_degN_1(iwant,ii)); % Absolute Salinity (g/kg)
        CT = gsw_CT_from_pt(SA,hold_T(iwant,:)); % Conservative Temperature (deg C)  
        rho0 = gsw_rho(SA,CT,0); %potential density
        meanrho0P(ii,jj,:)=nansum(rho0*dz(jj).*repmat(tarea(iwant,ii),1,count(4)),1)./volumeTP(ii,jj); %density referenced to 2000m

    end

end

% dedge=depth(1:end-1)+0.5*diff(depth); %depth_m_1 is the cell center; finding the edges to make dz
% dedge=cat(1,0,dedge,depth_m_1(end)+0.5*(depth(end)-depth_m_1(end-1)));
% dz=diff(dedge.');
D0A=squeeze(nansum((meanrho0A-max(meanrho0A,[],2)).*repmat(dz.*-depth.',ny,1),2)./nansum((meanrho0A-max(meanrho0A,[],2)).*repmat(dz,ny,1),2)); %from potential density
D0P=squeeze(nansum((meanrho0P-max(meanrho0P,[],2)).*repmat(dz.*-depth.',ny,1),2)./nansum((meanrho0P-max(meanrho0P,[],2)).*repmat(dz,ny,1),2)); %from potential density

end