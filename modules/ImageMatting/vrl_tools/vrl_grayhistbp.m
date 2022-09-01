function roi_project = vrl_grayhistbp(test_img, roi_hist)

%% Function to Compute a Histogram BackProjection
% Usage
% roi_project = vrl_grayhistbp(test_img, roi_hist)
% Input
% test_img - Necessarily a GrayScale Input Image
% roi_hist - The histogram characterizing the region of interest learnt offline

% Output
% roi_project - BackProjection of Histogram onto the test image

test_img = double(test_img);
[no_rows no_cols no_slices] = size(test_img);
if(no_slices ~= 1)
    error('Image is not GrayScale');
end
    
test_vectors = test_img(:); 
no_bins = numel(roi_hist);
bin_width = 256/no_bins;
h = double(ceil( test_vectors / bin_width ));  
h(h==0) = 1;

roi_proj = roi_hist(h);
roi_project = reshape(roi_proj, no_rows, no_cols);

roi_project = roi_project ./ max(roi_project(:));