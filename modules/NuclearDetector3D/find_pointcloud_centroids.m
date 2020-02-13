% find_pointcloud_centroids - 
%   find centroids of the point cloud using simple heuristic
%   it's simpler and faster than deterministic annealing 
%   implementation is similar to the filtering but
%   it computes centroid locations by averaging nearby points
%
%  [np] = find_pointcloud_centroids(np, ns, numsets)
% 
%   INPUT:
%       np     - set of positions, possibly repeating
%                it's a matrix in a form:
%                   m(:,1) -> Y coordinate (starting at 1)
%                   m(:,2) -> X coordinate (starting at 1)
%                   m(:,3) -> Z coordinate (starting at 1)
%                   m(:,4) -> anything
%                   m(:,5) -> confidence [0:1]
%       ns       - nuclear size in image pixels
%       numsets  - is the number of sets in the data, used for computing
%                  the average of confidence, forces lower numbers if fewer
%                  matches found
%
%   OUTPUT:
%       np  - matrix of centroid locations
%
%   AUTHOR:
%       Dmitry Fedorov, www.dimin.net
%
%   VERSION:
%       0.1 - 2011-03-29 First implementation

function [np] = find_pointcloud_centroids(np, ns, numsets)
    
    %% heuristic based on associated confidence values of points 
    np = sortrows(np, 5);
    np(:,4) = 1; % use this column for count    
        
    %% ascending sorted array is required before pruning
    sz = size(np,1);        
    for i=sz:-1:2,
        if np(i,1)==-1, continue; end
        
        [j, ~] = find( np(1:i-1,1)>np(i,1)-ns(1) & np(1:i-1,1)<np(i,1)+ns(1) & ...
                       np(1:i-1,2)>np(i,2)-ns(2) & np(1:i-1,2)<np(i,2)+ns(2) & ...
                       np(1:i-1,3)>np(i,3)-ns(3) & np(1:i-1,3)<np(i,3)+ns(3) );
                  
        if ~isempty(j),  
            np(i,1:3) = mean(np([j;i],1:3));
            np(i,4:5) = sum(np([j;i],4:5));
            np(j,:) = -1;            
        end
        
    end

    %% remove those -1 elemens
    np = np(np(:,1)>-1,:);
    
    %% update confidence
    if nargin>=3,
        np(:,5) = np(:,5)./numsets;    
    else
        np(:,5) = np(:,5)./np(:,4);   
    end;
    
    np = sortrows(np,5);
end    

 