function dic=CreateDictionary( user,pass, urls , ClassifierMethod , tags_of_interest,foldername )
% main purpose: creates a dictionary for the trainer file creating classes
%               for all the none matching tags
% requires: session mex
%           urls of the images in the bisque database
%           ClassifierMethod: Bush Descriptor
%                             Leaf Descriptor
%           Tags of interest: The names of the tags to be classified.
%                   requirments: have to be in a cell array
%           foldername: the name of the folder where the dictionary will be
%                       stored

    if strcmp(ClassifierMethod,'Bush Descriptor')
        df = fopen(sprintf('%s/dictionary/bush.txt',foldername), 'w');
    elseif strcmp(ClassifierMethod, 'Leaf Descriptor')
        df = fopen(sprintf('%s/dictionary/leaf.txt',foldername), 'w');
    end

    tagnames=[];
    for k=1:length(tags_of_interest)
        if isempty(tagnames)
            tagnames=char(tags_of_interest{k});
        else
            tagnames=[tagnames,';',char(tags_of_interest{k})];
        end
    end
    fprintf(df,'%d', 0);
    fprintf(df, '=%s',tagnames);
    fprintf(df,'\n');


    %creates dictionary files to store the dictionary
    
    import javax.xml.xpath.*;
    fprintf('Progress:    ');
    dic = containers.Map();
    for i=1:length(urls)
        
        fprintf('\b\b\b\b%3d%%',int8(i/length(urls)*100));
        
        img = bq.Factory.fetch([urls{i} '?view=deep'],[],user,pass);
        tagvaluelist=[];
        factory = XPathFactory.newInstance;
        xpath = factory.newXPath;  
        tagvaluelist=[];
        for x=1:length(tags_of_interest)
    
            expression = ['//tag[@name="',char(tags_of_interest{x}),'"]'];
            xnodes = xpath.evaluate(expression, img.element, XPathConstants.NODESET );
            %warning messages
            if xnodes.getLength()>1
                warning('Two tags with the same name')
            elseif xnodes.getLength()<1
                warning('No tag found on this image with the name %s',char(tags_of_interest{x}),urls{i})
            else
                if isempty(char(xnodes.item(0).getAttribute('value')))
                    value='None';
                else
                    value=char(xnodes.item(0).getAttribute('value'));
                end
                if isempty(tagvaluelist)
                    tagvaluelist=value;
                else
                    tagvaluelist=[tagvaluelist,';',value];
                end
            end
        end
        
        if isempty(tagvaluelist)
            warning('Will skip image at %s',urls{i})
            fprintf('Progress:    ');
        elseif not(isKey(dic, tagvaluelist))
            dic(tagvaluelist) = length(dic) + 1;
            fprintf(df,'%d', length(dic));
            fprintf(df, '=%s',tagvaluelist);
            fprintf(df,'\n');
        end
    end
    fclose(df);
end

