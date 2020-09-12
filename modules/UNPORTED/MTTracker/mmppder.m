function ppd=mmppder(pp)
%MMPPDER Cubic Spline Derivative Interpolation.
% PPD=MMPPDER(PP) returns the piecewise polynomial vector PPD
% describing the cubic spline derivative of the curve described by
% the piecewise polynomial in PP. 

[br,co,npy,nco]=unmkpp(pp);	   % take apart pp
sf=nco-1:-1:1;							% scale factors for differentiation
dco=sf(ones(npy,1),:).*co(:,1:nco-1);	% derivative coefficients
ppd=mkpp(br,dco); 					% build pp form for derivative