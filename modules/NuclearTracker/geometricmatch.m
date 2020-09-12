function framematches = geometricmatch(centroidcells, confidencecell, confidencethreshold, resolution, session)
%centroidcells in an lx1 cell array, where l is the number of frames in the
%data set. resolution is an lx3 matrix which contains the measured
%resolution of every frame as (x,y,z).
sizethreshold=4; % defined as sizethreshold * average nearest centroid distance
l=length(centroidcells);

voxelsize=zeros(l,1);
for i=1:l%computing the voxel size for every frame
    voxelsize(i)=prod(resolution(i,:));
end

[~,svsind]=min(voxelsize); %svsind is indice of smallest voxelsize, so the resolution to which all other frames have to be transformed

scaling=zeros(l,3);
normlocs=cell(l,2);
dists=cell(l,2);
for i=1:l
    scaling(i,:)=resolution(i,:)./resolution(svsind,:); % scalingfactor
    normlocs{i}=centroidcells{i}*diag(scaling(i,:)); %resolution normalizing centroid positions 
    locs=normlocs{i};
    d=zeros(length(locs),length(locs));%computing the distance from every centroid to every centroid
    for j=1:length(locs) %distance computation has been optimized for maximum speed
        d(:,j)=sqrt((locs(j,1)-locs(:,1)).^2+(locs(j,2)-locs(:,2)).^2+(locs(j,3)-locs(:,3)).^2);
    end
    dists{i,1}=d;%saving distance matrix
end

%confidence filtering
for i=1:l
    confidence=confidencecell{i};
    withindices=[confidence';1:length(confidence)]';
    scaledthres=max(confidence)*confidencethreshold;
    originalindices{i}=withindices(confidence>=scaledthres,2);
    templocs=normlocs{i,1};
    normlocs{i,2}=templocs(originalindices{i},:);
    tempdists=dists{i,1};
    dists{i,2}=tempdists(originalindices{i},originalindices{i})';
end

%hash table creation

temp=sort(dists{1});
thres=mean(temp(2,:));
allhashtables=cell(l,1);
for i=1:l
    d=dists{i,2};%getting distances from storage
    hashtables=cell(length(d)*3,1);%precomputing the hashtable storage cell, it's three times the number of centoids as for every centroid three different hash tables are created (by switching basis triplets)
    nlocs=normlocs{i,2};%getting normlalized centroid positions from storage
    for j=3:3:3*length(d)%taking steps of three because we are saving three at a time
        
        withinthres=find(d(j/3,:)<sizethreshold*thres); %finding indices of centroids within threshold distance
        if length(withinthres)>=3,
            sortedbydist=sortrows([withinthres;d(j/3,withinthres)]',2); %sorting them by distance
            orind=sortedbydist(:,1)';%returning to the original indice numbering
            if length(withinthres)>3,
                orind2=[orind(1) orind(3) orind(2) orind(4:end)];%switching second and third basetriplet point
                orind3=[orind(1:2) orind(4) orind(3) orind(5:end)]; %switching third and fourth basetriplet point
            else
                orind2=orind;
                orind3=orind;
            end
            hashtable1.indices=orind;%every hashtable is saved as a struct with the indices of its hash inputs, its hash posititions and its orientation angle
            hashtable1.positions=nlocs(hashtable1.indices,:);
            [hashtable1.hashtable hashtable1.angle]=computehashtable(nlocs(hashtable1.indices(1:3),:),nlocs(hashtable1.indices,:));%computing hashtables
            hashtables{j-2}=hashtable1;%saving to hashtable storage
            
            hashtable2.indices=orind2;
            hashtable2.positions=nlocs(hashtable2.indices,:);
            [hashtable2.hashtable hashtable2.angle]=computehashtable(nlocs(hashtable2.indices(1:3),:),nlocs(hashtable2.indices,:));%computing hashtables
            hashtables{j-1}=hashtable2;%saving to hashtable storage
            
            hashtable3.indices=orind3;
            hashtable3.positions=nlocs(hashtable3.indices,:);
            [hashtable3.hashtable hashtable3.angle]=computehashtable(nlocs(hashtable3.indices(1:3),:),nlocs(hashtable3.indices,:));%computing hashtables
            hashtables{j}=hashtable3;%saving to hashtable storage
        end
    end
    allhashtables{i}=hashtables;
end

%initial matching sequence


for frame=1:l-1
    if exist('session', 'var')
        session.update(sprintf('%d%% - tracking', round(10+frame*80/(l-1))));
    else
        fprintf('%d/%d ', frame, l-1);    
    end
    matchnumber=1;%initiate matchnumber as the first group that has sufficient matches
    matchgroups = {};
    matchgroupsize = [];
    
    set1=allhashtables{frame};%select the hash table storages of the frames that are to be compared
    set2=allhashtables{frame+1};
    for j=1:length(set1);%for every hash table in frame 1
        if isstruct(set1{j})
            a1=set1{j}.angle;% get orientation angle
            hashpos1=set1{j}.hashtable;%hash positions
            btrip1=hashpos1(1:3,:);%basis triplet
            
            for k=1:length(set2); %for every hash table in frame 2
                
                if isstruct(set2{k})
                    a2=set2{k}.angle;
                    hashpos2=set2{k}.hashtable;
                    btrip2=hashpos2(1:3,:);
                    
                    if acos(a1*a2')<pi/2 && sum(sqrt(sum((btrip1-btrip2).^2,2))<thres/2)==3
                        matches=match(hashpos1,hashpos2,thres/2);
                        matchgroups{matchnumber}=[set1{j}.indices(matches(:,1));set2{k}.indices(matches(:,2))]';
                        matchgroupsize(matchnumber)=size(matches,1);
                        matchnumber=matchnumber+1;
                    end
                end
            end
        end
    end
    
    
    % finding matching groups with overlapping matches
    sortedbysize=sortrows([1:length(matchgroupsize);matchgroupsize]',2);
    if size(sortedbysize,1)>501,
        bestgroups = matchgroups(sortedbysize(end-499:end,1));%selecting 500 biggest matching groups
    else
        bestgroups = matchgroups(sortedbysize(:,1));
    end
    
    overlapmatrix=zeros(length(bestgroups),length(bestgroups));%this takes really long for some reason
    for i=1:length(bestgroups)
        mg1=bestgroups{i};
        for j=i:length(bestgroups)
            overlapmatrix(i,j)=length(intersect(mg1,bestgroups{j},'rows'));
        end
    end
    overlapmatrix=overlapmatrix+overlapmatrix';
    
    overlaps=zeros(size(overlapmatrix));
    for i=1:length(bestgroups)
        temp=find(overlapmatrix(i,:));
        overlaps(i,1:length(temp))=temp;
    end
    
    tempoverlaps=zeros(size(overlapmatrix));
    check=0;
    while check==0
        for i=1:length(bestgroups)
            members=overlaps(overlaps(i,overlaps(i,:)>0),:);
            newmembers=unique(members(members>0))';
            tempoverlaps(i,1:length(newmembers))=newmembers;
        end
        check=isequal(tempoverlaps,overlaps);
        overlaps=tempoverlaps;
        tempoverlaps=zeros(size(overlapmatrix));
    end
    
    % putting the matches of overlapping groups together
    overlaps=unique(overlaps,'rows');
    for i=1:size(overlaps,1)
        totalmatches=[];
        for j=1:sum(overlaps(i,:)>0)
            totalmatches=[totalmatches;bestgroups{overlaps(i,j)}];
        end
        filteredmatchgroups{i}=filtermatches(totalmatches);
        nrofmatches(i)=length(filteredmatchgroups{i});
    end
    
    biggestgroup=filteredmatchgroups{nrofmatches==max(nrofmatches)};
    
    %putting high confidence indices into total indices again
    orindf1=originalindices{frame};
    orindf2=originalindices{frame+1};
    referencematches=[orindf1(biggestgroup(:,1)) orindf2(biggestgroup(:,2))];
    
    d=dists{frame,1};
    for i=1:length(d)
        centroidgroupf1{i}=find(d(i,:)<sizethreshold*thres);
    end
    
    d2=dists{frame+1,1};
    for i=1:length(d2)
        centroidgroupf2{i}=find(d2(i,:)<sizethreshold*thres);
    end
    
    locs1=normlocs{frame,1};
    locs2=normlocs{frame+1,1};
    
    nrofmatchesit=[0];
    whilecheck=1;
    while whilecheck==1
        iterativematches=[];
        
        for i=1:size(referencematches,1)
            matcheddists=[referencematches';d(referencematches(i,1),referencematches(:,1))]';
            sorted=sortrows(matcheddists,3);
            basetripletsind=sorted(1:3,1:2);
            
            basetriplet1=locs1(basetripletsind(:,1),:);
            basetriplet2=locs2(basetripletsind(:,2),:);
            
            hash1.indices=centroidgroupf1{basetripletsind(1,1)};
            hash2.indices=centroidgroupf2{basetripletsind(1,2)};
            
            [hash1.hashbase hash1.hashpos]=computehashtableiterative(basetriplet1,locs1(hash1.indices,:));
            [hash2.hashbase hash2.hashpos]=computehashtableiterative(basetriplet2,locs2(hash2.indices,:));
            if sum(sqrt(sum((hash1.hashbase-hash2.hashbase).^2,2))<thres/2)==3
                localmatches=match(hash1.hashpos,hash2.hashpos,thres);
                iterativematches=[iterativematches;[hash1.indices(localmatches(:,1));hash2.indices(localmatches(:,2))]'];
            end
            
        end
        filterediterative=filtermatches(iterativematches);
        nrofmatchesit=[nrofmatchesit;size(filterediterative,1)];
        whilecheck = nrofmatchesit(end)>nrofmatchesit(end-1);
        referencematches=filterediterative;
    end
    framematches{frame}=filtermatchesdivision(iterativematches);
end

end

function [hashtable angle hashbasetriplet]=computehashtable(basetriplet,locs)
%function that redescribes centroid positions of a hash table to intrinsic
%coordinates given 3x3 base triplet matrix and an nx3 position matrix of
%all centroids in the hash table.
origin=mean(basetriplet);

primvec=basetriplet(1,:)-basetriplet(2,:);%not normalized yet
d=1/norm(primvec);primvec=primvec*d;%normalized, multiplication is faster than dividing
secvec=cross(primvec,basetriplet(3,:)-basetriplet(1,:));
d=1/norm(secvec);secvec=secvec*d;
tertvec=cross(primvec,secvec);

angle=(primvec+secvec+tertvec);%orientation of the hash table. This is used to exclude hash table matches.
d=1/norm(angle);angle=d*angle;

centered = locs - origin(ones(size(locs,1),1),:);%subtracting origin from positions
m=[primvec;secvec;tertvec]';
hashtable=centered*m; %redescribing positions to intrinsic coordinate system
end

function [hashbasetriplet hashtable]=computehashtableiterative(basetriplet,locs)
%function that redescribes centroid positions of a hash table to intrinsic
%coordinates given 3x3 base triplet matrix and an nx3 position matrix of
%all centroids in the hash table.
origin=mean(basetriplet);

primvec=basetriplet(1,:)-basetriplet(2,:);%not normalized yet
d=1/norm(primvec);primvec=primvec*d;%normalized, multiplication is faster than dividing
secvec=cross(primvec,basetriplet(3,:)-basetriplet(1,:));
d=1/norm(secvec);secvec=secvec*d;
tertvec=cross(primvec,secvec);

centered = locs - origin(ones(size(locs,1),1),:);%subtracting origin from positions
m=[primvec;secvec;tertvec]';
hashtable=centered*m; %redescribing positions to intrinsic coordinate system
centeredbase=basetriplet-origin(ones(size(basetriplet,1),1),:);
hashbasetriplet=centeredbase*m;
end

function matches=match(ht1,ht2,thres)
prematches=zeros(length(ht1),3);
for i=1:length(ht1) %distance computation has been optimized for maximum speed
        d=sqrt((ht1(i,1)-ht2(:,1)).^2+(ht1(i,2)-ht2(:,2)).^2+(ht1(i,3)-ht2(:,3)).^2);
        mind=min(d);
        prematches(i,:)=[i find(d==mind,1) mind];
end
prematches=prematches(prematches(:,3)<thres,1:3);
u=unique(prematches(:,2));
if length(u)==size(prematches,1)
    matches=prematches;
else
    matches=zeros(length(u),2);
    for i=1:length(u)
        sorted=sortrows(prematches(prematches(:,2)==u(i),1:3),3);
        matches(i,1:2)=sorted(1,1:2);
    end
end
end

function nodoubles=filtermatches(rawmatches)
%count all occurrences of every match
umatches=unique(rawmatches,'rows');
for i=1:length(umatches)
    for j=1:length(rawmatches)
        sametest(j)=isequal(rawmatches(j,:),umatches(i,:));
    end
    occurrencesind{i}=find(sametest);
    occurrences(i)=sum(sametest);
end
%remove all double second matches (no two cells can divide into a single
%following cell)

usecond=unique(rawmatches(:,2));
nodoublesecond=zeros(size(usecond,1),2); %here the matches without double second occurrences will be saved
newoccurrences=zeros(size(usecond,1),1);
for i=1:length(usecond)
        ind=find(umatches(:,2)==usecond(i));
        if length(ind)>1 %if more than one different match connects to a second cell
            secondocc=occurrences(ind);%find the occurrences
            secondind=find(secondocc==max(secondocc));%find the one with the most occurrences
            if length(secondind)>1 % if several matches have the same number of max occurrences
                nodoublesecond(i,:)=umatches(ind(secondind(1)),:); %select the first one
                newoccurrences(i)=secondocc(secondind(1));
            else
                nodoublesecond(i,:)=umatches(ind(secondind),:);%select the one with the most occurrences
                newoccurrences(i)=secondocc(secondind);
            end
        else
            nodoublesecond(i,:)=umatches(ind,:); %if no multiple occurrences, just select it
            newoccurrences(i)=occurrences(i);
        end
end

%remove all first double matches
ufirst=unique(nodoublesecond(:,1));
nodoubles=zeros(size(ufirst,1),2);
for i=1:length(ufirst)
    ind=find(nodoublesecond(:,1)==ufirst(i));
    if length(ind)>1 %if a cell is detected to divide into two or more cells
        firstocc=newoccurrences(ind);
        firstind=find(firstocc==max(firstocc));
        if length(firstind)>1
            nodoubles(i,:)=nodoublesecond(ind(firstind(1)),:);
        else
            nodoubles(i,:)=nodoublesecond(ind(firstind),:);
        end
    else
        nodoubles(i,:)=nodoublesecond(ind,:);
    end
end
end

function nodoubles=filtermatchesdivision(rawmatches)
%count all occurrences of every match
umatches=unique(rawmatches,'rows');
for i=1:length(umatches)
    for j=1:length(rawmatches)
        sametest(j)=isequal(rawmatches(j,:),umatches(i,:));
    end
    occurrencesind{i}=find(sametest);
    occurrences(i)=sum(sametest);
end
%remove all double second matches (no two cells can divide into a single
%following cell)

usecond=unique(rawmatches(:,2));
nodoublesecond=zeros(size(usecond,1),2); %here the matches without double second occurrences will be saved
newoccurrences=zeros(size(usecond,1),1);
for i=1:length(usecond)
        ind=find(umatches(:,2)==usecond(i));
        if length(ind)>1 %if more than one different match connects to a second cell
            secondocc=occurrences(ind);%find the occurrences
            secondind=find(secondocc==max(secondocc));%find the one with the most occurrences
            if length(secondind)>1 % if several matches have the same number of max occurrences
                nodoublesecond(i,:)=umatches(ind(secondind(1)),:); %select the first one
                newoccurrences(i)=secondocc(secondind(1));
            else
                nodoublesecond(i,:)=umatches(ind(secondind),:);%select the one with the most occurrences
                newoccurrences(i)=secondocc(secondind);
            end
        else
            nodoublesecond(i,:)=umatches(ind,:); %if no multiple occurrences, just select it
            newoccurrences(i)=occurrences(i);
        end
end

%remove all triple first occurrences (a first cell can occur at most twice,
%once for every dividing daughter cell)
ufirst=unique(nodoublesecond(:,1));
nodoubles=[];
for i=1:length(ufirst)
    ind=find(nodoublesecond(:,1)==ufirst(i));
    if length(ind)>2 %if a cell is detected to divide into more than 2 cells
        firstocc=sortrows([ind newoccurrences(ind)],2);
        nodoubles=[nodoubles;nodoublesecond(firstocc(end-1:end,1),:)];      
    else
        nodoubles=[nodoubles;nodoublesecond(ind,:)];
    end
end
end