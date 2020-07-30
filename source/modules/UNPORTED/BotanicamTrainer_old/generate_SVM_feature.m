function generate_SVM_feature(Ig, svmFeatFile)


    % %~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    % % Extract texture features
    % %~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    scale=6;
    orientation=6;
    window_size=64;


    GW = gabor_filter_gen(scale, orientation, window_size);%calculates gabor filter
    
    GF=get_feature_vector_SeparateMB(Ig,scale,orientation,window_size,GW); %calculates features

    

    % %~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    % % save the texture features
    % %~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    %
    fid=fopen(svmFeatFile,'a'); %open the svm feature file

    dummyTag=1;
    NM=size(GF,1);
    for nm=1:NM
        fprintf(fid, ' %d', dummyTag);
        %     fwrite(fid, downsampling, 'uint8');
        %     fwrite(fid, rect, 'uint16');
        for fi=1:size(GF,2)
            fprintf(fid, ' %d:%f', fi, GF(nm,fi));
            %             fwrite(fid, meanF(nm,fi) ,'double');
        end

        fprintf(fid, '\n');
    end

    fclose(fid);
end