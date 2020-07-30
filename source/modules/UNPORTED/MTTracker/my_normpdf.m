function out = my_normpdf(x, m, s)

out = exp(-0.5 * ((x - m) ./ s).^2) ./ (sqrt(2 * pi) .* s);
