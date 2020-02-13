function [D] = structureTensor(D,F)
%matlabpool 4

D1 = D(:,:,1).^2;
D2 = D(:,:,2).^2;
D3 = D(:,:,1).*D(:,:,2);
D = cat(3,D,D1,D2,D3);
for i = 0:2
    fprintf(['Starting ' num2str(i) '\n']);
    D(:,:,end-i) = imfilter(D(:,:,end-i),F);
    fprintf(['Ending ' num2str(i) '\n']);
end
%matlabpool close
%{
D1 = imfilter(D(:,:,1).^2,F);
D2 = imfilter(D(:,:,2).^2,F);
D3 = imfilter(D(:,:,1).*D(:,:,2),F);
%}
