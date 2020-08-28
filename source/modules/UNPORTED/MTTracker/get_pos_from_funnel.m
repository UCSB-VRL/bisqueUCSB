function [Ix,Iy] = get_pos_from_funnel(Ix_start,Iy_start,node_id,V,vec_p,vec_n,d,n)
Ix = Ix_start + d*V(node_id,2)*vec_p(2) + n*V(node_id,1)*vec_n(2);
Iy = Iy_start + d*V(node_id,2)*vec_p(1) + n*V(node_id,1)*vec_n(1);