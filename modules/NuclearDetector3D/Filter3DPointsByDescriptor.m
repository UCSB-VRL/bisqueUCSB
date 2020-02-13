%% Filter3DPointsByDescriptor - pruning nuclei positions
%   (this used to be called: BOStatDescriptor3D)
%    np = Filter3DPointsByDescriptor(np, ns)
%
%   INPUT:
%       np      - detected nuclei positions
%                   np(:,1) -> Y coordinate (starting at 1)
%                   np(:,2) -> X coordinate (starting at 1)
%                   np(:,3) -> Z coordinate (starting at 1)
%                   np(:,4) -> point IDs
%                   np(:,5) -> feature value used for filtering
%       ns      - nuclei size
%
%   OUTPUT:
%       np      - pruned nuclei positions, is a matrix of form:
%                   np(:,1) -> Y coordinate (starting at 1)
%                   np(:,2) -> X coordinate (starting at 1)
%                   np(:,3) -> Z coordinate (starting at 1)
%                   np(:,4) -> point IDs
%                   np(:,5) -> feature value used for filtering
%
%   AUTHOR:
%       Boguslaw Obara, http://boguslawobara.net/
%       Dmitry Fedorov, www.dimin.net
%
%   VERSION:
%       0.1 - 30/06/2009 First implementation
%       0.2 - 04/06/2010 Revision
%       0.3 - 24/09/2010 Speed up
%       0.4 - 2011-06-03 by Dmitry: complete rewrite with two variants:
%                                   N1 - 6X speed improvement
%                                   N2 - 127X speed improvement
%%
function np = Filter3DPointsByDescriptor(np, ns)
    
    %% dima N2 - 127X speed improvement
    % most optimized filtering, using find instead of a for loop
    % and a simple differemce instead of eucledian distance
   
    %% ascending sorted array is required before pruning
    np = sortrows(np, 5);    
    sz = size(np,1);      
    for i=sz:-1:2,
        if np(i,1)==-1, continue; end
        
        [j, ~] = find( np(1:i-1,1)>np(i,1)-ns(1) & np(1:i-1,1)<np(i,1)+ns(1) & ...
                       np(1:i-1,2)>np(i,2)-ns(2) & np(1:i-1,2)<np(i,2)+ns(2) & ...
                       np(1:i-1,3)>np(i,3)-ns(3) & np(1:i-1,3)<np(i,3)+ns(3) );
                  
        if ~isempty(j),        
            np(j,:) = -1;            
        end
        
    end

    %% remove those -1 elemens
    np = np(np(:,1)>-1,:);
    np = sortrows(np,4);

%%   
%     %% dima N1
%     % new clearer and simpler code with 6X speed improvement
%     dmax = sqrt( ns(1)^2 + ns(2)^2 + ns(3)^2 ); 
%     xy2z = ns(1)/ns(3); % X/Z resolution
% 
%     % set the feature to use for pruning
%     sz = size(np,1);    
%     for i=1:sz,   
%         % use intensity sum feature
%         np(i,5) = dt{np(i,4)}.sum;        
%     end    
%     np = sortrows(np, 5);
%     
%     % ascending sorted array is required before pruning
%     %for i=sz-1:-1:1,
%     for i=sz:-1:2,
%         if np(i,1)==-1, continue; end
%         %for j=sz:-1:i+1,
%         for j=i-1:-1:1,
%             if np(j,1)==-1, continue; end
%                 
%             d = sqrt( (np(i,1)-np(j,1))^2 + ... 
%                       (np(i,2)-np(j,2))^2 + ... 
%                       (xy2z*(np(i,3)-np(j,3)))^2 );
%             
%             if (d<dmax),
%                 np(j,:) = -1;
%             end
%         end
%     end
% 
%     % remove those -1 elemens
%     np = np(np(:,1)>-1,:);
%     np = sortrows(np,4);
%     
%     fprintf('removed %d points\n', sz-size(np, 1)); 
    
    
    
    
%     
%     %%% bogus
%     dmax = sqrt( ns(1)^2 + ns(2)^2 + ns(3)^2 ); 
%     npp = np; ts = size(npp,1);
%     stop = 1; stopmin = 0; j = 1;
%     xy2z = ns(1)/ns(3); % X/Z resolution
%     %xy2z = 1;
% 
%     %% Loop
%     while(stop>0)
%         ix = 1;
%         if j>ts; break; end
%         m = 10000000;
%         for i=1:ts
%             if i~=j,
%                 d = sqrt(   (npp(i,1)-npp(j,1))^2 + ... 
%                             (npp(i,2)-npp(j,2))^2 + ... 
%                             (xy2z*npp(i,3)-xy2z*npp(j,3))^2);
%                 if m > d
%                     m = d; ix = i; jx = j;
%                 end
%             end
%         end
%     %%  
%         if (m<dmax)
%             s1 = dt{npp(jx,4)}.sum;        
%             s2 = dt{npp(ix,4)}.sum;   
%             removal = removal + 1;         
%             if s1<s2
%                 npp(jx,:) = [];
%                 fprintf('removal N%d of %d \n', removal, jx);
%             else
%                 npp(ix,:) = [];
%                 fprintf('removal N%d of %d \n', removal, ix);
%             end
%             stopmin = 1;
%             ts = size(npp,1);   
%         end
%         j = j + 1;
%         if j>ts
%             if stopmin>0
%                 stopmin = 0;
%                 j = 1;
%             else
%                 stop = 0;
%             end
%         end
%     end
%     %% Sort
%     npp = sortrows(npp,4);
%     npp(:,5) = 1; % dima, just keep compatibility
%     np = npp;
%     fprintf('removed %d points\n', ts-size(np, 1)); 
    
end
