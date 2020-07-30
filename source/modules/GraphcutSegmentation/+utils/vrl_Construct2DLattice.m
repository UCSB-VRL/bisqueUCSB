function [edges,M] = vrl_Construct2DLattice(lattice_size,connectivity)

% edges = f_Construct2DLattice(lattice_size,connectivity)
% Construct the edge list for a regular lattice.
%
% INPUTS:
%   lattice_size = [r c] rows and cols in the lattice (width,height)
%   connectivity = scalar {0,1,2} specifying the neighborhood connectivity
%       0 = 4-conn, 1 = 8-conn, 2 = 16-conn
%
% OUTPUTs:
%   edges = [M x 2] list with each row specifying the two nodes sharing an
%       edge.
%   M = scalar number of edges
%
% Nhat Vu
% 02.23.2008

r = lattice_size(1);
c = lattice_size(2);

if nargin < 2,
    connectivity = 0;
end

if (connectivity > 2) || (connectivity < 0),
    error('Lattice connectivity must be 0, 1, or 2.');
end

% number of vertices (nodes)
N = r*c;

% case of 1D set of nodes
if (r==1) || (c==1),
    M = N-1;
    edgeMat = (1:N)';
    edges = [edgeMat(1:N-1) edgeMat(2:end)];
    return;
end
    
% define a few convenient terms
c1 = c-1;
r1 = r-1;

% number of edges to initialize edge list
M = r*c1 + r1*c;  % horizontal and vertical edges

if connectivity >= 1,
    M = M + 2*r1*c1;    % right and left diagonal edges
end

if connectivity == 2,
    M = M + 2*r1*(c1-1) + 2*(r1-1)*c1;  % 2 right and 2 left diagonals
end

edges = zeros(M,2);

% matrix with node indices
edgeMat = reshape(1:N,r,c);

% all cases have horizonal and vertical connections (so conn = 0 by default)
% horizontal connections
Mtemp = r*c1;
edges(1:Mtemp,:) = [reshape(edgeMat(:,1:c1),r*c1,1) reshape(edgeMat(:,2:c),r*c1,1)];

% vertical connections
edges(Mtemp+1:Mtemp+r1*c,:) = [reshape(edgeMat(1:r1,:),r1*c,1) reshape(edgeMat(2:r,:),r1*c,1)];
Mtemp = Mtemp + r1*c;

% if 8-connected
if connectivity >= 1,
    % right diagonal \
    edges(Mtemp+1:Mtemp+r1*c1,:) = [reshape(edgeMat(1:r1,1:c1),r1*c1,1) reshape(edgeMat(2:r,2:c),r1*c1,1)];
    Mtemp = Mtemp + r1*c1;
    
    % left diagonal /
    edges(Mtemp+1:Mtemp+r1*c1,:)  = [reshape(edgeMat(1:r1,2:c),r1*c1,1) reshape(edgeMat(2:r,1:c1),r1*c1,1)];
    Mtemp = Mtemp + r1*c1;
end

% if 16-connected
if connectivity == 2,
    % right upper diagonal
    edges(Mtemp+1:Mtemp+r1*(c1-1),:) = [reshape(edgeMat(1:r1,1:(c1-1)),r1*(c1-1),1) reshape(edgeMat(2:r,3:c),r1*(c1-1),1)];
    Mtemp = Mtemp + r1*(c1-1);
    
    % right lower diagonal
    edges(Mtemp+1:Mtemp+(r1-1)*c1,:) = [reshape(edgeMat(1:(r1-1),1:c1),(r1-1)*c1,1) reshape(edgeMat(3:r,2:c),(r1-1)*c1,1)];
    Mtemp = Mtemp + (r1-1)*c1;
    
    % left upper diagonal
    edges(Mtemp+1:Mtemp+r1*(c1-1),:) = [reshape(edgeMat(1:r1,3:c),r1*(c1-1),1) reshape(edgeMat(2:r,1:(c1-1)),r1*(c1-1),1)];
    Mtemp = Mtemp + r1*(c1-1);
    
    % left lower diagonal
    edges(Mtemp+1:Mtemp+(r1-1)*c1,:) = [reshape(edgeMat(1:(r1-1),2:c),(r1-1)*c1,1) reshape(edgeMat(3:r,1:c1),(r1-1)*c1,1)];
end