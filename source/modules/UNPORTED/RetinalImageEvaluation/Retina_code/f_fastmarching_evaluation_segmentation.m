function [average_distance]=f_fastmarching_evaluation_segmentation(GT,SEG,im)

% function [average_distance]=f_fastmarching_evaluation(GT,SEG,im)
% 
% function uses fast marching to find the average distance between any two lines on 
%  any image. Here it is used to find the average distance between a ground
%  line and a SEG (output of a segmentation algorithm line) 
%  
% % % 
% inputs: 
% 
% 1) GT = (:,2) matrix containing points in ground truth line
% 2) SEG = (:,2) matrix containing points in SEG line
% 3) im = image for both gt and SEG
% 
% outputs:
% 
% 
% average_distance = scalare = average distance b/w lines
% 
% Jose Freire 8/19/2007
% jmhfreire@gmail.com

GT=round(GT);
SEG=round(SEG);

% Connects GT points and creates a mask where points =1
gt_mask_img = zeros(size(im));
for i = 1:size(GT,1)-1
   [search_path,I] = get_search_path(size(im),GT(i,2),GT(i,1),GT(i+1,2),GT(i+1,1)); 
   gt_mask_img(I)=1;
end
[I1, I2]=find(gt_mask_img==1);
gt_mask_line = [I1,I2];

% Connects SEG points and creates a mask where points =1
SEG_mask_img = zeros(size(im));
for i = 1:size(SEG,1)-1
   [search_path,I] = get_search_path(size(im),SEG(i,2),SEG(i,1),SEG(i+1,2),SEG(i+1,1)); 
   SEG_mask_img(I)=1;
end
[I1 , I2] = find(SEG_mask_img==1);
SEG_mask_line = [I1,I2];
% [SEG_mask_line(:,1) SEG_mask_line(:,2)]=find(SEG_mask_img==1);

% initialize matrices
A=ones(size(im,1),size(im,2));
B=zeros(size(im,1),size(im,2));

% create distance matrix using ground truth mask
dist_matrix1=Fast_Marching_OP(A,gt_mask_img,B);

% create matrix of distances from gt to SEG
dist_index1=sub2ind(size(im),SEG_mask_line(:,1),SEG_mask_line(:,2));
dist_gt2SEG=dist_matrix1(dist_index1);

% compute average distances from gt to SEG
avg_dist_gt2SEG=sum(dist_gt2SEG)/length(dist_gt2SEG);

% create distance matrix using SEG mask
dist_matrix2=Fast_Marching_OP(A,SEG_mask_img,B);

% create matrix of distances from SEG to gt
dist_index2=sub2ind(size(im),gt_mask_line(:,1),gt_mask_line(:,2));
dist_SEG2gt=dist_matrix2(dist_index2);

% compute average distances from SEG to gt
avg_dist_SEG2gt=sum(dist_SEG2gt)/length(dist_SEG2gt);

% find the average of the above average distances
average_distance=(avg_dist_SEG2gt+avg_dist_gt2SEG)/2;

return