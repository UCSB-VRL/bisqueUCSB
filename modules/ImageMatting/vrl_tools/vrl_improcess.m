function op = vrl_improcess(I, varargin)

%% Function to Perform Gaussian Smoothing Gradient of an Image
% uses the imfilter command from matlab
% Input Arguments: 
% I - The image for which gradient is to be computed
%   varargin{1}(1) - Number of iterations ()
%   varargin{1}(2) - Conduction Coefficient (20-100)
%   varargin{1}(3) - lambda max value of .25 for stability
% Output Arguments:
% I_x - X component of gradient
% I_y - Y component of gradient
% E   - Resulting Canny Edge Map with default thresholds 


op.I = double(I);

[op.Ix op.Iy op.grad_mag op.edge_indicator op.edge_canny] = vrl_imgrad(op.I);

if(nargin>1)
    try
    op.diffuse = kovesi_anisodiff(op.I, varargin{1}(1), varargin{1}(2), varargin{1}(3), 1);
    catch me
        display('Error in Diffusion Parameters ... not computing diffusion');
    end
else
    op.diffuse = kovesi_anisodiff(op.I, 10, 20, .25, 1);
end