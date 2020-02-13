function [MID] = SPEC_getMidlines(FileList,midO,disp)

RAD = 70;
[R T] = ndgrid(linspace(0,RAD,RAD),linspace(-pi,pi,100));
X1 = R.*cos(T);
X2 = R.*sin(T);
MID = [];

    for i = 1:size(FileList,1)
        % read the image
        FileList{i}
        I = imread(FileList{i});        
        [I] = handleFLIP(I);
        I = fliplr(I);
        I = imclose(I,strel('disk',5));
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
        MID{i} = getMidline(B,tip);
        
        fprintf(['Done with ' num2str(i) ' of ' num2str(size(FileList,2)) '\n'])

        if disp 
            %subplot(1,2,1)
            imshow(I,[]);            
            hold on;
            scatter(tip(2),tip(1),'r*');    
            quiver(tip(2),tip(1),BV(1,1),BV(2,1),500,'r');
            quiver(tip(2),tip(1),-BV(1,1),-BV(2,1),500,'b');
            scatter(X1(fidx)+tip(2),X2(fidx)+tip(1),'c.')
            scatter(tip(2) + 5*BV(1),tip(1) + 5*BV(2),'g*')
            plot(MID{i}(:,2),MID{i}(:,1),'r')            
            drawnow
        end
    end
%matlabpool close

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
FilePath = 'Y:\nate\amy\data\chf gravitropism test\';
FilePath = 'Y:\nate\amy\data\MS .5\';
FileList = {};
FileExt = {'tif','TIF'};
FileList = Wdig(FilePath,FileList,FileExt,1);
clear name pathstr NUMname
    
for i = 1:size(FileList,1)
%    [pathstr{i}, name{i}, ext{i}, versn] = fileparts(FileList{i});
    [pathstr{i}, name{i}, ext{i}] = fileparts(FileList{i});
    pathstr{i} = [pathstr{i} '\'];
    NUMname(i) = str2num(name{i});
end
fidx = find(NUMname == 43020);
FileList = FileList(fidx);
[MID] = SPEC_getMidlines(FileList,1,1);
pathstr = pathstr(fidx);
clear genoType
for i = 1:size(pathstr,2)
    fidx = findstr(pathstr{i},'_');    
    genoType{i} = pathstr{i}(fidx(end)+1:end-1);   
end

nG = [];
ridx = find(strcmp(genoType,'wt'));
for i = 1:size(ridx,2)
    genoType{ridx(i)} = 'WT';
end
    
    
U = unique(genoType);
for i = 1:size(U,2)
    for j = 1:size(genoType,2)
        if strcmp(genoType{j},U(i))
            nG(j) = i;
        end
    end    
end
    
    
    
%K = Kur(MID,10,5,350,15);
K = Kur(MID,10,5,600,15);    
K = K(:,25:end-25);
ridx = find(any(K < -0.04,2));    
K(ridx,:) = [];
nG(ridx)
nG(ridx) = [];


ridx = find(any(K(:,250) < -0.01,2));    
K(ridx,:) = [];
nG(ridx)
nG(ridx) = [];
    
    
ridx = find(any(K(:,200) < -0.01,2));    
K(ridx,:) = [];
nG(ridx)
nG(ridx) = [];
    
    
%[K Um BV L COEFFS ERR] = PCA_FIT(K',3);
%K = K';
    
figure;plot(mean(K))
figure;
hold all 
for i =1:3
    Um = mean(K(nG==i,:));
    Sm = std(K(nG==i,:))*sum(nG==i)^-.5;
    errorbar(Um,Sm)    
end
legend(U)
    

figure;
CL = {'b' 'g' 'r'};
for i = 1:3
    plot(K(nG==i,:)',CL{i})
    hold on
end
[M2 P2] = ttest2(K(nG==1,:),K(nG==2,:),[],[]);
[M3 P3] = ttest2(K(nG==1,:),K(nG==3,:),[],[]);
M2 = M2* min(K(:));
M3 = M3* min(K(:));
    

    

    
    
    
%}


    
%{

DPATH = 'Y:\nate\amy\data\chf gravitropism test\';
cdir = dir(DPATH);
cdir(1:2) = [];
for i = 1:size(cdir,1)
    PATHIN{i} = [DPATH cdir(i).name '\'];
end






PATHIN = unique(pathstr);
[A MID] = getMidlines(PATHIN,0,0);
A(7) = [];
PATHIN(7) = [];
AN = cell2mat(A');
ridx = find(any(abs(diff(AN*180/pi,1,2)) > 20,2));   
PATHIN(ridx) = [];
AN(ridx,:) = [];
    
for i = 1:size(PATHIN,2)
    fidx = findstr(PATHIN{i},'_');    
    genoType{i} = PATHIN{i}(fidx(end)+1:end-1);
end
    
U = unique(genoType);
for i = 1:size(U,2)
    for j = 1:size(genoType,2)
        if strcmp(genoType{j},U(i))
            nG(j) = i;
        end
    end    
end
    
for i = 1:size(AN,1)
        DEL(i,:) = AN(i,:) - AN(i,1);
end

for i = 1:size(AN,1)
    DAN(i,:) = cwt(AN(i,:),1,'gaus1');
end

figure
TEMP = AN*180/pi;
CLIP = 1;
CL = {'r' 'b' 'g'};
for i = 1:size(U,2)    
    temp = TEMP(find(nG==i),:);
    plot(temp',CL{i})
   
    if size(temp,1) > 1
        u = mean(temp);
        s = std(TEMP(find(nG==i),:),1,1)*size(find(nG==1),2)^-.5;
    else 
        u = temp;
        s = zeros(size(temp));
    end
    
    %errorbar(-u(CLIP:end-CLIP-1),s(CLIP:end-CLIP-1),CL{i})    
    hold on
end
    
legend(U)
    
for i = 1:size(U,2)
    plot(-TEMP(find(nG==i),CLIP:end-CLIP-1)',CL{i});
end


    
    
%}

%{
    [A MID] = getMidlines(PATHIN,1,1);
%}
    
%{
    AN = cell2mat(A');
    ridx = find(any(abs(diff(AN*180/pi,1,2)) > 20,2));   
    PATHIN(ridx) = [];
    AN(ridx,:) = [];
    ridx    
    AN = diff(AN,1,2);
    
    
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
    
    uWT = mean(-AN([3 7 10],:));
    sWT = std(-AN([3 7 10],:))*3^-.5;
    uMT = mean(-AN([1:2 4:6 8:9],:));
    sMT = std(-AN([1:2 4:6 8:9],:))*7^-.5;    
    
    
    SWT = (-AN([3 7 10],:));    
    SMT = (-AN([1:2 4:6 8:9],:));
    
    
    %{
    uWT = mean(-DEL([3 7 10],:));    
    sWT = std(-DEL([3 7 10],:))*3^-.5;
    uMT = mean(-DEL([1:2 4:6 8:9],:));
    sMT = std(-DEL([1:2 4:6 8:9],:))*7^-.5;
    %}
    
    %{
    for i = 1:size(AN,1)
        AN(i,:) = cwt(AN(i,:),10,'gaus1');
    end
    %}
    
    errorbar(uWT,sWT,'b')
    hold on
    errorbar(uMT,sMT,'r')
    
    
    
%}
    
    
%{

%}


