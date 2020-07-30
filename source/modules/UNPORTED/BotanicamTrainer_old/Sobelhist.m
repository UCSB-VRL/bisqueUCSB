function [ h ] = Sobelhist( im )
grey=rgb2gray(im);
grey=double(grey);
Gx=fspecial('sobel');
Gy=Gx';
Sobelx=imfilter(grey,Gx);
%figure
%imshow(Sobelx,[])
Sobely=imfilter(grey,Gy);
%figure
%imshow(Sobely,[])
Mag=sqrt(Sobelx.^2+Sobely.^2);
Ang=180/pi*atan2(Sobely,Sobelx)+180;

h=[];
for theta = 1:360
    fang=and(Ang>=theta,Ang<theta+1);
    h(theta)=sum(sum(fang.*Mag));
end
h=h/sum(h);
end

