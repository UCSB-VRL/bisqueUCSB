function [neighbor_structure]=cell_neighbor(phi,alpha,cellarea_threshold,neighbor_threshold)
cord=regionprops(bwlabeln(phi),'Pixellist','PixelIdxList', 'Image','FilledImage','BoundingBox','area','ConvexArea','EulerNumber','ConvexHull','Extrema','centroid','Solidity','Extent','EquivDiamete','Perimeter','MajorAxisLength', 'MinorAxisLength','Orientation','FilledArea');
[graph_matrix1,edge_matrix1,direction_matrix1]=graphmatrix(cord,neighbor_threshold);

neighbor_structure=struct('neighbors',{},'length',{},'orientation',{},'area',{});
n=length(cord);

for i=1:n
     sorted=fliplr(sort(direction_matrix1(i,:)));
     s=find(sorted>0);
     l=length(s);
     for jj=1:l
         m=find(direction_matrix1(i,:)==sorted(s(jj)));
         neighbor_structure(i).neighbors(jj)=m;
         neighbor_structure(i).orientation(jj)=direction_matrix1(i,m);
         neighbor_structure(i).length(jj)=edge_matrix1(i,m);
         neighbor_structure(i).area(jj)=cord(m).FilledArea;
     end
end
         
         