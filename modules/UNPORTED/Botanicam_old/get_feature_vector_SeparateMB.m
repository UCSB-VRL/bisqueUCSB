function GF=get_feature_vector_SeparateMB(im,scale,orientation,window_size,GW)

%window resize and converted to gray scale
imgsize = 512; 

[h, w, dim] = size(im);
if dim == 3
    im = rgb2gray(im);
end

%downsampling

while max(h, w) > 2000
    im = imresize(im, 1/2);
    [h,w] = size(im);
end

%crop
if min(h, w) > imgsize
    h = floor(h/2);
    w = floor(w/2);
    s = floor(imgsize/2);
    im = im(h-s:h+s-1,w-s:w+s-1);
end

[height,width]=size(im);
% --------------- generate the Gabor FFT data ---------------------
%disp('generating the Gabor FFT matrix');


Nf = window_size; %filter size

% -------------------------------------------------------------------------
% % Divide the image into overlapping patches and compute feature vectors for each patch
%disp('computing features');
Nh = floor(height/Nf*2)-1;
Nw = floor(width/Nf*2)-1;


%applies filter matrix to a patch of the image
GF=zeros(Nw*Nh,2*scale*orientation);
count=0;
for i = 1:Nh,
    for j = 1:Nw,
        count=count+1;
        patch = im((i-1)*Nf/2+1:(i-1)*Nf/2+Nf, (j-1)*Nf/2+1:(j-1)*Nf/2+Nf);
        F = Fea_Gabor_brodatz(patch, GW, scale, orientation, Nf);
        GF(count,:)=[F(:,1)' F(:,2)'];
    end;
end;
end



