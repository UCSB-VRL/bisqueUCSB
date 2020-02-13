function [VEC] = my_corner_TRACK(FileList,InitPoint,RAD,PHI,disp)
RADIUS = 30;
VEC = [];


% for each file read and track corners
for i = 1:size(FileList,2)
    
    FileName = FileList{i};
    fprintf(['Working with ' strrep(FileName,'\','\\') '\n'])
    I = double(imread(FileName));
    tVEC = [];
    % for each init point
    for k = 1:size(InitPoint,1)
        % filter for InitPoint
        if InitPoint(k,1)-RADIUS < 1 | ...
           InitPoint(k,1)+RADIUS > size(I,1) | ...
           InitPoint(k,2)-RADIUS < 1 | ...
           InitPoint(k,2)+RADIUS > size(I,2)
                InitPoint(k,:) = size(I)/2;
        end
        SAM = I(round(InitPoint(k,1)-RADIUS:InitPoint(k,1)+RADIUS),...
                round(InitPoint(k,2)-RADIUS:InitPoint(k,2)+RADIUS));       
        [X] = my_corner(SAM,0,0,1,RAD,PHI);
        dist = [];
        % for each corner found within the image
        for j = 1:size(X,1)
            dist(j) = norm(X(j,1:2) - RADIUS);
        end
        % find the nearest corner
        [JUNK fidx] = min(dist);
        tVEC = [tVEC ; X(fidx,:)];
        tVEC(k,1:2) = (tVEC(k,1:2)) + InitPoint(k,:) - RADIUS - 1;
        % reinit the point set list
        InitPoint(k,:) = tVEC(k,1:2);
        QVEC(k,:) = tVEC(k,4:5);
    end
    VEC = [VEC , tVEC];
    fprintf(['Done with ' num2str(i) ' of ' num2str(size(FileList,2)) '.\n'])
    if disp
        imshow(I,[])
        hold on
        scatter(InitPoint(:,2),InitPoint(:,1),'r*')
        quiver(InitPoint(:,2),InitPoint(:,1),QVEC(:,1),QVEC(:,2),1,'r')
        hold off
        drawnow
    end
    
end


%{
I = imread('Y:\takeshi\Maize\IBM lines\Gravitropism\IBM5s4\400000.tif');
[r c V] = impixel(I);
[VEC] = my_corner_TRACK('Y:\takeshi\Maize\IBM lines\Gravitropism\IBM5s4\',[c r],30,100,0);





%{
% short cut to the pipline here
rootPath{1} = 'Y:\takeshi\Maize\IBM (spectrum)\';
[FileSequences1] = findFileSequences(rootPath{1});
rootPath{2} = 'Y:\takeshi\Maize\IBM lines\Gravitropism\';
[FileSequences2] = findFileSequences(rootPath{2});
rootPath{3} = 'Y:\takeshi\Maize\IBM lines\Gravitropism (Second run)\';
[FileSequences3] = findFileSequences(rootPath{3});
FS = [FileSequences1';FileSequences2';FileSequences3'];

[T D]  = xlsread('N:\Measure Code\takeshi pipeline\root tips\data.csv');
D(1,:) = [];
for i = 1:size(D,1)
    if strcmp(D{i,1}(end),'a')
        S{i} = 2;
        D{i,1} = D{i,1}(1:end-1);
    elseif strcmp(D{i,1}(end),'b')
        S{i} = 3;
        D{i,1} = D{i,1}(1:end-1);
    else
        S{i} = 0;
    end
    D{i,1} = ['\' D{i,1} '\'];
end

warning off
M = [];
matlabpool 4
for i = 1:size(D,1)    
    fidx = strfind(FS,D{i,1});
    for j = 1:size(fidx,1)
        sidx(j) = size(fidx{j},1) ~= 0;
    end
    sidx = find(sidx);
    if S{i} ~= 0
        RP = rootPath{S{i}};
    else
        RP = FS{sidx}(1:fidx{sidx}-1);
    end
    FPi = [RP D{i,1}];
    [FileList] = getFileList(FPi,'.TIF');
    [VEC] = my_corner_TRACK(FileList,fliplr(T(i,:)).*[1040 1392],30,100,0);
    M{i} = VEC';
    fprintf(['Done with ' num2str(i) ' of ' num2str(size(D,1)) '\n'])
end
matlabpool close

basepath = 'N:\Measure Code\takeshi pipeline\MC';
for i = 1:size(D,1)
    filename = [basepath D{i,1}(1:end-1) '_' num2str(i) '.txt'];
    dlmwrite(filename,M{i})
    fprintf(['Done with ' num2str(i) ' of ' num2str(size(D,1)) '\n'])
end

%}
%}