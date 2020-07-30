function [f_measure_matrix]=f_get_fmeasure(seg_dir, gt_dir, suffix, condition, num_layers)


% function [f_measure_matrix]=f_get_fmeasure(seg_dir,gt_dir,suffix,condition,num_layers)
%
%
% this function gets the ground truth and segmenation masks and uses them
% to calculate the f_measure for Nhat Vu's retinal layer segmentation.
%
% inputs:
%
% seg_dir is where the segmentation results (masks and points) are stored
%
% gt_dir is where the ground truth masks are stored. This script uses those
% masks to calculate the f-measure weighted with area
%
% condition =   tells program which condition you want to use
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
% f_measure_matrix:
%       column 1    =   condition
%       column 2    =   subgroup
%       column 3    =   file number
%       column 4    =   f_measure for bg
%       column 5    =   f_measure for GCL
%       column 6    =   f_measure for INL
%       column 7    =   f_measure for ONL
%       column 8    =   f_measure for OS
%       column 9    =   f_measure for bg
%       column 10   =   weighted f_measure for all layers


f_measure_matrix=[];


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


        % get name of ground truth file
        if (file_num(i)<10)
            gt_name=[ gt_dir prefix1 prefix_tif '0' num2str(file_num(i)) ').mat'];
        else
            gt_name=[ gt_dir prefix1 prefix_tif num2str(file_num(i)) ').mat'];
        end

        % load ground truth
        eval(['load( ''' gt_name ''');']);
        %         disp(gt_name);

        % get the name of the segmentation results directory
        dir_name=[ seg_dir prefix2 num2str(subgroup) '/'];

        % find segmentations of same image as ground truth
        files=dir([dir_name '*mask' num2str(file_num(i)) '.mat']);

        num_files=size(files,1);
        f_measure_total=zeros(num_files,1);
        f_measure_layers=zeros(num_files,num_layers);

        % load each segmentation and get f_measure against the ground truth
        %   there are multiple files because we use different training
        %   images to produce segmentation
        for j=1:num_files
            eval(['load ' dir_name files(j,1).name ' final_mask']);
            % disp(files(j,1).name);
            [f_measure_total(j,1), f_measure_layers(j, :)] = f_measure_warea(final_mask, im_mask);
        end

        f_measure_matrix(end+1, :)= [ condition subgroup file_num(i) mean(f_measure_layers) std(f_measure_layers) mean(f_measure_total) std(f_measure_total)];

        % displays f_measure for each subgroup
        %  disp([num2str(mean(f_measure_total)) ' ' num2str(mean(f_measure_layers))]);

    end
    % displays progress of this function
    disp([prefix1 num2str(subgroup)]);
end

return
