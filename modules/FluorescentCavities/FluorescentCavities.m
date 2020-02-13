function FluorescentCavities(mex_url, access_token, varargin)
    session = bq.Session(mex_url, access_token);
    try
        dataset_url = session.mex.findValue('//tag[@name="inputs"]/tag[@name="resource_url"]');
        dataset = session.fetch([dataset_url '?view=deep']);
        images = dataset.getValues('object');
        stats = cell(length(images), 5);
        totalStart = tic;
        for i=1:size(images,2),
            fprintf('Processing image: %s\n', images{i});
            image = session.fetch(images{i});
            I = image.command('intensityprojection', 'max').fetch();
            [area, area_avg, area_std] = cavity_segmentation(I);
            stats{i,1} = image.getAttribute('uri');
            stats{i,2} = image.getAttribute('name');
            stats{i,3} = area;
            stats{i,4} = area_avg;
            stats{i,5} = area_std;
        end
        disp(stats); % debugging

        mex_name = session.mex.getAttribute('name');
        mex_id = strsplit(mex_url, '/'); mex_id = mex_id{end};
        dt = datestr(now,'yyyymmddTHHMMss');
        csv_fname = sprintf('areas_%s_%s.csv', dt, mex_id);

        ds = cell2dataset(stats, 'VarNames', {'URI', 'Filename', 'MedianArea', 'AreaAverage', 'AreaStd'});
        export(ds, 'file', csv_fname, 'delimiter', ',');
        fprintf('Total processing time: %.4f seconds\n', toc(totalStart));

        %% Store results
        totalStart = tic;
        fprintf('Storing results\n');

        session.update('90% - storing results');
        outputs = session.mex.addTag('outputs');
        summary = outputs.addTag('summary');
        summary.addTag('Average of areas', mean(ds.MedianArea));
        summary.addTag('Standard deviation of areas', std(ds.MedianArea));
        summary.addTag('Number of empty', length(ds.MedianArea(ds.MedianArea==0)));

        file = sprintf('<resource name="ModuleExecutions/%s/%s_%s/%s" type="table" />', mex_name, dt, mex_id, csv_fname);
        fim = session.storeFile(csv_fname, file);
        outputs.addTag('MedianAreas', fim.getAttribute('uri'), 'table');

        fprintf('Final result:\n%s', outputs.toString()); % debugging
        session.finish();
        fprintf('Storing time: %.4f seconds\n', toc(totalStart));
    catch err
       ErrorMsg = [err.message, 10, 'Stack:', 10];
       for i=1:size(err.stack,1)
           ErrorMsg = [ErrorMsg, '     ', err.stack(i,1).file, ':', num2str(err.stack(i,1).line), ':', err.stack(i,1).name, 10];
       end
       session.fail(ErrorMsg);
    end
end
