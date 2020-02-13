function [MVEC FileName] = spec_roll_main_ver1(inPATH,tipOUTPATH,samOUTPATH,ret)
%matlabpool 4
cdir = dir(inPATH);
cdir(1:2) = [];
cdir(end) = [];
for i = 1:size(cdir,1)
    FilePath = [inPATH cdir(i).name '\'];
    fprintf(['Op on ' cdir(i).name '\n']);
    [FileList] = getFileList(FilePath,'.TIF');
    [VEC Samples] = spec_main_ver1(FileList,...
            'N:\Measure Code\takeshi pipeline\seed_counter.mat',...
            'N:\Measure Code\takeshi pipeline\tip_counter2.mat',30,100,0,1);
    MVEC{i} = VEC;
    FileName{i} = FilePath;
    fidx = findstr(FilePath,'\');
    tp = [tipOUTPATH FilePath(fidx(end-1)+1:fidx(end)-1) '_tips.txt'];
    sp = [samOUTPATH FilePath(fidx(end-1)+1:fidx(end)-1) '_samples.txt'];
    %dlmwrite(tp,VEC');
    %dlmwrite(sp,Samples');
end
%matlabpool close
%{
    inPATH = 'Y:\takeshi\Maize\IBM (spectrum)\Gravitropism\';
    inPATH = 'Y:\takeshi\Maize\IBM lines\Gravitropism\';
    tipOUTPATH = 'N:\Measure Code\takeshi pipeline\results second run\tips\';
    tipOUTPATH = 'N:\Measure Code\takeshi pipeline\results third run\tips\';
    samOUTPATH = 'N:\Measure Code\takeshi pipeline\results third run\samples\';    
    [VEC FileName] = spec_roll_main_ver1(inPATH,tipOUTPATH,samOUTPATH,1);
%}