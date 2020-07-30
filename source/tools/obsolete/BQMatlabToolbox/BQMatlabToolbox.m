function varargout=BQMatlabToolbox()
% BQMatlabToolbox - matlab toolbox for Bisquik
% Boguslaw Obara, http://boguslawobara.net/
%
% Version:
%   0.1 - 11/01/2008 First implementation
%   0.11- 07/07/2008 New Java Jar

%% Int
clc; close all;
%% GUI
BQMT.scxy=get(0,'ScreenSize');
BQMT.xw=500;
BQMT.yw=550;
BQMT.xs=(BQMT.scxy(1,3)-BQMT.xw)/2;
BQMT.ys=(BQMT.scxy(1,4)-BQMT.yw)/2;
BQMT.units='pixels';
BQMT.figure=figure('Name','BQMatlabToolbox','MenuBar','none','Toolbar','none',...
    'Units',BQMT.units,'NumberTitle','off','Position',[BQMT.xs BQMT.ys BQMT.xw BQMT.yw],...
    'Resize','off','Color', get(0, 'defaultuicontrolbackgroundcolor'));
% BQMT.tinfo1=uicontrol('Parent',BQMT.figure,'Style','text','Units',BQMT.units,...
%      'Position',[5 25 100 10],'String','Center for BioImage Informatics','FontSize',7);
% BQMT.tinfo2=uicontrol('Parent',BQMT.figure,'Style','text','Units',BQMT.units,...
%      'Position',[5 15 100 10],'String','University of California','FontSize',7);
% BQMT.tinfo3=uicontrol('Parent',BQMT.figure,'Style','text','Units',BQMT.units,...
%      'Position',[5 5 100 10],'String','Santa Barbara, USA','FontSize',7);

BQMT.panelIL=uipanel('Parent',BQMT.figure,'Units',BQMT.units,...
    'Position',[5 95 200 350],'Title','Image List');
BQMT.listIL=uicontrol('Parent',BQMT.panelIL,'Style','listbox','Units',BQMT.units,...
    'Position',[5 5 185 325],'String','','BackgroundColor','white',...
        'Max',1000,'Min',1,'Callback',@BQMTSelectImage);

BQMT.panelIB=uipanel('Parent',BQMT.figure,'Units',BQMT.units,...
    'Position',[205 95 290 350],'Title','Image Browser');
BQMT.axesIB=axes('Parent',BQMT.panelIB,'Units',BQMT.units,...
    'Position',[90 220 100 100],'XTick',[],'YTick',[]);
BQMT.listTag=uicontrol('Parent',BQMT.panelIB,'Style','listbox','Units',BQMT.units,...
    'Position',[5 5 280 175],'String','','BackgroundColor','white',...
    'Max',1000,'Min',1);
BQMT.checkboxShowTag=uicontrol('Parent',BQMT.panelIB,'Style','checkbox','Units',BQMT.units,...
    'Position',[5 185 100 15],'String','Show Tags','Value',0);
    
%'Position',[5 45 240 20],'String','http://bodzio.ece.ucsb.edu:8080',...    
BQMT.panelSS=uipanel('Parent',BQMT.figure,'Units',BQMT.units,...
    'Position',[5 455 250 85],'Title','Server Settings');
BQMT.editServer=uicontrol('Parent',BQMT.panelSS,'Style','edit','Units',BQMT.units,...
    'Position',[5 45 240 20],'String','http://bodzio.ece.ucsb.edu:8080',...
    'BackgroundColor','white', 'HorizontalAlignment','left');
BQMT.textPassword=uicontrol('Parent',BQMT.panelSS,'Style','text','Units',BQMT.units,...
      'Position',[5 5 100 15],'String','Password:', 'HorizontalAlignment','right');
BQMT.editPassword=uicontrol('Parent',BQMT.panelSS,'Style','edit','Units',BQMT.units,...
    'Position',[105 5 140 20],'String','admin',...
    'BackgroundColor','white', 'HorizontalAlignment','right');
BQMT.textUser=uicontrol('Parent',BQMT.panelSS,'Style','text','Units',BQMT.units,...
      'Position',[5 25 100 15],'String','User:', 'HorizontalAlignment','right');
BQMT.editUser=uicontrol('Parent',BQMT.panelSS,'Style','edit','Units',BQMT.units,...
    'Position',[105 25 140 20],'String','admin',...
    'BackgroundColor','white', 'HorizontalAlignment','right');

BQMT.panelS=uipanel('Parent',BQMT.figure,'Units',BQMT.units,...
    'Position',[255 455 240 85],'Title','Search');
BQMT.editSearch=uicontrol('Parent',BQMT.panelS,'Style','edit','Units',BQMT.units,...
    'Position',[10 40 220 20],'String','',...
    'BackgroundColor','white', 'HorizontalAlignment','right');
BQMT.buttonSearch=uicontrol('Parent',BQMT.panelS,'Style','pushbutton','Units',BQMT.units,...
    'Position',[10 5 220 30],'String','Search','Callback',@BQMTSearch);



BQMT.panelDU=uipanel('Parent',BQMT.figure,'Units',BQMT.units,...
    'Position',[5 5 490 85],'Title','Operations');
BQMT.buttonSearch=uicontrol('Parent',BQMT.panelDU,'Style','pushbutton','Units',BQMT.units,...
    'Position',[5 5 120 30],'String','Download','Callback',@BQMTDownloadImage);
BQMT.textProcess=uicontrol('Parent',BQMT.panelDU,'Style','text','Units',BQMT.units,...
    'Position',[350 5 130 15],'String','...');


%% Functions
BQMT.Image = [];
if nargout>0
uiwait(BQMT.figure);
end
%% Outputs
mOutputArgs     =   {}; 
mOutputArgs{1} = BQMT.Image;
if nargout>0
    [varargout{1:nargout}] = mOutputArgs{:};
end
%%
%% Include
javaaddpath('bisque.jar');
import bisque.*

%% Search
function BQMTSearch(obj,event)
    import bisque.*
	BQ = BQMatlab;
    BQ.initServers(get(BQMT.editServer,'String'),get(BQMT.editServer,'String'));
    BQ.login(get(BQMT.editUser,'String'), get(BQMT.editPassword,'String'));
	BQMT.SearchListJ = BQ.search(get(BQMT.editSearch,'String'));
    BQMT.SearchList = {};
    set(BQMT.listIL,'String',BQMT.SearchList);
    for i=1:size(BQMT.SearchListJ)
        url = char(BQMT.SearchListJ.get(i-1));
        BQMT.SearchList{i,1} = regexprep(url, get(BQMT.editServer,'String'), '');
    end
    set(BQMT.listIL,'String',BQMT.SearchList);
end
%% Select Image
function BQMTSelectImage(obj,event)
    import bisque.*
    BQMT.SelectedIDname = get(BQMT.listIL,'String');
    BQMT.SelectedIDix = get(BQMT.listIL,'Value');
    if isempty(BQMT.SelectedIDname)
        errordlg('You must select one file',...
        'Incorrect Selection','modal')
        return;
    else
        %ImageID = BQMT.SelectedIDname{BQMT.SelectedIDix(1)};
        %ImageID = char(BQMT.SearchListJ.get(BQMT.SelectedIDix(1)-1))
        %BQAuthorization.setAuthorization(get(BQMT.editUser,'String'), get(BQMT.editPassword,'String'));
        %T = uint8(BQThumbnail.getImage(ImageID, 100,100));   
        BQMTShowThumbnails()
    end
end
%% Show Images
function BQMTShowThumbnails()
    import bisque.*
	BQ = BQMatlab;
    BQ.initServers(get(BQMT.editServer,'String'),get(BQMT.editServer,'String'));
    BQ.login(get(BQMT.editUser,'String'), get(BQMT.editPassword,'String'));    
    set(BQMT.textProcess,'String','Uploading'); pause(0.001);
    BQMT.SelectedIDname = get(BQMT.listIL,'String');
    BQMT.SelectedIDix = get(BQMT.listIL,'Value');
    ImageID = char(BQMT.SearchListJ.get(BQMT.SelectedIDix(1)-1));

    T = uint8(BQ.loadThumbnailData(ImageID, 100,100));        
    axes(BQMT.axesIB(1));
    imagesc(T); axis image;    
    set(BQMT.axesIB(1),'XTick',[],'YTick',[]);

    BQMTGetTags(ImageID);
    set(BQMT.textProcess,'String','...');
end
%% Download
function BQMTDownloadImage(obj,event)
    import bisque.*
	BQ = BQMatlab;
    BQ.initServers(get(BQMT.editServer,'String'),get(BQMT.editServer,'String'));
    BQ.login(get(BQMT.editUser,'String'), get(BQMT.editPassword,'String'));       
    BQMT.SelectedIDname = get(BQMT.listIL,'String');
    BQMT.SelectedIDix = get(BQMT.listIL,'Value');
    if isempty(BQMT.SelectedIDname)
        errordlg('You must select one file',...
        'Incorrect Selection','modal')
        return;
    else
        %ImageID = BQMT.SelectedIDname{BQMT.SelectedIDix(1)};
        ImageID = char(BQMT.SearchListJ.get(BQMT.SelectedIDix(1)-1));
        %ImageURL = [get(BQMT.editServer,'String') ImageID];
        %ImageSRC = char(BQImage.getImageURL(ImageID));
        %ThumbnailURL = [ImageSRC '?remap=display&slice=,,1,1&resize=100,100&format=raw'];
        image_ = BQ.loadImage(ImageID);
        BQMT.Image = uint8(BQ.loadImageData(image_)); 
        %BQMT.Image = BQImage.getImage(ImageID); 
        %figure, imagesc(IM)
        %save(['tmp.mat'], 'IM');
    end
end
%% Info
function info = BQMTInfo(URL)
    import bisque.*
    arrayImageInfo = BQImage.getImageInfo(URL);
    infoz = char(BQImage.searchImageInfo(arrayImageInfo, 'zsize'));
    infot = char(BQImage.searchImageInfo(arrayImageInfo, 'tsize'));
    infoh = char(BQImage.searchImageInfo(arrayImageInfo, 'height'));
    infow = char(BQImage.searchImageInfo(arrayImageInfo, 'width'));
    infod = char(BQImage.searchImageInfo(arrayImageInfo, 'depth'));
    infoch = char(BQImage.searchImageInfo(arrayImageInfo, 'channels'));
    info = ['w:' infow ', h:' infoh ', z:' infoz ', t:' infot ', d:' infod ', ch:' infoch];
end
%% Info
function BQMTGetTags(URL)
    import bisque.*
	BQ = BQMatlab;
    BQ.initServers(get(BQMT.editServer,'String'),get(BQMT.editServer,'String'));
    BQ.login(get(BQMT.editUser,'String'), get(BQMT.editPassword,'String'));    
    
    if get(BQMT.checkboxShowTag,'Value')==1
        image_ = BQ.loadImage([URL '?view=full']);
        BQMT.TagListJ = image_.tags;
        for i=1:size(BQMT.TagListJ)
            name = char(BQMT.TagListJ.get(i-1).name);
            value = char(BQMT.TagListJ.get(i-1).values.get(0).value);
            BQMT.TagList{i,1} = [name ' : ' value];
        end
        set(BQMT.listTag,'String',BQMT.TagList);
    else
        BQMT.TagList = {};
        set(BQMT.listTag,'String',BQMT.TagList);
    end
end
%% End
end
