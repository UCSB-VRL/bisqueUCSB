function [ErrorMsg segm_pts] = mask2seg(image,interval,max_layers)
% usage segm_pts_set_to_be_updated = bmap2seg (greyscale_input_image, interval_for_scan)

% update 1: check added to see if the layers are consistent
% if more than 3 noisy pixels break

%% NOTE : Image size and mask size should be same
%% NOTE : Assumes a image with less noise. Better to do a simple median filtering on the image before calling this function
ErrorMsg = '';

[height, width] = size(image);

rows = [1:interval:height height];
    try
        %do for all the intervals
        for i = rows
            pix_val = image(i,1);
            flag_first = 0;
            flag_normal = 0;
            layer_num = 1;
            for j = 1:width-11
                new_pix_val = image(i,j);
 %the condition below is not stable - fails on mask image of the reference
 %as the mask as 1's on the LHS region of the mask
 %condition introduced for images which are output of GPAC, and fail to
 %generate any output boundary (any region with pixvals=255)- in this case,
 %set the boundary to left boundary of the image
 
                if(pix_val == 1 && ~flag_first && ~flag_normal)
                    index = ceil(i/interval);
                    segm_pts{layer_num}(index,1) = j+2;
                    segm_pts{layer_num}(index,2) = i;
                    flag_first =1;
                    
                    layer_num = layer_num +1;
                    pix_val = new_pix_val;
             
                elseif((pix_val == new_pix_val) && (j<width-11))
                    continue;  
                           
                else % : update 1:
                    flag_error = 0;
                    err_val = 0;
                    for k = j:j+10
                        if((image(i,k) ~= image(i,k+1)))
                            err_val = err_val +1;
                            if(err_val > 3)
                                flag_error = 1;
                                break;
                            end
                        end
                    end
                    if(flag_error || layer_num > max_layers)
                        continue;
                    end
                    index = ceil(i/interval);
                    segm_pts{layer_num}(index,1) = j;
                    segm_pts{layer_num}(index,2) = i;

                    layer_num = layer_num +1;
                    pix_val = new_pix_val;
                    flag_normal = 1;
                end
                
            end
        end
    end
end
        
