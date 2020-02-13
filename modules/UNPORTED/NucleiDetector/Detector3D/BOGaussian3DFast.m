function imageOut = BOGaussian3DFast(img,s_x,s_y,s_z,std)
%% BOGaussian3DFast - convolving image with 3D Log
% 
% Boguslaw Obara, http://boguslawobara.net/
%
% Version:
%   0.1 - 16/02/2008 First implementation
%%
imageOut = [];
    try
        %siz = [s_x s_y s_z];
        % construct the kernel;
        %[x,y,z] = meshgrid(-(siz(2)-1)/2:(siz(2)-1)/2,-(siz(1)-1)/2:(siz(1)-1)/2,-(siz(3)-1)/2:(siz(3)-1)/2);
        %ker = exp(-(x.*x + y.*y + z.*z)/(2*std*std));
        %ker = ker/sum(sum(sum(ker)));
        
        % display the kernel
        %for i=1:s_z
        %    imagesc(ker(:,:,i));
        %    waitforbuttonpress
        %end
%         ker1 = gausskernel(s_x/2-1,std);        
%         ker2 = gausskernel(s_y/2-1,std);        
%         ker3 = gausskernel(s_z/2-1,std);
        
%         s_x=getKernelSize(s_x);
%         s_y=getKernelSize(s_y);
%         s_z=getKernelSize(s_z);
        ker1 = logkernel(s_x,std);        
        ker2 = logkernel(s_y,std);        
        ker3 = logkernel(s_z,std);
        %tic; orig = convn(img,ker,'same'); toc
        imageOut = convnsep(ker1,ker2,ker3,img,'same');
        %filimg = convn(img,ker,'same');
    catch
        lasterror
        return;
    end
%--------------------------------------------------------------------------

end
