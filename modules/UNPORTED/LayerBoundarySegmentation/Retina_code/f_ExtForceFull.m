function [f,E,ind_m,ind_p] = f_ExtForceFull(prof_test,prof_target,win_weight,ds)

% [f,E,ind_m,ind_p] = f_ExtForceFull(prof_test,prof_target,win_weight,ds)
% Computes the external or data driven force.
%
% Nhat Vu
% 01.10.07

% number of profiles and total length of profile
[n_prof,np] = size(prof_test);

% if only one prof_target, repeat to same size as prof_test
n_target = size(prof_target,1);
if n_target == 1,
    prof_target = repmat(prof_target,n_prof,1);
end

win_weight = repmat(win_weight,n_prof,1);
% s_win = size(win_weight)
% s_tar = size(prof_target)
% s_prof = size(prof_test)
% half width
n = (np-1)/2;

% initialize energy
E = zeros(n_prof,np);

for k = 0:n,
    
    % define weight
    w = np/(np - 2*abs(k));
    
    % target and test profile indices (reverse for negative side)
    ind_target = (k+1):np;
    ind_test = 1:(np-k);
    
    % negative energy
    E(:,n+1-k) = w*sum(win_weight(:,ind_test).*abs(prof_target(:,ind_test)-prof_test(:,ind_target)),2);
    
    % positive energy
    E(:,k+n+1) = w*sum(win_weight(:,ind_target).*abs(prof_target(:,ind_target)-prof_test(:,ind_test)),2);
        
end


% find the minimum energy spot
[val,ind_min] = min(E,[],2);

% indices that are on the left
ind_left = ind_min < (n+1);
ind_mid = ind_min == (n+1);
ind_right = ind_min > (n+1);

% corresponding indices on other side
ind_m = ind_min; ind_m(~ind_left) = np-ind_m(~ind_left)+1;
ind_p = ind_min; ind_p(~ind_right) = 2*(n+1)-ind_p(~ind_right);

% ind_m(ind_mid) = n;
% ind_p(ind_mid) = n+2;

dr = ind_p - ind_m;

% ind_m_local = n*ones(size(ind_m));
% ind_p_local = (n+2)*ones(size(ind_p));

ind_row = 1:n_prof;
ind_m = sub2ind([n_prof np],ind_row',ind_m);
ind_p = sub2ind([n_prof np],ind_row',ind_p);

% ind_m_local = sub2ind([n_prof np],ind_row',ind_m_local);
% ind_p_local = sub2ind([n_prof np],ind_row',ind_p_local);

% force is -central difference dE(0)
% f_local = -(E(ind_p_local) - E(ind_m_local))/(2*ds);
f = -(E(ind_p) - E(ind_m));
ind_dr = (dr ~= 0);
f(ind_dr) = f(ind_dr)./(dr(ind_dr));

% discrete filter
% kernel = [0.5 1 0.5];
% f = [f(1); f; f(end)];
% f = conv(f,kernel);
% f = f(3:end-2);