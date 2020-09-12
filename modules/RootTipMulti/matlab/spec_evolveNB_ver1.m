function [numMovedUp] = spec_evolveNB_ver1(tipPackage,Data)
load(tipPackage)
[D U BV] = spec_QCS_ver1(Data(:,1:end-1),1,[],corner_U,corner_BV);
nb = corner_nb;
cpre = Data(:,end);
for i = 1:10
    [D corner_U corner_BV] = QCS(Data(find(cpre),1:end-1),1,4,[],[]); 
    [D corner_U corner_BV] = spec_QCS_ver1(Data(:,1:end-1),1,[],corner_U,corner_BV);
    nb = NaiveBayes.fit(D,cpre);
    L = bwlabel(Data(:,end));
    R = regionprops(L,['PixelIdxList']);
    for j = 1:size(R,1)
        if j == size(R,1)
            endidx = size(Data,1);
        else
            endidx = R(j+1).PixelIdxList(1)-1;
        end
        subD = D(R(j).PixelIdxList(1):endidx,:);
        [post,cpre,logp] = posterior(nb,subD);
        [JUNK sidx] = sort(post(:,2),'descend');
        numMovedUp(j) = sum(sidx(1:size(R(j).PixelIdxList,1)) > size(R(j).PixelIdxList,1));
        fprintf(['Number moved up for iteration and set: ' num2str(numMovedUp(j)) ' - ' num2str(i) ' - ' num2str(j) '.\n']);
    end 
    fprintf(['Number of new advacements: ' num2str(sum(numMovedUp)) '.\n']);
    [post,cpre,logp] = posterior(nb,D);
end
corner_nb = nb;
outFILE = [tipPackage(1:end-5) num2str(str2num(tipPackage(end-4))+1) '.mat'];
save(outFILE,'corner_nb','corner_U','corner_BV')

%{
    FilePath = 'N:\Measure Code\takeshi pipeline\results2\samples\';
    cdir = dir(FilePath);
    cdir(1:2) = [];
    SAM = [];
    for i = 1:size(cdir,1)
        SAM = [SAM;dlmread([FilePath cdir(i).name])];
        i
    end
    tipPackage = 'N:\Measure Code\takeshi pipeline\tip_counter2.mat';
    [A] = spec_evolveNB_ver1(tipPackage,SAM);

    % use the new and old on the top 10
    [JUNK sidx] = sort(A,'descend');
    inPATH = 'Y:\takeshi\Maize\IBM lines\Gravitropism\';
    seedPackage = 'N:\Measure Code\takeshi pipeline\seed_counter.mat';
    old_tipPackage = 'N:\Measure Code\takeshi pipeline\tip_counter2.mat';
    new_tipPackage = 'N:\Measure Code\takeshi pipeline\tip_counter3.mat';
    RAD = 30;
    PHI = 100;
    for i = 1:20
        i
        fidx = findstr(cdir(sidx(i)).name,'_');
        FilePath = [inPATH cdir(sidx(i)).name(1:fidx-1) '\']
        [FileList] = getFileList(FilePath,'.TIF');
        FileName = FileList{1};
        spec_use_tip_finder_ver1(FileName,seedPackage,old_tipPackage,RAD,PHI,1);        
        drawnow
        spec_use_tip_finder_ver1(FileName,seedPackage,new_tipPackage,RAD,PHI,1);
        drawnow
    end


%}

