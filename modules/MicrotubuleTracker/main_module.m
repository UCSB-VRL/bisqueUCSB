function y = main_module();
start_frame=1;
% load image_data;
load im_da_2;
im=B(:,:,start_frame);
% im=rgb2gray(im);
% im=mat2gray(im);
imshow(im);
hold on
[Ix Iy] = ginput(3);
my_inv=0;
% num_frames=size(B,4);
num_frames=38;
gradients = gradient_computation_module(im,my_inv);
[my_path,a,b,thresh] = tracing_module(im,gradients,Ix,Iy);
f1 = figure;
imshow(imadjust(im),'init', 'fit')
hold on;
plot(my_path(:,2),my_path(:,1),'g','Linewidth',2)
drawnow;
MtTraceStack={};
MtTraceStack=[MtTraceStack {my_path}];
pred_path=my_path;
close figure 1;
close figure 2;
for frame=start_frame+1:num_frames
    frame
    im=B(:,:,frame);
%     im=rgb2gray(im);
%     im=mat2gray(im);
    gradients = gradient_computation_module(im,my_inv);
    [my_path,a,b,thresh,pred_path]=tracking_module(im,gradients,pred_path,a,b,thresh);
    f=figure;
    imshow(imadjust(im),'init','fit')
    hold on;
    plot(my_path(:,2),my_path(:,1),'g','Linewidth',2)
    drawnow
    saveas(f,['f' num2str(frame)],'jpg');
    MtTraceStack=[MtTraceStack {my_path}];
    close figure 1;
end
y=MtTraceStack;   