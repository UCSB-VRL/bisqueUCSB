%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% user/password based session operations
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
user = 'XXXX';
pass = 'XXXX';
bisque_root = 'http://bisque.ece.ucsb.edu';
s = bq.Session(user, pass, bisque_root);

% list 10 most recent images
images = s.query('image', [], '@ts:desc', 'full', 0, 10);
images{1}.toString()
images{1}.info

% find an exact image matching filename
image = s.find('image', 'filename:"9_DAP_wild_tomato_root_cross_section_2.TIF"', 'deep');
image.toString()
image.info
m = image.getNameValueMap('*');
m.keys()
m.values()


%% shares

image = s.fetch('http://bisque.ece.ucsb.edu/data_service/00-7oisD8Jqm3YerdDMxfdQSj');

%share an image with another user
image.share('dima1', 'read');
image.share('dima1', 'edit');

% remove the share with another user
image.share('dima1');



%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% MEX based session operations
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


% initing session
s = bq.Session('http://vidi.ece.ucsb.edu:9090/data_service/mex/981', 'XXXXXX');

% while running
s.update('RUNNING');

% fetch input tags as a map
inputs = s.mex.getNameValueMap('//tag[@name="inputs"]/tag');
inm = [inputs.keys; inputs.values]';

% fetch some input tags as a map with default values
tags = { 'image_url', 'str', []; 'threshold', 'int', 0; };
mytags = s.mex.findNameValueMap(tags, '//tag[@name="inputs"]/tag[@name=''%s'']');
mym = [mytags.keys; mytags.values]';

% fetch some input tag as a bq.Node
imageurl = s.mex.findValue('//tag[@name="inputs"]/tag[@name="resource_url"]');
% fetch first plane of the first channel
image = s.fetch(imageurl);
im = image.slice(1,1).remap(1).fetch();
imagesc(im);


% fetch some input tags as a cell of bq.Node
ts = s.mex.findNodes('//tag[@name="inputs"]/tag');
value = ts{1}.getAttribute('value');

% navigate in tags by bq.Node
tag = s.mex.tag('inputs');
tag = s.mex.tag('inputs').tag('image_url');
imageurl = tag.getAttribute('value');

s.update('10%');


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% creating results
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

outputs = s.mex.addTag('outputs');
outputs.addTag('my_number_objects', 123);
outputs.addTag('some_float', 456.78);

g = outputs.addGobject('my_gobs2', 'my_gobs2');

g.addGobject('point', '1', [1,2,3] );
g.addGobject('point', '2', [4,5,6] );
g.addGobject('point', '3', [7,8,9] );


p = [1,2,3;4,5,6;7,8,9];
g.addGobject('polyline', 'poly-in-z', p );

p = [1,2,-1,3;4,5,-1,6;7,8,-1,9];
g.addGobject('polyline', 'poly-in-t', p );


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% create new metadata resources
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

resource = bq.Factory.new('project', 'my new project 2016');
resource.addTag('compound', 'caffeine');
resource.addTag('author', 'someone');
resource = s.store(resource);

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% upload files and images
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

f = s.storeFile('my_file.bin');

resource = bq.Factory.new('molecule', 'my_mols/2016/my_file.mol');
resource.addTag('compound', 'caffeine');
f2 = s.storeFile('my_file.mol', resource);

image = zeros(128, 128, 'double');
args = struct('filename', 'my_2d_double_image.ome.tif');
im = s.storeImage(image, args);

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% queries
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%



%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% finish
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

s.finish();





