function min_project = vrl_visualize_interaction_map(I, nlink_sigma, fignum)

% Usage is vrl_visualize_interaction_map(I, nlink_sigma, fignum)

if(isinteger(I))
    I = double(I);
end
        
grad_s =  exp( - sqrt(sum((I(1:end-1,:,:) - I(2:end, :,:)).^2, 3))            / (2*nlink_sigma^2) );
grad_e =  exp( - sqrt(sum((I(:, 1:end-1,:) - I(:, 2:end,:)).^2, 3))           / (2*nlink_sigma^2) );
grad_se = exp( - sqrt(sum((I(1:end-1, 1:end-1,:) - I(2:end, 2:end,:)).^2, 3)) / (2*nlink_sigma^2) );
grad_sw = exp( - sqrt(sum((I(1:end-1, 2:end,:) - I(2:end, 1:end-1,:)).^2, 3)) / (2*nlink_sigma^2) );

if(fignum~=0)
    figure(fignum);
    subplot(321); imagesc(grad_s); title('South');
    subplot(322); imagesc(grad_e); title('East');
    subplot(323); imagesc(grad_se); title('South-East');
    subplot(324); imagesc(grad_sw); title('South-West');
end

min_img = cat(3, grad_s(:, 1:end-1), grad_e(1:end-1,:), grad_se, grad_sw);
if(fignum~=0)
    subplot(325); imagesc(min(min_img, [], 3)); title('Minimum of all the four planes ');
    subplot(326); hist(min_img(:),10); title('Histogram of Minimum Projection');
end
min_project = hist(min_img(:),10);
