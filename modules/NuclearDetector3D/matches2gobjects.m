% matches2gobjects - matches, unmatches and all indivisual points into a
%                    Bisque Gobjects XML format
% 
%   INPUT:
%       filename - string of file name to write
%       pts      - detected nuclei positions, is a matrix of form:
%       gt       - ground truth nuclear positions, is a matrix of form:
%                   m(:,1) -> Y coordinate (starting at 1)
%                   m(:,2) -> X coordinate (starting at 1)
%                   m(:,3) -> Z coordinate (starting at 1)
%                   m(:,4) -> point IDs
%                   m(:,5) -> confidence [0:1]
%       matches  - matrix of matched locations: [index_pts, index_gt]
%       left_pts - indices of unmatched pts
%       left_gt  - indices of unmatched GT
%       ns       - nuclear size in image pixels
%
%   AUTHOR:
%       Dmitry Fedorov, www.dimin.net
%
%   VERSION:
%       0.1 - 2011-03-29 First implementation

function matches2gobjects ( filename, pts, gt, matches, left_pts, left_gt, ns )
  fid = fopen(filename, 'wt');
  fprintf(fid, '<bfi>\n');   
  
  dmax = sqrt( ns(1)^2 + ns(2)^2 + ns(3)^2 ); 
  
  N = size(matches, 1);
  fprintf(fid, '<gobject type="Matched" name="Matched" >\n');     
  for n=1:N,
     x1 = pts(matches(n,1), 2)-1.0;
     y1 = pts(matches(n,1), 1)-1.0;
     z1 = pts(matches(n,1), 3)-1.0;  
     p1 = pts(matches(n,1), 5);
      
     x2 = gt(matches(n,2), 2)-1.0;
     y2 = gt(matches(n,2), 1)-1.0;
     z2 = gt(matches(n,2), 3)-1.0;
     p2 = gt(matches(n,2), 5);
     
     pM = mean([p1 p2]) * 100;
     pD = 100 - ( sqrt((x1-x2)^2+(y1-y2)^2+(z1-z2)^2) / dmax) * 100;
     pC = (pM + pD) / 2.0;

     fprintf(fid, '  <gobject type="polyline" name="%d" >\n', n);     
     fprintf(fid, '    <vertex x="%.2f" y="%.2f" z="%.2f" index="1" />\n', x1, y1, z1); 
     fprintf(fid, '    <vertex x="%.2f" y="%.2f" z="%.2f" index="2" />\n', x2, y2, z2);      
     fprintf(fid, '    <tag name="color" value="%s" />\n', '#FFFFFF');
     
     fprintf(fid, '    <tag name="probability_match" value="%.2f" />\n', pM);
     fprintf(fid, '    <tag name="probability_distance" value="%.2f" />\n', pD);     
     fprintf(fid, '    <tag name="probability_combined" value="%.2f" />\n', pC);     
     
     fprintf(fid, '  </gobject>\n');      
  end        
  fprintf(fid, '</gobject>\n');  
 
  points2gobjects ( [], pts, 'ND3D-Unmatched', 'ND3D-Unmatched', '#FF0000', fid, left_pts );
  points2gobjects ( [], gt, 'GT-Unmatched', 'GT-Unmatched', '#00FF00', fid, left_gt );
  
  points2gobjects ( [], pts, 'ND3D', 'ND3D', '#FFFF00', fid  );
  points2gobjects ( [], gt, 'GT', 'GT', '#0000FF', fid );
  
  fprintf(fid, '</bfi>\n');     
  fclose(fid);    
end 

