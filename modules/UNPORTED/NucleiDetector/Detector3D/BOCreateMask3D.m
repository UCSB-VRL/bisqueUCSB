function [imageInMask valuesInMask]= BOCreateMask3D(imageIn, x, y, z, maskSizeXY, maskSizeZ)    
    imageMask = logical(zeros(size(imageIn)));
    imageMask(x, y, z) = 1;
    seUp = strel('disk',maskSizeXY);
    seDown = strel('disk',maskSizeXY-2);
    
    z1=z-round(maskSizeZ/2);
    z2=z+round(maskSizeZ/2);    
    if z1<1
        z1=1;
    end
    if z2>size(imageIn,3)
        z2=size(imageIn,3);
    end
    %imageMask2D = logical(imsubtract(imdilate(imageMask(:,:,z),seUp), imdilate(imageMask(:,:,z),seDown)));
    imageMask2D = logical(imdilate(imageMask(:,:,z),seUp));
    for i=z1:z2
        imageMask(:,:,i) = imageMask2D;
    end
    imageInMask = immultiply(imageIn, imageMask);
    valuesInMask = imageInMask(imageMask==1);
    %plotborder(imageIn(:,:,z), imageMask2D);    
end