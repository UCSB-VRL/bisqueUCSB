function [f_measure_total, f_measure_layers] = f_measure(SEG, GT)

%function [f_measure_total, f_measure_layers] = f_measure(SEG, GT)
%
%function takes the matrices of two images (segmentation and ground truth)
%and calculates the f-measure for the total image and for each layer 
%
%INPUTS:
%   segmentation_result = segmented image matrix
%   ground_truth = ground truth image matrix
%
%OUTPUTS
%
%   f_measure_total =  (100/number of layers)*2pr/(p+r)
%       where p = the sum of precision for all layers
%       where r = the sum of recall for all layers
%
%   f_measure_layers =   100 * 2pr/(p+r)
%       where p = precision for one layer
%       where r = recall for one layer

[truth, false_negative, false_positive, precision, recall] = f_discrepancy(SEG, GT);


layers = length(precision);

for i = 1:layers,
    f_measure_layers(i) = 100*(2*precision(i)*recall(i))/(precision(i) + recall(i));
end
    
total_precision = sum(precision);
total_recall = sum(recall);

%   F measure calculation 
f_measure_total = (100/layers)*(2*total_precision*total_recall)/(total_precision + total_recall)
f_measure_layers

return
