function [line_coord,line_ind] = f_pt2line(P,im_size)

% [line_coord,line_ind] = f_pt2line(P,im_size)
% Create the indices of the line containing P and the coordinates (r,c) of
% the line.
%
% INPUT:
%   P = N x 2 (row,col) coordinates of points
%   im_size = output of size(img_R)
%
% OUTPUT:
%   line_ind = N x 1 indices of line
%   line_coord = N x 2 (row,col) coordinates of line
%
%
% Nhat Vu
% 01.11.2007

r = im_size(1);
c = im_size(2);

% extend P to border if not at border
if P(1,1) ~= 1,
    P = [1 P(1,2); P];
end
if P(end,1) ~= r,
    P = [P; r P(end,2)];
end

% resample at subpixel length away
dp = 0.5;
P = f_ResampleCurve(P,dp);
line_coord = P;

if nargout == 2,
    
    % ceiling and get rid of redundant points
    P = ceil(P);
    [Ptemp,P_ind] = unique(P,'rows');

    % reorder point into original order
    P_ind = sort(P_ind);
    xy_line = P(P_ind,:);
    line_ind = sub2ind(im_size,xy_line(:,1),xy_line(:,2));
end