originObj=actxserver('Origin.Application');
invoke(originObj, 'Execute', 'doc -mc 1;');
P = invoke(originObj,'CreatePage',2,'Test');
invoke(originObj,'PutWorksheet','Test',D',0,0);
G = invoke(originObj,'GraphPages');
L = invoke(G,'Add');
invoke(originObj, 'Execute', 'page.active = 1; layer -i Test_a Test_b')
invoke(originObj, 'Execute', 'layer.Y.from = -10; layer.Y.to = 80');


%%
proj = invoke(originObj,'NewProject');
fld = invoke(originObj,'RootFolder');
flds = invoke(fld,'Folders');
flder = invoke(flds,'Add','Testing');
u = invoke(flds,'FolderFromPath','Testing');



flder = invoke(flds,'Count');
flder = invoke(flds,'Item','Testing');
P = invoke(originObj,'CreatePage',2,'Test');    
P = invoke(originObj,'CreatePage',3,'Test');    
invoke(originObj,'PutWorksheet','Test',D',0,0);
invoke(originObj,'GetWorkSheet','Test')
G = invoke(originObj,'GraphPages');
L = invoke(G,'Add');
invoke(G,'Add',D');
invoke(originObj,'ActiveFolder','Testing');
invoke(flder,'Activate','Testing');


%invoke(originObj, 'PutWorksheet', 'Data1', mdata);
%%
figure;
PATH = 'N:\Measure Code\takeshi pipeline\results3\tips\';
PATH = 'N:\Measure Code\takeshi pipeline\results second run\tips\';
cdir = dir(PATH);
cdir(1:2) = [];
DM = [];
NM = [];
for i = 1:size(cdir,1)    
    VEC = dlmread(([PATH cdir(i).name]))';    
    if size(VEC,2) > 183610
        VEC(:,end-(3010-1):end) = [];
    end
    
    
    D = VEC(:,3:3010:end);
    D = D *180/pi;
    % outliner rejection based on the tip being lost
    OUT = reshape(VEC,[size(VEC,2)/61 61*size(VEC,1)]);
    OUT(1:2,:) = 0;
    R = [];
    for j = 1:size(OUT,2)
        R(j) = all(zeros(size(OUT,1),1) == OUT(:,j));
    end
    R = reshape(R,[61 size(VEC,1)]);
    R = any(R,1);
    ridx = find(R);
    kidx = find(~R);    
    % outliner rejection based on the tip being lost
    
    QWER{i} = D;
    %{
    h = figure;
    hold off
    plot(D(ridx,:)','r');
    hold on
    plot(D(kidx,:)','b');    
    hold off
    title(num2str(i))
    %}
    
    
    % outliner rejection based on the tip being lost    
    D = D(kidx,:);
    % outliner rejection based on the tip being lost
    
    dA = diff(D,1,2);
    ridx = any(dA > 20,2);
    rdix = find(ridx);    
    %{
    plot(D(ridx,:),'g')
    drawnow
    pause(.2);
    close(h)
    %}
    
     D(ridx,:) = [];
     if size(D,1) > 0







        SNIP = D(:,10:20);
        SLOPE = [];
        for j = 1:size(D,1)
            P = polyfit(1:size(SNIP,2),SNIP(j,:),1);
            SLOPE(j) = P(1);
        end
        uS(i) = mean(SLOPE);
        sS(i) = std(SLOPE);
        ENDSNIP = D(:,end-3:end);
        uE(i) = mean(ENDSNIP(:));
        sE(i) = std(ENDSNIP(:));
        U = mean(D,1);
        if size(D,1) == 1
            S = zeros(size(U));
        else
            S = std(D,1).*size(VEC,1)^-.5;
        end
        errorbar(U,S)
        hold all
        DM = [DM ;D];
        NM = [NM ;i*ones(size(D,1),1)];
        %P = invoke(originObj,'CreatePage',2,'Test');    
        %invoke(originObj,'PutWorksheet','Test',D',0,0);
        i
        drawnow
        mU{i} = U;
        mS{i} = S;
     else
         mU{i} = zeros(1,61);
         mS{i} = zeros(1,61);    
        
     end
    
    LEG{i} = [cdir(i).name(1:end-4) '-' num2str(size(VEC,1)) '-' num2str(size(D,1))];    
end

legend(LEG)

figure;hist(uS,30)
figure;hist(uE,30)
figure;scatter(uS,uE)

%%
for i = 1:size(LEG,2)
    T(i) = str2num(LEG{i}(end-2));
    O(i) = str2num(LEG{i}(end));
end

%%
figure
TR = 5;
r = 1 + (size(cdir,1)-1).*rand(TR,1);
r = round(r);
r = 1:TR
UQ = [];
SQ = [];
for i = 1:TR
    errorbar(mU{r(i)},mS{r(i)})
    UQ = [UQ mU{r(i)}' mS{r(i)}'];       
    hold all       
end
LEG{r}
%%
figure;
[SIM U BV L COEFFS ERR] = PCA_FIT(DM,61);
plot(cumsum(diag(L)/sum(diag(L))))
[SIM U BV L COEFFS ERR] = PCA_FIT(DM,2);
figure;
for i = 1:NM(end)
    fidx = find(NM == i);
    SP = COEFFS(fidx,1:2);
    U = mean(SP);
    scatter(U(1),U(2));
    hold all
end
legend(LEG)
