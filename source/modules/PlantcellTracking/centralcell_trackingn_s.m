function [correspondence]=centralcell_trackingn_s(phi1,phi2,edge_threshold1,edge_threshold2,neighbor_threshold,cellarea_threshold1,cellarea_threshold2)
%i,j are the correspondence central cell index in phi1 and phi2
eps=10e-9;


%cord1=getcentroid(phi1,edge_threshold1,cellarea_threshold1);
cord1=regionprops(bwlabeln(phi1),'Pixellist','PixelIdxList', 'Image','FilledImage','BoundingBox','area','ConvexArea','EulerNumber','ConvexHull','Extrema','centroid','Solidity','Extent','EquivDiamete','Perimeter','MajorAxisLength', 'MinorAxisLength','Orientation','FilledArea');
[graph_matrix1,edge_matrix1,direction_matrix1]=graphmatrix(cord1,neighbor_threshold);
m11=size(graph_matrix1);

%cord2=getcentroid(phi2,edge_threshold2,cellarea_threshold2);
cord2=regionprops(bwlabeln(phi2),'Pixellist','PixelIdxList', 'Image','FilledImage','BoundingBox','area','ConvexArea','EulerNumber','ConvexHull','Extrema','centroid','Solidity','Extent','EquivDiamete','Perimeter','MajorAxisLength', 'MinorAxisLength','Orientation','FilledArea');
[graph_matrix2,edge_matrix2,direction_matrix2]=graphmatrix(cord2,neighbor_threshold);
m22=size(graph_matrix2);

[n1,m1]=size(cord1);
[n2,m2]=size(cord2);

correspondence=zeros(m11,m22);

for i=1:n1
    for j=1:n2
        
        distance=(cord1(i).Centroid(1)-cord2(j).Centroid(1))^2+(cord1(i).Centroid(2)-cord2(j).Centroid(2))^2;
        P1=cord1(i).PixelList;
        P2=cord2(j).PixelList;
        %shape_simi=ShapeCompare(P1(:,1),P1(:,2),P2(:,1),P2(:,2),100,0);
        %distance_diff(i,j)=distance;
        %[percentage]=cell_overlap(cord1,cord2,i,j);
        if distance<30
            %if abs(cord1(i).Area-cord2(j).Area)<=15
            if (abs(cord1(i).FilledArea-cord2(j).FilledArea)<=min(cord1(i).FilledArea,cord2(j).FilledArea)/4) 
             %if percentage>0.8
                correspondence(i,j)=1;
                
               %end
            end
        end
    end
end

% minimum=min(distance_diff);
% sorted_minimum=sort(minimum);
% sorted_5=sorted_minimum(1:120);
