function nucleiPositions = BONucleiDetector2D(imageNuclei, imageMembrane, nucleiSize, thValue, resolutionXY, scaleXY,client_server, mex_url, user, password)
%%  BONucleiDetector2D - Automatic 2D Nuclei Detector
%       
%        We start with a laser scanning confocal 3D stack that has a nuclear stain channel.
%   INPUT:
%       imageNuclei, imageMembrane  - Channels are selected by number and nuclear channel must to be present. You can also select a membrane channel if it exists, this could help to filter out incorrectly detected centroids.
%       nucleiSize                  - nuclei size: We have approximately measured the size of the nucleus and obtained 3 microns. This value we will enter as "Nuclei Size" parameter.
%       thValue                     - low intensity bound: We would also like to reject 20% of lower intensity levels as a valid response of a nuclei, so we set 0.2 as a "Low intensity level".
%       resolutionXY, scaleXY       - pixel size: If the image has embedded meta-data then both pixel resolution X/Y and Z will be filled automatically. If you would want to change these values, they will be stored in the appropriate image tag and preserved.
%   OUTPUT:
%       nucleiPositions             - detected nuclei positions
%
% 
%   Boguslaw Obara, http://boguslawobara.net/
%
%   Version:
%       0.1 - 14/11/2008 First implementation

%% LOGIN
javaaddpath('../lib/bisque.jar');
import bisque.*
BQ = BQMatlab;
BQ.initServers(client_server,client_server);
BQ.login(user, password);
mex = BQ.loadMEX(mex_url);
%% LoG
[nucleiPositions] = BOLoGDetector2D(imageNuclei, nucleiSize, resolutionXY, scaleXY, thValue);
resp = BQ.updateProgress(mex, 40);
%% Filtering
descriptorTable = BOMaskDescriptor2D(imageNuclei, nucleiPositions, nucleiSize, resolutionXY, scaleXY);
resp = BQ.updateProgress(mex, 60);
if ~isempty(imageMembrane)
    nucleiPositions = BOProfileDescriptor2D(imageMembrane, nucleiPositions, descriptorTable, nucleiSize*1.5, resolutionXY, scaleXY);
else
    nucleiPositions = BOStatDescriptor2D(imageNuclei, nucleiPositions, descriptorTable, nucleiSize*1.5, resolutionXY, scaleXY);
end
resp = BQ.updateProgress(mex, 80);
%%
end      
