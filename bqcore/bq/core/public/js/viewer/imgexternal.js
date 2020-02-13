function ImgExternal (viewer,name){
    this.base = ViewerPlugin;
    this.base (viewer, name);
    var me = this;
	this.imgCurrentView = new ImgCurrentView(viewer)

    this.viewer.addMenu([{
        itemId: 'menu_viewer_external',
        xtype:'button',
        text: 'Export',
        iconCls: 'external',
        needsAuth: false,
        scope: this,
        tooltip: 'Export current image to external applications',
        menu: {
            cls: 'bq-editor-menu',
            defaults: {
                scope: this,
            },

            items: [{
                xtype  : 'menuitem',
                itemId : 'menu_viewer_export_view',
                text   : 'Export current view',
                scale  : 1,
                border: true, //default
                showGobjects: true,
                handler: function() {
                    this.getCurrentView(0)
                },

                menu   : {
                    //hidden: true,
                    handler: function() {return false;},
                    items   : [
                    //'<b class="menu-title">Choose a Scale</b>',
					{
						//hidden: true,
                        text: '100%',
						itemId : 'menu_viewer_export_view_button_100',
                        handler: function() {
                            this.getCurrentView(0)
                        },
                        scope: this,
                        //checked: false,
                        //hideOnClick : false,
                        group: 'scale',
                        tooltip: 'Download current view scaled at 100%',
                    }, {
						//hidden: true,
                        text: '200%',
						itemId : 'menu_viewer_export_view_button_200',
                        handler: function(){
                            this.getCurrentView(1)
                        },
                        scope: this,
                        //checked: true,
                        //hideOnClick : false,
                        group: 'scale',
                        tooltip: 'Download current view scaled at 200%',
                    }, {
						//hidden: true,
                        text: '400%',
						itemId : 'menu_viewer_export_view_button_400',
                        handler: function(){
                            this.getCurrentView(2)
                        },
                        scope: this,
                        //checked: false,
                        //hideOnClick : false,
                        group: 'scale',
                        tooltip: 'Download current view scaled at 400%',
                }]},


            },{
                xtype  : 'menuitem',
                itemId : 'menu_viewer_external_bioView',
                text   : 'View in bioView',
                handler: this.launchBioView,
            }, {
                xtype  : 'menuitem',
                itemId : 'menu_viewer_external_bioView3D',
                text   : 'View in bioView3D',
                handler: this.launchBioView3D,
            }, /*{
                xtype  : 'menuitem',
                itemId : 'menu_viewer_export_gobs_gdocs',
                text   : 'Export GObjects to Google Docs',
                handler: this.exportGObjectsToGoogle,
            },{
                xtype  : 'menuitem',
                itemId : 'menu_viewer_export_tags_gdocs',
                text   : 'Export Tags to Google Docs',
                handler: this.exportTagsToGoogle,
            }*/]
        },
    }]);

    this.menu_operations = this.viewer.addMenu([{
        itemId: 'menu_viewer_operations',
        xtype:'button',
        text: 'Operations',
        iconCls: 'converter',
        needsAuth: false,
        scope: this,
        //tooltip: 'Export current image to external applications',
        menu: {
            cls: 'bq-editor-menu',
            defaults: {
                scope: this,
            },
            items: [{
                itemId: 'menu_viewer_converter',
                text: 'Convert',
                iconCls: 'converter',
                tooltip: 'Convert and download the current image',
                scope: this,
                handler: this.convert,
            }, {
                xtype  : 'menuitem',
                itemId : 'menu_viewer_calibrate_image',
                text   : 'Calibrate Image',
                //disabled: !BQApp.hasUser(), //too slow to initialize
                disabled: true,
                handler: this.calibrateResolution,
            }
            /*, {
                xtype  : 'menuitem',
                itemId : 'menu_viewer_precache',
                text   : 'Pre-cache current view',
                disabled: true,
                handler: this.calibrateResolution,
            }*/]
        },
    }]);

    //enables the calibrate image if user is found
    BQApp.on('gotuser', function() {
        if (!me.viewer.toolbar) return;
        var calibrateResolution = me.viewer.toolbar.queryById('menu_viewer_calibrate_image');
        calibrateResolution.setDisabled(false);
    });
    if (BQApp.hasUser() && this.viewer.toolbar) { //checks for user
        var calibrateResolution = this.viewer.toolbar.queryById('menu_viewer_calibrate_image');
        calibrateResolution.setDisabled(false);
    }
};

ImgExternal.prototype = new ViewerPlugin();

ImgExternal.prototype.create = function (parent) {
    this.parent = parent;
    return parent;
};

ImgExternal.prototype.newImage = function () {
    var v = this.viewer;
    if (v.toolbar) {
        var m = v.toolbar.queryById('menu_viewer_external_bioView3D');
        if (m) m.setDisabled(v.imagedim.z<2);
    }

    // Add download graphical annotations as KML
    var phys = v.imagephys,
        download = BQApp.getToolbar().queryById('button_download'),
        url = v.image.uri,
        url_kml = url.replace('/data_service/', '/export/') + '?format=kml',
        url_geojson = url.replace('/data_service/', '/export/') + '?format=geojson';
    if (v.is_geo_enabeled()) {
        download.menu.add(['-', {
            itemId: 'download_annotations_as_kml',
            text: 'Graphical annotations as KML',
            handler: function() {
                window.open(url_kml);
            },
        }, {
            itemId: 'download_annotations_as_geojson',
            text: 'Graphical annotations as GeoJson',
            handler: function() {
                window.open(url_geojson);
            },
        }]);
    };
};

/*
*   getCurrentView
*
*       Runs currentView plugin in imgExternal
*
*       @param: levelDiff - sets the currentView level
*/
ImgExternal.prototype.getCurrentView = function(levelDiff) {

    var level = this.imgCurrentView.getCurrentLevel();
    this.imgCurrentView.setLevel(level-levelDiff);
    function callback(canvas_view) {
        var pixels = canvas_view.width*canvas_view.height;
        if(pixels<268435456) { // limit of canvas
            var url = canvas_view.toDataURL("image/jpeg");
            window.open(url);
        } else {
            BQ.ui.notification('Screen capture is too large! Select a smaller size or reduce the viewer size.')
        }
    }

    var canvas_view = this.imgCurrentView.returnCurrentView(callback);

};


ImgExternal.prototype.updateImage = function () {

	//set the options for the export at different scales
	if (this.imgCurrentView && this.viewer.toolbar) {
		var level = this.imgCurrentView.getCurrentLevel(); //level can not drop below 0
		var currentView200 = this.viewer.toolbar.queryById('menu_viewer_export_view_button_200');
		var currentView400 = this.viewer.toolbar.queryById('menu_viewer_export_view_button_400');
		if (level && currentView200 && currentView400) {
			if (level<1) currentView200.setDisabled(true);
			else currentView200.setDisabled(false);
			if (level<2) currentView400.setDisabled(true);
			else currentView400.setDisabled(false);
		} else if (currentView200 && currentView400) {
			currentView200.setDisabled(true);
			currentView400.setDisabled(true);
		}
	}

};

ImgExternal.prototype.launchBioView = function () {
    var url = 'bioview://resource/?url='+this.viewer.image.uri;
    if (this.viewer.user) {
        var user = this.viewer.user.credentials.user;
        var pass = this.viewer.user.credentials.pass;
        url += '&user='+user+'&pass='+pass;
    }
    //window.location = url;
    window.open( url );
};

ImgExternal.prototype.launchBioView3D = function () {
    if (this.viewer.imagedim.z * this.viewer.imagedim.t <= 1) {
        BQ.ui.notification ("Image is not a 3D stack (multiplane image)");
        return;
    }
    var url = 'bioview3d://resource/?url='+this.viewer.image.uri;
    if (this.viewer.user) {
        var user = this.viewer.user.credentials.user;
        var pass = this.viewer.user.credentials.pass;
        url += '&user='+user+'&pass='+pass;
    }
    //window.location = url;
    window.open( url );
};

ImgExternal.prototype.exportGObjectsToGoogle = function () {
    window.open( '/export/to_gdocs?url=' + this.viewer.image.uri + "/gobject" );
};

ImgExternal.prototype.exportTagsToGoogle = function () {
    window.open( '/export/to_gdocs?url=' + this.viewer.image.uri + "/tag" );
};


ImgExternal.prototype.convert = function () {
    var image = this.viewer.image;
    var phys = this.viewer.imagephys;
    var title = 'Image converter [W:'+phys.x+', H:'+phys.y+', Z:'+phys.z+', T:'+phys.t+' Ch:'+phys.ch+'/'+phys.pixel_depth+'bits'+'] ' + image.name;
    Ext.create('Ext.window.Window', {
        modal: true,
        width: BQApp?BQApp.getCenterComponent().getWidth()/1.6:document.width/1.6,
        height: BQApp?BQApp.getCenterComponent().getHeight()/1.1:document.height/1.1,
        layout: 'fit',
        border: false,
        maxWidth: 600,
        title: title,
        items: [{
            xtype  : 'bqimageconverter',
            image  : this.viewer.image,
            phys   : this.viewer.imagephys,
            slice  : this.viewer.findPlugin('slicer').getParams(),
            view   : this.viewer.findPlugin('ops').getParams(),
        }],
    }).show();
};

ImgExternal.prototype.calibrateResolution = function () {
    var image = this.viewer.image;
    var imageMetaEditor = Ext.create('BQ.viewer.Calibration',{
        //layout : 'fit',
        height : '85%',
        width : '85%',
        modal : true,
        image_resource: image.uri, //accepts a data_service uri
    })
    imageMetaEditor.show();
};

ImgExternal.prototype.onPreferences = function () {
    var viewer = this.viewer,
        resource_uniq = viewer.image.resource_uniq;
    //if (BQ.Preferences.get('user', 'ResourceBrowser/Images/enable_annotation_status', false) === true) {
    if (!this.annotation_status &&
        BQ.Preferences.get(resource_uniq, 'ResourceBrowser/Images/enable_annotation_status', false) === true) {
        this.annotation_status = viewer.addMenu({
            xtype: 'bqannotationstatus',
            itemId: 'annotation_status',
            needsAuth: true,
            resource : viewer.image,
            listeners: {
                //scope: this,
                changed: function(cnt) {
                    if (viewer.parameters.tagsChanged)
                        viewer.parameters.tagsChanged();
                },
            },
        });
    }
};

