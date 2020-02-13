function gray_hist = vrl_grayhist(I, I_roi, no_bins)

%% Creation of a Color Histogram for the Input Color Image
% Usage
% gray_hist = vrl_grayhist(I, I_roi, no_bins)
% Input
% I - The input image ... must necessarily be a three channel image
% I_roi - The region of interest or the pixel set in the foreground
% no_bins - The number of bins to be used in the histogram

% gray_hist - A [no_bins no_bins no_bins] matrix containing the histogram

I = double(I);
    [no_rows no_cols no_slices] = size(I);
    if(no_slices ~= 1)
        error('Input is not a GrayScale');
    end
roi_pixels = I(I_roi);
    
gray_hist = hist(roi_pixels(:), no_bins);
gray_hist = gray_hist ./ sum(gray_hist(:));