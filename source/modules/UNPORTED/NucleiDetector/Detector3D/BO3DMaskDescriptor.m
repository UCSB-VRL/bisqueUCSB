function descriptorTable = BO3DMaskDescriptor(imageIn, nucleiPositions, cellSize, resolutionXY, resolutionZ, scaleXY, scaleZ )
% BO3DMaskDescriptor
%%
fprintf('BO3DMaskDescriptor ... \n');
%% 
% cellSize=2.4*1.4;
% resolutionXY = 0.138661; 
% resolutionZ = 1;
% scaleXY = 1.0;
% scaleZ = 1.0;

cellsizeXY = cellSize;
cellsizeZ = cellSize;
sizeXY = cellsizeXY/resolutionXY;
sizeZ = cellsizeZ/resolutionZ;
distanceMaxValueXY = round(scaleXY*sizeXY);
distanceMaxValueZ = round(scaleZ*sizeZ);
%distanceMaxValueXY = round(25*0.75);
%distanceMaxValueZ = 1;

descriptorTable = [];
for i=1:size(nucleiPositions,1)
    [imageInMask valuesInMask]= BOCreateMask3D(imageIn, nucleiPositions(i,1), nucleiPositions(i,2), nucleiPositions(i,3), distanceMaxValueXY, distanceMaxValueZ);        
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