% Similar to Matlab URLREAD adding authentication
%
% [s, info] = bq.urlread(url, user, password)
%
% INPUT:
%    url      - url to fetch, may contain authentication which will be
%               stripped and sent in the HTTP header:
%               * Basic Auth - http://user:pass@host/path
%               * Bisque Mex - http://Mex:IIII@host/path
%    user     - optional: string with user name
%    password - optional: string with user password
%
% OUTPUT:
%    s      - byte vector fetched from the response body
%    info   - struct with HTTP return code and error string
%
% EXAMPLES:
%   s = bq.urlread('http://user:pass@bisque.edu/ds/images/XXXXX');
%   [s, info] = bq.urlread('http://host/path', 'user', 'pass');
%   [f, info] = bq.urlread('http://user:pass@host/path');
%
%   AUTHOR:
%       Dmitry Fedorov, www.dimin.net
%
%   VERSION:
%       0.1 - 2011-06-27 First implementation
%

function [s, info] = urlread(url, user, password)
    narginchk(1,3);
    if nargin==2,
        error('bq.urread:InvalidInput', 'You must provide both user name and password');
    end

    if nargin<2, 
        [s, info] = bq.get(url);
    else
        [s, info] = bq.get(url, [], user, password);
    end
end
