function [Vx_n,Vy_n,Vx_p,Vy_p,fd,sd,t] = calculate_directions(gxx,gxy,gyx,gyy,gx,gy,Ix,Iy)


Ix = round(Ix);
Iy = round(Iy);

rx = gx(Iy,Ix);
ry = gy(Iy,Ix);
rxx = gxx(Iy,Ix);
rxy = gxy(Iy,Ix);
ryx = gyx(Iy,Ix);
ryy = gyy(Iy,Ix);

% kernel_center_val=0.25;

% rx = interp2(gx,Ix,Iy,'spline');
% ry = interp2(gy,Ix,Iy, 'spline');
% rxx = interp2(gxx,Ix,Iy,'spline');
% rxy = interp2(gxy,Ix,Iy,'spline');
% ryx = interp2(gyx,Ix,Iy,'spline');
% ryy = interp2(gyy,Ix,Iy,'spline');

% rx = interp2(gx,Ix,Iy);
% ry = interp2(gy,Ix,Iy);
% rxx = interp2(gxx,Ix,Iy);
% rxy = interp2(gxy,Ix,Iy);
% ryx = interp2(gyx,Ix,Iy);
% ryy = interp2(gyy,Ix,Iy);


h = [rxx,rxy;
     ryx,ryy];

[v,d] = eig(h);
%[max_val,max_ind]=max(abs(diag(d)));
%[min_val,min_ind]=min(abs(diag(d)));
try
Vx_n = v(1,1);
Vy_n = v(2,1);
catch
h;
end
% [v,d] = eig(h);
% [max_val,max_ind]=max(abs(diag(d)));
% %[min_val,min_ind]=min(abs(diag(d)));
% Vx_n = v(1,max_ind);
% Vy_n = v(2,max_ind);


Vx_p = v(1,2);
Vy_p = v(2,2);

t = - (rx*Vx_n+ry*Vy_n)/(rxx*Vx_n^2+2*rxy*Vx_n*Vy_n+ryy*Vy_n^2+1e-6);

%t = - ([Vx_n,Vy_n]*[rx;ry])/( -2*kernel_center_val*Vx_n*Vx_n - 2*kernel_center_val*Vy_n*Vy_n + [Vx_n,Vy_n]*[rxx,rxy;ryx,ryy]*[Vx_n;Vy_n]   );

fd = [Vx_n,Vy_n]*[rx;ry];
sd = [Vx_n,Vy_n]*[rxx,rxy;ryx,ryy]*[Vx_n;Vy_n];

