% bq.Url
% A class wrapping URL parsing
%   
%   AUTHOR:
%       Dmitry Fedorov, www.dimin.net
%
%   VERSION:
%       0.1 - 2011-06-27 First implementation
%

%classdef Url < handle
classdef Url < matlab.mixin.Copyable
    
    properties
        url = [];
        purl = [];  
        
    end % properties
    
    methods
        
        function [self] = Url(url)
            self.url = url;
            self.parse();
        end % constructor
    
        %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        % Parse
        %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%        
        
        function parse(self)
            pattern = [ '^(?<scheme>\w+)://'...
                        '(?<auth>\w+:\w+@)?'...
                        '(?<authority>[\w\.\-_:]+)($|/)'...
                        '(?<path>[-\w~!$+|.,=/]+)?'...
                        '(?<query>\?[\w!$+|.,-_~=&%@/]+)?'...
                        '(?<fragment>#[\w!$+|.,-_~=&%@/]+)?'];
            self.purl = regexp(self.url, pattern, 'names');
            if isempty(self.purl),
                return;
            end
            
            % parse user and password
            self.purl.user = [];
            self.purl.password = [];            
            if ~isempty(self.purl.auth) && strfind(self.purl.auth, '@'),
                expression = '(?<user>\w+):(?<password>\w+)@';
                R = regexp(self.purl.auth, expression, 'names');
                self.purl.user = R.user;
                self.purl.password = R.password;        
            end               
            
            % parse query: '?aa=bb&cc=dd'
            % dima: add URL encoding and URL decoding
            if ~isempty(self.purl.query) && strfind(self.purl.query, '?'),
                 query = self.purl.query(2:end);
                 query = regexp(query, '&', 'split')';
                 query{1,2} = [];
                 for i=1:size(query,1),
                     a = regexp(query{i}, '=', 'split');
                     if ~isempty(a), query{i,1} = a{1}; end                       
                     if length(a)>1, query{i,2} = a{2}; end    
                 end
                 self.purl.query = query;
            end
            
            % parse fragment: '#ff=rr&kk=ll'
            if ~isempty(self.purl.fragment) && strfind(self.purl.fragment, '#'),
                 fragment = self.purl.fragment(2:end);
                 self.purl.fragment = fragment;
            end            
        end           
        
        %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        % toString
        %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        function r = toString(self)
            if self.hasUser() && self.hasPassword(),
                r = [self.purl.scheme '://' self.purl.user ':' self.purl.password '@' self.purl.authority];                
            else
                r = [self.purl.scheme '://' self.purl.authority];
            end

            % append path
            if ~isempty(self.purl.path),
                r = [r '/' self.purl.path]; 
            end
            
            % append query
            if ~isempty(self.purl.query)
                query = [];
                for i=1:size(self.purl.query, 1),
                    s = self.purl.query{i,1};
                    if ~isempty(self.purl.query{i,2}), 
                        s = [s '=' self.purl.query{i,2}];
                    end
                    if ~isempty(query), 
                        query = [query '&' s];
                    else
                        query = s;
                    end
                end
                r = [r '?' query]; 
            end            
            
            % append fragment            
            if ~isempty(self.purl.fragment)
                r = [r '#' self.purl.fragment]; 
            end
        end    
        
        %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        % Accessors
        %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%        
        
        function r = getRoot(self)
            r = [self.purl.scheme '://' self.purl.authority];
        end
        
        function r = getScheme(self)
            r = self.purl.scheme;
        end        
        
        function setScheme(self, scheme)
            self.purl.scheme = scheme;
        end   
        
        % credentials

        function r = hasCredentials(self)
            r = self.hasUser() && self.hasPassword();
        end            
        
        function r = hasUser(self)
            r = isfield(self.purl, 'user') && ~isempty(self.purl.user);
        end          
        
        function r = getUser(self)
            r = self.purl.user;
        end        
        
        function setUser(self, user)
            self.purl.user = user;
        end   
        
        function r = hasPassword(self)
            r = isfield(self.purl, 'password') && ~isempty(self.purl.password);
        end           
        
        function r = getPassword(self)
            r = self.purl.password;
        end          
        
        function setPassword(self, pass)
            self.purl.password = pass;
        end  
        
        % path
        
        function path = getPath(self)
            path = self.purl.path;
        end        
        
        function setPath(self, path)
            self.purl.path = path;
        end          
        
        %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        % Query
        %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%         

        function pushQuery(self, field, value)
            if ~exist('value', 'var'),            
                value = [];
            end
            if ~isempty(self.purl.query),
                self.purl.query{end+1, 1} = field;
                self.purl.query{end, 2} = bq.Url.urlencode(value);
            else
                self.purl.query = {field, bq.Url.urlencode(value)};
            end
        end           
        
        function q = popQuery(self)
            q = [];
            if ~isempty(self.purl.query),
                q = self.purl.query(end, :);
                self.purl.query(end, :) = [];
            end
        end
        
        function q = findQuery(self, field)
            q = [];
            if ~isempty(self.purl.query),
                for i=1:size(self.purl.query, 1),
                    if strcmpi(self.purl.query{i,1}, field),
                        q = self.purl.query(i, :);
                        break;
                    end
                end                
            end
        end         
        
        function q = removeQuery(self, field)
            q = [];
            if ~isempty(self.purl.query),
                for i=1:size(self.purl.query, 1),
                    if strcmpi(self.purl.query{i,1}, field),
                        q = self.purl.query(i, :);
                        self.purl.query(i, :) = [];
                        break;
                    end
                end                
            end
        end          
        
    end% methods
    
    methods (Static)    

        function urlOut = urlencode(urlIn)
        %URLENCODE Replace special characters with escape characters URLs need 
            urlOut = urlIn;
            if ~isempty(urlIn)
                urlOut = char(java.net.URLEncoder.encode(urlIn,'UTF-8'));
                % un-encode commas, cannot pass a list of ignored characters
                urlOut = strrep(urlOut, '%2C', ',');
            end
        end % urlencode
        
        function urlOut = urldecode(urlIn)
        %URLDECODE Replace URL-escaped strings with their original characters
            urlOut = urlIn;
            if ~isempty(urlIn)
                urlOut = char(java.net.URLDecoder.decode(urlIn,'UTF-8'));
            end
        end % urldecode
        
    end % static methods    
    
end% classdef
