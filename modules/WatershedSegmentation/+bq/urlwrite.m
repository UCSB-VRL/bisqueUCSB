% Similar to Matlab URLWRITE adding authentication
%
% [output, info] = bq.urlwrite(url, location, user, password)
%
% INPUT:
%    url      - url to fetch, may contain authentication which will be
%               stripped and sent in the HTTP header:
%               * Basic Auth - http://user:pass@host/path
%               * Bisque Mex - http://Mex:IIII@host/path
%    location - file path to where to store fetched bytes, give [] if no
%               file should be written
%    user     - optional: string with user name
%    password - optional: string with user password
%
% OUTPUT:
%    output   - location of the written file
%    info     - struct with HTTP return code and error string
%
% EXAMPLES:
%   [f, info] = bq.urlread('http://user:pass@host/path', 'myfile.txt');
%   [f, info] = bq.urlread('http://host/path', 'myfile.txt', 'user', 'pass');
%
%   AUTHOR:
%       Dmitry Fedorov, www.dimin.net
%
%   VERSION:
%       0.1 - 2011-06-27 First implementation
%
function [output, info] = urlwrite(url, location, user, password)

    narginchk(2,4);
    if nargin==3
        error('bq.urread:InvalidInput', 'You must provide both user name and password');
    end
    
    if nargin<2
        [output, info] = bq.get(url);      
    elseif nargin<3
        [output, info] = bq.get(url, location);
    else
        [output, info] = bq.get(url, location, user, password);
    end
    
end

