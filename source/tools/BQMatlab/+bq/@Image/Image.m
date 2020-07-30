% bq.Image
% A class wrapping a Bisque image along with it's pixels
%   Constructor:
%       Image(doc, element, user, password)
%         doc      - URL string or DOM document
%         element  - optional: DOM element
%         user     - optional: string
%         password - optional: string
%   
%   AUTHOR:
%       Dmitry Fedorov, www.dimin.net
%
%   VERSION:
%       0.1 - 2011-06-27 First implementation
%

classdef Image < bq.File
    
    properties
        info = [];
        pixels_url = [];
        meta = [];
    end % properties
    
    methods

        % doc      - URL string or DOM document
        % element  - optional: DOM element
        % user     - optional: string
        % password - optional: string
        function [self] = Image(doc, element, user, password)
            supargs = {};
            if exist('doc', 'var'), supargs{1} = doc; end
            if exist('element', 'var'), supargs{2} = element; end            
            if exist('user', 'var'), supargs{3} = user; end 
            if exist('password', 'var'), supargs{4} = password; end             
            self = self@bq.File(supargs{:});            
            self.init(); 
        end % constructor

        function init(self)
            if isempty(self.doc) || ~self.hasAttribute('uri'),
                return;
            end
            
            uri = self.getAttribute('uri');   
            if ~isempty(self.user) && ~isempty(self.password),
                [self.info, M] = bq.iminfo(uri, self.user, self.password);
            else
                [self.info, M] = bq.iminfo(uri);                
            end
            self.meta = M;
            self.pixels_url = bq.Url(self.info.pixles_url);  
        end % init   
        
        %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        % image_meta - metadata override for mutli-file images
        %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        
        % sets image metadata override needed to correct embedded metadata
        % problems or set proper metadata for multi-file images
        % nz - number of z slices, 1 for none
        % nt - number of time points, 1 for none
        % nc - number of channels, set empty if channels are not stored 
        %      as separate files
        % res - vector with pixel resolution in order: xyzt
        % cnames - cell array with channel names
        function set_image_meta(self, nz, nt, nc, res, cnames)
            image_meta = self.findNode('tag[@name="image_meta" and @type="image_meta"]');
            if isempty(image_meta),
                image_meta = self.addTag('image_meta', 'image_meta', 'image_meta');
            end
            image_meta.addTag('storage', 'multi_file_series');
            image_meta.addTag('dimensions', 'XYCZT');

            image_meta.addTag('image_num_z', nz, 'number');
            image_meta.addTag('image_num_t', nt, 'number');
            if exist('nc', 'var') && ~isempty(nc),
                image_meta.addTag('image_num_c', nc, 'number');
            end
            
            if exist('res', 'var') && ~isempty(res),
                image_meta.addTag('pixel_resolution_x', res(1), 'number');
                image_meta.addTag('pixel_resolution_y', res(2), 'number');
                image_meta.addTag('pixel_resolution_unit_x', 'microns');
                image_meta.addTag('pixel_resolution_unit_y', 'microns');
                if length(res)>2
                    image_meta.addTag('pixel_resolution_z', res(3), 'number');
                    image_meta.addTag('pixel_resolution_unit_z', 'microns');
                end
                if length(res)>3
                    image_meta.addTag('pixel_resolution_unit_t', 'seconds');
                    
                end                
            end
            
            if exist('cnames', 'var') && ~isempty(cnames),
                for i=1:length(cnames),
                    image_meta.addTag(sprintf('channel_%d_name', i), cnames{i});
                end
            end
        end % set_image_meta          
       
        %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        % Pixels
        %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        
        
        % filename - optional: if given and not empty represents a filename to save the image into
        %                      if given but is empty instructs to use resource's name
        % im - the actual image matrix data if no filename was provided or 
        %      the filename where the image was stored        
        function im = fetch(self, filename)
            if exist('filename', 'var')
                if self.pixels_url.hasQuery() == true
                    [im, ~] = bq.connect('GET', self.pixels_url.toString(), filename, [], self.user, self.password);    
                else
                    im = self.fetch@bq.File(filename); 
                end
            else
                im = bq.imreadND(self.pixels_url.toString(), self.user, self.password );
            end
        end % fetch  

        % im - the actual image matrix data if no filename was provided or 
        %      the filename where the image was stored 
        % the difference with fetch is by using TIFF to trasmit data
        function im = load(self)
            filename = tempname;
            self.fetch(filename); 
            t = Tiff(filename, 'r');
            im = read(t);
            t.close();
            delete(filename);
        end % load          
        
        function imo = command(self, command, params)
            imo = copy(self);
            imo.pixels_url.pushQuery(command, params);
        end % command          
        
        function imo = slice(self, z, t)
            if exist('z', 'var') && exist('t', 'var') && ~isempty(z) && ~isempty(t), 
                params = sprintf(',,%d,%d', z, t);
            elseif exist('z', 'var') && (~exist('t', 'var') || isempty(t)), 
                params = sprintf(',,%d,', z);               
            elseif (~exist('z', 'var') || isempty(z)) && exist('t', 'var'), 
                params = sprintf(',,,%d', t);               
            end
            imo = self.command('slice', params);
        end % slice           
        
        % extended slice opration giving access to more dimensions
        function imo = slicex(self, dim, p)
            params = sprintf('%s:%d', dim, p);
            imo = self.command('slice', params);
        end % slicex          
        
        % m = im.remap(1).fetch();
        % m = im.remap([3,2,1]).fetch();
        function imo = remap(self, c)
            params = '';
            for i=1:length(c),
                params = [params sprintf('%d', c(i))];
            end
            imo = self.command('remap', params);
        end % command         
        
        % d - depth: 8|16|32|64
        % m - mode: f|F|d|D|t|T|e|E
        function imo = depth(self, d, m)
            params = sprintf('%d,%s', d, m);
            imo = self.command('depth', params);
        end % depth          
        
        % w,h - width/height
        % m - method: NN or BL, or BC (Nearest neighbor, Bilinear, Bicubic respectively)
        % a - arguments: 'AR' or 'MX' or ''
        function imo = resize(self, w, h, m, a)
            params = sprintf('%d,%d,%s,%s', w, h, m, a);
            imo = self.command('resize', params);
        end % resize          
        
        % returns an RGB image
        function imo = default(self)
            imo = self.command('default', '');
        end % depth              
        
        function imo = roi(self, x1,y1,x2,y2)
            params = sprintf('%d,%d,%d,%d', x1,y1,x2,y2);
            imo = self.command('roi', params);
        end % roi            
        
        function imo = format(self, fmt)
            imo = self.command('format', fmt);
        end % roi            
        
    end% methods
    
    methods (Static)    
        % image - image matrix or a filename
        % args: struct describing the image
        % args.filename
        % args.dim - c z t (as bim.write_ome_tiff requires)
        % args.res - x y z t (as bim.write_ome_tiff requires)
        % node  - bq.Node object of the created resource
        function node = store(image, args, root_url, user, password, resource)
            if ~exist('user', 'var') || isempty(user) || ~exist('password', 'var') || isempty(password),
                error('bq.Image.store:UserCredentialsInvalid', 'Store requires user name and password');
            end        
            
            % if an image was given, store it as OME-TIFF and then upload
            if ~ischar(image),
                if ~exist('args', 'var') || isempty(args),
                    error('bq.Image.store: ImageArgsRequired', 'You must describe the image matrix');
                end                  
                
                if ~isfield(args, 'dim'), args.dim = []; end
                if ~isfield(args, 'res'), args.res = []; end  
                
                s = strsplit(args.filename, '/');
                filename = s{1, size(s, 2)};
                filename = [tempdir filename];
                bim.write_ome_tiff( image, filename, args.dim, args.res);
                if ~exist('resource', 'var') || isempty(resource),
                    resource = ['<image name="', args.filename ,'" />'];
                end
            elseif ~exist('resource', 'var') || isempty(resource),
                filename = image;
                if ~exist('args', 'var') || isempty(args),
                    resource = [];
                else
                    resource = ['<image name="', args.filename ,'" />']; 
                end        
            end            
            node = bq.File.store(filename, root_url, user, password, resource); 
        end % store          
    end % static methods    
    
    methods(Access = protected)
        % Override copyElement method:
        function cpObj = copyElement(obj)
            % Make a shallow copy of all four properties
            cpObj = copyElement@matlab.mixin.Copyable(obj);
            % Make a deep copy of the DeepCp object
            cpObj.pixels_url = copy(obj.pixels_url);
        end
    end    
    
end% classdef
