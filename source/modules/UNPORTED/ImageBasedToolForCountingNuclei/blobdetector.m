function [image_resource ErrorCode ErrorMsg] = blobdetector(url, ImageID);
%function [image_resource ErrorCode ErrorMsg] = blobdetector(url, ImageID, side, min_dist,option,th);


%
% Input
%-------------------------------------------------------------
% im = image to count cells
% side: filter size - choose the diameter (or slightly larger) of the blob (in pixels)
% min_dist : minimum distance between peaks
% option : 1 if the peak to detect is dark
%          0 if the peak to detect is bright (e.g. Topro stained image)
% map : mask of layer
% th : threshold for filter output
      %- suggested to choose -0.05 or 0

% Output
%-------------------------------------------------------------
% p: returns the number of peaks (cells) detected.
% image_resource: resultImaage 
% Result(filter size,min_dist)_p_totalarea

% Works only with gray-scale images. If RGB image is input, the image will
% be converted to gray image

%

% Protocol to talk to bisquik
init();
ErrorCode = 0;
ErrorMsg = '';
image_resource = '';

try
    [im_data ErrorCode ErrorMsg] = getImageData(url, ImageID);
    im = readImage(url, im_data, 'tiff');
    [im_tags ErrorCode ErrorMsg] = getImageTags(url, im_data);
    [im_reference Types ErrorCode ErrorMsg] = findTagValue(im_tags, 'labelImg');
    [gt_data ErrorCode ErrorMsg] = getImageData(url, im_reference);
    gt = readImage(url, gt_data, 'bmp');
    [mag_xy Types ErrorCode ErrorMsg] = findTagValue(im_tags, 'mag_xy');
catch
    return;
end


% initialization
cellSize =6;
map =zeros(size(im,1),size(im,2));
% ONL == 7 in gt
map(find(gt==7))= 1;
option =0; % should be changed according to metadata
th =0;
mag =str2num(mag_xy);
area_onl = calculateArea(gt, 7, mag);
filterSize= round(cellSize/mag);
minDist = round(filterSize*0.5);


if size(im,3) ==1
    img = im;
else
    img = rgb2gray(im);
end

if option==0
    img = 255-img;
end

% apply the filter
ac = lapofgau(img,filterSize);
ac(find(ac<th))=th;
ac = ac-th;

scaling = 1;
ac2=ac;
figure; imagesc(ac); axis image; axis off

% find local maxima from filter output
[i,j,val] = find_local_max_2D(ac2,[],floor(filterSize/4/scaling),inf,minDist,[],[1 1],map);

area = length(find(map==255 |map==1 ));

p =0;
ind=[];
tmp = [i' j' ];
if size(im,3) ==1 % gray
    result(:,:,1) = im;
    result(:,:,2) = im;
    result(:,:,3) = im;
else
    result = im;
end

for k =1: length(i)
    p = p+1;
    ind = [ind ; tmp(k,:)];
    result(tmp(k,1), tmp(k,2),1)= 255;
    result(tmp(k,1), tmp(k,2),2)= 255;
    result(tmp(k,1), tmp(k,2),3)= 0;
end

cellDensity= (p/area_onl)*1e6;
figure;
imagesc(im);axis image; colormap gray; axis off
hold on; plot(scaling*ind(:,2), scaling*ind(:,1), '.r');
title([num2str(p),' blobs (area:',num2str(area),')']);

image_post = postImage(url, '/bisquik/upload_handler_mex', result, 'tiff');
image_resource = findImageAttribute(image_post, 'uri');
resultTags= addTag('cellDetectionResult', image_resource);
postTag(url, ImageID, resultTags);

% nucleiInfoTags = addTag('cellNumber', num2str(p));
% nucleiInfoTags= addTag('cellDensity', num2str(cellDensity),nucleiInfoTags);
%postTag(url, ImageID, nucleiInfoTags);
cellNumberTags = addTag('cellNumber', num2str(p));
postTag(url, ImageID, cellNumberTags);
cellDensityTags= addTag('cellDensity', num2str(cellDensity));
postTag(url, ImageID, cellDensityTags);


%imwrite(result,[resultPath,'Result(',num2str(side),',',num2str(min_dist),')_',num2str(p),'_',num2str(area),'.tif'],'tif');

