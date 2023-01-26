/*
  Image Viewer shell for Bisquik viewer
  The viewer can contain plugins that may modify the
  the image src and the current image contents (i.e the view)


  Example call:
     var viewer_params = {'gobjects':'http://gobejcts_url', 'noedit':''};
     var image_viewer = new ImgViewer ("parent_div_id", 'http://image_url', 'user_name', viewer_params );

  Available parameters:
    simpleviewer   - sets a minimal set of plug-ins and also read-only view for gobjects
    onlyedit       - only sets plug-in needed for editing of gobjects

    *** NOT IMPLEMENTED ***
        intialMode     - Sets the first mode on the viewer after instantiated.
            Modes:
                : navigation - initializes in navigation mode
                : edit - initializes in edit mode
                : delete - intializes in delete mode
                : point - starts in edit mode with points
                : rectangle - starts in edit mode with rectangle
                : polyline - starts in edit mode with polyline
                : polygon - starts in edit mode with polygons
                : circle - starts in edit mode with circles

        disableMaximize - disables the maximize window option form the viewer
        disableViewOptions -
        disableThumbnail -
        minimizeThumbnail -
    *** NOT IMPLEMENTED ***

    nogobects      - disable loading gobjects by default
    gobjects       - load gobjects from the givel URL, 'gobjects':'http://gobejcts_url'

    noedit         - read-only view for gobjects
    alwaysedit     - instantiates editor right away and disables hiding it
    nosave         - disables saving gobjects
    editprimitives - only load edit for given primitives, 'editprimitives':'point,polyline'
                       can be one of: 'Point,Rectangle,Polyline,Polygon,Circle'

    external_edit_controls - when set to true will stop the viewer creating any editor buttons

    gobjectschanged - callback to call when graphical objects have changed
    gobjectDeleted - callback to call when graphical objects have been deleted

    gobjectMove      - returns shape object when manipulating a gobject, shape object has pointer to gob
    gobjectMoveStart - returns shape object when beginning a gobject manipulation, shape object has pointer to gob
    gobjectMoveEnd   - returns shape object when ending a gobject manipulation, shape object has pointer to gob

    onworking - callback to call when graphical objects have changed
    ondone - callback to call when graphical objects have changed
    onerror - callback to call when graphical objects have changed

*/


var imgview_min_width = 400;


////////////////////////////////////////////////////////////
// ImageDim
// Maintain a record of image imagedimensions

function ImageDim (x, y, z, t, ch){
    this.x = x;
    this.y = y;
    this.z = z;
    this.t = t;
    this.ch = ch;
};
ImageDim.prototype.clone = function () {
    return new ImageDim(this.x, this.y, this.z, this.t, this.ch);
};

////////////////////////////////////////////////////////////
// Viewstate
// Current viewer properties (viewed dimensions)

function Viewstate (w, h, z, t, scale, rot, offx, offy,origw,origh) {


    this.width = w;
    this.height = h;
    this.z = z;
    this.t = t;
    this.scale = scale;
    this.rotation = rot || 0;
    this.offset_x = offx || 0;
    this.offset_y = offy || 0;
    this.original_width = origw || w;
    this.original_height = origh|| h;

    this.gob_tolerance = { z: 1.0, t: 1.0 };

    this.imagedim = null;
    this.imagesrc = null;

    this.src_args = [];         // Array of arguments
};

Viewstate.prototype.clone = function  () {
    var v =  new Viewstate (this.width, this.height, this.z, this.t,
                            this.scale, this.rotation,
                            this.offset_x, this.offset_y);
    if (this.imagedim)
        v.imagedim = this.imagedim.clone();
    v.imagesrc = this.imagesrc;
    return v;
};


Viewstate.prototype.setSizeTo = function  (w, h) {
    this.width = w;
    this.height = h;
    this.original_width = w;
    this.original_height = h;
    this.scaleBy(1);
};

Viewstate.prototype.scaleBy = function  (scale_by) {
    if (scale_by<1 && Math.min(this.width*scale_by, this.height*scale_by) < imgview_min_width )
        scale_by = Math.max(imgview_min_width/this.width, imgview_min_width/this.height);

    this.scale *= scale_by;
    this.width *= scale_by;
    this.height *= scale_by;
};

Viewstate.prototype.scaleToBox = function  (bound_w, bound_h) {
    bound_w = Math.max(bound_w, imgview_min_width);
    bound_h = Math.max(bound_h, imgview_min_width);
    var scale = Math.max(bound_w/this.original_width, bound_h/this.original_height);

    this.scale  = scale;
    this.width  = scale*this.original_width;
    this.height = scale*this.original_height;
};

Viewstate.prototype.scaleTo = function  (new_scale) {
    this.scale  = new_scale;
    this.width  = this.scale*this.original_width;
    this.height = this.scale*this.original_height;
};

Viewstate.prototype.scaleToSmallest = function  () {
    this.scaleToBox(imgview_min_width, imgview_min_width);
};

Viewstate.prototype.rotateTo = function(alfa) {
    this.rotation = alfa;

    var ow = this.original_width * this.scale;
    var oh = this.original_height * this.scale;
    var wp = ow;
    var hp = oh;

    var a = this.rotation * ( Math.PI/180.0 );
    var sina = Math.sin(a);
    var cosa = Math.cos(a);
    if (sina*cosa < 0) {
      wp = Math.abs(ow*cosa - oh*sina);
      hp = Math.abs(ow*sina - oh*cosa);
    } else {
      wp = Math.abs(ow*cosa + oh*sina);
      hp = Math.abs(ow*sina + oh*cosa);
    }

    this.width = wp;
    this.height = hp;
};

Viewstate.prototype.transformPoint = function  (ix, iy) {
    var x = ix * this.scale + this.offset_x;
    var y = iy * this.scale + this.offset_y;

    var ow = this.original_width * this.scale;
    var oh = this.original_height * this.scale;
    x = x - ow/2.0;
    y = y - oh/2.0;
    var a = this.rotation * ( Math.PI/180.0 );
    var sina = Math.sin(a);
    var cosa = Math.cos(a);
    var xp = x*cosa - y*sina;
    var yp = x*sina + y*cosa;
    xp += this.width/2.0;
    yp += this.height/2.0;

    return { x:xp, y:yp };
};

Viewstate.prototype.inverseTransformPoint = function  (ix, iy) {

    var x = (ix - this.offset_x - this.width/2.0) / this.scale;
    var y = (iy - this.offset_y - this.height/2.0) / this.scale;

    var a = (360-this.rotation) * ( Math.PI/180.0 );
    var sina = Math.sin(a);
    var cosa = Math.cos(a);
    var xp = x*cosa - y*sina;
    var yp = x*sina + y*cosa;
    xp += this.original_width/2.0;
    yp += this.original_height/2.0;

    return { x: Ext.util.Format.round(xp, 2), y: Ext.util.Format.round(yp, 2) };
};


Viewstate.prototype.addParams = function (params) {
    params = params || [];
    if ( params instanceof Array ) {
        for (var  i =0;  params.length ; i++)
            this.src_args.push (params[i]);
        return;
    }
    this.src_args.push (params);
};

Viewstate.prototype.image_url = function (auxparams) {
    var url = this.imagesrc;
    var params = auxparams || [];

    var args = null;
    var arglist = this.src_args.concat();
    //for (var x in params) arglist.push (params[x]);
    for (var i=0; i<params.length; i++)
      arglist.push (params[i]);

    arglist.push ('format=jpeg');

    for (var i = 0; i < arglist.length; i++) {
        if (args == null)
            args = "?" + arglist[i];
        else
            args += "&" + arglist[i];
    }
    return url + args;
};



////////////////////////////////////////////////////////////
// ImagePhys
// Maintain a record of image physical parameters
function ImagePhys () {
    this.pixel_size = new Array (0);
    this.channel_names = new Array (0);
    this.display_channels = new Array (0);
};

ImagePhys.prototype.setPixelSize = function ( x, y, z, t ) {
    this.pixel_size[0] = x;
    this.pixel_size[1] = y;
    this.pixel_size[2] = z;
    this.pixel_size[3] = t;
};
////////////////////////////////////////////////////////////
// ViewerPlugin
// ImgViewer extensions are plugins that are arranged as pipeline
//      ImageViewer
//  P1 -> P2 -> P3 -> P4

function ViewerPlugin (viewer, name) {
    this.child = null;          // Next in line viewer or html element
    this.viewer= viewer || null;   // The top level viewer
    this.name  = name || "";    // name for logging and such
};
ViewerPlugin.prototype.create = function (parent){
    return parent;
};
ViewerPlugin.prototype.newImage = function (){

};
ViewerPlugin.prototype.updateImage = function (){
};

ViewerPlugin.prototype.onPreferences = function (){
};

ViewerPlugin.prototype.updateView = function (view){
};

// this will be called after all updateImage were called, if any elements are to be positioned
// relative to elements resized later in updateImage queue
ViewerPlugin.prototype.updatePosition = function (){
};

ViewerPlugin.prototype.setSize = function (size)
{
    if (size.height)
        this.imagediv.style.height = size.height+"px";
    if (size.width)
        this.imagediv.style.width = size.width+"px";
};

////////////////////////////////////////////////////////////
// DefaultPlugin
//  A simple plugin as a example.. Set the view size based
//  on the image size

function DefaultImgPlugin (viewer, name) {
    this.base = ViewerPlugin;
    this.base (viewer, name);

//    this.viewer.addCommand ('blink', callback (this, 'blink'));
};

DefaultImgPlugin.prototype = new ViewerPlugin();
DefaultImgPlugin.prototype.newImage = function () {
    var d = this.viewer.imagedim;
    var v = this.viewer.current_view;
    v.setSizeTo( d.x, d.y );
    //var view = this.viewer.view();
    //this.viewer.src_args.push ('resize=' + view.width + ',' + view.height );
    //this.viewer.src_args.push ('format=jpeg');
};

DefaultImgPlugin.prototype.blink = function (){
    alert ('blink');
};

//////////////////////////////////////////////////////
//  Image Viewer shell for Bisquik viewer
//  The viewer can contain plugins that may modify the
//  the image src and the current image contents (i.e the view)

function ImgViewer (parentid, image_or_uri, parameters) {

    this.update_delay_ms = 250;  // Update the viewer asynchronously

    this.target = getObj(parentid);
    this.imageuri = null;   // Toplevel Image URI
    this.plugins = [];          // Ordered array of plugins to be called
    this.plugins_by_name = {};  // dictionary of plugins
    this.imagedim = null;      // Original Image dimensions
    this.imagesrc = null;       // Constructed image src
    this.imagephys = null;
    this.current_view = null;
    this.groups = {};           // Menu Groups
    this.submenu = null;
    this.image_or_uri = image_or_uri;

    this.parameters = Ext.apply(parameters || {}, this.getAttributes());

    //this.menudiv = document.createElementNS (xhtmlns, "div");
    //this.menudiv.id =  "imgmenu";
    //this.menudiv.className = "buttonbar";

    this.imagediv = document.createElementNS (xhtmlns, "div");
    this.imagediv.id="imgviewer_image";
    this.imagediv.className = "image_viewer_display";
    var me = this;

    //initializing preference for the image viewer
    this.preferences = this.parameters.preferences;

    /*
    BQ.Preferences.get({
        key : 'Viewer',
        callback : Ext.bind(this.onPreferences, this),
    });
    */
    this.target.appendChild (this.imagediv);
    this.toolbar = this.parameters.toolbar;
    this.widget = this.parameters.widget;
    this.plugins_skip = this.parameters.plugins_skip || {};


    var plugin_list = "default,slicer,tiles,ops,download,external,pixelcounter,scalebar,progressbar,infobar,overlay,edit,renderer";
    if ('onlyedit' in this.parameters)
        plugin_list = "default,slicer,tiles,ops,scalebar,progressbar,infobar,overlay,edit,renderer";
    if ('simpleview' in this.parameters) {
        plugin_list = "default,slicer,tiles,ops,scalebar,progressbar,infobar,renderer";
        this.parameters['noedit'] = '';
    }

    if (ImgViewer.pluginmap == null)
        ImgViewer.pluginmap = {
            "default"     : DefaultImgPlugin,
            "movie"       : ImgMovie,
            "external"    : ImgExternal,
            "converter"   : ImageConverter,
            "statistics"  : ImgStatistics,
            "scalebar"    : ImgScaleBar,
            "progressbar" : ProgressBar,
            "infobar"     : ImgInfoBar,
            "slicer"      : ImgSlicer,
            "edit"        : ImgEdit,
            "tiles"       : TilesRenderer, // TILES RENDERER MUST BE BEFORE SVGRenderer
            "ops"         : ImgOperations, // Ops should be after tiler
            "pixelcounter": ImgPixelCounter,
            "overlay"     : SVGRenderer,
            "renderer"    : CanvasRenderer,   // RENDERER MUST BE LAST
        };

    var plugin_names = plugin_list.split(',');
    for (var i=0; i < plugin_names.length; i++) {
        var name = plugin_names[i];
        var ctor = ImgViewer.pluginmap[name];
        if (ctor)
           this.plugins_by_name[name] = this.addPlugin (new ctor(this, name));
    }

    this.init();
};

ImgViewer.prototype = new ViewerPlugin();
ImgViewer.prototype.close = function (){
    history.back();
};

ImgViewer.prototype.getAttributes = function () {
    var s = window.location.hash.replace(/^#/, '') || window.location.search.replace(/^\?/, '');
    var attributes = {};
    var aa = s.split('&');
    var a = undefined;
    for (var i=0; a=aa[i]; ++i) {
        var b = a.split('=', 2);
        attributes[b[0]] =  decodeURIComponent(b[1]);
    }
    return attributes;
};

ImgViewer.prototype.init = function () {
    this.renderer = this.plugins_by_name.renderer;
    this.overlay  = this.plugins_by_name.overlay;
    this.editor   = this.plugins_by_name.edit;
    this.tiles    = this.plugins_by_name.tiles;
    this.slicer   = this.plugins_by_name.slicer;
    this.createPlugins(this.imagediv);
    if (this.image_or_uri instanceof BQImage)
        this.newImage(this.image_or_uri);
    else if (this.image_or_uri instanceof BQObject)
        throw BQOperationError;
    else if (this.image_or_uri)
        this.load(this.image_or_uri);
};

ImgViewer.prototype.cleanup = function() {
    this.target.removeChild (this.imagediv);
    //mouser=null;
};

ImgViewer.prototype.addPlugin = function  (plugin) {
    this.plugins.push (plugin);
    return plugin;
};

ImgViewer.prototype.onkeyboard = function(e) {
    if (!this.tiles) return;
    this.tiles.tiled_viewer.keyboardHandler(e);
};

////////////////////////////////////////
// Ask each plugin to create the needed structures including divs.
//
ImgViewer.prototype.createPlugins = function (parent) {
    var currentdiv = parent;
    for (var i=0; i < this.plugins.length; i++) {
        var plugin = this.plugins[i];
        currentdiv = plugin.create (currentdiv);
    }
};

ImgViewer.prototype.addMenu = function (m) {
    if (!this.toolbar) return;
    var toolbar = this.toolbar;
    var n = toolbar.items.getCount()-4;
    var menu = toolbar.insert(n, m);
    toolbar.doLayout();
    if (menu.length === 1)
        return menu[0];
    return menu;
};

ImgViewer.prototype.view = function  () {
    return this.current_view;
};

ImgViewer.prototype.resize = function  (sz) {
    if (sz && sz.height)
        //this.imagediv.style.height = (sz.height-this.menudiv.clientHeight)+"px";
        this.imagediv.style.height = sz.height+"px";

    if (sz && sz.width)
        this.imagediv.style.width = sz.width+"px";

  if ('tiles' in this.plugins_by_name)
    this.plugins_by_name.tiles.resize();

  if ('renderer' in this.plugins_by_name)
    this.plugins_by_name.renderer.updateImage();
};


ImgViewer.prototype.need_update = function () {
    if (this.update_needed == null) {
        this.update_needed = setTimeout(callback(this, 'updateImage'), this.update_delay_ms);
    }
};

ImgViewer.prototype.load = function (uri){
    BQFactory.load (uri, callback(this, 'newImage'));
};


ImgViewer.prototype.newImage = function (bqimage) {
    if (! (bqimage instanceof BQImage) ) {
        throw BQOperationError;
    }
    this.image = bqimage;
    this.imageuri = bqimage.uri;
    this.imagesrc  = this.image.src;

    var phys = new BQImagePhys (this.image);
    phys.load (callback (this, 'newPhys') );

    BQ.Preferences.on('update_'+this.image.resource_uniq+'_pref', this.onPreferences, this);
    BQ.Preferences.on('onerror_'+this.image.resource_uniq+'_pref', this.onPreferences, this);
    BQ.Preferences.load(this.image.resource_uniq);

    // this probably should be run after the imagephys is acquired
    // in order to disable the use of "default" service at all!
    // here we would have to init a certain waiting widget
    //this.updateImage (); // dima
};

ImgViewer.prototype.updateView = function (view) {
    view = view || this.current_view;

    view.imagedim = this.imagedim.clone();
    view.src_args = [];

    for (var i = 0; i < this.plugins.length; i++) {
        plugin = this.plugins[i];
        plugin.updateView (view);
    }
    return view;
};

ImgViewer.prototype.image_url = function (view, auxparams) {
    view = this.updateView(view);
    return view.image_url(auxparams);
};

ImgViewer.prototype.doUpdateImage = function () {
    // Plugins use current view to calculate actual src url.
    this.update_needed = null;
    this.updateView();

    // If the image is tagged as video, skip creation of image pyramid
    if (this.image.converter === "ffmpeg") {
        return;
    }
    for (var i=0; i<this.plugins.length; i++) {
        plugin = this.plugins[i];
        plugin.updateImage ();
    }

    // the new updatePosition call
    for (i=0; i<this.plugins.length; i++) {
        plugin = this.plugins[i];
        plugin.updatePosition ();
    }
};

ImgViewer.prototype.updateImage = function () {
    this.requires_update = undefined;
    this.doUpdateImage();

    if (this.update_needed) clearTimeout(this.update_needed);
    //this.update_needed = setTimeout(callback(this, 'doUpdateImage'), this.update_delay_ms);
    this.update_needed = setTimeout(callback(this, 'doUpdateImage'), 0);

};

ImgViewer.prototype.findPlugin = function(name) {
    return this.plugins_by_name[name];
};

ImgViewer.prototype.gobjects = function() {
    return this.image.gobjects;
},

ImgViewer.prototype.loadGObjects = function(gobs) {

    if (gobs instanceof Array ) {
        this.gobjectsLoaded(gobs);
    } else if (gobs instanceof BQGObject) {
        this.gobjectsLoaded([gobs]);
    } else if (typeof gobs =='string') {
        this.start_wait({op: 'gobjects', message: 'Fetching gobjects'});
        BQFactory.request ({
            uri :  gobs,
            uri_params: { view : 'deep'},
            cache: false,
            cb: callback(this, 'gobjectsLoaded'),
            errorcb: this.parameters.onerror ? this.parameters.onerror : undefined,
        });
    } else if (!gobs) {
        this.start_wait({op: 'gobjects', message: 'Fetching gobjects'});
        this.image.load_gobjects(callback(this, 'gobjectsLoaded'));
    }
};

ImgViewer.prototype.gobjectsLoadProgress = function(gObj)
{
    if (this.renderWhileLoading)
    {
        this.visit_render.visitall(gObj, [this.current_view]);
        //this.gObjects.push(gObj);
        this.image.gobjects.push(gObj);
    }
};

ImgViewer.prototype.gobjectsLoaded = function(gobs) {
    this.show_additional_gobjects(gobs);
};

ImgViewer.prototype.show_additional_gobjects = function(gobs) {
    if (!(gobs instanceof Array))
        gobs = [gobs];
    this.image.gobjects.push.apply(this.image.gobjects, gobs);
    this.renderer.rerender(gobs, [this.current_view, true]);
};

ImgViewer.prototype.showGObjects = function(gobs) {
    if (!(gobs instanceof Array))
        gobs = [gobs];
    this.renderer.rerender(gobs, [this.current_view, true]);
};

ImgViewer.prototype.hideGObjects = function(gobs) {
    if (!(gobs instanceof Array))
        gobs = [gobs];

    //gobs.forEach();
    this.renderer.unselectCurrent();
    this.renderer.rerender(gobs, [this.current_view, false]);
};

ImgViewer.prototype.rerender = function() {
    this.renderer.rerender();
};

ImgViewer.prototype.setGobProjection = function(projection) {
    this.current_view.gob_projection = projection;
    this.renderer.rerender();
};

ImgViewer.prototype.setGobTolerance = function(tolerance) {
    this.current_view.gob_tolerance = tolerance;
    this.renderer.rerender();
};

ImgViewer.prototype.getGobTolerance = function() {
    return this.current_view.gob_tolerance;
};

ImgViewer.prototype.highlight_gobject = function(gob, selection) {
    // reposition the image to expose the object
    if (selection) {
        // 3D position
        //if(this.tiles.cur_z != gob.vertices[0].z)
        this.slicer.ensureVisible(gob);
        // 2D position
        //if(this.tiles.cur_z != gob.vertices[0].z)
        this.tiles.ensureVisible(gob);

        this.editor.display_gob_info(gob);
    }
    if (!gob || !gob.vertices[0]) return;
    if(this.tiles.cur_z != gob.vertices[0].z)
        this.doUpdateImage();

    // highlight the selected object
    this.renderer.highlight(gob, selection);
};

ImgViewer.prototype.select_plane = function(z, t) {
    this.slicer.setPosition(z, t);
    if (this.tiles.cur_z != z || this.tiles.cur_t != t)
        this.doUpdateImage();
};

/*
ImgViewer.prototype.color_gobject = function(gob, color) {
    this.renderer.setcolor(gob, color);
    var xml = gob.xmlNode();
    var tagColor = BQ.util.xpath_nodes(xml,'tag[@name="color"]');
    var uri = null;
    if(tagColor.length > 0){
        uri = tagColor[0].getAttribute('uri');
    }

    var t = gob.addtag(new BQTag(uri, 'color', color, 'color'));
    t.save_reload(gob.uri);
    this.renderer.rerender([gob], [this.current_view, true]);
    console.log(gob.uri + '?view=deep');
};
*/
ImgViewer.prototype.delete_gobjects = function(gobs) {
    var g=undefined;

    for (var i=0; (g=gobs[i]); i++)
        this.editor.remove_gobject(g);
};

ImgViewer.prototype.set_parent_gobject = function(gob) {
    this.editor.global_parent = gob;
    // dima: if gob is a leaf node, move over to root (or its parent???)
    if (gob && gob.isPrimitive()) {
        if (gob.parent instanceof BQGObject)
            this.editor.global_parent = gob.parent;
        else
        this.editor.global_parent = undefined;
    }
};

ImgViewer.prototype.start_wait = function (o) {
    var p = this.plugins_by_name.progressbar;
    if (!p) {
      document.body.style.cursor= "wait";
    } else {
      p.start(o);
    }
};

ImgViewer.prototype.end_wait = function (o) {
    var p = this.plugins_by_name.progressbar;
    if (!p) {
      document.body.style.cursor= "default";
    } else {
      p.end(o);
    }
};


ImgViewer.prototype.newPhys = function (phys) {
    if (this.parameters.onloaded) this.parameters.onloaded();

    this.imagephys = phys;
    this.imagedim = new ImageDim (phys.x, phys.y, phys.z, phys.t, phys.ch);

    if (phys.z<3)
        this.current_view = new Viewstate(imgview_min_width, imgview_min_width, 0, 0, 1.0);
    else
        this.current_view = new Viewstate(imgview_min_width, imgview_min_width, Math.floor((phys.z-1)/2), 0, 1.0);
    this.current_view.imagesrc = this.imagesrc;
    this.current_view.imagedim = this.imagedim.clone();

    var resource_uniq = this.image.resource_uniq;
    this.current_view.gob_tolerance.z = BQ.Preferences.get(resource_uniq, 'GraphicalAnnotations/Projections/visible_plane_tolerance_z', 1.0);
    this.current_view.gob_tolerance.t = BQ.Preferences.get(resource_uniq, 'GraphicalAnnotations/Projections/visible_plane_tolerance_t', 1.0);

    if (this.parameters.onphys) this.parameters.onphys();

    for (var i = 0; i < this.plugins.length; i++) {
        plugin = this.plugins[i];
        plugin.newImage ();
    }

    //this.updateImage();
    if (this.preferences)
        this.updateImage();
    else
        this.requires_update = true;

    // Load gobjects from string and return
    if ('gobjects_xml' in this.parameters) {
        var gobjects_xml = this.parameters['gobjects_xml'];
        var gobjects = BQFactory.parseBQDocument (gobjects_xml);
        this.loadGObjects(gobjects);
    } else if ('gobjects' in this.parameters){
        var gobjects_url = this.parameters['gobjects'];
        this.loadGObjects(gobjects_url);
    }

    this.renderer.rerender(this.image.gobjects, [this.current_view, true]);
    if (this.parameters.afterphys) this.parameters.afterphys();
};

ImgViewer.prototype.is_geo_enabeled = function() {
    var phys = this.imagephys;
    if (this.disable_geo) return false;
    if (!phys || !phys.geo) return false;
    if (phys.geo.center) return true;
    return (phys.geo.proj4 && phys.geo.res && phys.geo.top_left);
};

ImgViewer.prototype.print_coordinate = function(pt, show_pix, show_phys) {
    var phys = this.imagephys,
        text = '',
        sep = '&nbsp;',
        ip = this.plugins_by_name['infobar'];

    // print image coordinates
    if (show_pix) {
        text += '('+BQ.util.formatFloat(pt.x, 6, 2, sep)+','+BQ.util.formatFloat(pt.y, 6, 2, sep)+')px';
    }

    if (!show_phys) {
        return text;
    }

    // print physical coordinates
    if (phys.pixel_size[0]>0 && phys.pixel_size[1]>0 && !phys.coordinates) {
        var c = phys.coordinate_to_phys(pt, false);
        text += ' ('+BQ.util.formatFloat(c[0], 6, 2, sep)+','+BQ.util.formatFloat(c[1], 6, 2, sep)+')'+phys.units;
    }

    // print transformed coordinates if available
    if (phys.coordinates && phys.coordinates.top_left) {
        var c = phys.coordinate_to_phys(pt, true);
        if (c) {
            text += ' Slide:';
            if (c.length>3)
                text += ' ('+BQ.util.formatFloat(c[2], 7, 2, sep)+','+BQ.util.formatFloat(c[3], 7, 2, sep)+')px';
            text += ' ('+BQ.util.formatFloat(c[0], 7, 2, sep)+','+BQ.util.formatFloat(c[1], 7, 2, sep)+')'+phys.units;
        }
    }

    // print geo coordinates if available
    if (this.is_geo_enabeled() && phys.geo.proj4 && phys.geo.res && phys.geo.top_left) {
        var c = phys.coordinate_to_phys(pt, true);
        if (c)
            text += ' Geo:('+BQ.util.formatFloat(c[0], 4, 6, sep)+','+BQ.util.formatFloat(c[1], 4, 6, sep)+')';
    }

    ip.posbar.innerHTML = text;
};

//----------------------------------------------------------------------
// viewer preferences
//----------------------------------------------------------------------

ImgViewer.prototype.onPreferences = function() {
    var resource_uniq = this.image.resource_uniq;
    this.disable_geo = BQ.Preferences.get(resource_uniq, 'Viewer/disable_geographical_extensions', false);
    if (this.current_view) {
        this.current_view.gob_tolerance.z = BQ.Preferences.get(resource_uniq, 'GraphicalAnnotations/Projections/visible_plane_tolerance_z', 1.0);
        this.current_view.gob_tolerance.t = BQ.Preferences.get(resource_uniq, 'GraphicalAnnotations/Projections/visible_plane_tolerance_t', 1.0);
    }
    if (!('semantic_types' in this.parameters)) {
        var require = BQ.Preferences.get(resource_uniq, 'GraphicalAnnotations/require_semantic_types', false);
        if (require)
            this.parameters.semantic_types = 'require';
    }

    this.preferences = this.parameters || {}; // local defines overwrite preferences
    for (var i = 0; i < this.plugins.length; i++) {
        plugin = this.plugins[i];
        plugin.onPreferences();
    }
    if (this.requires_update) {
        this.updateImage();
        //this.updateView();
    }
};

//----------------------------------------------------------------------
// view menu
//----------------------------------------------------------------------

ImgViewer.prototype.createCombo = function (label, items, def, scope, cb, min_width) {
    var options = Ext.create('Ext.data.Store', {
        fields: ['value', 'text'],
        data : items
    });
    var combo = this.menu_view.add({
        xtype: 'combobox',
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
            'select': cb,
        },
    });
    return combo;
};

ImgViewer.prototype.createViewMenu = function() {
    if (this.menu_view)
        return this.menu_view;
    var m = Ext.create('BQ.viewer.ViewMenu', {
        renderTo: this.viewer_controls_surface || this.imagediv,
        widget: this.widget,
    });
    this.menu_view = m.menu;
    return this.menu_view;

    /*
    if (!this.menubutton) {
        this.menubutton = document.createElement('span');

        // temp fix to work similar to panojs3, will be updated to media queries
        if (isClientTouch())
            this.menubutton.className = 'viewoptions viewoptions-touch';
        else if (isClientPhone())
            this.menubutton.className = 'viewoptions viewoptions-phone';
        else
            this.menubutton.className = 'viewoptions';
    }

    if (!this.menu_view) {
        this.menu_view = Ext.create('Ext.tip.ToolTip', {
            target: this.menubutton,
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
        var el = Ext.get(this.menubutton);
        el.on('click', this.onMenuClick, this);
    }
    return this.menu_view;
    */
};

/*
ImgViewer.prototype.onMenuClick = function (e, btn) {
    e.preventDefault();
    e.stopPropagation();
    if (this.menu_view.isVisible())
        this.menu_view.hide();
    else
        this.menu_view.show();
};
*/

////////////////////////////////////////////////
// Simple  renderer for testing

function SimpleImgRenderer (viewer,name){
    this.base = ViewerPlugin;
    this.base (viewer, name);
};
SimpleImgRenderer.prototype = new ViewerPlugin();
SimpleImgRenderer.prototype.create = function (parent) {
    this.image = document.createElementNS(xhtmlns, "img");
    parent.appendChild(this.image);
    return this.image;
};

SimpleImgRenderer.prototype.updateImage = function () {
    var src = this.viewer.image_url();
    this.image.setAttributeNS(null, "src",   src);
};
