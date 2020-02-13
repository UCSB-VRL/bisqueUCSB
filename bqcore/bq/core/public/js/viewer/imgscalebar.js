function ImgScaleBar (viewer,name){
    this.base = ViewerPlugin;
    this.base (viewer, name);
}

ImgScaleBar.prototype = new ViewerPlugin();

ImgScaleBar.prototype.create = function (parent) {
    this.parentdiv = parent;
    this.scalebar = null;
    return parent;
};

ImgScaleBar.prototype.newImage = function () {

};

ImgScaleBar.prototype.updateImage = function () {
    var view = this.viewer.current_view;
    var dim = view.imagedim;
    var imgphys = this.viewer.imagephys;

    if (imgphys==null || imgphys.pixel_size[0]==undefined || imgphys.pixel_size[0]==0.0000) {
		if (this.scalebar != null) {
			this.div.removeChild (this.scalebar.widget);
			delete this.scalebar;
		}
		this.scalebar = null;
		return;
    }

    var surf = this.parentdiv;
    if (this.scalebar == null) this.scalebar = new ScaleBar ( surf, imgphys.pixel_size[0]/view.scale, imgphys.units);
	this.scalebar.setPixSize(imgphys.pixel_size[0]/view.scale);
	this.scalebar.resetValue();
};

ImgScaleBar.prototype.updatePosition = function () {
    if (this.scalebar == null) return;
    var view = this.viewer.current_view;

    var imgphys = this.viewer.imagephys;
	this.scalebar.setPixSize(imgphys.pixel_size[0]/view.scale);
	this.scalebar.resetValue();
};
