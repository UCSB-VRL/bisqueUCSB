function [a,b,thresh,my_path,pred_path] = mt_track(im,gradients,my_path,a,b,my_thresh,track_type)


mt_track_config = xml_load('mt_track_config.xml');
%mt_track_config = xml_parseany(fileread('mt_track_config.xml'));

NL = mt_track_config.NL;     % length of normal
d_n = mt_track_config.d_n;
d_p = mt_track_config.d_p;
S = mt_track_config.S;
thresh_s = 2;
Q = S+2;

switch track_type
    case 'trackMotility'
        p2 = [ones(1,S),0,1]/(S+1);
    case 'trackinvivo'
        k=1;
        p2 = [mk_stochastic(my_normpdf(1:S, round(S/2), (S-round(S/2))))*k,1-k,0];
        %p2 = [ones(1,S)/S*k,0,1-k];
end

tr = mt_track_config.tr;

[r,my_path] = trellis(im, my_path , d_p , S , NL );
B = calculate_obs_prob(r,gradients,a,b);
[state_path,delta,psi] = my_viterbi_path(p2,r,B,tr);

my_path_end = my_path(1,:);


I = find(state_path~=S+1&state_path~=S+2);
r.vx = r.vx(:,I);
r.vy = r.vy(:,I);
r.nx = r.nx(I);
r.ny = r.ny(I);
my_path = my_path(I,:);
B = B(:,:,I(1:end-1));




depth = 3; bf = 3;
thresh = my_thresh;
[E,V] = create_funnel(depth,bf,S);

switch track_type
    case 'trackMotility'
        end_control = [0,0];
    case 'trackinvivo'
        end_control = [1,0];
end


for iter = 1:10
    if ~end_control(1)

        Ix_end = my_path(1,2);   Iy_end = my_path(1,1);

        [vec_p_end,vec_n_end] = calculate_vec_p_n(my_path(1,:),my_path(2,:));

        sp =  mt_funnel(zeros(Q,1),Ix_end,Iy_end,E,V,vec_p_end,d_p,...
            vec_n_end,d_n,gradients,a,thresh,depth,S);

        if isempty(sp)
            end_control(1) = 1;
            B_end = [];
        else
            [current_x,current_y] = get_pos_from_funnel(Ix_end,Iy_end,sp(2),V,vec_p_end,vec_n_end,d_p,d_n);

            [my_vec_p,my_vec_n] = calculate_vec_p_n([current_y,current_x],[Iy_end,Ix_end]);

            %Ix_end_new = Ix_end + d_p*my_vec_p(2);
            %Iy_end_new = Iy_end + d_p*my_vec_p(1);

            Ix_end_new = current_x;
            Iy_end_new = current_y;


            my_path = [Iy_end_new,Ix_end_new;my_path];

            r.vx = [linspace(Ix_end_new-my_vec_n(2)*NL,Ix_end_new+my_vec_n(2)*NL,S)',r.vx];
            r.vy = [linspace(Iy_end_new-my_vec_n(1)*NL,Iy_end_new+my_vec_n(1)*NL,S)',r.vy];

            r.nx = [my_vec_n(2);r.nx];
            r.ny = [my_vec_n(1);r.ny];

            r2.vx = r.vx(:,1:2);
            r2.vy = r.vy(:,1:2);
            r2.nx = r.nx(1:2);
            r2.ny = r.ny(1:2);

            B_end = calculate_obs_prob(r2,gradients,a,b);

            %B_end = [calculate_obs_prob_ext(r,S,gradients,a,b,d_p,NL,'end2'),...
            %    calculate_obs_prob_ext(r,S,gradients,a,b,d_p,NL,'end')];
        end
    else
        B_end = [];
    end
    if ~end_control(2)
        Ix_tip = my_path(end,2); Iy_tip = my_path(end,1);

        [vec_p_tip,vec_n_tip] = calculate_vec_p_n(my_path(end,:),my_path(end-1,:));


        %sp =  mt_funnel(zeros(Q,1),Ix_tip,Iy_tip,E,V,vec_p_tip,d_p,...
        %    vec_n_tip,d_n,gradients,a,thresh,depth,S);


        sp =  mt_funnel(delta(:,end),Ix_tip,Iy_tip,E,V,vec_p_tip,d_p,...
            vec_n_tip,d_n,gradients,a,thresh,depth,S);

        if isempty(sp)
            end_control(2) = 1;
            B_tip=[];
        else
            [current_x,current_y] = get_pos_from_funnel(Ix_tip,Iy_tip,sp(2),V,vec_p_tip,vec_n_tip,d_p,d_n);

            [my_vec_p,my_vec_n] = calculate_vec_p_n([current_y,current_x],[Iy_tip,Ix_tip]);

            %Ix_tip_new = Ix_tip + d_p*my_vec_p(2);
            %Iy_tip_new = Iy_tip + d_p*my_vec_p(1);

            Ix_tip_new = current_x;
            Iy_tip_new = current_y;


            my_path = [my_path;Iy_tip_new,Ix_tip_new];

            r.vx = [r.vx,linspace(Ix_tip_new-my_vec_n(2)*NL,Ix_tip_new+my_vec_n(2)*NL,S)'];
            r.vy = [r.vy,linspace(Iy_tip_new-my_vec_n(1)*NL,Iy_tip_new+my_vec_n(1)*NL,S)'];

            r.nx = [r.nx;my_vec_n(2)];
            r.ny = [r.ny;my_vec_n(1)];

            r2.vx = r.vx(:,end-1:end);
            r2.vy = r.vy(:,end-1:end);
            r2.nx = r.nx(end-1:end);
            r2.ny = r.ny(end-1:end);




            B_tip = calculate_obs_prob(r2,gradients,a,b);

        end
    else
        B_tip=[];
    end


    B = cat(3, B_end, B);
    B = cat(3, B, B_tip);
    

    [state_path,delta,psi] = my_viterbi_path(p2,r,B,tr);


    if state_path(end) == S+2
        end_control(2) = 1;
    end

    if state_path(1) == S+1
        end_control(1) = 1;
    end

    if end_control(1) && end_control(2)
        break;
    end


end


my_path = path_conv(state_path,r.vx,r.vy,Q);
[r,pred_path] = trellis(im, my_path , d_p , S , NL );
%[a,b,thresh] = get_fg_bg_model(r,S,gradients,thresh_s,a,b);
if strcmp(track_type,'trackinvivo')
    pred_path(1,:) = my_path_end;
end
pred_path = smooth_path(pred_path);



% imshow(im,'init','fit'); hold on; plot(my_path(:,2),my_path(:,1));
% hold off;





