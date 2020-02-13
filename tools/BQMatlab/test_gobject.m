url = 'http://bisque.ece.ucsb.edu/data_service/image/765131?view=deep';

% get gobject in the image
image = bq.Factory.fetch(url);

poly = image.findNode('//polygon[@name="Hippocampus"]');
vx1 = poly.getVertices();

point = image.findNode('//gobject[@name="PHF+ Cell"]/point[@name="Centroid"]');
vx2 = point.getVertices();

