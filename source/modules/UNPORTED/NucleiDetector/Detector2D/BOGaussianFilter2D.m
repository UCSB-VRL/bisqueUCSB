function imageOut = BOGaussianFilter2D(img,s_x,s_y,std)
%% BOGaussianFilter2D - convolving image with 3D Log
% 
%   Boguslaw Obara, http://boguslawobara.net/
%
%   Version:
%       0.1 - 14/11/2008 First implementation
%%
ker1 = logkernel(s_x,std);        
ker2 = logkernel(s_y,std);        
imageOut = convnsep(ker1,ker2,img,'same');
end