function [F_measure_region F_measure_boundary]= eval_segmentingretina(Seg,GT)

%function [F_measure_region, F_measure_boundary]= eval_segmentingretina(Seg,GT)
% AUTHOR:
% Elisa Drelie Gelasca drelie@ece.ucsb.edu
% DESC:
% computes the F-measure and other discrepancy measures in evaluating retinal layer segmentation 
%
% VERSION:
% 1.0
%
% INPUT:
% Seg: detection result by a segmenation algorithm 
% GT: ground truth for segmented region
%
% OUTPUT:

% F measure for boundary and region: harmonic mean of precision and recall
% (=2*p*r/(p+r))

% HISTORY
% 1.0.0             - 05/29/07 - trial version


[P_A,R_A,P_B,R_B] = Compute_PR(Seg,GT);
F_measure_region= (2*P_A*R_A)/(P_A+R_A);
F_measure_boundary=(2*P_B*R_B)/(P_B+R_B);

return