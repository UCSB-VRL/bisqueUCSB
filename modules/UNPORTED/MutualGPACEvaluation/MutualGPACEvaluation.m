function ErrorMsg = MutualGPACEvaluation(client_server, image_url, Retlayer, user, password)
%client_server='http://bodzio.ece.ucsb.edu:8080';image_url='http://bodzio.ece.ucsb.edu:8080/ds/images/5051';user='admin'; password='admin';Retlayer='ONL';

%INPUT: image_url of input image to be segmented and comparted to ground 
%       Retlayer 
%truth


%% Path
%javaaddpath('Z:\Elisa\PostImagetoBisquick\Statistcs\interface_V2');
%addpath Z:\Elisa\PostImagetoBisquick\UploadRetina\Retina_code
ErrorMsg = '';
%addpath('../modules/MutualGPACEvaluation/Retina_code/');
irtdir = which('MutualGPACEvaluation.m');
[irtdir dummy] = fileparts(irtdir);
clear dummy;
path([irtdir '/Retina_code'], path)
disp(['Adding to path ' [irtdir '/lib']]);
%addpath('./Retina_code/');
javaaddpath('../../lib/bisque.jar');
import bisque.*

%% MAIN

%%VAR
% try
    if (strcmp(Retlayer,''))
        Retlayer = 'ONL';
    end

    BQ = BQMatlab;
    BQ.login(user, password);

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

try
if (strcmp(Retlayer, 'ONL'))
    
    retina.layer=255;
    retina.gt_image=retina_loadgtmask(retina.image_url,retina.user,retina.password,'GroundTruth_ONL');
    retina.seglayer=7;
elseif (strcmp(Retlayer, 'IS'))
    
    retina.layer = 8;
    retina.seglayer = 8;
    retina.gt_image=retina_loadgtmask(retina.image_url,retina.user,retina.password,'GroundTruth_Layers');
elseif (strcmp(Retlayer, 'OS'))
    
    retina.layer = 9;
    retina.seglayer = 9;
    retina.gt_image=retina_loadgtmask(retina.image_url,retina.user,retina.password,'GroundTruth_Layers');
elseif (strcmp(Retlayer, 'ML'))
    
    retina.layer = 11;
        retina.seglayer = 11;
    retina.gt_image=retina_loadgtmask(retina.image_url,retina.user,retina.password,'GroundTruth_Layers');
elseif (strcmp(Retlayer, 'BG'))
    
    retina.layer = 1;
    retina.seglayer = 1;
    retina.gt_image=retina_loadgtmask(retina.image_url,retina.user,retina.password,'GroundTruth_Layers');
else
    
    retina.layer = 255;
    retina.seglayer = 7;
    retina.gt_image=retina_loadgtmask(retina.image_url,retina.user,retina.password,'GroundTruth_ONL');
end


retina.segmentation=retina_loadsegmmask(retina.image_url,retina.user,retina.password,['Layer_' Retlayer '_Segmentation_mask']);




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
% catch
%     lasterror
%     return;
% end
% 
% %%

%%
    function mask=retina_loadsegmmask(url,user,pass,tag)
        image = BQ.loadImage(url);
        segm_url = char(BQ.findTag(image,tag));

        if(isempty(segm_url)); error(char(BQError.getLastError())); end      
        image = BQ.loadImage(segm_url);    
        im_mask=uint8(BQ.loadImageData(image));
        if(isempty(im_mask)); error(char(BQError.getLastError())); end          
        %%% Groundtruth for bg=1|GCL+IPL+INL+OPL=4|ONL=7|IS=8|OS=9|bg=1

        segm_image=zeros(size(im_mask));
        segm_image(find(im_mask~=retina.seglayer))=0;
        segm_image(find(im_mask==retina.seglayer))=1;
        mask=segm_image;
    end
%%
    function mask=retina_loadgtmask(url,user,pass,tag)

        image = BQ.loadImage(url);
        retina.gt_url = char(BQ.findTag(image,tag));
        if(isempty(retina.gt_url)); error(char(BQError.getLastError())); end          
        

        gt_url = char(BQ.findTag(image,tag));
        gt_url = char(BQ.findTag(image,tag));
        if(isempty(gt_url)); error(char(BQError.getLastError())); end          
        image = BQ.loadImage(gt_url);
        im_mask=uint8(BQ.loadImageData(image));
        if(isempty(im_mask)); error(char(BQError.getLastError())); end 
        
        if isempty(find(im_mask==retina.layer))
           error('This layer does not have a ground truth');
           return
        end
        
        % Groundtruth for bg=1|GCL+IPL+INL+OPL=4|ONL=7|IS=8|OS=9|bg=1
        gt_image=zeros(size(im_mask));
        gt_image(find(im_mask~=retina.layer))=0;
        gt_image(find(im_mask==retina.layer))=1;
        mask=gt_image;
    end
%%

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
    
   for i=1:length(retina.f_measure_layers)
       if (retina.precision(i) + retina.recall(i))==0
           
        retina.f_measure_layers(i)=0;
       end
   end
   
    
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
    precision=sprintf('%3.3f;',retina.precision(1));
    recall=sprintf('%3.3f;',retina.recall(1));
    false_alarm_rate=sprintf('%3.3f;',retina.false_alarm_rate(1));
    f_measure_vector=sprintf('%3.3f;',retina.f_measure_layers(1));
    wf_measure_vector=sprintf('%3.3f;',retina.wf_measure_total);
   

    
precision_tag = BQ.addTag(image, ['precision ' Retlayer],  (precision));
    if(isempty(precision_tag)); error(char(BQError.getLastError())); end  
    
    response = BQ.saveTag(image, precision_tag);
    if(isempty(response)); error(char(BQError.getLastError())); end  
    
    recall_tag = BQ.addTag(image, ['recall (sensitivity) ' Retlayer] ,  (recall));
    if(isempty(recall_tag)); error(char(BQError.getLastError())); end  
    
    response = BQ.saveTag(image, recall_tag);
    if(isempty(response)); error(char(BQError.getLastError())); end  
    
    false_alarm_rate_tag = BQ.addTag(image, ['false alarm rate (1-specificity) ' Retlayer] ,   (false_alarm_rate));
    if(isempty(false_alarm_rate_tag)); error(char(BQError.getLastError())); end  
    
    response = BQ.saveTag(image,  false_alarm_rate_tag);
    if(isempty(response)); error(char(BQError.getLastError())); end  
    
    f_measure_tag = BQ.addTag(image, ['f_measure '  Retlayer],  (f_measure_vector));
    if(isempty(f_measure_tag)); error(char(BQError.getLastError())); end  
    
    response = BQ.saveTag(image, f_measure_tag);
    if(isempty(response)); error(char(BQError.getLastError())); end  
    
    w_fmeasure = BQ.addTag(image, ['w_fmeasure '  Retlayer], (wf_measure_vector));
    if(isempty(w_fmeasure)); error(char(BQError.getLastError())); end  
    
    response = BQ.saveTag(image, w_fmeasure);
    if(isempty(response)); error(char(BQError.getLastError())); end  
end
end

