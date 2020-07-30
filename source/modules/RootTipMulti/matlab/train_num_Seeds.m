function [nb U BV] = train_num_Seeds(PATH,NDIM)
cdir = dir(PATH);
cdir(1:2) = [];
STK = [];
SV = [];
button = 'Yes';
for i = 1:size(cdir,1)
    PATH1 = [PATH cdir(i).name '\'];
    cdir1 = dir(PATH1);
    cdir1(1:2) = [];
    R = [];
    I = double(imread([PATH1 cdir1(1).name]));
    
    % gather domain data
    J = imresize(I,1);
    J = imfilter(J,fspecial('average',32));
    background = imclose(J,strel('disk',60));
    J = double(J) - double(background);
    J = J - min(J(:));
    J = J / max(J(:));
    level = graythresh(J);
    B = ~im2bw(J,level);
    B = imclearborder(B);
    B = bwareaopen(B,250);
    E = edge(B);
    L = bwlabel(B);        
    R = regionprops(L,'Centroid','Area','Image','Eccentricity','MajorAxisLength','MinorAxisLength','Solidity','PixelIdxList');
    TEMP = [[R.Area];[R.Eccentricity];[R.MajorAxisLength];[R.MinorAxisLength];[R.Solidity];reshape([R.Centroid],[2 size(R,1)])]';
    
    % predict
    if i ~= 1            
        [SIM C ERR] = PCA_REPROJ(TEMP(:,1:end-2),BV,U);                
        C = [C ERR TEMP(:,end-1)];

        % run simulation
        [post,cpre,logp] = posterior(nb,C);
        cpre(isnan(cpre)) = 0;
        % view
        Z = zeros(size(I));
        sidx = find(cpre);
        for i = 1:size(sidx,1)
            Z(R(sidx(i)).PixelIdxList) = 1;
        end
        subplot(1,2,1)
        imshow(Z,[])
        subplot(1,2,2)
        imshow(I,[]);        
        drawnow
        button = questdlg('train');
    end
               
          
        
    % stack domain data
    STK = cat(1,STK,TEMP);            

    if strcmp(button,'Yes')
        tV = [];
        % gather user data
        for k = 1:size(R,1)
            figure
            imshow(R(k).Image)
            if strcmp(questdlg('seed'),'Yes')
                tV(k) = 1;
            else
                tV(k) = 0;
            end
            close
            
        end
    elseif strcmp(button,'No')
        tV = zeros(1,size(R,1));
        tV(find(cpre)) = 1;
    end

    SV = [SV;tV'];

    % reduce
    [SIM U BV L C ERR] = PCA_FIT(STK(find(SV),1:end-2),NDIM);
    [SIM pC ERR] = PCA_REPROJ(STK(:,1:end-2),BV,U);
    pC = [pC ERR STK(:,end-1)];

    if strcmp(button,'Cancel')
        break
    end
    
    % train
    nb = NaiveBayes.fit(pC,SV,'Distribution','kernel');
        

end
