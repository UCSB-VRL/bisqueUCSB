function [X] = my_corner(I,disp);
D = diffmethod(I,1);
D = structureTensor(D,fspecial('average',[9 9]));
D = cornerstrength(D,fspecial('gaussian',[5 5],2));
[r,c] = nonmaxsuppts(D(:,:,6), 6, 10);
if disp
    imshow(I,[]);
    hold on
    scatter(c,r)
end

%{
I = double(imread('Y:\takeshi\Maize\IBM lines\Gravitropism\IBM5s4\400000.tif'));
X = my_corner(I,0);
%}