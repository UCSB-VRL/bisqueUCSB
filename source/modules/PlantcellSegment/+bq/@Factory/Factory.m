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
            { 'node', 'image', 'file', ...
              'gobject', 'point', 'polyline', 'polygon', ...
              'rectangle', 'square', 'circle', 'ellipse', 'label' }, ... % types           
            { @bq.Node, @bq.Image, @bq.File, ...
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
        
    end% static methods
end% classdef
