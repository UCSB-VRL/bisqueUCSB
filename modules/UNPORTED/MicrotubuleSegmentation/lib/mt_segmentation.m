function out_im=mt_segmentation(in_im,filter,length_se,sigma_se,nr_dir_se,se_d,se_l,nr_dir_se2)    
%--------------------------------------------------------------------------
% mt_segmentation - launch segmentation algorithm.
%
%   out_im=mt_segmentation(in_im,filter,length_se,sigma_se,nr_dir_se,se_d,se_l,nr_dir_se2)
%   
%   'in_im'         - input image of Microtubules
%   'filter'        - with initial filtration
%   'length_se'     - lenght of Gauss kermel structuring element
%   'sigma_se'      - sigma of Gauss kernel
%   'nr_dir_se'     - number of directions for Gauss filtration
%   'se_d'          - size of structuring element for final filtration
%   'se_l'          - lenght of structuring element for final filtration
%   'nr_dir_se2'    - number of directions for final filtration
%
%   'out_im'        - output image (label)
%
% Boguslaw Obara <ngobara@cyf-kr.edu.pl, obara@ece.ucsb.edu>
%--------------------------------------------------------------------------

%--------------------------------------------------------------------------
    if filter==1
        se=ones(7,7); se=se*-1; se(4,4)=49;
        ff_im=imfilter(in_im,se,'conv','replicate');
    else
        ff_im=in_im;
    end
%--------------------------------------------------------------------------
    theta_se=0.0;
    max_im=zeros(size(in_im),class(in_im));
    for i=0:nr_dir_se
        theta_se=theta_se+pi/nr_dir_se;
        se=mt_gauss_kernel(length_se,theta_se,sigma_se);
        f_im=imfilter(imcomplement(ff_im),se,'conv','replicate');
        max_im=max(max_im,f_im);
    end
    clear ff_im; clear f_im;    
%--------------------------------------------------------------------------
    max_im=imcomplement(max_im);
    thresh_v=mt_niblack_threshold(max_im,50,-0.8);
    th_im=max_im<thresh_v;
%--------------------------------------------------------------------------
    out_im=logical(zeros(size(th_im)));  
    se=strel('disk',se_d);%2
    ero_im=imerode(th_im,se);
    th_im=imreconstruct(ero_im,th_im);
    for i=0:(180/nr_dir_se2):180
        se=strel('line',se_l,i);%25
        ero_im=imerode(th_im,se);
        rec_im=imreconstruct(ero_im,th_im);
        out_im=max(out_im,rec_im);
    end
    clear max_im; clear ero_im; clear rec_im;
%--------------------------------------------------------------------------
end
%--------------------------------------------------------------------------