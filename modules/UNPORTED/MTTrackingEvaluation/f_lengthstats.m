function [length_gt, length_trace, diff, percent_diff]= f_lengthstats(GT,TRACE)

% function [length_gt, length_trace, diff, percent_diff]=
% f_lengthstats(GT,TRACE)

length_gt=f_length_trace(GT);
length_trace=f_length_trace(TRACE);

diff=abs(length_gt-length_trace);
percent_diff=diff./length_gt;

return