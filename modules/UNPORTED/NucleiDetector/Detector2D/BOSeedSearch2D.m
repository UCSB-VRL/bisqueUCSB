function nucleiPositions = BOSeedSearch2D(imageGauss, masksizeXY, th_value)
%% BOSeedSearch2D - finding seeds
% 
% Boguslaw Obara, http://boguslawobara.net/
%
% Version:
%   0.1 - 14/11/2008 First implementation
%%
fprintf('BOSeedSearch2D ... \n');
%%
max_c = max(imageGauss(:));
th_level = th_value*max_c;
nucleiPositions = [];
imageMask = imageGauss;
max_c = max(imageMask(:));
%%
while max_c > th_level
    %max_c
    flag=0; 
    while flag==0
        [xc,yc] = find(imageMask==max_c,1,'first');
        if ~isempty([xc,yc]), flag=1; end
    end
    if flag==1
        imageMask = masking_circle(imageMask, masksizeXY, xc, yc);    
        max_c = max(imageMask(:));
        nucleiPositions = [nucleiPositions; xc yc];
    end
end
%%
%% masking_circle
    function imageOut = masking_circle(imageGauss, size_rxy, x0, y0)
        [xs ys]=size(imageGauss);
        mask = ones(xs, ys);
        x1=round(x0-size_rxy); %/2
        x2=round(x0+size_rxy);
        y1=round(y0-size_rxy);
        y2=round(y0+size_rxy);

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
        imageOut = immultiply(imageGauss, mask);
    end
%%
end
