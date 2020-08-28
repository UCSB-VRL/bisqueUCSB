function [Ib mask Weights] = CanvasWarpTPS(I, MK_inv, X_CON, size_c)
% function [Ib mask] = CanvasWarpTPS(I, M, K_inv, X_CON, size_c)
%
% Warps an image I onto the canvas of size size_c
% using a Thin Plate Splines warping model
% For the meaning of the matrix MK_inv (M*K_inv) we refer to the CVPR paper by
% Jongwoo Lim and Ming-Hsuan Yang "A Direct Method for Modeling Non-Rigid 
% Motion with Thin Plate Spline".
% X_CON position of the transformed control points.
%
% Luca Bertelli - lbertelli@ece.ucsb.edu
% version 0.01
% Vision Research Lab
% University of California, Santa Barbara
% March 2007

X_PRIM=MK_inv*X_CON;


x_min=1;
y_min=1;
x_max=size_c(1,1);
y_max=size_c(2,1);
N_channels = size(I, 3);
Ib = zeros(x_max, y_max, N_channels,'double');
mask=zeros(x_max, y_max, 1, 'double');
Weights=zeros(x_max, y_max, 1, 'double');
debug = false;

[n2,m2,l]=size(I);
X=zeros(n2*m2,2);
 for j=1:1:m2
     for i=1:1:n2
         X(i+(j-1)*n2,:)=[i-1 j-1];
     end
 end
 
%  XX=[X ones(100*100,1)];
%  XX=XX';
%  XXX=H*XX;
%  XXX=XXX';
%  XXX=XXX(:,1:2);
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% forward project the image onto the canvas
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
X1_prime = [1; 1];
X2_prime = [size(I,1); size(I,2)];

X1 = (X_PRIM(1,:))'+1;
X2 = (X_PRIM(end,:))'+1;

% compute the bounding box of the image I warped back onto the canvas
xb_min = inf;
yb_min = inf;
xb_max = -inf;
yb_max = -inf;

if (xb_min > X1(1)), xb_min = X1(1); end;
if (xb_min > X2(1)), xb_min = X2(1); end;
if (xb_max < X1(1)), xb_max = X1(1); end;
if (xb_max < X2(1)), xb_max = X2(1); end;

if (yb_min > X1(2)), yb_min = X1(2); end;
if (yb_min > X2(2)), yb_min = X2(2); end;
if (yb_max < X1(2)), yb_max = X1(2); end;
if (yb_max < X2(2)), yb_max = X2(2); end;

xb_min = round(xb_min);
xb_max = round(xb_max);
yb_min = round(yb_min);
yb_max = round(yb_max);

%  fprintf('\nWarping frame from (%f,%f) to (%f,%f)\n', xb_min, yb_min, xb_max, yb_max);

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% warp
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

for k=1:1:n2*m2
    
    x_prime=X_PRIM(k,1);
    y_prime=X_PRIM(k,2);
%      x_prime=XXX(k,1);
%      y_prime=XXX(k,2);
    
    x=X(k,1);
    y=X(k,2);
    
    xx_prime = round(x_prime);
    yy_prime = round(y_prime);
    
    if (xx_prime+1>=1 && xx_prime+1<=x_max && yy_prime+1>=1 && yy_prime+1<=y_max)
        
        dx = x_prime - xx_prime;
        dy = y_prime - yy_prime;
        dist=sqrt(dx^2+dy^2);

        max_d=sqrt(2);
        F=double(I(x+1,   y+1 ,  :));
        Ib(xx_prime+1, yy_prime+1, :) = Ib(xx_prime+1, yy_prime+1, :) + (max_d-dist)*F;
        Weights(xx_prime+1,yy_prime+1)=Weights(xx_prime+1,yy_prime+1)+(max_d-dist);
        mask(xx_prime+1,yy_prime+1)=1; 
    
    end
    
end

totNan=0;

for i = 1:1:x_max
    for j = 1:1:y_max
        if(mask(i,j)==1)
            Ib(i,j,:)=Ib(i,j,:)/Weights(i,j);
        else
            Ib(i,j,:)=NaN*ones(size(Ib(i,j,:)));
            totNan=totNan+1;
        end
    end
end

if (totNan~=0)
    
    Ib=inpaint_nans(Ib);

%     pw = 1:30; % possible widths
%     sigma=1.5;
%     GaussianDieOff = .0001;  
%     ssq = sigma^2;
%     width = find(exp(-(pw.*pw)/(2*ssq))>GaussianDieOff,1,'last');
%     if isempty(width)
%     width = 1;  % the user entered a really small sigma
%     end
% 
%     t = (-width:width);
%     gau = exp(-(t.*t)/(2*ssq))/(sqrt(2*pi*ssq)); % the gaussian 1D filter
%     gau=gau./sum(gau);
%     [x,y]=meshgrid(-width:width,-width:width);
% 
%     %smooth the image out
%     aSmooth=imfilter(Ib,gau,'conv','replicate');   % run the filter accross rows
%     aSmooth=imfilter(aSmooth,gau','conv','replicate');
% 
%     Ib=aSmooth;
end


return