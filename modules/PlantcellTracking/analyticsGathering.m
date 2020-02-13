function[threshMetrics]= analyticsGathering(input)
% HIT F5 to run this file

%% Read and Normalize the image
% extension = '.tif';
% STEP 1: 
% Mention the sequence of images to find their respective threshold values, e.g.
% imageInd = [1 6]: will find automatic threshold for images 1 through 6.
% Make sure these images are in the current directory
% imageInd = [1];
% numImages = imageInd(2)-imageInd(2)+1;
% readIm = strcat(num2str(imageInd(1)),extension);
%temp=imread(readIm);
temp=input;
temp=temp(:,:,1);
im = normalize(temp);
% STEP 2: 
% Change the range in which you want to find the threshold. 0.2 to 0.8 is
% decided by research and analysis.
threshRange = [0.02 0.08];
sizeIm = size(im);
Masks = zeros(sizeIm(1),sizeIm(2),1);
threshMetrics=zeros(1,13,4);  
% for k=imageInd(1):imageInd(2)
%     dir = 'C:\ucr\cell tracking\P3\Watershed & Tracking\';
%     filename = strcat(dir, num2str(k), extension);
%     temp=imread(filename);
temp=temp(:,:,1);
    tempIm = normalize(temp);
    gBlurIm = imfilter(tempIm,fspecial('gaussian',[10 10],15));
    count=1;
    for threshold = threshRange(1):0.005:threshRange(2)
        MASK1 = watershed(imhmin(gBlurIm,threshold));
        MASK1 = MASK1==0;
        MASK1 = bwareaopen(MASK1,100);
        MASK1 = double(MASK1);
        [B L] = bwboundaries(MASK1, 'holes');       
        [centroid area cellPixelArray] = findCellInfo(B,L);
        centroid=centroid;
        threshMetrics(1,count,:)=[threshold length(area), mean(area), std(area)];
        count=count+1;
    end
% end

%save('threshStudyMetrics', 'threshMetrics');
