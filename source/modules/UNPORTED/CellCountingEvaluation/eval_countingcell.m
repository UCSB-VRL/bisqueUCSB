function error=eval_countingcell(ND, Manual)

% error=eval_countingcell(ND, Manual)
%
% AUTHOR:
% Elisa Drelie Gelasca drelie@ece.ucsb.edu
% DESC:
% computes the error in counting 
%
% VERSION:
% 1.0
%
% INPUT:
% ND: detection result by a Nucleus Detector  
% Manual: array of manual counts
%
% OUTPUT:

%  Error: percentage error between manual counts and result by a nucleus detector ( |ND-manual counts|/manual counts)

% HISTORY
% 1.0.0             - 05/25/07 - trial version


Manual_avg=mean(Manual);
error=abs(ND-Manual_avg)*100/Manual_avg;

return
