% HTTP DELETE operation with Bisque authentication
%   [info] = bq.delete(url, user, password)
%
% INPUT:
%   url      - url of a resource to delete, may contain authentication which will be
%               stripped and sent in the HTTP header:
%               * Basic Auth - http://user:pass@host/path
%               * Bisque Mex - http://Mex:IIII@host/path
%   user     - optional: string with user name
%   password - optional: string with user password
%
% OUTPUT:
%    info   - struct with HTTP return code and error string
%
% REQUIREMENTS:
%    For all practical purpouses you need an increased JVM heap
%    in order to get all the commmunication functionality going smoothly 
%    you should increase those settings by copying the file java.opts
%    to your matlab location:
%        MATLAB/YOUR-VERSION/bin/YOUR-ARCH/
%    where:
%        YOUR-VERSION will be something like R2009b, R2011a, ect...
%        YOUR-ARCH may be something like win64
%
% EXAMPLES:
%   info = bq.delete('http://user:pass@host/path');
%   info = bq.delete('http://host/path', 'user', 'pass');
%
% AUTHOR:
%   Dmitry Fedorov, www.dimin.net
%
% VERSION:
%   0.1 - 2011-06-27 First implementation
%

function [info] = delete(url, user, password)

    error(nargchk(1,3,nargin));
    %if nargin<2 && isempty(strfind(url, '@')),
    %    error('bq.urread:InvalidInput', 'You must provede user credentials if the URL does not contain them.');
    %end

    [~, info] = bq.connect('DELETE', url, [], [], user, password);  
end


