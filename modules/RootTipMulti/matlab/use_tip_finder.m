function [X] = use_tip_finder(I,RAD,PHI,corner_nb,corner_U,corner_BV,seed_nb,seed_U,seed_BV,disp1,disp2)
NUMS = use_seed_counter(I,seed_nb,seed_U,seed_BV);
[X] = my_corner(I,disp1,1,1,RAD,PHI);
[D U BV] = QCS(X,1,[],corner_U,corner_BV);
% run simulation
[post,cpre,logp] = posterior(corner_nb,D);
[JUNK fidx] = sort(post(:,2),'descend');
cpre2 = zeros(size(cpre));
cpre2(fidx(1:NUMS)) = 1;    
% find the next 3
cpre3 = zeros(size(cpre));
cpre3(fidx(NUMS+1:NUMS+3)) = 1;    
% view
r = X(:,1);
c = X(:,2);
X = X(find(cpre2),:);
if disp2
    if ~disp1
        imshow(I,[]);
    end
    title(num2str(NUMS))
    hold on
    scatter(c,r,'bo')            
    scatter(c(find(cpre)),r(find(cpre)),'ro')        
    scatter(c(find(cpre2)),r(find(cpre2)),'g*')        
    scatter(c(find(cpre3)),r(find(cpre3)),'m*')   
end


