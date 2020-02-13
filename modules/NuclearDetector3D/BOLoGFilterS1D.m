%%  BOLoGFilterS1D - separable Laplacian of Gaussian filter
%   
%   REFERENCE:
%       A. Huertas and G. Medioni, 
%       Detection of intensity changes with subpixel accuracy using 
%       Laplacian-Gaussian masks,
%       IEEE Transactions on Pattern Analysis and Machine Intelligence, 
%       8, 5, 651-664, 1986.
%
%       D. Sage and F.R. Neumann and F. Hediger and S.M. Gasser and M. Unser 
%       Automatic tracking of individual fluorescence particles: 
%       application to the study of chromosome dynamics,
%       IEEE Transactions on Image Processing, 14, 9, 1372-1383, 2005, 
%
%   INPUT:
%       s           - sigma
%
%   OUTPUT:
%       LoG1,LoG2   - 1D LoG filters
%
%   HELP: 
%       LoG  = G"
%       2D -> conv2(im,LoG) = conv2(LoG1,LoG2,im)+conv2(LoG2,LoG1,im)
%       3D -> conv3(im,LoG) = conv3(LoG1,LoG2,LoG2,im)
%                           + conv3(LoG2,LoG1,LoG2,im)
%                           + conv3(LoG2,LoG2,LoG1,im)
%
%   USAGE:
%       [LoG1,LoG2] = BOLoGFilterS1D(3)
% 
%   AUTHOR:
%       Boguslaw Obara, http://boguslawobara.net/
%
%   VERSION:
%       0.1 - 03/06/2010 First implementation
%%

function [LoG1,LoG2] = BOLoGFilterS1D(s)
    %% Grid coordinates
    x = (-3*s:3*s)';
    %% LoG
    LoG1 = (1/(sqrt(2*pi)*s)) * (1 - x.^2/s^2 ) .* exp(-x.^2/(2*s^2));
    LoG2 = (1/(sqrt(2*pi)*s)) * exp(-x.^2/(2*s^2));
end