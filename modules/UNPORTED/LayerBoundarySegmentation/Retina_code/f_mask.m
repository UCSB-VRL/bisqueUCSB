function f_mask(save_dir, suffix, condition, num_layers, im_size)


% save_dir='/cluster/home/jose/code/Segmentation_layer/Results/';
% gt_dir='/cluster/home/jose/code/Segmentation_layer/Retina_RO_GFAP/';
% save_dir='/cluster/home/jose/results/';
% file_name='fm_matrix_median';
% suffix = 'boundary_res_median.mat'

% function [avg_matrix]=f_evaluate(save_dir, gt_dir, save_dir, file_name, condition, num_layers)
%
%
% this function finds the average distance between ground truth and Nhat Vu's
% retinal segmentation algorithm.
%
% inputs:
%
% save_dir  =   directory where segmentation results are stored.
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
        eval(['load ' save_dir prefix2 num2str(subgroup) '/' prefix num2str(file_num(i)) suffix ' P']);
        count=0;

        % load the ground truths that match segmentation result
        for j=1:length(file_num)

            % skip the training file
            if(file_num(j)~=file_num(i))
                count=count+1;
                points=P(count,1:num_layers);
                [final_mask]=f_get1mask(points, im_size);
                eval(['save ' save_dir prefix2 num2str(subgroup) '/' prefix ...
                    num2str(file_num(i)) 'mask' num2str(file_num(j)) '.mat final_mask']);
            end
        end
    end
    disp([ prefix1 num2str(subgroup)]);
    %     save([ save_dir file_name num2str(condition) num2str(subgroup) '.mat'],'avg_matrix');
end