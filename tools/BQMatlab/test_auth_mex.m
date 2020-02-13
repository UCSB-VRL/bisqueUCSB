mex_url = 'http://HOST/module_service/mex/UUID';
auth_key = '';
url = 'http://HOST/data_service/00-T2J3fYGFJKADzaTXE8nmog';

s = bq.Session(mex_url, auth_key);

% fetch image as a matrix
image = s.fetch(url);
image.info

%im1 = image.command('slice', 'fov:300').fetch();
im1 = image.slicex('fov', 300).format('tiff').load();
figure; imagesc(im1(:,:,1));
