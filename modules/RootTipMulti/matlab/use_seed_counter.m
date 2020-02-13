function [NUMS] = use_seed_counter(I,nb,U,BV)
% gather domain data
J = imresize(I,1);
J = imfilter(J,fspecial('average',32));
background = imclose(J,strel('disk',60));
J = double(J) - double(background);
J = J - min(J(:));
J = J / max(J(:));
level = graythresh(J);
B = ~im2bw(J,level);
B = imclearborder(B);
B = bwareaopen(B,250);
E = edge(B);
L = bwlabel(B);        
R = regionprops(L,'Centroid','Area','Image','Eccentricity','MajorAxisLength','MinorAxisLength','Solidity','PixelIdxList');
TEMP = [[R.Area];[R.Eccentricity];[R.MajorAxisLength];[R.MinorAxisLength];[R.Solidity];reshape([R.Centroid],[2 size(R,1)])]';

% condense data
[SIM C ERR] = PCA_REPROJ(TEMP(:,1:end-2),BV,U);                
C = [C ERR TEMP(:,end-1)];

% run simulation
[post,cpre,logp] = posterior(nb,C);
cpre(isnan(cpre)) = 0;
NUMS = sum(cpre);