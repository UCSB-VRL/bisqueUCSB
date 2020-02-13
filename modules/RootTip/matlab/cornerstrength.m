function [D] = cornerstrength(D,F)
D = cat(3,D,(D(:,:,3).*D(:,:,4) - D(:,:,5).^2).*(D(:,:,3) + D(:,:,4) + eps).^-1);
%D(:,:,6) = imfilter(D(:,:,6),F);
