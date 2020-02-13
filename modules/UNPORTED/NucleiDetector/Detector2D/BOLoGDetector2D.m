function nucleiPositions = BOLoGDetector2D( imageIn, cellSize, resolutionXY, scaleXY, thValue )
%% BOLoGDetector2D - calculate 2D log
% 
%   Boguslaw Obara, http://boguslawobara.net/
%
%   Version:
%       0.1 - 14/09/2007 First implementation
%%
fprintf('BOLoGDetector3D ... \n');
%% Setting the kernel and mask size
cellsizeXY = cellSize;
sizeXY = cellsizeXY/resolutionXY;

kernelsizeXY = round(sizeXY/2);
kernelsizeSigma = 3;

masksizeXY = round(scaleXY*sizeXY);
%% Gauss filtering
imageGauss = BOGaussianFilter2D(imageIn, kernelsizeXY, kernelsizeXY, kernelsizeSigma);
%% Seeds searching
nucleiPositions = BOSeedSearch2D(imageGauss, masksizeXY, thValue);
nucleiPositions(:,3) = (1:size(nucleiPositions,1))';
end
