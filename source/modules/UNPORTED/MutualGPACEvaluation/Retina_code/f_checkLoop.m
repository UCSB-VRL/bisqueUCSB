function [loop_ind,theta] = f_checkLoop(P,dp)

% [loop_ind,theta] = f_checkLoop(P,dp)
% Determines if the is a possible loop in the snake.  Not 100% accurate, but
% saves time over having to use f_detectLoop everytime.
%
% INPUT:
%   P = N x 2 snake vertices
%   dp = scalar: spacing of snake vertices
% OUTPUT:
%   loop_ind = 1 if loop, 0 if no loop
%   theta = total winding number;
%
% Nhat Vu
% 01.09.2007

npt = size(P,1);

xp = [P(2:npt,1); P(npt,1)];
xm = [P(1,1); P(1:npt-1,1)];
yp = [P(2:npt,2); P(npt,2)];
ym = [P(1,2); P(1:npt-1,2)];

dx = (xp - xm)./(2*dp);
dy = (yp - ym)./(2*dp);

dxx = (xp - 2*P(:,1) + xm)./(dp^2);
dyy = (yp - 2*P(:,2) + ym)./(dp^2);

dtheta = (dx.*dyy - dy.*dxx)./(dx.^2 + dy.^2);

theta = sum(dtheta);

loop_ind = abs(theta) > 1;