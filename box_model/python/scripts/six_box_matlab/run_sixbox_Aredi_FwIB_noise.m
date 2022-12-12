N=8000;
Kv=0.1e-4;
AI=1000;
Mek=25e6;
Aredi=1000;
M_s=15e6;
D0A=420;
D0PI=380;
TrnA=0;
TrnP=2;
Trs=-10;
TrlPI=17.8;
TrlA=16.8;
T0nA=4;
T0nP=4;
T0s=4;
T0lPI=17.2;
T0lA=16.2;
T0d=3;
S0nA=35;
S0nP=33.8;
S0s=34;
S0lA=35.8;
S0lPI=35;
S0d=34.8;
fac=1.8;
Fws0=1.1e6*fac;
Fwn0A=0.45e6*fac;
Fwn0P=0.34e6*fac;
Fw0IB=0.3e6*fac;
epsilonA=1.2e-4;
epsilonP=1.2e-4;
epsilonIB=0.57e-4;
noiseamp=0;

[M_nA M_nP M_upwA M_upwPI M_eddyA M_eddyPI M_ex DlowA DlowPI T S sigma0]=...
    sixbox_Aredi_IB_noise(N,Kv,AI,Mek,Aredi,M_s,D0A,D0PI,TrnA,TrnP,Trs,TrlA,TrlPI,T0nA,T0nP,T0s,T0lA,T0lPI,T0d,S0nA,S0nP,S0s,S0lA,S0lPI,S0d,Fws0,Fwn0A,Fwn0P,Fw0IB,epsilonA,epsilonP,epsilonIB,noiseamp);

[T(N,:)
 S(N,:)
 sw_dens(S(N,:),T(N,:),0)-1000]   