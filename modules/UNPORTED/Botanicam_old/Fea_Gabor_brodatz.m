% -----------------------------------------------------------------
% This function compute the image features for each Gabor filter
% output, it is used for PAMI paper.
% -----------------------------------------------------------------

function F = Fea_Gabor_brodatz(img,GW,stage,orientation,Nf)

A = fft2(img);

F = [];

%% This function simply concatenates the mean and variance of the patches
newA = repmat(A,[1,1,stage*orientation]);
D=abs(ifft2(newA.*GW));
meanout=mean(mean((D)));
F(:,1)=meanout;
F(:,2)=sqrt(mean(mean(D-repmat(meanout,[Nf,Nf,1]))).^2);
end
