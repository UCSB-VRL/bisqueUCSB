%% BOBlobDetector3D - enhances 3D blob-like structures
%
%   INPUT:
%       im      - image
%       s       - sigma = [sigmax sigmay sigmaz]
%
%   OUTPUT:
%       imlog   - enhanced output image
%
%   AUTHOR:
%       Boguslaw Obara, http://boguslawobara.net/
%       Dmitry Fedorov, www.dimin.net
%
%   REFERENCE:
%       A. Huertas and G. Medioni, 
%       Detection of intensity changes with subpixel accuracy using 
%       Laplacian-Gaussian masks,
%       IEEE Transactions on Pattern Analysis and Machine Intelligence, 
%       8, 5, 651-664, 1986.
%
%       D. Sage and F.R. Neumann and F. Hediger and S.M. Gasser and M. Unser 
%       Automatic tracking of individual fluorescence particles: 
%       application to the study of chromosome dynamics,
%       IEEE Transactions on Image Processing, 14, 9, 1372-1383, 2005, 
%
%   VERSION:
%       0.1 - 03/06/2010 First implementation
%       0.2 - code cleanup
%       0.3 - Dmitry: support for non double typed images
%       0.4A - Dmitry: speed-up by 17 times shifting dims before convolution 
%             matlab does not actually parallelize convolutions in 3-d
%             dimension which leads to a very slow processing
%       0.4B - Dmitry: speed-up by 4 times with GPU
%             overall improvement of 62 times!
%%

function imlog = BOBlobDetector3D(im,s)

    %% 3D LoG
    [LoGx,Gx] = BOLoGFilterS1D(s(1));
    [LoGy,Gy] = BOLoGFilterS1D(s(2));
    [LoGz,Gz] = BOLoGFilterS1D(s(3));

    %% convolution
    imlog = log_fast(im, LoGx, LoGy, LoGz, Gx, Gy, Gz);

    %% Use only hills, valleys are removed
    imlog(imlog<0) = 0;
    
    %% Normalize
    maxval = 1;
    if isinteger(imlog),
       maxval = intmax(class(imlog));
    end    
    imlog = (imlog-min(imlog(:))) * (maxval / (max(imlog(:))-min(imlog(:))) );    
end

%% Separable Convolution
function im = log_fast(im, LoGx, LoGy, LoGz, Gx, Gy, Gz)
    try
        imgpu = gpuArray(im);
        imgpu = convs(imgpu, {LoGx,Gy,Gz}) + ... 
                convs(imgpu, {Gx,LoGy,Gz}) + ...
                convs(imgpu, {Gx,Gy,LoGz});
        im = gather(imgpu);
    catch err
        im = convs_fast(im, {LoGx,Gy,Gz}) + ... 
             convs_fast(im, {Gx,LoGy,Gz}) + ...
             convs_fast(im, {Gx,Gy,LoGz});
    end
end

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

%% original and depricated method
% function im = convsB(im, H)
%     N = length(H);
%     for k = 1:N,
%         orient = ones(1,ndims(im));   
%         orient(k) = numel(H{k});
%         kernel = reshape(H{k}, orient);
%         im = imfilter(im, kernel, 'symmetric', 'same');
%     end
% end
