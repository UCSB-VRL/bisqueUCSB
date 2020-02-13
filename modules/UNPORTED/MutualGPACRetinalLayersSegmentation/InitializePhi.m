function [Phi] = InitializePhi(size, row, col)

%Calculates the initial profile of the function phi with number of zero
%level set curves depending on the parameter size.
%The first input size is the size of each tile with a one zero level set
%curve
%row and column are the desired dimension of Phi 
%
%Author Luca Bertelli 
%Vision Research Lab 
%University of California, Santa Barbara
%lbertelli@ece.ucsb.edu

%Definition of the initial function profile

%Number of Grid Points
N=size;

for i=1:1:N
    for j=1:1:N
        tile(i,j)=-(sqrt((2*(i-1)/(N-1)-1)^2+(2*(j-1)/(N-1)-1)^2)-0.7);
    end
end

Phi=zeros(row,col);


% %This is with linear extrapolation
% n_tiles_r=floor(row/N);
% n_tiles_c=floor(col/N);
% 
% 
% for i=1:1:n_tiles_r
%     for j=1:1:n_tiles_c
%         Phi((i-1)*N+1:i*N,(j-1)*N+1:j*N)=tile;
%     end
% end
% 
% 
% 
% %Linear extrapolation if nocovered the whole domain
% 
% gap_r=row-n_tiles_r*N;
% gap_c=col-n_tiles_c*N;
% 
% if (gap_r>0)
%     for i=1:1:gap_r
%         Phi(n_tiles_r*N+i,:)=Phi(n_tiles_r*N+i-1,:)+ sign(Phi(n_tiles_r*N+i-1,:)).*abs(Phi(n_tiles_r*N+i-1,:)-Phi(n_tiles_r*N+i-2,:));
%     end
% end
% 
% if (gap_c>0)
%     for i=1:1:gap_c
%         Phi(:,n_tiles_c*N+i)=Phi(:,n_tiles_c*N+i-1)+ sign(Phi(:,n_tiles_c*N+i-1)).*abs(Phi(:,n_tiles_c*N+i-1)-Phi(:,n_tiles_c*N+i-2));
%     end
% end


%this is for without linear extrapolation
n_tiles_r=ceil(row/N);
n_tiles_c=ceil(col/N);

Phi_temp=zeros(size*n_tiles_r,size*n_tiles_c);

for i=1:1:n_tiles_r
    for j=1:1:n_tiles_c
        Phi_temp((i-1)*N+1:i*N,(j-1)*N+1:j*N)=tile;
    end
end

Phi=Phi_temp(1:row,1:col);


