function B = calculate_obs_prob_ext(r,Q,gradients,a,b,d_p,NL,tip_or_end)
S = Q*Q+2;
B = zeros(S,1);
dead_state_prob = zeros(S-2,1);
Ix_end = r.vx((Q+1)/2,1);   Iy_end = r.vy((Q+1)/2,1);
[my_vec_p,my_vec_n] = my_vec_p_n([Iy_end,Ix_end],[r.vy((Q+1)/2,2),r.vx((Q+1)/2,2)]);
Ix_end_new = Ix_end + d_p*my_vec_p(2);
Iy_end_new = Iy_end + d_p*my_vec_p(1);
vx_ext = linspace(Ix_end_new-my_vec_n(2)*NL,Ix_end_new+my_vec_n(2)*NL,Q)';
vy_ext = linspace(Iy_end_new-my_vec_n(1)*NL,Iy_end_new+my_vec_n(1)*NL,Q)';
for j=1:Q
    for k=1:Q
        switch tip_or_end
            case 'end2'
                f = calculate_obs(gradients,r.vx(j,1),vx_ext(k),r.vy(j,1),vy_ext(k));
            case 'tip'
                f = calculate_obs(gradients,r.vx(j,end),r.vx(k,end-1),r.vy(j,end),r.vy(k,end-1));
            case 'end'
                f = calculate_obs(gradients,r.vx(j,2),r.vx(k,1),r.vy(j,2),r.vy(k,1));
        end
        if f == -inf
            B((j-1)*Q+k) = 0;
            dead_state_prob((j-1)*Q+k) = 1;
        else
            B((j-1)*Q+k) = my_normpdf(f,a.m,a.s);
            dead_state_prob((j-1)*Q+k) = my_normpdf(f,b.m,b.s);
        end
    end
end
B(S-1) = min(dead_state_prob);
B(S) = min(dead_state_prob);