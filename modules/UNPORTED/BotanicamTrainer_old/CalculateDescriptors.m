function CalculateDescriptors(user,pass,urls,ClassifierMethod,foldername)
% main purpose: to calculate the descriptors for images
% requires: session mex
%           urls of the images in the bisque database
%           ClassifierMethod: Bush Descriptor
%                             Leaf Descriptor
% accessories: can take in gobject tagged in the image url but only 
%              rectangles

    %import dictionary and setting contants
    display('importing dictionary');
    
    if strcmp(ClassifierMethod,'Bush Descriptor')
        %for bush descriptor
        dictionarytype=sprintf('%s/dictionary/bush.txt',foldername);       
        scale = 6;
        orientation = 6;
        window_size = 64;
        imgsize = 512;      %the size of the portion to take
        GW = gabor_filter_gen(scale, orientation, window_size);        
        
    elseif strcmp(ClassifierMethod, 'Leaf Descriptor')
        %for leaf descriptor
        dictionarytype=sprintf('%s/dictionary/leaf.txt',foldername);
        D_num=500;     %number of dimensions of descriptor
        threshold=180; %segmenation

    end
    %creating species map    
    df=fopen(dictionarytype,'r'); %has to be able to change
    d2c=containers.Map('KeyType','double','ValueType','char');
    c2d=containers.Map('KeyType','char','ValueType','double');
    while ~feof(df)
        line =fgetl(df);
        s = textscan(line,'%s %s','Delimiter','=');
        c2d(char(s{2}))=str2double(s{1});
        d2c(str2double(s{1}))=char(s{2});
    end
    fclose(df);
    
    %fetch dataset from the query training data set
    display('collecting image info')
    fprintf('Progress:    ');
    tic
    tagtitles=textscan(d2c(0),'%s','Delimiter',';');
    plants=cell(1,length(urls));
    import javax.xml.xpath.*;
    
    for i=1:length(urls),
        
        img = bq.Factory.fetch([urls{i} '?view=deep'],[],user,pass);
        tagvaluelist=[];
        %creates tags for the data set
        factory = XPathFactory.newInstance;
        xpath = factory.newXPath;  
        for x=1:length(tagtitles{1})
            expression = ['//tag[@name="',char(tagtitles{1}(x)),'"]'];
            xnodes = xpath.evaluate(expression, img.element, XPathConstants.NODESET );
            %error messages
            if xnodes.getLength()>1
                %error('error: two tags with the same name');
                warning('Two tags with the same name')
            elseif xnodes.getLength()<1
                %error('error: not tag found on this image with the name %s',char(tagtitles{1}(x)))
                warning('No tag found on this image with the name %s',char(tagtitles{1}(x)),urls{i})
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
    
        try
            plants{i} ={img, c2d(tagvaluelist)}; 
        catch
            warning('Will skip image at %s',urls{i})
            fprintf('Progress:    ');
        end

        fprintf('\b\b\b\b%3d%%',int8(i/length(urls)*100));
    end
    
    fprintf('\n')
    
    elapsedtime=toc;
    fprintf('Elasped Time : %f sec\n',elapsedtime);

    fh = fopen('training_features', 'w');
    
    display('Processing images')
    fprintf('Progress:  0%%');
    tic
    
    %initalizing the xpaths for the boxes
    expression = '//rectangle';
    import javax.xml.xpath.*;
    
    clusters=100; %number of clusters for kmean
    
    for i=1:length(plants)

        %produces image
        if isempty(plants{i})
            continue; %skips images with errors found in the tagging proccess
        else
            I = plants{i}{1}.fetch();
            [h, w, ~] = size(I);

            % fetch gobjects
            factory = XPathFactory.newInstance;
            xpath = factory.newXPath;    
            xnodes = xpath.evaluate(expression, plants{i}{1}.element, XPathConstants.NODESET );
            usecrop=1; %flag to use the crop if no gobject for bush descriptor
            if xnodes.getLength()~=0
                usecrop=0;
                boxes=cell(xnodes.getLength(),1);
                for k=1:xnodes.getLength()
                    if xnodes.item(k-1).getLength()~=2
                        error('error: vertex has too many nodes in it')
                    end
                    %vertex = [x1,y1,x2,y2] x1<x2 , y1<y2
                    for j=1:2
                        x1=str2double(char(xnodes.item(k-1).item(0).getAttribute('x')));
                        x2=str2double(char(xnodes.item(k-1).item(1).getAttribute('x')));
                        if x1>x2  %swaps values if condition is not satisfied
                           x3=x1;
                           x1=x2;
                           x2=x3;
                        end
                        y1=str2double(char(xnodes.item(k-1).item(0).getAttribute('y')));
                        y2=str2double(char(xnodes.item(k-1).item(1).getAttribute('y')));
                        if y1>y2  %swaps values if condition is not satisfied
                           y3=y1;
                           y1=y2;
                           y2=y3;
                        end
                        %condition so that the vertecies are not outside of the
                        %image
                        if x1<1
                            x1=1;
                        end
                        if x2>w
                            x2=w;
                        end
                        if y1<1
                            y1=1;
                        end
                        if y2>h
                            y2=h;
                        end
                        vertex = [y1,y2,x1,x2];  
                    end
                    boxes{k}=vertex;
                end
            else
                vertex=[1,h,1,w];
                boxes={vertex};
            end

            descriptor_total=[];
            
            for x=1:length(boxes)

                 im=I(boxes{x}(1):boxes{x}(2),boxes{x}(3):boxes{x}(4),:); %cuts out a gobject drawn on the image

                %calculate descriptors for each image 
                if strcmp(ClassifierMethod,'Leaf Descriptor')
                    %leaf descriptor
                    FFTD = FFTSD(im, threshold, D_num );
                    S = Sobelhist( im );    
                    descriptor_total=[FFTD,S];

                elseif strcmp(ClassifierMethod, 'Bush Descriptor')
                    %%bush descriptor
                    %if there is no gobject the image a cropped to save time
                    if usecrop==1
                        while max(h, w) > 2000
                            im = imresize(im, 1/2);
                            [h,w] = size(im);
                        end

                        %crop
                        if min(h, w) > imgsize
                            h = floor(h/2);
                            w = floor(w/2);
                            s = floor(imgsize/2);
                            im = im(h-s:h+s-1,w-s:w+s-1);
                        end
                    end
                    descriptor=get_feature_vector_SeparateMB(im,scale,orientation,window_size,GW);
                    descriptor_total=[descriptor_total;descriptor];
                end
                %if the count of the descriptors is less then number of clusters defined kmean does not run 
                if size(descriptor_total,1)>clusters
                    try
                       [~,descriptor_total]=kmeans(descriptor_total,clusters);
                    catch
                       continue;
                    end
                end

            end
        end
        
        %writes descriptor to file to let the svm train analyze
        NM = size(descriptor_total, 1);
        for nm = 1:NM
            fprintf(fh, ' %d', plants{i}{2});
            for fi = 1:size(descriptor_total, 2)
                fprintf(fh, ' %d:%f', fi, descriptor_total(nm, fi));
            end
            fprintf(fh, '\n');
        end
        
        fprintf('\b\b\b\b%3d%%',int8(i/length(plants)*100));
        
    end

    fprintf('\n')
    elapsedtime=toc;
    fprintf('Elasped Time : %f sec\n',elapsedtime);
    fclose(fh);
    
end




