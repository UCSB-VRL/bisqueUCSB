clear; close all; clc;
stack_dir = '/cluster/home/jose/everything/mt_trace_evaluation/mt_data/';
gt_dir = '/cluster/home/jose/everything/mt_trace_evaluation/ground_truth/';
gt_dir = '/cluster/home/jose/everything/mt_trace_evaluation/new_ground_truth/corey/combined/';
out_dir = '/cluster/home/jose/everything/mt_trace_evaluation/output/';

% these thresholds and weights are subject to change
% see comments in f_trace_error1 for details
weight1=.85; weight2=.10; weight3=.05;
threshold1=6;threshold2=3; threshold3=.15;

% find names and number of files in gt_dir
temp = dir([gt_dir,'*.mat']);
num_files = length(temp);

% initializations
% stack_name_list = {};
% frame_id_list = [];
% track_id_list = [];
microtubule_matrix=[];

% run through all files in ground truth directory
for file_id = 1:num_files
    mat_name = temp(file_id).name;
    
    % load ground truth
    eval(['load ',gt_dir,mat_name]);
    gt_trace = track;
    
    %load tracing algorithm's output (trace)
    eval(['load ',out_dir,mat_name]);
    mt_trace_output = track;
    
    
    [pathstr, name, ext, versn] = fileparts(stack_name);

    % run through all tracks in each file
    for track_id = 1:length(gt_trace{1})
        
        % run through all frames in each track
        for frame_num = 1:length(gt_trace)
            
            % check number of points in trace output and ground truth
            if ~isempty(mt_trace_output{frame_num}{track_id}) && size(gt_trace{frame_num}{track_id},1)>=3
%                 stack_name_list{end+1}=name;
%                 frame_id_list(end+1) = frame_num;
%                 track_id_list(end+1) = track_id;
 
                % get the image (needed for f_getstats_one_microtubule)
                stack_name1=[name,'.tif'];
                im=imread([stack_dir,stack_name1],frame_num);

                % microtubule vector contains: 
                % [tip_distance,average_distance,max_distance,length_gt,length_trace, ...
                % diff,percent_diff,hausdorff_distance,error]
                [microtubule_vector]=f_getstats_one_microtubule(...
                 gt_trace{frame_num}{track_id}(:,:), mt_trace_output{frame_num}{track_id}(:,:),...
                    im,threshold1,threshold2,threshold3,weight1,weight2,weight3);
                % creates a matrix with file# track# frame# and all
                % components of microtubule_vector
                microtubule_matrix(end+1, :)=[file_id, track_id, frame_num, microtubule_vector]
                pause
            end
        end
    end
end
