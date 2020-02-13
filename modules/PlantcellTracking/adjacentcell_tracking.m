function [correspondence]=adjacentcell_tracking(phi1,phi2,edge_threshold1,edge_threshold2,neighbor_threshold)

[index1,index2]=centralcell_tracking(phi1,phi2,edge_threshold1,edge_threshold2,neighbor_threshold);

cord1=getcentroid(phi1,edge_threshold1);
[graph_matrix1,binary_matrix,direction_matrix1]=graphmatrix(cord1,neighbor_threshold);
m1=size(graph_matrix1);
adjacent_cells1=direction_matrix1(index1,:);%adjacent cells

cord2=getcentroid(phi2,edge_threshold2);
[graph_matrix2,binary_matrix,direction_matrix2]=graphmatrix(cord2,neighbor_threshold);
m2=size(graph_matrix2);
adjacent_cells2=direction_matrix2(index2,:);%adjacent cells

m=max(m1,m2);
correspondence=zeros(m,m);


sorted1=fliplr(sort(adjacent_cells1));
sorted1_max=sorted1(1:8);
sorted2=fliplr(sort(adjacent_cells2));
sorted2_max=sorted2(1:8);

cord1=getcentroid_f(phi1,edge_threshold1);  
%cord2=getcentroid(phi2,3.5);

for i=1:8
    a=find(adjacent_cells1==sorted1_max(i));
    b=find(adjacent_cells2==sorted2_max(i));
    correspondence(a,b)=1;
    
    c=int2str(i);
    text(cord2(b).Centroid(1),cord2(b).Centroid(2),c,'Color',[1,0,0],'FontSize',8);

    % plot(cord2(b).Centroid(1),cord2(b).Centroid(2),'Color',[0,0,1],'Marker','o','MarkerSize',10);
end

cord2=getcentroid_f(phi2,edge_threshold2);
for i=1:8
    a=find(adjacent_cells1==sorted1_max(i));
    b=find(adjacent_cells2==sorted2_max(i));
    correspondence(a,b)=1;
    

    %plot(cord1(a).Centroid(1),cord1(a).Centroid(2),'Color',[i/7,i/7,i/7],'Marker','.','MarkerSize',20);
    c=int2str(i);
    text(cord2(b).Centroid(1),cord2(b).Centroid(2),c,'Color',[1,0,0],'FontSize',8);
end