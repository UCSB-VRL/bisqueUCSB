function [correspondence]=centralcell_trackingn_un(phi1,phi2,edge_threshold1,edge_threshold2,neighbor_threshold,cellarea_threshold1,cellarea_threshold2)
%neighbor_threshold=80;
eps=10e-9;

cord1=regionprops(bwlabeln(phi1),'Pixellist','PixelIdxList', 'Image','FilledImage','BoundingBox','area','ConvexArea','EulerNumber','ConvexHull','Extrema','centroid','Solidity','Extent','EquivDiamete','Perimeter','MajorAxisLength', 'MinorAxisLength','Orientation','FilledArea');
cord2=regionprops(bwlabeln(phi2),'Pixellist','PixelIdxList', 'Image','FilledImage','BoundingBox','area','ConvexArea','EulerNumber','ConvexHull','Extrema','centroid','Solidity','Extent','EquivDiamete','Perimeter','MajorAxisLength', 'MinorAxisLength','Orientation','FilledArea');

[neighbor_structure1]=cell_neighbor(phi1,edge_threshold1,cellarea_threshold1,neighbor_threshold);
[neighbor_structure2]=cell_neighbor(phi2,edge_threshold2,cellarea_threshold2,neighbor_threshold);

n1=length(cord1);
n2=length(cord2);

correspondence=zeros(n1,n2);

for i=1:n1
    for j=1:n2
        neighbors1=neighbor_structure1(i).neighbors;
        neighbors2=neighbor_structure2(j).neighbors;
        distance1=neighbor_structure1(i).length;
        distance2=neighbor_structure2(j).length;
        orientation1=neighbor_structure1(i).orientation;
        orientation2=neighbor_structure2(j).orientation;
        area1=neighbor_structure1(i).area;
        area2=neighbor_structure2(j).area;
        l1=length(neighbors1);
        l2=length(neighbors2);
        s(i,j)=0;
        if (l1>4)&&(l2>4)&&((abs(cord1(i).FilledArea-cord2(j).FilledArea)/(cord1(i).FilledArea+cord2(j).FilledArea))<1/8)
            for ii=1:l1
                for jj=1:l2
                    
                    orientation_diff=abs(orientation1(ii)-orientation2(jj));
                    if orientation_diff>=180
                        orientation_diff=360-orientation_diff;
                    end
                    
                    distance_diff=abs((distance1(ii)-distance2(jj))/((distance1(ii)+distance2(jj))/2));
                    % area_diff=abs(area1(ii)-area2(jj));
                    area_diff=(abs(area1(ii)-area2(jj))/(area1(ii)+area2(jj)));
                    if (orientation_diff<5)&&(distance_diff<0.05)&&(area_diff<1/8)
                        s(i,j)=s(i,j)+1;
                    end
                end
            end
        end
        s(i,j)=2*s(i,j)/(l1+l2);
    end
end

max_s=max(max(s));
[iii,jjj]=find(s==max_s);
lll=length(iii);
for i=1:lll
    correspondence(iii(i),jjj(i))=1;
end