function gradients = compute_gradients(im,invert)

filt_size = 9;
s = 1.5;
gradients.gxx = [];
gradients.gxy = [];
gradients.gyx = [];
gradients.gyy = [];
gradients.gx  = [];
gradients.gy  = [];

if isempty(invert)
    invert = 0;
end

if invert
    mt_image = 1-im;
else
    mt_image = im;
end

mt_image = mat2gray(mt_image);

h = fspecial('gaussian',filt_size,s);
mt_image = mat2gray(my_filter2(mt_image,h));
[gradients.gx,gradients.gy]=gradient(mt_image);

[gradients.gxx,gradients.gxy,gradients.gyy] = my_gradient(mt_image);
gradients.gyx = gradients.gxy;