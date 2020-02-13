function ImgOperations (viewer, name) {
    var p = viewer.parameters || {};
    this.default_enhancement      = p.enhancement     || 'd'; // values: 'd', 'f', 't', 'e'
    this.default_enhancement_8bit = p.enhancement8bit || 'f';
    this.default_negative         = p.negative        || '';  // values: '', 'negative'
    this.default_fusion_method    = p.fusion_method   || 'm'; // values: 'a', 'm'
    this.default_fusion_method_4plus  = p.default_fusion_method_4plus || 'm';
    this.default_rotate           = p.rotate          || 0;   // values: 0, 270, 90, 180

    this.default_brightness       = p.brightness      || 0;   // values: [-100, 100]
    this.default_contrast         = p.contrast        || 0;   // values: [-100, 100]

    this.default_autoupdate       = false;

    this.base = ViewerPlugin;
    this.base (viewer, name);
}
ImgOperations.prototype = new ViewerPlugin();

ImgOperations.prototype.create = function (parent) {
    this.parent = parent;
    return parent;
};

ImgOperations.prototype.newImage = function () {
    this.phys_inited = false;
};

ImgOperations.prototype.updateImage = function () {

};

ImgOperations.prototype.getParams = function () {
    return this.params || {};
};

ImgOperations.prototype.updateView = function (view) {
    if (!this.menu  && this.viewer.viewer_controls_surface) this.createMenu();
    if (this.menu) {
        this.params = {};

        var channels_separate = 'cs'; // cs cc
        var b = this.menu.queryById('slider_brightness').getValue();
        var c = this.menu.queryById('slider_contrast').getValue();
        var enh = this.combo_enhancement.getValue();
        this.params.enhancement = enh;
        if (enh.indexOf('hounsfield') != 0) {
            if (b!==0 || c!==0) view.addParams  ('brightnesscontrast='+b+','+c);
            view.addParams  ('depth=8,' + this.combo_enhancement.getValue() + ',u,cs');
        } else {
            var a = enh.split(':');
            view.addParams  ('depth=8,hounsfield,u,,'+a[1]);
            if (b!==0 || c!==0) view.addParams  ('brightnesscontrast='+b+','+c);
        }

        var fusion = this.phys.fusion2string() + ':'+this.combo_fusion.getValue();
        view.addParams  ('fuse='+fusion);

/*
        cb = this.menu_elements['Rotate'];
        if (cb.value != 0)
            view.addParams  ('rotate=' + cb.value);
        cb.disabled=true; // no rotation for now
        view.rotateTo( parseInt(cb.value) );
*/

        if (this.combo_negative.getValue()) {
            this.params.negative = this.combo_negative.getValue();
            view.addParams(this.combo_negative.getValue());
        }
    }
};

ImgOperations.prototype.doUpdate = function () {
    this.viewer.need_update();
};

ImgOperations.prototype.changed = function () {
    if (!this.update_check || (this.update_check && this.update_check.checked) )
        this.viewer.need_update();
};

ImgOperations.prototype.save_brightness = function (v) {
    var me = this;
    clearTimeout(this.timeout_brightness);
    this.timeout_brightness = setTimeout(function(){
        BQ.Preferences.set(me.uuid, 'Viewer/brightness', v);
    }, 500);
};

ImgOperations.prototype.save_contrast = function (v) {
    var me = this;
    clearTimeout(this.timeout_contrast);
    this.timeout_contrast = setTimeout(function(){
        BQ.Preferences.set(me.uuid, 'Viewer/contrast', v);
    }, 500);
};

ImgOperations.prototype.createMenu = function () {
    if (this.menu) return;
    this.menu = this.viewer.createViewMenu();
    this.uuid = this.viewer.image.resource_uniq;
    this.phys = this.viewer.imagephys;

    var dim = this.viewer.imagedim,
        phys = this.viewer.imagephys,
        enhancement = phys && parseInt(phys.pixel_depth)===8 ? this.default_enhancement_8bit : this.default_enhancement,
        fusion_method = phys && parseInt(phys.ch)>3 ? this.default_fusion_method_4plus : this.default_fusion_method;

    this.createChannelMap();

    this.menu.add({
        xtype: 'displayfield',
        fieldLabel: 'View',
        cls: 'heading',
    });

    this.menu.add({
        xtype: 'slider',
        itemId: 'slider_brightness',
        fieldLabel: 'Brightness',
        cls: 'contrast',
        width: 400,
        value: this.default_brightness,
        minValue: -100,
        maxValue: 100,
        increment: 10,
        zeroBasedSnapping: true,
        checkChangeBuffer: 150, // dima: does not seem to work
        listeners: {
            scope: this,
            change: function(slider, v) {
                this.save_brightness(v);
                this.changed();
            },
        },
    });

    this.menu.add({
        xtype: 'slider',
        itemId: 'slider_contrast',
        fieldLabel: 'Contrast',
        cls: 'contrast',
        width: 400,
        value: this.default_contrast,
        minValue: -100,
        maxValue: 100,
        increment: 10,
        zeroBasedSnapping: true,
        checkChangeBuffer: 150, // dima: does not seem to work
        listeners: {
            scope: this,
            change: function(slider, v) {
                this.save_contrast(v);
                this.changed();
            },
        },
    });

    this.combo_fusion = this.viewer.createCombo( 'Fusion', [
        {"value":"a", "text":"Average"},
        {"value":"m", "text":"Maximum"},
    ], fusion_method, this,
    function() {
        BQ.Preferences.set(this.uuid, 'Viewer/fusion_method', this.combo_fusion.value);
        this.changed();
    });

    var enhancement_options = phys.getEnhancementOptions();
    enhancement = enhancement_options.prefferred || enhancement;
    this.combo_enhancement = this.viewer.createCombo( 'Enhancement', enhancement_options, enhancement, this,
    function() {
        var enhancementVer = phys && parseInt(phys.pixel_depth)===8 ? 'enhancement-8bit' : 'enhancement';
        BQ.Preferences.set(this.uuid, 'Viewer/'+enhancementVer, this.combo_enhancement.value);
        this.changed();
    },
    300);

    this.combo_negative = this.viewer.createCombo( 'Negative', [
        {"value":"negative", "text":"Yes"},
        {"value":"", "text":"No"},
    ], this.default_negative, this,
    function() {
        BQ.Preferences.set(this.uuid, 'Viewer/negative', this.combo_negative.value);
        this.changed();
    });
};

ImgOperations.prototype.createChannelMap = function ( ) {
    var phys = this.viewer.imagephys,
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
                    var c = Ext.draw.Color.fromString('#'+value);
                    if (c) {
                        channel_colors[field.channel] = c;
                        phys.prefsSetFusion (this.uuid);
                        this.changed();
                    }
                },
            },
        });
    }
};

ImgOperations.prototype.onPreferences = function () {
    var resource_uniq = this.viewer.image.resource_uniq;
    this.default_autoupdate       = BQ.Preferences.get(resource_uniq, 'Viewer/autoUpdate',       this.default_autoupdate);
    this.default_negative         = BQ.Preferences.get(resource_uniq, 'Viewer/negative',         this.default_negative);
    this.default_enhancement      = BQ.Preferences.get(resource_uniq, 'Viewer/enhancement',      this.default_enhancement);
    this.default_rotate           = BQ.Preferences.get(resource_uniq, 'Viewer/rotate',           this.default_rotate);
    this.default_enhancement_8bit = BQ.Preferences.get(resource_uniq, 'Viewer/enhancement-8bit', this.default_enhancement_8bit);
    this.default_fusion_method    = BQ.Preferences.get(resource_uniq, 'Viewer/fusion_method',    this.default_fusion_method) || this.default_fusion_method;
    this.default_fusion_method_4plus     = BQ.Preferences.get(resource_uniq, 'Viewer/fusion_method_4plus',  this.default_fusion_method_4plus) || this.default_fusion_method_4plus;
    this.default_brightness       = BQ.Preferences.get(resource_uniq, 'Viewer/brightness',       this.default_brightness) || this.default_brightness;
    this.default_contrast         = BQ.Preferences.get(resource_uniq, 'Viewer/contrast',         this.default_contrast) || this.default_contrast;
};



//-----------------------------------------------------------------------
// BQ.editor.GraphicalSelector - Graphical annotations menu
//-----------------------------------------------------------------------

Ext.define('BQ.viewer.ViewMenu', {
    extend: 'BQ.viewer.MenuButton',
    alias: 'widget.viewer_menu_view',
    componentCls: 'viewoptions',

    createMenu: function() {
        if (this.menu) return;
        var buttons = [],
            el = this.getEl(),
            offset = el.getY(),
            h = 90;

        this.menu = Ext.create('Ext.tip.ToolTip', {
            target: el,
            anchor: 'top',
            anchorToTarget: true,
            anchorOffset: -5,
            cls: 'bq-viewer-menu',
            width: 460,
            //height: h,
            autoHide: false,
            shadow: false,
            closable: true,
            layout: {
                type: 'vbox',
                //align: 'stretch',
                //pack: 'start',
            },
            defaults: {
                labelSeparator: '',
                labelWidth: 200,
            },
            //items: items,
        });
    },

    onPreferences: function() {
        //this.auto_hide = BQ.Preferences.get('user','Viewer/gobjects_editor_auto_hide', true);
    },

});
