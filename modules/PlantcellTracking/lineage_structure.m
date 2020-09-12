function [lineage] = lineage_structure(c)

noCells=size(c,1);

lineage=struct('daughters',{});

for i=1:noCells
    
   lineage(i).daughters=find(c(i,:)>0);
end

