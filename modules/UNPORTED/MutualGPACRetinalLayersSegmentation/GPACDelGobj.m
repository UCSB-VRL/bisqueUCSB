function GPACDelGobj(client_server,imageurl,layer,user,password)

    if(nargin < 5)
        user = 'admin';
        password = 'admin';
    end
  
%    javaaddpath('../../lib/bisque.jar');

    import bisque.*

% Initialize servers and authorize
    BQ = BQMatlab;
    BQ.initServers(client_server,client_server);
    BQ.login(user, password);

    %delete the gobject
    in_image_deep = BQ.loadImage([imageurl '?view=deep']);
    image_gobj = in_image_deep.gobjects;
    for i = 0:size(image_gobj)-1
        if(strcmp(image_gobj.get(i).name, ['GPAC_',layer,'Output_SEG_Data']))
            BQ.deleteGObject(image_gobj.get(i));
        end
    end
    
    %delete the tag
    BQ.deleteTag(in_image_deep,['GPAC_Layer_' layer '_Seg_GObj']);
    disp('Deleted GObject');
    
    %delete the mask image and the tag
    saved_img_url = char(BQ.findTag(in_image_deep,['GPAC_Layer_' layer '_Seg_Mask']));
    if(~isempty(saved_img_url))
        BQ.deleteImage(saved_img_url);
        BQ.deleteTag(in_image_deep,['GPAC_Layer_' layer '_Seg_Mask']);
    end
    disp('Deleted Mask');
  
        
end