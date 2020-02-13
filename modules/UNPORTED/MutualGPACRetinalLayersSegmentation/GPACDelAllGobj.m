function GPACDelAllGobj(client_server,imageurl,layer,user,password)

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
            BQ.deleteGObject(image_gobj.get(i));
    end
    
    layers = {'ONL';'IS';'OS';'ML';'BG'};
    for i = 1:size(layers,1)
        layer = layers{i};
        %delete the tag
        BQ.deleteTag(in_image_deep,['GPAC_Layer_' layer '_Seg_GObj']);
        disp(['deleted tag for layer',layer]);
        saved_img_url = char(BQ.findTag(in_image_deep,['GPAC_Layer_' layer '_Seg_Mask']));
        if(~isempty(saved_img_url))
            BQ.deleteImage(saved_img_url);
            BQ.deleteTag(in_image_deep,['GPAC_Layer_' layer '_Seg_Mask']);
        end
    disp(['deleted mask for layer',layer]);
    end
    
     BQ.deleteTag(in_image_deep,['Splines_Seg_GObj']);
        disp(['deleted tag for layer',layer]);
        saved_img_url = char(BQ.findTag(in_image_deep,['Splines_Seg_GObj']));
     if(~isempty(saved_img_url))
            BQ.deleteImage(saved_img_url);
     end
     BQ.deleteTag(in_image_deep,['Splines_Seg_Mask']);
     
     
     BQ.deleteTag(in_image_deep,['groundtruth_GObj']);
        disp(['deleted GT tag']);
        
end