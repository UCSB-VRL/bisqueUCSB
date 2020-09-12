function imageOut = BOGaussian3DFastDiv(imageIn, sizex, sizey, sizez, sigma)    
%% BOGaussian3DFastDiv - convolving image with 3D Log  + div.
% 
% Boguslaw Obara, http://boguslawobara.net/
%
% Version:
%   0.1 - 16/02/2008 First implementation
%%
size_s = size(imageIn);
fxy = 100;
%fxy = 40;
h_s = sizex; %16;
steps_x = ceil(size_s(1,1)/fxy);
steps_y = ceil(size_s(1,2)/fxy);
fx = 1;
for x = 1:steps_x
    fy = 1;
    for y = 1:steps_y
        %xb1=(1+fxy*(x-1)+h_s);
        xb2=(1+fxy*x+h_s);
        %yb1=(1+fxy*(y-1)+h_s);
        yb2=(1+fxy*y+h_s);
        %s=[x1 y1 x2 y2]
        if xb2>size_s(1,1), xb2=size_s(1,1); end
        if yb2>size_s(1,2), yb2=size_s(1,2); end
        %-------------------------------------        
        xs1=(1+fxy*(x-1)-h_s);
        %xs2=(1+fxy*x-h_s);
        ys1=(1+fxy*(y-1)-h_s);
        %ys2=(1+fxy*y-h_s);
        %s=[x1 y1 x2 y2]
        if xs1<1, xs1=1; end
        if ys1<1, ys1=1; end
        %-------------------------------------
        x1=(1+fxy*(x-1));
        x2=(1+fxy*x);
        y1=(1+fxy*(y-1));
        y2=(1+fxy*y);
        %s=[x1 y1 x2 y2]
        if x2>size_s(1,1), x2=size_s(1,1); end
        if y2>size_s(1,2), y2=size_s(1,2); end
        %-------------------------------------
        sx=x2-x1; sy=y2-y1;
        if x>1, fx=2; end
        if y>1, fy=2; end
        xss1=(1+h_s*(fx-1));
        xss2=xss1+sx;
        yss1=(1+h_s*(fy-1));
        yss2=yss1+sy;
        %s=[x1 y1 x2 y2]
        if xss2>size_s(1,1), xss2=size_s(1,1); end
        if yss2>size_s(1,2), yss2=size_s(1,2); end
        %-------------------------------------
        %tmp_stack=imfilter(imageIn(xs1:xb2,ys1:yb2),h,'conv'); 
        %tmp_stack = uint16(ngui_gaussian3Dfil(imageIn(xs1:xb2,ys1:yb2,:), sizex, sizey, sizez, sigma));
        tmp_stack = BOGaussian3DFast(imageIn(xs1:xb2,ys1:yb2,:), sizex, sizey, sizez, sigma);

        %tmp_stack=imageIn(xs1:xb2,ys1:yb2); 
        imageOut(x1:x2,y1:y2,:) = tmp_stack(xss1:xss2,yss1:yss2,:);
%         imagesc(imageOut(:,:,1));
%         w=[x1 x2 y1 y2]
%         w=[xs1 xb2 ys1 yb2]
%         waitforbuttonpress
        %size(imageOut)
        clear tmp_stack;
    end
end
%%
end
