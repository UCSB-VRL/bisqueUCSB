function out = get_contours(cc)
s = 1;
k = 2;
out = {};
while k <= size(cc, 2)
    m = cc(2, k - 1);
    out{s} = cc(:, k:(k+m-1));
    k = k + m + 1;
    s = s + 1;
end