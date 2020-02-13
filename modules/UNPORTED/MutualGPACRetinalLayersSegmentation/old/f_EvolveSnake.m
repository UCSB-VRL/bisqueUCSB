function [P_new,V_new] = f_EvolveSnake(P,V,f_total,R,dp,p_mass,p_acc,p_vel,im_size,im_buffer)

% [P_new,V_new] = f_EvolveSnake(P,V,f_total,R,dp,p_mass,p_acc,p_vel,im_size,im_buffer)
% Update the positions P and velocities V of the snake at each vertex.
%
% INPUT:
%   P = N x 2 snake vertices (row,column) coordinates
%   V = N x 1 velocity from previous update
%   f_total = N x 1 force (f_int + f_ext + f_damp) computed outside
%   R = N x 2 normal vectors at vertices
%   dp = scalar: spacing of snake vertices
%   p_mass = mass parameter
%   p_acc = acceleration parameter
%   p_vel = velocity parameter
%   im_size = [r,c] from size(image)
%   im_buffer = scalar: spacing from border point
%
% OUTPUT:
%   P_new = M x 2 updated snake vertices
%   V_new = M x 1 updated snake velocity
%
% Nhat Vu (modified from Pratim Ghosh)
% 12.22.2006

% acceleration
acc = f_total./p_mass;

% velocity
V_new = V + p_acc*(acc);

% update position along normal direction only
P_new = P + p_vel*repmat(V_new,1,2).*R;

%---check for snake points outside image buffer after update------
% maximum size for image
r_max = im_size(1) - im_buffer;
c_max = im_size(2) - im_buffer;

% indices of points outside left column
c_index1 = find(P_new(:,2)<1);
if ~isempty(c_index1),
    P_new(c_index1,2) = 1;
    V_new(c_index1) = 0;
end

% indices of points outside right column
c_index2 = find(P_new(:,2)>c_max);
if ~isempty(c_index2),
    P_new(c_index2,2) = c_max;
    V_new(c_index2) = 0;
end

% indices of points outside top row
r_index1 = find(P_new(:,1)<=im_buffer,1,'last');
if ~isempty(r_index1),
    if abs(im_buffer - P_new(r_index1+1,1)) >= 0.1,
        % cut outside portion, then place new point at border
        P_int = f_intersect([im_buffer 1 im_buffer c_max]',[P_new(r_index1,:) P_new(r_index1+1,:)]');
        P_new = [P_int'; P_new(r_index1+1:end,:)];
        V_new = [V_new(r_index1); V_new(r_index1+1:end)];
    else
        P_new = P_new(r_index1+1:end,:);
        V_new = V_new(r_index1+1:end);
    end
elseif isempty(r_index1) & (abs(im_buffer - P_new(1,1)) >= 0.1), 
    % add point at border anyway in case snake moved inside too much
    P_int = f_intersect([im_buffer 1 im_buffer c_max]',[P_new(1,:) P_new(2,:)]');
    P_new = [P_int'; P_new];
    V_new = [V_new(1); V_new];
end

% indices of points outside bottom row
r_index2 = find(P_new(:,1)>=r_max,1,'first');
if ~isempty(r_index2),
    if abs(P_new(r_index2-1,1) - r_max) >= 0.1,
        P_int = f_intersect([r_max 1 r_max c_max]',[P_new(r_index2,:) P_new(r_index2-1,:)]');
        P_new = [P_new(1:r_index2-1,:); P_int'];
        V_new = [V_new(1:r_index2-1); V_new(r_index2)];
    else
        P_new = P_new(1:r_index2-1,:);
        V_new = V_new(1:r_index2-1);
    end
elseif isempty(r_index2) & (abs(P_new(end,1) - r_max) >=0.1), 
    % add point at border anyway in case snake moved inside too much
    P_int = f_intersect([r_max 1 r_max c_max]',[P_new(end,:) P_new(end-1,:)]');
    P_new = [P_new; P_int'];
    V_new = [V_new; V_new(end)];
end

% resample curve                               
PV = f_ResampleCurve([P_new V_new],dp);
P_new = [PV(:,1),PV(:,2)];
V_new = PV(:,3);