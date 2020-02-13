% HTTP POST operation with Bisque authentication
%   [output, info] = bq.post(url, input, user, password)
%
% INPUT:
%   url      - url to fetch, may contain authentication which will be
%               stripped and sent in the HTTP header:
%               * Basic Auth - http://user:pass@host/path
%               * Bisque Mex - http://Mex:IIII@host/path
%   input    - document to post, should be a string or XML document
%   user     - optional: string with user name
%   password - optional: string with user password
%
% OUTPUT:
%    output - either byte vector or a file name if location was given 
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
%   info = bq.post('http://user:pass@host/path', '<resource><tag>....');
%   info = bq.post('http://host/path', '<resource><tag>....', 'user', 'pass');
%
% AUTHOR:
%   Dmitry Fedorov, www.dimin.net
%
% VERSION:
%   0.1 - 2011-06-27 First implementation
%

function [output, info] = post(url, input, user, password)

    narginchk(1,4);
    %if nargin<2 && isempty(strfind(url, '@')),
    %    error('bq.urread:InvalidInput', 'You must provede user credentials if the URL does not contain them.');
    %end

    [output, info] = bq.connect('POST', url, [], input, user, password);  
end


