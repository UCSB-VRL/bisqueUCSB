function vrl_show_interaction(I, I_fg)    

%% Output Full Interaction 
I_show = I; 
if(size(I_show,3) == 1)
    I_show = repmat(I_show,[1 1 3]);
end

for obj_iter = 1:numel(I_fg)
    tempo = I_show(:,:,1);
    tempo( I_fg{obj_iter} ) = 255*rand;
    I_show(:,:,1) = tempo;
end


    
    
    figure;
    h = gcf;
    imshow(uint8(I_show));
    