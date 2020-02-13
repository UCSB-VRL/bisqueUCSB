function [I_d I_ud] = vrl_user_interaction(I, no_objects)

%% Code that takes in the image alone and gets four user markings
%% First two markings are for foreground
%% Second two markings are for background

%% Input Variables
%% I   - Input Image assumed to be RGB

%% Output Variables
%% I_fg - Coordinates for the Foreground Markings
%% I_bg - Coordinates for the Background Markings


    %% Initializing Parameters
    im = zeros(size(I, 1), size(I, 2));
    if(size(I,3) == 1)
        I_show = cat(3, I, I, I);
    else
        I_show = I;
    end
    dilate_size = 3;
I_d = cell(1,no_objects);
I_ud = cell(1,no_objects);
for obj_iter = 1:no_objects    
    I_fg = [];
    
    pts_fg = cell(2, 1);     
    
    %% Actual User Interaction
    flag_val = true;
    count = 1;
    while(flag_val)
          [pts_fg{count} flag_val] = vrl_freehand_draw(true);
          count = count + 1;         
    end


    %% Getting the Foreground Points
    for i = 1:length(pts_fg)
        pts = pts_fg{i};
        for j = 2:size(pts, 1)
            [d1, d2] = vrl_get_search_path(size(im), pts(j - 1, 1), pts(j - 1, 2), pts(j, 1), pts(j, 2));
            I_fg = [I_fg; d2];
        end
    end
    I_fg = unique(I_fg);
    Ibw = false(size(im));
    Ibw(I_fg) = true;
    I_fg_ud = find(Ibw);
    Ibw = imdilate(Ibw, strel('disk', dilate_size, 0));
    I_fg = find(Ibw);
    I_ud{obj_iter} = I_fg_ud;
    I_d{obj_iter} = I_fg;
    %% Output Full Interaction       

    tempo = I_show(:,:,1);
    tempo( I_fg ) = 255*rand;
    I_show(:,:,1) = tempo;
    
    imshow(uint8(I_show)); title('User_Interaction');
end
            
