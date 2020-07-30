function ErrorMsg = RetinalImageEvaluation(client_server, image_url, user, password)
%USAGE
% ErrorMsg = RetinalImageEvaluation('http://bodzio.ece.ucsb.edu:8080','http://bodzio.ece.ucsb.edu:8080/ds/images/661','admin','admin')
ErrorMsg = '';


% Note : This effort was started towards the benchmarking, so that gobjects can be compared . It is incomplete
% Modules required to compare Gobject polylines, polygons etc, and derive difference statistics should be completed before aiming to complete this
% sharath@cs.ucsb.edu
%% Path

%addpath interface
%addpath ./Retina_code
addpath('../modules/RetinalImageEvaluation/Retina_code/');
%javaclasspath
javaaddpath('../../lib/bisque.jar');
import bisque.*
%% MAIN

%%VAR
try
    BQ = BQMatlab;
    BQ.initServers(client_server,client_server);
    BQ.login(user, password);

retina.pts_orig = cell(1,5); %layer ground truth from image_url
retina.P = cell(1,5); %layer segmented by Nhat's algorithm

retina.image_url=image_url;
retina.user=user;
retina.password=password;
%% Load

%load ground truth in pts_orig:
%pts_orig{1}  % bg/GCL
%pts_orig{5} % GCL/INL
%pts_orig{3} INL/ONL
%pts_orig{4} % ONL/IS
%pts_orig{2} % IS/bg
%pts_orig{6} % Neuron/GCL layer - comment if necessary

% retina.pts_orig=retina_loadgtdata(retina.image_url,retina.user,retina.password,'GroundTruth_Layers');
% retina.P=retina_loadgtdata(retina.image_url,retina.user,retina.password,'LayerBoundarySegmentation_mask');
% retina.segmentation=retina_loadsegmmask(retina.image_url,retina.user,retina.password,'LayerBoundarySegmentation_mask');
% retina.gt_image=retina_loadgtmask(retina.image_url,retina.user,retina.password,'GroundTruth_Layers');

retina.segm_layers={'boundary_bg/GCL';'boundary_IS/bg';'boundary_INL/ONL';'boundary_ONL/IS';'boundary_GCL/INL';'boundary_Neuron/GCL'};

retina.pts_orig = loadGObjData(retina.image_url,'training_GT_data');
retina.P = loadGObjData(retina.image_url,'output_SEG_data');
retina.segmentation=retina_loadsegmmask(retina.image_url,retina.user,retina.password,'layerSegmentation_mask');

mask_vals = [0,5,4,3,2,1,0]; %according to LBS
mask_vals = [1,12,11,7,8,9,1]; %according to GPAC

[ht wd] = size(retina.segmentation);
%retina.gt_image = call_f_pt2mask(retina.pts_orig,ht,wd,length(retina.segm_layers));

retina.gt_image = f_pt2mask1(retina.pts_orig,ht,wd,mask_vals);
% need to standardize for all the algorithms - disprepency b/w GPAC and LBS
    retina.gt_image(retina.gt_image==11)=4;
    retina.gt_image(retina.gt_image==7)=3;
    retina.gt_image(retina.gt_image==8)=2;
    retina.gt_image(retina.gt_image==1)=0; % wrong if the this and next line are interchanged
    retina.gt_image(retina.gt_image==9)=1;
    retina.gt_image(retina.gt_image==12)=5;

%%
%%Evaluate the segmentation in terms of boundary distances

 retina_evaluate_distance()
%%
%%Evaluate wfmeasure
 retina_evaluate_wfmeasure()
%%
%%Save
retina_save_evaluation()

if(~strcmp(char(BQError.getLastError()),'')); error(char(BQError.getLastError())); end    
catch
    err = lasterror;
    ErrorMsg = err. message;
    return;

end

%% 
function segm_image = call_f_pt2mask(pts,ht,wd,num_layers)
    
    %generate an empty mask
    im_mask = zeros(ht,wd);

    for layer=1:num_layers
        %bg=5|GCL=4|IPL+INL+OPL=3|ONL=2|IS+OS=1|bg=0
        [line_ind,xy_line,mask] = f_pt2mask2(pts{layer},[ht wd],1);
        im_mask = im_mask + mask;
    end

    %%CHANGE HERE if you want to save the result of segmentation in the
    %%same format the ground truth is saved in Bisquick:
    %%% Groundtruth for bg=1|GCL=3|IPL+INL+OPL=22|ONL=7|IS+OS=21|bg=1

    segm_image=zeros(size(im_mask));
    segm_image((im_mask==1))=0;
    segm_image((im_mask==21))=1;
    segm_image((im_mask==7))=2;
    segm_image((im_mask==22))=3;
    segm_image((im_mask==3))=4;
    segm_image((im_mask==2))=5; %Neuron layer - comment if necessary.
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

%%
function pts = loadGObjData(image_url,tag)

    global userErrorMsg;
    import bisque.*
    BQ = BQMatlab;
    flag = 0;

    %get the GT data
    in_image = BQ.loadImage([image_url '?view=deep']);

    image_gobj = in_image.gobjects;
    if(isempty(image_gobj)); error(char(BQError.getLastError())); end

    segm_layers={'boundary_bg/GCL';'boundary_IS/bg';'boundary_INL/ONL';'boundary_ONL/IS';'boundary_GCL/INL';'boundary_Neuron/GCL'};

    %take care of Mlab and C indexing used in GObject library
    for i = 0:size(image_gobj)-1

    %read from this tag, get all the polylines from these
        if(strcmp(image_gobj.get(i).name,tag))

            flag = 1;
            %get to the layer gobject

            polyline = image_gobj.get(i).gobjects;
            if(isempty(polyline)); error(char(BQError.getLastError())); end

            num_layers = size(polyline);

            % indexing done in c style - For some reason, order of
            % Gobjects is reversed, as stored in the database

            temp = num_layers;
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
                        %pts stored as [row,col]
                        pts{temp}(index,1) = x;
                        pts{temp}(index,2) = y;
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

%%
function pts=retina_loadgtdata(url,user,pass,tag)
%load gt data point into retina struct

image = BQ.loadImage(url);        
gt_url = char(BQ.findTag(image, tag));  

if(isempty(gt_url)); error(char(BQError.getLastError())); end
pts{1}=RetinaEvaluation(gt_url, 'boundary_bg/GCL' , user, password);
pts{5}=RetinaEvaluation(gt_url,'boundary_GCL/INL',user, password);
pts{3}=RetinaEvaluation(gt_url,'boundary_INL/ONL',user, password);
pts{4}=RetinaEvaluation(gt_url,'boundary_ONL/IS',user, password);
pts{2}=RetinaEvaluation(gt_url,'boundary_IS/bg',user, password);
% not used retina.pts_orig{6}=RetinaEvaluation(retina.gt_url,'boundary_Neuron/GCL',retina.user, retina.password);
end
function pts_orig=RetinaEvaluation(image_url, tag_name , user, password)
image = BQ.loadImage(image_url);        
tag = char(BQ.findTag(image, tag_name)); 

if(isempty(tag)); error(char(BQError.getLastError())); end
eval(['pts_orig = ',tag,';']);
end

%%
    function mask=retina_loadsegmmask(url,user,pass,tag)
        image = BQ.loadImage(url);        
        segm_url = char(BQ.findTag(image, tag));  

        if(isempty(segm_url)); error(char(BQError.getLastError())); end
        image = BQ.loadImage(segm_url);
        im_mask = uint8(BQ.loadImageData(image)); 

        if(isempty(im_mask)); error(char(BQError.getLastError())); end
        %%% Groundtruth for bg=1|GCL=3|IPL+INL+OPL=22|ONL=7|IS+OS=21|bg=1

        segm_image=zeros(size(im_mask));
        
       % segm_image(find(im_mask==0))=5;
        segm_image(find(im_mask==1))=0;
        segm_image(find(im_mask==3))=4;
        segm_image(find(im_mask==22))=3;
        segm_image(find(im_mask==7))=2;
        segm_image(find(im_mask==21))=1;
        mask=segm_image;
    end
%%
    function mask=retina_loadgtmask(url,user,pass,tag)

        image = BQ.loadImage(url);        
        retina.gt_url = char(BQ.findTag(image, tag)); 

        if(isempty(retina.gt_url)); error(char(BQError.getLastError())); end
        image = BQ.loadImage(retina.gt_url);
        retina.gt_image = uint8(BQ.loadImageData(image));
        
        if(isempty(retina.gt_image)); error(char(BQError.getLastError())); end

        gt_url = char(BQ.findTag(image, tag));
        
        if(isempty(gt_url)); error(char(BQError.getLastError())); end        
        image = BQ.loadImage(gt_url);
        im_mask = uint8(BQ.loadImageData(image));

        if(isempty(im_mask)); error(char(BQError.getLastError())); end        
        % Groundtruth for bg=1|GCL=3|IPL=4|INL+OPL=20|ONL=7|IS+OS=21|bg=1
        gt_image=zeros(size(im_mask));
        gt_image(find(im_mask==1))=0;
        gt_image(find(im_mask==3))=4;
        gt_image(find(im_mask==4))=3;
        gt_image(find(im_mask==20))=3;
        gt_image(find(im_mask==7))=2;
        gt_image(find(im_mask==21))=1;
        mask=gt_image;
    end
%%
%evaluate distance betweene layers
    function retina_evaluate_distance()
        for layer=1:5
             P_gt=[];
             P_seg=[];
             
             % Stored as (X,Y)
             P_seg=retina.P{layer};
             P_gt = [retina.pts_orig{1,layer}(:,1) retina.pts_orig{1,layer}(:,2)];
             
             %calculate average distance between P_gt and P_seg
             mask = zeros(size(retina.segmentation,1),size(retina.segmentation,2));
             [retina.layerdistance(layer)]=f_fastmarching_evaluation_segmentation(P_gt,P_seg,mask);
         end

         %%
    end
%%
%evaluate the f_weighted measure for layers and true, false positive
%and false negative pixels    
    function retina_evaluate_wfmeasure()
   
    
        
    [retina.truth, retina.false_negative, retina.false_positive, retina.precision, retina.recall, retina.false_alarm_rate] = f_discrepancy(retina.segmentation, retina.gt_image);
    % find the number of layers
    layers = length(retina.precision);

    % initialize matrices
    area(1:layers) = 0;

    % calculate size of SEG
    total_area = size(retina.segmentation, 1)*size(retina.segmentation, 2);

    % calculate f_measure for each layer
    retina.f_measure_layers = (2*(retina.precision).*(retina.recall))./(retina.precision + retina.recall);

    % find the area (the number of pixels) in each layer
    for i = 1:layers,
        area(i) = length(find(retina.segmentation == layers - i))/total_area;
    end

    % F_measure calculation normalized with area of each layer
    retina.wf_measure_total = sum(retina.f_measure_layers.*area);

    %%
    end
%%
%%
%%Save
%% Save
function retina_save_evaluation()

    %pts_orig{1}  % bg/GCL
%pts_orig{5} % GCL/INL
%pts_orig{3} INL/ONL
%pts_orig{4} % ONL/IS
%pts_orig{2} % IS/bg
    precision=sprintf('[');
    recall=sprintf('[');
    false_alarm_rate=sprintf('[');
    layerdistance = sprintf('[');
    f_measure_vector=sprintf('[');
    
        layerdistance=[layerdistance,sprintf('%f;',retina.layerdistance(1)),sprintf('%f;',retina.layerdistance(5)),sprintf('%f;',retina.layerdistance(3)),sprintf('%f;',retina.layerdistance(4)),sprintf('%f;',retina.layerdistance(2)) ];
        f_measure_vector=[f_measure_vector,sprintf('%f;',retina.f_measure_layers(4)),sprintf('%f;',retina.f_measure_layers(3)),sprintf('%f;',retina.f_measure_layers(2)),sprintf('%f;',retina.f_measure_layers(1))];
        precision=[precision, sprintf('%f;',retina.precision(4)), sprintf('%f;',retina.precision(3)), sprintf('%f;',retina.precision(2)), sprintf('%f;',retina.precision(1))];
        recall=[recall, sprintf('%f;',retina.recall(4)),sprintf('%f;',retina.recall(3)),sprintf('%f;',retina.recall(2)),sprintf('%f;',retina.recall(1))];
        false_alarm_rate=[false_alarm_rate, sprintf('%f;',retina.false_alarm_rate(4)),sprintf('%f;',retina.false_alarm_rate(3)),sprintf('%f;',retina.false_alarm_rate(2)),sprintf('%f;',retina.false_alarm_rate(1))];
   
    layerdistance=[layerdistance,sprintf(']')];
    precision=[precision,sprintf(']')];
    recall=[recall,sprintf(']')];
    false_alarm_rate=[false_alarm_rate,sprintf(']')];
    f_measure_vector=[f_measure_vector,sprintf(']')];


    image = BQ.loadImage(retina.image_url);
    layer_distance = BQ.addTag(image,'layer_distance', layerdistance);
    if(isempty(layer_distance)); error(char(BQError.getLastError())); end        
    response = BQ.saveTag(image, layer_distance);
    if(isempty(response)); error(char(BQError.getLastError())); end        
    precision_tag = BQ.addTag(image,'precision', precision);
    if(isempty(precision_tag)); error(char(BQError.getLastError())); end        
    response = BQ.saveTag(image, precision_tag);
    if(isempty(response)); error(char(BQError.getLastError())); end        
    recall_tag = BQ.addTag(image,'recall (sensitivity)', recall);
    if(isempty(recall_tag)); error(char(BQError.getLastError())); end        
    response = BQ.saveTag(image, recall_tag);
    if(isempty(response)); error(char(BQError.getLastError())); end        
    false_alarm_rate_tag = BQ.addTag(image,'false alarm rate (1-specificity)',  false_alarm_rate);
    if(isempty(false_alarm_rate_tag)); error(char(BQError.getLastError())); end        
    response = BQ.saveTag(image, false_alarm_rate_tag);
    if(isempty(response)); error(char(BQError.getLastError())); end        
    f_measure_tag = BQ.addTag(image,'f_measure', f_measure_vector);
    if(isempty(f_measure_tag)); error(char(BQError.getLastError())); end        
    response = BQ.saveTag(image, f_measure_tag);
    if(isempty(response)); error(char(BQError.getLastError())); end        
    w_fmeasure = BQ.addTag(image,'w_fmeasure',num2str(retina.wf_measure_total));
    if(isempty(w_fmeasure)); error(char(BQError.getLastError())); end        
    response = BQ.saveTag(image, w_fmeasure);
    if(isempty(response)); error(char(BQError.getLastError())); end        
end
end

