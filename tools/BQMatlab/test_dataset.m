bisque_root = 'http://BISQUE_HOST:9090';
user = 'username';
pass = 'password';

s = bq.Session(user, pass, bisque_root);


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% creating a new dataset using higher level API
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

members = {
    'http://bisque.ece.ucsb.edu/data_service/00-wSNHBdiTN2fdcSSehpfDZc', ...
    'http://bisque.ece.ucsb.edu/data_service/00-CfZ5UrFh5teejLCyyYR3aV', ...
    'http://bisque.ece.ucsb.edu/data_service/00-A3cQsLxCBupcbuDNPxCNLP'
};

dataset = bq.Factory.new('dataset', 'my dataset 2016');
dataset.setValues(members);
dataset = s.store(dataset);

%share an image with another user
dataset.share('dima1', 'read');
dataset.share('dima1', 'edit');

% remove the share with another user
dataset.share('dima1');

% remove dataset and all of its members from the database
dataset.remove(1);

% remove dataset but keep all of its members
dataset.remove();


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% rename some tags within the dataset
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

url = 'http://host/data_service/dataset/635?view=deep';
%dataset = bq.Factory.fetch(url, [], user, pass);
dataset = s.fetch(url);
images = dataset.getValues('object');

for i=1:size(images,2),
    im = bq.Factory.fetch([images{i} '?view=deep'], [], user, pass);
    t = im.tag('height');
    dirty = 0;
    if ~isempty(t),
        t.setAttribute('name', 'Height');
        dirty = 1;        
    end

    t = im.tag('Height ');
    if ~isempty(t),
        t.setAttribute('name', 'Height');
        dirty = 1;                
    end
    
    if dirty == 1,        
        im.save();
    end
end
