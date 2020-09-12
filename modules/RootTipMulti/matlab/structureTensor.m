function [D] = structureTensor(D,F)
D1 = imfilter(D(:,:,1).^2,F);
D2 = imfilter(D(:,:,2).^2,F);
D3 = imfilter(D(:,:,1).*D(:,:,2),F);
D = cat(3,D,D1,D2,D3);