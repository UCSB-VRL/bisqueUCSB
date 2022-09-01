function [vec_p vec_n] = my_vec_p_n(end_point,start_point);
vec_p = end_point-start_point;
vec_p=(vec_p')./norm(vec_p);
vec_n = null(vec_p');