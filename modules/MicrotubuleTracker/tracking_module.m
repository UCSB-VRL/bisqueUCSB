function [my_path,a,b,thresh,pred_path,result_flag] = tracking_module(im,gradients,my_path,a,b,my_thresh);
mt_track_config = xml_load('mt_track_config.xml');
NL = mt_track_config.NL;
d_n = mt_track_config.d_n;
d_p = mt_track_config.d_p;
S = mt_track_config.S;
thresh_s = 2;
d_p=1;
Q = S+2;
k=1;
p2 = [mk_stochastic(my_normpdf(1:S, round(S/2), (S-round(S/2))))*k,0,1-k];
tr = mt_track_config.tr;
[r,my_path] = trellis(my_path,d_p,S,NL);
B=calculate_obs_prob2(r,S,gradients,a,b,NL,d_p);
[state_path,delta,psi] = my_viterbi_path(p2,r,B,tr);
my_path_end = my_path(1,:);
I = find(state_path~=S+1&state_path~=S+2);
% a1=a;
% while numel(I) < 2
%     a1=a;
%     a1.m=2*a.m/3;
%     [r,my_path] = trellis(my_path,d_p,S,NL);
%     B=calculate_obs_prob2(r,S,gradients,a1,b,NL,d_p);
%     [state_path,delta,psi] = my_viterbi_path(p2,r,B,tr);
%     my_path_end = my_path(1,:);
%     I = find(state_path~=S+1&state_path~=S+2);
% end
r.vx = r.vx(:,I);
r.vy = r.vy(:,I);
r.nx = r.nx(I);
r.ny = r.ny(I);
my_path = my_path(I,:);
B = B(:,I);

if growthVar==1
    depth = 3; bf = 3;
    thresh = my_thresh;
    [E,V] = create_funnel(depth,bf,S);
    end_control = [1,0];
    iterations=10;
    thresh=my_thresh;
    result_flag =1;
    for i=1:iterations
        if ~ end_control(1)
            Ix_end = my_path(1,2); Iy_end = my_path(1,1);
            [vec_p_end,vec_n_end] = my_vec_p_n(my_path(1,:),my_path(2,:));
            sp =  mt_funnel(zeros(Q,1),Ix_end,Iy_end,E,V,vec_p_end,d_p,...
                vec_n_end,d_n,gradients,a,thresh,depth,S);
            if isempty(sp)
                B_end=[];
                end_control(1)=1;
            else
                [current_x,current_y] = get_pos_from_funnel(Ix_end,Iy_end,sp(2),V,vec_p_end,vec_n_end,d_p,d_n);
                [my_vec_p,my_vec_n] = my_vec_p_n([current_y,current_x],[Iy_end,Ix_end]);
                Ix_end_new = current_x;
                Iy_end_new = current_y;
                my_path = [Iy_end_new,Ix_end_new;my_path];
                r.vx = [linspace(Ix_end_new-my_vec_n(2)*NL,Ix_end_new+my_vec_n(2)*NL,S)',r.vx];
                r.vy = [linspace(Iy_end_new-my_vec_n(1)*NL,Iy_end_new+my_vec_n(1)*NL,S)',r.vy];
                r.nx = [my_vec_n(2);r.nx];
                r.ny = [my_vec_n(1);r.ny];
                B_end = [calculate_obs_prob_ext(r,S,gradients,a,b,d_p,NL,'end2'),...
                    calculate_obs_prob_ext(r,S,gradients,a,b,d_p,NL,'end')];
            end
        else
            B_end = [];
        end
        if ~ end_control(2)
            Ix_tip = my_path(end,2); Iy_tip = my_path(end,1);
            %
            if size(my_path,1) <=1
                result_flag = 0;
                disp ('lost the contour: reinitialize.'); 
                continue; 
            end
            %
            [vec_p_tip,vec_n_tip] = my_vec_p_n(my_path(end,:),my_path(end-1,:));
            sp =  mt_funnel(delta(:,end),Ix_tip,Iy_tip,E,V,vec_p_tip,d_p,...
                vec_n_tip,d_n,gradients,a,thresh,depth,S);
            if isempty(sp)
                end_control(2) = 1;
                B_tip=[];
            else
                [current_x,current_y] = get_pos_from_funnel(Ix_tip,Iy_tip,sp(2),V,vec_p_tip,vec_n_tip,d_p,d_n);
                [my_vec_p,my_vec_n] = my_vec_p_n([current_y,current_x],[Iy_tip,Ix_tip]);
                Ix_tip_new = current_x;
                Iy_tip_new = current_y;
                my_path = [my_path;Iy_tip_new,Ix_tip_new];
                r.vx = [r.vx,linspace(Ix_tip_new-my_vec_n(2)*NL,Ix_tip_new+my_vec_n(2)*NL,S)'];
                r.vy = [r.vy,linspace(Iy_tip_new-my_vec_n(1)*NL,Iy_tip_new+my_vec_n(1)*NL,S)'];
                r.nx = [r.nx;my_vec_n(2)];
                r.ny = [r.ny;my_vec_n(1)];
                B_tip = calculate_obs_prob_ext(r,S,gradients,a,b,d_p,NL,'tip');
            end
        else
            B_tip=[];
        end
        if ~isempty(B_end)
            B = [B_end,B(:,2:end),B_tip];
        else
            B = [B,B_tip];
        end


        [state_path,delta,psi] = my_viterbi_path(p2,r,B,tr);

        if state_path(end) == S+1
            end_control(2) = 1;
        end

        if state_path(1) == S+2
            end_control(1) = 1;
        end

        if end_control(1) && end_control(2)
            break;
        end
    end
end    
    %
if result_flag ~= 0
    my_path = path_conv(state_path,r.vx,r.vy,Q);
    [r,pred_path] = trellis(my_path , d_p , S , NL );
    pred_path = smooth_path(pred_path);
    [r,pred_path] = trellis(pred_path , d_p , S , NL );
    [a,b,thresh] = get_fg_bg_model(r,S,gradients,thresh_s,a,b);
else
    my_path=[];
    pred_path=[];
end

    
%
% [a,b,thresh] = get_fg_bg_model_train(r,S,gradients,thresh_s);

