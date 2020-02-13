function [area, area_avg, area_std] = cavity_segmentation(I)
    level = graythresh(I);
    I = 1 - im2bw(I, level);
    %imagesc(I);

    cs = bwboundaries(I, 'noholes');

    %sz = zeros(size(cs));
    areas = zeros(size(cs));
    for j=1:length(cs),
        v = cs{j};
        if length(v)>3,
            %sz(j) = length(v);
            areas(j) = polyarea(v(:,1), v(:,2));
        end
    end

    %th = median(areas) + std(areas);
    th = (size(I, 1)*size(I, 2)) / 30;
    %sz(areas>th) = 0;
    areas(areas>th) = 0;
    
    area = median(areas(areas>0));
    area_avg = mean(areas(areas>0));
    area_std = std(areas(areas>0));
    if isnan(area),
       area = 0;
    end
    if isnan(area_avg),
       area_avg = 0;
    end
    if isnan(area_std),
       area_std = 0;
    end    
end

