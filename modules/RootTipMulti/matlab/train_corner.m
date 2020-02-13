function [nb U BV] = train_corner(seedCounter,seed_U,seed_BV,PATH,RAD,PHI,NDIM)

figure;
cdir = dir(PATH);
cdir(1:2) = [];
SAM = [];
[R T] = ndgrid(linspace(0,RAD,RAD),linspace(-pi,pi,PHI));
Xo = R.*cos(T);
Yo = R.*sin(T);
STK = [];
SV = [];
button = 'Yes';
FeM = [];
SCC = [];

for i = 1:size(cdir,1)
    PATH1 = [PATH cdir(i).name '\'];
    cdir1 = dir(PATH1);
    cdir1(1:2) = [];
    R = [];
    I = double(imread([PATH1 cdir1(1).name]));
    X = my_corner(I,0,1,1,RAD,PHI);
    r = X(:,1);
    c = X(:,2);
       
    % predict
    if i ~= 1            
        % count seeds
        NUMS = use_seed_counter(I,seedCounter,seed_U,seed_BV);        
        % condense
        [D U BV] = QCS(X,1,[],U,BV);        
        [post,cpre,logp] = posterior(nb,D);
        [JUNK fidx] = sort(post(:,2),'descend');
        cpre2 = zeros(size(cpre));
        cpre2(fidx(1:NUMS)) = 1;
        % view
        imshow(I,[]);
        title(num2str(NUMS))
        hold on
        scatter(c,r,'bo')            
        scatter(c(find(cpre)),r(find(cpre)),'ro')        
        scatter(c(find(cpre2)),r(find(cpre2)),'g*')        
        drawnow                    
        button = questdlg('train');
    end
               
          
        
    % stack domain data
    STK = cat(1,STK,X);            

    if strcmp(button,'Yes')
        % gather user data
        [rc cc V] = impixel(I/255);
        tV = zeros(size(r));
        for k = 1:size(rc,1)
            d = [];
            for l = 1:size(r,1)
                d(l) = norm([rc(k) - c(l) cc(k) - r(l)]);
            end
            [JUNK sidx] = min(d);
            tV(sidx) = 1;
        end
    elseif strcmp(button,'No')
        tV = zeros(size(r));
        tV(find(cpre2)) = 1;
    end

    SV = [SV;tV];

    
    % if break then return
    if strcmp(button,'Cancel')
        break
    end
    
    % reduce corner around the corner points
    [D U BV] = QCS(STK(find(SV),:),1,NDIM,[],[]);
    % reduce the dataset around the corner points    
    [D U BV] = QCS(STK,1,[],U,BV);
    
	% train
    nb = NaiveBayes.fit(D,SV,'Distribution','kernel');
    
    % view user data
    imshow(I,[]);
    hold on
    scatter(c,r,'bo')        
    scatter(c(find(tV)),r(find(tV)),'r.')
    drawnow        
    hold off
        

end
