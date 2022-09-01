function [centroidCell areaCell cellPixelArray] = findCellInfo(B,L)
    for k=2:length(B)
        [r c] = find(L==k); 
        centroidCell(k-1,:) = [mean(c) mean(r)]; 
%         plot(centroid(k-1,1), centroid(k-1,2), 'g.');
        boundary = B{k};
        areaCell(k-1,1) = polyarea(boundary(:,1),boundary(:,2));
        cellPixelArray{k-1} = B(k);
    end    
end