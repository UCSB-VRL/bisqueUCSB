function [X Y] = spec_use_tip_finder_ver1(FileName,seedPackage,tipPackage,RAD,PHI,display_corner_sites)

% count the seeds
tm = clock;
NUMS = spec_use_seed_counter_ver1(FileName,seedPackage);
fprintf(['Time to count seeds ' num2str(etime(clock,tm)) '.\n'])


% read the file and sample corners
tm = clock;
I = double(imread(FileName));
[X] = my_corner(I,0,0,1,RAD,PHI);
fprintf(['Time to sample the corners ' num2str(etime(clock,tm)) '.\n'])


% load tip pacckage,
% project data via query conditional sample,
% grade via bayes method
tm = clock;
load(tipPackage)
[D U BV] = spec_QCS_ver1(X,1,[],corner_U,corner_BV);
[post,cpre,logp] = posterior(corner_nb,D);
[JUNK fidx] = sort(post(:,2),'descend');
cpre2 = zeros(size(cpre));
cpre2(fidx(1:NUMS)) = 1;    
fprintf(['Time to sample the isolate the tips ' num2str(etime(clock,tm)) '.\n'])


% view
r = X(:,1);
c = X(:,2);
Y = [X(fidx,:) cpre2(fidx)];
X = X(find(cpre2),:);



if display_corner_sites
    tm = clock;
    imshow(I,[])
    title(num2str(NUMS))
    hold on
    scatter(c,r,'bo')            
    scatter(c(find(cpre)),r(find(cpre)),'ro');     
    scatter(c(find(cpre2)),r(find(cpre2)),'g*');
    fprintf(['Time to sample the view the results ' num2str(etime(clock,tm)) '.\n'])
end


%{
    % test script one
    tic
    FileName = 'Y:\takeshi\Maize\IBM lines\Gravitropism\IBM4s3\400000.tif';
    seedPackage = 'N:\Measure Code\takeshi pipeline\seed_counter.mat';
    cornerPackage = 'N:\Measure Code\takeshi pipeline\tip_counter2.mat';
    RAD = 30;
    PHI = 100;
    [X Y]= spec_use_tip_finder_ver1(FileName,seedPackage,cornerPackage,RAD,PHI,1);
    toc
%}


