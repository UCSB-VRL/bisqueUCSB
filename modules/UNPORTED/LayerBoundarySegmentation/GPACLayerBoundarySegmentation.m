function [Resources ErrorMsg] = GPACLayerBoundarySegmentation(client_server, image_url, user, password)

%USAGE
% ErrorMsg = LayerBoundarySegmentation('http://bodzio.ece.ucsb.edu:8080', 'http://bodzio.ece.ucsb.edu:8080/ds/images/661', 'admin', 'admin')
%function m_loadtry(image_url, user, password)
%         m_loadtry('http://bodzio.ece.ucsb.edu:8080/ds/images/91','admin', 'admin')
%
%INPUT: image_url of input image to be segmented

javaaddpath('../../lib/bisque.jar');

import bisque.*

Resources = ''; % Resources is not being used
ErrorMsg = '';
global userErrorMsg;
%% Path
%addpath interface
%addpath ./Retina_code
irtdir = which('LayerBoundarySegmentation.m');
[irtdir dummy] = fileparts(irtdir);
clear dummy;
path([irtdir '/Retina_code'], path)

addpath('./Retina_code');

%% global cell array for all information
global retina; 

% SAMPLE retina information
% image_url: 'http://bodzio.ece.ucsb.edu:8080/ds/images/1739'
% user: 'admin'
% password: 'admin'
% server: 'http://bodzio.ece.ucsb.edu:8080'
% segm_layers: {6x1 cell}
% BQ_image_url: [1x1 bisque.BQImage]
% num_layers: 6
% condition: '3d'
% group_num: 2
% current_group: {1x6 cell}
% subgroup: 3
% image_number: 23
% training_number: {[24]  [25]  [26]  [27]  [28]  [29]  [30]  [31]}
% image: [512x768x3 uint8]
% train_image_url: 'http://bodzio.ece.ucsb.edu:8080/ds/images/1761'
% train_image: [512x768x3 uint8]
% train_gt: {[13x2 double]  [14x2 double]  [18x2 double]  [18x2 double]  [19x2 double]  [16x2 double]}
% t_prof: {[2x65 double]  [2x65 double]  [2x65 double]  [2x65 double]  [2x65 double]  [2x65 double]}
% segm_out: {[35x2 double]  [41x2 double]  [39x2 double]  [42x2 double]  [37x2 double]  [56x2 double]}
% GObject_url: 'http://bodzio.ece.ucsb.edu:8080/ds/gobjects/17923'
% GObject:

%% MAIN
try
    userErrorMsg = '';
% Initialize servers and authorize
    BQ = BQMatlab;
    BQ.initServers(client_server,client_server);
    BQ.login(user, password);
    
%   retina.pts_orig = cell(1,5); %layer ground truth from image_url


    retina.image_url=image_url;
    retina.user=user;
    retina.password=password;
    retina.server = client_server;

    retina.segm_layers={'boundary_bg/GCL';'boundary_IS/bg';'boundary_INL/ONL';'boundary_ONL/IS';'boundary_GCL/INL'};%;'boundary_Neuron/GCL'};
    retina.BQ_image_url = BQ.loadImage(retina.image_url);
    retina.num_layers = length(retina.segm_layers);
       
%  No user interaction for now, on the input image; 
    
% Get input image information
    %get_image_info();
    retina.image = uint8(BQ.loadImageData(retina.BQ_image_url));
    if(isempty(retina.image)); error(char(BQError.getLastError())); end  
 
% Search for training image if available in the database, and update the
% image to retina.image
    %search_training_image();

    %retina.train_image_url=char(BQ.findTag(retina.BQ_image_url, 'reference_image'));
    %if(isempty(retina.train_image_url)); error(char(BQError.getLastError())); end;
    
    retina.train_image_url = 'http://bodzio.ece.ucsb.edu:8080/ds/images/21212';
    image_ = BQ.loadImage(retina.train_image_url);
    
    retina.train_image = uint8(BQ.loadImageData(image_)); 
    if(isempty(retina.train_image)); error(char(BQError.getLastError())); end     

    % Load the training data from the image, else the user inputs the data

    [num_segm_layers,temp] = size(retina.segm_layers);
    retina.train_gt=cell(1,num_segm_layers); 

    %load_training_data();
    retina.train_gt = load_GObj_data(retina.train_image_url,'training_GT_data',retina.num_layers);
 
% perform the training
    retina.t_prof = cell(1,retina.num_layers); 
    retina.t_prof = retina_train(retina.train_image, retina.train_gt);
    
% Segment the input based on the training data 
    retina.segm_out = retina_segment(retina.image, retina.t_prof,retina.train_gt,retina.train_image);
    
% Save the segmentation output as GObjects
    retina_save_segm_out();

% Save the mask image if required
    retina_save_segm_mask();
    
    if(~strcmp(char(BQError.getLastError()),'')); error(char(BQError.getLastError())); end

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
%% Get the complete image information
% Need to change on the structure - retaining all the information for now
function get_image_info()
    import bisque.*
    BQ = BQMatlab;
    global retina;
    global userErrorMsg;
    %retina.gt_url = char(BQ.findTag(retina.BQ_image_url, 'GroundTruth_Layers'));   

    %recover the condition(group), sretina.BQ_imageURLubgroup and imagenumber to choose the appropriate training image
    %Segment input image according to
    %-group_num 1: N, 2: %3d, 3: 7d, 4: 28d
    %-sub_group for each group_num
    %-image_number for each sub_group
    %LOOK  UP TABLE
    %-------------------------------------
    %intialize the group,sub_group and image number:
    group_N{1} = 2:6;
    group_N{2} = 8:14;
    group_N{3} = 17:20;
    group_N{4} = 21:25;
    group_N{5} = [26 27 29:33];

    group_3d{1} = 1:13;
    group_3d{2} = 14:22;
    group_3d{3} = 23:31;
    group_3d{4} = [33 36 39 42 45];
    group_3d{5} = [34 37 40 43 46 48 49 50 51];
    group_3d{6} = [35 38 41 44 47];

    group_7d{1} = [1:4 6 8 10 11];
    group_7d{2} = [13 15 18 20 21];

    group_28d{1} = 1:5;
    group_28d{2} = 10:15;
    group_28d{3} = 17:24;
    group_28d{4} = 26:33;
    group_28d{5} = 34:39;
    group_28d{6} = 40:46;
    group_28d{7} = [47:55 58:65];

    %-------------------------------------
    im_group{1} = group_N;
    im_group{2} = group_3d;
    im_group{3} = group_7d;
    im_group{4} = group_28d;
    %-------------------------------------

    % Error 

    temp = char(BQ.findTag(retina.BQ_image_url, 'dataset_label'));
    if(isempty(temp) || ~strcmp(temp,'layer_boundary_segmentation'))
        userErrorMsg = 'Selected Image has no valid tag information. Tag: dataset_label=layer_boundary_segmentation. Unable to perform Segmentation';
        error(userErrorMsg);
    end

    % %find the group number from the tag of image_url
    retina.condition = char(BQ.findTag(retina.BQ_image_url, 'condition')); 
    if(isempty(retina.condition)); error(char(BQError.getLastError())); end   
    % requires changing for each group that you want segment
    switch retina.condition,
        case 'normal',
            retina.group_num=1;
        case '3d',
             retina.group_num=2;
        case '7d',
            retina.group_num=3;
        case '28d',
            retina.group_num=4;
    end

    retina.current_group = im_group{retina.group_num};
    %-------------------------------------
    %find the sub group number from the tag of image_url

    retina.subgroup = str2num(char(BQ.findTag(retina.BQ_image_url, 'subgroup'))); 
    if(isempty(retina.subgroup)); error(char(BQError.getLastError())); end   
    % requires changing the training image GT for each sub group that you want
    % segment
    retina.image_number = str2num(char(BQ.findTag(retina.BQ_image_url, 'image_number'))); 
    if(isempty(retina.image_number)); error(char(BQError.getLastError())); end   

    % requires changing the training image GT for each sub group that you want segment
    %!!!change here if you want to segment several times the same with
    %with different training images and build a vector with image_number of subgroup minus current image_number,

    % using only one training image
    num_train=1;
    for i=(retina.current_group{retina.subgroup}(1):retina.current_group{retina.subgroup}(end))
        if retina.image_number~=i
            retina.training_number{num_train}=i;
            num_train=num_train+1;
        end
    end

    % Load the input image to be segmented
    retina.image = uint8(BQ.loadImageData(retina.BQ_image_url));

    if(isempty(retina.image)); error(char(BQError.getLastError())); end  

end

%% Search for training image
function search_training_image()
    global retina;
    global userErrorMsg;
    import bisque.*
    BQ = BQMatlab;

    list = BQ.search(['condition:' retina.condition]);
    if(isempty(list)); error(char(BQError.getLastError())); end   

 %list=(BQGetImage.getImagesList('http://bodzio.ece.ucsb.edu:8080', ['condition:' retina.condition  ' and subgroup:' num2str(retina.subgroup) '
 % and  image_number:'  num2str(retina.training_number{1}) ] ));

    retina.train_image_url='';
    i=0;
    % image_ is a temp BQ image URL
    while (isempty(retina.train_image_url) &  i<=(list.size()-1)) %1:length(allimage_url)
             image_ = BQ.loadImage(list.get(i));
             subgroup = char(BQ.findTag(image_, 'subgroup'));

            if (~isempty(subgroup)& (str2num(subgroup)==retina.subgroup))
                image_number = (char(BQ.findTag(image_,'image_number')));
                if(isempty(image_number)); error(char(BQError.getLastError())); end   
                %CHANGE: here it can be changed and save all the url for all the training images and not only one
                if ~isempty(image_number)  & str2num(subgroup)==retina.subgroup & sum(str2num(image_number)==retina.training_number{1})~=0
                    retina.train_image_url=list.get(i);
                end
            end

       i=i+1;
    end

    % Check if the training image url is not empty
    if(strcmp(retina.train_image_url,''))
        userErrorMsg = 'Training Image unavailable for the input image!';
        error(userErrorMsg);
    end

    %initialize training image and gt for the retina image
    image_ = BQ.loadImage(retina.train_image_url);
    retina.train_image = uint8(BQ.loadImageData(image_)); 

    if(isempty(retina.train_image)); error(char(BQError.getLastError())); end        
end

%% Load the ground truth data from the image URL - used if the mask is generated from the stored gobjects of ref image
function pts = load_GObj_data(image_url,tag,num_layers)

    global userErrorMsg;

    import bisque.*
    BQ = BQMatlab;

    flag = 0;
    segm_layers={'boundary_bg/GCL';'boundary_IS/bg';'boundary_INL/ONL';'boundary_ONL/IS';'boundary_GCL/INL'}; % 'boundary_Neuron/GCL' not included
    %segm_layers={'boundary_bg/GCL';'boundary_GCL/INL';'boundary_INL/ONL';'boundary_ONL/IS';'boundary_IS/bg'}; % 'boundary_Neuron/GCL' not included
    
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

            %temp = size(polyline);
            %temp = num_layers;
            

            % indexing done in c style - For some reason, order of
            % Gobjects is reversed, as stored in the database
            
            for layer = 0:size(polyline)-1
                %search for the layer, as mentioned in the segm_layers
               loc = 1;
               while(strcmp(polyline.get(layer).name, segm_layers{loc}) ~= 1)    
                   loc = loc + 1;
                   if(loc > num_layers)
                        break;
                   end            
               end
               if(loc > num_layers)
                   continue;
               end
                   %get the vertices fromthe polyline gobject
                   vert = polyline.get(layer).vertices;
                   if(isempty(vert)); error(char(BQError.getLastError())); end

                   for v=0:size(vert)-1
                        index = vert.get(v).index.intValue + 1;
                        x = vert.get(v).x.doubleValue;
                        y = vert.get(v).y.doubleValue;

                        % pts stores all the vertices for all layers
                        pts{loc}(index,1) = x;
                        pts{loc}(index,2) = y;
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

%% Load the training data
function load_training_data()

    global retina;
    global userErrorMsg;
    import bisque.*
    BQ = BQMatlab;
    flag = 0;

    %get the GT data
    in_image = BQ.loadImage([retina.train_image_url '?view=deep']);

    image_gobj = in_image.gobjects;
    if(isempty(image_gobj)); error(char(BQError.getLastError())); end

    % for now, assume only one GT data exists
    % look here for adding profile data

    %take care of Mlab and C indexing used in GObject library
    for i = 0:size(image_gobj)-1

    %read from this tag, get all the polylines from these
        if(strcmp(image_gobj.get(i).name,'training_GT_data'))

            flag = 1;
            %get to the layer gobject

            polyline = image_gobj.get(0).gobjects;
            if(isempty(polyline)); error(char(BQError.getLastError())); end

            retina.num_layers = size(polyline);

            % indexing done in c style - For some reason, order of
            % Gobjects is reversed, as stored in the database

            temp = retina.num_layers;
            for layer = 0:size(polyline)-1

               if(strcmp(polyline.get(layer).name, retina.segm_layers{temp}))    

                   %get the vertices fromthe polyline gobject
                   vert = polyline.get(layer).vertices;
                   if(isempty(vert)); error(char(BQError.getLastError())); end

                   for v=0:size(vert)-1
                        index = vert.get(v).index.intValue + 1;
                        x = vert.get(v).x.doubleValue;
                        y = vert.get(v).y.doubleValue;

                        % pts stores all the vertices for all layers
                        retina.train_gt{temp}(index,1) = x;
                        retina.train_gt{temp}(index,2) = y;
                   end
                   temp = temp -1;
               else
                   % need to do something:: For now, flag an error
                   userErrorMsg = 'Incorrect Ground Truth Data labels in the Training Image';
                   error(userErrorMsg);  
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

%% Save the segmentation results as GObject in the input image
function retina_save_segm_out()

    global retina;
    global userErrorMsg;
    import bisque.*
    BQ = BQMatlab;
    % save the results of Retina.seg_out into the input image as
    % a hierarchy of gobjects

    % for now, assume only one GT data exists
    % look here for adding profile data

    %Delete existing Segmentation_Output results
    in_image_deep = BQ.loadImage([retina.image_url '?view=deep']);
    image_gobj = in_image_deep.gobjects;
    for i = 0:size(image_gobj)-1
        if(strcmp(image_gobj.get(i).name,'output_SEG_data'))
            BQ.deleteGObject(image_gobj.get(i));
        end
    end

    %add GObjects to it
    retina.GObject = BQ.createGObject('polyline_set','output_SEG_data');

    %create a GObject for every layer
    for cur_layer = 1:retina.num_layers
            %every layer will have a polyline
            polyline(cur_layer) = BQ.createGObject('polyline',retina.segm_layers{cur_layer});

           %now add the vertices to the polyline from the pts set
            cur_layer_temp = retina.segm_out{cur_layer};
            for i = 1:length(cur_layer_temp)
                %vert = [cur_layer_temp(i,1),cur_layer_temp(i,2)];
                % interchanging x and y coordinates - Mlab and GObjects
                % change in coordinate system
                vert = [cur_layer_temp(i,2),cur_layer_temp(i,1)];
                BQ.addVertices(polyline(cur_layer),vert);
            end

             %add the current layer to gt_data
            BQ.addGObject(retina.GObject,polyline(cur_layer));
    end

    %finally add the gt_data to the image
    retina.GObjectURL = char(BQ.saveGObjectURL(retina.BQ_image_url,retina.GObject));   

    %add tags to the segmentation output
    BQ.deleteTag(retina.BQ_image_url,'segmentationOut_GObj');
    tag = BQ.addTag(retina.BQ_image_url,'segmentationOut_GObj',char(retina.GObjectURL));
    if(isempty(tag)); error(char(BQError.getLastError())); end   
    res = BQ.saveTag(retina.BQ_image_url, tag);
    if(isempty(res)); error(char(BQError.getLastError())); end         

    BQ.deleteTag(retina.BQ_image_url,'training_image');
    tag2 = BQ.addTag(retina.BQ_image_url,'training_image',char(retina.train_image_url));
    if(isempty(tag2)); error(char(BQError.getLastError())); end   
    res2 = BQ.saveTag(retina.BQ_image_url, tag2);
    if(isempty(res2)); error(char(BQError.getLastError())); end     

end
    
%% Save the segmentation results as a mask image
function retina_save_segm_mask()

    global retina;
    global userErrorMsg;
    import bisque.*;
    BQ = BQMatlab;

    %get the image size
    r=size(retina.image,1);
    c=size(retina.image,2);

    %generate an empty mask
    im_mask = zeros(r,c);

    for layer=1:retina.num_layers
        %bg=5|GCL=4|IPL+INL+OPL=3|ONL=2|IS+OS=1|bg=0
        [line_ind,xy_line,mask] = f_pt2mask2((retina.segm_out{layer}),[r c],1);
        im_mask = im_mask + mask;
    end

    %%CHANGE HERE if you want to save the result of segmentation in the
    %%same format the ground truth is saved in Bisquick:
    %%% Groundtruth for bg=1|GCL=3|IPL+INL+OPL=22|ONL=7|IS+OS=21|bg=1

    segm_image=zeros(size(im_mask));
    segm_image((im_mask==0))=1;
    segm_image((im_mask==1))=21;
    segm_image((im_mask==2))=7;
    segm_image((im_mask==3))=22;
    segm_image((im_mask==4))=3;
    segm_image((im_mask==5))=2; % Neuron Layer - comment if necessary

    %save the mask image
    size_im = size(segm_image);
    new_image = BQ.initImage(size_im(1,1), size_im(1,2), 1, 1, 1, 8, 'uint8', 1);
    retina.segm_mask_url = BQ.saveImage(new_image, uint8(segm_image));    
    if(isempty(retina.segm_mask_url)); error(char(BQError.getLastError())); end

    %add a tag to the input image, linking it to the mask image
    BQ.deleteTag(retina.BQ_image_url,'layerSegmentation_mask');
    maskTag = BQ.addTag(retina.BQ_image_url, 'layerSegmentation_mask', char(retina.segm_mask_url));
    if(isempty(maskTag)); error(char(BQError.getLastError())); end     
    response = BQ.saveTag(retina.BQ_image_url, maskTag);
    if(isempty(response)); error(char(BQError.getLastError())); end   

    %add the gobject information to the mask image
    BQ_segm_image_url = BQ.loadImage(retina.segm_mask_url);

    %BQ.saveGObjectURL(BQ_segm_image_url,retina.GObject);

    %add tag information to the mask image
    BQ.deleteTag(BQ_segm_image_url,'image');
    BQ.deleteTag(BQ_segm_image_url,'segmentationOut_GObj');
    tag1 = BQ.addTag(BQ_segm_image_url,'image', retina.image_url);
    if(isempty(tag1)); error(char(BQError.getLastError())); end    
    tag2 = BQ.addTag(BQ_segm_image_url,'segmentationOut_GObj',char(retina.GObjectURL));
    if(isempty(tag2)); error(char(BQError.getLastError())); end   

    res1 = BQ.saveTag(BQ_segm_image_url, tag1);
    if(isempty(res1)); error(char(BQError.getLastError())); end 
    res2 = BQ.saveTag(BQ_segm_image_url, tag2);                        
    if(isempty(res2)); error(char(BQError.getLastError())); end                            

end
