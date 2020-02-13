close all;
clear all;
clc;

for vidIter = 0:2
    videoName = ['C:\researchCode\dataBase\multiCamera\epfl\campus2\campus7-c' num2str(vidIter) '.avi'];
    inpVideo = mmreader(videoName);
    aviobj = avifile(['campus' num2str(vidIter+1) '.avi']);
    aviobj.Quality = 100;
    for iter = 1:inpVideo.NumberOfFrames
        aviobj = addframe(aviobj, inpVideo.read(iter) );
        [num2str(iter) 'of' num2str(inpVideo.NumberOfFrames) 'completed']
    end
    aviobj = close(aviobj);
    clear aviobj;
end