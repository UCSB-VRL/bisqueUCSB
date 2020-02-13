function [VEC] = maizeG(FileList)
RADIUS = 30;
VEC = [];
%InitPoint = csvread(InitPoint);
[csvfilelist] = Ldig(FileList,{},{'csv','CSV'},1);
csvfilelist = csvfilelist{1};
InitPoint = csvread(csvfilelist);
RAD = 30;
PHI = 100;
disp = 0;

[FileList] = Ldig(FileList,{},{'TIF','tif'},1)';
qVEC = [];
tips = [];
% for each file read and track corners
for i = 1:size(FileList,2)
  FileName = FileList{i};
    I = imread(FileName);
    if size(I,3) > 1
        I = rgb2gray(I);        
    end
    I = double(I);
    tVEC = [];
    % for each init point
    for k = 1:size(InitPoint,1)
        % filter for InitPoint
        if InitPoint(k,1)-RADIUS < 1 | ...
           InitPoint(k,1)+RADIUS > size(I,1) | ...
           InitPoint(k,2)-RADIUS < 1 | ...
           InitPoint(k,2)+RADIUS > size(I,2)
                InitPoint(k,:) = size(I)./2;
        end
        SAM = I(InitPoint(k,1)-RADIUS:InitPoint(k,1)+RADIUS,...
                InitPoint(k,2)-RADIUS:InitPoint(k,2)+RADIUS);       
        [X] = my_corner(SAM,0,0,1,RAD,PHI);
        dist = [];
        % for each corner found within the image
        for j = 1:size(X,1)
            dist(j) = norm(X(j,1:2) - RADIUS);
        end
        % find the nearest corner
        [JUNK fidx] = min(dist);
        tVEC = [tVEC ; X(fidx,:)];
        A(k) = X(fidx,3);
        tVEC(k,1:2) = (tVEC(k,1:2)) + InitPoint(k,:) - RADIUS - 1;
        % reinit the point set list
        InitPoint(k,:) = tVEC(k,1:2);
        QVEC(k,:) = tVEC(k,4:5);
        
    end
    VEC = [VEC , tVEC];
    qVEC = [qVEC;A];
    fprintf(['Done with ' num2str(i) ' of ' num2str(size(FileList,2)) '.\n'])
    tt = fliplr(InitPoint(:,1:2));
    tt2 = [];
    for iii = 1:size(tt,1)
        tt2 = [tt2,tt(iii,:)];

    end
    tips = [tips; tt2];
    if disp
        imshow(I,[])
        hold on
        scatter(InitPoint(:,2),InitPoint(:,1),'r*')
        scatter(X(:,1),X(:,2),'b.')
        quiver(InitPoint(:,2),InitPoint(:,1),QVEC(:,1),QVEC(:,2),1,'r')
        hold off
        drawnow
    end    
end
VEC = qVEC;
csvwrite('./angles.csv',VEC)
tips = round(tips);
csvwrite('./tips.csv',tips)


%{
I = imread('Y:\for logans visit\data\maize root gravitropism\IBM231s2\200000.tif');
[r c V] = impixel(I);
csvwrite('Y:\for logans visit\code\maize root gravitropism\takeshi pipeline\InitPoints.csv',[c r]);
[VEC] = maizeG('Y:\for logans visit\data\maize root gravitropism\IBM231s2\','Y:\for logans visit\code\maize root gravitropism\takeshi pipeline\InitPoints.csv',30,100,0);

%}
