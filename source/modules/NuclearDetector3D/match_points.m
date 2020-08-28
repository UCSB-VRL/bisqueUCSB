% match_points - this function matches points from the set pts1 to the set pts2
% using maximum distance specified by ns
% returns indices for matched and unmatched locations
% 
%   INPUT:
%       pts1     - first set of nuclear positions, is a matrix of form:
%       pts2     - second set of nuclear positions, is a matrix of form:
%                   m(:,1) -> Y coordinate (starting at 1)
%                   m(:,2) -> X coordinate (starting at 1)
%                   m(:,3) -> Z coordinate (starting at 1)
%                   m(:,4) -> point IDs
%                   m(:,5) -> confidence [0:1]
%       ns       - nuclear size in image pixels
%
%   OUTPUT:
%       matches  - matrix of matched locations: [index_pts1, index_pts2]
%       left1    - indices of unmatched points from set N1
%       left2    - indices of unmatched points from set N2
%
%   AUTHOR:
%       Dmitry Fedorov, www.dimin.net
%
%   VERSION:
%       0.1 - 2011-03-29 First implementation

function [matches, left1, left2] = match_points(pts1, pts2, ns)
    
    dmax = sqrt( ns(1)^2 + ns(2)^2 + ns(3)^2 ); 
    sz1 = size(pts1,1);
    sz2 = size(pts2,1);
    
    big = 10000;
    dst = zeros( sz1, sz2 );
    dst(:,:) = big;
    
    % compute all reasonable distances
    for i=1:sz1,
%         l = pts1(i,:)-ns;
%         u = pts1(i,:)+ns;
%         [j, ~] = find( pts2(:,1)>l(1) & pts2(:,1)<u(1) & ...
%                        pts2(:,2)>l(2) & pts2(:,2)<u(2) & ...
%                        pts2(:,3)>l(3) & pts2(:,3)<u(3) );
%                   

        % Compute distance with every point from pts2
        d = sqrt((pts2(:,1)-pts1(i,1)).^2 + ...
                 (pts2(:,2)-pts1(i,2)).^2 + ...
                 (pts2(:,3)-pts1(i,3)).^2); 
        
       dst(i,:) = d;
    end
    
    % find matches    
    matches = [];
    for it=1:min(sz1,sz2),
        [md, indx] = min(dst(:));
        if md>dmax, break; end % no more matches can be found
        [ii, jj] = ind2sub(size(dst), indx);
        matches = [matches; ii, jj, md];
        dst(ii,:) = big;
        dst(:,jj) = big;
    end
      
    left1 = setdiff(1:sz1, matches(:,1));
    left2 = setdiff(1:sz2, matches(:,2));
    
end    

 