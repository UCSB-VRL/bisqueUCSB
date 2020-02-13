function y = main_module_2()
start_frame=1;
video_info=mmreader('Phase_Videos/example.avi');
VidFrames = read(video_info);
num_frames=get(video_info,'NumberofFrames');
im=VidFrames(:,:,:,start_frame);
im=rgb2gray(im);
im=mat2gray(im);
imshow(im);
hold on
[Ix Iy] = ginput(6);
im = 1 - im;
my_inv=0;
gradients = gradient_computation_module(im,my_inv);
[my_path,a,b,thresh] = tracing_module(im,gradients,Ix,Iy);
figure;
imshow(im)
hold on;
plot(my_path(:,2),my_path(:,1))
drawnow;
pred_path=my_path;
res_flag = 1;
for frame=start_frame+1:num_frames
    frame
    im=VidFrames(:,:,:,frame);
    im=rgb2gray(im);
    im=mat2gray(im);
    im=1-im;
    gradients = gradient_computation_module(im,my_inv);
    [my_path,a,b,thresh,pred_path,res_flag]=tracking_module(im,gradients,pred_path,a,b,thresh);
    if res_flag == 0;
        continue;
    end
    imshow(im)
    hold on;
    plot(my_path(:,2),my_path(:,1))
    drawnow;
end
y=thresh;