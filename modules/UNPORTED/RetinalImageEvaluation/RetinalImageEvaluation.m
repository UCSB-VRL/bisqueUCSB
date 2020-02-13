function ErrorMsg = RetinalImageEvaluation(client_server, image_url, user, password)
ErrorMsg = '';
%function m_loadtry(image_url, user, password)
%USAGE
%         m_loadtry('http://bodzio.ece.ucsb.edu:8080/ds/images/91','admin', 'admin')
%
%INPUT: image_url of input image to be segmented and comparted to ground
%truth


%% Path

%addpath interface
%addpath ./Retina_code
addpath('../modules/RetinalImageEvaluation/Retina_code/');
%javaclasspath
javaaddpath('../../lib/bisque.jar');
import bisque.*
%clc; close all;
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
%pts_orig{6} % Neuron/GCL layer (NOT USED)
retina.pts_orig=retina_loadgtdata(retina.image_url,retina.user,retina.password,'GroundTruth_Layers');
retina.P=retina_loadgtdata(retina.image_url,retina.user,retina.password,'LayerBoundarySegmentation_mask');
retina.segmentation=retina_loadsegmmask(retina.image_url,retina.user,retina.password,'LayerBoundarySegmentation_mask');
retina.gt_image=retina_loadgtmask(retina.image_url,retina.user,retina.password,'GroundTruth_Layers');

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
             P_seg=retina.P{layer};
             P_gt(:,1)=retina.pts_orig{1,layer}(:,2);
             P_gt(:,2)=retina.pts_orig{1,layer}(:,1);
             %     % calculate average distance between P_gt and P_seg
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

