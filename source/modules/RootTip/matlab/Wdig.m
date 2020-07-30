function [FileList] = Wdig(FilePath,FileList,FileExt,verbose)
dirList = dir(FilePath);
ridx = strcmp({dirList.name},'.') | strcmp({dirList.name},'..');
dirList(ridx) = [];
if size(dirList,2) ~= 0
    for listing = 1:size(dirList,1)
        current_Path = [FilePath dirList(listing).name];
        typed_path = regexprep(current_Path,'\','\\\');
        if verbose
            fprintf(['Looking at:' typed_path '\n']);
        end
        if dirList(listing).isdir
            FileList = Wdig([current_Path '\'],FileList,FileExt,verbose);
        else
            FileExt;
            dirList(listing).name(end-2:end);
            if any(strcmp(FileExt,dirList(listing).name(end-2:end)))
                FileList{end+1,1} = current_Path;
            end
        end
    end
end



%{
%%%
% Useful examples
%%%

% ALL DATA
FilePath = 'F:\';
FileList = {};
FileExt = {'tif','TIF'};
FileList = Dig(FilePath,FileList,FileExt);


% Root Data
FilePath = 'F:\';
FileList = {};
FileExt = {'tif','TIF'};
FileList = Dig(FilePath,FileList,FileExt);


% Growth data
FilePath = 'F:\Tessa Data\Growth Data\';
FileList = {};
FileExt = {'tif','TIF'};
FileList = Dig(FilePath,FileList,FileExt);


% nicks
FilePath = 'E:\Vlad\Nick\Impalement Data\';
FileList = {};
FileExt = {'xls'};
FileList = Dig(FilePath,FileList,FileExt);

% Candace
FilePath = 'C:\NDM\Data Set\candace\PBGs\';
FileList = {};
FileExt = {'tif','TIF'};
FileList = Dig(FilePath,FileList,FileExt);

% surface potential
FilePath = '\\Euclid\buslink g\Raw Data\Surface Potential\BLSP Data\';
FileList = {};
FileExt = {'xls'};
FileList = Dig(FilePath,FileList,FileExt);

filterList = {'sp05' 'oc05' 'nv05' 'dc05' 'jn06'};
filteredList = name_restrict(FileList,filterList);
reader1(filteredList)




%}

%{
OTHER

% find the first images
filter = {'\0.TIF' '\0.tif'};
B = zeros(size(FileList));
for f = 1:size(filter,2)
    idx = strfind(FileList,filter{f});
    for i = 1:size(idx,1)
        B(i) = B(i) | size(idx{i},2) > 0;
    end    
end
Bidx = find(B);

% find the cropped images
filter = {'BackUp'};
A = zeros(size(FileList));
for f = 1:size(filter,2)
    idx = strfind(FileList,filter{f});
    for i = 1:size(idx,1)
        A(i) = A(i) | size(idx{i},2) > 0;
    end    
end
Aidx = find(A);


% those of beginning type and cropped
BA = intersect(Bidx,Aidx);

% find the paths to the desired image sets
for i = 1:size(BA,1)
    idx = findstr(FileList{BA(i)},'BackUp');
    PathList{i} = FileList{BA(i)}(1:idx-1);
end

% desire to use this set
h = figure;
for i = 1:size(PathList,2)
    I = imread([PathList{i} 'BackUp\' '0.TIF']);
    figure(h)
    imshow(I);    
    figure(d);  
    A = questdlg('Use?');
    U(i) = strcmp(A,'Yes');
end


PathList(~U) = [];



% extract information
Q = [];
se = strel('disk',5);
N = 10;
for i = 1:size(PathList,2)
    I = imread([PathList{i} 'BackUp\' '0.TIF']);
    E = edge(I);
    E = imclose(E,se);
    L = bwlabel(E);
    P = regionprops(L,'Area','MajorAxisLength','MinorAxisLength');
    P = struct2cell(P);
    P = cell2mat(P)';
    P = sortrows(P);
    P = flipud(P);
    if size(P,1) < N
        P = [P;zeros((N - size(P,1)),size(P,2))];
    end
    P = P(1:N,:);
    P = reshape(P,[prod(size(P)) 1]);
    Q = [Q P];
end






























%}
