function [f,R] = f_InternalForce(P)

% [f,R] = f_InternalForce(P) computes the curvature based internal force at
% points P along a curve.
%
% INPUT:
%   P = N x 2 xy coordinates of N points
%
% OUTPUT
%   R = N x 2 xy components of normal vectors at P
%   f = N x 1 curvature based force
%
% Nhat Vu (modified from Pratim Ghosh)
% 12.22.2006

% get the normal vectors and curvature of P
[R,C] = f_getNormalCurvature(P);

% discrete filter
kernel = [-0.5 1 -0.5];

% project curvature onto normal before filtering
c_project = sum(C.*R,2);

% f = filter(kernel,1,c_project);
f = c_project;

% c_project = [c_project(1); c_project; c_project(end)];
% f = conv(c_project,kernel);
% f = f(3:end-2);