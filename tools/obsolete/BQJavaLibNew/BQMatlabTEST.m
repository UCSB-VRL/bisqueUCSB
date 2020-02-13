%% Protocol to talk to Bisquik DataBase
%% Compile java classes and set up java paths 
clc; clear all; clear java;
import bisque.*
try
%% Start BQ lib
BQ = BQMatlab; 
%% Setup serversds_uri = 'http://bodzio.ece.ucsb.edu:8080';
cs_uri = 'http://bodzio.ece.ucsb.edu:8080';
ds_uri = 'http://hammer.ece.ucsb.edu:8080';
cs_uri = 'http://hammer.ece.ucsb.edu:8080';
BQ.initServers(ds_uri,cs_uri);
%% Login to Bisquik DB
user = 'admin'; password = 'admin';
BQ.login(user, password);
mex = BQ.loadMEX(['http://hammer.ece.ucsb.edu:8080/ds/mex/947?view=deep,canonical'])
%% Post Image from File
%% Load image
image_uri = 'http://bodzio.ece.ucsb.edu:8080/ds/images/14477';
image = BQ.loadImage(image_uri);
plane = BQ.loadImagePlane(image,1,1);
pp = plane.toMatrix;

return
image_data = uint8(BQ.loadImageData(image));

new_image = BQ.initImage(size(image_data,1), size(image_data,2), 1, 1, size(image_data,3), 8, 'uint8', 1);
new_image_url = BQ.saveImage(new_image, uint8(image_data));

return


%% Setup servers
%ds_uri = 'http://bodzio.ece.ucsb.edu:8080';
%cs_uri = 'http://bodzio.ece.ucsb.edu:8080';
%ds_uri = 'http://dough.ece.ucsb.edu';
%cs_uri = 'http://dough.ece.ucsb.edu';
%BQ.initServers(ds_uri,cs_uri);
%% Login to Bisquik DB
%user = 'nuclei3d'; password = 'nuclei3d';
%user = 'admin'; password = 'admin';
%BQ.login(user, password);

%new_image = BQ.initImage(size(image_data,1), size(image_data,2), size(image_data,4), 1, 2, 16, 'uint16', 1);
%new_image_url = BQ.saveImage(new_image, uint16(image_data));

%return











%BQ.deleteTagFull(image)
%BQ.deleteGObjectFull(image)
%return
%nuclei3dTag = BQ.createTag(['Nuclei3D ' datestr(now,31)],'');
%BQ.saveTag(image, nuclei3dTag);

%nucleiCountTag = BQ.createTag('nuclei_count', '20');
%BQ.addTag(nuclei3dTag, nucleiCountTag);

%nuclei_count_url = char(BQ.saveTagURL(nuclei3dTag, nucleiCountTag));
%nucleiCountTag.setValue(nuclei_count_url);
%BQ.updateTag(nuclei3dTag, nucleiCountTag);

%BQ.saveTag(image, nucleiGObjectsTag);
%nuclei_count_url = char(BQ.saveTagURL(nuclei3dTag, nucleiCountTag));
%BQ.updateTag(image, new_tag);


%BQ.deleteGObjectFull(image)


image_data = BQ.loadImageData(image);
%image_data2 = BQ.loadImageDataCH(image,2);

% %% Save image
ds_uri = 'http://loup.ece.ucsb.edu:8080';
cs_uri = 'http://loup.ece.ucsb.edu:8080';
BQ.initServers(ds_uri,cs_uri);
%% Login to Bisquik DB
user = 'admin'; password = 'admin';
BQ.login(user, password);
new_image = BQ.initImage(size(image_data,1), size(image_data,2), size(image_data,4), 1, size(image_data,3), 8, 'uint16', 1);
new_image.tags = image.tags 
new_image_url = BQ.saveImage(new_image, uint16(image_data));

for i=0:new_image.tags.size-1
new_tag = new_image.tags.get(i);
new_tag.uri = [];
new_tag_url = BQ.saveTag(new_image, new_tag);
end

%% Create Tag
%return
%new_tag = BQ.addTag(image, 'number',12.3);
%new_tag_url = BQ.saveTag(image, new_tag);
%BQ.updateTag(image, new_tag);
%% Create GObject
% new_go = BQ.createGObject('ROI','My ROI');
% new_rect = BQ.createGObject('rectangle','My rect');
% v = zeros(2,2);
% v(1,:) = [10 10];
% v(2,:) = [300 300];
% BQ.addVertices(new_rect,v);
% BQ.addGObject(new_go, new_rect);
%new_go_url = BQ.saveGObject(image, new_go);
%% Search
% search_list = char(BQ.search(''));
%% Find Tag
% value = BQ.findTag(image, 'me')
%%
catch
    err = lasterror
    ErrorMsg = err.message
	return;
end

%%
