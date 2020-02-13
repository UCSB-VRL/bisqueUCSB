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
PATH{1} = 'N:\Measure Code\takeshi pipeline\results3\tips\';
PATH{2} = 'N:\Measure Code\takeshi pipeline\results second run\tips\';

for p = 1:size(PATH,2)
    cdir{p} = dir(PATH{p});
    cdir{p}(1:2) = [];
    DM = [];
    NM = [];
    SZ(p) = size(cdir{p},1);
end
%% build the paths
cnt = 1;
for p = 1:size(PATH,2)
    for i = 1:size(cdir{p},1)
        fidx = strfind(cdir{p}(i).name,'_');
        F{cnt} = cdir{p}(i).name(1:fidx(1)-1-2);
        W{cnt} = [PATH{p} cdir{p}(i).name];
        cnt = cnt + 1;
    end
end
[UF fidx] = unique(F);

%% dig through results
cnt = 1;
for i = 1:size(UF,2)
    fidx = find(strcmp(UF{i},F));
    sidx{i} = fidx;    
    for j = 1:size(fidx,2)
        i
        size(UF,2)
        W{fidx(j)}
        VEC = dlmread(W{fidx(j)})';    
        if size(VEC,2) > 183610
            VEC(:,end-(3010-1):end) = [];
        elseif size(VEC,2) < 183610
            VEC = zeros(2,183610);
        end
        
        
        
        D = VEC(:,3:3010:end);
        D = D *180/pi;
        % outliner rejection based on the tip being lost
        OUT = reshape(VEC,[size(VEC,2)/61 61*size(VEC,1)]);
        OUT(1:2,:) = 0;
        R = [];
        for k = 1:size(OUT,2)
            R(k) = all(zeros(size(OUT,1),1) == OUT(:,k));
        end
        R = reshape(R,[61 size(VEC,1)]);
        R = any(R,1);
        ridx = find(R);
        kidx = find(~R);    
        % outliner rejection based on the tip being lost

        
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
        
        
        dA = abs(diff(D,1,2));
        ridx = any(dA > 10,2);
        rdix = find(ridx);    
        %{
        plot(D(ridx,:),'g')
        drawnow
        pause(.2);
        close(h)
        %}

        D(ridx,:) = [];
         
         
        U = mean(D,1);
        if size(D,1) == 1
            S = zeros(size(U));
        else
            S = std(D,1).*size(VEC,1)^-.5;
        end
        DD{fidx(j)} = D;
        mU{fidx(j)} = U;
        mS{fidx(j)} = S;  
        cnt = cnt + 1;
    end    
end

%%
figure;
for i = 1:size(UF,2)
    L = [];
    for j = 1:size(sidx{i},2)
        errorbar(mU{sidx{i}(j)},mS{sidx{i}(j)})
        hold all
        L{j} = W{sidx{i}(j)};
    end        
    legend(L);
    hold off
    pause(.5)
end
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
