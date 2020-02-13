close all; clear all; clc;

% This script segments one retinal layer condition using Nhat Vu's algorithm
% 
% If you want to segment a single layer of a single retinal image
% use f_example(x_in,current_layer,test_name,train_name,load_name)
% 
% 

save_dir='/cluster/home/jose/code/Segmentation_layer/Results/';
gt_dir='/cluster/home/jose/code/Segmentation_layer/Retina_RO_GFAP/';
suffix='boundary_res.mat';
condition=3;
num_layers=5;

f_segment(save_dir, gt_dir, suffix, condition, num_layers);