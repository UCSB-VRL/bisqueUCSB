function [ h ] = Sobelhist( im )
%given an image and returns a histogram of all the angles multiplied by
%their given magnitudes
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

h=zeros(1,360);
for theta = 1:360
    fang=and(Ang>=theta,Ang<theta+1);
    h(theta)=sum(sum(fang.*Mag));
end
h=h/sum(h);
end

