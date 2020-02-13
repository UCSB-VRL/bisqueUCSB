function mixture1 = EMIterate(mixture, pixels)
% mixture1 = EMIterate(mixture, pixels)
%     perform the EM algorithm with a preassigned fixed order K
%
%     mixture: a mixture structure pre-initialized
%              mixture.K - order of the mixture
%              mixture.M - dimension of observations
%              mixture.cluster - an array of K cluster structure
%     pixels: a N x M observation matrix, each row is an observation vector
%
%     mixture1: converged result
%              mixture1.rissanen: MDL(K)
%

[N M] = size(pixels);
Lc = 1+M+0.5*M*(M+1);
epsilon = 0.01*Lc*log(N*M);
[mixture, llnew] = EStep(mixture, pixels);
while true
   llold = llnew;
   mixture = MStep(mixture, pixels);
   [mixture, llnew] = EStep(mixture, pixels);
   if (llnew-llold)<=epsilon
      break;
   end
end
mixture = rmfield(mixture, 'pnk');
mixture.rissanen = -llnew+0.5*(mixture.K*Lc-1)*log(N*M);
mixture.loglikelihood = llnew;
mixture1 = mixture;
