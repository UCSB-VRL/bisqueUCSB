function [r,trace] = trellis(im, trace, d_p , s, n)
x = trace(:,2);
y = trace(:,1);
my_dist = trace(2:end,:) - trace(1:end-1,:);
my_dist = sqrt(sum(my_dist.^2,2)); 
t = [0;cumsum(my_dist)];
%tt = (0:3:t(end))';
tt = linspace(0,t(end),round(t(end)/d_p))';
if length(t) == 2
    pp_xx = spline(t,x);
    pp_yy = spline(t,y);
else
    sx1 = (x(2)-x(1))/(t(2)-t(1));
    sx2 = (x(end)-x(end-1))/(t(end)-t(end-1));
    sy1 = (y(2)-y(1))/(t(2)-t(1));
    sy2 = (y(end)-y(end-1))/(t(end)-t(end-1));
    pp_xx = spline(t,[sx1;x;sx2]);
    pp_yy = spline(t,[sy1;y;sy2]);
end
xx = ppval(pp_xx,tt);
yy = ppval(pp_yy,tt);
%xx_d = ppval_d(pp_xx,tt);
%yy_d = ppval_d(pp_yy,tt);
xx_d = ppval(mmppder(pp_xx),tt);
yy_d = ppval(mmppder(pp_yy),tt);
norm_d = sqrt(xx_d.^2+yy_d.^2);
nx = yy_d./norm_d;
ny = -xx_d./norm_d;
Vnx = interp1([0,1],[xx-n*nx,xx+n*nx]',linspace(0,1,s));
Vny = interp1([0,1],[yy-n*ny,yy+n*ny]',linspace(0,1,s));
r.vx = Vnx;
r.vy = Vny;
r.nx = nx;
r.ny = ny;
trace = [yy,xx];

