function [VEC Samples] = spec_main_ver1(FileList,seedPackage,tipPackage,RAD,PHI,display_corner_sites,display_tracking)
warning off
TM = clock;
% get the initial points from the first image in the list
[InitPoints Samples] = spec_use_tip_finder_ver1(FileList{1},seedPackage,tipPackage,RAD,PHI,display_corner_sites);
% track the points
tm = clock;
[VEC] = spec_my_corner_TRACK(FileList,InitPoints(:,1:2),RAD,PHI,display_tracking);
fprintf(['Time to track root tips ' num2str(etime(clock,tm)) '.\n'])
fprintf(['Total algorithm time ' num2str(etime(clock,TM)) '.\n'])

%{
    FilePath = 'Y:\takeshi\Maize\IBM lines\Gravitropism\IBM4s3\';
    [FileList] = getFileList(FilePath,'.TIF');
    [VEC] = spec_main_ver1(FileList,...
            'N:\Measure Code\takeshi pipeline\seed_counter.mat',...
            'N:\Measure Code\takeshi pipeline\tip_counter2.mat',30,100,0,0);

%}
