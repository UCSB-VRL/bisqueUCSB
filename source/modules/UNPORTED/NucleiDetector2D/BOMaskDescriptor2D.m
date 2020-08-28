function descriptorTable = BOMaskDescriptor2D(imageIn, nucleiPositions, cellSize, resolutionXY, scaleXY)
%% BOMaskDescriptor2D - calculate mask descriptor
% 
%   Boguslaw Obara, http://boguslawobara.net/
%
%   Version:
%       0.1 - 14/11/2007 First implementation
%%
fprintf('BOMaskDescriptor2D ... \n');
%% Setting the kernel and mask size
cellsizeXY = cellSize;
sizeXY = cellsizeXY/resolutionXY;
distanceMaxValueXY = round(scaleXY*sizeXY);
descriptorTable = [];
for i=1:size(nucleiPositions,1)
    [imageInMask valuesInMask]= BOCreateMask2D(imageIn, nucleiPositions(i,1), nucleiPositions(i,2), distanceMaxValueXY);        
    valuesInMask = double(valuesInMask)/double(max(valuesInMask(:)));
    v = var(double(valuesInMask(:)));
    sd = std(double(valuesInMask(:)));
    m = mean(double(valuesInMask(:)));
    s = sum(double(valuesInMask(:)));    
    descriptorTable(i,1) = m;
    descriptorTable(i,2) = v;
    descriptorTable(i,3) = sd;    
    descriptorTable(i,4) = s;        
    descriptorTable(i,5) = i;
end
end