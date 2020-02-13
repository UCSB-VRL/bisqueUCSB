function out = my_normpdf(x, mean, sigma)

out = exp(-0.5*((x-mean)./sigma).^2)./(sqrt(2*pi).*sigma);
