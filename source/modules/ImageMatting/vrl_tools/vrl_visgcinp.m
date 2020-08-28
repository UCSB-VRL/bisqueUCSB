function vrl_visgcinp(unary_potentials, img_smooth, nlink_sigma, LABELS)

no_objects = size(unary_potentials,3);

% Visualizing Unary Potentials ... 
figure(101)
for iter = 1:no_objects
    subplot(ceil(no_objects/2), 2, iter)
    imagesc(unary_potentials(:,:,iter)); title(['Object No:' num2str(iter)]);
    axis tight;
end

% Visualizing Interaction Map
vrl_visualize_interaction_map(img_smooth, nlink_sigma, 102);
axis tight;

% Visualizing Oversegmentation
if(nargin > 3)
    figure(103);
    imagesc(LABELS);
    axis tight;
    try
    pause; close(101,102,103);
    catch me
        close;
    end
else
    pause; close(101,102);
end

