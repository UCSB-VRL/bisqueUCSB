function ImageConverter (viewer, name) {
    this.base = ViewerPlugin;
    this.base (viewer, name);

    this.viewer.addMenu([{
        itemId: 'menu_viewer_converter',
        xtype:'button',
        text: 'Convert',
        iconCls: 'converter',
        tooltip: 'Convert and download the current image',
        scope: this,
        handler: this.convert,
    }, '-' ]);
}
ImageConverter.prototype = new ViewerPlugin();

ImageConverter.prototype.create = function (parent) {
    return parent;
};

ImageConverter.prototype.newImage = function () {
};

ImageConverter.prototype.updateImage = function () {
};

ImageConverter.prototype.convert = function () {
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

