%Fourbox
function [M_n M_upw M_eddy Dlow T S sigma0]=...
    fourbox_Aredi(N,Kv,AI,Mek,Aredi,M_s,D0,T0s,T0n,T0l,T0d,S0s,S0n,S0l,S0d,Fws,Fwn,epsilon)
Area=3.6e14;
Area_low=2e14;
Area_s=1e14;
Area_n=0.6e14;
Dhigh=100;
dt=365*86400/4;

inorth=1;
isouth=2;
ilow=3;
ideep=4;

T=zeros(N,4);
S=zeros(N,4);
V=zeros(N,4);
M_n=zeros(N,1);
M_upw=zeros(N,1);
M_eddy=zeros(N,1);
Dlow=zeros(N,1);
Dlow(1)=D0;

T(1,:)=[T0n T0s T0l T0d];
S(1,:)=[S0s S0n S0l S0d];


for j=1:N
%Compute density
sigma0(j,:)=real(sw_dens(S(j,:),T(j,:),0));
sigma2(j,:)=sw_dens(S(j,:),T(j,:),2000);
M_LS=Aredi*2.5e7*Dlow(j)/1e6;
M_LN=Aredi*5e6*Dlow(j)/1e6;

if (sigma0(j,inorth)>sigma0(j,ilow))
  gprime=9.8*(sigma0(j,inorth)-sigma0(j,ilow))/sigma0(j,inorth);
  M_n(j)=gprime*Dlow(j)^2/epsilon;
  M_upw(j)=Kv*Area_low/min(Dlow(j),3700-Dlow(j));
  M_eddy(j)=AI*Dlow(j)*2.5e7/1e6;
  Vdeep=3700*Area-Area_n*Dhigh-Area_s*Dhigh-Area_low*Dlow(j);
  Vlow=Area_low*Dlow(j);
  Sinitlow=S(j,ilow)*Area_low*Dlow(j);
  dVlow=(Mek-M_eddy(j)-M_n(j)+M_upw(j)-Fws-Fwn)*dt;
  dVdeep=-dVlow;
  Dlow(j+1)=Dlow(j)+dVlow/Area_low;
  dSlow=(Mek*S(j,isouth)-M_eddy(j)*S(j,ilow)-M_n(j)*S(j,ilow) ...
      +M_upw(j)*S(j,ideep)+M_LS*(S(j,isouth)-S(j,ilow))+...
      M_LN*(S(j,inorth)-S(j,ilow)))*dt;
  dSSouth=((M_eddy(j)+M_LS)*(S(j,ilow)-S(j,isouth))+...
      (Mek+M_s)*(S(j,ideep)-S(j,isouth))-Fws*S(j,isouth))*dt;
  dSDeep=(M_n(j)*S(j,inorth)-(M_upw(j)+Mek+M_s)*S(j,ideep)...
          +(M_eddy(j)+M_s)*S(j,isouth)+Fws*S(j,isouth)+Fwn*S(j,inorth))*dt;
  dSNorth=((M_n(j)+M_LN)*(S(j,ilow)-S(j,inorth))-Fwn*S(j,inorth))*dt;
  dTlow=(Mek*T(j,isouth)-M_eddy(j)*T(j,ilow)-M_n(j)*T(j,ilow) ...
      +M_upw(j)*T(j,ideep)+M_LS*(T(j,isouth)-T(j,ilow))+...
      M_LN*(T(j,inorth)-T(j,ilow))+Area_low*100*(T0l-T(j,ilow))/365/86400)*dt;
  dTSouth=((M_eddy(j)+M_LS)*(T(j,ilow)-T(j,isouth))+...
      (Mek+M_s)*(T(j,ideep)-T(j,isouth))+...
     +Area_s*100*(T0s-T(j,isouth))/365/86400)*dt;
  dTDeep=((M_n(j)+Fwn)*T(j,inorth)-(M_upw(j)+Mek+M_s)*T(j,ideep)...
          +(M_eddy(j)+M_s+Fws)*T(j,isouth))*dt;
  dTNorth=((M_n(j)+M_LN)*(T(j,ilow)-T(j,inorth))...
        +Area_n*100*(T0n-T(j,inorth))/365/86400)*dt;
  S(j+1,inorth)=S(j,inorth)+dSNorth/(Dhigh*Area_n);
  S(j+1,isouth)=S(j,isouth)+dSSouth/(Dhigh*Area_s);
  S(j+1,ilow)=(S(j,ilow)*Vlow+dSlow)/(Vlow+dVlow);
  S(j+1,ideep)=(S(j,ideep)*Vdeep+dSDeep)/(Vdeep+dVdeep);
  T(j+1,inorth)=T(j,inorth)+dTNorth/(Dhigh*Area_n);
  T(j+1,isouth)=T(j,isouth)+dTSouth/(Dhigh*Area_s);
  T(j+1,ilow)=(T(j,ilow)*Vlow+dTlow)/(Vlow+dVlow);
  T(j+1,ideep)=(T(j,ideep)*Vdeep+dTDeep)/(Vdeep+dVdeep);
end
if (sigma0(j,inorth)<=sigma0(j,ilow))
  gprime=9.8*(sigma0(j,inorth)-sigma0(j,ilow))/sigma0(j,inorth);
  M_n(j)=gprime*Dhigh^2/epsilon;
  M_upw(j)=Kv*Area_low/min(Dlow(j),3700-Dlow(j));
  M_eddy(j)=AI*Dlow(j)*2.5e7/1e6;
  Vdeep=3700*Area-Area_n*Dhigh-Area_s*Dhigh-Area_low*Dlow(j);
  Vlow=Area_low*Dlow(j);
  dVlow=(Mek-M_eddy(j)-M_n(j)+M_upw(j)-Fws-Fwn)*dt;
  dVdeep=-dVlow;
  Dlow(j+1)=Dlow(j)+dVlow/Area_low;
  dSlow=(Mek*S(j,isouth)-M_eddy(j)*S(j,ilow)-M_n(j)*S(j,inorth) ...
      +M_upw(j)*S(j,ideep)+M_LS*(S(j,isouth)-S(j,ilow))+...
      M_LN*(S(j,inorth)-S(j,ilow)))*dt;
  dSSouth=((M_eddy(j)+M_LS)*(S(j,ilow)-S(j,isouth))+...
      Mek*(S(j,ideep)-S(j,isouth))+M_s*(S(j,ideep)-S(j,isouth))...
     -Fws*S(j,isouth))*dt;
  dSDeep=(-(M_upw(j)+Mek+M_s-M_n(j))*S(j,ideep)...
          +(M_eddy(j)+M_s+Fws)*S(j,isouth)+Fwn*S(j,inorth))*dt;
  dSNorth=(M_LN*(S(j,ilow)-S(j,inorth))-M_n(j)*(S(j,ideep)-S(j,inorth))-Fwn*S(j,inorth))*dt;
  dTlow=(Mek*T(j,isouth)-M_eddy(j)*T(j,ilow)-M_n(j)*T(j,inorth) ...
      +M_upw(j)*T(j,ideep)+M_LS*(T(j,isouth)-T(j,ilow))+...
      M_LN*(T(j,inorth)-T(j,ilow))+Area_low*100*(T0l-T(j,ilow))/365/86400)*dt;
  dTSouth=((M_eddy(j)+M_LS)*(T(j,ilow)-T(j,isouth))+...
      (Mek+M_s)*(T(j,ideep)-T(j,isouth))+...
     +Area_s*100*(T0s-T(j,isouth))/365/86400)*dt;
  dTDeep=(-(M_upw(j)+Mek+M_s-M_n(j))*T(j,ideep)...
          +(M_eddy(j)+M_s)*T(j,isouth))*dt;
  dTNorth=((-M_n(j)+M_LN)*(T(j,ilow)-T(j,inorth))+Area_n*100*(T0n-T(j,inorth))/365/86400)*dt;
  S(j+1,inorth)=S(j,inorth)+dSNorth/(Area_n*Dhigh);
  S(j+1,isouth)=S(j,isouth)+dSSouth/(Area_s*Dhigh);
  S(j+1,ilow)=(S(j,ilow)*Vlow+dSlow)/(Vlow+dVlow);
  S(j+1,ideep)=(S(j,ideep)*Vdeep+dSDeep)/(Vdeep+dVdeep);
  T(j+1,inorth)=T(j,inorth)+dTNorth/(Dhigh*Area_n);
  T(j+1,isouth)=T(j,isouth)+dTSouth/(Dhigh*Area_s);
  T(j+1,ilow)=(T(j,ilow)*Vlow+dTlow)/(Vlow+dVlow);
  T(j+1,ideep)=(T(j,ideep)*Vdeep+dTDeep)/(Vdeep+dVdeep);
end
%[j [Area_n*Dhigh Area_s*Dhigh Vlow+dVlow Vdeep+dVdeep]*S(j+1,:)'-[Area_n*Dhigh Area_s*Dhigh Vlow Vdeep]*S(j,:)']
end

figure(1)
clf
subplot(211)
plot(S)
legend('North','South','Low','Deep')
subplot(212)
plot((1:N),M_n/1e6,(1:N),M_upw/1e6,(1:N),(Mek-M_eddy)/1e6)
legend('North','Upw','South')
pause(0.1);
%keyboard
return