      
function [out] = enhance3d ( img, ns )
   
    %% convolution based    
    out = gaussianFilter(img, ns./2);
    
    %out = uint16(double(img)-double(out));
    out = img-out;
end

function [G] = gaussianFilterS1D(s)
    %% Grid coordinates
    x = (-3*s:3*s)';
    G = (1/(sqrt(2*pi)*s)) * exp(-x.^2/(2*s^2));
end

function out = gaussianFilter(im, s)

    %% 3D LoG
    Gx = gaussianFilterS1D(s(1));
    Gy = gaussianFilterS1D(s(2));
    Gz = gaussianFilterS1D(s(3));
   
    try
        imgpu = gpuArray(im);
        imgpu = convs(imgpu, {Gx,Gy,Gz});
        out = gather(imgpu);
    catch err
        out = convs_fast(im, {Gx,Gy,Gz});
    end    
end

%% Separable Convolution
function im = convs(im, H)
    im = imfilter(im, H{1}, 'symmetric', 'same');

    im = shiftdim(im,1);
    im = imfilter(im, H{2}, 'symmetric', 'same');    
        
    im = shiftdim(im,1);
    im = imfilter(im, H{3}, 'symmetric', 'same');    

    im = shiftdim(im,1);    
end

function im = convs_fast(im, H)
    im = filter_fast(im, H{1});

    im = shiftdim(im,1);
    im = filter_fast(im, H{2});
        
    im = shiftdim(im,1);
    im = filter_fast(im, H{3});

    im = shiftdim(im,1);    
end

function im = filter_fast(im, kernel)
    try
        imgpu = gpuArray(im);
        imgpu = imfilter(imgpu, kernel, 'symmetric', 'same');
        im = gather(imgpu);
    catch err
        im = imfilter(im, kernel, 'symmetric', 'same'); 
    end
end
