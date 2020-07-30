function feat_hist = vrl_feathist(roi_pixels, no_bins)

    bin_width = 256 / no_bins;
    h            = double(ceil( roi_pixels / bin_width ));
    h(h==0)      = 1; 
    feat_hist    = zeros(no_bins, no_bins, no_bins);
    for row_iter = 1:size(h,1)
        feat_hist(h(row_iter,1),h(row_iter,2),h(row_iter,3)) = feat_hist(h(row_iter,1),h(row_iter,2),h(row_iter,3)) + 1;
    end
    feat_hist = feat_hist ./ sum( feat_hist(:) );