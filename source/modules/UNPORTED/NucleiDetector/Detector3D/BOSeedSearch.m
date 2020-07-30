function [imageOut table] = BOSeedSearch(imageIn, imageGauss, masksizeXY, masksizeZ, th_value)
%% BOSeedSearch - finding seeds
% 
% Boguslaw Obara, http://boguslawobara.net/
%
% Version:
%   0.1 - 16/02/2008 First implementation
%%
fprintf('BOSeedSearch ... \n');
%%
max_c = max(imageGauss(:));
%im = double(((imageGauss-min(imageGauss(:)))/(max(imageGauss(:))-min(imageGauss(:)))));
%th_level=max_c*graythresh(im);
%th_level = max_c / 0.3;%2.5;
th_level = th_value*max_c;

table=[];
[Ix Iy Iz] = size(imageGauss);
imageOut = logical(zeros(size(imageGauss)));
imageMask = imageGauss;
max_c = max(imageMask(:));
while max_c > th_level
    %max_c
    flag=0; ix=1;
    while flag==0
        [xc,yc] = find(imageMask(:,:,ix)==max_c,1,'first');
        if ~isempty([xc,yc]), flag=1; end
        ix=ix+1;
        if  ix>Iz+1, flag=2; end
    end
    if flag==1
        imageMask = masking_circle(imageMask, masksizeXY, masksizeZ, xc, yc, ix-1);    
        max_c = max(imageMask(:));
        imageOut(xc,yc,ix-1) = 1;
        if (ix-1)==0
            error('ERROR :)')
        end
        table = [table; xc yc ix-1];
        %[r c ix-1]
%         subplot(1,2,1); imagesc (imageIn(:,:,ix-1)), title(ix-1);
%         subplot(1,2,2); imagesc (imageMask(:,:,ix-1)), title(ix-1);
%         pause(0.1)
%         waitforbuttonpress
        %size(table);
    elseif flag==2
        max_c = max(imageMask(:));
    end
end
%%
%% masking_circle
    function imageOut=masking_circle(imageGauss, size_rxy, size_rz, x0, y0, z0)
        [xs ys zs]=size(imageGauss);
        mask = ones(xs, ys);
        x1=round(x0-size_rxy); %/2
        x2=round(x0+size_rxy);
        y1=round(y0-size_rxy);
        y2=round(y0+size_rxy);
        z1=round(z0-size_rz);
        z2=round(z0+size_rz);
        
        for x=x1:x2 
            for y=y1:y2
                if ((x-x0)*(x-x0)+(y-y0)*(y-y0))<=(size_rxy*size_rxy)
                    xw=x;
                    yw=y;                    
                    if(x<1), xw=1; end 
                    if(y<1), yw=1; end 
                    if(x>xs), xw=xs; end
                    if(y>ys), yw=ys; end 
                    mask(xw,yw)=0;
                end
            end
        end
        for z=z1:z2 
            zw=z;
            if(z<1), zw=1; end 
            if(z>zs), zw=zs; end
            imageGauss(:,:,zw)= immultiply(imageGauss(:,:,zw), mask);
        end
        imageOut=imageGauss;
%         for i=1:10
%             imagesc(imageOut(:,:,i));
%             title(i);
%             pause(1)
%         end        
    end
%% masking_circleX
    function imageOut=masking_circleX(imageGauss, size_rxy, size_rz, x0, y0, z0)
        [xs ys zs]=size(imageGauss);
        mask = ones(xs, ys);
        x1=round(x0-size_rxy); %/2
        x2=round(x0+size_rxy);
        y1=round(y0-size_rxy);
        y2=round(y0+size_rxy);
        z1=round(z0-size_rz);
        z2=round(z0+size_rz);
        
        for x=x1:x2 
            for y=y1:y2
                if ((x-x0)*(x-x0)+(y-y0)*(y-y0))<=(size_rxy*size_rxy)
                    xw=x;
                    yw=y;                    
                    if(x<1), xw=1; end 
                    if(y<1), yw=1; end 
                    if(x>xs), xw=xs; end
                    if(y>ys), yw=ys; end 
                    mask(xw,yw)=0;
                end
            end
        end
        for z=z1:z2 
            zw=z;
            if(z<1), zw=1; end 
            if(z>zs), zw=zs; end
            imageGauss(:,:,zw)= immultiply(imageGauss(:,:,zw), mask);
        end
        imageOut=imageGauss;
%         for i=1:10
%             imagesc(imageOut(:,:,i));
%             title(i);
%             pause(1)
%         end        
    end
%%
end
