function sp =  mt_funnel(delta,Ix_tip,Iy_tip,E,V,vec_p,d_p,vec_n,d_n,gradients,a,thresh,depth,S)
N = size(E,1);
for i = 1:N
    [start_x,start_y] = get_pos_from_funnel(Ix_tip,Iy_tip,E(i,1),V,vec_p,vec_n,d_p,d_n);
    [end_x,end_y] = get_pos_from_funnel(Ix_tip,Iy_tip,E(i,2),V,vec_p,vec_n,d_p,d_n);
    E(i,3)=-log(my_normpdf(calculate_obs(gradients,start_x,end_x,start_y,end_y),a.m,a.s));
end


end_nodes = depth^2 +1 + (S-1)*depth:(depth+1)^2 + (S-1)*(depth+1);
dSP = extract_graph_distance(E);
temp = zeros(S,2);
for starting_pt = 1:S
    [min_val,min_ind] = min(dSP(starting_pt,end_nodes)-delta(starting_pt));
    temp(starting_pt,1) = min_val;
    temp(starting_pt,2) = min_ind;
end
[min_val,min_ind] = min(temp(:,1));
sp = extract_best_path(E,dSP,min_ind,end_nodes(temp(min_ind,2)));

if isempty(sp)
    return;
else
    n = length(sp);
    temp = zeros(n-1,1);
    for i = 1:n-1
        [start_x,start_y] = get_pos_from_funnel(Ix_tip,Iy_tip,sp(i),V,vec_p,vec_n,d_p,d_n);
        [end_x,end_y] = get_pos_from_funnel(Ix_tip,Iy_tip,sp(i+1),V,vec_p,vec_n,d_p,d_n);
        temp(i) = calculate_obs(gradients,start_x,end_x,start_y,end_y);
    end
    t1 = sum(temp)/depth;
    t2 = temp(1);
    if t2< thresh %~(t1 > thresh || t2 > thresh)
        sp = [];
    end
end