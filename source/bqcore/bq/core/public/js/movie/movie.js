/*******************************************************************************
  ExtJS wrapper for the html5 video player
  Author: Dima Fedorov <dima@dimin.net>

  Configurations:
      resource   - url string or bqimage (required)
      phys       - image phys BQImagePhys (preferred)
      preferences - BQPpreferences object (preferred)

  Events:
      loaded     - event fired when the viewer is loaded
      working
      done
      error

*******************************************************************************/

Ext.define('BQ.viewer.Movie', {
    alias: 'widget.bq_movie_viewer',
    extend: 'Ext.container.Container',
    border: 0,
    cls: 'bq-viewer-movie',
    layout: 'fit',

    update_delay_ms: 500,  // Update the viewer asynchronously

    initComponent : function() {
        this.items = [{
            xtype: 'component',
            itemId: 'player',
            autoEl: {
                tag: 'video',
                cls: 'player',
            },
            listeners: {
                scope: this,
                stalled: {
                    element: 'el', //bind to the underlying el property on the panel
                    fn: function() { this.onworking('Loading movie...'); },
                },
                /*loadstart: {
                    element: 'el', //bind to the underlying el property on the panel
                    fn: this.onworking, //function() { BQ.ui.message('loadstart'); },
                },*/
                loadeddata: {
                    element: 'el', //bind to the underlying el property on the panel
                    fn: this.ondone, //function() { BQ.ui.message('loadeddata'); },
                },
                error: {
                    element: 'el', //bind to the underlying el property on the panel
                    //fn: this.onerror, //function() { BQ.ui.message('error'); },
                },
            },
        }, {
            xtype: 'component',
            itemId: 'button-menu',
            //floating: true,
            autoEl: {
                tag: 'span',
                cls: 'viewoptions'
            },
            listeners: {
                scope: this,
                click: {
                    element: 'el', //bind to the underlying el property on the panel
                    fn: this.onMenuClick
                }
            }
        }, {
            xtype: 'component',
            itemId: 'button-fullscreen',
            //floating: true,
            autoEl: {
                tag: 'span',
                cls: 'fullscreen'
            },
            listeners: {
                scope: this,
                click: {
                    element: 'el', //bind to the underlying el property on the panel
                    fn: this.onFullScreenClick
                }
            }
        }, {
            xtype: 'component',
            itemId: 'logo',
            hidden: this.parameters && this.parameters.logo ? false : true,
            autoEl: {
                tag: 'a',
                cls: 'logo',
            },
        }];
        //this.on('resize', this.onResize, this);
        this.callParent();
        this.plug_ins = [ new PlayerSlice(this), new PlayerSize(this), new PlayerDisplay(this), new PlayerFormat(this) ];
    },

    afterRender : function() {
        this.callParent();
        if (!this.resource) {
            BQ.ui.error('No image defined...');
            return;
        }

        this.setLoading('Loading...');
        if (typeof this.resource === 'string') {
            BQFactory.request({
                uri: this.resource,
                uri_params: {view: 'short'},
                cb: callback(this, this.onImage),
                //errorcb: callback(this, this.onerror),
            });
        } else if (this.resource instanceof BQImage) {
            this.onImage(this.resource);
        }

        /*this.keyNav = Ext.create('Ext.util.KeyNav', document.body, {
            left:     this.onkeyboard,
            right:    this.onkeyboard,
            up:       this.onkeyboard,
            down:     this.onkeyboard,
            pageUp:   this.onkeyboard,
            pageDown: this.onkeyboard,
            scope : this
        });*/
    },

    onDestroy: function() {
        if (this.menu && this.menu.isVisible())
            this.menu.hide();
    },

    onImage: function(resource) {
        if (!resource) return;
        this.resource = resource;

        var logo = this.queryById('logo');
        if (logo) {
            logo.getEl().dom.href = '/client_service/view?resource='+resource.uri;
        }

        if (!this.phys) {
            var phys = new BQImagePhys (this.resource);
            phys.load (callback (this, this.onPhys) );
        }
        this.onPartFetch();
    },

    onPhys: function(phys) {
        if (!phys) return;
        this.phys = phys;
        this.onPartFetch();
    },

    onPartFetch: function() {
        if (!this.resource || !this.phys) return;
        this.setLoading(false);
        this.dims = new ImageDim (this.phys.x, this.phys.y, this.phys.z, this.phys.t, this.phys.ch);
        if (!this.viewer)
            this.loadPlayer();
    },

    loadPlayer: function() {
        if (this.viewer) return;

        this.player = this.queryById('player');
        this.viewer = this.player.getEl().dom;
        this.viewer.controls = true;
        this.viewer.autoplay = true;
        this.viewer.loop = true;

        this.createViewMenu();

        // init plug-ins
        var plugin = null;
        for (var i=0; (plugin=this.plug_ins[i]); i++)
            plugin.init();

        this.viewer.poster = this.constructPreviewUrl();
        this.doUpdate();
        this.fireEvent( 'loaded', this );
    },

    onResize: function(me, width, height) {
        if (me.viewer) me.viewer.resize();
    },

    onHide: function() {
        if (this.viewer) {
           this.viewer.pause();
        }
        this.callParent();
    },

    constructUrl: function(opts) {
        var command=[],
            plugin=null;
        for (var i=0; (plugin=this.plug_ins[i]); i++)
            plugin.addCommand(command, opts);
        return this.resource.src+'?'+command.join('&');
    },

    constructMovieUrl: function(format) {
        return this.constructUrl({
            format: format,
        });
    },

    constructPreviewUrl: function() {
        return this.constructUrl({
            format: 'jpeg',
            z: 1,
            t: 1,
        });
    },

    export: function (format) {
        window.open( this.constructMovieUrl(format) );
    },

    doUpdate: function () {
        this.update_needed = undefined;
        if (Ext.isChrome || Ext.isGecko || Ext.isOpera)
            this.viewer.src = this.constructMovieUrl('webm');
        else
            this.viewer.src = this.constructMovieUrl('h264');

    },

    needs_update: function () {
        this.requires_update = undefined;
        if (this.update_needed)
            clearTimeout(this.update_needed);
        this.update_needed = setTimeout(callback(this, this.doUpdate), this.update_delay_ms);
    },

    onloaded : function() {
        this.setLoading(false);
    },

    onworking : function(message) {
        message = message || 'loading movie...';
        if (this.hasListeners.working)
            this.fireEvent( 'working', message );
        else
            this.setLoading(message);
    },

    ondone : function() {
        this.setLoading(false);
        this.fireEvent( 'done', this );
    },

    onerror : function(error) {
        error = error.message_short ? error : { message: 'Video Still Loading', message_short: 'Video Still Loading', };
        this.setLoading(false);
        if (this.hasListeners.error)
            this.fireEvent( 'error', error );
        else
            BQ.ui.error(error.message_short);
    },

    //----------------------------------------------------------------------
    // view menu
    //----------------------------------------------------------------------

    createCombo : function (label, items, def, scope, cb, id, min_width) {
        var options = Ext.create('Ext.data.Store', {
            fields: ['value', 'text'],
            data : items
        });
        return this.menu.add({
            xtype: 'combobox',
            itemId: id ? id : undefined,
            width: 380,
            fieldLabel: label,
            store: options,
            queryMode: 'local',
            displayField: 'text',
            valueField: 'value',
            forceSelection: true,
            editable: false,
            value: def,
            listConfig : {
                minWidth: min_width || 70,
            },
            listeners:{
                scope: scope,
                select: cb,
            }
        });
    },

    createViewMenu: function() {
        if (!this.menu) {
            var menubutton = this.queryById('button-menu');
            this.menu = Ext.create('Ext.tip.ToolTip', {
                target: menubutton.getEl(),
                anchor: 'top',
                anchorToTarget: true,
                cls: 'bq-viewer-menu',
                maxWidth: 460,
                anchorOffset: -5,
                autoHide: false,
                shadow: false,
                closable: true,
                layout: {
                    type: 'vbox',
                    //align: 'stretch',
                },
                defaults: {
                    labelSeparator: '',
                    labelWidth: 200,
                },
            });
        }
    },

    onMenuClick: function (e, btn) {
        e.preventDefault();
        e.stopPropagation();
        if (this.menu.isVisible())
            this.menu.hide();
        else
            this.menu.show();
    },

    onFullScreenClick: function (e, btn) {
        e.preventDefault();
        e.stopPropagation();
        this.doFullScreen();
    },

    doFullScreen: function () {
        var maximized = (document.fullscreenElement || document.mozFullScreenElement || document.webkitFullscreenElement || document.msFullscreenElement),
            vd = this.viewer,
            has_fs = vd.requestFullscreen || vd.webkitRequestFullscreen || vd.msRequestFullscreen || vd.mozRequestFullScreen;
        if (!has_fs) return;

        if (!maximized) {
            if (vd.requestFullscreen) {
                vd.requestFullscreen();
            } else if (vd.webkitRequestFullscreen) {
                vd.webkitRequestFullscreen();
            } else if (vd.msRequestFullscreen) {
                vd.msRequestFullscreen();
            } else if (vd.mozRequestFullScreen) {
                vd.mozRequestFullScreen();
            }
        } else {
            if (document.exitFullscreen) {
                document.exitFullscreen();
            } else if (document.webkitExitFullscreen) {
                document.webkitExitFullscreen();
            } else if (document.msExitFullscreen) {
                document.msExitFullscreen();
            } else if (document.mozCancelFullScreen) {
                document.mozCancelFullScreen();
            }
        }
    },

});

//--------------------------------------------------------------------------------------
// BQ.viewer.Movie.Dialog
//--------------------------------------------------------------------------------------

Ext.define('BQ.viewer.Movie.Dialog', {
    extend : 'Ext.window.Window',
    alias: 'widget.bq_movie_dialog',
    border: 0,
    layout: 'fit',
    modal : true,
    border : false,
    width : '85%',
    height : '85%',
    buttonAlign: 'center',
    autoScroll: true,
    title: 'Movie',

    constructor : function(config) {
        config = config || {};
        Ext.apply(this, {
            title: 'Movie for ' + config.resource.name,
            buttons: [{
                text: 'Done',
                scale: 'large',
                scope: this,
                handler: this.close,
            }],
            items: [{
                xtype: 'bq_movie_viewer',
                itemId: 'viewer_movie',
                border: 0,
                resource: config.resource,
            }],
        }, config);

        this.callParent(arguments);
        this.show();
    },

});

//--------------------------------------------------------------------------------------
// Plug-ins - base
//--------------------------------------------------------------------------------------

function PlayerPlugin (player) {
    this.player = player;
};

PlayerPlugin.prototype.init = function () {
};

PlayerPlugin.prototype.addCommand = function (command, pars) {
};

PlayerPlugin.prototype.changed = function () {
  if (!this.update_check || (this.update_check && this.update_check.checked) )
    this.player.needs_update();
};

//--------------------------------------------------------------------------------------
// Plug-ins - slice
//--------------------------------------------------------------------------------------

function PlayerSlice (player) {
    this.base = PlayerPlugin;
    this.base (player);
    this.uuid = this.player.resource.resource_uniq;
    // do stuff
};
PlayerSlice.prototype = new PlayerPlugin();

PlayerSlice.prototype.init = function () {
    if (this.menu) return;
    var z = parseInt(this.player.dims.z);
    var t = parseInt(this.player.dims.t);
    if (z<=1 || t<=1) return;
    this.menu = this.player.menu;

    this.menu.add({
        xtype: 'displayfield',
        fieldLabel: 'Projection',
        cls: 'heading',
    });

    var def_depth = Math.ceil(z/2);
    var depth = [{'value': 0, 'text':'All'}];
    for (var i=1; i<=z; i++)
        depth.push({'value': i, 'text':i});
    this.combo_depth = this.player.createCombo( 'Depth', depth, def_depth, this, this.onDepth, 'combo_depth');

    var time = [{'value': 0, 'text':'All'}];
    for (var i=1; i<=t; i++)
        time.push({'value': i, 'text':i});
    this.combo_time = this.player.createCombo( 'Time', time, 0, this, this.onTime, 'combo_time');
};

PlayerSlice.prototype.onTime = function () {
    var nz = parseInt(this.player.dims.z);
    var nt = parseInt(this.player.dims.t);
    var t = this.combo_time.getValue();
    var z = this.combo_depth.getValue();
    if (t>0) {
        if (z!==0)
            this.combo_depth.setValue(0);
        this.changed();
    } else {
        if (z===0)
            this.combo_depth.setValue(Math.ceil(nz/2));
        this.changed();
    }
},

PlayerSlice.prototype.onDepth = function () {
    var nz = parseInt(this.player.dims.z);
    var nt = parseInt(this.player.dims.t);
    var t = this.combo_time.getValue();
    var z = this.combo_depth.getValue();
    if (z>0) {
        if (t!==0)
            this.combo_time.setValue(0);
        this.changed();
    } else {
        if (t===0)
            this.combo_time.setValue(Math.ceil(nt/2));
        this.changed();
    }
},

PlayerSlice.prototype.addCommand = function (command, pars) {
    if (pars.t && pars.z) {
        command.push('slice=,,'+pars.z+','+pars.t);
        return;
    }
    if (!this.menu) return;
    var z = this.combo_depth.getValue();
    var t = this.combo_time.getValue();
    command.push('slice=,,'+(z>0?z:'')+','+(t>0?t:''));
};

//--------------------------------------------------------------------------------------
// Plug-ins - size
//--------------------------------------------------------------------------------------

function PlayerSize (player) {
    this.base = PlayerPlugin;
    this.base (player);

    this.uuid = this.player.resource.resource_uniq;
    this.resolutions = {
        'SD':    {w: 720, h: 480, },
        'HD720': {w: 1280, h: 720, },
        'HD':    {w: 1920, h: 1080, },
        '4K':    {w: 3840, h: 2160, },
    };
};
PlayerSize.prototype = new PlayerPlugin();

PlayerSize.prototype.init = function () {
    this.def = {
        videoResolution  : BQ.Preferences.get(this.uuid, 'Viewer/video_resolution') || 'HD', // values: 'SD', 'HD720', 'HD', '4K'
    };
    if (!this.menu)
        this.createMenu();
};

PlayerSize.prototype.addCommand = function (command, pars) {
    var r = this.resolutions[this.combo_resolution.getValue()];
    command.push('resize='+r.w+','+r.h+',BC,MX');
};

PlayerSize.prototype.createMenu = function () {
    if (this.menu) return;
    this.menu = this.player.menu;

    this.menu.add({
        xtype: 'displayfield',
        fieldLabel: 'Video',
        cls: 'heading',
    });
    this.combo_resolution = this.player.createCombo( 'Video Resolution', [
        {"value":"SD",    "text":"SD (720x480)"},
        {"value":"HD720", "text":"HD 720p (1280x720)"},
        {"value":"HD",    "text":"HD 1080p (1920x1080)"},
        {"value":"4K",    "text":"4K (3840x2160)"}
    ], this.def.videoResolution, this, this.doChange, 'combo_resolution');

};

PlayerSize.prototype.doChange = function () {
    BQ.Preferences.set(this.uuid, 'Viewer/video_resolution', this.combo_resolution.value);
    this.changed();
};

//--------------------------------------------------------------------------------------
// Plug-ins - display
//--------------------------------------------------------------------------------------

function PlayerDisplay (player) {
    this.base = PlayerPlugin;
    this.base (player);
    this.uuid = this.player.resource.resource_uniq;
    this.phys = this.player.phys;
};
PlayerDisplay.prototype = new PlayerPlugin();

PlayerDisplay.prototype.init = function () {
    this.def = {
        enhancement      : BQ.Preferences.get(this.uuid, 'Viewer/enhancement') || 'd', // values: 'd', 'f', 't', 'e'
        enhancement_8bit : BQ.Preferences.get(this.uuid, 'Viewer/enhancement-8bit') || 'f',
        negative         : BQ.Preferences.get(this.uuid, 'Viewer/negative') || '',  // values: '', 'negative'
        rotate           : BQ.Preferences.get(this.uuid, 'Viewer/rotate') || 0,   // values: 0, 270, 90, 180
        fusion           : BQ.Preferences.get(this.uuid, 'Viewer/fusion'),
        fusion_method    : BQ.Preferences.get(this.uuid, 'Viewer/fusion_method') || 'm', // values: 'a', 'm'
        brightness       : BQ.Preferences.get(this.uuid, 'Viewer/brightness') || 0, // values: [-100, 100]
        contrast         : BQ.Preferences.get(this.uuid, 'Viewer/contrast') || 0, // values: [-100, 100]
        autoupdate       : false,
    };
    if (!this.menu)
        this.createMenu();
};

PlayerDisplay.prototype.addCommand = function (command, pars) {
    if (!this.menu) {
        command.push ('remap=display');
        return;
    }

    var enh = this.combo_enhancement.getValue();
    if (enh.indexOf('hounsfield') != 0) {
        command.push ('depth=8,' + this.combo_enhancement.getValue() + ',u');
    } else {
        var a = enh.split(':');
        command.push ('depth=8,hounsfield,u,,'+a[1]);
    }

    var b = this.menu.queryById('slider_brightness').getValue();
    var c = this.menu.queryById('slider_contrast').getValue();
    if (b!==0 || c!==0)
        command.push('brightnesscontrast='+b+','+c);

    var fusion = this.phys.fusion2string() + ':'+this.combo_fusion.getValue();
    command.push ('fuse='+fusion);

    var ang = this.combo_rotation.getValue();
    if (ang && ang!==''&& ang!==0)
        command.push ('rotate=' + ang);

    if (this.combo_negative.getValue()) {
        command.push(this.combo_negative.getValue());
    }
};

PlayerDisplay.prototype.createMenu = function () {
    if (this.menu) return;

    this.menu = this.player.menu;

    this.createChannelMap();

    var phys = this.player.phys,
        enhancement = phys && parseInt(phys.pixel_depth)===8 ? this.def.enhancement_8bit : this.def.enhancement;

    this.menu.add({
        xtype: 'displayfield',
        fieldLabel: 'View',
        cls: 'heading',
    });

    this.menu.add({
        xtype: 'slider',
        itemId: 'slider_brightness',
        fieldLabel: 'Brightness',
        width: 400,
        value: this.def.brightness,
        minValue: -100,
        maxValue: 100,
        increment: 10,
        zeroBasedSnapping: true,
        listeners: {
            scope: this,
            change: function(slider, v) {
                BQ.Preferences.set(this.uuid, 'Viewer/brightness', v);
                this.changed();
            },
        },
    });

    this.menu.add({
        xtype: 'slider',
        itemId: 'slider_contrast',
        fieldLabel: 'Contrast',
        width: 400,
        value: this.def.contrast,
        minValue: -100,
        maxValue: 100,
        increment: 10,
        zeroBasedSnapping: true,
        listeners: {
            scope: this,
            change: function(slider, v) {
                BQ.Preferences.set(this.uuid, 'Viewer/contrast', v);
                this.changed();
            },
        },
    });

    // fusion
    this.combo_fusion = this.player.createCombo( 'Fusion', [
        {"value":"a", "text":"Average"},
        {"value":"m", "text":"Maximum"},
    ], this.def.fusion_method, this, function() {
        BQ.Preferences.set(this.uuid, 'Viewer/fusion_method', this.combo_fusion.value);
        this.changed();
    });

    // enhancement
    var enhancement_options = phys.getEnhancementOptions();
    enhancement = enhancement_options.prefferred || enhancement;
    this.combo_enhancement = this.player.createCombo( 'Enhancement', enhancement_options, enhancement, this, function() {
        BQ.Preferences.set(this.uuid, 'Viewer/enhancement', this.combo_enhancement.value);
        this.changed();
    }, undefined, 300);

    // negative
    this.combo_negative = this.player.createCombo( 'Negative', [
        {"value":"", "text":"No"},
        {"value":"negative", "text":"Negative"},
    ], this.def.negative, this, function() {
        BQ.Preferences.set(this.uuid, 'Viewer/negative', this.combo_negative.value);
        this.changed();
    });

    // rotations
    this.combo_rotation = this.player.createCombo( 'Rotation', [
        {"value":0, "text":"No"},
        {"value":90, "text":"Right 90deg"},
        {"value":-90, "text":"Left 90deg"},
        {"value":180, "text":"180deg"},
    ], this.def.rotate, this, function() {
        BQ.Preferences.set(this.uuid, 'Viewer/rotate', this.combo_rotation.value);
        this.changed();
    });

};

PlayerDisplay.prototype.createChannelMap = function() {
    var phys = this.player.phys,
        channel_names = phys.getDisplayNames(this.uuid),
        channel_colors = phys.getDisplayColors(this.uuid);

    this.menu.add({
        xtype: 'displayfield',
        fieldLabel: 'Channels',
        cls: 'heading',
    });

    for (var ch=0; ch<phys.ch; ch++) {
        this.menu.add({
            xtype: 'colorfield',
            fieldLabel: ''+channel_names[ch],
            name: 'channel_color_'+ch,
            channel: ch,
            value: channel_colors[ch].toString().replace('#', ''),
            listeners: {
                scope: this,
                change: function(field, value) {
                    channel_colors[field.channel] = Ext.draw.Color.fromString('#'+value);
                    phys.prefsSetFusion (this.uuid);
                    this.changed();
                },
            },
        });
    }
};


//--------------------------------------------------------------------------------------
// Plug-ins - format
//--------------------------------------------------------------------------------------

function PlayerFormat (player) {
    this.base = PlayerPlugin;
    this.base (player);
    this.uuid = this.player.resource.resource_uniq;
};
PlayerFormat.prototype = new PlayerPlugin();

PlayerFormat.prototype.init = function () {
    if (this.menu) return;
    this.menu = this.player.menu;

    var z = parseInt(this.player.dims.z);
    var t = parseInt(this.player.dims.t);
    var pages = t * z;
    var fps = 30;
    if (pages < 30) fps = 15;
    if (pages < 15) fps = 6;
    fps = BQ.Preferences.get(this.uuid, 'Viewer/video_fps') || fps;

    var index = this.menu.items.findIndex( 'itemId', 'combo_resolution' );
    this.menu.insert(index+1, {
        xtype: 'numberfield',
        itemId: 'frames_per_second',
        fieldLabel: 'Frames per second',
        name: 'frames_per_second',
        value: fps,
        maxValue: 60,
        minValue: 1,
        listeners: {
            scope: this,
            change: function() {
                BQ.Preferences.set(this.uuid, 'Viewer/video_fps', this.menu.queryById('frames_per_second').getValue());
                this.changed();
            },
        },
    });
};

PlayerFormat.prototype.addCommand = function (command, pars) {
    var fps = this.menu.queryById('frames_per_second').getValue();
    var format = pars.format || 'h264';
    if (format==='jpeg')
        command.push('format=jpeg');
    else
        if (fps != 30)
            command.push('format='+format+',fps,'+fps);
        else
            command.push('format='+format);
};

