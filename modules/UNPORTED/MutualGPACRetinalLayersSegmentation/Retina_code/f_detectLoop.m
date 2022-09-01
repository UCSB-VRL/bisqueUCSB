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

% check to see if there is possibly a loop before doing anything
loop_ind = f_checkLoop(P,dp);

if loop_ind == 1,
    % number of snake points
    n_pts = size(P,1);

    % loop indicator (default is 0, no loop)
    loop_ind = 0;

    % start segment index
    count = 1;

    % current points to test for intersections
    n_pts_current = n_pts-1;

    % loop through all segments
    while count < n_pts_current,

        % start line (4x1)
        line_count = [P(count,:) P(count+1,:)]';

        % slope of line_count (for kb later)
        dyb = line_count(3) - line_count(1);
        dxb = line_count(4) - line_count(2);

        % test segment index
        k = count + 2;

        % loop through all test segments
        while k <= n_pts_current,

            % test line
            line_check = [P(k,:) P(k+1,:)]';

            % find intersection point
            P_int = f_intersect(line_count,line_check);

            % compute ka and kb to see if point is on both lines
            dya = line_check(3) - line_check(1);
            dxa = line_check(4) - line_check(2);
            if dya ~= 0,
                ka = (P_int(1)-line_check(1))/dya;
            else
                ka = (P_int(2)-line_check(2))/dxa;
            end
            if dyb ~= 0,
                kb = (P_int(1)-line_count(1))/dyb;
            else
                kb = (P_int(2)-line_count(2))/dxb;
            end

            % lines intersect if 0 < ka,kb < 1
            if (ka < 1) & (ka > 0) & (kb < 1) & (kb > 0),

                % loop indicator is 1
                loop_ind = 1;

                % keep non-looping points and velocities
                P = [P(1:count,:); P(k+1:end,:)];
                V = [V(1:count); V(k+1:end)];

                % update number of test points and index
                n_pts_current = size(P,1)-1;
                k = count + 2;

                % update the start line
                line_count = [P(count,:) P(count+1,:)]';

                % slope of line_count (for kb later)
                dyb = line_count(3) - line_count(1);
                dxb = line_count(4) - line_count(2);
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
end