% write_ome_tiff - writies 3-5D OME TIFF files
%
%   INPUT:
%       im       - 3D-5D image matrix
%                  requires XYCZT sequence of dimensions, allows skipping
%                  dimensions with only 1 element,
%                  e.g. 3D image with 1 channel can be XYZ
%       filename - string of file name to write
%       dim      - struct with image dimension:
%                    dim.c, dim.z, dim.t
%                  can be automatically derived for 5D matrix
%                  must be provided for 3D and 4D matrices
%                  for 3D or 4D cases can provide dimension ==0 for autofilling
%                  e.g. XYZ, dim = struct('z', 0)
%       res      - struct with image resolution, if known
%                  res.x, res.y, res.z, res.t
%
%   EXAMPLE:
%
%       bim.write_ome_tiff( im, 'myimage.ome.tif', struct('z', 0), struct('x', 0.6215, 'y', 0.6215, 'z', 1.0));
%
%
%   AUTHOR:
%       Dmitry Fedorov, <www.dimin.net>
%
%   VERSION:
%       1  - 2012-01-11 first implementation

function write_ome_tiff( data, filename, dim, res)
    if ~exist('dim', 'var'), dim=[]; end
    if ~exist('res', 'var'), res=[]; end
    dim = get_image_dims(data, dim);
    if exist('res', 'var') && ~isempty(res), res = ensure_res(res); end
    xml = get_ome_xml(dim, res);
    tif = Tiff(filename, 'w');
    for t=1:dim.t,
        for z=1:dim.z,
            for c=1:dim.c,
                if ndims(data)==2,
                    im = data;
                elseif ndims(data)==3,
                    if dim.c>1,
                       im = data(:,:,c);
                    elseif dim.z>1,
                       im = data(:,:,z);
                    elseif dim.t>1,
                       im = data(:,:,t);
                    end
                elseif ndims(data)==4,
                    if dim.c>1 && dim.z>1,
                       im = data(:,:,c,z);
                    elseif dim.c>1 && dim.t>1,
                       im = data(:,:,c,t);
                    elseif dim.z>1 && dim.t>1,
                       im = data(:,:,z,t);
                    end
                elseif ndims(data)==5,
                    im = data(:,:,c,z,t);
                end

                tags = struct;
                tags.ImageLength         = dim.x;
                tags.ImageWidth          = dim.y;
                tags.Photometric         = Tiff.Photometric.MinIsBlack;
                tags.BitsPerSample       = pixel_bit_depth(im);
                tags.SampleFormat        = pixel_format(im);
                tags.SamplesPerPixel     = 1;
                tags.RowsPerStrip        = 16;
                tags.PlanarConfiguration = Tiff.PlanarConfiguration.Chunky;
                tags.Compression         = Tiff.Compression.LZW;

                tags.Software            = 'bimwrite';
                if c==1 && z==1 && t==1, % only write OME-XML for first page
                    tags.ImageDescription = xml;
                end
                tif.setTag(tags);
                tif.write(im);
                tif.writeDirectory();
            end
        end
    end
    tif.close();
end

function [depth] = pixel_bit_depth(im)
    e = im(ones(1,ndims(im)));
    e = e(1);
    r = whos('e');
    depth = r.bytes*8;
end

function [fmt] = pixel_format(image)
    fmt = Tiff.SampleFormat.UInt;
    if isa(image, 'float'),
        fmt = Tiff.SampleFormat.IEEEFP;
    elseif isa(image, 'int8') || isa(image, 'int16') || ...
           isa(image, 'int32') || isa(image, 'int64'),
        fmt = Tiff.SampleFormat.Int;
    end

end

function [dim] = get_image_dims(im, dim)
    if ~exist('dim', 'var') || isempty(dim),
        dim = struct();
    end
    dim.type = class(im);
    dim.x = size(im,1);
    dim.y = size(im,2);
    if ~isfield(dim, 'c'), dim.c = 1; end
    if ~isfield(dim, 'z'), dim.z = 1; end
    if ~isfield(dim, 't'), dim.t = 1; end

    if ndims(im)==5,
        dim.c = size(im,3);
        dim.z = size(im,4);
        dim.t = size(im,5);
    elseif ndims(im)==2,
        dim.c = 1;
        dim.z = 1;
        dim.t = 1;
    elseif ndims(im)==3 || ndims(im)==4,
        % order is XYCZT
        p = 3;
        if dim.c==0,
            dim.c = size(im,p);
            p=p+1;
        end
        if dim.z==0,
            dim.z = size(im,p);
            p=p+1;
        end
        if dim.t==0,
            dim.t = size(im,p);
            %p=p+1; % not required
        end
    end
end

function [res] = ensure_res(res)
    if ~isfield(res, 'x'), res.x = 0; end
    if ~isfield(res, 'y'), res.y = 0; end
    if ~isfield(res, 'z'), res.z = 0; end
    if ~isfield(res, 't'), res.t = 0; end
end

function [xml] = get_ome_xml(dim, res)
    xml = '<?xml version="1.0" encoding="UTF-8"?>';
    xml = [xml '<OME xmlns="http://www.openmicroscopy.org/XMLschemas/OME/FC/ome.xsd" '];
    xml = [xml 'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '];
    xml = [xml 'xsi:schemaLocation="http://www.openmicroscopy.org/XMLschemas/OME/FC/ome.xsd '];
    xml = [xml 'http://www.openmicroscopy.org/XMLschemas/OME/FC/ome.xsd">'];
    xml = [xml '<Image ID="openmicroscopy.org:Image:1" Name="libbioimage" DefaultPixels="openmicroscopy.org:Pixels:1-1">'];
    xml = [xml '<Pixels ID="openmicroscopy.org:Pixels:1-1" DimensionOrder="XYCZT" BigEndian="false"'];

    d = sprintf(' PixelType="%s" SizeX="%d" SizeY="%d" SizeC="%d" SizeZ="%d" SizeT="%d"',...
                dim.type, dim.x, dim.y, dim.c, dim.z, dim.t);
    xml = [xml d];

    if ~isempty(res),
        r = sprintf(' PhysicalSizeX="%f" PhysicalSizeY="%f" PhysicalSizeZ="%f" TimeIncrement="%f"',...
                    res.x, res.y, res.z, res.t);
        xml = [xml r];
    end

    xml = [xml ' >'];
    xml = [xml '<TiffData/>'];
    xml = [xml '</Pixels>'];
    xml = [xml '</Image>'];
    xml = [xml '</OME>'];
end

