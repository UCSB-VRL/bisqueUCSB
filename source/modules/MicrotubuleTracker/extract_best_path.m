function sp=extract_best_path(E,dSP,s,t)

% ============= Input data validation ==================
if nargin<1,
  error('There are no input data!')
end
[m,n,E] = grValidation(E); % E data validation

sp=[];
if (~(s==round(s)))|(~(t==round(t)))|(s<1)|(s>n)|(t<1)|(t>n),
  error(['s and t must be integer from 1 to ' num2str(n)])
end
if isinf(dSP(s,t)), % t is not accessible from s
  return
end
dSP1=dSP;
dSP1(1:n+1:n^2)=0; % modified dSP
l=ones(m,1); % label for each arrow
sp=t; % final vertex
while ~(sp(1)==s),
  nv=find((E(:,2)==sp(1))&l); % all labeled arrows to sp(1)
  vnv=abs((dSP1(s,sp(1))-dSP1(s,E(nv,1)))'-E(nv,3))<eps*1e8; % valided arrows
  l(nv(~vnv))=0; % labels of not valided arrows
  if all(~vnv), % invalided arrows
    l(find((E(:,1)==sp(1))&(E(:,2)==sp(2))))=0; 
    sp=sp(2:end); % one step back
  else
    nv=nv(vnv); % rested vaded arrows
    sp=[E(nv(1),1) sp]; % add one vertex to shortest path
  end
end
return