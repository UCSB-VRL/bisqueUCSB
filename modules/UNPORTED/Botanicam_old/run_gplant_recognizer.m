function [output] = run_gplant_recognizer(I,foldername,file)
    %takes an input of the image of a plant and the folder the zip file was
    %opened in. This module also requires that the trainer module was run
    %for the bush method to produce the dictionary file and the scale and
    %model files.
    
    %The output is tags of information about the bush identified to be in
    %the image


    % number of trained species =11
    if size(I,3)==3,
        I=rgb2gray(I);
    end

    %downsampling
    [h,w]=size(I);
    while max(h,w)>2000
        I=imresize(I,1/2);
        [h,w]=size(I);
    end

    %crop (cuts a square image which is a multiple of the window size : 512)
    windowsize=512;
    if min(h,w)>windowsize
        h=floor(h/2);
        w=floor(w/2);
        s=floor(windowsize/2);
        I=I(h-s:h+s-1,w-s:w+s-1);
    end

    %%
    %specify the name of feature file to be used by svm classifier

    svmFeatFile='queryFeatFile';

    generate_SVM_feature(I, svmFeatFile);

    %%
    %call the SVM classifier and the trained model
    %runs svm-scale and svm-predict to find the bush that matches the image
    %given to it
    svmOutput='SVMoutput';

    system(sprintf('svm-scale -r %s/bushscaledata %s > %sS',foldername,svmFeatFile,svmFeatFile));
    system(sprintf('svm-predict -b 1 %sS  %s/bushmodel %s', svmFeatFile,foldername, svmOutput));

    %%
    %get the final tag prediction and the confidence from the SVM results
    fh = fopen(svmOutput);
    tags = [];
    [~]=fgetl(fh);%skips first line
    while ~feof(fh)
        line=fgetl(fh);
        tag=textscan(line,'%s');
        tag=str2double(tag{1}(1));
        tags=[tags;tag];  
    end
    table = sortrows(tabulate(tags),3);
    type=table(end,1);
    %confidence=table(end,end);
    fclose(fh);
    
    %%
    %Display the final results
    fprintf('Getting specie for tag: %d', type);
    
    %finding output
    expression = '//file/tag';
    import javax.xml.xpath.*;
    factory = XPathFactory.newInstance;
    xpath = factory.newXPath;    
    xnodes = xpath.evaluate(expression, file.element, XPathConstants.NODESET );
    if isempty(xnodes) || xnodes.getLength()<1,
        error('error: No Botanicam model file found');
    end             

    %find Classes
    flag=0;
    for i=1:xnodes.getLength()
        if strcmp(char(xnodes.item(i-1).getAttribute('name')),'Classes');
            if flag==0
                ClassesNode=i-1;
                flag=1;
            else
                error('error: To many Classes in tags');
            end
        end
    end

    if flag==0
        error('error: no Classes found in tags');
    end

    %find answer and collect tag values
    flag=0;
    for i=1:xnodes.item(ClassesNode).getLength(),
        if strcmp(char(xnodes.item(ClassesNode).item(i-1).getAttribute('name')),num2str(type));
            if flag==0
                output=cell(1,xnodes.item(ClassesNode).item(i-1).getLength());
                for j=1:xnodes.item(ClassesNode).item(i-1).getLength()
                    tagtitles=char(xnodes.item(ClassesNode).item(i-1).item(j-1).getAttribute('name'));
                    tagvalues=char(xnodes.item(ClassesNode).item(i-1).item(j-1).getAttribute('value'));
                    output{j}={{tagtitles},{tagvalues}};
                    flag=1;
                end
            else
               error('error: found too many classifications in the Classes tags');
            end
        end
    end

    if flag==0
        error('error: didnt find the classification in the Classes tags');
    end
    
end
