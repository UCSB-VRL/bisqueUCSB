function [mixture, optmixture] = GaussianMixture(pixels, initK, finalK, verbose)
% [mixture, optmixture] = GaussianMixture(pixels, initK, finalK)
%        perform the EM algorithm to estimate the order, and
%        parameters of a Gaussian Mixture model for a given set of
%        observation.
%
%     pixels: a N x M matrix of observation vectors with each row being an
%        M-dimensional observation vector, totally N observations
%     initK: the initial number of clusters to start with and will be reduced
%        to find the optimal order or the desired order based on MDL
%     finalK: the desired final number of clusters for the model.
%        Estimate the optimal order if finalK == 0.
%     verbose: true/false, return clustering information if true
%
%     mixture: an array of mixture structures with each containing the
%        converged Gaussian mixture at a given order
%           mixture(l).K: order of the mixture
%           mixture(l).M: dimension of observation vectors
%           mixture(l).rissanen: converaged MDL(K) 
%           mixture(l).loglikelihood: ln( Prob{Y=y|K, theta*} )
%           mixture(l).cluster: an array of cluster structures with each
%              containing the converged cluster parameters
%                 mixture(l).cluster(k).pb: pi(k)=Prob(Xn=k|K, theta*)
%                 mixture(l).cluster(k).mu: mu(k), mean vector of the k-th cluster
%                 mixture(l).cluster(k).R: R(k), covariance matrix of the k-th cluser
%     optmixture: one of the element in the mixture array. 
%        If finalK > 0, optmixture = mixture(1) and is the mixture with order finalK. 
%        If finalK == 0, optmixture is the one in mixture with minimum MDL
%

if ~isnumeric(initK) || ~all(size(initK)==[1,1]) || initK<=0 || mod(initK,1)~=0
   error('GaussianMixture: initial number of clusters initK must be a positive integer');
end
if ~isnumeric(finalK) || ~all(size(finalK)==[1,1]) || finalK<0 || mod(finalK,1)~=0
   error('GaussianMixture: final number of clusters finalK must be a positive integer or zero');
end
if finalK > initK
   error('GaussianMixture: finalK cannot be greater than initK');
end
if ~isa(pixels,'double')
   pixels = double(pixels);
end
mtr = initMixture(pixels, initK);
mtr = EMIterate(mtr, pixels);
if verbose
   disp(sprintf('K: %d\t rissanen: %f', mtr.K, mtr.rissanen));
end
mixture(mtr.K-max(1,finalK)+1) = mtr;
while mtr.K > max(1, finalK)
   mtr = MDLReduceOrder(mtr, verbose);
   mtr = EMIterate(mtr, pixels);
   if verbose
      disp(sprintf('K: %d\t rissanen: %f', mtr.K, mtr.rissanen));
   end
   mixture(mtr.K-max(1,finalK)+1) = mtr;
end

if finalK>0
   optmixture = mixture(1);
else
   minriss = mixture(length(mixture)).rissanen; optl=length(mixture);
   for l=length(mixture)-1:-1:1
      if mixture(l).rissanen < minriss
         minriss = mixture(l).rissanen;
         optl = l;
      end
   end
   optmixture = mixture(optl);
end

   
