function [edges,M] = vrl_Construct3DLattice(lattice_size,connectivity)

% edges = f_Construct3DLattice(lattice_size,connectivity)
% Construct the edge list for a regular 3D lattice.
%
% INPUTS:
%   lattice_size = [r c p] rows, cols, and planes in the lattice (width,height,depth)
%   connectivity = scalar {0,1} specifying the neighborhood connectivity
%       0 = 6-conn, 1 = 26-conn
%
% OUTPUTs:
%   edges = [M x 2] list with each row specifying the two nodes sharing an
%       edge.
%   M = scalar number of edges
%
% Nhat Vu
% 04.30.2008

if numel(lattice_size) ~= 3,
    error('f_Construct3DLattice: Lattice size must have three components [width height depth]');
end

r = lattice_size(1);
c = lattice_size(2);
p = lattice_size(3);

% case of 1D set of nodes
if (r==1) || (c==1) || (p==1),
    error('f_Construct3DLattice: Use the 2D version instead.');
end

% define a few convenient terms
c1 = c-1;
r1 = r-1;
p1 = p-1;

if nargin < 2,
    connectivity = 0;
end
if (connectivity > 1) || (connectivity < 0),
    error('f_Construct3DLattice: Lattice connectivity must be 0 or 1.');
end

% number of vertices (nodes)
N = r*c*p;

% number of edges to initialize edge list
M = r*c*p1 + r*c1*p + r1*c*p;  % horizontal, vertical, and inplane edges

if connectivity >= 1,
    M = M + 2*r1*c1*p + 2*r1*c*p1 + 2*r*c1*p1 + 4*r1*c1*p1;     % diagonal edges
end
edges = zeros(M,2);

% matrix with node indices shaped into lattice
edgeMat = reshape(1:N,r,c,p);

% all cases have horizonal, vertical, and inplane connections (so conn = 0 by default)
% inplane connections
Mtemp = r*c*p1;
edges(1:Mtemp,:) = [reshape(edgeMat(:,:,1:p1),r*c*p1,1) reshape(edgeMat(:,:,2:p),r*c*p1,1)];

% horizonal connections
edges(Mtemp+1:Mtemp+r*c1*p,:) = [reshape(edgeMat(:,1:c1,:),r*c1*p,1) reshape(edgeMat(:,2:c,:),r*c1*p,1)];
Mtemp = Mtemp + r*c1*p;

% vertical connections
edges(Mtemp+1:Mtemp+r1*c*p,:) = [reshape(edgeMat(1:r1,:,:),r1*c*p,1) reshape(edgeMat(2:r,:,:),r1*c*p,1)];

% if 26-connected
if connectivity >= 1,
    Mtemp = Mtemp + r1*c*p;
    %-----------------------------
    % r,c right diagonal \
    edges(Mtemp+1:Mtemp+r1*c1*p,:) = [reshape(edgeMat(1:r1,1:c1,:),r1*c1*p,1) reshape(edgeMat(2:r,2:c,:),r1*c1*p,1)];
    Mtemp = Mtemp + r1*c1*p;
    
    % r,c left diagonal /
    edges(Mtemp+1:Mtemp+r1*c1*p,:) = [reshape(edgeMat(1:r1,2:c,:),r1*c1*p,1) reshape(edgeMat(2:r,1:c1,:),r1*c1*p,1)];
    Mtemp = Mtemp + r1*c1*p;
    %------------------------------
    % r,p right diagonal \
    edges(Mtemp+1:Mtemp+r1*c*p1,:) = [reshape(edgeMat(1:r1,:,1:p1),r1*c*p1,1) reshape(edgeMat(2:r,:,2:p),r1*c*p1,1)];
    Mtemp = Mtemp + r1*c*p1;
    
    % r,p left diagonal /
    edges(Mtemp+1:Mtemp+r1*c*p1,:) = [reshape(edgeMat(1:r1,:,2:p),r1*c*p1,1) reshape(edgeMat(2:r,:,1:p1),r1*c*p1,1)];
    Mtemp = Mtemp + r1*c*p1;
    %------------------------------
    % c,p right diagonal \
    edges(Mtemp+1:Mtemp+r*c1*p1,:) = [reshape(edgeMat(:,1:c1,1:p1),r*c1*p1,1) reshape(edgeMat(:,2:c,2:p),r*c1*p1,1)];
    Mtemp = Mtemp + r*c1*p1;
    
    % c,p left diagonal /
    edges(Mtemp+1:Mtemp+r*c1*p1,:) = [reshape(edgeMat(:,1:c1,2:p),r*c1*p1,1) reshape(edgeMat(:,2:c,1:p1),r*c1*p1,1)];
    Mtemp = Mtemp + r*c1*p1;
    %------------------------------
    % top-left to bottom-right diagonal
    edges(Mtemp+1:Mtemp+r1*c1*p1,:) = [reshape(edgeMat(1:r1,1:c1,1:p1),r1*c1*p1,1) reshape(edgeMat(2:r,2:c,2:p),r1*c1*p1,1)];
    Mtemp = Mtemp + r1*c1*p1;
    
    % bottom-left to top-right diagonal
    edges(Mtemp+1:Mtemp+r1*c1*p1,:) = [reshape(edgeMat(2:r,1:c1,1:p1),r1*c1*p1,1) reshape(edgeMat(1:r1,2:c,2:p),r1*c1*p1,1)];
    Mtemp = Mtemp + r1*c1*p1;
    %------------------------------
    % top-in to bottom-out diagonal
    edges(Mtemp+1:Mtemp+r1*c1*p1,:) = [reshape(edgeMat(1:r1,2:c,1:p1),r1*c1*p1,1) reshape(edgeMat(2:r,1:c1,2:p),r1*c1*p1,1)];
    Mtemp = Mtemp + r1*c1*p1;
    
    % bottom-in to top-out diagonal
    edges(Mtemp+1:Mtemp+r1*c1*p1,:) = [reshape(edgeMat(2:r,2:c,1:p1),r1*c1*p1,1) reshape(edgeMat(1:r1,1:c1,2:p),r1*c1*p1,1)];
end