function se=mt_gauss_kernel(L,theta,sigma)
%--------------------------------------------------------------------------
%  mt_gauss_kernel - launch Gauss kernel calculation algorithm
%
%       se=gauss_kernel(theta,L,sigma,size_se)
%
%       'L'         - input length of kernel
%       'theta'     - input theta value: theta=pi/4
%       'sigma'     - input sigma value: sigma=2.0
%       'se'        - output kernel matrix
%
% Boguslaw Obara <ngobara@cyf-kr.edu.pl, obara@ece.ucsb.edu>
%--------------------------------------------------------------------------

%--------------------------------------------------------------------------
% clc;
% theta=pi/4;
% sigma=2.0; 
% L=9.0;
% se=gauss_kernel(L,theta,sigma);
%--------------------------------------------------------------------------
    x_size=0; sum=0.0;
    start=-(L-1); stop=(L-1);
	size=abs(start)+abs(stop)+1;
	K=zeros(size,size);
  	se=zeros(size,size);
%--------------------------------------------------------------------------
    for x=start:stop
        for y=start:stop
            u=double(x)*cos(theta)-double(y)*sin(theta);
            v=double(x)*sin(theta)+double(y)*cos(theta);	
            if (abs(u)<=3.0*sigma && abs(v)<=L/2.0) 
                K(x+abs(start)+1,y+abs(start)+1)=-exp(-(u*u)/(2.0*sigma*sigma));
                x_size=x_size+1;
            else
                K(x+abs(start)+1,y+abs(start)+1)=0.0;
            end
        end
    end
%--------------------------------------------------------------------------
    for x=start:stop
        for y=start:stop
            sum=sum+K(x+abs(start)+1,y+abs(start)+1);
        end
    end
    me=sum/double((x_size));
%--------------------------------------------------------------------------
    for x=start:stop
        for y=start:stop
            u=double(x)*cos(theta)-double(y)*sin(theta);
            v=double(x)*sin(theta)+double(y)*cos(theta);	
            if abs(u)<=3*sigma && abs(v)<=L/2
                %se(x+abs(start)+1,y+abs(start)+1) = int16(10.0*(K(x+abs(start)+1,y+abs(start)+1)-me));
                se(x+abs(start)+1,y+abs(start)+1)=(K(x+abs(start)+1,y+abs(start)+1)-me);
            else
                %se(x+abs(start)+1,y+abs(start)+1) = int16(0.0);
                se(x+abs(start)+1,y+abs(start)+1)=0.0;
            end
        end
    end
%--------------------------------------------------------------------------
end