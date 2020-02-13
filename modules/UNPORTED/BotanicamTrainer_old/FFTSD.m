function [ fftd ] = FFTSD(im, threshold, D_num )
%im = image
%threshold for segmentation 
%D_num = number of descriptors
%threshold=180;
%D_num = 500;
seg = htseg(im, threshold);
%figure;
%imshow(seg);
B = bwboundaries(seg);
len=[];
for n=1:length(B)
    len=[len,length(B{n})];
end
[~,index]=max(len);
contour=B{index};

%sample the resample contours
y=contour(:,1);
x=contour(:,2);
mean_y=mean(y);
mean_x=mean(x);
y=y-mean_y;
x=x-mean_x;
y=y(:,1);
x=x(:,1);

y_rep=repmat(y,[3,1]);
x_rep=repmat(x,[3,1]);

p=D_num; %sample length

y_rep=resample(y_rep,p-1,length(y));
x_rep=resample(x_rep,p-1,length(x));

start=length(y_rep)/3;
ends=length(y_rep)-start;

y=y_rep(start:ends)';
x=x_rep(start:ends)';


z=x+1i*y;
fftd=abs(fft(z));
end