function [VEC] = spec_my_corner_TRACK(FileList,InitPoint,RAD,PHI,disp)
RADIUS = 30;
VEC = [];


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
                InitPoint(k,:) = size(I)/2;
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

%}