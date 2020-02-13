% bq.Factory
% A factory class producing Nodes, Images etc...
%   
% i = bq.Factory.fetch('http://hjdfhjdhfjd');
%
%   AUTHOR:
%       Dmitry Fedorov, www.dimin.net
%
%   VERSION:
%       0.1 - 2011-06-27 First implementation
%

classdef Factory
    
    properties (Constant)
        resources = containers.Map( ...
            { 'node', 'image', 'file', 'dataset', ...
              'gobject', 'point', 'polyline', 'polygon', ...
              'rectangle', 'square', 'circle', 'ellipse', 'label' }, ... % types           
            { @bq.Node, @bq.Image, @bq.File, @bq.Dataset, ...
              @bq.Gobject, @bq.Gobject, @bq.Gobject, @bq.Gobject, ...
              @bq.Gobject, @bq.Gobject, @bq.Gobject, @bq.Gobject, @bq.Gobject } ... % classes
        )
    end % constant properties
    
    methods (Static)
        
        function [node] = fetch(doc, element, user, password)
        % parses the Bisque documentand returns a root bq.Node
        % if doc is not a DOM document but a string, fetches that first
        % from file or Bisque server
        %   doc      - URL string, DOM document or a file name
        %   element  - optional: DOM element
        %   user     - optional: string
        %   password - optional: string
        
            creds = exist('user', 'var') && ~isempty(user) && ...
                    exist('password', 'var') && ~isempty(password);
            
            if ischar(doc) && strcmpi(doc(1:4), 'http'),
                % if doc is a URL then fetch it first
                if creds,
                    doc = bq.get_xml( doc, user, password );
                else
                    doc = bq.get_xml( doc );    
                end                    
            elseif ischar(doc),
                % if doc is a filename, load from a file
                doc = xmlread(doc);
            end            
            
            if ~exist('element', 'var') || isempty(element),
                element = doc.getDocumentElement();
            end               
            
            % find class name based on the xml tag name
            tag = char(element.getTagName());
            if ~bq.Factory.resources.isKey(tag),              
                tag = 'node';
            end
            
            % get class and instantiate it
            myclass = bq.Factory.resources(tag);
            try
                if creds,
                    node = myclass(doc, element, user, password );
                else
                    node = myclass(doc, element);
                end                  
            catch error
                warning(error.identifier, error.message);
                node = [];
            end            
        end % fetch
        
        function [node] = new(type, name, value)
        % creates a new DOM document and returns respective bq.Node
        %   type  - string of a Bisque object type
        %   name  - name string
        %   value - value string            
            if ~exist('type', 'var'),
                error('bq.factory.new: type is required', '');
            end
            input = sprintf('<%s />', type);
            doc = bq.str2xml(input);
            node = bq.Factory.fetch(doc);
            
            if exist('name', 'var'),                
                node.setAttribute('name', name);
            end
            if exist('value', 'var'),                
                node.setAttribute('value', value);                
            end
        end % new
        
        function nodes = query(bisque_root, resource_type, tag_query, tag_order, view, offset, limit, wpublic, user, password)
        % exposes query RESTful API: http://biodev.ece.ucsb.edu/projects/bisquik/wiki/Developer/DataServer
        % resource_type: resource type to search for, e.g. image
        % view: Change the output format of the returned resource [short, full, deep], clean,
        % limit: Limit the number of items returned
        % offset: used with limit to fetch more items
        % tag_query: Query resources (image) by underlying tag: [TYPE:[[NAME:]VAL...&]]
        % tag_order: Order the response based on the values of a tag:
        %    @ts:desc - return images sorted by time stamp(most recent first)
        %    tagname:asc - sorted by a particular tag value
            
            url = bq.Url(bisque_root); 
            if exist('resource_type', 'var') && ~isempty(resource_type),
                url.setPath(['data_service/' resource_type]);
            else
                url.setPath('data_service');                
            end
            
            if exist('tag_query', 'var') && ~isempty(tag_query),
                url.pushQuery('tag_query', tag_query);
            end
            if exist('tag_order', 'var') && ~isempty(tag_order),
                url.pushQuery('tag_order', tag_order);
            end
            if exist('view', 'var') && ~isempty(view),
                url.pushQuery('view', view);
            end
            if exist('offset', 'var') && ~isempty(offset),
                url.pushQuery('offset', num2str(offset));
            end            
            if exist('limit', 'var') && ~isempty(limit),
                url.pushQuery('limit', num2str(limit));
            end
            if exist('wpublic', 'var') && ~isempty(wpublic),
                url.pushQuery('wpublic', 'true');
            end 
            
            if exist('user', 'var') && exist('password', 'var') && ~isempty(user) && ~isempty(password),  
                doc = bq.get_xml( url.toString(), user, password );
            else
                doc = bq.get_xml( url.toString() );                
            end
            
            % walk the children and create output nodes
     
            import javax.xml.xpath.*;
            factory = XPathFactory.newInstance;
            xpath = factory.newXPath;    
            xnodes = xpath.evaluate('resource/*', doc, XPathConstants.NODESET);
            if isempty(xnodes) || xnodes.getLength()<1,
                nodes = cell(0,1);
                return;
            end            
            nodes = cell(xnodes.getLength(),1);
            for i=1:xnodes.getLength(),
                if exist('user', 'var') && exist('password', 'var') && ~isempty(user) && ~isempty(password), 
                    nodes{i} = bq.Factory.fetch(doc, xnodes.item(i-1), user, password);
                else
                    nodes{i} = bq.Factory.fetch(doc, xnodes.item(i-1));                    
                end
            end            
            
        end % query          
        
        function node = find(bisque_root, resource_type, tag_query, view, wpublic, user, password)
        % find one resource matching tag_query, see query for more info
            if ~exist('user', 'var'), user=[]; end
            if ~exist('password', 'var'), password=[]; end
            if ~exist('wpublic', 'var'), wpublic=[]; end
            nodes = bq.Factory.query(bisque_root, resource_type, tag_query, [], view, 0, 1, wpublic, user, password);
            if length(nodes)<1,
                node = [];
            else
                node = nodes{1};
            end
        end % find        
       
    end% static methods
end% classdef
