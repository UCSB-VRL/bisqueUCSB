function[B cellStructureTemp MASK1] = subSegmentation(im,k)
    MASK1 = watershed(im);       
    MASK1 = MASK1==0;
    MASK1=bwareaopen(MASK1,100);
    MASK1 = double(MASK1);
%     figure, imshow(MASK1);
    [B L] = bwboundaries(MASK1, 'holes');
    
%     numCells(k) = length(B);
%     Masks(:,:,k) = MASK1;
    [centroid area cellPixelArray] = findCellInfo(B,L);
    cellStructureTemp = struct('centroid', {centroid}, 'area', {area}, 'cellBoundaries',{cellPixelArray}, 'label', {L});
end