function [Ix Iy grad_mag edge_indicator edge_canny] = vrl_imgrad(I)

%% Function to Perform Gaussian Smoothing Gradient of an Image
% uses the imfilter command from matlab
% Input Arguments: 
% I - The image for which gradient is to be computed

% Output Arguments:
% I_x - X component of gradient
% I_y - Y component of gradient
% grad_mag - magnitude of the gradient
% edge_indicator - Edge Indicator for a GAC like function
% edge_canny   - Resulting Canny Edge Map with default thresholds 


I = double(I);

% Smoothing the Image
I_smooth = vrl_imsmooth(I, 3, 2);

% Computing Image Gradients
[Ix Iy] = gradient(I_smooth);

% Gradient Magnitude
grad_mag = sqrt(Ix.^2 + Iy.^2);

% Computation of the Edge Indicator
edge_indicator = 1 ./ (1+grad_mag.^2);

% Canny Detector
edge_canny = edge(I_smooth,'canny');