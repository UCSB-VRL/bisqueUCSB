function [frameEnd,ALL_PATHS] = MainModuleNew(ImageSequenceFile,initial_trace_text_file,start_frame, bqsession)
%for checking try using the image_data3.mat file.

ImageSequenceFile = mat2gray(ImageSequenceFile);

if numel(size(ImageSequenceFile))==4
    ImageSequenceFile = ImageSequenceFile(:,:,:,start_frame:end);
else
    ImageSequenceFile = ImageSequenceFile(:,:,start_frame:end);
end

FullFile = ImageSequenceFile;
if numel(size(FullFile))==4
    temp = zeros(size(FullFile,1),size(FullFile,2),size(FullFile,4));
    for t = 1:size(FullFile,4)
        temp1 = mat2gray(rgb2gray(FullFile(:,:,:,t)));
        if mean(mean(temp1))>0.5
            temp1 = 1-temp1;
        end
        temp(:,:,t) = temp1;
    end
else
    temp = zeros(size(FullFile,1),size(FullFile,2),size(FullFile,3));
    for t=1:size(FullFile,3)
        temp1 = FullFile(:,:,t);
        if mean(mean(temp1))>0.5
            temp1 = 1-temp1;
        end
        temp(:,:,t) = temp1;
    end
end
% comment the next line when you integrate with bisque. When you test it (say before bisque integration),
% you need this line to give a text input for the program to read and begin
% running.
my_path = initial_trace_text_file;

Ix = my_path(:,1); Iy = my_path(:,2);
im = temp(:,:,1);
my_inv=0;
gradients = gradient_computation_module(im,my_inv);
[my_path,a,b,thresh] = tracing_module(im,gradients,Ix,Iy);
pred_path=my_path;
num_frames = size(temp,3);
ALL_PATHS  = cell(num_frames,1);
ALL_PATHS{1} = my_path;
%generate_text_fileOUTPUT(my_path,frame);UNCOMMENT BEFORE INTEGRATION
for frame=2:num_frames
    bqsession.update(sprintf('%d%%', round(frame*100/num_frames)))
    im=temp(:,:,frame);
    gradients = gradient_computation_module(im,my_inv);
    [my_path,a,b,thresh,pred_path,resultFlag]=tracking_module(im,gradients,pred_path,a,b,thresh);
    if resultFlag==0
        continue;
    end
    ALL_PATHS{frame,1} = my_path;
    % generate_text_fileOUTPUT(my_path,frame); %UNCOMMENT BEFORE INTEGRATION
end
frameEnd = frame;
