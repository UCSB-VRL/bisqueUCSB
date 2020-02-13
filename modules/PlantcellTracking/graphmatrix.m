function [graph_matrix,edge_matrix,direction_matrix]=graphmatrix(cord,threshold)

%usually, the threshold is 50
eps=10e-9;
m=length(cord);
for i=1:m
    for j=1:m
        graph_matrix(i,j)=sqrt((cord(i).Centroid(1)-cord(j).Centroid(1))^2+(cord(i).Centroid(2)-cord(j).Centroid(2))^2);
        
        if graph_matrix(i,j)<threshold
           
            edge_matrix(i,j)=graph_matrix(i,j);
            
            if (cord(j).Centroid(2)-cord(i).Centroid(2)>=0)&&(cord(j).Centroid(1)-cord(i).Centroid(1)>=0)
                direction_matrix(i,j)=atan((cord(j).Centroid(2)-cord(i).Centroid(2))/(cord(j).Centroid(1)-cord(i).Centroid(1)+eps))*360/2/pi;
            
            elseif (cord(j).Centroid(2)-cord(i).Centroid(2)>0)&&(cord(j).Centroid(1)-cord(i).Centroid(1)<0)
                direction_matrix(i,j)=atan((cord(j).Centroid(2)-cord(i).Centroid(2))/(cord(j).Centroid(1)-cord(i).Centroid(1)+eps))*360/2/pi+180;
                
            elseif (cord(j).Centroid(2)-cord(i).Centroid(2)<0)&&(cord(j).Centroid(1)-cord(i).Centroid(1)<0)
                direction_matrix(i,j)=atan((cord(j).Centroid(2)-cord(i).Centroid(2))/(cord(j).Centroid(1)-cord(i).Centroid(1)+eps))*360/2/pi+180;
                
            elseif (cord(j).Centroid(2)-cord(i).Centroid(2)<0)&&(cord(j).Centroid(1)-cord(i).Centroid(1)>0)
                direction_matrix(i,j)=atan((cord(j).Centroid(2)-cord(i).Centroid(2))/(cord(j).Centroid(1)-cord(i).Centroid(1)+eps))*360/2/pi+360;
            end
        
        else
            edge_matrix(i,j)=0;
            direction_matrix(i,j)=0;
        end
    end
end

for i=1:m
    direction_matrix(i,i)=0;
end
