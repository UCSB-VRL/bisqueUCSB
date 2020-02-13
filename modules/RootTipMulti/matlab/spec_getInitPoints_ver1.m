function [X] = spec_getInitPoints_ver1(FilePath,seedPackage,tipPackage,RAD,PHI)
% load corner
load(tipPackage,'corner_nb');
load(tipPackage,'corner_U');
load(tipPackage,'corner_BV');
% load seed counter
load(seedPackage,'seed_nb');
load(seedPackage,'seed_U');
load(seedPackage,'seed_BV');
I = double(imread(FilePath));
% find the init tips
X = spec_use_tip_finder_ver1(FilePath,seedPackage,tipPackage,RAD,PHI,0);




