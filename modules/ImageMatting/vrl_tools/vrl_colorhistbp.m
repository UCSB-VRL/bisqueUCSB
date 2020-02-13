function roi_project = vrl_colorhistbp(test_img, roi_hist)

%% Function to Compute a Histogram BackProjection
% Usage
% roi_project = vrl_colorhistbp(test_img, roi_hist)
% Input
% test_img - Necessarily a Color Input Image
% roi_hist - The histogram characterizing the region of interest learnt offline

% Output
% roi_project - BackProjection of Histogram onto the test image

test_img = double(test_img);
[no_rows no_cols no_slices] = size(test_img);
if(no_slices ~= 3)
    error('Image is not Color');
end
    
test_vectors = reshape(test_img, no_rows*no_cols, 3); 
no_bins = nthroot(numel(roi_hist),3);
bin_width = 256/no_bins;
h = double(ceil( test_vectors / bin_width ));  
h(h==0) = 1;

roi_proj = roi_hist(sub2ind(size(roi_hist), h(:, 1), h(:, 2), h(:, 3)));
roi_project = reshape(roi_proj, no_rows, no_cols);