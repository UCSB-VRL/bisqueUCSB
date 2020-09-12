function [X_CON]=Mutual_CV_Multi_TPS(phi,Prob,mu,mask,MKinv, X_CON)

[dummy total_num_of_cells] = size(phi);
[NCONPTS dummy dummy2]=size(X_CON);
[row1 col1 dummy]=size(phi{1});
epsilon=0.01;
deltat=0.5;

NCONPTS=NCONPTS-3;
dT_dh=zeros(NCONPTS,2);
 
% 	%Here we begin the steepest descent along the TPS parameters
% 

for index=1:1:total_num_of_cells
    [Phi_out2 mask2 Weights] = CanvasWarpTPS(phi{index}, MKinv, X_CON, [row1; col1]);
    [dy_Phi2 dx_Phi2]=gradient(Phi_out2);
    
    for j=1:1:col1
        for i=1:1:row1
            if(mask(i,j)==1)
                force=-0.1*Prob{index}(i,j);
                del=delta(Phi_out2(i,j),epsilon);
                for kk=1:1:NCONPTS
						dT_dh(kk,1)=dT_dh(kk,1)+force*del*dx_Phi2(i,j)*MKinv(i+(j-1)*row1,kk);
						dT_dh(kk,2)=dT_dh(kk,2)+force*del*dy_Phi2(i,j)*MKinv(i+(j-1)*row1,kk);
                end
            end
        end
    end
end

NaNflag=nnz(isnan(dT_dh));
 
if(NaNflag==0)
    for kk=1:1:NCONPTS
        X_CON(kk,1)=X_CON(kk,1)+1*deltat*dT_dh(kk,1);
        X_CON(kk,2)=X_CON(kk,2)+1*deltat*dT_dh(kk,2);
    end
end

return;

function [delt]=delta(z,epsilon)
    delt=(1/(1+(z*z)/(epsilon*epsilon)));
return; 

% 
% double heaviside(double z, double epsilon)
% {
% 
% 
% 	return (0.5*(1+2/PI*atan(z/epsilon)));
% }