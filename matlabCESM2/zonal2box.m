function [T4,S4,sigma4,D,Mn,Mek,Ms] = zonal2box(latNorth,latSouth,depthH,depth,meanlatA,volume1,meanT,meanSAL,meanrho0,D0,AMOC_Sv)
%zonal2box Summary of this function goes here
%   Detailed explanation goes here
if length(latNorth)==1
    ni=find(meanlatA>latNorth,1,'first');
    ni2=length(meanlatA);
elseif length(latNorth)==2
    ni=find(meanlatA>latNorth(1),1,'first');
    ni2=find(meanlatA<latNorth(2),1,'last');
end
si=find(meanlatA<latSouth,1,'last');
hdi=find(depth<depthH,1,'last');

meanSAL(meanSAL==0)=NaN;
D0L=squeeze(nansum(D0(si+1:ni-1,:).*repmat(sum(volume1(si+1:ni-1,:),2),[1 count(4)]),1))./sum(volume1(si+1:ni-1,:),[1 2]); %
salN=squeeze(nansum(meanSAL(ni:ni2,1:hdi,:).*repmat(volume1(ni:ni2,1:hdi),[1 1 count(4)]),[1 2]))./sum(volume1(ni:ni2,1:hdi),[1 2]); %north
tempN=squeeze(nansum(meanT(ni:ni2,1:hdi,:).*repmat(volume1(ni:ni2,1:hdi),[1 1 count(4)]),[1 2]))./sum(volume1(ni:ni2,1:hdi),[1 2]); %north
sigmaN=squeeze(nansum(meanrho0(ni:ni2,1:hdi,:).*repmat(volume1(ni:ni2,1:hdi),[1 1 count(4)]),[1 2]))./sum(volume1(ni:ni2,1:hdi),[1 2])-1000; %north

salS=squeeze(nansum(meanSAL(1:si,1:hdi,:).*repmat(volume1(1:si,1:hdi),[1 1 count(4)]),[1 2]))./sum(volume1(1:si,1:hdi),[1 2]); %south
tempS=squeeze(nansum(meanT(1:si,1:hdi,:).*repmat(volume1(1:si,1:hdi),[1 1 count(4)]),[1 2]))./sum(volume1(1:si,1:hdi),[1 2]); %south
sigmaS=squeeze(nansum(meanrho0(1:si,1:hdi,:).*repmat(volume1(1:si,1:hdi),[1 1 count(4)]),[1 2]))./sum(volume1(1:si,1:hdi),[1 2])-1000; %south

for timei=1:count(4)
ldi=find(-dedge>D0L(timei),1,'last')-1; %the index for the cell center whose bottom edge is above the mean pycnocline depth
if ldi<hdi
    ldi=hdi+1;
end


salL(timei)=squeeze(nansum(meanSAL(si+1:ni-1,1:ldi,timei).*volume1(si+1:ni-1,1:ldi),[1 2]))./sum(volume1(si+1:ni-1,1:ldi),[1 2]); %low lat
tempL(timei)=squeeze(nansum(meanT(si+1:ni-1,1:ldi,timei).*volume1(si+1:ni-1,1:ldi),[1 2]))./sum(volume1(si+1:ni-1,1:ldi),[1 2]); %low lat
sigmaL(timei)=squeeze(nansum(meanrho0(si+1:ni-1,1:ldi,timei).*volume1(si+1:ni-1,1:ldi),[1 2]))./sum(volume1(si+1:ni-1,1:ldi),[1 2])-1000; %low lat

%deep box via 3 portions
vd1=sum(volume1(ni:end,hdi+1:ldi),[1 2]);
sald1=squeeze(nansum(meanSAL(ni:end,hdi+1:ldi,timei).*volume1(ni:end,hdi+1:ldi),[1 2]))./vd1; %north mid
td1=squeeze(nansum(meanT(ni:end,hdi+1:ldi,timei).*volume1(ni:end,hdi+1:ldi),[1 2]))./vd1; %north mid
sd1=squeeze(nansum(meanrho0(ni:end,hdi+1:ldi,timei).*volume1(ni:end,hdi+1:ldi),[1 2]))./vd1 -1000; %north mid

vd2=sum(volume1(1:si,hdi+1:ldi),[1 2]);
sald2=squeeze(nansum(meanSAL(1:si,hdi+1:ldi,timei).*volume1(1:si,hdi+1:ldi),[1 2]))./vd2; %south mid
td2=squeeze(nansum(meanT(1:si,hdi+1:ldi,timei).*volume1(1:si,hdi+1:ldi),[1 2]))./vd1; %north mid
sd2=squeeze(nansum(meanrho0(1:si,hdi+1:ldi,timei).*volume1(1:si,hdi+1:ldi),[1 2]))./vd1 -1000; %north mid

vd3=sum(volume1(:,ldi+1:end),[1 2]);
sald3=squeeze(nansum(meanSAL(:,ldi+1:end,timei).*volume1(:,ldi+1:end),[1 2]))./vd3; %deep
td3=squeeze(nansum(meanT(:,ldi+1:end,timei).*volume1(:,ldi+1:end),[1 2]))./vd3;
sd3=squeeze(nansum(meanrho0(:,ldi+1:end,timei).*volume1(:,ldi+1:end),[1 2]))./vd3 -1000;

salD(timei)=(sald1.*vd1+sald2.*vd2+sald3.*vd3)/(vd1+vd2+vd3);
tempD(timei)=(td1.*vd1+td2.*vd2+td3.*vd3)/(vd1+vd2+vd3);
sigmaD(timei)=(sd1.*vd1+sd2.*vd2+sd3.*vd3)/(vd1+vd2+vd3);

end
clear sald1 td1 sd1 sald2 td2 sd2 sald3 sd3 td3

Mn=max(AMOC_Sv(ni,:,:),[],2);%maximum over depth at north box edge
Mek=max(AMOC_Sv(si,:,:),[],2);
Ms=abs(min(AMOC_Sv(si,:,:),[],2));
T4=[tempN,tempS,tempL,tempD];
S4=[salN,salS,salL,salD];
sigma4=[sigmaN,sigmaS,sigmaL,sigmaD];
D=D0L;

end