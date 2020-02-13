function dSP=extract_graph_distance(E)

% ============= Input data validation ==================
if nargin<1,
  error('There is no input data!')
end
[m,n,E] = grValidation(E); % E data validation

% ================ Initial values ===============
dSP=ones(n)*inf; % initial distances
dSP((E(:,2)-1)*n+E(:,1))=E(:,3);

% ========= The main cycle of Floyd-Warshall algorithm =========
for j=1:n,
  i=setdiff((1:n),j);
  dSP(i,i)=min(dSP(i,i),repmat(dSP(i,j),1,n-1)+repmat(dSP(j,i),n-1,1));
end