function [IMG] = measure(FileName,threshold)
    disp=0;
    % declare data structure
    IMG.SeedSheet = [];
    IMG.threshold = [];
    IMG.SeedCount = [];
    IMG.Percent_Clusters = [];
    
    %%%%%%%%%%%%%%%%%%%%%%%%%%% line(s) used for sub image    
    %info = imfinfo(FileName);    
    %I = imread(FileName,'PixelRegion',{[1 round(info.Height/2)] , [1 round(info.Width/2)]});    
    %%%%%%%%%%%%%%%%%%%%%%%%%%% line(s) used for sub image    
    % read the image
    tic
    I = imread(FileName);    
    toc
    %if isrgb(I)
    if size(I,3)==3,
        I = rgb2gray(I);
    end
    % get the threshold
    if size(threshold,1) == 0
        threshold = graythresh(I);
    end    
    BW = I < 255*threshold;
    BW = bwareaopen(BW,500);
    % label and measure    
    tic
    CC = bwconncomp(BW,8);
    %L = labelmatrix(CC);
    R = regionprops(CC,'Area','MinorAxisLength','MajorAxisLength','Centroid','Orientation');
    toc
    % perform the histogram
    bins = linspace(0,20000,200);
    v = hist([R.Area],bins);
    [JUNK xpos] = max(v);
    SSS = bins(xpos);           % single seed size
    SPC = round([R.Area]/SSS);  % seeds per cluster    
    NUM_SEEDS = sum(SPC);       % number of seeds
    sidx = find(SPC==1);
    centtmp = [R(sidx).Centroid];
    tmpidx1 = 1:2:numel(centtmp);
    centtmp1 = centtmp(tmpidx1);
    tmpidx2 = 2:2:numel(centtmp);
    centtmp2 = centtmp(tmpidx2);
    M = [[R(sidx).Area]' [R(sidx).MinorAxisLength]' [R(sidx).MajorAxisLength]' centtmp1' centtmp2' [R(sidx).Orientation]'];
    miX = ( cosd(M(:,6)-90) * .5 .* M(:,2)) + M(:,4);
    miY = (sind(M(:,6)-90) * .5 .* M(:,2)) + M(:,5);
    maX = (cosd(M(:,6)) * .5 .* M(:,3)) + M(:,4);
    maY = (sind(M(:,6)) * .5 .* M(:,3)) + M(:,5);
    M = [M, miX, miY, maX, maY];
    % compute percent
    U = unique(SPC);    
    for i = 1:size(U,2)
        TYPE(i) = sum(SPC == U(i));
    end   
    % fill out object
    IMG.SeedSheet = M;
    IMG.threshold = threshold;
    IMG.SeedCount = NUM_SEEDS;
    IMG.Percent_Clusters = TYPE.*U * NUM_SEEDS^-1;      
    if length(IMG.Percent_Clusters) < 2
       IMG.Percent_Clusters=[IMG.Percent_Clusters,  IMG.Percent_Clusters];
    end
    % filter
    RATIO = (IMG.SeedSheet(:,2).*IMG.SeedSheet(:,3)*pi/4.*IMG.SeedSheet(:,1).^-1);
    A = find(RATIO < 1.1 & (IMG.SeedSheet(:,3).*IMG.SeedSheet(:,2).^-1 < 2.5));
    IMG.SeedSheet = IMG.SeedSheet(A,:);
    IMG.SeedCount = size(IMG.SeedSheet,1);
    % display
    if disp
        imshow(I,[])
        hold on
        for i = 1:size(A,1)
            scatter(R(sidx(A(i))).Centroid(:,1),R(sidx(A(i))).Centroid(:,2),'o')        
        end    
        drawnow
        hold off
    end
end
