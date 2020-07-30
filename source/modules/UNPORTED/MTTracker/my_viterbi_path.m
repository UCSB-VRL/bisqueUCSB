function [state_path,delta,psi] = my_viterbi_path(p,r,B,tr)
T=size(B,3)+1;
N=size(B,1);
M = N-2;
delta = zeros(N,T);
psi = zeros(N,T);
state_path = zeros(1,T);

delta(:,1)=log(p(:));


alpha = 1/T;
beta = 1e-2;
%tr = [tr*(1-alpha) alpha*ones(M,1);zeros(1,M),1];
%tr = [tr,zeros(M+1,1);[mk_stochastic([my_normpdf(1:M, round(M/2), (M-round(M/2))), 0])*(1-beta), beta ] ];




tr = [ tr*(1-alpha), zeros(M,1),alpha*ones(M,1);[(1-beta)/M*ones(1,M);zeros(1,M)],[beta,0;0,1]];


for t = 2:T
    for i=1:N
        [delta(i,t),psi(i,t)]=max(delta(:,t-1)+log(tr(:,i))+ log(B(:,i,t-1))  );
    end
end

[lik , state_path(T)] = max(delta(:,T));
for t=T-1:-1:1
    state_path(t) = psi(state_path(t+1),t+1);
end

