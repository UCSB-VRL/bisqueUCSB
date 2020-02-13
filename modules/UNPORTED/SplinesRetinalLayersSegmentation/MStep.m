function mixture1 = MStep(mixture, pixels)
% MStep     perform the M-step of the EM algorithm
%        from the pnk calculated in the E-step, update parameters of each cluster
%

   for k=1:mixture.K
      mixture.cluster(k).N = sum(mixture.pnk(:,k));
      mixture.cluster(k).pb = mixture.cluster(k).N;
      mixture.cluster(k).mu = (pixels' * mixture.pnk(:,k))/mixture.cluster(k).N;
      for r=1:mixture.M
         for s=r:mixture.M
            mixture.cluster(k).R(r,s) = ((pixels(:,r)-mixture.cluster(k).mu(r))' ...
                           * ((pixels(:,s)-mixture.cluster(k).mu(s)).*mixture.pnk(:,k))) ...
                           /mixture.cluster(k).N;
            if r~=s
               mixture.cluster(k).R(s,r) = mixture.cluster(k).R(r,s);
            end
         end
      end
      mixture.cluster(k).R = mixture.cluster(k).R+mixture.Rmin*eye(mixture.M);
   end
   mixture1=ClusterNormalize(mixture);
end

