function f = lapofgau(im, s);
%
%function f = lapofgau(im, s);
%
% im: image matrix (2 dimensional)
% s: filter width
% f: filter output.
% Author: Baris Sumengen - sumengen@ece.ucsb.edu
%

%global sigma

sigma = (s-1)/3;
op = fspecial('log',s,sigma); 
op = op - sum(op(:))/prod(size(op)); % make the op to sum to zero
f = filter2(op,im);

