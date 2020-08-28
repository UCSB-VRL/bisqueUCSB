% analyze_match - computes precision, recall and F for all points
%   [f, p, r, rmse] = analyze_match(pts, gt, ns, res)
% 
%   INPUT:
%       pts     - detected nuclear positions, is a matrix of form:
%       gt      - ground truth nuclear positions, is a matrix of form:
%                   m(:,1) -> Y coordinate (starting at 1)
%                   m(:,2) -> X coordinate (starting at 1)
%                   m(:,3) -> Z coordinate (starting at 1)
%                   m(:,4) -> point IDs
%                   m(:,5) -> confidence [0:1]
%       ns       - nuclear size in image pixels
%       res      - voxel resolution
%
%   OUTPUT:
%       f    - F measure, matrix for both probability values, pts on i
%       p    - Precision, matrix for both probability values, pts on i
%       r    - Recall, matrix for both probability values, pts on i
%       rmse - RMSE, matrix for both probability values, pts on i
%
%   AUTHOR:
%       Dmitry Fedorov, www.dimin.net
%
%   VERSION:
%       0.1 - 2011-03-29 First implementation

function [f, p, r, rmse] = analyze_match(pts, gt, ns, res)

    %% N2: match once and then look at every combination of thresholds
    % this will show how stable the perfect solution is
    [matches, left_pts, left_gt] = match_points(pts, gt, ns);
    v_match_pt = pts(matches(:,1),:);
    v_match_gt = gt(matches(:,2),:);

    %% compute rmse for matched locations
    n = size(v_match_pt,1);
    rmse(1) = sqrt( 1/n * sum((v_match_pt(:,1)-v_match_gt(:,1)).^2 + ...
                                (v_match_pt(:,2)-v_match_gt(:,2)).^2 + ...
                                (v_match_pt(:,3)-v_match_gt(:,3)).^2) );   

    rmse(2) = sqrt( 1/n * sum(((v_match_pt(:,1)-v_match_gt(:,1)).*res(1)).^2 + ...
                                ((v_match_pt(:,2)-v_match_gt(:,2)).*res(2)).^2 + ...
                                ((v_match_pt(:,3)-v_match_gt(:,3)).*res(3)).^2) );  
            
    %% compute p,r,f                
    m      = size(matches,1);
    un_pts = size(left_pts,2);
    un_gt  = size(left_gt,2);     
    
    
    %% Results
    %% compute precision, recall and F   
    p = m ./ (m + un_pts);
    r = m ./ (m + un_gt);
    f = ( (p .* r)./(p + r) ) .* 2;
    
    
    %% find the highest point on F measure
    maxf = f;
    maxp = p;
    maxr = r;
    maxrmse = rmse(1);
    max_match  = m;    
    max_un_pts = un_pts;
    max_un_gt  = un_gt;    
    nuclear_diameter = max(ns .* res .* 2);
    rmse = rmse(2);
    
    fprintf('Max F=%f P=%f R=%f\n', maxf, maxp, maxr );
    fprintf('RMSE=%f %f%% of nuclear size\n', maxrmse, maxrmse/nuclear_diameter*100);    
    fprintf('matched=%d un_pts=%d un_gt=%d \n\n', max_match, max_un_pts, max_un_gt );        
end    

 