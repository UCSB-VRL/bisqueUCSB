function [princMag princDir] = vrl_shapeMoments(I)

if( size(I,3) == 1)
    [y x] = find(I);
    y =  y - mean(y);
    x =  x - mean(x);
    covMat = cov(x, y);
    [u s v] = svd(covMat);
    princDir = u;
    princMag = diag( s );
end