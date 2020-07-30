% Decode path from bisque url spec
%
% path = bq.url2path(url)
%
% INPUT:
%    url      - encoded path
%
% OUTPUT:
%    path     - path to the file
%
%   AUTHOR:
%       Dmitry Fedorov, www.dimin.net
%
%   VERSION:
%       1 - 2016-01-20 First implementation
%

function path = url2path(url)
    path = url;
    path = strrep(path, 'file:///', '');
    path = regexprep(path, '^(\w+)://', '');
    path = urldecode(path);
    if ispc,
        path = strrep(path, '/', '\');
    end    
end
