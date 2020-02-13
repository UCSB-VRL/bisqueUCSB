function [i, j, val] = find_local_max_2D(E, delta, epsilon, N, min_dist, crop_box_m, borders_m,map)

% [i, j, val] = find_local_max_2D(E, delta, epsilon, N, min_dist, crop_box_m, borders_m)
%
% DESC:
% finds at most N local max in the 2D map E. The minimum distance between
% the peaks is min_dist. The neighborhood to verify the presence of a max
% has radius epsilon
%
% AUTHOR
% Marco Zuliani - zuliani@ece.ucsb.edu
% 
% VERSION:
% 1.1
% 
% INPUT:
% E			    = input 2D map (the entries should be POSITIVE)
% delta         = lattice cell dimensions (if empty then the distance
%                 between the lattice elements is assumed to be 1)
% epsilon       = radius of the interval inside which we look for the
%                 stationary point (defined w.r.t. delta)
% N             = number of desired peaks (inf to find all the admissible
%                 peaks)
% min_dist      = minimum distance between peaks
% crop_box_m    = defines the map portion [x_min x_max] 
%                 to be processed. If empty use the whole map
% borders_m     = prevents the search in the map borders If empty use the
%                 whole map portion
%
% OUTPUT:
% i, j          = peaks coordinates (in the lattice coordinates)
% val           = peaks value

if isempty(delta)
    delta = [1 1];
end;

% select image portion
if isempty(crop_box_m)
    crop_box = [1 size(E, 1) 1 size(E, 2)];
    E_c = E;
else
    crop_box = ceil(crop_box_m ./ delta);
    E_c = E(crop_box(1):crop_box(2), crop_box(3):crop_box(4));
end;


% save some memory
clear E;

if isempty(borders_m)
    borders_m = [0 0];    
end;
borders = ceil(borders_m ./ delta);

% clean non-numeric elements
minimum = min(E_c(:));
E_c(find(~isfinite(E_c))) = minimum;
s = size(E_c);
s_m = delta .* s;

% prepare neighborhood indices
n_dim = ceil(epsilon ./ delta);

h = 1;
ind_n=[];
for i = -n_dim(1):n_dim(1)
    for j = -n_dim(2):n_dim(2)
        
        if ~(i == 0) && ~(j == 0) && ((i*delta(1))^2 + (j*delta(1))^2 <= epsilon^2)
            
            ind_n(1:2, h) = [i; j];
            h = h + 1;
            
        end;
        
    end;
end;
N_n = h - 1;

% prepare extended neighborhood indices
n_dim = ceil(min_dist./delta);

h = 1;
for i = -n_dim(1):n_dim(1)
    for j = -n_dim(2):n_dim(2)
        
        if ( (i*delta(1))^2 + (j*delta(2))^2 <= min_dist^2 )                
            
            ind_n_ext(1:2, h) = [i; j;];  
            h = h + 1;
            
        end;
        
    end;
end;
N_n_ext = h - 1;

l = 1;
val = [];
i = [];
j = [];
mask_s = ones(size(E_c));
mask_s(1:borders(1), :) = 0;
mask_s(size(E_c, 1)-borders(1)+1:size(E_c, 1), :) = 0;
mask_s(:, 1:borders(2)) = 0;
mask_s(:, size(E_c, 2)-borders(2)+1:size(E_c, 2)) = 0;
% only work for map ==1
% to avoid to find a local maximum on the borders
%map = bwmorph(map,'erode');
mask_s(find(map==0))=0;
minimum = min(E_c(:));
while (length(i) < N)
    
    % seek for peaks inside the allowed region
    ind_s = find(mask_s == 1);
   if isempty(ind_s)
        break
    end;
    [v_0 temp] = max(E_c(ind_s));
    if (v_0 == minimum) | isempty(v_0)
        break
    end;
    ind = ind_s(temp(1));
    if isempty(ind)
        break
    end;            
    [I J] = ind2sub(s, ind(1));
    I_m = delta(1) * I;
    J_m = delta(2) * J;
    
    indices = ind_n + repmat([I(1); J(1)], 1, N_n);
    
    % check if we are inside the map portion
    in = find(...
        (indices(1, :) >= 1) & (indices(1, :) <= s(1)) & ...
        (indices(2, :) >= 1) & (indices(2, :) <= s(2)) ...
        );

   
    N_n_in = length(in);
    
    if N_n_in > 0;
        
        % check if v_0 is actually a max
        flag = 1;
        p = 1;
        while (flag) && (p <= N_n_in)
            
            flag = flag && (v_0(1) >= E_c(indices(1, in(p)), indices(2, in(p))));
            p = p + 1;
            
        end;
        
        if flag
            
            % fprintf('\n%d local max found', l);
            
            % save the peak data
            i(l) = crop_box(1) + I - 1;
            j(l) = crop_box(3) + J - 1;
            val(l) = v_0;
            l = l + 1;                
            
        else
            
            mask_s(I, J) = 0;
            
        end;
                
        % and remove it from the map (together with the minimum
        % distance neighborhood)
        indices = ind_n_ext + repmat([I(1); J(1)], 1, N_n_ext);
        in = find( ...
            (indices(1, :) >= 1 & indices(1, :) <= s(1)) & ...
            (indices(2, :) >= 1 & indices(2, :) <= s(2)) ...
            );
        mask_s(sub2ind(s, indices(1, in), indices(2, in))) = 0;
     end;        
    
end;
    
return;