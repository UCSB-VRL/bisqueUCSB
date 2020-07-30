

function out = eval_2d_gmm(layer,x,y)


x_vec = x(:); y_vec = y(:);
feat = [x_vec,y_vec];


lik_score = zeros(size(feat,1),1);
for nn = 1:length(layer.cluster)
    cluster = layer.cluster(nn);
    mu = layer.cluster(nn).mu;
    R = layer.cluster(nn).R;
    dim = length(mu);
    pb  = layer.cluster(nn).pb;
    temp = feat-ones(size(feat,1),1)*mu.';
    temp2 = temp*inv(R);
    nll = sum(temp2.'.*temp.').';
    lik_score = lik_score + pb*1/sqrt((2*pi)^dim*det(R))*exp(-0.5*nll);
end


out = reshape(lik_score,size(x,1),size(x,2));