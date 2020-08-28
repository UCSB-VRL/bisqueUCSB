function [SIM U BV L COEFFS ERR] = PCA_FIT(M,COM)
U = mean(M,1);
for i = 1:size(M,1)
    M(i,:) = M(i,:) - U;
end
%COV = ((size(M,1)-1)^-1)*M'*M;
COV = cov(M);
[BV L] = eigs(double(COV),COM);
COEFFS = M*BV;
% create the simulated signal
SIM = (BV*COEFFS')';
for i = 1:size(SIM,1)
    SIM(i,:) = SIM(i,:) + U;
end
ERR = sum((SIM - M).^2,2).^.5;