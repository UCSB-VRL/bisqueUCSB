function imd = imdiff(im1, im2)
% Normalized image difference
%
%

    %% normalize diff image
    std1 = std(single(im1(:)));
    std2 = std(single(im2(:)));    
    d_std = double(std1) / double(std2);
    im2 = im2 .* d_std;
    
    d_avg = mean(im1(:)) - mean(im2(:));
    im2 = im2 + d_avg;
       
    imd = im1 - im2;
end    
