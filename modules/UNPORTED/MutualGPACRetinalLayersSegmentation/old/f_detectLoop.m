function [P,V] = f_detectLoop(P,V,dp)

% [P,V] = f_detectLoop(P,V,dp)
% Given the snake points P, f_detectLoop removes all the loops from the
% snake.  The remaining points will retain their original velocities before
% resampling.
%
% INPUT:
%   P = N x 2 snake vertices
%   V = N x 1 velocity from previous update
%   dp = scalar: spacing of snake vertices
% OUTPUT:
%   P and V are loop free if original P,V had loops
%
% Nhat Vu
% 01.09.2007

% number of snake points
n_pts = size(P,1);

% loop indicator (default is 0, no loop)
loop_ind = 0;

% start segment index
count = 1;

% current points to test for intersections
n_pts_current = n_pts-2;

% loop through all segments
while count < n_pts_current,
   
    % start line (4x1)
    line_count = [P(count,:) P(count+1,:)]';
    
    % test segment index
    k = count + 2;
    
    % loop through all test segments
    while k <= n_pts_current,
        
        % test line
        line_check = [P(k,:) P(k+1,:)]';
        
        % find intersection point
        P_int = f_intersect(line_count,line_check);
        
        % compute convex hull to determine whether P_int inside quad
        x = [P([count count+1],1); P([k k+1],1); P_int(1)]; 
        y = [P([count count+1],2); P([k k+1],2); P_int(2)]; 
        
        % try/catch in case all pts on straight line and convhull cannot compute
        try
            c = convhull(x,y);
        catch
            c = 0;
        end
        
        % see if P_int is included in convhull
        int_indicator = find(c == 5);
        
        % if not included and c is quadrillateral (lenght(c)=5)
        if (length(c) == 5) & isempty(int_indicator),
            
            % loop indicator is 1
            loop_ind = 1;
            
            % keep non-looping points and velocities
            P = [P(1:count,:); P(k+1:end,:)];
            V = [V(1:count); V(k+1:end)];
            
            % update number of test points and index
            n_pts_current = size(P,1)-2;
            k = count + 2;
            
            % update the start line
            line_count = [P(count,:) P(count+1,:)]';         
        else
            k = k + 1;
        end
    end   
    count = count + 1;
end

% resample curve only if loop_ind is 1
if loop_ind == 1,
    PV = f_ResampleCurve([P V],dp);
    P = [PV(:,1),PV(:,2)];
    V = PV(:,3);
end
    