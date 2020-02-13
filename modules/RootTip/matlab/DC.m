function [direc] = DC(I)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% This code will find the direction that the root is coming from.
% authored last at: June 21, 2007
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% setup
IDX = 1:50;
h = fspecial('gaussian',[10 1],5);
U = [];

% sample from the left
V = I(:,IDX);
V = mean(V,2);
V = interp1(1:1:size(V,1),V,linspace(1,size(V,1),1000));
U = [U;V];

% sample from the right
I = fliplr(I);
V = I(:,IDX);
V = mean(V,2);
V = interp1(1:1:size(V,1),V,linspace(1,size(V,1),1000));
U = [U;V];

% sample from the top/bottom
I = I';
V = I(:,IDX);
V = mean(V,2);
V = interp1(1:1:size(V,1),V,linspace(1,size(V,1),1000));
U = [U;V];

% sample from the top/bottom
I = fliplr(I);
V = I(:,IDX);
V = mean(V,2);
V = interp1(1:1:size(V,1),V,linspace(1,size(V,1),1000));
U = [U;V];

% find the outlier
u = mean(U(:),1);
for i = 1:size(U,1)
    D(i) = norm(U(i,:)-u*ones(1,1000),2);
end
[JUNK direc] = max(D);

