function win_weight = f_getWindow(sig_win_pixel,n_prof_samp,ds)

% win_weight = f_getWindow(sig_win_pixels,n_prof_samp,ds)
% Computes a weighted Gaussian window with std sig_win_pixels.
%
% INPUT:
%   sig_win_pixel = standard deviation in number of pixels
%   n_prof_samp = number of samples in half of profile (np-1)/2
%   ds = spacing of profile samples
% OUTPUT:
%   win_weight = 1 x (2*n_prof_samp+1) weights of the window
%
% Nhat Vu
% 01.10.2007

% effective sigma in terms of profile samples
sig_win_eff = sig_win_pixel/ds;

% define weighting window
x = -n_prof_samp:n_prof_samp;
win_weight = exp(-1/(sig_win_eff^2)*x.^2);
win_weight = win_weight./max(win_weight);