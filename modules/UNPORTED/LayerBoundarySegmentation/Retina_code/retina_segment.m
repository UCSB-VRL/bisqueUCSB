function layer_seg = retina_segment(test_image,profile_full,train_gt,im)

% load temp1.mat;
% profile_full = initial_full_profile;

[r c z] = size(test_image);
num_layers = size(train_gt,2);
%==========================================================================
% parameters that are set by user
dp_train = 10;  % sampling along training border
dp = 15;        % sampling along snake border
ds = 5;         % sampling along snake profile (delta in paper)
len_prof_pix = 160;     % desired half length of profile (pixels)
sig_w_pix = 30;         % effective scale for windowing profile energies
im_buffer = 2;  % pixels from top and bottom of im to skip (bad images somtimes)

% weighting of forces from each channel (equal in this case)
w_r = 1;
w_g = 1;

% snake dynamics parameters (empirically set)
p_mass = 1;
p_acc = 1;
p_vel_min = 0.01;
p_damp = -0.8;
w_int = 2000/dp;    % weight of internal force
w_ext = 10;         % weight of external force

% derived parameters
sig_eff = 30/dp;    % effective scale for smoothing across profiles
n_samp = ceil(len_prof_pix/ds);     % number of samples on each side
np = 2*n_samp + 1;                  % number of samples total (M in paper)
len_prof = ds*n_samp;               % actual number of half length (pixels)

% compute window for profile energy (alpha(k) in paper)
gweight = f_getWindow(sig_w_pix,n_samp,ds);
%==========================================================================




%==========================================================================
% load testing image
im_test = test_image;

% equalize channels
im_test = im_test(:,:,1:2);
for k = 1:2
    im_test(:,:,k) = histeq(im_test(:,:,k));
end
im_test = double(im_test);


% Start boundary segmentation by initializing snake somewhere near the
% boundary (within +/- len_prof_pix).  Here, the user is prompted to select
% a point in the image near the desired boundary.  Of course this can be
% done automatically given a prior info on image geometry.

% prompt user to select a point near boundary
% figure(1); imshow(im_test(:,:,2),[0 255]); hold on;
% impixelinfo;
% title('click a point near desired boundary');
% [x_in y_in] = ginput(1);
% y_in=size(im_test,1)/2;

% hold off;

for lay = 1:num_layers

    x_in=median(train_gt{lay}(:,1));
    
    prof_train(1,:) = profile_full{lay}(1,:);
%     if(lay == 1)
%         prof_train2 = prof_train(1,:);
%         save temp2.mat prof_train2;
%     end
%     error('Stop Here');
    prof_train(2,:) = profile_full{lay}(2,:);
    
    % initialize P as vertical line containing selected point
    P = [im_buffer:dp:r-im_buffer+1]';
    P(:,2) = x_in;

    % initialize velocity Vel = 0 for all points in P
    Vel = zeros(size(P,1),1);

    % iterate
    for k = 1:200,

        % compute internal force and normal direction R
        [f_int,R] = f_InternalForce(P);

        % get current profile, then compute external force
        prof_test = f_getProfile(im_test,P,R,len_prof,ds,im_buffer,sig_eff);

        % compute external force for each channel
        f_ext_r = f_ExtForceFull(prof_test(:,:,1),prof_train(1,:),gweight,ds);
        f_ext_g = f_ExtForceFull(prof_test(:,:,2),prof_train(2,:),gweight,ds);

        % total external force is weighted sum
        f_ext = w_r*f_ext_r + w_g*f_ext_g;

        % damping force
        f_damp = p_damp.*Vel;

        % total force
        f_total = w_int*f_int + w_ext*f_ext + f_damp;

        % parameter for velocity update (based on how strong the force is)
        p_vel = min(p_vel_min,0.1/max(abs(f_ext+eps)));

        % evolve the snake to new position
        [P,Vel] = f_EvolveSnake(P,Vel,f_total,R,dp,p_mass,p_acc,p_vel,size(im),im_buffer);

        % check for self-intersection every N iterations
        if mod(k,21) == 0,
            [P,Vel] = f_detectLoop(P,Vel,dp);
        end

        % end if all forces are zeros
        if max(abs(f_ext))==0,
            disp('break');
            break
        end

    end
    layer_seg{lay} = fliplr(P);
end