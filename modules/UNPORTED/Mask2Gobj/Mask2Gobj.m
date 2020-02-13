function [Resources ErrorMsg] = Mask2Gobj(client_server, image_url, tagname, user, password)

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

    image1 = BQ.loadImage(image_url);
    
    in_mask_url = char(BQ.findTag(image1, tagname));
    if(isempty(in_mask_url)); error(char(BQError.getLastError())); end
     
    image2 = BQ.loadImage(in_mask_url);  
    input_mask = uint8(BQ.loadImageData(image2));         
    if(isempty(input_mask)); error(char(BQError.getLastError())); end   
    
        bin_mask = im2bw(input_mask,0.8); % Convert it to binary
        %temp_mask = medfilt2(bin_mask,[15 15]); % Use median filtering to remove salt and pepper noise
        temp_mask = bin_mask;
        %get the areas of all the regions and select the big ones 
        [conn_im,num_reg] =bwlabel(temp_mask,8);
        reg_areas = regionprops(conn_im,'Area');

        %trace the boundaries
        b_trace = bwboundaries(temp_mask,8,'noholes');

    save_segm_out_polygons(image_url,b_trace,1); % 10 is the sampling interval in the boundary trace
    
catch
    if (~strcmp(userErrorMsg,''))
        ErrorMsg = userErrorMsg;
    else
        err = lasterror;
        ErrorMsg = err. message;
    end
    return;
end

end

%% Save the segmentation results as polygon GObject
function save_segm_out_polygons(image_url,segm_pts,interval)

    import bisque.*
    BQ = BQMatlab;

    in_image_deep = BQ.loadImage([image_url '?view=deep']);
    image_gobj = in_image_deep.gobjects;

    flag = 0;index = 0;
    for i = 0:size(image_gobj)-1
        if(strcmp(image_gobj.get(i).name,['Output_SEG_Data']))
            %BQ.deleteGObject(image_gobj.get(i));
            index = i;
            flag = 1;
        end
    end

    if(~flag)
        segm_GObject = BQ.createGObject('polygon_set',['Output_SEG_Data']);
        active_gobj = segm_GObject;
    else

        %% TODO : the code reloads the gobjects from the image after
        %% deleting them:: Change the code to modify the Java Array            
        %% ERROR in Java Code BQMatlab in the lines commented below

        polyline_gobj = image_gobj.get(index).gobjects;
        %i = 0;
        %while( (i <= size(polyline_gobj)-1) && BQ.isGObjectValid(polyline_gobj.get(i)) )
        for i =0:size(polyline_gobj)-1
            if(strcmp(polyline_gobj.get(i).name,['Layer_AC']))
                %BQ.delGObject(image_gobj.get(index),polyline_gobj.get(i));
                
                %BQ.deleteGObject(polyline_gobj.get(i));
            end
           % i=i+1;
        end
        %BQ.removeGObjectFromList(image_gobj.get(index),['Layer_' ret_layer]);

        %un-wanted reloading of the image
        in_image_deep = BQ.loadImage([image_url '?view=deep']);
        image_gobj = in_image_deep.gobjects;
        active_gobj = image_gobj.get(index);            
    end

    %create a GObject for every layer
    temp_num = 0;
    for cur_layer = 1:size(segm_pts,1)

        cur_layer_temp = segm_pts{cur_layer};
        if(length(cur_layer_temp) < 5)
            disp('\n Mask2Gobj:Region empty');
            continue;
        end
        temp_num =temp_num +1
        polygon_name = ['Layer_AC'];% '_' char(temp_num)]
        polygon = BQ.createGObject('polygon',polygon_name)

       %now add the vertices to the polyline from the pts set

        for i = 1:interval:length(cur_layer_temp)
            % x and y coordinates - Mlab and GObjects are the
            % same
            vert = [cur_layer_temp(i,2),cur_layer_temp(i,1)];
            BQ.addVertices(polygon,vert);
        end

        %add the current layer to gt_data
        BQ.addGObject(active_gobj,polygon);

    end   

    %finally add the gt_data to the image
    BQ_image_url = BQ.loadImage(image_url);
    GObjectURL = char(BQ.saveGObjectURL(BQ_image_url,active_gobj));   

    %add tags to the segmentation output
    BQ.deleteTag(BQ_image_url,['Seg_GObj']);
    tag = BQ.addTag(BQ_image_url,['Seg_GObj'],char(GObjectURL));
    if(isempty(tag)); error(char(BQError.getLastError())); end   
    res = BQ.saveTag(BQ_image_url, tag);
    if(isempty(res)); error(char(BQError.getLastError())); end         

end
 
