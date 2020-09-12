function[thresholdVec]=threshStudy(threshStudyMetrics);
% HIT F5 to run this file
%% Loading the metric - this metric is used to find minimum variance threshold
%load threshStudyMetrics
threshMetrics=threshStudyMetrics;
%%
% set plotTrue = 0 - get only values and no graph
% set plotTrue = 1 - get values as well as graph
numImages = size(threshMetrics,1);
% plotTrue=1;
% xLab='Threshold';
% yLab=['numCells';'avegArea';'varAreas'];
% titleVec=['NumCells vs. Threshold';'AvegArea vs. Threshold';'Variance vs. Threshold'];
% Use the same image numbers from analyticsGathering.m as in imageInd
% for l=1:n,
%     if(plotTrue==1)
%         %f(l)=figure;
%         for k=1:3,
%             %subplot(1,3,k)
%             %plot(threshMetrics(l,1:13,1), threshMetrics(l,1:13,k+1));
%             xlabel(xLab);
%             ylabel(yLab(k,:));
%             title(titleVec(k,:));
%         end
%     end
l=1;
    b=threshMetrics(l,1:13,4);
    minVar(l)=min(b);
    fVec=find(minVar(l)==b);
    if(length(fVec)>1)
        deltaThresh=mean(fVec)-1;  
        thresholdVec(l)=0.02+deltaThresh*0.005;
    else
        thresholdVec(l)=0.02+(fVec-1)*0.005;
    end
% end
%% Print the values
%thresholdVec