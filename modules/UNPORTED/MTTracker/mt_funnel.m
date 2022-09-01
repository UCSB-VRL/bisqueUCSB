
function sp =  mt_funnel(delta,Ix_tip,Iy_tip,E,V,vec_p,d_p,vec_n,d_n,gradients,a,thresh,depth,S)
[start_x,start_y] = get_pos_from_funnel(Ix_tip,Iy_tip,E(:,1),V,vec_p,vec_n,d_p,d_n);
[end_x,end_y] = get_pos_from_funnel(Ix_tip,Iy_tip,E(:,2),V,vec_p,vec_n,d_p,d_n);
d_deriv = calculate_d_deriv(gradients,start_x,end_x,start_y,end_y);
E(:,3) = 0.5/(a.s).^2*(d_deriv-a.m).^2;



end_nodes = depth^2 +1 + (S-1)*depth:(depth+1)^2 + (S-1)*(depth+1);
num_nodes = (depth+1)^2 + (S-1)*(depth+1);


A = sparse(E(:,1),E(:,2),E(:,3),num_nodes,num_nodes);

temp = zeros(S,2);
for starting_pt = 1:S
    d = shortest_paths(A,starting_pt,struct('algname','dag'));
    [min_val,min_ind] = min(d(end_nodes)-delta(starting_pt));
        
    temp(starting_pt,1) = min_val;
    temp(starting_pt,2) = min_ind;
end
[min_val,min_ind] = min(temp(:,1));

[d,pred] = shortest_paths(A,min_ind,struct('algname','dag'));
sp = path_from_pred(pred,end_nodes(temp(min_ind,2)));


if length(sp) == 1
  sp = [];
    return;
else
    n = length(sp);
    temp = zeros(n-1,1);
    for i = 1:n-1
        [start_x,start_y] = get_pos_from_funnel(Ix_tip,Iy_tip,sp(i),V,vec_p,vec_n,d_p,d_n);
        [end_x,end_y] = get_pos_from_funnel(Ix_tip,Iy_tip,sp(i+1),V,vec_p,vec_n,d_p,d_n);
        temp(i) = calculate_d_deriv(gradients,start_x,end_x,start_y,end_y);
    end
    t1 = sum(temp)/depth;
    t2 = temp(1);
    if t2< thresh %~(t1 > thresh || t2 > thresh)
        sp = [];
    end
end