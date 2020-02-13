function [a,b,thresh] = get_fg_bg_model(r,Q,gradients,s,a,b)
N = length(r.nx);
c.data = [];
d.data = [];
for i=2:N
    for j=1:Q
        for k=1:Q
            f = calculate_obs(gradients,r.vx(j,i),r.vx(k,i-1),r.vy(j,i),r.vy(k,i-1));
            if f~=-inf
                if k==(Q+1)/2 && j==(Q+1)/2
                    c.data = [c.data;f];
                else
                    d.data = [d.data;f];
                end
            end
        end
    end
end
a.m = mean(a.data);
b.m = mean(b.data);
c.m = mean(c.data);
d.m = mean(d.data);
a.m = (a.m+9*c.m)/10;
b.m = (b.m+9*d.m)/10;
a.data = [a.data;c.data];
b.data = [b.data;d.data];
a.s = std(a.data);
b.s = std(b.data);
thresh = (a.m+b.m)/2;