% analyze_matches - produces probabilistic precision, recall and F
% the plot goes by thresholding both point lists by probability
%   [f, p, r, rmse] = analyze_matches(pts, gt, ns, res)
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

function [f, p, r, rmse] = analyze_matches(pts, gt, ns, res)

    range = 0:1:100;
    sz = length(range);

    % go over ground truth probability, all points below
    m = zeros(sz,sz);
    un_pts = zeros(sz,sz);
    un_gt = zeros(sz,sz);    
    rmse = zeros(sz,sz,2);
    
    %% N1: match on every combination of thresholds
    % this will be closer to the reality
    i=0;
    for p_pts = range,   
        ptsProb = pts(pts(:,5)>=p_pts/100, :);
        i=i+1; j=0;
        for p_gt = range,
            gtProb = gt(gt(:,5)>=p_gt/100, :);
            [matches, left_pts, left_gt] = match_points(ptsProb, gtProb, ns);
            j=j+1;
            m(i,j) = size(matches,1);
            un_pts(i,j) = size(left_pts,2);
            un_gt(i,j) = size(left_gt,2);
            
            % compute rmse for matched locations
            v_match_pt = ptsProb(matches(:,1),:);
            v_match_gt = gtProb(matches(:,2),:);
            n = size(v_match_pt,1);
            rmse(i,j,1) = sqrt( 1/n * sum((v_match_pt(:,1)-v_match_gt(:,1)).^2 + ...
                                          (v_match_pt(:,2)-v_match_gt(:,2)).^2 + ...
                                          (v_match_pt(:,3)-v_match_gt(:,3)).^2) );   

            rmse(i,j,2) = sqrt( 1/n * sum(((v_match_pt(:,1)-v_match_gt(:,1)).*res(1)).^2 + ...
                                          ((v_match_pt(:,2)-v_match_gt(:,2)).*res(2)).^2 + ...
                                          ((v_match_pt(:,3)-v_match_gt(:,3)).*res(3)).^2) );  
        end
    end




%     %% N2: match once and then look at every combination of thresholds
%     % this will show how stable the perfect solution is
%     [matches left_pts left_gt] = match_points(pts, gt, ns);
%     v_match_pt = pts(matches(:,1),:);
%     v_match_gt = gt(matches(:,2),:);
%     v_pt = pts(left_pts,:);
%     v_gt = gt(left_gt,:);    
% 
%     %% compute rmse for matched locations
%     n = size(v_match_pt,1);
%     rmse_px_v = sqrt( 1/n * sum((v_match_pt(:,1)-v_match_gt(:,1)).^2 + ...
%                                 (v_match_pt(:,2)-v_match_gt(:,2)).^2 + ...
%                                 (v_match_pt(:,3)-v_match_gt(:,3)).^2) );   
% 
%     rmse_um_v = sqrt( 1/n * sum(((v_match_pt(:,1)-v_match_gt(:,1)).*res(1)).^2 + ...
%                                 ((v_match_pt(:,2)-v_match_gt(:,2)).*res(2)).^2 + ...
%                                 ((v_match_pt(:,3)-v_match_gt(:,3)).*res(3)).^2) );  
% 
%     rmse(:,:,1) = rmse_um_v;
%     rmse(:,:,2) = rmse_px_v;    
%                 
%     %% compute p,r,f                
%     i=0;
%     for p_pts = range,   
%         i=i+1; j=0;
%         for p_gt = range,
%             p_left_pt = v_pt(v_pt(:,5)>=p_pts/100, :); 
%             p_left_gt = v_gt(v_gt(:,5)>=p_gt/100, :); 
%             p_match = v_match_pt(v_match_pt(:,5)>=p_pts/100 &...
%                                  v_match_gt(:,5)>=p_gt/100, :); 
%             
%             j=j+1;
%             m(i,j) = size(p_match,1);
%             un_pts(i,j) = size(p_left_pt,1);
%             un_gt(i,j) = size(p_left_gt,1);     
%         end
%     end
    
    
    %% Results
    %% compute precision, recall and F   
    p = m ./ (m + un_pts);
    r = m ./ (m + un_gt);
    f = ( (p .* r)./(p + r) ) .* 2;
    
    
    %% find the highest point on F measure
    [maxf, i] = max(f(:));
    [i, j] = ind2sub(size(f), i);
    maxp = p(i, j);
    maxr = r(i, j);
    maxrmse = rmse(i, j, 1);
    
    max_match  = m(i, j);    
    max_un_pts = un_pts(i, j);
    max_un_gt  = un_gt(i, j);    
    
    
    nuclear_diameter = max(ns .* res .* 2);
    
    fprintf('Max F=%f P=%f R=%f\n', maxf, maxp, maxr );
    fprintf('RMSE=%f %f%% of nuclear size\n', maxrmse, maxrmse/nuclear_diameter*100);    
    fprintf('auto-t=%d%% gt-t=%d%%\n', range(i), range(j) );    
    fprintf('matched=%d un_pts=%d un_gt=%d \n\n', max_match, max_un_pts, max_un_gt );        
    
    %% plotting results
    figure; 
    %surf(p); 
    imagesc(p);
    title('Precision','FontSize',16); 
    xlabel('Detected centroids thresholded by probability value'); 
    ylabel('Ground truth thresholded by probability value');
    set(gca, 'XTickLabel', range ); set(gca, 'YTickLabel', range );    
    
    figure; 
    %surf(r); 
    imagesc(r);    
    title('Recall','FontSize',16); 
    xlabel('Detected centroids thresholded by probability value'); 
    ylabel('Ground truth thresholded by probability value');
    set(gca, 'XTickLabel', range ); set(gca, 'YTickLabel', range );    
    
    figure; 
    %surf(f); 
    imagesc(f);    
    title('F','FontSize',16);     
    xlabel('Detected centroids thresholded by probability value'); 
    ylabel('Ground truth thresholded by probability value');
    set(gca, 'XTickLabel', range ); set(gca, 'YTickLabel', range );    
   
    figure; 
    %surf(f); 
    imagesc(rmse(:,:,1));    
    title('RMSE','FontSize',16);     
    xlabel('Detected centroids thresholded by probability value'); 
    ylabel('Ground truth thresholded by probability value');    
    set(gca, 'XTickLabel', range ); set(gca, 'YTickLabel', range );    
    
end    

 