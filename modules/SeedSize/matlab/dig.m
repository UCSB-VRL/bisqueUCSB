function [FileList] = dig(FilePath,FileList,FileExt,verbose)
dirList = dir(FilePath);
ridx = strcmp({dirList.name},'.') | strcmp({dirList.name},'..');
dirList(ridx) = [];
if size(dirList,2) ~= 0
    for listing = 1:size(dirList,1)
        current_Path = [FilePath dirList(listing).name];
        typed_path = regexprep(current_Path,filesep,[filesep filesep]);
        if verbose
            fprintf(['Looking at:' typed_path '\n']);
        end
        if dirList(listing).isdir
            FileList = Wdig([current_Path filesep],FileList,FileExt,verbose);
        else
            FileExt;
            dirList(listing).name(end-2:end);
            if any(strcmp(FileExt,dirList(listing).name(end-2:end)))
                FileList{end+1,1} = current_Path;
            end
        end
    end
end
