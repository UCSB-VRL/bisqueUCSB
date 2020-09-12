function Whole_prof=f_GetWholeTraining(im,pts_orig,r,c)

%%% parameters
im = im(:,:,1:2);
for k = 1:2,
    im(:,:,k) = histeq(im(:,:,k));
end
im = double(im);


dp_train = 10;
dp = 15;
ds = 5;
len_prof_pixels = 160;
n = ceil(len_prof_pixels/ds);
np = 2*n + 1;
len_prof = ds*n;
im_buffer = 2;
sig_eff = 30/dp;
Whole_prof=[];
% figure(3);imshow(uint8(im(:,:,1)));
for i=1:6
    P_raw = pts_orig{1,i};
    P_train = f_pt2line(fliplr(P_raw),[r c]);
    P_train = P_train(1:dp_train:end,:);
%     hold on;plot(P_train(:,2),P_train(:,1));hold off;
    [R,C] = f_getNormalCurvature(P_train);
    prof_train_all = f_getProfile(im,P_train,R,len_prof,ds,im_buffer,sig_eff);

    % mean of training profiles
    for k = 1:2,
        prof_train(k,:) = mean(prof_train_all(:,:,k),1);
    end
    Whole_prof=[Whole_prof;prof_train];
%     pause;
end
    
