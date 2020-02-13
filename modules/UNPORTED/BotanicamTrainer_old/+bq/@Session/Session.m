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
        
        function [self] = Session(mex_url, auth_token, bisque_root)
        % mex_url     - url to the MEX documment
        % auth_token  - auth token given by the system
        % bisque_root - optional: server root             
            if nargin==2,
                self.init(mex_url, auth_token);
            elseif nargin==3,
                self.init(mex_url, auth_token, bisque_root);
            end
        end % constructor
        
        function init(self, mex_url, auth_token, bisque_root )
        % mex_url     - url to the MEX documment
        % auth_token  - auth token given by the system
        % bisque_root - optional: server root 
            self.mex_url    = mex_url;
            self.auth_token = auth_token;
            self.user = 'Mex';
            self.password = self.auth_token;

            % if Bisque root isn't given, try to parse from mex url
            if ~exist('bisque_root', 'var'),
                purl = bq.Url(self.mex_url);
                bisque_root = purl.getRoot();
            end
            self.bisque_root = bisque_root;   
            
            self.mex = bq.Factory.fetch([self.mex_url '?view=deep'], [], self.user, self.password);
        end % init
    
        function update(self, status)
        % updates status/value of the MEX on the server, with given status string
            self.error = struct();
            if isempty(self.mex),
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
            if isempty(self.mex),
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
            if isempty(self.mex),
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
          
            if isempty(ops) || ~isempty(ops) && ops.hasAttribute('uri'),
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
            outputs = self.mex.findNode('//tag[@name="outputs"]');
            if isempty(outputs),
                outputs = self.mex.addTag('outputs');
            end
        end % createOutputs         
        
        %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        % helper functions for reading objects from Bisque servers
        %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
       
        function res = fetch(self, url)
            res = bq.Factory.fetch(url, [], self.user, self.password);
        end
        
        function res = storeFile(self, filename)
            res = bq.File.store(filename, self.bisque_root, self.user, self.password); 
        end        
        
        function res = storeImage(self, image, args)
            res = bq.Image.store(image, args, self.bisque_root, self.user, self.password); 
        end             
        
    end% methods
end% classdef
