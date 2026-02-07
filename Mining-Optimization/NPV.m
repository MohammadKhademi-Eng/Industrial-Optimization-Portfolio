function npv=NPV(n) 
        
           
        
        global NFE;
        if isempty(NFE)
            NFE=0;
        end
        
        NFE=NFE+1;

        Qm1=12000000;    
        Qm=12000000;
        Z=0;
        
        for j=1:15 
         NPV=0;
         s1=775;
         Qpzn=150000;
         Qppb=60000;
         s2=435;
         m=1;
         Q=1000000;
         c=16.25;
         Qk=500000;
         r1=525;
         r2=220;
         f=10000000;
         d=0.2;
         yzn=0.8;
         ypb=0.6;
         e=1;
         q1 = 15;
         q2 = 14;
         l = q1+q2;
         xu1 = 30;
         xl1 = 0;
         xu2 = 16;
         xl2 = 0;
         
         gzn=[0 4 7 10 14 17 20 24 27 30];
         gpb=0:4:16;
         
         Q1=[12000000 6925000 4630000 3015000 1795000;11628000 6803000 4618000 3008000 1793000;10518000 6593000 4508000 2908000 1763000;9458000 6233000 4248000 2698000 1613000;8603000 5563000 3748000 2308000 1243000;7328000 4788000 3143000 1873000 898000;5788000 3818000 2563000 1443000 618000;3293000 2223000 1738000 888000 253000;1828000 1178000 893000 293000 28000;513000 213000 98000 38000 3000];
         gavgzn=[18.0603 19.7175 20.0994 18.7633 16.9636;18.5521 20.0132 20.1432 18.7995 16.9792;19.9452 20.4827 20.5084 19.2706 17.1786;21.2789 21.1679 21.2239 20.0662 17.9224 ;22.215 22.2949 22.4846 21.4649 19.7508 ;23.4895 23.481 23.9427 22.9665 21.5684;24.8006 24.7559 25.199 24.3193 22.9903;27.332 27.1293 26.9405 26.175 25.3711;29.1212 28.8375 28.4533 28.0361 28.6746;31.5825 31.0791 30.855 30.6734 30.13];
         gavgpb=[8.3006 12.9737 16.6563 20.4633 24.5442;8.4904 13.1106 16.66 20.468 24.5401;9.0347 13.1883 16.6856 20.616 24.6146;9.2268 12.9589 16.3831 20.3114 24.2654;8.9311 12.6881 16.1259 20.2228 25.1779;8.5601 11.9712 15.3295 19.2165 24.3741;8.3442 11.5999 14.5485 18.3588 23.5196;8.5365 11.6602 13.314 16.7192 22.5525;7.2564 10.15 11.4712 14.8914 21.7693;4.6139 8.3237 11.4024 14.6274 20.43];
         Q2=Q1./12000000;
         Q3=Q2.*Z;
         Q4=Q1-Q3;
         
         for k=1:e
              mat_pool(k,:) = round(rand(1,l));
         end
          
         for k=1:e
              xzn = xl1+(xu1-xl1)/(2^q1-1)*bin2dec(num2str(mat_pool(k,1:q1)));
              xpb = xl2+(xu2-xl2)/(2^q2-1)*bin2dec(num2str(mat_pool(k,q1+1:l)));
           
              Qc=interp2(gpb,gzn,Q4,xpb,xzn);
              gzn1=interp2(gpb,gzn,gavgzn,xpb,xzn);
              gpb1=interp2(gpb,gzn,gavgpb,xpb,xzn);
              Qrzn=(Qc*(gzn1/100)*yzn);
              Qrpb=(Qc*(gpb1/100)*ypb);
   
      V=[];
     for q=1:50
         
     if isempty(V)
               V=0;
           else
               V=npv;
     end
     
     
     vm=(s1-r1)*Qrzn+(s2-r2)*Qrpb-c*Qc-m*Qm-((f+V*d)*Qm)/Q;
     vc=(s1-r1)*Qrzn+(s2-r2)*Qrpb-c*Qc-m*Qm-((f+V*d)*Qc)/Qk;
     vrzn=(s1-r1)*Qrzn+(s2-r2)*Qrpb-c*Qc-m*Qm-((f+V*d)*Qrzn)/Qpzn;
     vrpb=(s1-r1)*Qrzn+(s2-r2)*Qrpb-c*Qc-m*Qm-((f+V*d)*Qrpb)/Qppb;
     ve1=[vm,vc,vrzn,vrpb];
     
     vbest=min(ve1);
     
      if vbest==vm
        T=Qm1/Q;
    qm=Q;
    qc=Qc/T;
    if qc>Qk
        qc=Qk;
    end
     if qm>=Qm1
        qm=Qm1;
        qc=Qc;
    end
    qr1=qc*yzn*gzn1/100;
    qr2=qc*ypb*gpb1/100;
    if qr1>Qpzn
        qr1=Qpzn;
    end
    if qr2>Qppb
        qr2=Qppb;
    end
    pv=((s1-r1)*qr1)+((s2-r2)*qr2)-(c*qc)-(m*qm)-f;
    npv=pv*((((1+d)^T)-1)/(d*((1+d)^T)));
    elseif vbest==vc
        T=Qc/Qk;
    qc=Qk;
    qm=Qm1/T;
     if qm>Q
        qm=Q;
     end
      if qm>=Qm1
        qm=Qm1;
        qc=Qc;
      end
    qr1=qc*yzn*gzn1/100;
    qr2=qc*ypb*gpb1/100;
    if qr1>Qpzn
        qr1=Qpzn;
    end
    if qr2>Qppb
        qr2=Qppb;
    end
    pv=((s1-r1)*qr1)+((s2-r2)*qr2)-(c*qc)-(m*qm)-f;
    npv=pv*((((1+d)^T)-1)/(d*((1+d)^T)));
    elseif vbest==vrzn
        T=Qrzn/Qpzn;
    qm=Qm1/T;
    qc=Qc/T;
     if qm>Q
        qm=Q;
     end
      if qc>Qk
        qc=Qk;
      end
       if qm>=Qm1
        qm=Qm1;
        qc=Qc;
       end
    qr1=Qpzn;
    qr2=qc*ypb*gpb1/100;
    if qr1>Qpzn
        qr1=Qpzn;
    end
    if qr2>Qppb
        qr2=Qppb;
    end
    pv=((s1-r1)*qr1)+((s2-r2)*qr2)-(c*qc)-(m*qm)-f;
    npv=pv*((((1+d)^T)-1)/(d*((1+d)^T)));
    elseif vbest==vrpb
        T=Qrpb/Qppb;
    qm=Qm1/T;
    qc=Qc/T;
     if qm>Q
        qm=Q;
     end
     if qc>Qk
        qc=Qk;
     end
      if qm>=Qm1
        qm=Qm1;
        qc=Qc;
      end
    qr1=qc*yzn*gzn1/100;
    qr2=Qppb;
    if qr1>Qpzn
        qr1=Qpzn;
    end
    if qr2>Qppb
        qr2=Qppb;
    end
    pv=((s1-r1)*qr1)+((s2-r2)*qr2)-(c*qc)-(m*qm)-f;
    npv=pv*((((1+d)^T)-1)/(d*((1+d)^T)));
    
      end
     
        
        if (npv<0)
            npv=0;
            break;
        end
        
        
        
        if (V-npv==0)
            break;
        else 
            continue;
        end
        
     end
     
     NPV(k,1)=npv;
     best=max(NPV);
    
     qm1(k,1)=qm;
     qc1(k,1)=qc;
     qr11(k,1)=qr1;
     qr21(k,1)=qr2;
     PV(k,1)=pv;
     F(k,1)=vbest;
     
     n=[xzn,xpb];
     
     disp(n)
     
         end
        
end