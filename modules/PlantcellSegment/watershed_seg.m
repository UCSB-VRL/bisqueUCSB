function [phi]=watershed_seg(input)

d=size(input);

if numel(d)==2
    thresh=analyticsGathering(input);
    t=threshStudy(thresh);
    phi(:,:,1,1)=ImProc(t,input);
elseif numel(d)==3
    for i=1:d(3)
        thresh=analyticsGathering(input(:,:,i));
        t=threshStudy(thresh);
        phi(:,:,i,1)=ImProc(t,input(:,:,i));
    end
else
    for i=1:d(3)
        for j=1:d(4)
            thresh=analyticsGathering(input(:,:,i,j));
            t=threshStudy(thresh);
            phi(:,:,i,j)=ImProc(t,input(:,:,i,j));
        end
    end
end