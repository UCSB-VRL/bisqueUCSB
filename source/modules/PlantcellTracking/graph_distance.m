function[d]=graph_distance(phi1,phi2,c,edge_threshold1,edge_threshold2,neighbor_threshold,cellarea_threshold1,cellarea_threshold2,ii)

jj=find(c(ii,:)>0);
dis=0;

if isempty(jj)==0
    eps=10e-9;
    
    cord1=getcentroid(phi1,edge_threshold1,cellarea_threshold1);
    [graph_matrix1,edge_matrix1,direction_matrix1]=graphmatrix(cord1,neighbor_threshold);
    
    cord2=getcentroid(phi2,edge_threshold2,cellarea_threshold2);
    [graph_matrix2,edge_matrix2,direction_matrix2]=graphmatrix(cord2,neighbor_threshold);
    
    ind1=find(direction_matrix1(ii,:)>0); %all neighbors
    N=1;
    
    for i=1:length(ind1)
        ind2=find(c(ind1(i),:)==1);
        if isempty(ind2)==0
            
            direction1=direction_matrix1(ii,ind1(i));
            direction2=direction_matrix2(jj,ind2);
            
            edge1=edge_matrix1(ii,ind1(i));
            edge2=edge_matrix2(jj,ind2);
            if edge1*edge2>0
                area1=cord1(ind1(i)).FilledArea;
                area2=cord2(ind2).FilledArea;
                
                if abs(direction1-direction2)>=180
                    delta_direction=360-abs(direction1-direction2);
                else
                    delta_direction=abs(direction1-direction2);
                end
                
                dis=dis+abs(area1-area2)^2/(area1^2)+abs(delta_direction)^2/((max(direction1,direction2))^2)+abs(edge1-edge2)^2/(edge1^2);
                N=N+1;
            else
                N=N;
            end
        else
            N=N;
        end
    end
    
    if N==1
        d=10^5;
    else
        d=dis/N;
    end
else
    d=10^5;
end
