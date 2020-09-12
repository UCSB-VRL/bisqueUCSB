function [truth, false_negative, false_positive, precision, recall] = f_discrepancy(segmentation_result, ground_truth)

%function [truth, false_negative, false_positive] = f_discrepancy(segmentation_result, ground_truth)
%
%function takes the matrices of two images (segmentation and ground truth) and finds the truth,
%false negative, and false positive. 
%
%INPUTS:
%   segmentation_result = segmented image matrix
%   ground_truth = ground truth image matrix
%
%OUTPUTS
%
%   truth = vector with # of true values for each layer
%
%   false_positive = vector with # of false_positive values for each layer  
%
%   false_negative = vector with # of false_negative values for each layer
%
%   precision = precision of each layer
%
%   recall = recall of each layer

layers = length(unique(ground_truth));

truth = zeros(1, layers);
false_negative = zeros(1, layers);
false_positive = zeros(1, layers);
precision = zeros(1, layers);
recall = zeros(1, layers);
f_measure = zeros(1, layers);
  
%   running through six layers    
for i = 1:layers,
    
    %   Creating Matrix marked with ones for each segmented layer
    pos=find(segmentation_result==layers-i);
    label_segmentation_temp = zeros(size(ground_truth));
    label_segmentation_temp(pos) = 1;
     
    %   Creating Matrix marked with ones for each ground truth layer
    pos_GT=find(ground_truth==layers-i);
    label_ground_temp = zeros(size(ground_truth));
    label_ground_temp(pos_GT) = 1;
    
    %   Creating a test matrix where ground_truth = 3, false_positive = 2, and false_negative = 2   
    test_matrix = label_ground_temp + label_ground_temp + label_segmentation_temp;
    pos_t = find(test_matrix == 3);
    pos_fp = find(test_matrix == 1);
    pos_fn = find(test_matrix == 2);
    
    %   Populating vectors with total area of truth, false_positive, and
    %   false_negative
    truth(i) = length(pos_t);
    false_negative(i) = length(pos_fn);
    false_positive(i) = length(pos_fp);
    
    %   Calculate GT and Seg for each layer
    gt_sum = sum(sum(label_ground_temp));
    seg_sum = sum(sum(label_segmentation_temp));
    
    %   Calculate
    precision(i) = truth(i)/(seg_sum);
    recall(i) = truth(i)/(gt_sum);

end   

return