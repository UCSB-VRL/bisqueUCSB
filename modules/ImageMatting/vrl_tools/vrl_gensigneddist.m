function [b bx by]=vrl_gensigneddist(a)

b = ones(size(a));
% a=flipud(a);
b(a>0) = -1;   
b = -double((b>0).*(bwdist(b<0)-0.5)-(b<0).*(bwdist(b>0)-0.5));

[bx by] = gradient(b);

% phi = ones(100,100);
% phi(10:40,10:40) = -1;
% figure;imagesc(phi);
% phi=flipud(phi);
% phi1 = double((phi > 0).*(bwdist(phi < 0)-0.5) - (phi < 0).*(bwdist(phi > 0)-0.5));
% figure;surf(-phi1);
% figure;contour(phi1, [0 0], 'r');