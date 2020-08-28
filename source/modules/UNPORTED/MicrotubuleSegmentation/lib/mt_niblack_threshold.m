function level=mt_niblack_threshold(in_im,filter_s,weight)
%--------------------------------------------------------------------------
%   mt_niblack_threshold - launch Niblack's threshold algorithm
%
%       level=mt_niblack_threshold(in_im,filter_s,weight)
%
%       'in_im'     - input image
%       'filter_s'  - input filter size: 31
%       'weight'    - input weight value: -0.8
%       'level'     - output threshold level
%
% Boguslaw Obara <ngobara@cyf-kr.edu.pl, obara@ece.ucsb.edu
%--------------------------------------------------------------------------

%--------------------------------------------------------------------------
    in_im=double(in_im);
    localMean=filter2(ones(filter_s),in_im)/(filter_s*filter_s);
    localVar=filter2(ones(filter_s),in_im.^2)/(filter_s*filter_s)-localMean.^2;
    localStd=sqrt(localVar);
    level=localMean+weight*localStd;
%--------------------------------------------------------------------------
end