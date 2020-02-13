function [state_path,delta,psi] = my_viterbi_path(p,r,B,tr)%p-state prior,r-info about trellis,B-obs Prob,tr-transition

T=size(B,2);
N=size(B,1);
M = sqrt(N-2);
delta = zeros(M+2,T);
psi = zeros(M+2,T);
state_path = zeros(1,T);

delta(:,1)=log(p(:));
alpha = 1/(T);
beta = 1e-2;
tr = [tr*(1-alpha) alpha*ones(M,1);zeros(1,M),1];
tr = [tr,zeros(M+1,1);[mk_stochastic([my_normpdf(1:M, round(M/2), (M-round(M/2))), 0])*(1-beta), beta ] ];

for t = 2:T
    for i=1:M
        [delta(i,t),psi(i,t)] = max(delta(:,t-1)+log(tr(:,i))+ log([ B(((i-1)*M+1):(i*M),t); 0 ; B(end,t)]));
    end
    [delta(M+1,t),psi(M+1,t)] = max(delta(:,t-1)+log(tr(:,M+1)));
    delta(M+1,t) = delta(M+1,t)+log(B(end-1,t));
    [delta(M+2,t),psi(M+2,t)] = max(delta(:,t-1)+log(tr(:,M+2)));
    delta(M+2,t) = delta(M+2,t)+log(B(end,t));
end

[lik , state_path(T)] = max(delta(:,T));
for t=T-1:-1:1
    state_path(t) = psi(state_path(t+1),t+1);
end
