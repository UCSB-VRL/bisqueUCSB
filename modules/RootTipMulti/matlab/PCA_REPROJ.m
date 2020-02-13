function [SIM COEFFS ERR] = PCA_REPROJ(M,BV,U)
% offset
for i = 1:size(M,1)
    M(i,:) = M(i,:) - U;                                % subtract the mean
end
% offset

% coeffs
COEFFS = M*BV;                                          % project to get the coeffs
% coeffs

% create the simulated signal
SIM = (BV*COEFFS')';                                    % simluate the signal
for i = 1:size(SIM,1)           
    SIM(i,:) = SIM(i,:) + U;                            % backoff to zero
end
% create the simulated signal


% offset
for i = 1:size(M,1)
    M(i,:) = M(i,:) + U;                                % subtract the mean
end
% offset

% error term
ERR = sum((SIM - M).^2,2).^.5;                          % vector perp to subspace
% error term
