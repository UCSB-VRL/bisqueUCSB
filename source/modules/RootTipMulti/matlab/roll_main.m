function [MVEC FileName] = spec_roll_main(PATH,ret)
%matlabpool 4
cdir = dir(PATH);
cdir(1:2) = [];
cdir(end) = [];
%MVEC = [];
parfor i = 1:size(cdir,1)
    FilePath = [PATH cdir(i).name '\'];
    fprintf(['Op on ' cdir(i).name '\n']);

    [VEC] = main_func(FilePath,...
            'N:\Measure Code\takeshi pipeline\tip_counter2.mat',...
            'N:\Measure Code\takeshi pipeline\seed_counter.mat',30,100);
    MVEC{i} = VEC;
    FileName{i} = FilePath;
    fidx = findstr(FilePath,'\');
    ['N:\Measure Code\takeshi pipeline\results\' FilePath(fidx(end-1)+1:fidx(end)-1) '.mat']
    save(['N:\Measure Code\takeshi pipeline\results\' FilePath(fidx(end-1)+1:fidx(end)-1) '.mat'],'VEC')    
end
%matlabpool close
%{
    [VEC FileName] = spec_roll_main('Y:\takeshi\Maize\IBM lines\Gravitropism\',1);
%}