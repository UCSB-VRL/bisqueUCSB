function [final_mask]=f_get1mask(points, im_size)
flag_side = 1;
final_mask=zeros(im_size);

num_layers=size(points, 2);
for i=1:num_layers
    [line_ind, xy_line, mask] = f_pt2mask2(points{i},im_size,flag_side);
    final_mask=final_mask+mask;
end

return

    