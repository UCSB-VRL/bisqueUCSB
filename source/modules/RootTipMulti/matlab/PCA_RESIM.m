function [SIM] = PCA_RESIM(BV,U,COEFFS)
% create the simulated signal
SIM = (BV*COEFFS')';
for i = 1:size(SIM,1)
    SIM(i,:) = SIM(i,:) + U;
end
