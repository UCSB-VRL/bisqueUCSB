% bq.File
% A class wrapping a Bisque file resource giving ability to fetch and store
%   Constructor:
%       File(doc, element, user, password)
%         doc      - URL string or DOM document
%         element  - optional: DOM element
%         user     - optional: string
%         password - optional: string
%   
%   AUTHOR:
%       Dmitry Fedorov, www.dimin.net
%
%   VERSION:
%       0.1 - 2011-06-27 First implementation
%

classdef File < bq.Node
    
    methods

        function [self] = File(doc, element, user, password)
        % doc      - URL string or DOM document
        % element  - optional: DOM element
        % user     - optional: string
        % password - optional: string
            
            supargs = {};
            if exist('doc', 'var'), supargs{1} = doc; end
            if exist('element', 'var'), supargs{2} = element; end            
            if exist('user', 'var'), supargs{3} = user; end 
            if exist('password', 'var'), supargs{4} = password; end             
            self = self@bq.Node(supargs{:});            
        end % constructor
        
        %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        % Blob access
        %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        
        function blob = fetch(self, filename)
        % filename - optional: if given and not empty represents a filename to save the stream into
        %                      if given but is empty instructs to use resources name
        % blob - the actual blob data if no filename was provided or 
        %        the filename where the blob was stored
        
            if isempty(self.doc) || ~self.hasAttribute('resource_uniq'),
                error('bq.File.fetch:InvalidResource', 'This resource is invalid');
            end
            uri = bq.Url(self.getAttribute('uri')); 
            source_url = [uri.getRoot() '/blob_service/' self.getAttribute('resource_uniq')];
            
            supargs{1} = 'GET';
            supargs{2} = source_url;
            if exist('filename', 'var') && ~isempty(filename), 
                supargs{3} = filename; 
            end
            if exist('filename', 'var') && isempty(filename), 
                supargs{3} = self.getAttribute('name'); 
            end            
            supargs{4} = [];             
            if ~isempty(self.user) && ~isempty(self.password),
                supargs{5} = self.user; 
                supargs{6} = self.password;                 
            end            

            [blob, ~] = bq.connect(supargs{:});    
        end % fetch   
        
    end % methods
    
    methods (Static)    

        function node = store(filename, root_url, user, password)
        % filename - filename
        % node     - bq.Node object of the created resource            
            if ~exist('user', 'var') || isempty(user) || ~exist('password', 'var') || isempty(password),
                error('bq.File.store:UserCredentialsInvalid', 'Store requires user name and password');
            end        
            
            url = bq.Url(root_url); 
            url.setPath('import/transfer');
            [output, info] = bq.post_mpform(url.toString(), filename, user, password);
            output = char(output);
            if ~isempty(output) && info.status<300 && isempty(regexpi(output, '(<html)', 'tokenExtents')),
                output = regexprep(output, '<resource type="uploaded">', '');
                output = regexprep(output, '</resource>$', '');
                doc = bq.str2xml(output);
                node = bq.Factory.fetch(doc, [], user, password);
            else
                node = [];
            end
        end % store          
    end % static methods
    
end% classdef
