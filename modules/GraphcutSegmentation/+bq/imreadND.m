% Loads ND images from the Bisque system without requiring local storage
%   I = bq.imreadND(url, user, password)
%
% 2.8X faster than using BQLib and more generic returning correct result
% Remember, all the image data is stored within matlab memory, so you can 
% run out of it if loading a very large image!!!
%
% INPUT:
%    url - a url to a Bisque image, may contain authentication inline
%            * Basic Auth - http://user:pass@host/path
%            * Bisque Mex - http://Mex:IIII@host/path
%
% OUTPUT:
%    I   - an ND matrix, with dimensions order: Y X C Z T
%
% EXAMPLES:
%   I = bq.imreadND('http://user:pass@host/imgsrv/XXXXX?slice=,,,2&remap=1');
%     this will fetch a 3D image (all z planes) at time point 2 and only
%     of the first channel
%   
%   AUTHOR:
%       Dmitry Fedorov, www.dimin.net
%
%   VERSION:
%       0.1 - 2011-06-27 First implementation
%

function I = imreadND(url, user, password)

    % default to Matlab if it's a local path
    if ~strfind(url, '://'),
        I = imread(url);
        return;
    end

    %% parse the url
    purl = bq.Url(url);
    if purl.hasUser() && purl.hasPassword(),
        user = purl.getUser();
        password = purl.getPassword();        
    end        
    
    %% fetch metadata from image service
    purl.pushQuery('dims');     
    if exist('user', 'var') && exist('password', 'var'),
        doc = bq.get_xml( purl.toString(), user, password );
    else
        doc = bq.get_xml( purl.toString() );
    end 
    
    template = '//image/tag[@name=''%s'']';
    tags = { 'image_num_z',        'int'; 
             'image_num_t',        'int';              
             'image_num_c',        'int'; 
             'image_num_x',        'int';
             'image_num_y',        'int';             
             'image_pixel_depth',  'int';
             'image_pixel_format', 'str';
           };
    info = bq.parsetags(doc, tags, template);
    purl.popQuery();    
    
    % convert pixel type
    pf_map = containers.Map({'unsigned integer 8', 'unsigned integer 16', 'unsigned integer 32', 'unsigned integer 64', ... 
                          'signed integer 8',   'signed integer 16',   'signed integer 32',   'signed integer 64', ... 
                          'floating point 32', 'floating point 64'}, ...
                         {'uint8', 'uint16', 'uint32', 'uint64', ...
                          'int8',  'int16',  'int32',  'int64', ...
                          'single', 'double' });
    pixel_type_str = sprintf('%s %d', info.image_pixel_format, info.image_pixel_depth);
    if ~pf_map.isKey(pixel_type_str),
        throw(MException('Image pixel format is not supported'));
    end
    pixel_type = pf_map(pixel_type_str);

    % fix for t and z that may be reported as 0, on which reshape breaks
    if info.image_num_t < 1, info.image_num_t = 1; end
    if info.image_num_z < 1, info.image_num_z = 1; end
    
    %% fetch image data stream and reshape it
    purl.pushQuery('format', 'raw');
    if exist('user', 'var') && exist('password', 'var'),
        [I, res] = bq.get(purl.toString(), [], user, password);
    else
        [I, res] = bq.get(purl.toString());
    end  
    if res.status>=300 || isempty(I),
        I = []; return;
    end
    I = typecast(I, pixel_type);
    I = squeeze(reshape(I, info.image_num_x, info.image_num_y, info.image_num_c, info.image_num_z, info.image_num_t)); 
    
    % matlab uses row-major order, opposite to column-major in Bisque
    % we need to transpose all the image planes
    p = 1:length(size(I));
    p(1:2) = [2 1];
    I = permute(I, p);
end

