user = '';
pass = '';
image_url = 'http://bisque.ece.ucsb.edu/data_service/00-cSqpgp8ZDhAjyjocvKiak7';

image = bq.Factory.fetch([image_url '?view=deep'], [], user, pass); 


min_sz = 60;
l = 0;
tsz = 512;
cells = {};

% fetch tiles
for tx = 134:135,
    for ty = 73:74,
        x = tx*512;
        y = ty*512;    

        %.command('transform', 'rgb2hsv').command('remap', '1')
        tile = sprintf('%d,%d,%d,%d', l, tx, ty, tsz);
        im = image.slice(1,1).command('tile', tile).depth(8, 'f').fetch();

        imagesc(im);

        % if we fetched RGB image, use Hue, skip otherwise
        HSV = rgb2hsv(im);
        I = HSV(:,:,3);
        I = uint8( (1-I)*255  );
        I = medfilt2(I, [11,11], 'symmetric');
        imagesc(I);

        [nrows, ncols] = size(I);
        I = reshape(I, nrows*ncols, 1);
        [cluster_idx, cluster_center] = kmeans(double(I), 3, 'distance','sqEuclidean', 'Replicates', 3);
        labels = reshape(cluster_idx, nrows, ncols);
        [v,p] = max(cluster_center);
        labels(labels~=p) = 0;
        level = graythresh(labels);
        labels = im2bw(labels, level);
        figure; imagesc(labels);

        cs = bwboundaries(labels, 'noholes');

        for j=1:length(cs),
            v = cs{j};
            if length(v) > min_sz,
                v = v + repmat([y,x], length(v), 1);
                v = reduce_poly(v', 40)';
                cells{end+1,1} = v;
            end
        end
    end % for ty
end % for tx

g = image.addGobject('cells', 'cells');
for j=1:length(cells),
    v = cells{j};
    name = sprintf('cells-%d', j);
    g.addGobject('polygon', name, v );
end

image.save();

