function [a,b,thresh] = get_fg_bg_model(r,Q,gradients,s,a,b)
N = length(r.nx);
if isempty(a) || isempty(b)
    a.data = [];
    b.data = [];
end
for i=2:N
    for j=1:Q
        for k=1:Q
            f = calculate_d_deriv(gradients,r.vx(j,i),r.vx(k,i-1),r.vy(j,i),r.vy(k,i-1));
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

%[a.m,a.s] = normfit(a.data);
%[b.m,b.s] = normfit(b.data);

a.m = mean(a.data);
a.s = std(a.data);

b.m = mean(b.data);
b.s = std(b.data);



%figure; hist(fg_data,30);
%figure; hist(bg_data,30);
%b = expfit(bg_data);

%P = 0.95;
%p = 2.5e-2;
%b = b*log(1-P)/log(p);

%b = b/2;

%a=b*2;
%x = linspace(0,max(bg_data),1000);
%figure; plot(x,exp(-x/b)/b,x,1-exp(-x/a)/a);
%thresh = (a.m)/s;
thresh = (a.m+b.m)/2;


