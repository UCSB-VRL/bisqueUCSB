function [a,b,thresh] = get_fg_bg_model_train(r,Q,gradients,s)
N = length(r.nx);
a.data = [];
b.data = [];
for i=2:N
    for j=1:Q
        for k=1:Q
            f = calculate_obs(gradients,r.vx(j,i),r.vx(k,i-1),r.vy(j,i),r.vy(k,i-1));
            if f~=-inf
                if k==(Q+1)/2 && j==(Q+1)/2
                    a.data = [a.data;f];
                else
                    b.data = [b.data;f];
                end
            end
        end
    end
end
a.m = mean(a.data);
a.s = std(a.data);
b.m = mean(b.data);
b.s = std(b.data);
thresh = (a.m+b.m)/s;