function out_path = smooth_path(my_path)
N = 5;
if size(my_path,1) >= N
    w = gausswin(N);
    w = w/sum(w);
    temp=filter(w,1,my_path);
    out_path = [my_path(1:(N-1)/2,:);temp(N:end,:);my_path(end-(N-1)/2+1:end,:)];
else
    out_path = my_path;
end

