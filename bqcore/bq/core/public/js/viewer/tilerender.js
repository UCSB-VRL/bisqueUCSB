
PanoJS.MSG_BEYOND_MIN_ZOOM = null;
PanoJS.MSG_BEYOND_MAX_ZOOM = null;
PanoJS.STATIC_BASE_URL = '/core/panojs3/';
PanoJS.CREATE_INFO_CONTROLS = false;
PanoJS.CREATE_THUMBNAIL_CONTROLS = true;
PanoJS.USE_KEYBOARD = false;

function TilesRenderer (viewer,name){
    this.base = ViewerPlugin;
    this.base (viewer, name);
    this.events    = {};
    this.tile_size = 512;
    this.template  = 'tile=0,0,0,'+this.tile_size;
    this.myTileProvider = new PanoJS.TileUrlProvider('','','');
};

TilesRenderer.prototype = new ViewerPlugin();

TilesRenderer.prototype.create = function (parent) {
    this.parent = parent;
    this.div  = document.createElementNS(xhtmlns, "div");
    this.div.id =  'tiled_viewer';
    this.div.className = 'viewer';
    this.div.style.width = '100%';
    this.div.style.height = '100%';
    this.parent.appendChild(this.div);
    return this.div;
};

TilesRenderer.prototype.newImage = function () {

};

TilesRenderer.prototype.updateView = function (view) {
    view.addParams ( this.template ); // add a placeholder for tile request, replaced later by the actual tile request
};

TilesRenderer.prototype.updateImage = function (){
    var viewstate = this.viewer.current_view;
    if (this.cur_t && this.cur_z && this.cur_t==viewstate.t && this.cur_z==viewstate.z) return;
    this.cur_t=viewstate.t; this.cur_z=viewstate.z;

    this.base_url = this.viewer.image_url();

    // update tile provider code
    var myPyramid = this.pyramid = new BisqueISPyramid( viewstate.imagedim.x, viewstate.imagedim.y, this.tile_size);
    var myTemplate = this.template;
    var myURL = this.base_url;

    this.myTileProvider.assembleUrl = function(xIndex, yIndex, zoom) {
        return myURL.replace(myTemplate, myPyramid.tile_filename( zoom, xIndex, yIndex ));
    };

    // create tiled viewer
    if (!this.tiled_viewer) {
      this.tiled_viewer = new PanoJS(this.div, {
          tileUrlProvider : this.myTileProvider,
          tileSize        : myPyramid.tilesize,
          maxZoom         : myPyramid.getMaxLevel(),
          imageWidth      : myPyramid.width,
          imageHeight     : myPyramid.height,
          blankTile       : PanoJS.STATIC_BASE_URL + 'images/blank.gif',
          loadingTile     : PanoJS.STATIC_BASE_URL + 'images/progress_' + this.tile_size+ '.gif'
      });

      // this listener will update viewer if scale has changed in the tiled viewer
      this.myZoomListener = new ZoomListner(this.tiled_viewer, this.viewer);

      // this listener will update viewer if scale has changed in the tiled viewer
      this.myCursorListner = new CursorListner(this.tiled_viewer, this.viewer);

      // this listener will update viewer size
      this.myResizeListner = new TiledResizeListner(this.tiled_viewer, this);

      //Ext.EventManager.addListener( window, 'resize', callback(this.tiled_viewer, this.tiled_viewer.resize) );
      this.tiled_viewer.init();
      this.viewer.viewer_controls_surface = this.div;

      this.div.contentEditable=true;
      this.div.focus();
      this.div.addEventListener('keydown', callback(this, this.onkeyboard), false);

    } else {
      // only update all the tiles in the viewer
      this.tiled_viewer.tileUrlProvider = this.myTileProvider;
      this.tiled_viewer.update();
    }
};

TilesRenderer.prototype.resize = function () {
    if (this.tiled_viewer)
        this.tiled_viewer.resize();
};

TilesRenderer.prototype.ensureVisible = function (gob) {
    if (!this.tiled_viewer || !gob || !gob.vertices || gob.vertices.length<1) return;
    var x = gob.vertices[0].x;
    var y = gob.vertices[0].y;
    var v=undefined;
    if (gob.vertices.length>1 && gob.resource_type in {polyline: undefined, polygon: undefined}) {
        for (var i=1; (v=gob.vertices[i]); i++) {
            x += v.x;
            y += v.y;
        }
        x /= gob.vertices.length;
        y /= gob.vertices.length;
    }
    this.tiled_viewer.ensureVisible({x: x, y: y});
};

TilesRenderer.prototype.getLoadedTileUrls = function () {
    return this.tiled_viewer.loadedTileUrls();
};

TilesRenderer.prototype.mousemove = function (e) {
    if (!e) e = window.event;  // IE event model
    if (e == null) return;
    //if (!(e.target===this.renderer.svgdoc ||
    //      e.target===this.renderer.svggobs ||
    //      (this.current_gob && e.target===this.current_gob.shape.svgNode))) return;

    this.div.focus();
    var view = this.viewer.current_view,
        p = this.renderer.getUserCoord(e),
        pt = view.inverseTransformPoint(p.x, p.y);
    this.viewer.print_coordinate(pt, true, true);
};

TilesRenderer.prototype.onkeyboard = function (e) {
    if (e.target !== this.div) return;
    this.tiled_viewer.keyboardHandler(e);
};

// Cursor Move Listner
function CursorListner(viewer, parent) {
    this.viewer = viewer;
    this.parent = parent;
    this.viewer.addCursorMovedListener(this);
}

CursorListner.prototype.cursorMoved = function(e) {
    this.parent.viewer_controls_surface.focus();
    this.parent.print_coordinate(e, true, true);
};

// Resize Listner
function TiledResizeListner(viewer, parent) {
    this.viewer = viewer;
    this.parent = parent;
    this.viewer.addViewerResizedListener(this);
}

TiledResizeListner.prototype.viewerResized = function(e) {
    this.parent.resize();
};
