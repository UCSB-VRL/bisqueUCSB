user = 'my_user';
pass = 'my_pass';
bisque_root = 'http://bisque.ece.ucsb.edu';
image_url = [bisque_root '/data_service/00-dcJZKvcHcmKLwQoktSgnfP'];

s = bq.Session(user, pass, bisque_root);
image = s.fetch([image_url '?view=deep']);

polygons = image.findNodes('//polygon');
areas = zeros(length(polygons),1);
for i=1:length(polygons),
    poly = polygons{i}.getVertices();
    a = polyarea(poly(:,1), poly(:,2));
    areas(i) = a;
end

idx = kmeans(areas, 3);

colors = cell(3,1);
colors{1} = '#FF0000';
colors{2} = '#FFFF00';
colors{3} = '#0000FF';

for i=1:length(polygons),
    polygons{i}.addTag('area', areas(i) );
    polygons{i}.addTag('class', num2str(idx(i)) );
    polygons{i}.addTag('color', colors{idx(i)} );
end

image.save();

