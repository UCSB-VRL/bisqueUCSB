function [imageSeeds nucleiPositions] = BOLoGDetector3D( imageIn, cellSize, resolutionXY, resolutionZ, scaleXY, scaleZ, thValue )
%% BO3DProfileDescriptor
%%
fprintf('BOLoGDetector3D ... \n');
%% Setting the kernel and mask size
% resolutionXY = 0.138661; 
% resolutionZ = 1;
% scaleXY = 1.0;
% scaleZ = 1.0;
cellsizeXY = cellSize;
cellsizeZ = cellSize;
sizeXY = cellsizeXY/resolutionXY;
sizeZ = cellsizeZ/resolutionZ;

kernelsizeXY = round(sizeXY/2);
kernelsizeZ = round(((resolutionXY/resolutionZ)*sizeXY)/2);
kernelsizeZ = max(1, kernelsizeZ);   
kernelsizeSigma = 3;

masksizeXY = round(scaleXY*sizeXY);
masksizeZ = round(scaleZ*sizeZ);
%% Gauss filtering
%im_gauss = gaussian3Dfil(im_green, sizex, sizey, sizez, sigma);
imageGauss = BOGaussian3DFast(imageIn, kernelsizeXY, kernelsizeXY, kernelsizeZ, kernelsizeSigma);
%imageGauss = BOGaussian3DFastDiv(imageIn, kernelsizeXY, kernelsizeXY, kernelsizeZ, kernelsizeSigma); 
%% Seeds searching
[imageSeeds nucleiPositions] = BOSeedSearch(imageIn, imageGauss, masksizeXY, masksizeZ, thValue);
nucleiPositions(:,4) = (1:size(nucleiPositions,1))';
end
