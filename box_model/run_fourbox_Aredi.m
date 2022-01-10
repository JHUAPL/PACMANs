% Run fourbox
%
 
N=4000;
Kv=1e-5;
AI=1000;
D0=400;
epsilon=1.2e-4;
Fws=1e6;
T0n=2;
T0s=4;
T0d=3;
T0l=17;
 
S0n=35;
S0s=36;
S0d=34.5;
S0l=36;
M_s=15e6;
Aredi=1000;
 
 for k=1:31
    Fwn=(k-1)*0.05e6;
    [M_n M_u M_eddy Dlow T S sigma0]=...
       fourbox_Aredi(N,Kv,AI,15e6,Aredi,M_s,D0,T0s,T0n,T0l,T0d,S0s,S0n,S0l,S0d,Fws,Fwn,epsilon);
    Mnsave15(k)=M_n(N);
    Musave15(k)=M_u(N);
    Meddysave15(k)=M_eddy(N);
    dsigmasave15(k)=sigma0(N,1)-sigma0(N,3);
    Dlowsave15(k)=Dlow(N);
 end

  for k=1:31
    Fwn=(k-1)*0.05e6;
    [M_n M_u M_eddy Dlow T S sigma0]=...
       fourbox_Aredi(N,Kv,AI,25e6,Aredi,M_s,D0,T0s,T0n,T0l,T0d,S0s,S0n,S0l,S0d,Fws,Fwn,epsilon);
    Mnsave25(k)=M_n(N);
    Musave25(k)=M_u(N);
    Meddysave25(k)=M_eddy(N);
    dsigmasave25(k)=sigma0(N,1)-sigma0(N,3);
    Dlowsave25(k)=Dlow(N);
  end
 
   for k=1:31
    Fwn=(k-1)*0.05e6;
    [M_n M_u M_eddy Dlow T S sigma0]=...
       fourbox_Aredi(N,Kv,AI,35e6,Aredi,M_s,D0,T0s,T0n,T0l,T0d,S0s,S0n,S0l,S0d,Fws,Fwn,epsilon);
    Mnsave35(k)=M_n(N);
    Musave35(k)=M_u(N);
    Meddysave35(k)=M_eddy(N);
    dsigmasave35(k)=sigma0(N,1)-sigma0(N,3);
    Dlowsave35(k)=Dlow(N);
   end
 % Redo for "off" state  
 
 D0=100;
 
 for k=1:31
    Fwn=(k-1)*0.05e6;
    [M_n M_u M_eddy Dlow T S sigma0]=...
       fourbox_Aredi(N,Kv,AI,15e6,Aredi,M_s,D0,T0s,T0n,T0l,T0d,S0s,S0n,S0l,S0d,Fws,Fwn,epsilon);
    Mnsave15_low(k)=M_n(N);
    Musave15_low(k)=M_u(N);
    Meddysave15_low(k)=M_eddy(N);
    dsigmasave15_low(k)=sigma0(N,1)-sigma0(N,3);
    Dlowsave15_low(k)=Dlow(N);
 end

  for k=1:31
    Fwn=(k-1)*0.05e6;
    [M_n M_u M_eddy Dlow T S sigma0]=...
       fourbox_Aredi(N,Kv,AI,25e6,Aredi,M_s,D0,T0s,T0n,T0l,T0d,S0s,S0n,S0l,S0d,Fws,Fwn,epsilon);
    Mnsave25_low(k)=M_n(N);
    Musave25_low(k)=M_u(N);
    Meddysave25_low(k)=M_eddy(N);
    dsigmasave25_low(k)=sigma0(N,1)-sigma0(N,3);
    Dlowsave25_low(k)=Dlow(N);
  end
 
   for k=1:31
    Fwn=(k-1)*0.05e6;
    [M_n M_u M_eddy Dlow T S sigma0]=...
       fourbox_Aredi(N,Kv,AI,35e6,Aredi,M_s,D0,T0s,T0n,T0l,T0d,S0s,S0n,S0l,S0d,Fws,Fwn,epsilon);
    Mnsave35_low(k)=M_n(N);
    Musave35_low(k)=M_u(N);
    Meddysave35_low(k)=M_eddy(N);
    dsigmasave35_low(k)=sigma0(N,1)-sigma0(N,3);
    Dlowsave35_low(k)=Dlow(N);
   end
   
 figure(2)
 Fwflux=(0:30)*0.05;
 subplot(221)
 plot(Fwflux,Mnsave15/1e6,'-+b',Fwflux,Mnsave25/1e6,'-xk',Fwflux,Mnsave35/1e6,'-or')
 hold on
 plot(Fwflux,Mnsave15_low/1e6,'-+b',Fwflux,Mnsave25_low/1e6,'-xk',Fwflux,Mnsave35_low/1e6,'-or')
 xlabel('Freshwater flux in Sv')
 ylabel('Overturning in Sv')
 title('a:NH Overturning')
 grid on
 hold off
 subplot(222)
 plot(Fwflux,Meddysave15/1e6-15,'-+b',Fwflux,Meddysave25/1e6-25,'-xk',Fwflux,Meddysave35/1e6-35,'-or')
 hold on
 plot(Fwflux,Meddysave15_low/1e6-15,'-+b',Fwflux,Meddysave25_low/1e6-25,'-xk',Fwflux,Meddysave35_low/1e6-35,'-or')
 hold off
 xlabel('Freshwater flux in Sv')
 ylabel('Overturning in Sv')
 title('b:SH Overturning')
 grid on
 subplot(223)
 plot(Fwflux,Dlowsave15,'-+b',Fwflux,Dlowsave25,'-xk',Fwflux,Dlowsave35,'-or')
 hold on
 plot(Fwflux,Dlowsave15_low,'-+b',Fwflux,Dlowsave25_low,'-xk',Fwflux,Dlowsave35_low,'-or')
 hold off
 xlabel('Freshwater flux in Sv')
 ylabel('Depth in m')
 title('c:Low latitude thermocline depth')
 grid on
 subplot(224)
 plot(Fwflux,dsigmasave15,'-+b',Fwflux,dsigmasave25,'-xk',Fwflux,dsigmasave35,'-or')
 hold on
 plot(Fwflux,dsigmasave15_low,'-+b',Fwflux,dsigmasave25_low,'-xk',Fwflux,dsigmasave35_low,'-or')
 hold off
 xlabel('Freshwater flux in Sv')
 ylabel('Density in kg/m^3')
 title('d:Density difference N-Low')
 grid on
 legend('M_e_k=15 Sv','M_e_k=25 Sv','M_e_k=35 Sv','Location','northeast')

 
N=8000;
Kv=1e-5;
AI=1000;
D0=400;
epsilon=1.2e-4;
Fws=1e6;
T0n=2;
T0s=4;
T0d=3;
T0l=17;
 
S0n=35;
S0s=36;
S0d=34.5;
S0l=36;
M_s=15e6;
Meks=25e6;

 for k=1:31
    Fwn=(k-1)*0.05e6;
    [M_n M_u M_eddy Dlow T S sigma0]=...
       fourbox_Aredi(N,Kv,AI,Meks,500,M_s,D0,T0s,T0n,T0l,T0d,S0s,S0n,S0l,S0d,Fws,Fwn,epsilon);
    MnsaveAredi500(k)=M_n(N);
    MusaveAredi500(k)=M_u(N);
    MeddysaveAredi500(k)=M_eddy(N);
    dsigmasaveAredi500(k)=sigma0(N,1)-sigma0(N,3);
    DlowsaveAredi500(k)=Dlow(N);
 end

  for k=1:31
    Fwn=(k-1)*0.05e6;
    [M_n M_u M_eddy Dlow T S sigma0]=...
       fourbox_Aredi(N,Kv,AI,Meks,2000,M_s,D0,T0s,T0n,T0l,T0d,S0s,S0n,S0l,S0d,Fws,Fwn,epsilon);
    MnsaveAredi2000(k)=M_n(N);
    MusaveAredi2000(k)=M_u(N);
    MeddysaveAredi2000(k)=M_eddy(N);
    dsigmasaveAredi2000(k)=sigma0(N,1)-sigma0(N,3);
    DlowsaveAredi2000(k)=Dlow(N);
  end
  %Map out low manifold
  
  D0=100;
  
  for k=1:31
    Fwn=(k-1)*0.05e6;
    [M_n M_u M_eddy Dlow T S sigma0]=...
       fourbox_Aredi(N,Kv,AI,Meks,500,M_s,D0,T0s,T0n,T0l,T0d,S0s,S0n,S0l,S0d,Fws,Fwn,epsilon);
    MnsaveAredi500_low(k)=M_n(N);
    MusaveAredi500_low(k)=M_u(N);
    MeddysaveAredi500_low(k)=M_eddy(N);
    dsigmasaveAredi500_low(k)=sigma0(N,1)-sigma0(N,3);
    DlowsaveAredi500_low(k)=Dlow(N);
 end

  for k=1:31
    Fwn=(k-1)*0.05e6;
    [M_n M_u M_eddy Dlow T S sigma0]=...
       fourbox_Aredi(N,Kv,AI,Meks,2000,M_s,D0,T0s,T0n,T0l,T0d,S0s,S0n,S0l,S0d,Fws,Fwn,epsilon);
    MnsaveAredi2000_low(k)=M_n(N);
    MusaveAredi2000_low(k)=M_u(N);
    MeddysaveAredi2000_low(k)=M_eddy(N);
    dsigmasaveAredi2000_low(k)=sigma0(N,1)-sigma0(N,3);
    DlowsaveAredi2000_low(k)=Dlow(N);
  end
 
 figure(3)
 Fwflux=(0:30)*0.05;
 subplot(221)
 plot(Fwflux,MnsaveAredi500/1e6,'-+b',Fwflux,Mnsave25/1e6,'-xk',Fwflux,MnsaveAredi2000/1e6,'-or')
 hold on
 plot(Fwflux,MnsaveAredi500_low/1e6,'-+b',Fwflux,Mnsave25_low/1e6,'-xk',Fwflux,MnsaveAredi2000_low/1e6,'-or')
 hold off
 xlabel('Freshwater flux in Sv')
 ylabel('Overturning in Sv')
 title('a: NH Overturning')
 grid on
 subplot(222)
 plot(Fwflux,MeddysaveAredi500/1e6-25,'-+b',Fwflux,Meddysave25/1e6-25,'-xk',Fwflux,MeddysaveAredi2000/1e6-25,'-or')
 hold on
 plot(Fwflux,MeddysaveAredi500_low/1e6-25,'-+b',Fwflux,Meddysave25_low/1e6-25,'-xk',Fwflux,MeddysaveAredi2000_low/1e6-25,'-or')
 hold off
 xlabel('Freshwater flux in Sv')
 ylabel('Overturning in Sv')
 title('b: SH Overturning')
 grid on
 subplot(223)
 plot(Fwflux,DlowsaveAredi500,'-+b',Fwflux,Dlowsave25,'-xk',Fwflux,DlowsaveAredi2000,'-or')
 hold on
 plot(Fwflux,DlowsaveAredi500_low,'-+b',Fwflux,Dlowsave25_low,'-xk',Fwflux,DlowsaveAredi2000_low,'-or')
 hold off
 xlabel('Freshwater flux in Sv')
 ylabel('Depth in m')
 title('c: Low latitude thermocline depth')
 grid on
 subplot(224)
 plot(Fwflux,dsigmasaveAredi500,'-+b',Fwflux,dsigmasave25,'-xk',Fwflux,dsigmasaveAredi2000,'-or')
 hold on
 plot(Fwflux,dsigmasaveAredi500_low,'-+b',Fwflux,dsigmasave25_low,'-xk',Fwflux,dsigmasaveAredi2000_low,'-or')
 hold off
 xlabel('Freshwater flux in Sv')
 ylabel('Density in kg/m^3')
 title('d: Density difference N-Low')
 grid on
 legend('A_R_e_d_i=500','A_R_e_d_i=1000','A_R_e_d_i=2000','Location','northeast') 

N=4000;
Kv=1e-5;
AI=1000;
D0=400;
epsilon=1.2e-4;
Fws=1e6;
T0n=2;
T0s=4;
T0d=3;
T0l=17;
 
S0n=35;
S0s=36;
S0d=34.5;
S0l=36;
M_s=15e6;
Meks=25e6;

 for k=1:31
    Fwn=(k-1)*0.05e6;
    [M_n M_u M_eddy Dlow T S sigma0]=...
       fourbox_Aredi(N,Kv,AI,Meks,AI,M_s,D0,T0s,T0n,T0l,T0d,S0s,S0n,S0l,S0d,Fws,Fwn,epsilon/2);
    Mnsaveepsxp5(k)=M_n(N);
    Musaveepsxp5(k)=M_u(N);
    Meddysaveepsxp5(k)=M_eddy(N);
    dsigmasaveepsxp5(k)=sigma0(N,1)-sigma0(N,3);
    Dlowsaveepsxp5(k)=Dlow(N);
 end

  for k=1:31
    Fwn=(k-1)*0.05e6;
    [M_n M_u M_eddy Dlow T S sigma0]=...
       fourbox_Aredi(N,Kv,AI,Meks,AI,M_s,D0,T0s,T0n,T0l,T0d,S0s,S0n,S0l,S0d,Fws,Fwn,epsilon*2);
    Mnsaveepsx2(k)=M_n(N);
    Musaveepsx2(k)=M_u(N);
    Meddysaveepsx2(k)=M_eddy(N);
    dsigmasaveepsx2(k)=sigma0(N,1)-sigma0(N,3);
    Dlowsaveepsx2(k)=Dlow(N);
  end
 
  D0=100;
  
   for k=1:31
    Fwn=(k-1)*0.05e6;
    [M_n M_u M_eddy Dlow T S sigma0]=...
       fourbox_Aredi(N,Kv,AI,Meks,AI,M_s,D0,T0s,T0n,T0l,T0d,S0s,S0n,S0l,S0d,Fws,Fwn,epsilon/2);
    Mnsaveepsxp5_low(k)=M_n(N);
    Musaveepsxp5_low(k)=M_u(N);
    Meddysaveepsxp5_low(k)=M_eddy(N);
    dsigmasaveepsxp5_low(k)=sigma0(N,1)-sigma0(N,3);
    Dlowsaveepsxp5_low(k)=Dlow(N);
 end

  for k=1:31
    Fwn=(k-1)*0.05e6;
    [M_n M_u M_eddy Dlow T S sigma0]=...
       fourbox_Aredi(N,Kv,AI,Meks,AI,M_s,D0,T0s,T0n,T0l,T0d,S0s,S0n,S0l,S0d,Fws,Fwn,epsilon*2);
    Mnsaveepsx2_low(k)=M_n(N);
    Musaveepsx2_low(k)=M_u(N);
    Meddysaveepsx2_low(k)=M_eddy(N);
    dsigmasaveepsx2_low(k)=sigma0(N,1)-sigma0(N,3);
    Dlowsaveepsx2_low(k)=Dlow(N);
  end
  
 figure(4)
 Fwflux=(0:30)*0.05;
 subplot(221)
 plot(Fwflux,Mnsaveepsxp5/1e6,'-+b',Fwflux,Mnsave25/1e6,'-xk',Fwflux,Mnsaveepsx2/1e6,'-or')
 hold on
 plot(Fwflux,Mnsaveepsxp5_low/1e6,'-+b',Fwflux,Mnsave25_low/1e6,'-xk',Fwflux,Mnsaveepsx2_low/1e6,'-or')
 hold off
 grid on
 xlabel('Freshwater flux in Sv')
 ylabel('Overturning in Sv')
 title('a: NH Overturning')
 subplot(222)
 plot(Fwflux,Meddysaveepsxp5/1e6-25,'-+b',Fwflux,Meddysave25/1e6-25,'-xk',Fwflux,Meddysaveepsx2/1e6-25,'-or')
 hold on
 plot(Fwflux,Meddysaveepsxp5_low/1e6-25,'-+b',Fwflux,Meddysave25_low/1e6-25,'-xk',Fwflux,Meddysaveepsx2_low/1e6-25,'-or')
 hold off
 grid on
 xlabel('Freshwater flux in Sv')
 ylabel('Overturning in Sv')
 title('b: SH Overturning')
 subplot(223)
 plot(Fwflux,Dlowsaveepsxp5,'-+b',Fwflux,Dlowsave25,'-xk',Fwflux,Dlowsaveepsx2,'-or')
 hold on
 plot(Fwflux,Dlowsaveepsxp5_low,'-+b',Fwflux,Dlowsave25_low,'-xk',Fwflux,Dlowsaveepsx2_low,'-or')
 hold off
 grid on
 xlabel('Freshwater flux in Sv')
 ylabel('Depth in m')
 title('c: Low latitude thermocline depth')
 subplot(224)
 plot(Fwflux,dsigmasaveepsxp5,'-+b',Fwflux,dsigmasave25,'-xk',Fwflux,dsigmasaveepsx2,'-or')
 hold on
 plot(Fwflux,dsigmasaveepsxp5_low,'-+b',Fwflux,dsigmasave25_low,'-xk',Fwflux,dsigmasaveepsx2_low,'-or')
 hold off
 grid on
 xlabel('Freshwater flux in Sv')
 ylabel('Density in kg/m^3')
 title('d: Density difference N-Low')
 legend('\epsilon=0.6e-4','\epsilon=1.2e-4','\epsilon=2.4e-4') 

N=8000;
Kv=1e-5;
AI=1000;
D0=400;
epsilon=1.2e-4;
Fws=1e6;
T0n=2;
T0s=4;
T0d=3;
T0l=17;
Aredi=1000; 
S0n=35;
S0s=36;
S0d=34.5;
S0l=36;
M_s=15e6;
Meks=25e6;

 for k=1:31
    Fwn=(k-1)*0.05e6;
    [M_n M_u M_eddy Dlow T S sigma0]=...
       fourbox_Aredi(N,Kv,500,Meks,Aredi,M_s,D0,T0s,T0n,T0l,T0d,S0s,S0n,S0l,S0d,Fws,Fwn,epsilon);
   pause(0.1); 
   MnsaveAGM500(k)=M_n(N);
    MusaveAGM500(k)=M_u(N);
    MeddysaveAGM500(k)=M_eddy(N);
    dsigmasaveAGM500(k)=sigma0(N,1)-sigma0(N,3);
    DlowsaveAGM500(k)=Dlow(N);
 end

  for k=1:31
    Fwn=(k-1)*0.05e6;
    [M_n M_u M_eddy Dlow T S sigma0]=...
       fourbox_Aredi(N,Kv,2000,Meks,Aredi,M_s,D0,T0s,T0n,T0l,T0d,S0s,S0n,S0l,S0d,Fws,Fwn,epsilon);
    pause(0.1);
    MnsaveAGM2000(k)=M_n(N);
    MusaveAGM2000(k)=M_u(N);
    MeddysaveAGM2000(k)=M_eddy(N);
    dsigmasaveAGM2000(k)=sigma0(N,1)-sigma0(N,3);
    DlowsaveAGM2000(k)=Dlow(N);
  end

  D0=100;
  
  for k=1:31
    Fwn=(k-1)*0.05e6;
    [M_n M_u M_eddy Dlow T S sigma0]=...
       fourbox_Aredi(N,Kv,500,Meks,Aredi,M_s,D0,T0s,T0n,T0l,T0d,S0s,S0n,S0l,S0d,Fws,Fwn,epsilon);
   pause(0.1); 
   MnsaveAGM500_low(k)=M_n(N);
    MusaveAGM500_low(k)=M_u(N);
    MeddysaveAGM500_low(k)=M_eddy(N);
    dsigmasaveAGM500_low(k)=sigma0(N,1)-sigma0(N,3);
    DlowsaveAGM500_low(k)=Dlow(N);
 end

  for k=1:31
    Fwn=(k-1)*0.05e6;
    [M_n M_u M_eddy Dlow T S sigma0]=...
       fourbox_Aredi(N,Kv,2000,Meks,Aredi,M_s,D0,T0s,T0n,T0l,T0d,S0s,S0n,S0l,S0d,Fws,Fwn,epsilon);
    pause(0.1);
    MnsaveAGM2000_low(k)=M_n(N);
    MusaveAGM2000_low(k)=M_u(N);
    MeddysaveAGM2000_low(k)=M_eddy(N);
    dsigmasaveAGM2000_low(k)=sigma0(N,1)-sigma0(N,3);
    DlowsaveAGM2000_low(k)=Dlow(N);
  end

  
 figure(5)
 Fwflux=(0:30)*0.05;
 subplot(221)
 plot(Fwflux,MnsaveAGM500/1e6,'-+b',Fwflux,Mnsave25/1e6,'-xk',Fwflux,MnsaveAGM2000/1e6,'-or')
 hold on
 plot(Fwflux,MnsaveAGM500_low/1e6,'-+b',Fwflux,Mnsave25_low/1e6,'-xk',Fwflux,MnsaveAGM2000_low/1e6,'-or')
 hold off
 xlabel('Freshwater flux in Sv')
 ylabel('Overturning in Sv')
 title('a: NH Overturning')
 grid on
 subplot(222)
 plot(Fwflux,MeddysaveAGM500/1e6-25,'-+b',Fwflux,Meddysave25/1e6-25,'-xk',Fwflux,MeddysaveAGM2000/1e6-25,'-or')
 hold on
 plot(Fwflux,MeddysaveAGM500_low/1e6-25,'-+b',Fwflux,Meddysave25_low/1e6-25,'-xk',Fwflux,MeddysaveAGM2000_low/1e6-25,'-or')
 hold off
 xlabel('Freshwater flux in Sv')
 ylabel('Overturning in Sv')
 title('b: SH Overturning')
 grid on
 subplot(223)
 plot(Fwflux,DlowsaveAGM500,'-+b',Fwflux,Dlowsave25,'-xk',Fwflux,DlowsaveAGM2000,'-or')
 hold on
 plot(Fwflux,DlowsaveAGM500_low,'-+b',Fwflux,Dlowsave25_low,'-xk',Fwflux,DlowsaveAGM2000_low,'-or')
 hold off
 xlabel('Freshwater flux in Sv')
 ylabel('Depth in m')
 title('c: Low latitude thermocline depth')
 grid on
 subplot(224)
 plot(Fwflux,dsigmasaveAGM500,'-+b',Fwflux,dsigmasave25,'-xk',Fwflux,dsigmasaveAGM2000,'-or')
 hold on
 plot(Fwflux,dsigmasaveAGM500_low,'-+b',Fwflux,dsigmasave25_low,'-xk',Fwflux,dsigmasaveAGM2000_low,'-or')
 hold off
 xlabel('Freshwater flux in Sv')
 ylabel('Density in kg/m^3')
 title('d: Density difference N-Low')
 legend('A_G_M=500','A_G_M=1000','A_G_M=2000')
 grid on
 
 N=8000;
AI=1000;
D0=400;
epsilon=1.2e-4;
Fws=1e6;
T0n=2;
T0s=4;
T0d=3;
T0l=17;
Aredi=1000; 
Agm=1000;
S0n=35;
S0s=36;
S0d=34.5;
S0l=36;
M_s=15e6;
Meks=25e6;

 for k=1:31
    Fwn=(k-1)*0.05e6;
    [M_n M_u M_eddy Dlow T S sigma0]=...
       fourbox_Aredi(N,0,Agm,Meks,Aredi,M_s,D0,T0s,T0n,T0l,T0d,S0s,S0n,S0l,S0d,Fws,Fwn,epsilon);
   pause(0.1); 
   MnsaveKv0(k)=M_n(N);
    MusaveKv0(k)=M_u(N);
    MeddysaveKv0(k)=M_eddy(N);
    dsigmasaveKv0(k)=sigma0(N,1)-sigma0(N,3);
    DlowsaveKv0(k)=Dlow(N);
 end

  for k=1:31
    Fwn=(k-1)*0.05e6;
    [M_n M_u M_eddy Dlow T S sigma0]=...
       fourbox_Aredi(N,5e-5,Agm,Meks,Aredi,M_s,D0,T0s,T0n,T0l,T0d,S0s,S0n,S0l,S0d,Fws,Fwn,epsilon);
    pause(0.1);
    MnsaveKv05(k)=M_n(N);
    MusaveKv05(k)=M_u(N);
    MeddysaveKv05(k)=M_eddy(N);
    dsigmasaveKv05(k)=sigma0(N,1)-sigma0(N,3);
    DlowsaveKv05(k)=Dlow(N);
  end

  D0=100;
  
  for k=1:31
    Fwn=(k-1)*0.05e6;
    [M_n M_u M_eddy Dlow T S sigma0]=...
       fourbox_Aredi(N,0,Agm,Meks,Aredi,M_s,D0,T0s,T0n,T0l,T0d,S0s,S0n,S0l,S0d,Fws,Fwn,epsilon);
   pause(0.1); 
   MnsaveKv0_low(k)=M_n(N);
    MusaveKv0_low(k)=M_u(N);
    MeddysaveKv0_low(k)=M_eddy(N);
    dsigmasaveKv0_low(k)=sigma0(N,1)-sigma0(N,3);
    DlowsaveKv0_low(k)=Dlow(N);
 end

  for k=1:31
    Fwn=(k-1)*0.05e6;
    [M_n M_u M_eddy Dlow T S sigma0]=...
       fourbox_Aredi(N,5e-5,Agm,Meks,Aredi,M_s,D0,T0s,T0n,T0l,T0d,S0s,S0n,S0l,S0d,Fws,Fwn,epsilon);
    pause(0.1);
    MnsaveKv05_low(k)=M_n(N);
    MusaveKv05_low(k)=M_u(N);
    MeddysaveKv05_low(k)=M_eddy(N);
    dsigmasaveKv05_low(k)=sigma0(N,1)-sigma0(N,3);
    DlowsaveKv05_low(k)=Dlow(N);
  end
  
 figure(6)
 Fwflux=(0:30)*0.05;
 subplot(221)
 plot(Fwflux,MnsaveKv0/1e6,'-+b',Fwflux,Mnsave25/1e6,'-xk',Fwflux,MnsaveKv05/1e6,'-or')
 hold on
 plot(Fwflux,MnsaveKv0_low/1e6,'-+b',Fwflux,Mnsave25_low/1e6,'-xk',Fwflux,MnsaveKv05_low/1e6,'-or')
 hold off
 xlabel('Freshwater flux in Sv')
 ylabel('Overturning in Sv')
 title('a: NH Overturning')
 grid on
 subplot(222)
 plot(Fwflux,MeddysaveKv0/1e6-25,'-+b',Fwflux,Meddysave25/1e6-25,'-xk',Fwflux,MeddysaveKv05/1e6-25,'-or')
 hold on
 plot(Fwflux,MeddysaveKv0_low/1e6-25,'-+b',Fwflux,Meddysave25_low/1e6-25,'-xk',Fwflux,MeddysaveKv05_low/1e6-25,'-or')
 hold off
 xlabel('Freshwater flux in Sv')
 ylabel('Overturning in Sv')
 title('b: SH Overturning')
 grid on
 subplot(223)
 plot(Fwflux,DlowsaveKv0,'-+b',Fwflux,Dlowsave25,'-xk',Fwflux,DlowsaveKv05,'-or')
 hold on
 plot(Fwflux,DlowsaveKv0_low,'-+b',Fwflux,Dlowsave25_low,'-xk',Fwflux,DlowsaveKv05_low,'-or')
 hold off
 xlabel('Freshwater flux in Sv')
 ylabel('Depth in m')
 title('c: Low latitude thermocline depth')
 grid on
 subplot(224)
 plot(Fwflux,dsigmasaveKv0,'-+b',Fwflux,dsigmasave25,'-xk',Fwflux,dsigmasaveKv05,'-or')
 hold on
 plot(Fwflux,dsigmasaveKv0_low,'-+b',Fwflux,dsigmasave25_low,'-xk',Fwflux,dsigmasaveKv05_low,'-or')
 hold off
 xlabel('Freshwater flux in Sv')
 ylabel('Density in kg/m^3')
 title('d: Density difference N-Low')
 grid on
 legend('K_v=0','K_v=1e-5','K_v=5e-5','Location','southwest')
 
 figure(7)
 subplot(322)
 plot(dsigmasave15,Mnsave15/1e6,'-+b',dsigmasave25,Mnsave25/1e6,'-xk',dsigmasave35,Mnsave35/1e6,'-or')
 hold on
 plot(dsigmasave15_low,Mnsave15_low/1e6,'-+b',dsigmasave25_low,Mnsave25_low/1e6,'-xk',dsigmasave35_low,Mnsave35_low/1e6,'-or')
 hold off
 title('b:M_n vs. \Delta\rho, Varying M_e_k')
 ylabel('Overturning in Sv')
 %xlabel('Density difference in kg/m^3')
 axis([-4 3 -5 40]);grid on
 h=gca;set(h,'Xtick',(-5:5))
 legend('M_e_k^s=15','M_e_k^s=25','M_e_k^s=35','Location','northwest')

 subplot(324)
 plot(dsigmasaveAredi500,MnsaveAredi500/1e6,'-+b',dsigmasave25,Mnsave25/1e6,'-xk',dsigmasaveAredi2000,MnsaveAredi2000/1e6,'-or')
 hold on
 plot(dsigmasaveAredi500_low,MnsaveAredi500_low/1e6,'-+b',dsigmasave25_low,Mnsave25_low/1e6,'-xk',dsigmasaveAredi2000_low,MnsaveAredi2000_low/1e6,'-or')
 hold off
 title('d:M_n vs \Delta\rho, Varying A_R_e_d_i')
 ylabel('Overturning in Sv')
 xlabel('Density difference in kg/m^3')
 axis([-4 3 -5 40]);grid on
  h=gca;set(h,'Xtick',(-5:5))
 legend('A_R_e_d_i=500','A_R_e_d_i=1000','A_R_e_d_i=2000','Location','northwest')

 subplot(325)
 plot(dsigmasaveepsxp5,Mnsaveepsxp5/1e6,'-+b',dsigmasave25,Mnsave25/1e6,'-xk',dsigmasaveepsx2,Mnsaveepsx2/1e6,'-or')
 hold on
 plot(dsigmasaveepsxp5_low,Mnsaveepsxp5_low/1e6,'-+b',dsigmasave25_low,Mnsave25_low/1e6,'-xk',dsigmasaveepsx2_low,Mnsaveepsx2_low/1e6,'-or')
 hold off
 title('e:M_n vs \Delta\rho, Varying \epsilon')
 ylabel('Overturning in Sv')
 xlabel('Density difference in kg/m^3')
 axis([-4 3 -5 40]);grid on
  h=gca;set(h,'Xtick',(-5:5))
 legend('\epsilon=0.6e-4','\epsilon=1.2e-4','\epsilon=2.4e-4','Location','northwest')
 
 subplot(323)
 plot(dsigmasaveAGM500,MnsaveAGM500/1e6,'-+b',dsigmasave25,Mnsave25/1e6,'-xk',dsigmasaveAGM2000,MnsaveAGM2000/1e6,'-or')
 hold on
 plot(dsigmasaveAGM500_low,MnsaveAGM500_low/1e6,'-+b',dsigmasave25_low,Mnsave25_low/1e6,'-xk',dsigmasaveAGM2000_low,MnsaveAGM2000_low/1e6,'-or')
 hold off
 title('c:M_n vs \Delta\rho, Varying A_G_M')
 axis([-4 3 -5 40]);grid on
 legend('A_G_M=500','A_G_M=1000','A_G_M=2000','Location','northwest')
 ylabel('Overturning in Sv')
 %xlabel('Density difference in kg/m^3')
 h=gca;set(h,'Xtick',(-5:5))
 
 subplot(321)
 plot(dsigmasaveKv0,MnsaveKv0/1e6,'-+b',dsigmasave25,Mnsave25/1e6,'-xk',dsigmasaveKv05,MnsaveKv05/1e6,'-or')
 hold on
 plot(dsigmasaveKv0_low,MnsaveKv0_low/1e6,'-+b',dsigmasave25_low,Mnsave25_low/1e6,'-xk',dsigmasaveKv05_low,MnsaveKv05_low/1e6,'-or')
 hold off
 title('a:M_n vs \Delta\rho, Varying K_v')
 axis([-4 3 -5 40]);grid on
 legend('K_v=0','K_v=1e-5','K_v=5e-5','Location','northwest')
 ylabel('Overturning in Sv')
 %xlabel('Density difference in kg/m^3')
 h=gca;set(h,'Xtick',(-5:5))
 
 
 figure(8)
 subplot(221)
 plot(Fwflux+0.075,dsigmasaveKv0,'-+b',Fwflux,dsigmasave25,'-xk',Fwflux-0.15,dsigmasaveKv05,'-or')
 hold on
 plot(Fwflux+0.075,dsigmasaveKv0_low,'-+b',Fwflux,dsigmasave25_low,'-xk',Fwflux-0.15,dsigmasaveKv05_low,'-or')
 plot(0.5,1.5,'og','MarkerSize',10,'LineWidth',3)
 hold off
 title('a:Density difference vs. Adjusted F_w^n, Varying K_v')
 axis([-0.25 1.75 -4 3]);grid on
 legend('K_v=0','K_v=1e-5','K_v=5e-5','Location','southwest')
 ylabel('Density difference in kg/m^3')
 xlabel('Total Freshwater flux-Flux adjustment')
 h=gca;set(h,'Ytick',(-5:5))
 
 subplot(222)
 plot(Fwflux+0.12,dsigmasave15,'-+b',Fwflux,dsigmasave25,'-xk',Fwflux-0.1,dsigmasave35,'-or')
 hold on
 plot(Fwflux+0.12,dsigmasave15_low,'-+b',Fwflux,dsigmasave25_low,'-xk',Fwflux-0.1,dsigmasave35_low,'-or')
 plot(0.5,1.5,'og','MarkerSize',10,'LineWidth',3)
 hold off
 title('b:Density difference vs. Adjusted F_w^n, Varying M_e_k')
 axis([-0.25 1.75 -4 3]);grid on
 legend('M_e_k=15 Sv','M_e_k=25 Sv','M_e_k=35 Sv','Location','southwest')
 ylabel('Density difference in kg/m^3')
 xlabel('Total Freshwater flux-Flux adjustment')
 h=gca;set(h,'Ytick',(-5:5))
 
 subplot(223)
 plot(Fwflux-0.1,dsigmasaveAGM500,'-+b',Fwflux,dsigmasave25,'-xk',Fwflux+0.12,dsigmasaveAGM2000,'-or')
 hold on
 plot(Fwflux-0.1,dsigmasaveAGM500_low,'-+b',Fwflux,dsigmasave25_low,'-xk',Fwflux+0.12,dsigmasaveAGM2000_low,'-or')
 plot(0.5,1.5,'og','MarkerSize',10,'LineWidth',3)
 hold off
 title('c:Density difference vs. Adjusted F_w^n, Varying A_G_M')
 axis([-0.25 1.75 -4 3]);grid on
 legend('A_G_M=500','A_G_M=1000','A_G_M=2000','Location','southwest')
 ylabel('Density difference in kg/m^3')
 xlabel('Total Freshwater flux-Flux adjustment')
 h=gca;set(h,'Ytick',(-5:5))
 
 subplot(224)
 plot(Fwflux-0.08,dsigmasaveepsxp5,'-+b',Fwflux,dsigmasave25,'-xk',Fwflux+0.07,dsigmasaveepsx2,'-or')
 hold on
 plot(Fwflux-0.08,dsigmasaveepsxp5_low,'-+b',Fwflux,dsigmasave25_low,'-xk',Fwflux+0.07,dsigmasaveepsx2_low,'-or')
 plot(0.5,1.5,'og','MarkerSize',10,'LineWidth',3)
 hold off
 title('d:Density difference vs. Adjusted F_w^n, Varying \epsilon')
 axis([-0.25 1.75 -4 3]);grid on
 legend('\epsilon=0.6e-4','\epsilon=1.2e-4','\epsilon=2.4e-4','Location','southwest')
 ylabel('Density difference in kg/m^3')
 xlabel('Total Freshwater flux-Flux adjustment')
 h=gca;set(h,'Ytick',(-5:5))