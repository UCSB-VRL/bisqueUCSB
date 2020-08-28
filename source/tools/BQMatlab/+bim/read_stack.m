% read_stack - load image stack creating 3D matrix
%
% Input:
%   filename - string with file name of image to decode 
%   channel  - the number of the channel to load
%
% Output:
%   img      - 3D matrix of the image in the native format
%
% ex:
%   img = bim.read_stack('myfile.tif', 1);
%
% Notes: 
%   Creates 8,16,32,64 bit arrays in float, signed and unsigned
%   If the input is 1 or 4 bit, that will be converted to 8bits
%

function [img, dim, res] = read_stack(filename)

  [im, format, pages, xyzr, metatxt] = bim.bimread( filename, 1 );
  sz = size(im);
  
  dim = struct();
  dim.c = 1;
  if size(sz)>2, dim.c = sz(3); end
  dim.z = pages;
  dim.t = 1;
  
  res = struct(); 
  res.x = xyzr(1);
  res.y = xyzr(2);
  res.z = xyzr(3);
  res.t = 0;

  img = zeros(sz(1), sz(2), dim.c, pages, class(im));
  if length(sz)==2,
     img(:,:,1) = im;
  else
     img(:,:,:,1) = im;
  end
  
  for i=2:pages,
    im = bim.bimread( filename, i );
    
    if length(sz)==2,
       img(:,:,i) = im;
    else
       img(:,:,:,i) = im;
    end    
    
  end
  
  clear mex;
end