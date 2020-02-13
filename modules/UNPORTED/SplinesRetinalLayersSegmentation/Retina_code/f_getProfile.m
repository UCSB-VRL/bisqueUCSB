function [prof,prof_ind,prof_ns,row_prof,col_prof] = f_getProfile(img,P,R,len_prof,ds,im_buffer,sigma_eff)

% [prof,prof_ind] = f_getProfile(img,P,R,len_prof,ds,im_buffer,sigma_eff)
% Computes the orthogonal intensity profiles along snake points P with normal R.
%
% INPUT:
%   img = r x c x z image (z >= 1)
%   P = N x 2 snake vertices
%   R = N x 2 normal vectors at P
%   len_prof = half length of profile in number of pixels
%   ds = sampling rate of profile (number of pixels)
%   im_buffer = number of pixels to skip from top and bottom of image
%   sigma_eff = effective sigma of tangential smoothing kernel
% OUTPUT:
%   prof = N x M x z: each row is a profile
%   prof_ind = indices of pixels at profile points (for plotting purposes)
%
% Nhat Vu (modified from Pratim Ghosh)
% 12.24.2006

% image dimension
[r,c,z] = size(img);

% number of snake points
N_pt = size(P,1);

% compute real length (if len_prof is not exact multiples of ds)
n_samp = ceil(len_prof/ds);
template = ds*[-n_samp:n_samp];
template(2,:) = 0;

% number of profile points
N_prof = size(template,2);

% coordinates of profile
row_prof = zeros(N_pt,N_prof);
col_prof = zeros(N_pt,N_prof);

% angle to rotate
ang = atan(-R(:,1)./R(:,2));

% rotate template by ang, then translate template to P
for i = 1:N_pt,
    a = sin(ang(i));
    b = cos(ang(i));
    rot_template = [b a;-a b]*template;
    
    % ceil is to convert to pixel location
    col_prof(i,:) = ceil(rot_template(1,:) + P(i,2));
    row_prof(i,:) = ceil(rot_template(2,:) + P(i,1));
end

% move out of bound points to border
col_prof(col_prof<1) = 1;
col_prof(col_prof>c) = c;
row_prof(row_prof<im_buffer) = im_buffer;
row_prof(row_prof > (r-im_buffer+1)) = r-im_buffer+1;

% convert profile points to image indices
prof_ind = sub2ind([r c],row_prof(:),col_prof(:));

% smoothing kernel
k_size = ceil(4*sigma_eff);
x = -k_size:k_size;
kernel = exp((-x.^2)./(2*sigma_eff^2));
kernel = kernel./sum(kernel(:));
n_pad = (length(x)-1)/2;
% get grey value from each layer of image then smooth tangentially
for k = 1:z,
    img_temp = img(:,:,k);
    prof_temp = reshape(img_temp(prof_ind),N_pt,N_prof);
    prof_ns = prof_temp;
    % smoothing (pad first, then convolve across rows)
    prof_temp = padarray(prof_temp,[n_pad 0],'replicate');
    prof(:,:,k) = conv2(kernel,[1],prof_temp,'valid');
end