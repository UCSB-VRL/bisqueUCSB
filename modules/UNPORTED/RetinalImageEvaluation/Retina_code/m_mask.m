

% This script creates all the masks needed for f-measure analysis
% on Nhat's algorithm
%
% If you want to segment a single layer of a single retinal image
% use f_example(x_in,current_layer,test_name,train_name,load_name)
% 
% 

save_dir='/cluster/home/jose/code/Segmentation_layer/Results/';
suffix='boundary_res_median.mat';
% condition=3;
num_layers=5;
im_size=[512 768];
f_mask(save_dir, suffix, condition, num_layers, im_size);