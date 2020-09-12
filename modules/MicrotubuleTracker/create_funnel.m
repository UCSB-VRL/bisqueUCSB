function [E,V] = create_funnel(depth,bf,S)

num_nodes = (depth+1)^2+(depth+1)*(S-1);
E = zeros(num_nodes,3);
V = zeros(num_nodes,2);
k=1;
for i = 1:depth+1
    start_node = (i-1)^2 +1 + (S-1)*(i-1);
    end_node = i^2 + (S-1)*i;
    for j=start_node:end_node
        V(j,2)=i-1;
        V(j,1)=j-(end_node+start_node)/2;
        if i<=depth
            for m=(2*i-1):(2*i-1)+bf-1
                E(k,1)=j;
                E(k,2)=j+m+S-1;
                k=k+1;
            end
        end
    end
end
% grPlot(V,E,'d','','%d');
