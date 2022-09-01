function [tip_distance] = f_tip_distance(A, B)

% function [tip_distance] = f_tip_distance(A, B)
% 
% This function simply calculates the distance between two points
% 
% inputs:
% 
%   A should be in (x,y) format
%   B should be in (x,y) format
% 
% output:
% 
%   tip_distance is a scalar
% 
%  jose freire 8/19/2007
%  jmhfreire@gmail.com

tip_distance = sqrt(((A(:,1)-B(:,1))^2)+((A(:,2)-B(:,2))^2));

return