function I_smooth = vrl_imsmooth(I, filt_size, filt_var)

%% Function to Perform Gaussian Smoothing of an image 
% uses the imfilter command from matlab
% Input Arguments: 
% I - The image to be used 
% filt_size - Filter Size to be used
% filt_var  - Filter Variance to be used

% Output Arguments:
% I_smooth - Smoothed Output Image

I = double(I);
S = fspecial('gauss', [filt_size filt_size], filt_var);
I_smooth = imfilter(I, S);
return;