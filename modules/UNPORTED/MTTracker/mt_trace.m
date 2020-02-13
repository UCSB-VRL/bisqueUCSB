function my_path = mt_trace(im,gradients,Ix_start,Iy_start,varargin)
p = inputParser;
p.addRequired('im');
p.addRequired('Ix_start');
p.addRequired('Iy_start');
p.addOptional('d_p',3);
p.addOptional('d_n',1);
p.addOptional('s',2);
p.addOptional('rect',[1 1 size(im,2) size(im,1)]);
p.parse(im,Ix_start,Iy_start, varargin{:});

d_p = p.Results.d_p;
d_n= p.Results.d_n;
s = p.Results.s;
rect= p.Results.rect;

if length(Ix_start)>1
    track_type = 'invivo';
else
    track_type = 'motility';
end


switch track_type
    case 'motility'
        my_path = init_path(Ix_start,Iy_start,...
            gradients.gxx,gradients.gxy,gradients.gyx,gradients.gyy,...
            gradients.gx,gradients.gy,d_p);
        iter = 100;
    case 'invivo'
        my_path = [Iy_start,Ix_start];
        iter = 50;
    otherwise
        error('Currently either motility and invivo tracking is supported\n');
end



%plot_trace(my_im,my_path,[],1,1,1);


depth = 3; bf = 3;
[E,V] = create_funnel(depth,bf,1);
N = size(E,1);

my_sdns = [];
for m = 1:size(my_path,1)-1
    f = calculate_d_deriv(gradients,my_path(m,2),my_path(m+1,2),my_path(m,1),my_path(m+1,1));

    if f~=-inf
        my_sdns = [my_sdns;f];
    end
end



thresh = mean(my_sdns)/s;

end_control = [0;0];
    
end_nodes = (depth+1)^2-depth*2:(depth+1)^2;   
num_nodes = (depth+1)^2;

for m = 1:iter
    my_vec = my_path(end,:)-my_path(end-1,:);
    my_vec_p = my_vec'/norm(my_vec);
    my_vec_n = null(my_vec_p');

    Ix = my_path(end,2); Iy = my_path(end,1);

    
    [start_x,start_y] = get_pos_from_funnel(Ix,Iy,E(:,1),V,my_vec_p,my_vec_n,d_p,d_n);
    [end_x,end_y] =     get_pos_from_funnel(Ix,Iy,E(:,2),V,my_vec_p,my_vec_n,d_p,d_n);
    E(:,3) = -calculate_d_deriv(gradients,start_x,end_x,start_y,end_y);



    A = sparse(E(:,1),E(:,2),E(:,3),num_nodes,num_nodes);
    
    [d,pred] = shortest_paths(A,1,struct('algname','dag'));
    [min_val,min_ind] = min(d(end_nodes));
    
    sp = path_from_pred(pred,end_nodes(min_ind));
    


    switch track_type
        case 'invivo'
            if length(sp) == 1
                break;
            else
                current_sdn = d(sp(2));
                if -min_val/depth > thresh || -current_sdn > thresh
                    for i = 2:2
                        [current_x,current_y] = get_pos_from_funnel(Ix,Iy,sp(2),V,my_vec_p,my_vec_n,d_p,d_n);
                        my_path = [my_path;current_y,current_x];
                    end
                    my_sdns = [my_sdns;-current_sdn];
                    thresh = mean(my_sdns)/s;
                else
                    break;
                end
            end
        case 'motility'
            if length(sp) == 1

                end_control(1)=1;
                my_path = flipud(my_path);
                end_control = flipud(end_control);
                continue;
            else
                current_sdn = d(sp(2));
                if -min_val/depth > thresh || -current_sdn > thresh  %-log(current_sdn)/s > thresh
                    for i = 2:2%length(sp)
                        [current_x,current_y] = get_pos_from_funnel(Ix,Iy,sp(2),V,my_vec_p,my_vec_n,d_p,d_n);
                        my_path = [my_path;current_y,current_x];
                    end
                    my_sdns = [my_sdns;-current_sdn];
                    if end_control(2)==0
                        my_path = flipud(my_path);
                        end_control = flipud(end_control);
                    end
                else
                    if end_control(2)==1
                        break;
                    else
                        end_control(1)=1;
                        my_path = flipud(my_path);
                        end_control = flipud(end_control);
                    end
                end
                thresh = mean(my_sdns)/s;
            end
        otherwise
            error('Currently either motility and invivo tracking is supported\n');
    end
end

