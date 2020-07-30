function my_path = init_path(Ix_start,Iy_start,gxx,gxy,gyx,gyy,gx,gy,d)

my_path = zeros(3,2);
Ix = Ix_start; Iy = Iy_start;
for i=1:3
    [Vx_n,Vy_n,Vx_p,Vy_p,fd,sd,t] = calculate_directions(gxx,gxy,gyx,gyy,gx,gy,Ix,Iy);
    [Iy,Ix] = project_to_tube(Ix,Iy,Vx_n,Vy_n,gxx,gxy,gyx,gyy,d);
    [Vx_n,Vy_n,Vx_p,Vy_p,fd,sd,t] = calculate_directions(gxx,gxy,gyx,gyy,gx,gy,Ix,Iy);

    if (abs(t*Vx_n) < 0.5 && abs(t*Vy_n) < 0.5 )
        Ix = Ix + t*Vx_n; Iy = Iy + t*Vy_n;
    end
    my_path(i,:) = [Iy,Ix];
    Iy_new = Iy + Vy_p*d;
    Ix_new = Ix + Vx_p*d;
    if i>1
        my_vec =  my_path(i-1,:) - my_path(i,:);
        my_vec = my_vec/(norm(my_vec)+1e-6);
        if my_vec*[Vy_p;Vx_p] > 0
            Iy_new = Iy - Vy_p*d;
            Ix_new = Ix - Vx_p*d;
        end
    end
    Iy = Iy_new;
    Ix = Ix_new;
end
