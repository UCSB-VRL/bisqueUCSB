function [ROIdapi, ROIphf] = getVolume( Idapi, Iphf, coord, descriptor_size )
   x1 = round(max(coord(1) - descriptor_size(1)/2, 1));
   x2 = round(min(coord(1) + descriptor_size(1)/2, size(Idapi, 1) ));   
   y1 = round(max(coord(2) - descriptor_size(2)/2, 1));
   y2 = round(min(coord(2) + descriptor_size(2)/2, size(Idapi, 2) ));   
   z1 = round(max(coord(3) - descriptor_size(3)/2, 1));
   z2 = round(min(coord(3) + descriptor_size(3)/2, size(Idapi, 3) ));      
   ROIdapi = Idapi( x1:x2,y1:y2,z1:z2 );
   ROIphf  = Iphf( x1:x2,y1:y2,z1:z2 ); 
end
