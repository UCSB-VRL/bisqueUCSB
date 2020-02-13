function [edges numLinks] = vrlConstructGraph(graphSize, connectivity)
%% Function to Construct a graph for 4-or 8- connecvitiy .. this for usage by
%  graph cuts

edges = [];
noRows = graphSize(1);
noCols = graphSize(2);

nodeID = 1:noRows*noCols;
nodeID = reshape( nodeID, noRows, noCols);

% Construct East Edges
fromEdges = nodeID(1:end, 1:end-1);
toEdges   = nodeID(1:end, 2:end);
edges = [edges; fromEdges(:) toEdges(:)];

% Construct South Edges
fromEdges = nodeID(1:end-1, 1:end);
toEdges = nodeID(2:end, 1:end);
edges = [edges; fromEdges(:) toEdges(:)];

if( connectivity == 1 )
    % Construct South East Edges
    fromEdges = nodeID(1:end-1, 1:end-1);
    toEdges   = nodeID(2:end, 2:end);
    edges = [edges; fromEdges(:) toEdges(:)];

    % Construct North East Edges
    fromEdges =  nodeID(2:end, 1:end-1);
    toEdges   =  nodeID(1:end-1, 2:end);
    edges = [edges; fromEdges(:) toEdges(:)];
end

numLinks = size(edges, 1);