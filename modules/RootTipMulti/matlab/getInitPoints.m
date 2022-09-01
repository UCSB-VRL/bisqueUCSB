function [InitPoints] = getInitPoints(FileList,bFile,sFile,RAD,PHI)
% load corner
load(bFile,'corner_nb');
load(bFile,'corner_U');
load(bFile,'corner_BV');
% load seed counter
load(sFile,'seed_nb');
load(sFile,'seed_U');
load(sFile,'seed_BV');
I = double(imread(FileList{1}));
% find the init tips
InitPoints = use_tip_finder(I,RAD,PHI,corner_nb,corner_U,corner_BV,seed_nb,seed_U,seed_BV,0,0);