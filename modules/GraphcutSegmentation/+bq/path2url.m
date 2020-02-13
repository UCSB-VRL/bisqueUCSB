% Encode path into bisque url spec
%
% url = bq.path2url(path, spec)
%
% INPUT:
%    path     - path to the file
%    spec     - optional: path spec file://, irods:// etc...
%
% OUTPUT:
%    url      - encoded path
%
%   AUTHOR:
%       Dmitry Fedorov, www.dimin.net
%
%   VERSION:
%       1 - 2016-01-20 First implementation
%

function url = path2url(path, spec)
    if ~exist('spec', 'var') || isempty(spec),
        if ispc,
           spec = 'file:///';
        else
           spec = 'file://';            
        end
    end
    path = strrep(path, '\', '/');
    path = [spec urlencode(path)];
    url = strrep(path, '%2F', '/');
end
