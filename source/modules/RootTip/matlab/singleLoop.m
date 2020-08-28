function [A MID] = getMidlines(PATHIN,midO,disp)
matlabpool 4
RAD = 70;
[R T] = ndgrid(linspace(0,RAD,RAD),linspace(-pi,pi,100));
X1 = R.*cos(T);
X2 = R.*sin(T);
MID = [];
NF = size(PATHIN,2);
for p = 1:NF
    FileList = spec_getFileList(PATHIN{p},'.TIF');
    tMID = [];
    parfor i = 1:size(FileList,2)
        % read the image
        I = imread(FileList{i});        
        level = graythresh(I);
        B = ~im2bw(I,level);
        B = bwareaopen(B,1000);
        B = imclose(B,strel('disk',11));
        B = imopen(B,strel('disk',3));
        % get the tip
        tip = getTip(B);
        SAM = interp2(B,X1 + tip(2),X2 + tip(1));
        fidx = find(SAM);
        [SIM U BV L COEFFS ERR] = PCA_FIT([X1(fidx) X2(fidx)],2);
        % trace the midline       
        if midO
            tMID(i) = getMidline(B,tip);
        end
        
        if ~interp2(B,tip(2) + 5*BV(1),tip(1) + 5*BV(2))
            BV(:,1) = -BV(:,1);
        end
        
        tA(i) = atan2(BV(2,1),BV(1,1));
        fprintf(['Done with ' num2str(i) ' of ' num2str(size(FileList,2)) '\n'])
        %{
        if disp 
            %subplot(1,2,1)
            imshow(I,[]);            
            hold on;
            scatter(tip(2),tip(1),'r*');    
            quiver(tip(2),tip(1),BV(1,1),BV(2,1),500,'r');
            quiver(tip(2),tip(1),-BV(1,1),-BV(2,1),500,'b');
            scatter(X1(fidx)+tip(2),X2(fidx)+tip(1),'c.')
            scatter(tip(2) + 5*BV(1),tip(1) + 5*BV(2),'g*')
            if midO
                plot(MID{p}{i}(:,2),MID{p}{i}(:,1),'r')
            end
            hold off
            %{
            subplot(1,2,2)
            plot(A{p})
            %}
            drawnow
        end
        %}
        
    end
    MID{p} = tMID;
    A{p} = tA;
end
matlabpool close

function [TIP] = getTip(B)
    fidx = find(B(:,end));
    W = bwtraceboundary(B,[fidx(1) size(B,2)],'NW',8,inf,'counterclockwise');
    CLIP = 100;
    WSIZE = 20;
    D1X1 = cwt(W(:,1),[WSIZE],'gaus1');
    D1X2 = cwt(W(:,2),[WSIZE],'gaus1');
    D2X1 = cwt(W(:,1),[WSIZE],'gaus2');
    D2X2 = cwt(W(:,2),[WSIZE],'gaus2');
    K = (D1X1.*D2X2 - D1X2.*D2X1).*(D1X1.^2 + D1X2.^2).^-3/2;
    [JUNK fidx] = max(K(CLIP:end-CLIP));
    fidx = fidx + CLIP;
    TIP = W(fidx,:);
    
    
function [MID] = getMidline(B,TIP)
    PD = 200;
    
    TI = zeros(size(B));
    TI(TIP(1),TIP(2)) = 1;
    
        
    B = padarray(B,[0 PD],'replicate','post');
    S = bwmorph(B,'skel',inf);
    B = B(:,1:end-(PD));
    S = S(:,1:end-(PD));
    
    SI = zeros(size(B));
    sidx = find(S(:,end));
    SI(sidx(1),end) = 1;
    
    
    [r c] = find(S);
    dist = (r-TIP(1)).^2 + (c-TIP(2)).^2;
    [JUNK sidx] = min(dist);
    X1 = [linspace(TIP(1),r(sidx),100)' linspace(TIP(2),c(sidx),100)'];
    X1 = unique(round(X1),'rows');
    for i = 1:size(X1,1)
        S(X1(i,1),X1(i,2)) = 1;
    end    
    %special spur
    J = (imfilter(double(S),ones(3)) .* double(S)) >= 4;    
    %J = bwmorph(S,'branchpoints');
    D = S - J;
    E = bwmorph(S,'endpoints') - TI - SI;    
    tic
    while sum(E(:)) ~= 0
        J = (imfilter(double(S),ones(3)) .* double(S)) >= 4;                  
        D = S - J;
        D = ~imfill(~logical(D),find(E),8);
        D = D + J;
        D = bwmorph(D,'skel',inf);
        S = D;
        D = S - J;        
        E = bwmorph(S,'endpoints') - TI - SI;
    end
    toc    
    % repeat spur
    MID = [];
    tic        
    [r c] = find(TI);
    S(r,c) = 0;    
    MID = [r c];
    [r c] = find(S);
    NP = size(r,1);
    for i = 1:NP
        i
        NP
        [JUNK sidx] = min((r - MID(i,1)).^2 + (c - MID(i,2)).^2);
        MID(i+1,:) = [r(sidx) c(sidx)];
        r(sidx) = [];
        c(sidx) = [];
    end
    
    
    
    
%{
    
    PATHIN{1} = 'Y:\nate\sense\';
    [A MID] = singleLoop(PATHIN,0,0);
%}

%{
DPATH = 'Y:\nate\amy\data\';
cdir = dir(DPATH);
cdir(1:2) = [];
for i = 1:size(cdir,1)
    PATHIN{i} = [DPATH cdir(i).name '\'];
end
[A MID] = getMidlines(PATHIN,0,0);
    
%}

%{
    AN = cell2mat(A');
    ridx = find(any(abs(diff(AN*180/pi,1,2)) > 20,2));   
    PATHIN(ridx) = [];
    AN(ridx,:) = [];
    ridx    
    

    plot(-AN([3 7 10],:))
    plot(-AN([3 7 10],:)','b')
    hold on
    plot(-AN([1:2 4:6 8:9],:)','r')
    
    
    for i = 1:size(AN,1)
        DEL(i,:) = AN(i,:) - AN(i,1);
    end
    plot(-DEL([3 7 10],:))
    plot(-DEL([3 7 10],:)','b')
    hold on
    plot(-DEL([1:2 4:6 8:9],:)','r');
    
    for i = 1:size(AN,1)
        D(i,:) = cwt(AN(i,:),4,'gaus1');
    end    
    plot(-D([3 7 10],10:end-10))
    plot(-D([3 7 10],10:end-10)','b')
    hold on
    plot(-D([1:2 4:6 8:9],10:end-10)','r');
    
    
%}
    
    
%{

%}


