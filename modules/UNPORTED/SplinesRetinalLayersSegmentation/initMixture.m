function mixture = initMixture(pixels, K)

[N M] = size(pixels);
mixture.K=K;
mixture.M=M;
R = (N-1)*cov(pixels)/N;
mixture.Rmin = mean(diag(R))/1e5;
cluster(1).N=0;
cluster(1).pb = 1/K;
cluster(1).mu = pixels(1,:)';
cluster(1).R=R+mixture.Rmin*eye(mixture.M);
if K>1
   period = (N-1)/(K-1);
   for k=2:K
      cluster(k).N=0;
      cluster(k).pb = 1/K;
      cluster(k).mu = pixels(floor((k-1)*period+1),:)';
      cluster(k).R=R+mixture.Rmin*eye(mixture.M);
   end
end
mixture.cluster = cluster;
mixture = ClusterNormalize(mixture);

