function op = vgg_vis_sup(temp)
op = temp;
supIds = unique(temp);
shuffler = randperm( numel(supIds) );
for iter = 1:numel(supIds)
    op( op == iter) = 3 * shuffler(iter);
end