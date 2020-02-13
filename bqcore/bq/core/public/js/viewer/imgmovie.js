function ImgMovie (viewer,name){
    this.base = ViewerPlugin;
    this.base (viewer, name);

    this.viewer.addMenu({
        itemId: 'menu_viewer_movie',
        xtype:'button',
        text: 'View as movie',
        iconCls: 'movie',
        tooltip: 'View and export current image as a movie',
        scope: this,
        handler: this.showMovie
    });
}
ImgMovie.prototype = new ViewerPlugin();

ImgMovie.prototype.create = function (parent) {
    this.parent = parent;
    return parent;
};

ImgMovie.prototype.newImage = function () {
    if (!this.viewer.toolbar) return;
    var m = this.viewer.toolbar.queryById('menu_viewer_movie');
    if (m) {
        m.setDisabled(this.viewer.imagedim.z * this.viewer.imagedim.t < 2);
    }
};

ImgMovie.prototype.updateImage = function () {
    // nothing here
};

ImgMovie.prototype.showMovie = function () {
    var player = Ext.create('BQ.viewer.Movie.Dialog', {
        resource: this.viewer.image,
        phys: this.viewer.imagephys,
        preferences: this.viewer.preferences
    });
};

