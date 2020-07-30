TC = 2;
ROWS = 3;
PLATES = 3;
P{1} = 'C:\Users\Nate\Desktop\data in\for amy gravi\gravity response\0h\';
P{2} = 'C:\Users\Nate\Desktop\data in\for amy gravi\gravity response\2h\';
P{3} = 'C:\Users\Nate\Desktop\data in\for amy gravi\gravity response\4h\';
MX = [];
for i = 1:1%size(P,2)
    FileList = spec_getFileList(P{i},'.jpg');    
    for j = 1:1%size(FileList,2)
        I = imread(FileList{j});
        I = imcrop(I);
        I = rgb2gray(I);
        [X] = my_corner(double(I),1,1,1,20,100);
    end
end

%%
FileName = 'Y:\nate\amy\scans\0h\auf1-2-1.tif';
I = imread(FileName);
I = I(1:4:end,1:4:end,:);
I = rgb2gray(I);
[X] = my_corner(double(I),1,1,1,25,200);


%% first tier
[SIM U BV L COEFFS ERR] = PCA_FIT(X(:,11:end),2);
NG = 5;
sidx = kmeans(COEFFS,NG);
imshow(I)
hold on
for i = 1:NG
    scatter(X(sidx==i,2),X(sidx==i,1))
    hold all   
    LEG{i} = num2str(i);
end
legend(LEG)
%% select group
SEL = 5;
Y = X(sidx==SEL,:);
bY = X(sidx~=SEL,:);
%% second tier
[SIM U BV L COEFFS ERR] = PCA_FIT(Y(:,11:end),3);
NG = 2;
sidx = kmeans(COEFFS,NG);
imshow(I)
hold on
for i = 1:NG
    scatter(Y(sidx==i,2),Y(sidx==i,1))
    hold all   
    LEG{i} = num2str(i);
end
legend(LEG)

%% select groups from 2nd tier
G = Y(sidx == 1,:);
B = [Y(sidx ~= 1,:);bY];


%% good basis vectors
gBV = BV;
gU = U;
%% bayes classifier
[SIM COEFFS ERR] = PCA_REPROJ([B(:,11:end);G(:,11:end)],gBV,gU);
A = [zeros(size(B,1),1);ones(size(G,1),1)];
cf = NaiveBayes.fit([COEFFS ERR],A);
cpre = predict(cf,[COEFFS ERR]);





%% use classifier
PATH = 'Y:\nate\amy\scans\2h\';
cdir = dir(PATH);
cdir(1:2) = [];
matlabpool 4
parfor i = 1:size(cdir,1)
    i
    I = imread([PATH cdir(i).name]);
    I = I(1:4:end,1:4:end,:);
    I = rgb2gray(I);    
    [X] = my_corner(double(I),0,1,1,15,200);
    XX{i} = X;
    ORG{i} = I;
    
    
    %{
    [SIM COEFFS ERR] = PCA_REPROJ(X(:,11:end),gBV,gU);
    cpre = predict(cf,[COEFFS ERR]);
    [post,cpre] = posterior(cf,[COEFFS ERR]);
    [JUNK sidx] = sort(post(:,2),'descend');
    imshow(I,[])
    hold on
    scatter(X(sidx(1:30),2),X(sidx(1:30),1))
    %}
end
matlabpool close

%% stack the data
MV = [];
NM = [];
for i = 1:size(cdir,1)
    Name{i} = cdir(i).name;
    MV = [MV;XX{i}];
    NM = [NM;i*ones(size(XX{i},1),1)];        
end
%% first tier
[SIM U BV L COEFFS ERR] = PCA_FIT(MV(:,11:end),2);
NG = 6;
sidx = kmeans(COEFFS,NG);
%% display the first tier
for j = 1:size(cdir,1)
    figure;
    imshow(ORG{j})
    subidx = sidx(NM==j);
    hold on   
    for i = 1:NG
        scatter(XX{j}(subidx==i,2),XX{j}(subidx==i,1))
        hold all   
        LEG{i} = num2str(i);
    end
    legend(LEG)
end
%% select group from first tier
SEL = 1;
for j = 1:size(cdir,1)    
    subidx = sidx(NM==j);
    XXX{j} = XX{j}(subidx==SEL,:);
    NM2{j} = NM(subidx==SEL);    
end
%% stack second tier
MV2 = [];
NM2 = [];
for i = 1:size(cdir,1)    
    MV2 = [MV2;XXX{i}];
    NM2 = [NM2;i*ones(size(XXX{i},1),1)];        
end

%% sub select second tier
[SIM U BV L COEFFS ERR] = PCA_FIT(MV2(:,11:end),2);
NG = 2;
sidx = kmeans(COEFFS,NG);
%% display the second tier
for j = 1:size(cdir,1)
    figure;
    imshow(ORG{j})
    subidx = sidx(NM2==j);
    hold on   
    for i = 1:NG
        scatter(XXX{j}(subidx==i,2),XXX{j}(subidx==i,1))
        quiver(XXX{j}(subidx==i,2),XXX{j}(subidx==i,1),XXX{j}(subidx==i,4),XXX{j}(subidx==i,5))
        hold all   
        LEG{i} = num2str(i);
    end
    legend(LEG)
end
%%
ANG = MV2(sidx==2,3)*180/pi;
NM3 = NM2(sidx==2);
G1 = ANG(NM3==1 | NM3==2);
G2 = ANG(NM3==3 | NM3==4);
G3 = ANG(NM3==5 | NM3==6);
s1 = std(G1)*sum(NM3==1 | NM3==2)^-.5;
s2 = std(G2)*sum(NM3==3 | NM3==4)^-.5;
s3 = std(G3)*sum(NM3==5 | NM3==6)^-.5;
errorbar(1,mean(G1),s1)
hold all
errorbar(2,mean(G2),s2)
errorbar(3,mean(G3),s3)









