[FileList] = Wdig('C:\FTP server\won\',{},{'mat'},0);
for i = 1:size(FileList,1)
    load(FileList{i})
    mid = [];
%    [pathstr, name, ext, versn] = fileparts(FileList{i});
    [pathstr, name, ext] = fileparts(FileList{i});
    for j = 1:size(MID{1},2)
        %
        LOS = MID{1}{1}';
        CHOP = 250;
        if j == 1
            [JUNK thres] = min(abs(abs(LOS(1,:) - LOS(1,end)) - CHOP));
            thres = LOS(1,thres);                
        end
        ridx = find(LOS(1,:) < thres);
        LOS(:,ridx) = [];
        %
        mid = cat(3,mid,LOS);
        
        L(j) = size(MID{1}{j},1);        
    end    
    save(['C:\FTP server\won\' name '_mid.mat'],'mid')
    xlswrite(['C:\FTP server\won\' name '_length.xls'],L)
    xlswrite(['C:\FTP server\won\' name '_gr.xls'],gradient(L))
end
