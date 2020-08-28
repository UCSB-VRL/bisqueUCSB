function f = calculate_obs(gradients,start_x,end_x,start_y,end_y)

    num_points = 10;
    gxx = my_interp2(gradients.gxx,start_x,end_x,start_y,end_y,num_points);
    gxy = my_interp2(gradients.gxy,start_x,end_x,start_y,end_y,num_points);
    gyx = my_interp2(gradients.gyx,start_x,end_x,start_y,end_y,num_points);
    gyy = my_interp2(gradients.gyy,start_x,end_x,start_y,end_y,num_points);


    my_vec = [start_x-end_x;start_y-end_y];
    my_vec = my_vec/norm(my_vec);
    my_angle = atan(my_vec(2)/(my_vec(1)+1e-6))+pi/2;

    if ~sum(isnan(gxx))
        GG = [gxx,gxy,gyx,gyy];
        gg = [cos(my_angle)^2;
            cos(my_angle)*sin(my_angle);
            cos(my_angle)*sin(my_angle);
            sin(my_angle)^2];
        temp = GG*gg;
        f = -(sum(temp)*2-temp(1)-temp(end))/(2*length(temp)); % synonymous to integration
    else
        f = -inf;
    end