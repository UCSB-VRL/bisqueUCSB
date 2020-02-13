url = 'http://bisque.ece.ucsb.edu/data_service/file/1974936';
user = '';
pass = '';

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% fetching a file from Bisque
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
file = bq.Factory.fetch(url, [], user, pass);
% fetch a file with the original file name to the current location
fn = file.fetch( [] );



%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% storing a file into Bisque
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
host = 'http://vidi.ece.ucsb.edu:9090';
user = 'USER';
pass = 'PASS';
%filename = 'PATH\gtrain.model';
%filename = 'PATH\pr-1z.tif';

file = bq.File.store(filename, host, user, pass); 
if ~isempty(file),
    file.setAttribute('permission', 'published');
    file.addTag('about', 'this is a file upload from Matlab API');
    file.save();
end

