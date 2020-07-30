% bq.Feature
%   
%   AUTHOR:
%       Chris Wheat
%
%   VERSION:
%       0.1   -  2014-09-03 First implementation
%       0.1.1 -  2014-09-04 Changed fetch to a static
classdef Feature < handle
    
    methods (Static)

        % resource_list  - Cell Array 
        % structure:
        %       {{'resource type1','resource url1';'resource type2','resource url2'...};...}
        % name           - string
        % user           - optional: string
        % password       - optional: string
        function [output, info] = fetch(resource_list, name, root_url, user, password, filename)
            
            if ~exist('resource_list', 'var'),
                error('bq.Feature.fetch:NotEnoughArgs', 'Feature request requires resource list');
            end
            
            if ~exist('name', 'var'),
                error('bq.Feature.fetch:NotEnoughArgs', 'Feature request requires feature name');
            end
            
            if ~exist('root_url', 'var'),
                error('bq.Feature.fetch:RequireRootUrl', 'Feature request requires root url');
            end
            
            if ~exist('user', 'var') || isempty(user) || ~exist('password', 'var') || isempty(password),
                error('bq.Feature.fetch:UserCredentialsInvalid', 'Feature request requires user name and password');
            end

            source_url = [root_url '/features/' name '/hdf'];
            
            %create feature request body
            body = bq.Factory.new('resource');
            for i = 1:length(resource_list)
                f = body.doc.createElement('feature');
                body.element.appendChild(f); 
                resource = resource_list{i};
                feature_element = bq.Url(source_url);
                for j = 1:size(resource,1)
                    feature_element.pushQuery(resource{j,1}, resource{j,2})
                end
                f.setAttribute('uri',feature_element.toString()) 
            end

            supargs{1} = 'POST';
            supargs{2} = source_url;
            
            if exist('filename', 'var'), supargs{3} = filename; end %save resulting hdf5 file
 
            supargs{4} = body;
            if ~isempty(user) && ~isempty(password)
                supargs{5} = user; 
                supargs{6} = password;                 
            end
            if exist('filename', 'var')
                [output, info] = bq.connect(supargs{:});
            else
                [output, info] = bq.connect(supargs{:});
                %write everything to a tempfile to read
                ftemp = tempname;
                temp = fopen(ftemp,'w');
                fwrite(temp, output);
                output = h5read(ftemp,'/values');
                fclose(temp); %close temp file
                delete(ftemp); %remove temp
            end
        end % fetch  
    end
    
end% classdef
