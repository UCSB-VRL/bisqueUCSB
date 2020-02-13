% t_snakeExample

% clear all;        %%%%%  Change N 3D 7D & 28D in '3' Places  
% clc
% clear path;
% dir_in = 'D:\contour\package\groundtruth_data\28d';
% addpath(dir_in);
% %=========================================
% im = imread(strcat(dir_in,'\','data (17).TIF'));  %%%% Change Here
% data_dir='D:\NhatSnake\Nhat_data\28d\';
% addpath(data_dir);
% load dat_gt_28d_im17 pts_orig r c z;    %%%%% Change Here
% 
% im_test = imread(strcat(dir_in,'\','data (21).TIF'));

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
clear all,clc;
clear path;
which=2;
    %%%%%% N %%%%%%%
IND{1}=[2:6];
IND{5}=[8:14];
IND{2}=[17:20];
IND{3}=[21:25];
IND{4}=[26,27,[29:33]];
    %%%%%% 3d %%%%%%%
IND{6}=[14:22];
IND{7}=[[23:26],[28:31]];
IND{8}=[33,36,39,42,45];
IND{9}=[34,37,40,43,46,48,49,50,51];
IND{10}=[35,38,41,44,47];
    %%%%%% 7d %%%%%%%
IND{11}=[1,2,3,4,8,10,11];
IND{12}=[13,15,18,20,21];
    %%%%%% 28d %%%%%%%
IND{13}=[10:15];
IND{14}=[17:24];
IND{15}=[26:33];
IND{16}=[34:39];
IND{17}=[49,51,53,55];
IND{18}=[50,52,54,58,59,60,61,62,64];

name_arr={'N','3d','7d','28d'};
img_dir='/cluster/home/pratim/SnakeProject/Matlab/ImageDatabase/';
data_dir='/cluster/home/pratim/SnakeProject/Matlab/NhatSnake/Nhat_data/';
img_dir=[img_dir name_arr{which} '/data ('];
data_dir=[data_dir name_arr{which} '/dat_gt_'  name_arr{which} '_im'];

if which==1
    start=1;
    finish=5;
end

if which==2
    start=6;
    finish=10;
end

if which==3
    start=11;
    finish=12;
end

if which==4
    start=13;
    finish=18;
end

count1=1;
for i=start:finish
    indices=IND{i};
    count=1;
    ALL={};
    for j=1:size(indices,2)
        im_train_name=[img_dir int2str(indices(j)) ').TIF'];
        data_file_name=[data_dir int2str(indices(j))];
        im_train=imread(im_train_name);
        load (data_file_name);
        Whole_prof=f_GetWholeTraining(im_train,pts_orig,r,c);
        clear pts_orig;
        for k=1:size(indices,2)
            im_test_name=[img_dir int2str(indices(k)) ').TIF'];
            im_test=imread(im_test_name);
            boundary=f_GetBoundary_WithLoop(im_test,Whole_prof,r,c);
            ALL{count}=boundary;
            count=count+1;
        end
    end
    BIG_ALL{count1}=ALL;
    count1
    count1=count1+1;
end

            
            
            
            
            
            
