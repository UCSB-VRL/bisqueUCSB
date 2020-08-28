function classes = SplitClasses(mixture)
% classes = SplitClasses(mixture)
% SplitClasses    splits the Gaussian mixture with K subclasses into K
%     Gaussian mixtures, each of order 1 containing each of the subclasses
%
%     mixture: a structure representing a Gaussian mixture of order
%        mixture.K
%
%     classes: an array of structures, with each representing a Gaussian 
%        mixture of order 1 consisting of one of the original subclasses
%

K=mixture.K;
for k=1:K
   classes(k) = mixture;
   classes(k).K=1;
   classes(k).cluster = mixture.cluster(k);
   classes(k).Rmin = NaN;
   classes(k).rissanen = NaN;
   classes(k).loglikelihood = NaN;
end
