function B = calculate_obs_prob2(r,Q,gradients,a,b,NL,d_p)
N = length(r.nx);
S = Q*Q+2;
B = zeros(S,N);
Ix_end = r.vx((Q+1)/2,1);   Iy_end = r.vy((Q+1)/2,1);
[my_vec_p,my_vec_n] = my_vec_p_n([Iy_end,Ix_end],[r.vy((Q+1)/2,2),r.vx((Q+1)/2,2)]);
Ix_end_new = Ix_end + d_p*my_vec_p(2);
Iy_end_new = Iy_end + d_p*my_vec_p(1);
vx_ext = linspace(Ix_end_new-my_vec_n(2)*NL,Ix_end_new+my_vec_n(2)*NL,Q)';
vy_ext = linspace(Iy_end_new-my_vec_n(1)*NL,Iy_end_new+my_vec_n(1)*NL,Q)';
for i=1:N
    dead_state_prob = zeros(S-2,1);
    for j=1:Q
        for k=1:Q
            if i ==1                
                f = calculate_obs(gradients,r.vx(j,i),vx_ext(k),r.vy(j,i),vy_ext(k));
            else
                f = calculate_obs(gradients,r.vx(j,i),r.vx(k,i-1),r.vy(j,i),r.vy(k,i-1));
            end
            if f == -inf
                B((j-1)*Q+k,i) = 0;
                dead_state_prob((j-1)*Q+k) = 1;
            else
                B((j-1)*Q+k,i) = my_normpdf(f,a.m,a.s);
                dead_state_prob((j-1)*Q+k) = my_normpdf(f,b.m,b.s);
            end
        end
    end
    B(S-1,i) = min(dead_state_prob);
    B(S,i) = min(dead_state_prob);
end
