function BotanicamTrainer(mex_url, access_token, query ,tags_of_interest , ClassifierMethod)
    session = bq.Session(mex_url, access_token); 
    try
        % gathering information
        session.update('0% - fetching image urls');
        
        %query the dataset
        queryurl=regexprep(query,'"','%22');
        queryurl=regexprep(queryurl,' ','%20');
        queryurl=regexprep(queryurl,'(','%28');
        queryurl=regexprep(queryurl,')','%29');
        data_service=[session.bisque_root,'/data_service/image/?','tag_query=',queryurl];
        dataset = session.fetch(data_service);
        
        %importing the urls of the images and the tags for those images
        expression = '//image';
        import javax.xml.xpath.*;
        factory = XPathFactory.newInstance;
        xpath = factory.newXPath;    
        xnodes = xpath.evaluate(expression, dataset.element, XPathConstants.NODESET );        
        urls = cell(xnodes.getLength(),1);
        for i=1:xnodes.getLength()
            urls{i} = char(xnodes.item(i-1).getAttribute('uri'));
        end
        tags_of_interest=textscan(tags_of_interest,'%s','Delimiter',',');
        tags=cell(length(tags_of_interest{1}),1);
        for x=1:length(tags_of_interest{1})
            tags{x}=tags_of_interest{1}(x);
        end
        
        %creating the botaniam model folder
        filename=sprintf('BotanicamModel%s.zip',access_token);
        foldername=sprintf('BotanicamModel%s',access_token);
        mkdir(foldername)
        mkdir(foldername,'dictionary')
        
        %% RUN
        %creating a dictionary file
        dic=CreateDictionary(session,urls,ClassifierMethod,tags,foldername);
        ClassificationNumber=dic.Count;
        Classes=dic.keys;
        Values=dic.values;
        [~,order]=sortrows(cell2mat(Values)');
        
        session.update('20% - classifying');
        
        %descriptor calculation
        CalculateDescriptors(session,urls,ClassifierMethod,foldername);

        session.update('70% - training');
        %training calculations
        kernel=2;
        train_svm(kernel,ClassifierMethod,foldername);        

        session.update('90% - uploading training model');
        
        %export the model files to bisque
        removeD=sprintf('%s\\dictionary',foldername);
        rmdir(removeD,'s'); %remove dictionary
        zip(filename,foldername);
        file = session.storeFile(filename);
        %exporting the dictionary as tags and setting the tags to published
        if ~isempty(file),
            file.setAttribute('permission','published');
            file.addTag('Dataset','Botanicam Model');
            c1 = file.addTag('Classes');
            c1.setAttribute('permission','published');
            for x=1:ClassificationNumber
                c2=c1.addTag(num2str(x));
                for y=1:length(tags)
                   Class=textscan(char(Classes{order(x)}),'%s','Delimiter',';');
                   p=c2.addTag(char(tags{y}),char(Class{1}(y)));
                   c2.setAttribute('permission','published');
                   p.setAttribute('permission','published');          
                end
            end
            p=file.addTag('Query',query);
            p.setAttribute('permission','published');
            p=file.addTag('Number of Classifications',ClassificationNumber);
            p.setAttribute('permission','published');
            p=file.addTag('Classification Method',ClassifierMethod);
            p.setAttribute('permission','published');
            file.save();
        end        
        session.update('100% - Finished');
        display('uploaded files');

	 %displays the file created by the module
        query=['"filename":"',filename,'"']; 
        outputs = session.mex.addTag('outputs');
        browser = outputs.addTag('similar_images', query, 'browser');
        
        
        session.finish();
        
    catch err
        ErrorMsg = [err.message, 10, 'Stack:', 10];
        for i=1:size(err.stack,1)
            ErrorMsg = [ErrorMsg, '     ', err.stack(i,1).file, ':', num2str(err.stack(i,1).line), ':', err.stack(i,1).name, 10];
        end
        session.fail(ErrorMsg);
    end
end
