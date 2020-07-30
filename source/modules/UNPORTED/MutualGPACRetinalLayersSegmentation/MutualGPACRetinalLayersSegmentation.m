function [image_resource ErrorMsg] = MutualGPACRetinalLayersSegmentation(client_server, image_url, ret_layer, user, password)
%Usage : MutualGPACRetinalLayersSegmentation('http://bodzio.ece.ucsb.edu:8080', 'http://bodzio.ece.ucsb.edu:8080/ds/images/17016','ONL', 'admin', 'admin')

%% Path
addpath('./Retina_code/');
javaaddpath('../../lib/bisque.jar');
import bisque.*
ErrorMsg = '';
image_resource = [];
global userErrorMsg;
% set userErrorMsg to the error message and flag the error.

%% Loose ends of the code

% UPDATED as of 4/10/2009
% 1.Error handling - use of userErrorMsg not proper
% 2.Saving/Deleting of GObjects - Hierarachy - undecided, hence continued
% with one structure.
% 3.Saving/Deleting of Tags - same as above
% 4.Image Resize from the image server - not done
% 5.Parallelization of different layers - not done
% 6.Implemented reading gobjects of ref image for the mask and regenerated the mask for the algorithm-
% proved to be slower than reading the available mask, hence just reading the ref_mask
% 7. Algorithm needs to be looked into - all the channels being considered
% for hist_eq image. Dimitry thinks it can be done better if done based on
% the antibody, considering only a specific channel (???)
% 8. Area of the polygonal region in the mask not used as of now. The
% polygons are shown if they have more than 100 boundary points
% 9. User Interaction : (???)
% 10. save polygons/polylines gobjects are pretty much the same code - can
% be combined if polylines are to be used

try
 
%% Init
    BQ = BQMatlab;
    BQ.initServers(client_server,client_server);
    BQ.login(user, password);

%% Load the images    

    if(~strcmp(ret_layer,'ONL') && ~strcmp(ret_layer,'IS')&& ~strcmp(ret_layer,'OS') && ~strcmp(ret_layer,'ML') && ~strcmp(ret_layer,'BG'))
        userErrorMsg = 'Layer can only be of ONL,IS,OS,ML or BG type.';
        error(userErrorMsg);
     end

    image1 = BQ.loadImage(image_url);
    input_img = uint8(BQ.loadImageData(image1)); 
    if(isempty(input_img)); error(char(BQError.getLastError())); end
    
    temp = char(BQ.findTag(image1, 'dataset_label'));
    if(isempty(temp) || ~strcmp(temp,'GPAC'))
        userErrorMsg = 'Selected Image has no valid tag information. Required tag- dataset_label:GPAC. Unable to perform Segmentation';
        error(userErrorMsg);
    end
    
    in_ref_url = char(BQ.findTag(image1, 'reference_image'));
    if(isempty(in_ref_url)); error(char(BQError.getLastError())); end
    
    %% TODO : Change the code here such that the imageserver gives the
    %% resized image of 200*300 instead of resizing it in Matlab
    
    image2 = BQ.loadImage(in_ref_url);  
    input_ref = uint8(BQ.loadImageData(image2));         
    if(isempty(input_ref)); error(char(BQError.getLastError())); end   
    
    in_mask_url = char(BQ.findTag(image1, 'reference_mask'));
    if(isempty(in_mask_url)); error(char(BQError.getLastError())); end    
 
    imagegt = BQ.loadImage(in_mask_url);  
    input_gt = uint8(BQ.loadImageData(imagegt)); 
    if(isempty(input_img)); error(char(BQError.getLastError())); end

% read the gobjects from the reference image and construct the mask
% works correctly, found to be slower than reading the mask image!

%    [ht wd ch] = size(input_ref);
%    mask_vals = [1,11,7,8,9,1];
%    gt_data = load_GObj_data(in_ref_url,'training_GT_data');   
%    input_gt = f_pt2mask1(gt_data,ht,wd,mask_vals);

%% Hack method employed in the code - initializes the active layer to have value 7

    if (strcmp(ret_layer, 'ONL'))
        layer = 7;
    elseif (strcmp(ret_layer, 'IS'))
        layer = 8;    
    elseif (strcmp(ret_layer, 'OS'))
        layer = 9;    
    elseif (strcmp(ret_layer, 'ML'))
        layer = 11;    
    elseif (strcmp(ret_layer, 'BG'))
        layer = 1;  
    else
        layer = 7;
    end

    if (layer ~= 7)
        input_gt((input_gt==7)) = 100;
        input_gt((input_gt==layer))=7;
        input_gt((input_gt==100))=layer;
    end
    
    size_im=size(input_img);
    
    % Resize the image to 200*300 in Matlab
    %% TODO : Change the code here such that the imageserver gives the
    %% resized image of 200*300 instead of resizing it in Matlab
    
    rescaled_image1 = imresize(input_img,[200 300],'nearest');
    rescaled_image2 = imresize(input_ref,[200 300],'nearest');
    rescaled_gt = imresize(input_gt,[200 300],'nearest');

    input_img=rescaled_image1;
    input_ref=rescaled_image2;
    input_gt=rescaled_gt;
    
%% Algorithm processing starts here

    [n1,m1,l1]=size(input_img);
    [n2,m2,l2]=size(input_ref);

    for i=1:l1
        input_img(:,:,i) = histeq(input_img(:,:,i));
    end
    
    input_img=double(input_img);
    c1{1}=input_img(:,:,1);
    c1{2}=input_img(:,:,2);
    c1{3}=input_img(:,:,3);

    input_ref=double(input_ref);
    c2{1}=input_ref(:,:,1);
    c2{2}=input_ref(:,:,2);
    c2{3}=input_ref(:,:,3);

    mask=ones(n2,m2);
    mask2 = [];

    % Perform tiling
    [W_col cen]=SimByTiles4Mutual(c1,c2,15,15,double(mask));

%% Texture part - not used
%
%     text_w = 0;
%     if(text_w~=0)
% 
%         gb1=gaborfiltering(rgb2gray(im1_backup));
%         gb2=gaborfiltering(rgb2gray(im2_backup));
%         for k=1:1:30
%             gb1{k}=abs(gb1{k});
%             gb2{k}=abs(gb2{k});
%         end
%         [W_text cen]=SimByTiles4Mutual(gb1,gb2,15,15,double(mask));
% 
%     end
% 
% 
%     if(text_w~=0)
%         W=col_w*W_col+text_w*W_text;
%     else
%         W=col_w*W_col;
%     end

%end texture part

%% Algorithm call for MutualPrior  GPAC 

    col_w = 1;
    W=col_w*W_col;

    [Ntiles,dummy]=size(cen);
    phi1=InitializePhi(20,n1,m1);

    phi2=double(input_gt);

    % Call GPAC - previously in the loop below
    [phi1 phi2]=MutualPrior_GPAC(phi1,phi2,W,cen,2000,double(mask));
    
%     forces_plus=zeros(m1,n1);
%     forces_minus1=zeros(m1,n1);
%     forces_minus2=zeros(m1,n1);
%     forces_minus3=zeros(m1,n1);
%     forces_minus4=zeros(m1,n1);
%     pos2neg=zeros(Ntiles,1);
%     neg2pos=zeros(Ntiles,1);
% 
%     points_changed=zeros(10,1);
% 
%     neg2pos_index=0;
%     pos2neg_index=0;
%     stop=0;

%    for i=1:1:1
%        phi_old=phi1;
%    [phi1 phi2]=MutualPrior_GPAC(phi1,phi2,W,cen,2000,double(mask));
    
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% 
%     segmentation=sign(phi1);
%     edges=seg2bmap(segmentation);
%     temp=im1_backup(:,:,1); temp(find(edges==1))=255; b(:,:,1)=temp;
%     temp=im1_backup(:,:,2); temp(find(edges==1))=255; b(:,:,2)=temp;
%     temp=im1_backup(:,:,3); temp(find(edges==1))=255; b(:,:,3)=temp;
%     imshow(uint8(b)); axis image;
% 
%     drawnow;

%     disp(i);
%    end

%% Post processing of segmentation results

    segmentation2=sign(phi1);
    segmentation2(segmentation2<0)=0;
    [L NUM] = bwlabeln(segmentation2, 8);
    %Compute the area of each component.
    S = regionprops(L, 'Area');
    maxArea=max([S.Area]);

    C = regionprops(L, 'centroid');
    bcc=[C.Centroid];
    dcc=reshape(bcc,2,NUM);
    acc=[C(([S.Area] == maxArea)).Centroid];
    acc=reshape(acc(1,1:2),2,1);
    dist=dcc-repmat(acc,1,NUM);
    dist=abs(dist(1,:));


    %Remove object far from the biggest one.
    %mask2 = ismember(L, find([S.Area] == maxArea));
    if layer~=1
        mask2 = ismember(L, find(dist<50));
    else
        mask2 = ismember(L, [find(dist<50),find(dist>200)]);
    end
    
    %% Further refining done later in the save stage
    %%Fill the holes
    if layer~=1
        vec1=mask2(1,:);
        mask2(1,min(find(vec1==1)):max(find(vec1==1)))=1;
        vec1=mask2(200,:);
        mask2(200,min(find(vec1==1)):max(find(vec1==1)))=1;
        mask2=imfill(mask2,'holes');
    end
    %%%%%

    mask2=255*mask2;

%     edges2=seg2bmap(double(mask2));
%     temp=im1_backup(:,:,1); temp((edges2==1))=255; %d(:,:,1)=temp;
%     temp=im1_backup(:,:,2); temp((edges2==1))=255; %d(:,:,2)=temp;
%     temp=im1_backup(:,:,3); temp((edges2==1))=255; %d(:,:,3)=temp;
  
    %image_post = postImage(url, '/bisquik/upload_handler_mex', mask2, 'bmp');
    %image_resource = findImageAttribute(image_post, 'uri');
    %maskTag = addTag('mask', image_resource);
    %saveTag(url, ImageID, maskTag);

    if (strcmp(ret_layer, 'ONL'))
        mask2((mask2==255))=7;
    elseif (strcmp(ret_layer, 'IS'))
         mask2((mask2==255))= 8;    
    elseif (strcmp(ret_layer, 'OS'))
         mask2((mask2==255))= 9;    
    elseif (strcmp(ret_layer, 'ML'))
         mask2((mask2==255))= 11;  
    elseif (strcmp(ret_layer, 'BG'))
         mask2((mask2==255))= 1;  
    else
      mask2((mask2==255))= 7;
    end

    % Rescale the mask image to the input image size
    rescaled_mask = imresize(mask2,[size_im(1) size_im(2)],'nearest');
    if(isempty(rescaled_mask)); error(char(BQError.getLastError())); end

%% Post-post processing of the mask to help extracting the boundaries to generate a polyline

    % refine the mask - method 1
%     bin_mask = im2bw(rescaled_mask,0.8); % Convert it to grayscale
%     se = strel('disk',15); % Use a disk of size 15
%     temp_mask = imclose(bin_mask,se); % Morphological operation
%     temp_mask2 = medfilt2(temp_mask,[5 5]); % Use median filtering to remove salt and pepper noise
%     temp_mask3 = imfill(temp_mask2,'holes'); % fill any BIG holes remaining in the image

    % refine the mask - method 2 - change in order - works better
%     bin_mask = im2bw(rescaled_mask,0.8); % Convert it to grayscale
%     temp_mask = medfilt2(bin_mask,[15 15]); % Use median filtering to remove salt and pepper noise
%     se = strel('disk',15); % Use a disk of size 15
%     temp_mask2 = imclose(temp_mask,se); % Morphological operation
%     temp_mask3 = imfill(temp_mask2,'holes'); % fill any BIG holes remaining in the image

    % Some error in the ext_pts code, ignore this
    %ext_mask = seg2bmap(temp_mask, size(temp_mask,1),size(temp_mask,2));
    % segm_pts = ext_pts(ext_mask);

    % Works for clean mask without noise, not written very well
%    [ErrorMsg segm_pts] = mask2seg(temp_mask3,15,2);

%% Generate a polygonal region for the segmentation output

    bin_mask = im2bw(rescaled_mask,0.8); % Convert it to grayscale
    temp_mask = medfilt2(bin_mask,[15 15]); % Use median filtering to remove salt and pepper noise
    
    %get the areas of all the regions and select the big ones - not being
    %used as of now
    [conn_im,num_reg] =bwlabel(temp_mask,8);
    reg_areas = regionprops(conn_im,'Area');
    
    %trace the boundaries
    b_trace = bwboundaries(temp_mask,8,'noholes');
    
%% Save the results of segmentation

% Save the output layer as a GObject
    save_segm_out_polygons(image_url,b_trace,ret_layer,10); % 10 is the sampling interval in the boundary trace
%    save_segm_out_polylines(image_url,segm_pts,ret_layer);

%Save the segmentation result
    save_segm_mask(image_url,rescaled_mask,ret_layer);

%image_resource = char(segm_imageURL);

clear functions;
%% Error Handling
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

%% Load the ground truth data from the image URL - used if the mask is generated from the stored gobjects of ref image
function pts = load_GObj_data(image_url,tag)

    global userErrorMsg;

    import bisque.*
    BQ = BQMatlab;

    flag = 0;
    segm_layers={'boundary_bg/GCL';'boundary_IS/bg';'boundary_INL/ONL';'boundary_ONL/IS';'boundary_GCL/INL'}; % 'boundary_Neuron/GCL' not included

    %get the GT data
    in_image = BQ.loadImage([image_url '?view=deep']);

    image_gobj = in_image.gobjects;
    if(isempty(image_gobj)); error(char(BQError.getLastError())); end

    % for now, assume only one GT data exists
    % look here for adding profile data

    %take care of Mlab and C indexing used in GObject library
    for i = 0:size(image_gobj)-1

    %read from this tag, get all the polylines from these
        if(strcmp(image_gobj.get(i).name,tag))

            flag = 1;
            %get to the layer gobject

            polyline = image_gobj.get(i).gobjects;
            if(isempty(polyline)); error(char(BQError.getLastError())); end

            temp = size(polyline);

            % indexing done in c style - For some reason, order of
            % Gobjects is reversed, as stored in the database

            for layer = 0:size(polyline)-1

               if(strcmp(polyline.get(layer).name, segm_layers{temp}))    

                   %get the vertices fromthe polyline gobject
                   vert = polyline.get(layer).vertices;
                   if(isempty(vert)); error(char(BQError.getLastError())); end

                   for v=0:size(vert)-1
                        index = vert.get(v).index.intValue + 1;
                        x = vert.get(v).x.doubleValue;
                        y = vert.get(v).y.doubleValue;

                        % pts stores all the vertices for all layers
                        pts{temp}(index,1) = x;
                        pts{temp}(index,2) = y;
                   end
                   temp = temp -1;
               else
                   % need to do something:: For now, flag an error
                   error(char(BQError.getLastError()));  
               end  
            end
        else
            %% CHANGE HERE if you want to take user input for GroundTruth
            % Take user input for training data and store it in to the image
            continue;
            %% user_input();
        end
    end

    if(flag == 0)
        userErrorMsg = 'Training Image does not have GroundTruth data!';
        error(userErrorMsg);
    end

end    
%% Generate the mask image from the segmentation point list- used if the mask is generated from the stored gobjects of ref image

function mask_image = f_pt2mask1(pts,ht,wd,value_array)

    [temp,layers] = size(value_array);
    mask_image = zeros(ht,wd);

    for i = 1:layers-2
        x1 = pts{i}(:,1);
        y1 = pts{i}(:,2);
        
        %check the start and the end
        if(y1(1) ~= 0)
            x1 = [x1(1);x1]; y1 = [0;y1];
        end
        
        if(y1(length(y1)) ~= ht)
            x1 = [x1;x1(length(x1))]; y1 = [y1;ht];
        end
        
        x2= pts{i+1}(:,1);
        y2= pts{i+1}(:,2);
        
        %check the start and the end
        if(y2(1) ~= 0)
            x2 = [x2(1);x2];y2 = [0;y2];
        end
        
        if(y2(length(y2)) ~= ht)
            x2 = [x2;x2(length(x2))];y2 = [y2;ht];
        end
        
        pt_set2 = [x2,y2];
        pt_set2 = flipud(pt_set2);
        
        poly_x = [x1',pt_set2(:,1)',x1(1)];
        poly_y = [y1',pt_set2(:,2)',y1(1)];
        temp_mask = poly2mask(poly_x,poly_y,ht,wd);
        mask_image((temp_mask==1)) = value_array(i+1);     
    end

    mask_image(mask_image==0)=1;
    mask_image(1,:) = mask_image(2,:);
end


%% Save the segmentation results as polygon GObject
function save_segm_out_polygons(image_url,segm_pts,ret_layer,interval)

% to save all the results of different layers, comment lines 455
% uncomment lines 457
% to save output of multiple expts on the same layer, change logic in lines 468 - 472. Comment  lines 617,618
    import bisque.*
    BQ = BQMatlab;

    in_image_deep = BQ.loadImage([image_url '?view=deep']);
    image_gobj = in_image_deep.gobjects;

    flag = 0;index = 0;
    for i = 0:size(image_gobj)-1
        if(strcmp(image_gobj.get(i).name,['GPAC_',ret_layer,'_Output_SEG_Data']))
            %BQ.deleteGObject(image_gobj.get(i));
            index = i;
            flag = 1;
        end
    end

    if(~flag)
        segm_GObject = BQ.createGObject('polygon_set',['GPAC_',ret_layer,'_Output_SEG_Data']);
        active_gobj = segm_GObject;
    else

        %% TODO : the code reloads the gobjects from the image after
        %% deleting them:: Change the code to modify the Java Array            
        %% ERROR in Java Code BQMatlab in the lines commented below

        polyline_gobj = image_gobj.get(index).gobjects;
        %i = 0;
        %while( (i <= size(polyline_gobj)-1) && BQ.isGObjectValid(polyline_gobj.get(i)) )
        for i =0:size(polyline_gobj)-1
            if(strcmp(polyline_gobj.get(i).name,['Layer_' ret_layer]))
                %BQ.delGObject(image_gobj.get(index),polyline_gobj.get(i));
                BQ.deleteGObject(polyline_gobj.get(i));
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
        if(length(cur_layer_temp) < 100)
            continue;
        end
        temp_num =temp_num +1;
        polygon_name = ['Layer_' ret_layer];% '_' char(temp_num)];
        polygon = BQ.createGObject('polygon',polygon_name);

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
    BQ.deleteTag(BQ_image_url,['GPAC_Layer_' ret_layer '_Seg_GObj']);
    tag = BQ.addTag(BQ_image_url,['GPAC_Layer_' ret_layer '_Seg_GObj'],char(GObjectURL));
    if(isempty(tag)); error(char(BQError.getLastError())); end   
    res = BQ.saveTag(BQ_image_url, tag);
    if(isempty(res)); error(char(BQError.getLastError())); end         

end


%% %% Save the segmentation results as GObject in the input image
function save_segm_out_polylines(image_url,segm_pts,ret_layer)

    import bisque.*
    BQ = BQMatlab;

    in_image_deep = BQ.loadImage([image_url '?view=deep']);
    image_gobj = in_image_deep.gobjects;

    flag = 0;index = 0;
    for i = 0:size(image_gobj)-1
        if(strcmp(image_gobj.get(i).name,['GPAC_',ret_layer,'_Output_SEG_Data']))
            BQ.deleteGObject(image_gobj.get(i));
            index = i;
            %flag = 1;
        end
    end

    if(~flag)
        segm_GObject = BQ.createGObject('polyline_set',['GPAC_',ret_layer,'_Output_SEG_Data']);
        active_gobj = segm_GObject;
    else

        %% TODO : the code reloads the gobjects from the image after
        %% deleting them:: Change the code to modify the Java Array            
        %% ERROR in Java Code BQMatlab in the lines commented below

        polyline_gobj = image_gobj.get(index).gobjects;
        %i = 0;
        %while( (i <= size(polyline_gobj)-1) && BQ.isGObjectValid(polyline_gobj.get(i)) )
        for i =0:size(polyline_gobj)-1
            if(strcmp(polyline_gobj.get(i).name,['Layer_' ret_layer]))
                %BQ.delGObject(image_gobj.get(index),polyline_gobj.get(i));
                BQ.deleteGObject(polyline_gobj.get(i));
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
    for cur_layer = 1:1%size(segm_pts,2)

        polyline_name = ['Layer_' ret_layer];
        polyline(cur_layer) = BQ.createGObject('polyline',polyline_name);

       %now add the vertices to the polyline from the pts set
        cur_layer_temp = segm_pts{cur_layer};
        for i = 1:length(cur_layer_temp)
            % x and y coordinates - Mlab and GObjects are the
            % same
            vert = [cur_layer_temp(i,1),cur_layer_temp(i,2)];
            BQ.addVertices(polyline(cur_layer),vert);
        end

        %add the current layer to gt_data
        BQ.addGObject(active_gobj,polyline(cur_layer));

    end   

    %finally add the gt_data to the image
    BQ_image_url = BQ.loadImage(image_url);
    GObjectURL = char(BQ.saveGObjectURL(BQ_image_url,active_gobj));   

    %add tags to the segmentation output
    BQ.deleteTag(BQ_image_url,['GPAC_Layer_' ret_layer '_Seg_GObj']);
    tag = BQ.addTag(BQ_image_url,['GPAC_Layer_' ret_layer '_Seg_GObj'],char(GObjectURL));
    if(isempty(tag)); error(char(BQError.getLastError())); end   
    res = BQ.saveTag(BQ_image_url, tag);
    if(isempty(res)); error(char(BQError.getLastError())); end         

end

%% Save the segmentation mask image
function save_segm_mask(image_url,rescaled_mask,ret_layer)

    import bisque.*
    BQ = BQMatlab;
    
    BQ_image_url = BQ.loadImage(image_url);
    
    %if a tag already exists, delete the old mask saved and the tag
    saved_img_url = char(BQ.findTag(BQ_image_url,['GPAC_Layer_' ret_layer '_Seg_Mask']));
    if(~isempty(saved_img_url))
        BQ.deleteImage(saved_img_url);
        BQ.deleteTag(BQ_image_url,['GPAC_Layer_' ret_layer '_Seg_Mask']);
    end
     
    new_image = BQ.initImage(size(rescaled_mask,1), size(rescaled_mask,2), 1, 1, 1, 8, 'uint8', 1);
    segm_maskURL = BQ.saveImage(new_image, uint8(rescaled_mask));    
    if(isempty(segm_maskURL)); error(char(BQError.getLastError())); end

    maskTag = BQ.addTag(BQ_image_url, ['GPAC_Layer_' ret_layer '_Seg_Mask'], char(segm_maskURL));
    if(isempty(maskTag)); error(char(BQError.getLastError())); end
    response = BQ.saveTag(BQ_image_url, maskTag);
    if(isempty(response)); error(char(BQError.getLastError())); end
      
%     img_tag = BQ.addTag(new_image, 'Input Image', char(image_url));
%     if(isempty(img_tag)); error(char(BQError.getLastError())); end
%     response = BQ.saveTag(new_image, img_tag);
%     if(isempty(response)); error(char(BQError.getLastError())); end
    
end