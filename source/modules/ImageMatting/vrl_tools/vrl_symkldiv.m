function kldiv = vrl_symkldiv(a,b)
%% Code to compute KL-Divergence
% USAGE: kldiv = vrl_symkldiv(a,b)
% a is a distribution
% b is a distribution
% THIS IS NOT FULLY TESTED CODE ... 

if(numel(a) ~= numel(b))
    error('Vector Lengths not the same');
end
if(sum(a)~=1)
    if(sum(a)==0), error('ALL a ZEROS'); end
    a = a./sum(a);
end

if(sum(b)~=1)
    if(sum(b)==0), error('ALL b ZEROS'); end
    b = b./sum(b);
end

a1 = a; b1 = b;
a1(a1==0) = eps;
kldiv1 = sum(a1.*log2(a1./(b1+eps)) );

a2 = a; b2 = b;
b2(b2==0) = eps;
kldiv2 = sum(b2.*log2(b2./(a2+eps)) );

kldiv = (kldiv1+kldiv2)/2;
kldiv(abs(kldiv)<.0001) = 0;