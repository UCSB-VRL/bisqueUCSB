function [R,C] = f_getNormalCurvature(P)

% [R,C] = f_getNormalCurvature(P) computes the normal vector along the parametric points
% P, where P are points on a curve.  Also return the curvature vector C at
% each point.
%
% INPUT:
%   P = N x 2 xy coordinates of N points
%
% OUTPUT
%   R = N x 2 xy components of normal vectors at P
%   C = N x 2 xy components of curvature vectors
%
% Nhat Vu (modified from Pratim Ghosh)
% 12.22.2006

% number of points
N = size(P,1);

% difference vectors between points then normalize
D = P(2:N,:)-P(1:N-1,:);
D = D./repmat(sqrt(sum(D.^2,2)),[1 2]);
n_D = size(D,1);

% curvature (first and last is 0)
C = zeros(N,2);
C(2:N-1,:) = D(2:n_D,:) - D(1:n_D-1,:);

% tangent direction (first and last is same as D) then normalize
T = zeros(N,2);
T(1,:) = D(1,:);
T(2:N-1,:) = D(2:n_D,:) + D(1:n_D-1,:);;
T(N,:) = D(n_D,:);
T = T./repmat(sqrt(sum(T.^2,2)),[1 2]);

% normal direction is rotation of 90 degrees
rotMat = [0 1;-1 0];
R = T*rotMat';