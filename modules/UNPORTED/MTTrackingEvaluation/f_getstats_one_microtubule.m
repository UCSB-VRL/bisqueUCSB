function [microtubule_vector]=f_getstats_one_microtubule(gt, trace, im,...
    threshold1, threshold2, threshold3, weight1, weight2, weight3)

% function [microtubule_vector]=f_getstats_one_microtubule(gt, trace, im_size,...
%     threshold1, threshold2, threshold3, weight1, weight2, weight3)
% 
% inputs: 
% 1)    gt should be a matrix of points with two columns and a row for each point
%       (x,y)
% 
% 2)    trace should also be a matrix of points with two colums and a row for
%       each point (x,y)
%
% 3)    im is image that gt and trace are both on
% 
% 4)    threshold1-3 are used to calculate Trace Error
%       at the time of writing this function thresholds were:
%           threshold1 was 6 pixels
%           threshold2 was 3 pixels
%           threshold3 was .15*length_gt
% 
% 5)    weights1-3 are used to calculate Trace Error% % % % % % % % % %
%           weight1 was .85
%           weight2 was .10
%           weight# was .05
%
% outputs:
%
% 1) a vector containing:
% [tip_distance,average_distance,max_distance,length_gt,length_trace, ...
%     diff,percent_diff,hausdorff_distance,error]
%
%
%
%
% jose freire 8-18-2007
% jose.freire@gmail.com

tip_distance=f_tip_distance(gt(end,:), trace(end,:));

hausdorff_distance=f_hausdorff_distance(gt, trace);

[length_gt, length_trace, diff, percent_diff]=f_lengthstats(gt, trace);

[max_distance average_distance]=f_fastmarching_evaluation(gt,trace,im);

[error]=f_trace_error1(tip_distance, average_distance,max_distance,diff,...
    percent_diff,threshold1,threshold2,threshold3,weight1,weight2,weight3);

microtubule_vector= [tip_distance,average_distance,max_distance, ...
    length_gt,length_trace,diff,percent_diff,hausdorff_distance,error];

return