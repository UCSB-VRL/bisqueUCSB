% Finds tags of interest and returns their values in proper formats
%   s = bq.parsetags(doc, tags, template)
%
% INPUT:
%    doc      - a parsed XML document as received from xmlread or bq.get_xml
%    tags     - an Nx2 cell with elemnets: 'tag_name', 'type';
%               types are: 'double', 'int' and 'str'
%               tags = { 'width', 'int'; 'descr', 'str'; 'pix_res', 'double'; }
%    template - an xpath expression template where %s should indicate
%               template = '//image/tag[@name=''%s'']';
%
% OUTPUT:
%    s   - a struct containing tag values by their names
%          for tags example above will produce:
%            s.width, s.descr, s.pix_res
%   
%   AUTHOR:
%       Dmitry Fedorov, www.dimin.net
%
%   VERSION:
%       0.1 - 2011-06-27 First implementation
%

function s = parsetags(doc, tags, template, s)
    import javax.xml.xpath.*;
    factory = XPathFactory.newInstance;
    xpath = factory.newXPath;    
    
    if ~exist('s', 'var')
        s = struct;
    end
    
    for i=1:size(tags,1),
        name = tags{i,1};
        type = tags{i,2};        
        expression = sprintf(template, name);
        t = xpath.evaluate(expression, doc, XPathConstants.NODE);    

        if ~isempty(t) && strcmp(type, 'double'), 
            s.(name) = str2double(t.getAttribute('value')); 
        elseif ~isempty(t) && strcmp(type, 'int'), 
            s.(name) = str2num(t.getAttribute('value')); 
        elseif ~isempty(t), 
            s.(name) = char(t.getAttribute('value')); 
        end
    end
end
