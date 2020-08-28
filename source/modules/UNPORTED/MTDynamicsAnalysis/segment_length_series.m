function [start_end_times,labels] = segment_length_series(time_length_series,params)

N = size(time_length_series,1);

length_series = time_length_series(:,2);
time_series = time_length_series(:,1);

slopes = zeros(N);
cost = zeros(N);
segment_info = zeros(N);

for i = 1:N
    for j = i:N
        x=(i:j)';
        y=length_series(x);
        t=time_series(x)/60;
        if length(t)>1
            p = polyfit(t,y,1);
            yp = polyval(p,t);
            temp = 0;
            for k = 1:length(t)-1
                m = (y(k+1)-y(k))/(t(k+1)-t(k))-(yp(k+1)-yp(k))/(t(k+1)-t(k));
                b = y(k)-yp(k) - m * t(k);
                temp = temp + 1/3*( m^2*(t(k+1)^3-t(k)^3)   +...
                    3*m*(t(k+1)^2-t(k)^2)*b + ...
                    3*(t(k+1)-t(k))*b^2 );
            end
            cost(i,j) = temp;
            s = p(1);
            slopes(i,j) = s;
            dt = t(end)-t(1);
            if s>params.growth_rate
                if s*dt < params.growth_len
                    cost(i,j) = inf;
                end
                segment_info(i,j) = 'g';
            elseif s<params.short_rate
                if s*dt > params.short_len
                    cost(i,j) = inf;
                end
                segment_info(i,j) = 's';
            else
                if dt < params.atten_dur/60 
                    cost(i,j) = inf;
                end
                segment_info(i,j) = 'a';
            end
        else
            cost(i,j) = inf;
        end
    end
end
F = zeros(N,N);
Q = zeros(N,N);
prev_seg_id = zeros(N,N);
F(:,1) = cost(1,:)';
Q(:,1) = 1;
prev_seg_id(:,1) = segment_info(1,:)';
for k = 2:N
    for j = 1:N
        if j<k
            F(j,k) = inf;
        else
            regular_cost = cost(1:j,j);
            for m = 1:length(regular_cost)
                if prev_seg_id(m,k-1) == segment_info(m,j);
                    regular_cost(m) = inf;
                end
            end
            [F(j,k),Q(j,k)] = min(F(1:j,k-1)+regular_cost);
            prev_seg_id(j,k) = segment_info(Q(j,k),j);
        end
    end
end
[min_val,K] = min(F(end,:));


start_end_times = zeros(K,2);
labels = cell(K,1);
slope_seq = zeros(K,1);
start_end_times(K,1) = Q(N,K);
start_end_times(K,2) = N;
for i = K-1:-1:1
    start_end_times(i,2) = start_end_times(i+1,1);
    start_end_times(i,1) = Q(start_end_times(i+1,1),i);
end
for i = 1:K
    labels{i} = char(segment_info(start_end_times(i,1),start_end_times(i,2)));
    slope_seq(i) = slopes(start_end_times(i,1),start_end_times(i,2));
end