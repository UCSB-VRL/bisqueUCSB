function [gobject_url nuclei_count_url ErrorMsg] = ...
         NucleiDetector(client_server, mex_url, image_url, cellSize, thValue, channel_Nuclei, channel_Membrane, user, password)

     
%[gobject_url nuclei_count_url ErrorMsg] = NucleiDetector('http://bodzio.ece.ucsb.edu:8080','http://bodzio.ece.ucsb.edu:8080/ds/mex/11930',
% 'http://bodzio.ece.ucsb.edu:8080/ds/images/14013', '4.4', '0.22', '2', '1', 'user', 'password']

%%Declarations
ErrorMsg = '';
gobject_url = '';
nuclei_count_url = '';
%% 
kernelSize = str2double(cellSize);
thValue = str2double(thValue);
%% Path
irtdir = which('NucleiDetector.m');
[irtdir dummy] = fileparts(irtdir);
clear dummy;
path([irtdir '/Detector2D'], path)
path([irtdir '/Detector3D'], path)

addpath('./Detector2D/');
addpath('./Detector3D/');

javaaddpath('../../lib/bisque.jar');
import bisque.*
%% PROGRAM
try
	BQ = BQMatlab;
    BQ.initServers(client_server,client_server);
    BQ.login(user, password);
    mex = BQ.loadMEX(mex_url);
    resp = BQ.updateProgress(mex, 0);
%% 
    
%% Load data and check for the type of data from the image url
    %% MetaData
    [imageNuclei, imageMembrane, resolutionXY, resolutionZ, scaleXY, scaleZ, numSlices] = BOGetImageData(client_server, image_url, channel_Nuclei, channel_Membrane, user, password);   
    resp = BQ.updateProgress(mex, 10);
%% RUN
    if(numSlices > 1)
        nucleiPositions = BONucleiDetector3D(imageNuclei, imageMembrane, kernelSize, thValue, resolutionXY, resolutionZ, scaleXY, scaleZ, client_server, mex_url, user, password);
    else
        nucleiPositions = BONucleiDetector2D(imageNuclei, imageMembrane, kernelSize, thValue, resolutionXY, scaleXY, client_server, mex_url, user, password);
    end
%% SAVE RESULTS

    if(numSlices > 1)
        go = BQ.createGObject('NucleiDetector3D_automatic', datestr(now));
        for i=1:length(nucleiPositions(:,2))
            p = BQ.createGObject('point',num2str(i));
            v = [nucleiPositions(i,2)-1 nucleiPositions(i,1)-1 int32(nucleiPositions(i,3)-1)];
            BQ.addVertices(p,v);
            BQ.addGObject(go, p);
        end
    else
        go = BQ.createGObject('NucleiDetector2D_automatic', datestr(now));
        for i=1:length(nucleiPositions(:,2))
            p = BQ.createGObject('point',num2str(i));
            v = [nucleiPositions(i,2)-1 nucleiPositions(i,1)-1];
            BQ.addVertices(p,v);
            BQ.addGObject(go, p);
        end
    end
    %BQ.saveObjectToXMLFile(go, '/home/boguslaw/result.xml');
    image = BQ.loadImage([image_url '?view=full']);
    BQ.deleteGObjectFull(image);
    gobject_url = char(BQ.saveGObjectURL(image,go));
    
    nucleiTag = BQ.createTag(['NucleiDetection ' datestr(now,31)],'');
    BQ.saveTag(image, nucleiTag);
    
    nucleiCountTag = BQ.createTag('nuclei_count', num2str(length(nucleiPositions)));
    nucleiGObjectsTag = BQ.createTag('gobject_url', gobject_url);
    nucleiMEXTag = BQ.createTag('mex_url', mex_url); 
    
    BQ.addTag(nucleiTag, nucleiCountTag);
    BQ.addTag(nucleiTag, nucleiGObjectsTag);
    BQ.addTag(nucleiTag, nucleiMEXTag);
    
    nuclei_count_url = char(BQ.saveTagURL(nucleiTag, nucleiCountTag));
    BQ.saveTag(nucleiTag, nucleiGObjectsTag);
    BQ.saveTag(nucleiTag, nucleiMEXTag);
    %resp = BQ.updateProgress(mex, 100);

    BQ.addTag(mex, 'gobject_url', gobject_url);
    BQ.addTag(mex, 'nuclei_count_url',nuclei_count_url );
    BQ.finished(mex, '');
catch
    err = lasterror 
    ErrorMsg = [err.message, 10, 'Stack:', 10];
    for i=1:size(err.stack,1)
      ErrorMsg = [ErrorMsg, '     ', err.stack(i,1).file, ':', num2str(err.stack(i,1).line), ':', err.stack(i,1).name, 10];
    end
    BQ.failed (mex, ErrorMsg);

end
