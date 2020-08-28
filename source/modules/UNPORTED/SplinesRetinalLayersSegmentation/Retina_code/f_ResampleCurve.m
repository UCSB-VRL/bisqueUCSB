function xy_new = f_ResampleCurve(xy,ds)

% xy = [Nx2]
nc = size(xy,1);

% make xy into real and imaginary vector z for ease of computation
z = xy(:,1)+j*xy(:,2);

% elements of dist represent chord length
dist = abs(diff(z));

% reparameterize arc length
s = zeros(1,nc);
for k = 1:nc-1;
    s(k+1) = sum(dist(1:k));
end

% total length
L_total = s(end);

% estimate closest number of points with ds spacing
n_pts = ceil(L_total/ds);

% use cubic-spline to interpolate s
xsamp = [0:L_total/(n_pts):L_total];
xy_new = interp1(s,xy,xsamp,'cubic');