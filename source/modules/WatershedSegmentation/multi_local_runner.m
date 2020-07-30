function multi_local_runner(path)
    files = dir([ path '*.jpg']);
    N = length(files);
    fprintf('Running in parallel %d images\n\n', N); drawnow('update');
    outputs = bq.Factory.new('tag', 'outputs');
    tic;
    for i=1:N,
        filename = [path files(i).name];
        fprintf('%d/%d\n', i, N); drawnow('update');
        WatershedSegmentation2(filename, outputs);
    end
    outputs.save([path 'outputs.xml']);    
    toc;
    disp(outputs.toString());
end