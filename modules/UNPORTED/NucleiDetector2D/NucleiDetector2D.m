function [gobject_url nuclei_count_url ErrorMsg] = ...
         NucleiDetector2D(client_server, image_url, cellSize, thValue, channel_Nuclei, channel_Membrane, user, password)

     
%[gobject_url nuclei_count_url ErrorMsg] = NucleiDetector2D('http://bodzio.ece.ucsb.edu:8080','http://bodzio.ece.ucsb.edu:8080/ds/images/14013', '4.4', '0.22', '2', '1', 'matthew', 'matthew')

%%Declarations
ErrorMsg = '';
gobject_url = '';
nuclei_count_url = '';
%% 
kernelSize = str2double(cellSize);
thValue = str2double(thValue);
%% Path
%javaaddpath('../lib/bisque.jar');
javaaddpath('../../lib/bisque.jar');
import bisque.*
%% PROGRAM
try
	BQ = BQMatlab;
    BQ.initServers(client_server,client_server);
    BQ.login(user, password);
%% Load data
    %% MetaData
    [imageNuclei, imageMembrane, resolutionXY, scaleXY] = BOGetImageData(client_server, image_url, channel_Nuclei, channel_Membrane, user, password);    
%% RUN
    nucleiPositions = BONucleiDetector2D(imageNuclei, imageMembrane, kernelSize, thValue, resolutionXY, scaleXY);
%% SAVE RESULTS

    go = BQ.createGObject(datestr(now),'NucleiDetector2D_automatic');
    for i=1:length(nucleiPositions(:,2))
        p = BQ.createGObject('point',num2str(i));
        v = [nucleiPositions(i,2)-1 nucleiPositions(i,1)-1];
        BQ.addVertices(p,v);
        BQ.addGObject(go, p);
    end
    %BQ.saveObjectToXMLFile(go, '/home/boguslaw/result.xml');
    image = BQ.loadImage([image_url '?view=full']);
    BQ.deleteGObjectFull(image);
    gobject_url = char(BQ.saveGObjectURL(image,go));
    
    nuclei2dTag = BQ.createTag(['Nuclei2D ' datestr(now,31)],'');
    BQ.saveTag(image, nuclei2dTag);
    
    nucleiCountTag = BQ.createTag('nuclei_count', num2str(length(nucleiPositions)));
    nucleiGObjectsTag = BQ.createTag('gobject_url', gobject_url);
    
    BQ.addTag(nuclei2dTag, nucleiCountTag);
    BQ.addTag(nuclei2dTag, nucleiGObjectsTag);
    
    nuclei_count_url = char(BQ.saveTagURL(nuclei2dTag, nucleiCountTag));
    BQ.saveTag(nuclei2dTag, nucleiGObjectsTag);

catch
    err = lasterror 
    ErrorMsg = [err.message ','];
    for i=1:size(err.stack,1)
        ErrorMsg = [ErrorMsg err.stack(i,1).file ',' err.stack(i,1).name ',' num2str(err.stack(i,1).line) ','];
    end
end
%% End

end
