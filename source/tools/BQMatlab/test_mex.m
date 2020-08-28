url = 'http://BISQUE_HOST:9090';
user = 'username';
pass = 'password';
module_url = '/module_service/MyData'

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% running a module using a higher level API
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

mex = bq.Factory.new('mex');
inputs = mex.addTag('inputs'); 
inputs.addTag('mex_url', '', 'system-input'); 
inputs.addTag('bisque_token', '', 'system-input'); 
inputs.addTag('image_url', 'http://bisque_root/some_image'); 
mex.save([url module_url '/execute'], user, pass);


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% running a module using lower level post
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

mex = [];
mex = [input sprintf('<mex>\n')];
mex = [input sprintf('<tag name="inputs">\n')];
mex = [input sprintf('   <tag type="system-input" name="mex_url" />\n')];
mex = [input sprintf('   <tag type="system-input" name="bisque_token" />\n')];
mex = [input sprintf('   <tag name="image_url" value="http://bisque_root/some_image" />\n')];
mex = [input sprintf('</tag>\n')];
mex = [input sprintf('</mex>\n')];

bq.post([url module_url '/execute'], mex, user, pass);


