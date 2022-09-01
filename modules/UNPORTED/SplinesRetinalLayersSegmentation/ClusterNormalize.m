function mixture1=ClusterNormalize(mixture)

   s = sum([mixture.cluster(:).pb]);
   for k=1:mixture.K
      mixture.cluster(k).pb = mixture.cluster(k).pb/s;
      mixture.cluster(k).invR = inv(mixture.cluster(k).R);
      mixture.cluster(k).const = -(mixture.M*log(2*pi) +log(det(mixture.cluster(k).R)))/2;
   end
   mixture1=mixture;

end
