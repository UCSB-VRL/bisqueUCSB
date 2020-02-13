function my_path = micro_tracing(im,gradients,Ix_start,Iy_start,varargin);
p = inputParser;
p.addRequired('gradients');
p.addRequired('Ix');
p.addRequired('Iy');
p.addOptional('d_p',3);
p.addOptional('d_n',1);
p.addOptional('s',2);
p.addOptional('rect',[1 1 size(im,2) size(im,1)]);
p.parse(im,Ix_start,Iy_start, varargin{:});
d_p = p.Results.d_p;
d_n= p.Results.d_n;
s = p.Results.s;
rect= p.Results.rect;
d_p=1;
my_path=[Iy_start Ix_start];
depth=3; bf=3;
[E,V] = create_funnel(depth,bf,1);
N = size(E,1);
my_sdns = [];
for i = 1:size(my_path,1)-1
    f = calculate_obs(gradients,my_path(i,2),my_path(i+1,2),my_path(i,1),my_path(i+1,1));
    if f~=-inf
        my_sdns = [my_sdns;f];
    end
end
thresh = mean(my_sdns)/s;
iterations=50;
for i=1:iterations
    my_vec_p = my_path(end,:)-my_path(end-1,:);
    my_vec_p=(my_vec_p')./norm(my_vec_p);
    my_vec_n=null(my_vec_p');
    Ix_end = my_path(end,2); Iy_end = my_path(end,1);
    pts = zeros(N,2);
    pts2 = zeros(N,2);
    for i = 1:N
        start_node_id = E(i,1);
        end_node_id = E(i,2);

        [s_x,s_y] = get_pos_from_funnel(Ix_end,Iy_end,start_node_id,V,my_vec_p,my_vec_n,d_p,d_n);
        [e_x,e_y] = get_pos_from_funnel(Ix_end,Iy_end,  end_node_id,V,my_vec_p,my_vec_n,d_p,d_n);

        E(i,3) = -calculate_obs(gradients,s_x,e_x,s_y,e_y);

        pts(i,:) = [e_y,e_x];
        pts2(i,:) = [s_y,s_x];
    end
    end_nodes = (depth+1)^2-depth*2:(depth+1)^2;
    dSP = extract_graph_distance(E);
    [min_val,min_ind] = min(dSP(1,end_nodes));
    sp = extract_best_path(E,dSP,1,end_nodes(min_ind));
    if isempty(sp)
        break;
    else
        current_sdn = dSP(1,sp(2));
        if -min_val/depth > thresh || -current_sdn > thresh
            [current_x,current_y] = get_pos_from_funnel(Ix_end,Iy_end,sp(2),V,my_vec_p,my_vec_n,d_p,d_n);
            my_path = [my_path;current_y,current_x];
            my_sdns = [my_sdns;-current_sdn];
            thresh = mean(my_sdns)/s;
        else
            break;
        end
    end
end