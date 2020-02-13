%% Protocol to talk to Bisquik DataBase
%% Compile java classes and set up java paths 
clc; clear all;
clear java;
javaaddpath('build/jar/bisque.jar');
import bisque.*
try
%% Start BQ lib
BQ = BQMatlab; 
%% Setup servers 
ds_uri = 'http://dough.ece.ucsb.edu';
cs_uri = 'http://dough.ece.ucsb.edu';
BQ.initServers(ds_uri,cs_uri);
%% Login to Bisquik DB
user = 'admin'; password = 'admin';
BQ.login(user, password);
%% Load image
image_uri = 'http://dough.ece.ucsb.edu/ds/images/18914';
image = BQ.loadImage([image_uri '?view=full']);
image_data = uint8(BQ.loadImageData(image));
%% Save Image
new_image = BQ.initImage(size(image_data,1), size(image_data,2), 1, 1, 3, 8, 'uint8', 1);
new_image_url = BQ.saveImage(new_image, uint16(image_data));
%% Save Tags
newTag = BQ.createTag('Time', datestr(now,31));
BQ.saveTag(new_image, newTag);
%% Create GObject
% new_go = BQ.createGObject('ROI','My ROI');
% new_rect = BQ.createGObject('rectangle','My rect');
% v = zeros(2,2);
% v(1,:) = [10 10];
% v(2,:) = [300 300];
% BQ.addVertices(new_rect,v);
% BQ.addGObject(new_go, new_rect);
%new_go_url = BQ.saveGObject(new_image, new_go);
%%
catch
    err = lasterror
    ErrorMsg = err.message
	return;
end

%%
