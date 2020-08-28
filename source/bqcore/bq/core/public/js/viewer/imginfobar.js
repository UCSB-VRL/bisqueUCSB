/*******************************************************************************
  ImgInfoBar - creates text about an image

  GSV 3.0 : PanoJS3
  @author Dmitry Fedorov  <fedorov@ece.ucsb.edu>

  Copyright (c) 2010 Dmitry Fedorov, Center for Bio-Image Informatics

  using: isClientTouch() and isClientPhone() from utils.js

*******************************************************************************/

function ImgInfoBar (viewer,name){
    this.base = ViewerPlugin;
    this.base (viewer, name);
}

ImgInfoBar.prototype = new ViewerPlugin();
ImgInfoBar.prototype.create = function (parent) {
    this.parentdiv = parent;
    this.infobar = null;
    this.namebar = null;
    this.mobile_cls = '';
    if (isClientTouch())
        this.mobile_cls = 'tablet';
    if (isClientPhone())
        this.mobile_cls = 'phone';
    return parent;
};

ImgInfoBar.prototype.newImage = function () {

};

ImgInfoBar.prototype.updateImage = function () {
    var viewer = this.viewer,
        view = viewer.current_view,
        dim = view.imagedim,
        phys = viewer.imagephys,
        surf = viewer.viewer_controls_surface ? viewer.viewer_controls_surface : this.parentdiv,
        params = viewer.parameters || {};

    // create info bar
    if (!this.infobar) {
        this.infobar = document.createElement('span');
        this.infobar.className = 'info '+this.mobile_cls;
        surf.appendChild(this.infobar);
    }

    // create name bar
    if (!this.namebar && !(viewer.parameters && viewer.parameters.hide_file_name_osd) ) {
        this.namebar = document.createElement('a');
        this.namebar.className = params.logo ? 'info name logo '+this.mobile_cls : 'info name '+this.mobile_cls;
        surf.appendChild(this.namebar);
    }

    // create position bar
    if (!this.posbar) {
        this.posbar = document.createElement('a');
        this.posbar.className = 'info position '+this.mobile_cls;
        surf.appendChild(this.posbar);
    }

    if (this.infobar) {
        var s = 'Image: '+dim.x+'x'+dim.y;
        if (dim.z>1) s += ' Z:'+dim.z;
        if (dim.t>1) s += ' T:'+dim.t;
        s += ' ch: '+ dim.ch;
        if (phys && phys.pixel_depth) s += '/'+ phys.pixel_depth +'bits';
        s += ' Scale: '+ view.scale*100 +'%';
        this.infobar.innerHTML = s;
    }

    if (this.namebar) {
        this.namebar.href = '/client_service/view?resource='+viewer.image.uri;
        if (!params.logo) {
            this.namebar.innerHTML = viewer.image.name;
        }
    }
};

ImgInfoBar.prototype.updateView = function (view) {
    if (!this.label && this.viewer.viewer_controls_surface) this.createLabel();
};

ImgInfoBar.prototype.createLabel = function () {
    if (this.label) return;
    this.uuid = this.viewer.image.resource_uniq;
    this.phys = this.viewer.imagephys;

    if (this.phys.previews) {
        this.label = true;
        this.preview = Ext.create('BQ.viewer.LabelView', {
            renderTo: this.viewer.viewer_controls_surface || this.viewer.imagediv,
            cls: 'preview',
            uri: Ext.String.format('/image_service/{0}/preview?depth=8,d,u&format=jpeg', this.uuid),
        });
    }

    if (this.phys.labels) {
        this.label = Ext.create('BQ.viewer.LabelView', {
            renderTo: this.viewer.viewer_controls_surface || this.viewer.imagediv,
            cls: 'label',
            uri: Ext.String.format('/image_service/{0}/label?depth=8,d,u&rotate=-90&format=jpeg', this.uuid),
        });
    }

};

//-----------------------------------------------------------------------
// BQ.editor.GraphicalSelector - Graphical annotations menu
//-----------------------------------------------------------------------

Ext.define('BQ.viewer.LabelView', {
    extend: 'BQ.viewer.MenuButton',
    alias: 'widget.viewer_label_view',
    componentCls: 'preview_button',

    afterRender : function() {
        this.callParent();
        this.getEl().dom.style.backgroundImage = Ext.String.format("url('{0}')", this.uri);
    },

    createMenu: function() {
        if (this.menu) return;
        var buttons = [],
            el = this.getEl(),
            offset = el.getY(),
            h = 90;

        this.menu = Ext.create('Ext.tip.ToolTip', {
            target: el,
            anchor: 'right',
            anchorToTarget: true,
            anchorOffset: 5,
            cls: 'bq-viewer-menu label',
            width: 650,
            height: 300,
            //height: h,
            autoHide: true,
            shadow: false,
            closable: false,
            layout: 'fit',
            items: [{
                xtype: 'component',
                cls: 'preview_image',
                style: Ext.String.format("background-image: url({0});", this.uri),
            }],
        });
    },

    onPreferences: function() {
        //this.auto_hide = BQ.Preferences.get('user','Viewer/gobjects_editor_auto_hide', true);
    },

});

