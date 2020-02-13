% MergeThresholds - merges lists of detected points for different thresholds
%   dets = MergeThresholds(np)
% 
%   INPUT:
%       np   - cell array with detected nuclei positions for all thresholds
%                np{t}(:,1) -> Y coordinate (starting at 1)
%                np{t}(:,2) -> X coordinate (starting at 1)
%                np{t}(:,3) -> Z coordinate (starting at 1)
%
%   OUTPUT:
%       dets - pruned nuclei positions
%                dets(:,1) -> Y coordinate (starting at 1)
%                dets(:,2) -> X coordinate (starting at 1)
%                dets(:,3) -> Z coordinate (starting at 1)
%                dets(:,4) -> appearence count
%
%   AUTHOR:
%       Dmitry Fedorov, www.dimin.net
%
%   VERSION:
%       0.1 - 2011-03-29 by Dmitry: First implementation
%       0.2 - 2011-06-03 by Dmitry: rewrite with two variants

function dets = MergeThresholds(np)

    % two ways of computing:
    
    % technique N1
    % use low t np, iterate over np find repeating to inc and append
    % generally this should be faster on most smaller vecotrs with few 
    % additional locations to the first vector 
    
    % init the list with the lowest threshold available
    dets = np{1};
    dets(:,5) = [];
    dets(:,4) = 1;

    for t=2:size(np,1),
      n2 = np{t};

      for i=1:size(n2,1),

        [j, ~] = find(dets(:,1)==n2(i,1) & ...
                      dets(:,2)==n2(i,2) & ...
                      dets(:,3)==n2(i,3), 1);

        if isempty(j),
            % we can accept this by expecting very few additions 
            dets = [dets; [n2(i,1:3), 1]];
        else
            dets(j, 4) = dets(j, 4) + 1;
        end

      end
    end
    
    
    % technique N2
    % splice all nps, iterate over, find repeating and set to -1, remove
    % uses more RAM but has no drawback of copying memory on additions
    % but will be slower for smaller matrices with few additions
    
%     dets = cell2mat(np); % this will only work if constructed as cell(N,1)
%     dets(:,5) = [];
%     dets(:,4) = 1;    
%     
%     for i=1:size(dets,1),  
%         
%         if dets(i,1) == -1, continue; end
% 
%         [j, ~] = find(dets(i+1:end,1)==dets(i,1) & ...
%                       dets(i+1:end,2)==dets(i,2) & ...
%                       dets(i+1:end,3)==dets(i,3));
%         j = j + i;
%         if ~isempty(j),
%             dets(i,4) = dets(i,4) + length(j);
%             dets(j,:) = -1;
%         end
% 
%     end
%       
%     remove all -1 elemens
%     dets = dets(dets(:,1)>-1,:);      
      
      

    % remove points with 1 appearence
    dets = dets(dets(:,4)>1, :);
    %dets = sortrows(dets,4);
end    

 