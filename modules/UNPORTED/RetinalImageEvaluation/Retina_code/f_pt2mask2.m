function [line_ind,xy_line,mask] = f_pt2mask2(P,im_size,flag_side)

% [line_ind,xy_line,mask]=f_pt2mask2(P,im_size,flag_side)
% Create the indices of the line containing P and the binary mask on the
% left or right of the line.
%
% INPUT:
%   P = N x 2 (row,col) coordinates of points
%   im_size = output of size(img_R)
%   flag_side = 0 (left) or 1 (right)
%
% OUTPUT:
%   line_ind = indices of line
%   mask = binary image with 1's on left or right of line
%
% EXAMPLE:
%   [line_ind,mask] = f_pt2mask(P,size(img_R),0)
%
%   img1 = logical(zeros(size(img_R)));
%   img1(line_ind) = 1;
%   figure; imshow(img1);
%   figure; imshow(mask);
%
% Nhat Vu
% 12.20.2006

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

% ceiling, check for border conflicts, and get rid of redundant points
P = ceil(P);

ind_left = find(P(:,2) < 1);
if ~isempty(ind_left),
    P(ind_left,2) = 1;
end
ind_right = find(P(:,2) > c);
if ~isempty(ind_right),
    P(ind_right,2) = c;
end
[Ptemp,P_ind] = unique(P,'rows');

% reorder point into original order
P_ind = sort(P_ind);
xy_line = P(P_ind,:);
line_ind = sub2ind(im_size,xy_line(:,1),xy_line(:,2));

if nargin < 3,
    flag_side = 0;
end
if nargout == 3,
    
    % create mask image
    mask = logical(ones(im_size));
    mask(line_ind) = 0;
    if flag_side == 0,
        mask = bwselect(mask,c,r,4);
    elseif flag_side == 1,
        mask = bwselect(mask,1,r,4);
    else
        disp('flag_side must be either 0 or 1');
        return;
    end

    mask(line_ind) = 1;
end