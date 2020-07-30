function out = my_interp2(f,start_x,end_x,start_y,end_y,n)

if floor(start_y) < 1        || floor(end_y) < 1 || ...
        floor(start_x) < 1        || floor(end_x) < 1 || ...
        ceil(start_y) > size(f,1) || ceil(end_y) > size(f,1) || ...
        ceil(start_x) > size(f,2) || ceil(end_x) > size(f,2)
    out = NaN;
    return;
end


x = linspace(start_x,end_x,n);
y = linspace(start_y,end_y,n);

fx = floor(x); fy = floor(y);

cx = ceil(x); cy = ceil(y);

siz = size(f);


fx2 = x-fx;
fy2 = y-fy;

b1 = f(fy+(fx-1)*siz(1));
k2 = f(fy+(cx-1)*siz(1));
k3 = f(cy+(fx-1)*siz(1));
k4 = f(cy+(cx-1)*siz(1));

b2 = k2 - b1;
b3 = k3 - b1;
b4 = b1 - k3 - k2 + k4;

out = sum([ones(1,n);fx2;fy2;fx2.*fy2].*[b1;b2;b3;b4])';