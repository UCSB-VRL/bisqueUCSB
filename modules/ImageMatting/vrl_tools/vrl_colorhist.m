function color_hist = vrl_colorhist(I, I_roi, no_bins, roi_pixels)


%% Creation of a Color Histogram for the Input Color Image
% Usage
% color_hist = vrl_colorhist(I, I_roi, no_bins)
% Input
% I - The input image ... must necessarily be a three channel image
% I_roi - The region of interest or the pixel set in the foreground
% no_bins - The number of bins to be used in the histogram

% color_hist - A [no_bins no_bins no_bins] matrix containing the histogram

    I = double(I);
    [no_rows no_cols no_slices] = size(I);
    if(no_slices ~= 3)
        error('Input is not a color Image');
    end
    R = I(:, :, 1); G = I(:, :, 2); B = I(:, :, 3);

    bin_width = 256 / no_bins; %% ss is the bin width while no_bins is the number of bins
    if( nargin ~= 4)
        roi_pixels = [R(I_roi), G(I_roi), B(I_roi)]; 
    end
    
    h            = double(ceil( roi_pixels / bin_width ));
    h(h==0)      = 1; 
    color_hist    = zeros(no_bins, no_bins, no_bins);
    for row_iter = 1:size(h,1)
        color_hist(h(row_iter,1),h(row_iter,2),h(row_iter,3)) = color_hist(h(row_iter,1),h(row_iter,2),h(row_iter,3)) + 1;
    end
    color_hist = color_hist ./ sum( color_hist(:) );