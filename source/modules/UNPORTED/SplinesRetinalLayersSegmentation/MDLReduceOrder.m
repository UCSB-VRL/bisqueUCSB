function mixture1 = MDLReduceOrder(mixture, verbose)
% MDLReduceOrder     reduce the order of the mixture by 1 by combining the
%     two closest distance clusters 

   K=mixture.K;
   for k1=1:K
      for k2=k1+1:K
         dist = distance(mixture.cluster(k1), mixture.cluster(k2));
         if (k1==1 && k2==2) || (dist < mindist)
            mink1=k1; mink2=k2;
            mindist = dist;
         end
      end
   end
   if verbose
      disp(['combining cluster: ' int2str(mink1) ' and ' int2str(mink2)]);
   end
   cluster = mixture.cluster;
   cluster(mink1) = addCluster(cluster(mink1), cluster(mink2));
   cluster(mink2:(K-1)) = cluster((mink2+1):K);
   cluster = cluster(1:(K-1));
   mixture1 = mixture;
   mixture1.cluster = cluster;
   mixture1.K = K-1;
   mixture1 = ClusterNormalize(mixture1);

   function d = distance(cluster1, cluster2)
      cluster3 = addCluster(cluster1, cluster2);
      d = cluster1.N*cluster1.const + cluster2.N*cluster2.const-cluster3.N*cluster3.const;
   end

   function cluster3 = addCluster(cluster1, cluster2)
      wt1 = cluster1.N/(cluster1.N+cluster2.N);
      wt2 = 1-wt1;
      M = length(cluster1.mu);
      cluster3 = cluster1;
      cluster3.mu = wt1*cluster1.mu+wt2*cluster2.mu;
      cluster3.R = wt1*(cluster1.R+(cluster3.mu-cluster1.mu)*(cluster3.mu-cluster1.mu)') ...
                     + wt2*(cluster2.R+(cluster3.mu-cluster2.mu)*(cluster3.mu-cluster2.mu)');
      cluster3.invR = inv(cluster3.R);
      cluster3.pb = cluster1.pb+cluster2.pb;
      cluster3.N = cluster1.N+cluster2.N;
      cluster3.const = -(M*log(2*pi) +log(det(cluster3.R)))/2;
   end
end