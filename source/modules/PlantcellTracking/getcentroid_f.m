function [cordnew]=getcentroid_f(phi,alpha,cellarea_threshold)

[ny,nx]=size(phi);

for i=1:ny
    for j=1:nx
        if phi(i,j)==1
            JJ(i,j)=255;        
        end
    end
end

cord=regionprops(bwlabeln(phi),'pixellist','PixelIdxList', 'Image','FilledImage','BoundingBox','area','ConvexArea','EulerNumber','ConvexHull','Extrema','centroid','Solidity','Extent','EquivDiamete','Perimeter','MajorAxisLength', 'MinorAxisLength','Orientation','FilledArea');

m=length(cord);
j=1;


for ii=1:m
    for jj=1:m
        graph_matrix(ii,jj)=sqrt((cord(ii).Centroid(1)-cord(jj).Centroid(1))^2+(cord(ii).Centroid(2)-cord(jj).Centroid(2))^2);
    end
end

for iii=1:m
   temp=sort(graph_matrix(iii,:));
   lengthsum(iii)=temp(1)+temp(2)+temp(3)+temp(4)+temp(5)+temp(6);
end
   
    
for i=1:m
    if (cord(i).BoundingBox(3)>cellarea_threshold)&&(cord(i).BoundingBox(4)>cellarea_threshold)&&(cord(i).BoundingBox(3)<100)&&(cord(i).BoundingBox(4)<100)&&(lengthsum(i)<300)&&(cord(i).MinorAxisLength>10)
        cordnew(j)=cord(i);
        j=j+1;
    else
        j=j;
    end
end

m_new=length(cordnew);
for i=1:m_new
    x(i)=cordnew(i).Centroid(1);
    y(i)=cordnew(i).Centroid(2);
end

figure,imshow(phi);
 hold on;
 n=length(cordnew);

for i=1:n
    c=int2str(i);
           %text(cordnew(i).Centroid(1),cordnew(i).Centroid(2),c,'Color',[0,1,0],'FontSize',9);
      %plot(cordnew(i).Centroid(1),cordnew(i).Centroid(2),'Color',[1,0,0],'Marker','.','MarkerSize',25);
end
