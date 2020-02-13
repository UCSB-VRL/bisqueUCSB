function [IS,XP] = view_tip_finder(PATH,corner_nb,corner_U,corner_BV,seed_nb,seed_U,seed_BV,RAD,PHI)
figure;
cdir = dir(PATH);
cdir(1:2) = [];
cdir(end-4:end) = [];
SAM = [];
[R T] = ndgrid(linspace(0,RAD,RAD),linspace(-pi,pi,PHI));
Xo = R.*cos(T);
Yo = R.*sin(T);
STK = [];
SV = [];
SeM = [];
IS = [];
for i = 1:size(cdir,1)
    PATH1 = [PATH cdir(i).name '\'];
    cdir1 = dir(PATH1);
    cdir1(1:2) = [];
    R = [];
    I = double(imread([PATH1 cdir1(1).name]));
    IS = cat(3,IS,I);
    X = use_tip_finder(I,RAD,PHI,corner_nb,corner_U,corner_BV,seed_nb,seed_U,seed_BV,0,1);
end

%{
    [seed_nb seed_U seed_BV] = train_num_Seeds('Y:\takeshi\Maize\IBM lines\Gravitropism\',1);
    save('N:\Measure Code\takeshi pipeline\seed_counter.mat','seed_nb','seed_U','seed_BV')
    load('N:\Measure Code\takeshi pipeline\seed_counter.mat','seed_nb','seed_U','seed_BV')

    [corner_nb corner_U corner_BV] = train_corner(seed_nb,seed_U,seed_BV,'Y:\takeshi\Maize\IBM lines\Gravitropism\',30,100,2);
    save('N:\Measure Code\takeshi pipeline\tip_counter2.mat','corner_nb','corner_U','corner_BV')
    [D U BV] = QCS(VEC,1,[],corner_U,corner_BV);
    nb = corner_nb;
    for i = 1:100
        cpre = predict(nb,D);
        sum(cpre)
        nb = NaiveBayes.fit(D,cpre);
    end

    


    [STACK X] = view_tip_finder('Y:\takeshi\Maize\IBM lines\Gravitropism\',corner_nb,corner_U,corner_BV,seed_nb,seed_U,seed_BV,30,100);
%}


