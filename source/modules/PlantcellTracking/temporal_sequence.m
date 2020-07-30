function [sequence,c] = temporal_sequence(segmentedImage)

d=size(segmentedImage,4);

for j=1:d
    cord{j}=regionprops(bwlabeln(segmentedImage(:,:,:,j)),'pixellist','PixelIdxList', 'centroid');
end

for j=1:d-1
    c{j}=full_tracking2(segmentedImage(:,:,:,j),segmentedImage(:,:,:,j+1),4,4,50,1,1);
    lineage{j}=lineage_structure(c{j});
end

[ind{1},ind{2}]=find(c{1}>0); 
noCells=length(ind{1});

for i=1:noCells %the ith cell
    s{1}=ind{1}(i);
    for t=2:d %the t time
        s{t}=[];
        for ii=1:length(s{t-1})
            s_temp=lineage{t-1}(s{t-1}(ii)).daughters;
            s{t}=[s{t},s_temp];
        end
    end
    sequence{i}=s;
end

for j=2:d-1
    c_matrix=c{j};
    [ind_1,ind_2]=find(c_matrix>0);
    for jj=1:length(ind_1) %# of new cells being tracked starting from the jth time point
        if isempty(find(c{j-1}(:,ind_1(jj))>0))==1
            noCells=noCells+1;
            for jjj=1:j-1
                s{jjj}=[];
            end
            s{j}=ind_1(jj);
            for t=j+1:d %the t time
                s{t}=[];
                for ii=1:length(s{t-1})
                    s_temp=lineage{t-1}(s{t-1}(ii)).daughters;
                    s{t}=[s{t},s_temp];
                end
            end
            sequence{noCells}=s;
        end
    end
end