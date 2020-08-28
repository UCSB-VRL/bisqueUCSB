%% BQMatlab
%% Compile java classes and set up java paths 
clear java;
clc; clear all;
javaaddpath('build/jar/bisque.jar');
import bisque.*
%try
%% Start BQ and BQM libs
BISQUE = BQM; 
%% Setup servers and login to Bisquik DB
user = 'admin'; password = 'admin';
bisque_uri = 'http://bodzio.ece.ucsb.edu:8080';
mex_uri = 'http://bodzio.ece.ucsb.edu:8080/ds/modules/87';
BISQUE.initialize(bisque_uri, user, password, mex_uri);
%% Load image
image_uri = 'http://bodzio.ece.ucsb.edu:8080/ds/images/242';
image = BISQUE.load(image_uri);
image.getInfo();
image_data = BISQUE.getPixels(image);
geom = BISQUE.getGeometry(image);

image_new = BISQUE.create('image');
BISQUE.setGeometry(image_new, geom(1), geom(2), geom(3), geom(4), geom(5));
BISQUE.setType(image_new,'uint8');
BISQUE.setPixels(image_new, uint8(image_data));

%pixels = image_new.getPixels();
%filename = 'file:///home/boguslaw/Desktop/im.raw';
%pixels.save('http://bodzio.ece.ucsb.edu:8080');
%pixels.save(filename);


%image.setImage(BQM.convertMa(mat)
%% Save Image
return
x = 100; y = 100; ch = 1; d = 8; z = 1; t = 1;
name = 'my image.raw'; type = 'uint8';
my_data = uint8(100*(rand(x,y)));
new_image = BQBisquik.create('image');
pixels = new_image.setPixels(x,y,z,t,ch,d,type,name);
pixels.setImage(convertMatlabMatrix(my_data));
pixels.save(filename);
%% Save Tags
%newTag = BQ.createTag('Time', datestr(now,31));
%BQ.saveTag(new_image, newTag);
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
% catch
%     err = lasterror
%     ErrorMsg = err.message
% 	return;
% end

%%
