% bq.Dataset
% A class wrapping a BisQue dataset resource giving ability to share and
% delete
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
%       0.1 - 2016-02-02 First implementation
%

classdef Dataset < bq.Node
    
    methods

        function [self] = Dataset(doc, element, user, password)
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
        % Dataset operations using dataset service
        %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        
        function remove(self, remove_members)
        % removes the dataset and all of its members if remove_members is 1
            if ~exist('remove_members', 'var') || remove_members == 0,
                remove@bq.Node(self);
            else
                uri = self.getAttribute('uri');
                url = bq.Url(uri);
                bisque_root = url.getRoot();
                [~, info] = bq.get([bisque_root '/dataset_service/delete?duri=' uri], [], self.user, self.password);
                if info.status>=300,
                    error('bq.Dataset.remove: Could not delete all the elements');
                end              
                remove@bq.Node(self, 1);
            end
        end % remove
        
        %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        % Sharing
        %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

        function changed = share(self, user, mode)
        % user - has to be an exact match of either:
        %     user name
        %     user email
        %     user url
        % mode - 
        %     read: allow only read access (default)
        %     edit: allow read and write access
        %     ~: empty (none value) remove share for that user 
            
            % dataset share does normal share on the dataset resource and
            % then calls /dataset_service/share to propagate the share to
            % all the dataset members
            if ~exist('mode', 'var')
                changed = share@bq.Node(self, user);
            else
                changed = share@bq.Node(self, user, mode);
            end
            
            if changed == 1,
                uri = self.getAttribute('uri');
                url = bq.Url(uri);
                bisque_root = url.getRoot();
                [~, info] = bq.get([bisque_root '/dataset_service/share?duri=' uri], [], self.user, self.password);
                if info.status>=300,
                    error('bq.Dataset.share: Could not share all the elements');
                end      
            end
        end % share          
        
    end % methods
    
end% classdef
