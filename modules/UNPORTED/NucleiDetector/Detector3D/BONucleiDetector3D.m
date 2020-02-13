function nucleiFilteredPositions = BONucleiDetector3D(imageNuclei, imageMembrane, kernelSize, thValue, resolutionXY, resolutionZ, scaleXY, scaleZ, client_server, mex_url, user, password)
javaaddpath('../lib/bisque.jar');
import bisque.*
%% PROGRAM
BQ = BQMatlab;
BQ.initServers(client_server,client_server);
BQ.login(user, password);
mex = BQ.loadMEX(mex_url);
%%
nucleiFilteredPositions = [];
cellSize = kernelSize;
%% LoG
[imageSeeds nucleiPositions] = BOLoGDetector3D(imageNuclei, cellSize, resolutionXY, resolutionZ, scaleXY, scaleZ, thValue);
resp = BQ.updateProgress(mex, 40);
%% Filtering
descriptorTable = BO3DMaskDescriptor(imageNuclei, nucleiPositions, cellSize, resolutionXY, resolutionZ, scaleXY, scaleZ);
resp = BQ.updateProgress(mex, 60);
if ~isempty(imageMembrane)
    nucleiFilteredPositions = BO3DProfileDescriptor(imageMembrane, nucleiPositions, descriptorTable, cellSize*1.5, resolutionXY, resolutionZ, scaleXY, scaleZ);
else
    nucleiFilteredPositions = BO3DStatDescriptor(imageNuclei, nucleiPositions, descriptorTable, cellSize*1.5, resolutionXY, resolutionZ, scaleXY, scaleZ);
end
resp = BQ.updateProgress(mex, 80);
%% Save    
%%
end      
