function filimg = BOGaussian3D(img,s_x,s_y,s_z,std)
%--------------------------------------------------------------------------
%   
%
%   Boguslaw Obara <obara@ece.ucsb.edu>
%--------------------------------------------------------------------------
    try
        siz = [s_x s_y s_z];
        % construct the kernel;
        [x,y,z] = meshgrid(-(siz(2)-1)/2:(siz(2)-1)/2,-(siz(1)-1)/2:(siz(1)-1)/2,-(siz(3)-1)/2:(siz(3)-1)/2);
        ker = exp(-(x.*x + y.*y + z.*z)/(2*std*std));
        ker = ker/sum(sum(sum(ker)));
        % display the kernel
        %for i=1:s_z
        %    imagesc(ker(:,:,i));
        %    waitforbuttonpress
        %end
        filimg = convn(img,ker,'same');
    catch
        lasterror
        return;
    end
%--------------------------------------------------------------------------
end
