function [Resources ErrorMsg] = delGobj(client_server, image_url, user, password)

%USAGE
% ErrorMsg = Mask2Gobj('http://bodzio.ece.ucsb.edu:8080', 'http://bodzio.ece.ucsb.edu:8080/ds/images/661', 'admin', 'admin')
%function m_loadtry(image_url, user, password)
%         m_loadtry('http://bodzio.ece.ucsb.edu:8080/ds/images/91','admin', 'admin')
%
%INPUT: image_url of input image to be segmented

javaaddpath('../../lib/bisque.jar');

import bisque.*

Resources = ''; % Resources is not being used
ErrorMsg = '';
global userErrorMsg;
try
 
%% 
    BQ = BQMatlab;
    BQ.initServers(client_server,client_server);
    BQ.login(user, password);
 
    in_image_deep = BQ.loadImage([image_url '?view=deep']);
    image_gobj = in_image_deep.gobjects;
    
       polyline_gobj = image_gobj.get(0).gobjects;
       for i =0:size(polyline_gobj)-1
            if(strcmp(polyline_gobj.get(i).name,['Layer_AC']))
                %BQ.delGObject(image_gobj.get(index),polyline_gobj.get(i));
                
                BQ.deleteGObject(polyline_gobj.get(i));
            end
           % i=i+1;
        end
end
 
