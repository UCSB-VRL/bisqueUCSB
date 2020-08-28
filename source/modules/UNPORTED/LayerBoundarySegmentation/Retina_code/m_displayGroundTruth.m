% m_displayGroundTruth
% Displays the ground truth retinal layer boundaries for the five layers:
% 1) bg/GCL, 2) GCL/INL, 3) INL/ONL, 4) ONL/IS, and 5) IS/bg.
% Note that you must change the parameter group_num below to display the
% normal, 3day, 7day, or 28day image groups.
%
% Need: get_file_list.m, f_pt2mask2.m and m-files therein
%
% Nhat Vu
% June.02.2007

clear all;
addpath /cluster/home/jose/code/Segmentation_layer/RetinaSnake
%--------Image Subgroups----------------
% These are subgroups that are visually similar in that they were probably
% taken during the same experiment or same staining level/microscrope 
% parameter settings.  Note that note all images were used because some did
% not look like they belonged to any group, etc.

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

%------Display GT for each group------
% requires changing for each group that you want to view

% loop runs through each of the four groups
for group_num = 1:4, 
% group_num = 4;  % 1: N, 2: 3d, 3: 7d, 4: 28d
current_group = im_group{group_num};

% image directory
switch group_num,
    case 1,
        dir_in = '../Retina_RO_GFAP/N';
        dir_out = '../Retina_maskGT/N';
        current_name = 'N_im';
    case 2,
        dir_in = '../Retina_RO_GFAP/3d';
        dir_out = '../Retina_maskGT/3d';
        current_name = '3d_im';
    case 3,
        dir_in = '../Retina_RO_GFAP/7d';
        dir_out = '../Retina_maskGT/7d';
        current_name = '7d_im';
    case 4,
        dir_in = '../Retina_RO_GFAP/28d';
        dir_out = '../Retina_maskGT/28d';
        current_name = '28d_im';
end

% get image names (all tif images in directory)
id = '.TIF*';
im_name = get_file_list(dir_in,id);
n_image = length(im_name);


% loop through subsets in a group
for n = 1:length(current_group),
    
    % loop through images in a subset
    for k = 1:length(current_group{n}),
        
        name_dat = strcat(dir_in,'/dat_gt_',current_name,num2str(current_group{n}(k)));
        disp(name_dat);
        [a_temp,name_gt,c_temp,d_temp]=fileparts(name_dat);
        % assign only file name to name_mask
        [a_temp,name_mask,c_temp,d_temp]=fileparts(im_name{current_group{n}(k)});
       
        % load image and histogram equalize each channel
        name_temp = strcat(dir_in,'/',im_name{current_group{n}(k)});
        im = imread(name_temp);
        [r,c,z] = size(im);
        for i = 1:2,
            im(:,:,i) = histeq(im(:,:,i));
        end
                
        % load gt dat file (contains pts_orig = 1x6 cell with each element
        % containing N x 2 xy point coordinates)
        load(name_dat,'pts_orig');
        
        % Create grayscale image with one value for each layer.
        % Binary masks for each layer can be extracted by thresholding the
        % resulting im_mask image.
        im_mask = zeros(r,c);
        for j = 1:6, %bg=6|GCL=5|IPL=4|INL+OPL=3|ONL=2|IS+OS=1|bg=0
            [line_ind,xy_line,mask] = f_pt2mask2(fliplr(pts_orig{j}),[r c],1);
            im_mask = im_mask + mask;
        end
 
        %bg=1|GCL=3|IPL=4|INL+OPL=20|ONL=7|IS+OS=21|bg=1
        im_mask(find(im_mask==1))=21;
        im_mask(find(im_mask==6))=1;
        im_mask(find(im_mask==3))=20;
        im_mask(find(im_mask==5))=3;
        im_mask(find(im_mask==2))=7;
        im_mask(find(im_mask==0))=1;
        
        
%         
%         % plot contour boundary on top of image (last cell element not used)        
%         figure(1); imshow(im); hold on;
%         plot(pts_orig{1}(:,1),pts_orig{1}(:,2),'r*-','linewidth',2); hold on;  % bg/GCL
%         plot(pts_orig{5}(:,1),pts_orig{5}(:,2),'m*-','linewidth',2); hold on;  % GCL/INL
%         plot(pts_orig{3}(:,1),pts_orig{3}(:,2),'b*-','linewidth',2); hold on;  % INL/ONL
%         plot(pts_orig{4}(:,1),pts_orig{4}(:,2),'y*-','linewidth',2); hold on;  % ONL/IS
%         plot(pts_orig{2}(:,1),pts_orig{2}(:,2),'w*-','linewidth',2); hold on; % IS/bg
%         plot(pts_orig{6}(:,1),pts_orig{6}(:,2),'m.-','linewidth',2); hold off; % Neuron/GCL layer (not used)
%         title(name_temp);
%         
%         figure(2); imagesc(im_mask); colormap gray; axis equal; axis tight;
        % saving files into directories and files
        
        
        
%      % write mask file in .png format
      imwrite(uint8(im_mask),[dir_out '/' name_mask '.png'], 'png')
      imwrite(uint8(im_mask),[dir_out '/' name_gt '.png'], 'png')
      imwrite(uint8(im_mask),[dir_out '/' name_mask '.jpg'], 'jpg')
      imwrite(uint8(im_mask),[dir_out '/' name_gt '.jpg'], 'jpg')
%    
%      % save the mask file in .mat format 
%      save ([dir_out '/' name_mask], 'im_mask');
        
    end
end
end