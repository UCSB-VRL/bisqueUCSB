imurl = 'http://bisque.ece.ucsb.edu/data_service/image/161855';

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% using bq.Image
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% fetch image as a matrix
image = bq.Factory.fetch(imurl);
im1 = image.remap(1).fetch();
im2 = image.remap(2).fetch();
figure; imagesc(im1(:,:,6));
figure; imagesc(im2(:,:,6));


% fetch image into a file using its original name
image = bq.Factory.fetch(imurl);
filename = image.fetch([]);

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% reading an image with user and password and show its metadata
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

url = 'http://HOST/data_service/00-mS4EJgtBdWC838EQyG5nCY';
user = 'XXX';
pass = 'XXX';

% image will contain metadata resource describing the image
image = bq.Factory.fetch([url '?view=deep'], [], user, pass); 

% m will contain an N-D matrix with image data
m = image.fetch();

% show annotations

% use xpath to find a value of a specific annotation by name
v = image.findValue('tag[@name="Patient ID"]');

% use xpath to find a value of a specific annotation by type
% here we use a specific DICOM tag type for Patient's Age
v = image.findValue('tag[@type=":///DICOM#0010,1010"]');

% use xpath to find several annotations, here we find all tags
% returned as a Map object
s = image.getNameValueMap('tag');
% for visualization construct a cell array
c = s.keys;
c(2, :) = s.values;


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% storing an image matrix into Bisque
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
host = 'http://vidi.ece.ucsb.edu:9090';
user = 'XXXX';
pass = 'XXXX';


% fastest way of storing image with annotations
filename = 'my_test_N1/my_2d_double_image.ome.tif'; % you can suggest path
image = zeros(128, 128, 'double');
args = struct('filename', filename);

resource = bq.Factory.new('image', filename);
resource.addTag('about', 'this is a 2D image upload from Matlab API');
image = bq.Image.store(image, args, host, user, pass, resource.toString());


% 2D image with no resolution
image = zeros(128, 128, 'double');
args = struct('filename', 'my_2d_double_image.ome.tif');

image = bq.Image.store(image, args, host, user, pass); 
if ~isempty(image),
    image.addTag('about', 'this is a 2D image upload from Matlab API');
    image.save();
end

% 3D image with no resolution
image = zeros(128, 128, 5, 'int16');
args = struct('filename', 'my_3d_XYZ_int16_image.ome.tif');
args.dim = struct('z', 0);
args.res = struct('x', 0.5, 'y', 0.5, 'z', 1.0);

image = bq.Image.store(image, args, host, user, pass); 
if ~isempty(image),
    image.addTag('about', 'this is a 3D image upload from Matlab API');
    image.save();
end

% 4D image with no resolution
image = zeros(128, 128, 2, 5, 'uint16');
args = struct('filename', 'my_3d_XYCZ_uint16_image.ome.tif');
args.dim = struct('c', 0, 'z', 0);
args.res = struct('x', 0.5, 'y', 0.5, 'z', 1.0);

image = bq.Image.store(image, args, host, user, pass); 
if ~isempty(image),
    image.addTag('about', 'this is a 4D image upload from Matlab API');
    image.save();
end

% 5D image with no resolution
image = zeros(128, 128, 2, 5, 10, 'uint8');
args = struct('filename', 'my_3d_XYCZ_uint8_image.ome.tif');
args.res = struct('x', 0.5, 'y', 0.5, 'z', 1.0, 't', 10.0);

image = bq.Image.store(image, args, host, user, pass); 
if ~isempty(image),
    image.addTag('about', 'this is a 5D image upload from Matlab API');
    image.save();
end

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% storing an image file into Bisque
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
host = 'http://vidi.ece.ucsb.edu:9090';
user = 'XXX';
pass = 'XXX';
filename = 'PATH/test_online.tif';

image = bq.Image.store(filename, [], host, user, pass); 
if ~isempty(image),
    image.addTag('about', 'this is an image upload from Matlab API');
    image.save();
end

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% registering a multi-file image from files accessible by the bisque system
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
host = 'http://vidi.ece.ucsb.edu:9090';
user = 'XXX';
pass = 'XXX';

files = {
    'G:\_tests\_test_z_stack\Z0_T000.tif', ...
    'G:\_tests\_test_z_stack\Z1_T000.tif', ...
    'G:\_tests\_test_z_stack\Z2_T000.tif', ...
    'G:\_tests\_test_z_stack\Z3_T000.tif', ...
    'G:\_tests\_test_z_stack\Z4_T000.tif' ...
};

% encode file paths to the url spec, using "file://" for local files
% under windows file:/// because of drive letters
for i=1:length(files),
    files{i} = bq.path2url(files{i});
end

image = bq.Factory.new('image', '_test_z_stack');
image.setValues(files);
image.set_image_meta(length(files), 1, []);

image.addTag('about', 'this is an image upload from Matlab API');
image.addGobject('polyline', 'poly-in-z', [10,20,1;40,50,2;70,80,4] );

s = bq.Session(user, pass, host);
image = s.store(image);

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% lower level API
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% direct reading of a public image by its image service URL
%3D image 512x512x13Zx2C: http://bisque.ece.ucsb.edu/data_service/image/161855
info = bq.iminfo(imurl);
url = bq.Url(info.src);

% read using multi dimentional reader from bisque 
tic;
I4d = bq.imreadND(url.toString());
toc;
figure;
imagesc(I4d(:,:,5));
% Elapsed time is 1.428959 seconds.

url.pushQuery('remap', '1');
tic;
I3d = bq.imreadND(url.toString());
toc;
figure;
imagesc(I3d(:,:,5));
% Elapsed time is 0.787190 seconds.

url.pushQuery('slice', ',,5,');
tic;
I2d = bq.imreadND(url.toString());
toc;
figure;
imagesc(I2d);
% Elapsed time is 0.141409 seconds.

% read using original imread, fetches the temp file and reads using imread
tic;
I2do = bq.imread(url.toString());
toc;
figure;
imagesc(I2do);
% Elapsed time is 0.074946 seconds.