[FileList] = Wdig('C:\FTP server\won\',{},{'zip'},0);
for i = 1:size(FileList,1)
    fprintf(['Make Dir \n']);
    mkdir('C:\FTP server\won\workingDIR\');
    fprintf(['Unzip \n']);
    unzip(FileList{i},'C:\FTP server\won\workingDIR\');    
    fprintf(['Get file name \n']);
%    [pathstr, name, ext, versn] = fileparts(FileList{i});
    [pathstr, name, ext] = fileparts(FileList{i});
    fprintf(['Get files \n']);
    [FileSequences] = findFileSequences('C:\FTP server\won\workingDIR\');
    fprintf(['Extract Data \n']);
    try
        [A MID] = getMidlines(FileSequences,1,0);        
    catch ME
        A{1} = 0;
        MID = 0';
    end    
    fprintf(['Write Data']);
    xlswrite(['C:\FTP server\won\' name '.xls'],-A{1}'*180/pi)
    save(['C:\FTP server\won\' name '.mat'],'MID')
    fprintf(['Remove dir \n']);
    rmdir('C:\FTP server\won\workingDIR\','s');
    sourcepath = ['Y:\nate\FTP store\won\' datestr(date) '\'];
    mkdir(sourcepath);
    destinationname = [sourcepath name '.zip'];
    fprintf(['Move File \n']);
    movefile(FileList{i},destinationname,'f');    
end
