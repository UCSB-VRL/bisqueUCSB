% [M, ind] = MedAD(x)
%
% DESC:
% estimate the scale of the sample data in x (robust Median Absolute
% Deviation estimator)
%
% AUTHOR
% Marco Zuliani - zuliani@ece.ucsb.edu
%
% VERSION:
% 1.1
%
% INPUT:
% x         = input data
%
% OUTPUT:
% M         = scale
% ind       = indices of the inliers (optional)

function [M, ind] = MedAD(x)
    x = double(x);
    med = median(x);
    temp = abs(x - med);
    M = 1.4826 * median(temp);

    if nargout > 1
        ind = find(x <= M);
    end;
end
