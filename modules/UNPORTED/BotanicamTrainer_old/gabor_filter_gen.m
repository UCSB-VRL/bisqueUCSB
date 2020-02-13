function [ newGW ] = gabor_filter_gen(scale, orientation, window_size)

% --------------- generate the Gabor FFT data ---------------------
%disp('generating the Gabor FFT matrix');


    Nf = window_size; %filter size
    freq = [0.01 0.4];%[0.05 0.4];
    flag = 0;

%fix GW matrix resizing
%creates a filter matrix

    for s = 1:scale,
        for n = 1:orientation,
            [Gr,Gi] = gabor(Nf,[s n],freq,[scale orientation],flag);
            F = fft2(Gr+1i*Gi);
            F(1,1) = 0;
            GW(Nf*(s-1)+1:Nf*s,Nf*(n-1)+1:Nf*n) = F;
        end;
    end;
% -------------------------------------------------------------------------
% % Divide the image into overlapping patches and compute feature vectors for each patch

    count=0;
    newGW=zeros([Nf,Nf,orientation*scale]);
    for s = 1:scale,
        for n = 1:orientation,
            count=count+1;
            newGW(:,:,count) = GW(Nf*(s-1)+1:Nf*s,Nf*(n-1)+1:Nf*n);
        end;
    end;
end

