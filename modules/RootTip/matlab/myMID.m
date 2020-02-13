function [mids] = myMID(I,tipPoints)
R = 200;
LS = -R:1:R;
[A B] = ndgrid(LS,LS);
X = [A(:) B(:)];
PD = 21;
for i = 1:size(tipPoints,1)    
    PATCH = ba_interp2(I,X(:,2)+tipPoints(i,2),X(:,1)+tipPoints(i,1));    
    PATCH = reshape(PATCH,[2*R+1 2*R+1]);    
    PATCH = imclose(PATCH,strel('disk',5));
    PATCH = imfilter(PATCH,fspecial('gaussian',11),'replicate');    
    PATCH = padarray(PATCH,[PD PD],'replicate','both');
    level = graythresh(PATCH/255);
    PATCH = ~im2bw(PATCH/255,level);
    PATCH = imclose(PATCH,strel('disk',5));
    PATCH = bwmorph(PATCH,'skeleton',inf);
    PATCH = PATCH(PD+1:end-(PD),PD+1:end-(PD));    
    PATCH = bwmorph(PATCH,'spur',5);    
    E = xor(bwmorph(PATCH,'spur',1),PATCH);
    [re ce] = find(E);
    d = (re - (R+1)).^2 + (ce - (R+1)).^2;
    [JUNK fidx] = min(d);
    re = re(fidx);
    ce = ce(fidx);
    F1 = round(linspace(re,R+1,100))';
    F2 = round(linspace(ce,R+1,100))';
    F = unique([F1 F2],'rows');
    for j = 1:size(F,1)
        PATCH(F(j,1),F(j,2)) = 1;
    end    
    PATCH(R+1,R+1) = 1; 
    PATCH = padarray(PATCH,[PD PD],'replicate','both');
    PATCH = bwmorph(PATCH,'skeleton',inf);
    
    
    flag = 1;
    cnt = 1;
    
    while flag & cnt < 20
        cnt = cnt + 1;
        E = xor(bwmorph(PATCH,'spur',1),PATCH);
        B = im2col(PATCH,[3 3],'sliding');    
        S = sum(B,1) >= 4;
        S = S & B(5,:);    
        B = col2im(S,[3 3],size(PATCH),'sliding');
        B = padarray(B,[1 1],0,'both');
        GLUE = xor(B,PATCH);
        [r c] = find(E);        
        [tf loc] = ismember([r c],[R+1+PD R+1+PD], 'rows');        
        r(find(loc)) = [];
        c(find(loc)) = [];
        if size(loc,1) == 1
            flag = 0;
        end
        if flag                
            IMG = imfill(~GLUE,[r c],8);
            IMG = ~IMG;
        else
            IMG = GLUE;
        end        
        IMG = or(IMG,B);
        PATCH = bwmorph(IMG,'skeleton',inf);        
    end
    PATCH = PATCH(PD+1:end-(PD),PD+1:end-(PD));
    
    mids{i} = [];
    for j = 1:100
        E = and(imfilter(double(PATCH),ones(3),'replicate') == 2,PATCH);
        
        PATCH = xor(E,PATCH);
        [r c] = find(E);
        mids{i} = [mids{i};[r c]];        
    end    
    mids{i}(:,2) = mids{i}(:,2) + tipPoints(i,2) - (R+1);
    mids{i}(:,1) = mids{i}(:,1) + tipPoints(i,1) - (R+1);    
    
    
    
    
    
    
    
    
    
    
    
end



