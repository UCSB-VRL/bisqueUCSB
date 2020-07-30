% This script calculates the weighted f_measure (see f_measure_warea.m for
% details) for Nhat's retinal segmentation algorithm. It uses the
% f_get_fmeasure function to extract all the data. 

% Please note that this script finds the fmeasure by comparing the ground
% truth with ALL the segmentation masks created from Nhat's algorithm. To
% get the data for Nhat's algorithm we 

% Directories:
%
% seg_dir is where the segmentation results (masks and points) are stored
% gt_dir is where the ground truth masks are stored. This script uses those
% masks to calculate the f-measure weighted with area
seg_dir='/cluster/home/jose/code/Segmentation_layer/Results/';
gt_dir='/cluster/home/jose/code/Segmentation_layer/Retina_maskGT/';


% Parameters used:
%   Besides the directories f_get_fmeasure needs to know the suffix, condition, and num_layers
   
%   suffix: 
%       tells the program which ground truth files to use. For
%       example, if suffix = 'boundary_res_median.mat', then the program
%       will use those files ending with 'boundary_res_median.mat'.

%   num_layers:
%       tells the program how many layers are in the segmentation

%   condition:
%       there are four conditions in the current data set Normal, 3-day, 7-day
%       and 28-day. condition tells the function which of those you want to use
%       

suffix = 'boundary_res_median.mat';
num_layers=6;

%   Output:
%       full_matrix contains all the data for each 

full_matrix=[];
complete_fmeasure=[];

% gets f-measure for all conditions
for i=1:4;
    condition=i;
    
    [fmeasure_matrix]=f_get_fmeasurestd(seg_dir, gt_dir, suffix, condition, num_layers);

a=size(full_matrix,1)+1;
b=size(fmeasure_matrix,1)+a-1;
    full_matrix(a:b, :)=fmeasure_matrix;
    complete_fmeasure(end+1,:)=mean(fmeasure_matrix)
end

complete_fmeasure=complete_fmeasure';
complete_fmeasure(2:3,:)=[];
