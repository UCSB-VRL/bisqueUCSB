function[phi] = getPhi(BG,MASK)
    
    [B,I] = bwboundaries(MASK,'holes');
    phi = zeros(size(BG));
    for k = 2:length(B)
        boundary = B{k};
        phi=getImageFromCell(phi,fliplr(boundary));
    end
end