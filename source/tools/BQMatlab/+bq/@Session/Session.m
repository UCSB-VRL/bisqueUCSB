% bq.Session
% A class wrapping a module session, wich goes in the following sequence:
%
% 1) initing session
% s = bq.Session('MEX_URL', 'AUTH_TOKEN');
%
% 2) while running
% s.update('RUNNING');
% % do stuff....
% s.update('10%');
% % do stuff....
%
% 3) creating results
% s.finish(outputs);
%   
%   AUTHOR:
%       Dmitry Fedorov, www.dimin.net
%
%   VERSION:
%       0.1 - 2011-06-27 First implementation
%

classdef Session < handle
    
    properties
        mex = [];
        services = [];
        user = [];
        password = [];
        mex_url = [];
        auth_token = [];
        bisque_root = [];
        
        error = struct();
    end % properties
    
    methods
        
        function [self] = Session(user_or_mex_url, pass_or_auth_token, bisque_root)
        % user_or_mex_url     - username or url to the MEX documment
        % pass_or_auth_token  - password or auth token given by the system
        % bisque_root - optional for mex auth: server root        
            if nargin==2
                self.init(user_or_mex_url, pass_or_auth_token);
            elseif nargin==3
                self.init(user_or_mex_url, pass_or_auth_token, bisque_root);
            end
        end % constructor
        
        function init(self, user_or_mex_url, pass_or_auth_token, bisque_root )
        % user_or_mex_url     - username or url to the MEX documment
        % pass_or_auth_token  - password or auth token given by the system
        % bisque_root - optional for mex auth: server root 
            
            self.auth_token = pass_or_auth_token;
            self.password = self.auth_token;

            %if authenticating with a mex url and auth_token
            if (strncmpi(user_or_mex_url, 'http://', 7)==1 || strncmpi(user_or_mex_url, 'https://', 8)==1),
                self.mex_url = user_or_mex_url;
                self.user = 'Mex';
                % if Bisque root isn't given, try to parse from mex url
                if ~exist('bisque_root', 'var')
                    purl = bq.Url(self.mex_url);
                    bisque_root = purl.getRoot();
                end
                self.bisque_root = bisque_root;                
                self.mex = bq.Factory.fetch([self.mex_url '?view=deep'], [], self.user, self.password);
            else
                self.mex_url = [];
                self.user = user_or_mex_url;
                self.mex = [];
                % if Bisque root isn't given, it's an error
                if ~exist('bisque_root', 'var')
                    error('bq.Session:init', 'bisque_root is required when using user name and password');
                else
                    self.bisque_root = bisque_root;
                end
            end            
        end % init
    
        function update(self, status)
        % updates status/value of the MEX on the server, with given status string
            self.error = struct();
            if isempty(self.mex)
                return;
            end
            
            % update MEX document in memory
            self.mex.setAttribute('value', status);
            
            % update the document on the server
            %input = sprintf('<mex uri="%s" value="%s" />', self.mex_url, status);
            %bq.post(self.mex_url, input, self.user, self.password);
            
            node = bq.Factory.fetch(bq.str2xml('<mex />'));
            node.setAttribute('uri', self.mex_url);
            node.setAttribute('value', status);
            bq.post(self.mex_url, node, self.user, self.password);
        end % update   
 
        function fail(self, message)
        % fails MEX execution with the given error message
            if isempty(self.mex)
                return;
            end
            status = 'FAILED';
            
%             % update MEX document in memory
%             self.mex.setAttribute('value', status);
%             self.mex.addTag('error_message', message);
%             % update the document on the server
%             bq.put(self.mex_url, self.mex.doc, self.user, self.password);
            
            % update the document on the server using POST and fresh doc
            node = bq.Factory.fetch(bq.str2xml('<mex />'));
            node.setAttribute('uri', self.mex_url);
            node.setAttribute('value', status);
            node.addTag('error_message', message);
            bq.post(self.mex_url, node, self.user, self.password);
        end % fail           

        function finish(self)
        % finishes the MEX posting outputs section to the system
            if isempty(self.mex)
                return;
            end
            status = 'FINISHED';
            
            % update MEX document in memory
            self.mex.setAttribute('value', status);
            
            %append outputs
%             if nargin==2,
%                 if isa(outputs, 'org.apache.xerces.dom.ElementImpl') ||...
%                    isa(outputs, 'org.apache.xerces.dom.DeferredElementImpl'),
%                        self.mex.element.appendChild(outputs);
%                 elseif iscell(outputs),
%                     %t = bq.addTag(self.mex, m, 'outputs');
%                     % iterate over cell and create all XML elements
%                     % dima: implement
%                 end            
%             end

            % update the document on the server
            ops = self.mex.findNode('//tag[@name="outputs"]');
          
            if isempty(ops) || ~isempty(ops) && ops.hasAttribute('uri')
                bq.put(self.mex_url, self.mex.doc, self.user, self.password);
            else
                % a little hack to create a document for POST operation
                node = bq.Factory.fetch(bq.str2xml('<mex />'));
                node.setAttribute('uri', self.mex_url);
                node.setAttribute('value', status);
                node.element.appendChild(node.doc.adoptNode(ops.element.cloneNode(true)));
                bq.post(self.mex_url, node, self.user, self.password);
            end            
        end % finish 
        
        function outputs = getOutputs(self)
        % returns outputs section for this MEX, if does not exist - creates
            if isempty(self.mex)
                return;
            end            
            outputs = self.mex.findNode('//tag[@name="outputs"]');
            if isempty(outputs)
                outputs = self.mex.addTag('outputs');
            end
        end % createOutputs         
        
        %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        % helper functions for reading objects from Bisque servers
        %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        
        function res = fetch(self, url)
        % fetch resource from the system
        % url - points to a bisque resource and can end with the view parameter
        %     'http://bisque.org/00-XYZ?view=deep'
        % view=deep will fetch the whole resource document
        % view=full will fetch the resource document with first level of tags and gobjects
        % view=short will fetch the minimal view of the resource, default if none provided            
            
            res = bq.Factory.fetch(url, [], self.user, self.password);
        end
   
        function resource = store(self, resource)
        % store a new metadata resource into the system
        % resource - bq.Node resource created with 
        %            resource = bq.Factory.new('resource', 'my_meta_n1');
            
            url = bq.Url(self.bisque_root); 
            url.setPath('data_service');
            resource.save(url.toString(), self.user, self.password);
        end          
        
        function res = storeFile(self, filename, resource)
        % store a new file described by a metadata resource into the system
        % filename - path to the file
        % resource - bq.Node resource describing the file created with:  
        %    resource = bq.Factory.new('resource', 'dir/dir2/filename.csv');
            
            if ~exist('resource', 'var'), resource=[]; end
            res = bq.File.store(filename, self.bisque_root, self.user, self.password, resource); 
        end
        
        function res = storeImage(self, image, args, resource)
        % store a new image (matlab matrix) with geometry described by args
        % image: matlab matrix
        % args: struct describing the image
        %     args.filename
        %     args.dim - c z t (as bim.write_ome_tiff requires)
        %     args.res - x y z t (as bim.write_ome_tiff requires)
        
            if ~exist('resource', 'var'), resource=[]; end       
            res = bq.Image.store(image, args, self.bisque_root, self.user, self.password, resource); 
        end
        
        function nodes = query(self, resource_type, tag_query, tag_order, view, offset, limit, wpublic)
        % exposes query RESTful API: http://biodev.ece.ucsb.edu/projects/bisquik/wiki/Developer/DataServer
        % resource_type: resource type to search for, e.g. image
        % view: Change the output format of the returned resource [short, full, deep], clean,
        % limit: Limit the number of items returned
        % offset: used with limit to fetch more items
        % tag_query: Query resources (image) by underlying tag: [TYPE:[[NAME:]VAL...&]]
        % tag_order: Order the response based on the values of a tag:
        %    @ts:desc - return images sorted by time stamp(most recent first)
        %    tagname:asc - sorted by a particular tag value
            
            if ~exist('offset', 'var'), offset=[]; end
            if ~exist('limit', 'var'), limit=[]; end
            if ~exist('wpublic', 'var'), wpublic=[]; end
            nodes = bq.Factory.query(self.bisque_root, resource_type, tag_query, tag_order, view, offset, limit, wpublic, self.user, self.password);
        end % query          
        
        function node = find(self, resource_type, tag_query, view)
        % find one resource matching tag_query, see query for more info
            nodes = self.query(resource_type, tag_query, [], view, 0, 1);
            if length(nodes)<1
                node = [];
            else
                node = nodes{1};
            end            
        end % find
        
    end% methods
end% classdef
