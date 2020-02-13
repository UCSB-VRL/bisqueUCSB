function multi_mex_runner(mex_url, access_token)
    sess = bq.Session(mex_url, access_token);
    try
        mexs = sess.mex.findNodes('/mex/mex');
        N = length(mexs);
        fprintf('Running in parallel %d images\n\n', N); drawnow('update');
        for i=1:N,
            mex = mexs{i};
            uri = mex.getAttribute('uri');
            value = mex.getValue();     
            if strcmp(value, 'FINISHED')==0,
                r = regexp(uri,'/','split');
                access_token = r{end};
                fprintf('Running: %d/%d - %s\n', i, N, uri); drawnow('update');
                try
                    WatershedSegmentation(uri, access_token);
                catch err
                    fprintf('Error in WatershedSegmentation: %s\n', err.message);
                end                
            else
                fprintf('Skipping: %d/%d - %s\n', i, N, uri); drawnow('update');
            end
        end
        fprintf('\nFinishing the session\n'); drawnow('update');        
        sess.update('FINISHED');
        %sess.finish();
    catch err
        ErrorMsg = [err.message, 10, 'Stack:', 10];
        for i=1:size(err.stack,1)
            ErrorMsg = [ErrorMsg, '     ', err.stack(i,1).file, ':', num2str(err.stack(i,1).line), ':', err.stack(i,1).name, 10];
        end
        sess.fail(ErrorMsg);
    end
end