function fg_proj = vrl_msPatchHistbp(I1, fg_hist)
          
%% Multi Scale Patch Histograms

% Filter image with gaussians having different standard deviations
FR1 = imfilter( I1, fspecial('gauss', [49 49], 3), 'same', 'conv'); 
FR2 = imfilter( I1, fspecial('gauss', [49 49], 7), 'same', 'conv');
FR3 = imfilter( I1, fspecial('gauss', [49 49], 11), 'same', 'conv');
FV = [FR1(:) FR2(:) FR3(:)];

% BackProject Feature Histograms
fg_proj =  vrl_feathistbp(FV, fg_hist) ;

fg_proj = reshape( fg_proj, size(I1) );