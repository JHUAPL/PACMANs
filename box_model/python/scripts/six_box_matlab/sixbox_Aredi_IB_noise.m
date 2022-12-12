function [M_nA M_nP M_upwA M_upwPI M_eddyA M_eddyPI M_ex DlowA DlowPI T S sigma0]=...
    sixbox_Aredi_IB_noise(N,Kv,AI,Mek,Aredi,M_s,D0A,D0PI,TrnA,TrnP,Trs,TrlA,TrlPI,T0nA,T0nP,T0s,T0lA,T0lPI,T0d,S0nA,S0nP,S0s,S0lA,S0lPI,S0d,Fws0,Fwn0A,Fwn0P,FwIB0,epsilonA,epsilonP,epsilonIB,noiseamp)
%sixbox_noise
%function [M_nA M_nP M_upwA M_upwPI M_eddyA M_eddyPI DlowA DlowPI T S sigma0]=...
%    sixbox_Aredi(N,Kv,AI,Mek,Aredi,M_s,D0,TrnA,TrnP,Trs,TrlA,TrlPI,T0nA,T0nP,T0s,T0lA,T0lPI,T0d,S0nA,S0nPI,S0s,S0lA,S0lPI,S0d,Fws0,Fwn0A,Fwn0P,Fw0IB,epsilonA,epsilonP,epsilonIB,noiseamp)

%Choose low-latitude areas 45S-45N, masked Pacific to Indian. 
%Include Arctic area in high latitude Atlantic box

Area=3.58e14;
Area_lowA=0.64e14;
Area_lowPI=2.0e14;
Area_s=0.62e13;
Area_nA=0.22e14;
Area_nP=0.1e14;
Dhigh=100;
dt=365*86400/4;

%Split Ekman flux,SH freshwater flux by basin by size of basin.
SOfracA=0.25;
SOfracPI=0.75;

inorthA=1;
inorthP=2;
isouth=3;
ilowA=4;
ilowPI=5;
ideep=6;

T=zeros(N,6);
S=zeros(N,6);
V=zeros(N,6);
M_nA=zeros(N,1);
M_nP=zeros(N,1);
M_upwA=zeros(N,1);
M_upwPI=zeros(N,1);
M_eddyA=zeros(N,1);
M_eddyPI=zeros(N,1);

DlowA=zeros(N,1);
DlowPI=zeros(N,1);
DlowA(1)=D0A;
DlowPI(1)=D0PI;

T(1,:)=[T0nA T0nP T0s T0lA T0lPI T0d];
S(1,:)=[S0nA S0nP S0s S0lA S0lPI S0d];



for j=1:N
Fws=Fws0+noiseamp*randn(1);
FwnA=Fwn0A+noiseamp*randn(1);
FwnP=Fwn0P+noiseamp*randn(1);
FwIB=FwIB0+noiseamp*randn(1);
%Compute density
sigma0(j,:)=real(sw_dens(S(j,:),T(j,:),0));
sigma2(j,:)=sw_dens(S(j,:),T(j,:),2000);
M_LSA=Aredi*2.5e7*SOfracA*DlowA(j)/1e6;
M_LSPI=Aredi*2.5e7*SOfracPI*DlowPI(j)/1e6;
M_LNA=Aredi*5e6*DlowA(j)/1e6;
M_LNP=Aredi*1e7*DlowPI(j)/1e6;

drhoAtl=sigma0(j,inorthA)-sigma0(j,isouth);
drhoPac=sigma0(j,inorthP)-sigma0(j,isouth);
%Compute fluxes  
  gprimeA=9.8*(sigma0(j,inorthA)-sigma0(j,ilowA))/sigma0(j,inorthA);
  M_nA(j)=gprimeA*DlowA(j)^2/(epsilonA*(1.5-0.5*tanh(drhoAtl/0.1)));
  
  gprimePI=9.8*(sigma0(j,inorthP)-sigma0(j,ilowPI))/sigma0(j,inorthP);
  M_nP(j)=gprimePI*DlowPI(j)^2/(epsilonP*(1.5-0.5*tanh(drhoPac/0.1)));

  %Compute upwelling fluxes 
  M_upwA(j)=Kv*Area_lowA/min(DlowA(j),3700-DlowA(j));
  M_upwPI(j)=Kv*Area_lowPI/min(DlowPI(j),3700-DlowPI(j));

  %Compute eddy fluxes
  M_eddyA(j)=AI*DlowA(j)*2.5e7*SOfracA/1e6;
  M_eddyPI(j)=AI*DlowPI(j)*2.5e7*SOfracPI/1e6;

 %Compute transfer velocity betwewen PI and A
  gprimeAtoD=9.8*(sigma0(j,ideep)-sigma0(j,ilowA))/sigma0(j,ilowA);
  gprimePItoD=9.8*(sigma0(j,ideep)-sigma0(j,ilowPI))/sigma0(j,ilowPI);

  %Flow between basins is driven both by density difference and the
  %difference in pycnocline depth.
  M_transPtoA=(gprimePItoD*DlowPI(j)^2-gprimeAtoD*DlowA(j)^2)/epsilonIB;
  M_ex(j)=M_transPtoA;

 %Compute volumes that change dynamically
  Vdeep=3700*Area-(Area_nA+Area_nP)*Dhigh-Area_s*Dhigh-Area_lowA*DlowA(j)-Area_lowPI*DlowPI(j);
  VlowA=Area_lowA*DlowA(j);
  VlowPI=Area_lowPI*DlowPI(j);
  
  %Compute initial salinities in volumes that change dynamically
  SinitlowA=S(j,ilowA)*VlowA;
  SinitlowPI=S(j,ilowPI)*VlowPI;

  %Compute change in volume of boxes
  dVlowA=(Mek*SOfracA-M_eddyA(j)-M_nA(j)*(drhoAtl>0)+M_upwA(j)+M_transPtoA-Fws*SOfracA-FwnA-FwIB)*dt;
  dVlowPI=(Mek*SOfracPI-M_eddyPI(j)-M_nP(j)*(drhoPac>0)+M_upwPI(j)-M_transPtoA-Fws*SOfracPI-FwnP+FwIB)*dt;
  
  dVdeep=-(dVlowA+dVlowPI);
  DlowA(j+1)=DlowA(j)+dVlowA/Area_lowA;
  DlowPI(j+1)=DlowPI(j)+dVlowPI/Area_lowPI;

  % Fluxes of salt go to deep ocean if overturning is positive, return
  % bearing N. Subpolar salinity if it is lighter than southern ocean
  dSlowA=(Mek*SOfracA*S(j,isouth)-M_eddyA(j)*S(j,ilowA)-abs(M_nA(j))*S(j,ilowA)+abs(M_nA(j))*S(j,inorthA)*(drhoAtl<0) ...
      +M_upwA(j)*S(j,ideep)+M_LSA*(S(j,isouth)-S(j,ilowA))+...
      M_LNA*(S(j,inorthA)-S(j,ilowA))+M_transPtoA*(S(j,ilowPI)*(M_transPtoA>0)+S(j,ilowA)*(M_transPtoA<0)))*dt;

  dSlowPI=(Mek*SOfracPI*S(j,isouth)-M_eddyPI(j)*S(j,ilowPI)-abs(M_nP(j))*S(j,ilowPI)+abs(M_nP(j))*S(j,inorthP)*(drhoPac<0) ...
      +M_upwPI(j)*S(j,ideep)+M_LSPI*(S(j,isouth)-S(j,ilowPI))+...
      M_LNP*(S(j,inorthP)-S(j,ilowPI))-M_transPtoA*(S(j,ilowPI)*(M_transPtoA>0)+S(j,ilowA)*(M_transPtoA<0)))*dt;

  dSSouth=((M_eddyA(j)+M_LSA)*(S(j,ilowA)-S(j,isouth))+...
           (M_eddyPI(j)+M_LSPI)*(S(j,ilowPI)-S(j,isouth))+...
      (Mek+M_s)*(S(j,ideep)-S(j,isouth))-Fws*S(j,isouth))*dt;

  dSDeep=(M_nA(j)*S(j,inorthA)*(drhoAtl>0)+M_nP(j)*S(j,inorthP)*(drhoPac>0)-(M_upwA(j)+M_upwPI(j)+Mek+M_s)*S(j,ideep)...
          +(M_eddyA(j)+M_eddyPI(j)+M_s)*S(j,isouth)+Fws*S(j,isouth)+FwnA*S(j,inorthA)+FwnP*S(j,inorthP))*dt;

  dSNorthA=((abs(M_nA(j))+M_LNA)*(S(j,ilowA)-S(j,inorthA))-FwnA*S(j,inorthA))*dt;
  dSNorthP=((abs(M_nP(j))+M_LNP)*(S(j,ilowPI)-S(j,inorthP))-FwnP*S(j,inorthP))*dt;


  dTlowA=(Mek*SOfracA*T(j,isouth)-M_eddyA(j)*T(j,ilowA)-abs(M_nA(j))*T(j,ilowA) ...
      -(M_nA(j)*T(j,inorthA)*(M_nA(j)<0))+M_upwA(j)*T(j,ideep)+M_LSA*(T(j,isouth)-T(j,ilowA))+...
      M_LNA*(T(j,inorthA)-T(j,ilowA))+M_transPtoA*(T(j,ilowPI)*(M_transPtoA>0)+T(j,ilowA)*(M_transPtoA<0))...
      +Area_lowA*100*(TrlA-T(j,ilowA))/365/86400)*dt;

  dTlowPI=(Mek*SOfracPI*T(j,isouth)-M_eddyPI(j)*T(j,ilowPI)-abs(M_nP(j))*T(j,ilowPI) ...
      -(M_nP(j)*T(j,inorthP)*(M_nP(j)<0))+M_upwPI(j)*T(j,ideep)+M_LSPI*(T(j,isouth)-T(j,ilowPI))+...
      M_LNP*(T(j,inorthP)-T(j,ilowPI))-M_transPtoA*(T(j,ilowPI)*(M_transPtoA>0)+T(j,ilowPI)*(M_transPtoA<0))...
      +Area_lowPI*100*(TrlPI-T(j,ilowPI))/365/86400)*dt;
  
  dTSouth=((M_eddyPI(j)+M_LSPI)*(T(j,ilowPI)-T(j,isouth))+...
            (M_eddyA(j)+M_LSA)*(T(j,ilowA)-T(j,isouth))+...
      (Mek+M_s)*(T(j,ideep)-T(j,isouth))+...
     +Area_s*100*(Trs-T(j,isouth))/365/86400)*dt;

  dTDeep=((M_nA(j)*(M_nA(j)>0)+FwnA)*T(j,inorthA)+...
          (M_nP(j)*(M_nP(j)>0)+FwnP)*T(j,inorthP)+ ...
          -(M_upwA(j)+M_upwPI(j)+Mek+M_s)*T(j,ideep)...
          +(M_eddyA(j)+M_eddyPI(j)+M_s+Fws)*T(j,isouth))*dt;

  dTNorthA=((abs(M_nA(j))+M_LNA)*(T(j,ilowA)-T(j,inorthA))...
        +Area_nA*100*(TrnA-T(j,inorthA))/365/86400)*dt;
  dTNorthP=((abs(M_nP(j))+M_LNP)*(T(j,ilowPI)-T(j,inorthP))...
        +Area_nP*100*(TrnP-T(j,inorthP))/365/86400)*dt;


  S(j+1,inorthA)=S(j,inorthA)+dSNorthA/(Dhigh*Area_nA);
  S(j+1,inorthP)=S(j,inorthP)+dSNorthP/(Dhigh*Area_nP);

  S(j+1,isouth)=S(j,isouth)+dSSouth/(Dhigh*Area_s);
  
  S(j+1,ilowA)=(S(j,ilowA)*VlowA+dSlowA)/(VlowA+dVlowA);
  S(j+1,ilowPI)=(S(j,ilowPI)*VlowPI+dSlowPI)/(VlowPI+dVlowPI);


  S(j+1,ideep)=(S(j,ideep)*Vdeep+dSDeep)/(Vdeep+dVdeep);
  
  T(j+1,inorthA)=T(j,inorthA)+dTNorthA/(Dhigh*Area_nA);
  T(j+1,inorthP)=T(j,inorthP)+dTNorthP/(Dhigh*Area_nP);


  T(j+1,isouth)=T(j,isouth)+dTSouth/(Dhigh*Area_s);
  T(j+1,ilowA)=(T(j,ilowA)*VlowA+dTlowA)/(VlowA+dVlowA);
  T(j+1,ilowPI)=(T(j,ilowPI)*VlowPI+dTlowPI)/(VlowPI+dVlowPI);
  T(j+1,ideep)=(T(j,ideep)*Vdeep+dTDeep)/(Vdeep+dVdeep);

[j [Area_nA*Dhigh Area_nP*Dhigh Area_s*Dhigh VlowA+dVlowA VlowPI+dVlowPI Vdeep+dVdeep]*S(j+1,:)'-[Area_nA*Dhigh Area_nP*Dhigh Area_s*Dhigh VlowA VlowPI Vdeep]*S(j,:)'];
end

figure(1)
clf
subplot(211)
%plot(S)
%legend('NA','NP','South','LowA','LowPI','Deep')
%subplot(212)
%keyboard
plot((1:N)*dt/365/86400,M_nA/1e6,(1:N)*dt/365/86400,M_nP/1e6,(1:N)*dt/365/86400,(M_upwA+M_upwPI)/1e6,(1:N)*dt/365/86400,(Mek-M_eddyA-M_eddyPI)/1e6)
legend('NorthA','NorthP','Upw','South')
pause(0.1);
ylabel('Transport in Sv')
xlabel('Time in Years')
return