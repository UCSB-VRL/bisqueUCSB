function [MVEC] = roll_samp(PATH)
figure;
cdir = dir(PATH);
cdir(1:2) = [];
cdir(end) = [];
MVEC = [];
for i = 1:size(cdir,1)
    FilePath = [PATH cdir(i).name '\'];
    [FileList] = getFileList(FilePath,'.TIF');
    I = double(imread(FileList{1}));
    [X] = my_corner(I,1,1,1,30,100);
    MVEC = [MVEC ; X];
    drawnow
    fprintf(['Done sampling ' num2str(i) ' of ' num2str(size(cdir,1)) '\n'])
end
%{
    VEC = roll_samp('Y:\takeshi\Maize\IBM lines\Gravitropism\');
%}