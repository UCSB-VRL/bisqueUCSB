function [] = seedSize(FilePath)            
    disp = 0;
    % function can be called with path to images
    if nargin == 0
        FilePath = uigetdir();
        FilePath = [FilePath filesep];
    end
    [FileList] = dig(FilePath,{},{'TIF' 'tif'},1);    
    NUMFILE = size(FileList,1);
    % get the common threshold
    % for each image, load-threshold-measure    
    parfor i = 1:NUMFILE   
        MI = measure(FileList{i},[]);                        
        level(i) = MI.threshold;
        csvwrite([FileList{i}(1:end-4) 'I.csv'],MI.SeedSheet);        
    end     
    % for each image load-threshold-measure with common threshold
    MMC = cell(NUMFILE,1);
    parfor i = 1:NUMFILE    
        MC = measure(FileList{i},mean(level));
        MMC{i} = MC;
        csvwrite([FileList{i}(1:end-4) 'C.csv'],MC.SeedSheet);       
    end      
    MMMC1 = [];
    MMMC2 = [];
    for i = 1:numel(MMC)
        NNNC = [mean(MMC{i}.SeedSheet(:,1:3)) std(MMC{i}.SeedSheet(:,1:3)) MMC{i}.SeedCount MMC{i}.threshold MMC{i}.Percent_Clusters(1:2)];
        %IMGNAMEsummary.csv
    %mean(area), mean(minoraxislen), mean(majoraxislen), standarddev(area),
    %standarddev(minoraxislen), standarddev(majoraxislen), seedcount,
    % thresholdused, percentclusters1, percentclusters2
        csvwrite([FileList{i}(1:end-4) 'summary.csv'],NNNC);
        MMMC1 = [MMMC1; [(MMC{i}.SeedSheet(:,1:3)) ]  ];
        MMMC2 = [MMMC2; [MMC{i}.SeedCount MMC{i}.threshold MMC{i}.Percent_Clusters(1:2)]];

    end
    percentseedsperimg =   MMMC2(:,1) ./ sum(MMMC2(:,1)) ;
    weigtedmean = [sum(percentseedsperimg .* MMMC2(:,3)),sum(percentseedsperimg .* MMMC2(:,4))];
    MMMC = [mean(MMMC1), std(MMMC1), sum(MMMC2(:,1)), mean(MMMC2(:,2)),  weigtedmean  ];
    %summary.csv
    %mean(area), mean(minoraxislen), mean(majoraxislen), standarddev(area),
    %standarddev(minoraxislen), standarddev(majoraxislen), total seedcount,
    %mean thresholdused, weighted mean of percentclusters1, weighted mean of percentclusters2
    csvwrite([FilePath filesep 'summary.csv'],MMMC); 
end




%{
    stat_path = 'W:\Candace\Seed Size\NILs\Biotron2010\';
    seedSize(stat_path);
    seedSize('X:\nate\beta - seedscan\speed test\')
%}