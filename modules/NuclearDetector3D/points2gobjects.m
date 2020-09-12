% points2gobjects - writies points to Bisque Gobjects XML format
% 
%   INPUT:
%       filename - string of file name to write
%       np        - detected nuclei positions, is a matrix where
%                   m(:,1) -> Y coordinate (starting at 1)
%                   m(:,2) -> X coordinate (starting at 1)
%                   m(:,3) -> Z coordinate (starting at 1)
%                   m(:,4) -> point IDs
%                   m(:,5) -> probability
%                   m(:,6) -> probability based on counts
%                   m(:,7) -> probability based on sums
%                   m(:,8) -> probability based on mean
%                   m(:,9) -> probability based on LoG mean
%
%   AUTHOR:
%       Dmitry Fedorov, www.dimin.net
%
%   VERSION:
%       0.1 - 2011-03-29 First implementation

function points2gobjects ( filename, np, tp )
    outputs = bq.Factory.new('gobject', 'nuclear_centroids');
    for i=1:size(np,1),       
        n = outputs.addGobject('nucleus', int2str(i));        
        v = [np(i,1:3), tp];
        p = n.addGobject('point', 'centroid', v );
        p.addTag('confidence', np(i,5)*100, 'number'); 
    end
    outputs.save(filename);    
end 
