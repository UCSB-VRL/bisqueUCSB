function out = path_conv(state_path,state_to_pos_x,state_to_pos_y,Q)

N = length(state_path);
out = zeros(N,2);


k = 1;

for i = 1:N

    if state_path(i) ~= Q

        if state_path(i) == Q-1

            break;
        else

            out(k,1) =  state_to_pos_y(state_path(i),i);
            out(k,2) =  state_to_pos_x(state_path(i),i);
            k = k+1;

        end

    end


end

out = out(1:k-1,:);