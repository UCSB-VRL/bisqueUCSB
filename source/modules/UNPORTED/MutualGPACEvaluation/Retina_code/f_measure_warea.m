function [f_measure_total, f_measure_layers] = f_measure_warea(SEG, GT)

%function [f_measure_total, f_measure_layers] = f_measure_warea(SEG, GT)
%
%function takes the matrices of two images (segmentation and ground truth)
%and calculates the f-measure for the total image and for each layer 
%
% The total f-measure weights each layer based on the proportion of its
% area to the total area of the image.

%INPUTS:
%   segmentation_result = segmented image matrix
%   ground_truth = ground truth image matrix
%
%OUTPUTS
%
%   f_measure_total = sum of f_measures*normalized area
%       where normalized area = layer area/total area
%
%   f_measure_layers =    2pr/(p+r)
%       where p = precision for one layer
%       where r = recall for one layer

[truth, false_negative, false_positive, precision, recall] = f_discrepancy(SEG, GT);

% find the number of layers
layers = length(precision);

% initialize matrices
area(1:layers) = 0;

% calculate size of SEG
total_area = size(SEG, 1)*size(SEG, 2);

% calculate f_measure for each layer
f_measure_layers = (2*precision.*recall)./(precision + recall);

% find the area (the number of pixels) in each layer
for i = 1:layers,
    area(i) = length(find(SEG == layers - i))/total_area;
end

% F_measure calculation normalized with area of each layer
f_measure_total = sum(f_measure_layers.*area);

return
