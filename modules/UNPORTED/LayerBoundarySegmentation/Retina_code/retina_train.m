function profile_full = retina_train(im,train_gt) % im is the training image
% Script for training 

% Input:
% im - The training image from which the profile is to be extracted
% train_gt - A cell array containing the points corresponding to the ground
% truth as each element in the cell array
% 1: GCL/bg, 2: OS/bg, 3: INL/ONL, 4: ONL/IS, 5: GCL/INL

% Output:
% profile_full - A cell array, where each element corresponds to the
% intensity profile extracted as a result of training ...

%==========================================================================
% parameters that are set by user
dp_train = 10;  % sampling along training border
dp = 15;        % sampling along snake border
ds = 5;         % sampling along snake profile (delta in paper)
len_prof_pix = 160;     % desired half length of profile (pixels)
sig_w_pix = 30;         % effective scale for windowing profile energies
im_buffer = 2;  % pixels from top and bottom of im to skip (bad images somtimes)

% derived parameters
sig_eff = 30/dp;    % effective scale for smoothing across profiles
n_samp = ceil(len_prof_pix/ds);     % number of samples on each side
np = 2*n_samp + 1;                  % number of samples total (M in paper)
len_prof = ds*n_samp;               % actual number of half length (pixels)
%==========================================================================


% Conversion to train all layers at the same time .....
%This will give the number of layers layers that need to be extracted ...
num_layers = size(train_gt,2);
[r c z] = size(im);
% prof_train = zeros(2,65);

 im = im(:,:,1:2);
        for k = 1:2,
            im(:,:,k) = histeq(im(:,:,k));
        end
im = double(im);

for lay = 1:num_layers
    % convert points to line with single pixel spacing
    P_raw = train_gt{1,lay};
    P_train = f_pt2line(fliplr(P_raw),[r c]);

    % equalize each channel (only red greed here)
   

    % get training profiles
    P_train = P_train(1:dp_train:end,:);    % resample traced curve
    [R,C] = f_getNormalCurvature(P_train);  % get normal direction
    tic,
    prof_train_all = f_getProfile(im,P_train,R,len_prof,ds,im_buffer,sig_eff);
    toc;
        % CHK: See sizes if needed % req_size = size(prof_train_all);

    % average profiles for each channel
        
            prof_train(1,:) = mean(prof_train_all(:,:,1),1);
            prof_train(2,:) = mean(prof_train_all(:,:,2),1);
        
    profile_full{lay} = prof_train;
    
end
%==========================================================================