function [imageInMask valuesInMask] = BOCreateMask2D(imageIn, x, y,maskSizeXY)  
%% BOCreateMask2D - create 2D mask
% 
%   Boguslaw Obara, http://boguslawobara.net/
%
%   Version:
%       0.1 - 14/11/2007 First implementation
%%
imageMask = logical(zeros(size(imageIn)));
imageMask(x, y) = 1;
seUp = strel('disk',maskSizeXY);
seDown = strel('disk',maskSizeXY-2);

imageMask = logical(imdilate(imageMask,seUp));
imageInMask = immultiply(imageIn, imageMask);
valuesInMask = imageInMask(imageMask==1);
end