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
[SIM U BV L COEFFS ERR] = PCA_FIT(Y(:,11:end),2);
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
G = Y(sidx == 2,:);
B = [Y(sidx ~= 2,:);bY];


%% good basis vectors
gBV = BV;
gU = U;
%% bayes classifier
[SIM COEFFS ERR] = PCA_REPROJ([B(:,11:end);G(:,11:end)],gBV,gU);
A = [zeros(size(B,1),1);ones(size(G,1),1)];
cf = NaiveBayes.fit([COEFFS ERR],A);
cpre = predict(cf,[COEFFS ERR]);





%% use classifier
PATH = 'Y:\nate\amy\scans\0h\';
cdir = dir(PATH);
cdir(1:2) = [];
for i = 1:1%size(cdir,1)
    I = imread([PATH cdir(i).name]);
    I = I(1:4:end,1:4:end,:);
    I = rgb2gray(I);    
    [X] = my_corner(double(I),1,1,1,25,200);
    [SIM COEFFS ERR] = PCA_REPROJ(X(:,11:end),gBV,gU);
    cpre = predict(cf,[COEFFS ERR]);
    [post,cpre] = posterior(cf,[COEFFS ERR]);
    [JUNK sidx] = sort(post(:,2),'descend');
    imshow(I,[])
    hold on
    scatter(X(sidx(1:40),2),X(sidx(1:40),1))
    
    
end

%%







imshow(I)
hold on
scatter(X(sidx==SEL,2),X(sidx==SEL,1))
quiver(X(sidx==SEL,2),X(sidx==SEL,1),X(sidx==SEL,4),X(sidx==SEL,5),10)





