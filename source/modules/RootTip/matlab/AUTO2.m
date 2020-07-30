
%{
[FileList] = Wdig('C:\FTP server\won\',{},{'zip'},0);
matlabpool 4

parfor i = 1:size(FileList,1)
    fprintf(['Make Dir \n']);
%    [pathstr, name, ext, versn] = fileparts(FileList{i});
    [pathstr, name, ext] = fileparts(FileList{i});
    mkdir(['C:\FTP server\won\workingDIR_' name '\']);
    fprintf(['Unzip \n']);
    unzip(FileList{i},['C:\FTP server\won\workingDIR_' name '\']);    
    fprintf(['Get file name \n']);    
    fprintf(['Get files \n']);
    [FileSequences] = findFileSequences(['C:\FTP server\won\workingDIR_' name '\']);
    fprintf(['Extract Data \n']);
    try
        [A MID] = getMidlines(FileSequences,1,0);        
        % get the midlines
        mid = [];
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
            mids = interp1((0:size(LOS,2)-1)',LOS',linspace(0,size(LOS,2)-1,1000)')';    
            mid = [mid ;mids];
            L(j) = size(MID{1}{j},1);        
        end
        % get the midlines
    catch ME
        A{1} = 0;
        MID = 0';
        L = 1;
        mid = 1;
    end
    
    fprintf(['Write Data']);
    csvwrite(['C:\FTP server\won\' name '_mid.csv'],mid)
    xlswrite(['C:\FTP server\won\' name '_length.xls'],L)
    xlswrite(['C:\FTP server\won\' name '_gr.xls'],gradient(L))
    xlswrite(['C:\FTP server\won\' name '_angle.xls'],-A{1}'*180/pi)
    %save(['C:\FTP server\won\' name '.mat'],'MID')
    fprintf(['Remove dir \n']);
    rmdir(['C:\FTP server\won\workingDIR_' name '\'],'s');
    sourcepath = ['Y:\nate\FTP store\won\' datestr(date) '\'];
    mkdir(sourcepath);
    destinationname = [sourcepath name '.zip'];
    fprintf(['Move File \n']);
    movefile(FileList{i},destinationname,'f');    
end
%}
