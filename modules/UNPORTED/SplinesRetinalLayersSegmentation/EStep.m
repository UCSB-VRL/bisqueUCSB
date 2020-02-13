function [mixture1 likelihood] = EStep(mixture, pixels)
% EStep     perform the E-step of the EM algorithm
%        1) calculate pnk = Prob(Xn=k|Yn=yn, theta)
%        2) calculate likelihood = log ( prob(Y=y|theta) )

   [N M] = size(pixels);
   K=mixture.K;
   pnk=zeros(N,K);            
   for k=1:K
      Y1=pixels-ones(N,1)*mixture.cluster(k).mu';
      Y2=-0.5*Y1*mixture.cluster(k).invR;
      pnk(:,k) = dot(Y1,Y2,2)+mixture.cluster(k).const;
   end
   llmax=max(pnk,[],2);
   pnk =exp( pnk-llmax*ones(1,K) );
   pnk = pnk.*(ones(N,1)*[mixture.cluster(:).pb]);
   ss = sum(pnk,2);
   likelihood = sum(log(ss)+llmax);
   pnk = pnk./(ss*ones(1,K));
   mixture1 = mixture;
   mixture1.pnk = pnk;
   
   
%    function ll = loglike(yn, cluster)
%       Y = yn-cluster.mu;
%       ll = -0.5*Y'*cluster.invR*Y+cluster.const;
%    end
% 
end