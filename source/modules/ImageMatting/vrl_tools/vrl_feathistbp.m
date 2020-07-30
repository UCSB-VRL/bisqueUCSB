function feat_project = vrl_feathistbp(test_vectors, feat_hist)

no_bins = nthroot(numel(feat_hist),3);
bin_width = 256/no_bins;
h = double(ceil( test_vectors / bin_width ));  
h(h==0) = 1;

feat_project = feat_hist(sub2ind(size(feat_hist), h(:, 1), h(:, 2), h(:, 3)));