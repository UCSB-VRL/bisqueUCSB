function boundary=f_GetBoundary(im_test,Whole_prof,r,c)


im_test = im_test(:,:,1:2);
for k = 1:2,
    im_test(:,:,k) = histeq(im_test(:,:,k));
end
im_test = double(im_test);

%%%%%% ALL Parameters %%%%%%%%%
dp_train = 10;
dp = 15;
ds = 5;
len_prof_pixels = 160;
n = ceil(len_prof_pixels/ds);
np = 2*n + 1;
len_prof = ds*n;
im_buffer = 2;
sig_eff = 30/dp;

sig_w_pix = 30;
win = f_getWindow(sig_w_pix,n,ds);
% snake parameters
p_mass = 1;
p_acc = 1;
p_vel = 1;
p_damp = -0.8;
% weighting of channels
w_r = 1;
w_g = 1;
% for display purposes only
chan_num = 1;
ITER=[400,400,400,400,400,400];
f_num=1;
% figure(1); imshow(im_test(:,:,chan_num),[0 255]); hold on;




%%%%%%%%%%%%%1st Layer %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


layer_no=1;
P = [im_buffer:dp:r-im_buffer+1]';                                           
P(:,2) = 60;
% plot(P(:,2),P(:,1),'r.-'); hold off;
Vel = zeros(size(P,1),1);
prof_train=Whole_prof((layer_no-1)*2+1:(layer_no-1)*2+2,:);

for k = 1:ITER(layer_no),
    
    % compute internal force and normal direction R
    [f_int,R] = f_InternalForce(P);
    f_damp = p_damp.*Vel;
    
    % get current profile, then compute external force
    prof_test = f_getProfile(im_test,P,R,len_prof,ds,im_buffer,sig_eff);
    
    % compute external force for each channel
    f_ext_r = f_ExtForceFull(prof_test(:,:,1),prof_train(1,:),win,ds);
    f_ext_g = f_ExtForceFull(prof_test(:,:,2),prof_train(2,:),win,ds);
    
    % total external force (equal weights)
    f_ext = 0*f_ext_r + w_g*f_ext_g;
    
    % total force
    f_total = 2000/dp*f_int + 10*f_ext + f_damp;
    
    % weight of the velocity update
    if max(abs(f_ext))~=0,
        p_vel = min(0.5,0.3/max(abs(f_ext)));
    else
        p_vel = 0.009;
    end
    
%     figure(f_num);imshow(im_test(:,:,chan_num),[0 255]); hold on;
%     plot(P(:,2),P(:,1),'g-','linewidth',2); hold off;
%     title(num2str(k));
%     pause(0.05);

    
    % evolve the snake
    [P,Vel] = f_EvolveSnake(P,Vel,f_total,R,dp,p_mass,p_acc,p_vel,[r,c],im_buffer);
%     if mod(k,21)==0,
%         [P,Vel] = f_detectLoop(P,Vel,dp);
%     end
    if max(abs(f_ext))==0,
%         disp('break');
        break
    end
end

boundary{layer_no}=P;


%%%%%%%%%%%%%%%%%%%%%%%%%%2nd Layer%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

layer_no=2;
P = [im_buffer:dp:r-im_buffer+1]';                                           
P(:,2) = c-60;
% plot(P(:,2),P(:,1),'r.-'); hold off;
Vel = zeros(size(P,1),1);
prof_train=Whole_prof((layer_no-1)*2+1:(layer_no-1)*2+2,:);

for k = 1:ITER(layer_no),
    
    % compute internal force and normal direction R
    [f_int,R] = f_InternalForce(P);
    f_damp = p_damp.*Vel;
    
    % get current profile, then compute external force
    prof_test = f_getProfile(im_test,P,R,len_prof,ds,im_buffer,sig_eff);
    
    % compute external force for each channel
    f_ext_r = f_ExtForceFull(prof_test(:,:,1),prof_train(1,:),win,ds);
    f_ext_g = f_ExtForceFull(prof_test(:,:,2),prof_train(2,:),win,ds);
    
    % total external force (equal weights)
    f_ext = w_r*f_ext_r + w_g*f_ext_g;
    
    % total force
    f_total = 2000/dp*f_int + 10*f_ext + f_damp;
    
    % weight of the velocity update
    if max(abs(f_ext))~=0,
        p_vel = min(0.5,0.3/max(abs(f_ext)));
    else
        p_vel = 0.009;
    end
    
%     figure(f_num);imshow(im_test(:,:,chan_num),[0 255]); hold on;
%     plot(P(:,2),P(:,1),'g-','linewidth',2); hold off;
%     title(num2str(k));
%     pause(0.05);

    
    % evolve the snake
    [P,Vel] = f_EvolveSnake(P,Vel,f_total,R,dp,p_mass,p_acc,p_vel,[r,c],im_buffer);
%     if mod(k,21)==0,
%         [P,Vel] = f_detectLoop(P,Vel,dp);
%     end
    if max(abs(f_ext))==0,
%         disp('break');
        break
    end
end

boundary{layer_no}=P;


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% 3rd Layer %%%%%%%%%%%%%%%%%%%%%%%%%%%%


layer_no=3;
P = [im_buffer:dp:r-im_buffer+1]';                                           
P(:,2) = 0.5*max(boundary{1}(:,2))+0.5*min(boundary{2}(:,2));;
% plot(P(:,2),P(:,1),'r.-'); hold off;
Vel = zeros(size(P,1),1);
prof_train=Whole_prof((layer_no-1)*2+1:(layer_no-1)*2+2,:);

for k = 1:ITER(layer_no),
    
    % compute internal force and normal direction R
    [f_int,R] = f_InternalForce(P);
    f_damp = p_damp.*Vel;
    
    % get current profile, then compute external force
    prof_test = f_getProfile(im_test,P,R,len_prof,ds,im_buffer,sig_eff);
    
    % compute external force for each channel
    f_ext_r = f_ExtForceFull(prof_test(:,:,1),prof_train(1,:),win,ds);
    f_ext_g = f_ExtForceFull(prof_test(:,:,2),prof_train(2,:),win,ds);
    
    % total external force (equal weights)
    f_ext = w_r*f_ext_r + w_g*f_ext_g;
    
    % total force
    f_total = 2000/dp*f_int + 10*f_ext + f_damp;
    
    % weight of the velocity update
    if max(abs(f_ext))~=0,
        p_vel = min(0.5,0.3/max(abs(f_ext)));
    else
        p_vel = 0.009;
    end
    
%     figure(f_num);imshow(im_test(:,:,chan_num),[0 255]); hold on;
%     plot(P(:,2),P(:,1),'g-','linewidth',2); hold off;
%     title(num2str(k));
%     pause(0.05);

    
    % evolve the snake
    [P,Vel] = f_EvolveSnake(P,Vel,f_total,R,dp,p_mass,p_acc,p_vel,[r,c],im_buffer);
%     if mod(k,21)==0,
%         [P,Vel] = f_detectLoop(P,Vel,dp);
%     end
    if max(abs(f_ext))==0,
%         disp('break');
        break
    end
end

boundary{layer_no}=P;


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% 4th Layer %%%%%%%%%%%%%%%%%%%%%%%%%%%%%


layer_no=4;
shift=min(boundary{2}(:,2))-0.15*max(boundary{3}(:,2))-0.85*min(boundary{2}(:,2));
P=boundary{2};
% P = [im_buffer:dp:r-im_buffer+1]';                                           
P(:,2) = P(:,2)-shift;
% plot(P(:,2),P(:,1),'r.-'); hold off;
Vel = zeros(size(P,1),1);
prof_train=Whole_prof((layer_no-1)*2+1:(layer_no-1)*2+2,:);

for k = 1:ITER(layer_no),
    
    % compute internal force and normal direction R
    [f_int,R] = f_InternalForce(P);
    f_damp = p_damp.*Vel;
    
    % get current profile, then compute external force
    prof_test = f_getProfile(im_test,P,R,len_prof,ds,im_buffer,sig_eff);
    
    % compute external force for each channel
    f_ext_r = f_ExtForceFull(prof_test(:,:,1),prof_train(1,:),win,ds);
    f_ext_g = f_ExtForceFull(prof_test(:,:,2),prof_train(2,:),win,ds);
    
    % total external force (equal weights)
    f_ext = w_r*f_ext_r + w_g*f_ext_g;
    
    % total force
    f_total = 2000/dp*f_int + 10*f_ext + f_damp;
    
    % weight of the velocity update
    if max(abs(f_ext))~=0,
        p_vel = min(0.5,0.3/max(abs(f_ext)));
    else
        p_vel = 0.009;
    end
    
%     figure(f_num);imshow(im_test(:,:,chan_num),[0 255]); hold on;
%     plot(P(:,2),P(:,1),'g-','linewidth',2); hold off;
%     title(num2str(k));
%     pause(0.05);

    
    % evolve the snake
    [P,Vel] = f_EvolveSnake(P,Vel,f_total,R,dp,p_mass,p_acc,p_vel,[r,c],im_buffer);
%     if mod(k,21)==0,
%         [P,Vel] = f_detectLoop(P,Vel,dp);
%     end
    if max(abs(f_ext))==0,
%         disp('break');
        break
    end
end

boundary{layer_no}=P;

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% 5th Layer %%%%%%%%%%%%%%%%%%%%%%%%%%%%



layer_no=5;
shift=0.9*max(boundary{1}(:,2))+0.1*min(boundary{3}(:,2))-max(boundary{1}(:,2));
P=boundary{1};
% P = [im_buffer:dp:r-im_buffer+1]';                                           
P(:,2) = P(:,2)+shift;
% plot(P(:,2),P(:,1),'r.-'); hold off;
Vel = zeros(size(P,1),1);
prof_train=Whole_prof((layer_no-1)*2+1:(layer_no-1)*2+2,:);

for k = 1:ITER(layer_no),
    
    % compute internal force and normal direction R
    [f_int,R] = f_InternalForce(P);
    f_damp = p_damp.*Vel;
    
    % get current profile, then compute external force
    prof_test = f_getProfile(im_test,P,R,len_prof,ds,im_buffer,sig_eff);
    
    % compute external force for each channel
    f_ext_r = f_ExtForceFull(prof_test(:,:,1),prof_train(1,:),win,ds);
    f_ext_g = f_ExtForceFull(prof_test(:,:,2),prof_train(2,:),win,ds);
    
    % total external force (equal weights)
    f_ext = w_r*f_ext_r + w_g*f_ext_g;
    
    % total force
    f_total = 2000/dp*f_int + 10*f_ext + f_damp;
    
    % weight of the velocity update
    if max(abs(f_ext))~=0,
        p_vel = min(0.5,0.3/max(abs(f_ext)));
    else
        p_vel = 0.009;
    end
    
%     figure(f_num);imshow(im_test(:,:,chan_num),[0 255]); hold on;
%     plot(P(:,2),P(:,1),'g-','linewidth',2); hold off;
%     title(num2str(k));
%     pause(0.05);

    
    % evolve the snake
    [P,Vel] = f_EvolveSnake(P,Vel,f_total,R,dp,p_mass,p_acc,p_vel,[r,c],im_buffer);
%     if mod(k,21)==0,
%         [P,Vel] = f_detectLoop(P,Vel,dp);
%     end
    if max(abs(f_ext))==0,
%         disp('break');
        break
    end
end

boundary{layer_no}=P;

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% 6th Layer %%%%%%%%%%%%%%%%%%%



layer_no=6;
% shift=0.9*max(boundary{1}(:,2))+0.1*min(boundary{3}(:,2));
% P=boundary{1};
P = [im_buffer:dp:r-im_buffer+1]';                                           
P(:,2) = 0.5*max(boundary{5}(:,2))+0.5*min(boundary{3}(:,2));
% plot(P(:,2),P(:,1),'r.-'); hold off;
Vel = zeros(size(P,1),1);
prof_train=Whole_prof((layer_no-1)*2+1:(layer_no-1)*2+2,:);

for k = 1:ITER(layer_no),
    
    % compute internal force and normal direction R
    [f_int,R] = f_InternalForce(P);
    f_damp = p_damp.*Vel;
    
    % get current profile, then compute external force
    prof_test = f_getProfile(im_test,P,R,len_prof,ds,im_buffer,sig_eff);
    
    % compute external force for each channel
    f_ext_r = f_ExtForceFull(prof_test(:,:,1),prof_train(1,:),win,ds);
    f_ext_g = f_ExtForceFull(prof_test(:,:,2),prof_train(2,:),win,ds);
    
    % total external force (equal weights)
    f_ext = w_r*f_ext_r + w_g*f_ext_g;
    
    % total force
    f_total = 2000/dp*f_int + 10*f_ext + f_damp;
    
    % weight of the velocity update
    if max(abs(f_ext))~=0,
        p_vel = min(0.5,0.3/max(abs(f_ext)));
    else
        p_vel = 0.009;
    end
    
%     figure(f_num);imshow(im_test(:,:,chan_num),[0 255]); hold on;
%     plot(P(:,2),P(:,1),'g-','linewidth',2); hold off;
%     title(num2str(k));
%     pause(0.05);

    
    % evolve the snake
    [P,Vel] = f_EvolveSnake(P,Vel,f_total,R,dp,p_mass,p_acc,p_vel,[r,c],im_buffer);
%     if mod(k,21)==0,
%         [P,Vel] = f_detectLoop(P,Vel,dp);
%     end
    if max(abs(f_ext))==0,
%         disp('break');
        break
    end
end

boundary{layer_no}=P;

