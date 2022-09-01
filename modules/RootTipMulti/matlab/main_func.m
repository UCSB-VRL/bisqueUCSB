function [VEC] = main_func(FilePath,bFile,sFile,RAD,PHI)
[FileList] = getFileList(FilePath,'.TIF');
[InitPoints] = getInitPoints(FileList,bFile,sFile,RAD,PHI);
[VEC] = my_corner_TRACK(FileList,InitPoints(:,1:2),RAD,PHI,0);

%{
main_func('Y:\takeshi\Maize\IBM lines\Gravitropism\IBM160s2\',...
            'N:\Measure Code\takeshi pipeline\tip_counter.mat',...
            'N:\Measure Code\takeshi pipeline\seed_counter.mat',30,100);
%}