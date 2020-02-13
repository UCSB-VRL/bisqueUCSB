function [avg_matrix avg_boundary_distance]=f_evaluate(data_dir, gt_dir, save_dir, file_name, suffix, condition, num_layers)


% data_dir='/cluster/home/jose/code/Segmentation_layer/Results/';
% gt_dir='/cluster/home/jose/code/Segmentation_layer/Retina_RO_GFAP/';
% save_dir='/cluster/home/jose/results/';
% file_name='fm_matrix_median';
% suffix = 'boundary_res_median.mat'

% function [avg_matrix]=f_evaluate(data_dir, gt_dir, save_dir, file_name, condition, num_layers)
% 
% 
% this function finds the average distance between ground truth and Nhat Vu's 
% retinal segmentation algorithm.
%
% inputs:
% 
% data_dir  =   directory where segmentation results are stored.
% **** Must be stored in current format of P{a,b} where a is the file segmented
% and b is the segmented layer. see examples in:
% /cluster/home/jose/code/Segmentation_layer/Results
% 
% gt_dir    =   directory where ground truth is stored
% **** Must be stored in current format of pts_orig r c z see 
% /cluster/home/jose/code/Segmentation_layer/Retina_RO_GFAP/ for examples
% 
% save_dir  =   directory where evaluation results will be saved
%
% file_name =   prefix you want to use to name your files,  e.g.
%               avg_matrix_median
%
% condition =   tells program which condition you want to use to find the average
%               distance.
%               There are four conditions: Normal, 3-day, 7-day, 28-day
%               condition = 1 is Normal
%               condition = 2 is 3-day
%               condition = 3 is 7-day
%               condition = 4 is 28-day
%
% num_layers =  number of layers in the segmentation
%
%
% output:
%
% avg_matrix:
% column 1  =   number of condition (e.g. 1 = Normal)
% column 2  =   number of subgroup
% column 3  =   number of training file within subgroup
% column 4  =   number of testing file within subgroup
% column 5  =   average distance for bg/GCL boundary
% column 6  =   average distance for OS/bg boundary
% column 7  =   average distance for INL/ONL boundary
% column 8  =   average distance for ONL/OS boundary
% column 9  =   average distance for GCL/INL boundary
% 
% avg_boundary_distance:
% row 1     =   mean distance for all bg/GCL boundaries in condition
% row 2     =   mean distance for all GCL/INL boundaries in condition
% row 3     =   mean distance for all INL/ONL boundaries in condition
% row 4     =   mean distance for all ONL/OS boundaries in condition
% row 5     =   mean distance for all OS/bg boundaries in condition 



average_distance=zeros(1,5);
avg_matrix=[];

% condition = 1 for Normal; 2 for 3d, 3 for 7d, and 4 for 28d

% get # of files in subgroup
% get prefixes used for saving/loading files
switch condition
    case 1
        num_subgrp=5;
        prefix='dat_gt_N_im';
        prefix2='N_im_';
        prefix1='N/';
    case 2
        num_subgrp=6;
        prefix='dat_gt_3d_im';
        prefix2='3d_im_';
        prefix1='3d/';
    case 3
        num_subgrp=2;
        prefix='dat_gt_7d_im';
        prefix2='7d_im_';
        prefix1='7d/';
    case 4
        num_subgrp=7;
        prefix='dat_gt_28d_im';
        prefix2='28d_im_';
        prefix1='28d/';
end

% go through each subgroup for condition chosen
for subgroup=1:num_subgrp

    % get the number associated with each file in subgroup
    switch condition
        case 1
            switch subgroup
                case 1
                    file_num=2:6;
                case 2
                    file_num=8:14;
                case 3
                    file_num=17:20;
                case 4
                    file_num=21:25;
                case 5
                    file_num=[26 27 29:33];
            end
        case 2
            switch subgroup
                case 1
                    file_num=1:13;
                case 2
                    file_num=14:22;
                case 3
                    file_num=23:31;
                case 4
                    file_num=[33 36 39 42 45];
                case 5
                    file_num=[34 37 40 43 46 48:51];
                case 6
                    file_num=[35 38 41 44 47];
            end
        case 3
            switch subgroup
                case 1
                    file_num=[1:4 6 8 10 11];
                case 2
                    file_num=[13 15 18 20 21];
            end
        case 4
            switch subgroup
                case 1
                    file_num=1:5;
                case 2
                    file_num=10:15;
                case 3
                    file_num=17:24;
                case 4
                    file_num=26:33;
                case 5
                    file_num=34:39;
                case 6
                    file_num=40:46;
                case 7
                    file_num=[47:55 58:65];
            end
    end

    % go through files in subgroup
    for i=1:length(file_num)

        % load segmentation
        eval(['load ' data_dir prefix2 num2str(subgroup) '/' prefix num2str(file_num(i)) suffix ' P']);
        count=0;

        % load the ground truths that match segmentation result
        for j=1:length(file_num)

            % skip the training file
            if(file_num(j)~=file_num(i))

                count=count+1;

                % load ground truth
                eval(['load ' gt_dir prefix1 prefix num2str(file_num(j))  '.mat' ' pts_orig r c']);
                mask=zeros(r,c);

                % disp(['i=' num2str(condition) '  j=' num2str(subgroup) '  k=' num2str(i) '  m=' num2str(j) '  count=' num2str(count)]);

                % get average distance for each layer 
                for k=1:num_layers
                    P_gt=[];
                    P_seg=[];
                    P_seg=P{count,k};
                    P_gt(:,1)=pts_orig{1,k}(:,2);
                    P_gt(:,2)=pts_orig{1,k}(:,1);

                    % calculate average distance
                    [average_distance(1,k)]=f_fastmarching_evaluation_segmentation(P_gt,P_seg,mask);
                end
                % place average distance into matrix
                avg_matrix(end+1,:)=[condition subgroup i j average_distance];
            end
        end
    end
    disp([ prefix1 num2str(subgroup)]);
%     save([ save_dir file_name num2str(condition) num2str(subgroup) '.mat'],'avg_matrix');
end
output_row = mean(avg_matrix(:,5:end));
temp = output_row(end);
output_row(end)= output_row(2);
output_row(2)=temp;
avg_boundary_distance = output_row'; 
save([ save_dir file_name num2str(condition) '_output.mat'],'avg_boundary_distance','avg_matrix');

