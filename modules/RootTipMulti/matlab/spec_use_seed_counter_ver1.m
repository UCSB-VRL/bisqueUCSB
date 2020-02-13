function [NUMS] = spec_use_seed_counter_ver1(FileName,seedPackage)
% load seed package information for bayes analysis
load(seedPackage);
% read the image
J = imread(FileName);
% smooth and close to make the background
% subtract off background and normalize image
J = imfilter(J,fspecial('average',32));
background = imclose(J,strel('disk',60));
J = double(J) - double(background);
J = J - min(J(:));
J = J / max(J(:));
% otsu threshold image, clear border, remove small objects
% label the objects and measure the properties
level = graythresh(J);
B = ~im2bw(J,level);
B = imclearborder(B);
B = bwareaopen(B,1000);
L = bwlabel(B);        
R = regionprops(L,'Centroid','Area','Image','Eccentricity','MajorAxisLength','MinorAxisLength','Solidity','PixelIdxList');
TEMP = [[R.Area];[R.Eccentricity];[R.MajorAxisLength];[R.MinorAxisLength];[R.Solidity];reshape([R.Centroid],[2 size(R,1)])]';
% condense data - use only some of the data
[SIM C ERR] = PCA_REPROJ(TEMP(:,1:end-2),seed_BV,seed_U);                
C = [C ERR TEMP(:,end-1)];
% run simulation from bayes package
[post,cpre,logp] = posterior(seed_nb,C);
cpre(isnan(cpre)) = 0;
NUMS = sum(cpre);

%{
% test script one
FileName = 'Y:\takeshi\Maize\IBM lines\Gravitropism\IBM4s3\400000.tif';
SeedPackage = 'N:\Measure Code\takeshi pipeline\seed_counter.mat';
tic
[NUMS] = spec_use_seed_counter_ver1(FileName,SeedPackage);
toc
%}

