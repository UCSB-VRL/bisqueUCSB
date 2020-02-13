function f_segment(save_dir, gt_dir, suffix, condition, num_layers)


% save_dir='/cluster/home/jose/code/Segmentation_layer/Results/';
% gt_dir='/cluster/home/jose/code/Segmentation_layer/Retina_RO_GFAP/';
% file_name='fm_matrix_median';
% suffix = 'boundary_res_median.mat'

% function []=f_segment(save_dir, gt_dir, condition, num_layers)
%
%
% this function segments retinal layers using Nhat Vu's retinal segmentation algorithm.
%
% inputs:
%
% save_dir  =   directory where segmentation results are saved.
% **** Must be stored in current format of P{a,b} where a is the file segmented
% and b is the segmented layer. see examples in:
% /cluster/home/jose/code/Segmentation_layer/Results
%
% gt_dir    =   directory where ground truth is stored
% **** Must be stored in current format of pts_orig r c z see
% /cluster/home/jose/code/Segmentation_layer/Retina_RO_GFAP/ for examples
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
% saves files in proper directories

% get # of files in subgroup
% get prefixes used for saving/loading files
switch condition
    case 1
        num_subgrp=5;
        prefix='dat_gt_N_im';
        prefix2='N_im_';
        prefix1='N/';
        prefix_tif='data (';
    case 2
        num_subgrp=6;
        prefix='dat_gt_3d_im';
        prefix2='3d_im_';
        prefix1='3d/';
        prefix_tif='data (';
    case 3
        num_subgrp=2;
        prefix='dat_gt_7d_im';
        prefix2='7d_im_';
        prefix1='7d/';
        prefix_tif='data (';
    case 4
        num_subgrp=7;
        prefix='dat_gt_28d_im';
        prefix2='28d_im_';
        prefix1='28d/';
        prefix_tif='data (';
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

        % get name of training picture
        if (file_num(i)<10)
            train_name=[ gt_dir prefix1 prefix_tif '0' num2str(file_num(i)) ').TIF'];
        else
            train_name=[ gt_dir prefix1 prefix_tif num2str(file_num(i)) ').TIF'];
        end
        load_name=[ gt_dir prefix1 prefix num2str(file_num(i)) '.mat'];
        count=0;

        % get names of testing images
        for j=1:length(file_num)

            % skip the training image
            if(file_num(j)~=file_num(i))
                % use correct testing image name
                if (file_num(j)<10)
                    test_name=[ gt_dir prefix1 prefix_tif '0' num2str(file_num(j)) ').TIF'];
                else
                    test_name=[ gt_dir prefix1 prefix_tif num2str(file_num(j)) ').TIF'];
                end

                % load ground truth points to find median
                eval(['load ' gt_dir prefix1 prefix num2str(file_num(j)) '.mat pts_orig']);

                count=count+1;

                % load median ground truth points
                % run algorithm for each layer
                for k=1:num_layers
                    switch k
                        case 1
                            x_in=median(pts_orig{1}(:,1));
                            current_layer=1;
                        case 2
                            x_in=median(pts_orig{2}(:,1));
                            current_layer=2;
                        case 3
                            x_in=median(pts_orig{3}(:,1));
                            current_layer=3;
                        case 4
                            x_in=median(pts_orig{4}(:,1));
                            current_layer=4;
                        case 5
                            x_in=median(pts_orig{5}(:,1));
                            current_layer=5;
                    end
                    % segment layer by layer using f_example
                    [Pts,im_test]=f_example(x_in,current_layer,test_name,train_name, load_name);
                    P{count, k} = Pts;
                end
            end
        end
        save([ save_dir prefix2 num2str(subgroup) '/' prefix num2str(file_num(i)) suffix]);
    end
    % displays programs progress
    disp([prefix1 num2str(subgroup)]);
end
return
