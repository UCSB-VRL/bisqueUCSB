% Finds tags of interest and returns their values in proper formats
%   info = bq.iminfo(url, user, password)
%
% INPUT:
%   url      - Bisque DataService URL to an image, may contain 
%              authentication which will be stripped and sent in the HTTP header:
%               * Basic Auth - http://user:pass@host/path
%               * Bisque Mex - http://Mex:IIII@host/path
%   user     - optional: string with user name
%   password - optional: string with user password
%
% OUTPUT:
%   info     - a struct containing image information, some fileds include:
%              info.pixles_url         - ImageSrvice url to the image
%              info.image_num_x        - Image width
%              info.pixel_resolution_x - pixel resolution in X axis
%   
%   AUTHOR:
%       Dmitry Fedorov, www.dimin.net
%
%   VERSION:
%       0.1 - 2011-06-27 First implementation
%

function [info, meta] = iminfo(url, user, password)

    %% parse the url
    purl = bq.Url(url);
    if purl.hasUser() && purl.hasPassword(),
        user = purl.getUser();
        password = purl.getPassword();        
    end    

    %% import necessary XPath includes
    import javax.xml.xpath.*
    factory = XPathFactory.newInstance;
    xpath = factory.newXPath;
    
    %% fetch image resource document
    if exist('user', 'var') && exist('password', 'var'),
        doc = bq.get_xml( [url '?view=full'], user, password );
    else
        doc = bq.get_xml( [url '?view=full'] );    
    end
   
    exp_image = xpath.compile('//image');
    image = exp_image.evaluate(doc, XPathConstants.NODE);
    
    info = struct();
    info.unique = char(image.getAttribute('resource_uniq'));    
    info.pixles_url = [purl.getRoot() '/image_service/' info.unique];       
    
    %% fetch metadata from image service
    if exist('user', 'var') && exist('password', 'var'),
        doc_meta = bq.get_xml( [info.pixles_url '?meta'], user, password );
    else
        doc_meta = bq.get_xml( [info.pixles_url '?meta'] );    
    end
    meta = [];
    if ~isempty(doc_meta),
        template = '//tag[@name=''%s'']';
        tags = { 'filename',    'str'; 
                 'image_num_x', 'int'; 
                 'image_num_y', 'int';              
                 'image_num_z', 'int'; 
                 'image_num_t', 'int';
                 'image_num_c', 'int';             
                 'image_pixel_depth',  'int';
                 'image_pixel_format', 'str';             
                 'pixel_resolution_x', 'double';
                 'pixel_resolution_y', 'double';
                 'pixel_resolution_z', 'double';
                 'pixel_resolution_t', 'double';
               };
        info = bq.parsetags(doc_meta, tags, template, info);
        meta = bq.Factory.fetch(doc_meta);
    end
    
    %% parse image resource tags overwriting some tag values
    template = '//tag[@name=''%s'']';
    tags = { 'filename',             'str';
             'pixel_resolution_x_y', 'double';             
             'pixel_resolution_x',   'double';
             'pixel_resolution_y',   'double';
             'pixel_resolution_z',   'double';
             'pixel_resolution_t',   'double';
           };
    info = bq.parsetags(doc, tags, template, info);
end
