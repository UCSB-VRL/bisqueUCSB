function [signed_dist contour_band] = compute_signed_dist(im, dist_var)

% Check if the image is binary or logical
contour_band = zeros(size(im));
if( ~islogical(im) )
    im = logical(im);
end

fgnd_indices = find(im);
bgnd_indices = find(~im);
bgnd_size = numel(fgnd_indices) / (numel(fgnd_indices) + numel(bgnd_indices) );
fgnd_size = 1-bgnd_size;
max_dist = sqrt(size(im,1)^2 + size(im,2)^2);

fg_dist = exp( - bwdist(im) ./ dist_var ); fg_dist(fgnd_indices) = 0;
bg_dist = exp( - bwdist(~im) ./ dist_var); bg_dist(bgnd_indices) = 0;
signed_dist = fg_dist + bg_dist;

    contour_band( signed_dist > .5 ) = 1;
    %figure; subplot(211); imagesc(signed_dist); subplot(212); imagesc(contour_band);
return;