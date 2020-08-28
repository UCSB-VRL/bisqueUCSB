function[phi]=ImProc(t,input)


%% Read and Normalize the image
extension = '.tif';
imNum=1;
imageToRead = strcat(num2str(imNum),'.tif');
%im = double(imread(imageToRead));
im = double(input);
imageInd = [1 1];
% deltaThresh = 
%thresholdVec =[0.0650    0.0725    0.0500    0.0650];
thresholdVec=t;
sizeIm = size(im);
Masks = zeros(sizeIm(1),sizeIm(2),1); 
clear BGImages;
for k=imageInd(1):imageInd(2)
    %filename = strcat(num2str(k), extension);
    temp=input;
temp=temp(:,:,1);
    tempIm = normalize(temp);
    BGImages(:,:,k) = tempIm;
    gBlurIm = imfilter(tempIm,fspecial('gaussian',[10 10],15));
    III=imhmin(gBlurIm,thresholdVec);
    [B cellStructureTemp MASK1] = subSegmentation(III);
    numCells(k) = length(B);
    Masks(:,:,k) = MASK1;
    cellStructure(k) = cellStructureTemp;
%     ShowOverlayMask(tempIm,MASK1, k);
    phi(:,:,k) = getPhi(tempIm,MASK1);  
%     k
end
% save 'BGImages.mat' BGImages;
% save 'numCells.mat' numCells;
% save 'Masks.mat' Masks;
% save 'cellStructure.mat' cellStructure;
% save 'phi.mat' phi;
