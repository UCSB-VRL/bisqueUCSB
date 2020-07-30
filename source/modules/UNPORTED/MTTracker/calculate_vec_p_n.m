function [vec_p,vec_n] = calculate_vec_p_n(vec_end,vec_start)

vec_p = vec_end-vec_start;
vec_p = vec_p'/norm(vec_p);
vec_n = null(vec_p');
