function gradients = gradient_computation_module(im,inv);
filt_size = 9;
s = 1.5;
gradients.gxx = [];
gradients.gxy = [];
gradients.gyx = [];
gradients.gyy = [];
gradients.gx  = [];
gradients.gy  = [];
if inv == 1
    im = 1-im;
end
mt_image = mat2gray(im);
h = fspecial('gaussian',filt_size,s);
mt_image = mat2gray(my_filter2(mt_image,h));
[gradients.gx,gradients.gy]=gradient(mt_image);
[gradients.gxx,gradients.gxy,gradients.gyy] = my_gradient(mt_image);
gradients.gyx = gradients.gxy;