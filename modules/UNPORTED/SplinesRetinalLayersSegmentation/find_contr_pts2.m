function [ContrPoint ContrPointsInfo tot_num_con_pts]=find_contr_pts2(im,min_dist)
%
% [ContrPoint ContrPointsInfo]=find_contr_pts2(im_mask,RM,min_dist)
%
% Finds the control points 
%
% im_mask -> image mask
% NCONPTS -> number of desired control points
% min_dist -> minimum distance
%
% Luca Bertelli - lbertelli@ece.ucsb.edu
% version 0.01
% Vision Research Lab
% University of California, Santa Barbara
% July 2007       

[n,m,l]=size(im);
ContrPoint=zeros(n,m);
tot_num_con_pts=0;

NCONPTS=numel(20:min_dist:n-20)*numel(20:min_dist:m-20);
ContrPointsInfo=zeros(NCONPTS,4);
for i=20:min_dist:n-20
    for j=20:min_dist:m-20
        
        ContrPoint(i,j)=1;
        tot_num_con_pts=tot_num_con_pts+1;
        ContrPointsInfo(tot_num_con_pts,3)=i;
        ContrPointsInfo(tot_num_con_pts,4)=j;
        
    end
    
end
if(NCONPTS~=tot_num_con_pts)
    error('Error in the contol points');
end