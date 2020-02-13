function trace_i = trace_interp(trace,d)
dist = trace(1:end-1,:)-trace(2:end,:);
dist = sqrt(sum(dist.^2,2));
dist = [0;cumsum(dist)];
%dist_i = 0:d:dist(end);
dist_i = linspace(0,dist(end),round(dist(end)/d)+1);
trace_i = [ interp1(dist,trace(:,1),dist_i)', interp1(dist,trace(:,2) , dist_i)' ] ;
