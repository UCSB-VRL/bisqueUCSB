function [imageNuclei imageMembrane resolutionXY resolutionZ scaleXY scaleZ] = ...
            BOGetImageData(client_server, image_url, channel_Nuclei, channel_Membrane, user, password)
imageNuclei = [];
imageMembrane = [];
%% Paths
javaaddpath('../lib/bisque.jar');
%javaaddpath('../../lib/bisque.jar');
import bisque.*
%%
try
	BQ = BQMatlab;
    BQ.initServers(client_server,client_server);
    BQ.login(user, password);
%% Load data
    %% MetaData
    image = BQ.loadImage(image_url);
    resolutionXYTag = char(BQ.findTag(image, 'pixel_resolution_x_y'));
    if isempty(resolutionXYTag)
        resolutionXY = 1.0; 
    else
        resolutionXY = str2double(resolutionXYTag);
    end
    resolutionZTag = char(BQ.findTag(image, 'pixel_resolution_z'));
    if isempty(resolutionZTag)
        resolutionZ = 1.0;
    else
        resolutionZ = str2double(resolutionZTag); %#ok<ST2NM>
    end
    scaleXY = 1.0;
    scaleZ = 1.0;
%% Data
    channel_Nuclei = str2double(channel_Nuclei);
    im = BQ.loadImageDataCH(image, channel_Nuclei);
    %imageNuclei = im(:,:,channel_Nuclei,:);
    imageNuclei = im;
    %imageNuclei = squeeze(imageNuclei);
    imageNuclei = double(imageNuclei)/double(max(imageNuclei(:)));
    if(isempty(imageNuclei)); error(char(BQError.getLastError())); end

    if(~strcmp(channel_Membrane,'None'))
        channel_Membrane = str2double(channel_Membrane);
        im = BQ.loadImageDataCH(image, channel_Membrane);
        %imageMembrane = im(:,:,channel_Membrane,:);
        imageMembrane = im;
        %imageMembrane = squeeze(imageMembrane);
        imageMembrane = double(imageMembrane)/double(max(imageMembrane(:)));
        if(isempty(imageMembrane)); error(char(BQError.getLastError())); end
    end
catch
    err = lasterror;
	return;
end
%% End

end
