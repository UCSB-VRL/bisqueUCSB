function [FileSequences] = findFileSequences(rootPath)
FileList = {};
FileExt = {'tif','TIF'};
FileList = Wdig(rootPath,FileList,FileExt,1);
for i = 1:size(FileList,1)
%    [pathstr{i}, name{i}, ext, versn] = fileparts(FileList{i});
    [pathstr{i}, name{i}, ext] = fileparts(FileList{i});
    pathstr{i} = [pathstr{i} '\'];
end
FileSequences = unique(pathstr);
