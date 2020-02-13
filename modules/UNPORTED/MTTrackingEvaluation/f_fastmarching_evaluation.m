function [max_distance average_distance]=f_fastmarching_evaluation(GT,Trace,im)

% function [max_distance average_distance]=f_fastmarching_evaluation(GT,Trace,im)
% 
% function uses fast marching to find the average distance between any two lines on 
%  any image. Here it is used to find the average and max distance between a ground
%  line and a trace (output of a tracing algorithm line) 
%  
% % % 
% inputs: 
% 
% 1) GT = (:,2) matrix containing points in ground truth line
% 2) Trace = (:,2) matrix containing points in trace line
% 3) im = image for both gt and trace
% 
% outputs:
% 
% 1) max_distance = scalar value = max distance b/w lines
% 2) average_distance = scalare = average distance b/w lines
% 
% Jose Freire 8/19/2007
% jmhfreire@gmail.com
% 11/08/07
%modified by Elisa to crop the part with MT

GT=round(GT);
Trace=round(Trace);

% Connects GT points and creates a mask where points =1
gt_mask_img = zeros(size(im,1),size(im,2));
for i = 1:size(GT,1)-1
   [search_path,I] = get_search_path(size(im),GT(i,2),GT(i,1),GT(i+1,2),GT(i+1,1)); 
   gt_mask_img(I)=1;
end
[I1, I2]=find(gt_mask_img==1);
gt_mask_line = [I1,I2];
l1=min(I2)-1;
r1=max(I2)+1;
u1=min(I1)-1;
b1=max(I1)+1;
% Connects Trace points and creates a mask where points =1
trace_mask_img = zeros(size(im,1),size(im,2));
for i = 1:size(Trace,1)-1
   [search_path,I] = get_search_path(size(im),Trace(i,2),Trace(i,1),Trace(i+1,2),Trace(i+1,1)); 
   trace_mask_img(I)=1;
end
[I1 , I2] = find(trace_mask_img==1);
trace_mask_line = [I1,I2];


%%FIND BOUNDING BOX TO SPEED UP
l2=min(I2)-1;
r2=max(I2)+1;
u2=min(I1)-1;
b2=max(I1)+1;
%%
l=min(l1,l2);
r=max(r1,r2);
u=min(u1,u2);
b=max(b1,b2);
%%

gt_mask_img1=imcrop(gt_mask_img,[l,(u),(r-l),(b-u)]); 

trace_mask_img1=imcrop(trace_mask_img,[l,(u),(r-l),(b-u)]); 
[I1 , I2] = find(trace_mask_img1==1);
trace_mask_line1 = [I1,I2];
[I1, I2]=find(gt_mask_img1==1);
gt_mask_line1 = [I1,I2];
% initialize matrices

A=ones(size(gt_mask_img1,1),size(gt_mask_img1,2));
B=zeros(size(gt_mask_img1,1),size(gt_mask_img1,2));
% create distance matrix using ground truth mask
dist_matrix1=Fast_Marching_OP(A,gt_mask_img1,B);

% create matrix of distances from gt to trace
dist_index1=sub2ind(size(gt_mask_img1),trace_mask_line1(:,1),trace_mask_line1(:,2));
dist_gt2trace=dist_matrix1(dist_index1);

% compute average and mask distances from gt to trace
avg_dist_gt2trace=sum(dist_gt2trace)/length(dist_gt2trace);
max_dist_gt2trace=max(dist_gt2trace);

% create distance matrix using trace mask
dist_matrix2=Fast_Marching_OP(A,trace_mask_img1,B);

% create matrix of distances from trace to gt
dist_index2=sub2ind(size(gt_mask_img1),gt_mask_line1(:,1),gt_mask_line1(:,2));
dist_trace2gt=dist_matrix2(dist_index2);

% compute average and mask distances from trace to gt
avg_dist_trace2gt=sum(dist_trace2gt)/length(dist_trace2gt);
max_dist_trace2gt=max(dist_trace2gt);

% find the average of the above average distances
average_distance=(avg_dist_trace2gt+avg_dist_gt2trace)/2;

% find the max of the max_distances
max_distance=max(max_dist_trace2gt, max_dist_gt2trace);
%%OLD CODE:
% 
% 
% 
% % initialize matrices
% A=ones(size(im,1),size(im,2));
% B=zeros(size(im,1),size(im,2));
% 
% % create distance matrix using ground truth mask
% dist_matrix1=Fast_Marching_OP(A,gt_mask_img,B);
% 
% % create matrix of distances from gt to trace
% dist_index1=sub2ind(size(im),trace_mask_line(:,1),trace_mask_line(:,2));
% dist_gt2trace=dist_matrix1(dist_index1);
% 
% % compute average and mask distances from gt to trace
% avg_dist_gt2trace=sum(dist_gt2trace)/length(dist_gt2trace);
% max_dist_gt2trace=max(dist_gt2trace);
% 
% % create distance matrix using trace mask
% dist_matrix2=Fast_Marching_OP(A,trace_mask_img,B);
% 
% % create matrix of distances from trace to gt
% dist_index2=sub2ind(size(im),gt_mask_line(:,1),gt_mask_line(:,2));
% dist_trace2gt=dist_matrix2(dist_index2);
% 
% % compute average and mask distances from trace to gt
% avg_dist_trace2gt=sum(dist_trace2gt)/length(dist_trace2gt);
% max_dist_trace2gt=max(dist_trace2gt);
% 
% % find the average of the above average distances
% average_distance=(avg_dist_trace2gt+avg_dist_gt2trace)/2;
% 
% % find the max of the max_distances
% max_distance=max(max_dist_trace2gt, max_dist_gt2trace);

return