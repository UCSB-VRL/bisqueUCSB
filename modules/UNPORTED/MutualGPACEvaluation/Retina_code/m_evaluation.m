close all; clear all; clc;

% This script runs through the all the values on one retinal layer
% condition to find the avg_distance for Nhat Vu's segmentation algorithm
% 
% If you want to find the average boundary distance for one single boundary
% use f_fastmarching_evaluation_segmentation(GT,SEG,im)
% 
% 

data_dir='/cluster/home/jose/code/Segmentation_layer/Results/';
gt_dir='/cluster/home/jose/code/Segmentation_layer/Retina_RO_GFAP/';
save_dir='/cluster/home/jose/results/';
file_name='avg_distance_median';
suffix='boundary_res.mat';
condition=3;
num_layers=5;

[avg_matrix avg_boundary_distance]=f_evaluate(data_dir, gt_dir, save_dir, file_name, suffix, condition, num_layers);