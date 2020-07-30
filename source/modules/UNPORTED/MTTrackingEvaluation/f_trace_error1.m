function [error]=f_trace_error1(tip_distance, average_distance,...
    max_distance, diff, percent_diff,...
    threshold1, threshold2, threshold3, weight1, weight2, weight3)

% function [error]=f_trace_error1(tip_distance, average_distance,...
%     max_distance, diff, percent_diff,...
%     threshold1, threshold2, threshold3, weight1, weight2, weight3)
% 
%  calculates the Trace Error of a single microtubule. Trace Error is a
%  overall evaluation for microtubule tracing created by Elisa Drelie
%  Gelasca & Jose Freire
% 
%   inputs:
%           
%   tip_distance = distance from gt tip to trace tip
%                = should be a scalar value
% 
%   average_distance = average_distance between gt and trace (see
%   f_getstats_one_microtubule for details)
% 
%   max_distance = max distance between gt and trace (see
%   f_getstats_one_microtubule for details)
% 
%   diff = distance between gt and trace lengths
% 
%   percent_diff = (length of gt-length of trace)/ length gt
% 
%   output:
%   error is a row vector where first term contains the Trace Error
%   calculation and 
% 
%   Trace Error formula (briefly)
%   Trace Error = (weight1*tip)/t1 + (weight2*average_dist)/t2 + (weight3*diff)/threshold1



error=zeros(1, 5);


if (tip_distance<threshold1) && (max_distance<threshold1 && average_distance<threshold2) && (diff<threshold1)
    error(1,1)=(weight1*tip_distance)/threshold1+(weight2*average_distance)/threshold2+(weight3*diff)/threshold1;
    error(1,2)=1;
end
    if (tip_distance>threshold1)
    error(1,1)=1;
    error(1,3)=1;
    end
    if(max_distance>=threshold1 || average_distance>=threshold2)
    error(1,1)=1;
    error(1,4)=1;
    end
  if (diff>=threshold1)
    error(1,1)=1;
    error(1,5)=1;
end

return