function out = vrl_interp2_wrapper(im, xx, yy)
xx(xx < 1) = 1;
yy(yy < 1) = 1;
xx(xx > size(im, 2)) = size(im, 2);
yy(yy > size(im, 1)) = size(im, 1);
out = interp2(im, xx, yy, 'linear', 0);