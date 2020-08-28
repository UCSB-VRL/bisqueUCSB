
function SVGRenderer (viewer,name) {
    var p = viewer.parameters || {};
    //this.default_showOverlay           = p.rotate          || 0;   // values: 0, 270, 90, 180
    this.default_showOverlay   = false;
    this.base = ViewerPlugin;
    this.base (viewer, name);
    this.events  = {};
}
SVGRenderer.prototype = new ViewerPlugin();

SVGRenderer.prototype.create = function (parent) {
    this.overlay = document.createElementNS(svgns, "svg");
    this.overlay.setAttributeNS(null, 'class', 'gobjects_overlay');
    this.overlay.setAttributeNS(null, 'id', 'overlay');
    parent.appendChild(this.overlay);
    this.overlay.style.position = "absolute";
    this.overlay.style.top = "0px";
    this.overlay.style.left = "0px";

    this.parent = parent;
    return parent;
};

SVGRenderer.prototype.updateView = function (view) {
    if (this.initialized || !this.viewer.tiles.tiled_viewer) return;
    this.initialized = true;
    this.myListener = new SvgControl( this.viewer.tiles.tiled_viewer, this.overlay );
    this.loadPreferences(this.viewer.preferences);
    if (this.showOverlay !== 'false')
        this.populate_overlay(this.showOverlay);
};

SVGRenderer.prototype.updateImage = function () {
    var viewstate = this.viewer.current_view;
    this.overlay.setAttributeNS( null, 'width', viewstate.width);
    this.overlay.setAttributeNS( null, 'height', viewstate.height);
};

SVGRenderer.prototype.loadPreferences = function (p) {
    this.showOverlay  = 'showOverlay' in p ? p.showOverlay  : this.default_showOverlay;
};

SVGRenderer.prototype.populate_overlay = function (mode) {
    removeAllChildren (this.overlay);

    var gobs = document.createElementNS(svgns, "g");
    this.overlay.appendChild(gobs);

    if (mode === 'dots') {
        for (var x=9; x<=95; x+=9)
        for (var y=12; y<=95; y+=9) {
            var circ = document.createElementNS( svgns, 'circle');
            circ.setAttributeNS(null, 'fill-opacity', 0.0);
            circ.setAttributeNS(null, 'fill', 'black');
            circ.setAttributeNS(null, 'stroke', 'black');
            circ.setAttributeNS(null, 'stroke-width', 2);
            circ.setAttributeNS(null, 'cx', ''+x+'%' );
            circ.setAttributeNS(null, 'cy', ''+y+'%');
            circ.setAttributeNS(null, 'r', '1%' );
            gobs.appendChild(circ);

            var circ = document.createElementNS( svgns, 'circle');
            circ.setAttributeNS(null, 'fill-opacity', 0.0);
            circ.setAttributeNS(null, 'fill', 'black');
            circ.setAttributeNS(null, 'stroke', 'white');
            circ.setAttributeNS(null, 'stroke-width', 1);
            circ.setAttributeNS(null, 'cx', ''+x+'%' );
            circ.setAttributeNS(null, 'cy', ''+y+'%');
            circ.setAttributeNS(null, 'r', '1%' );
            gobs.appendChild(circ);
        }
    } else if (mode === 'dots_medium') {
        for (var x=9; x<=95; x+=9)
        for (var y=15; y<=90; y+=8) {
            var circ = document.createElementNS( svgns, 'circle');
            circ.setAttributeNS(null, 'fill-opacity', 0.0);
            circ.setAttributeNS(null, 'fill', 'black');
            circ.setAttributeNS(null, 'stroke', 'black');
            circ.setAttributeNS(null, 'stroke-width', 2);
            circ.setAttributeNS(null, 'cx', ''+x+'%' );
            circ.setAttributeNS(null, 'cy', ''+y+'%');
            circ.setAttributeNS(null, 'r', '1%' );
            gobs.appendChild(circ);

            var circ = document.createElementNS( svgns, 'circle');
            circ.setAttributeNS(null, 'fill-opacity', 0.0);
            circ.setAttributeNS(null, 'fill', 'black');
            circ.setAttributeNS(null, 'stroke', 'white');
            circ.setAttributeNS(null, 'stroke-width', 1);
            circ.setAttributeNS(null, 'cx', ''+x+'%' );
            circ.setAttributeNS(null, 'cy', ''+y+'%');
            circ.setAttributeNS(null, 'r', '1%' );
            gobs.appendChild(circ);
        }
    } else if (mode === 'dots_narrow') {
        for (var x=15; x<=90; x+=8)
        for (var y=20; y<=85; y+=7) {
            var circ = document.createElementNS( svgns, 'circle');
            circ.setAttributeNS(null, 'fill-opacity', 0.0);
            circ.setAttributeNS(null, 'fill', 'black');
            circ.setAttributeNS(null, 'stroke', 'black');
            circ.setAttributeNS(null, 'stroke-width', 2);
            circ.setAttributeNS(null, 'cx', ''+x+'%' );
            circ.setAttributeNS(null, 'cy', ''+y+'%');
            circ.setAttributeNS(null, 'r', '1%' );
            gobs.appendChild(circ);

            var circ = document.createElementNS( svgns, 'circle');
            circ.setAttributeNS(null, 'fill-opacity', 0.0);
            circ.setAttributeNS(null, 'fill', 'black');
            circ.setAttributeNS(null, 'stroke', 'white');
            circ.setAttributeNS(null, 'stroke-width', 1);
            circ.setAttributeNS(null, 'cx', ''+x+'%' );
            circ.setAttributeNS(null, 'cy', ''+y+'%');
            circ.setAttributeNS(null, 'r', '1%' );
            gobs.appendChild(circ);
        }
    } else if (mode === 'grid') {
        for (var y=12; y<=95; y+=9) {
            var circ = document.createElementNS( svgns, 'line');
            circ.setAttributeNS(null, 'fill-opacity', 0.0);
            circ.setAttributeNS(null, 'fill', 'black');
            circ.setAttributeNS(null, 'stroke', 'black');
            circ.setAttributeNS(null, 'stroke-width', 2);
            circ.setAttributeNS(null, 'x1', '0%' );
            circ.setAttributeNS(null, 'x2', '100%' );
            circ.setAttributeNS(null, 'y1', ''+y+'%');
            circ.setAttributeNS(null, 'y2', ''+y+'%');
            gobs.appendChild(circ);

            var circ = document.createElementNS( svgns, 'line');
            circ.setAttributeNS(null, 'fill-opacity', 0.0);
            circ.setAttributeNS(null, 'fill', 'black');
            circ.setAttributeNS(null, 'stroke', 'white');
            circ.setAttributeNS(null, 'stroke-width', 1);
            circ.setAttributeNS(null, 'x1', '0%' );
            circ.setAttributeNS(null, 'x2', '100%' );
            circ.setAttributeNS(null, 'y1', ''+y+'%');
            circ.setAttributeNS(null, 'y2', ''+y+'%');
            gobs.appendChild(circ);
        }
    }
};

//------------------------------------------------------------------------------------------------
// canvas test
//------------------------------------------------------------------------------------------------

function TestRenderer (viewer,name) {
    var p = viewer.parameters || {};
    this.base = ViewerPlugin;
    this.base (viewer, name);
    this.events  = {};
}
TestRenderer.prototype = new ViewerPlugin();

TestRenderer.prototype.create = function (parent) {
    this.overlay = document.createElementNS(xhtmlns, "canvas");
    this.overlay.setAttributeNS(null, 'class', 'gobjects_overlay');
    this.overlay.setAttributeNS(null, 'id', 'overlay_test');
    parent.appendChild(this.overlay);
    this.overlay.style.position = "absolute";
    this.overlay.style.top = "0px";
    this.overlay.style.left = "0px";
    this.overlay.style.width = "100%";
    this.overlay.style.height = "100%";

    this.parent = parent;
    return parent;
};

TestRenderer.prototype.newImage = function () {
    var viewstate = this.viewer.current_view;
    this.points = [];
    for (var i=0; i<10000; ++i) {
        this.points.push({
            x: Math.random()*viewstate.width,
            y: Math.random()*viewstate.height,
        });
    }
};

TestRenderer.prototype.updateView = function (view) {
    if (this.initialized) return;
    var tv = this.viewer.tiles.tiled_viewer;
    if (tv) {
        this.loadPreferences(this.viewer.preferences);
        this.initialized = true;
        tv.addViewerZoomedListener(this);
        tv.addViewerMovedListener(this);
    }
};

// begin: panojs required events

TestRenderer.prototype.viewerMoved = function(e) {
    this.x = e.x;
    this.y = e.y;
    this.redraw();
};

TestRenderer.prototype.viewerZoomed = function(e) {
    this.x = e.x;
    this.y = e.y;
};

// end: panojs required events

TestRenderer.prototype.updateImage = function () {
    this.overlay.width  = this.overlay.clientWidth || this.overlay.innerWidth;
    this.overlay.height = this.overlay.clientHeight || this.overlay.innerHeight;
    this.redraw();
};

TestRenderer.prototype.redraw = function () {
    if (!this.points) return;
    var viewstate = this.viewer.current_view;
    var context = this.overlay.getContext('2d');
    context.clearRect(0, 0, this.overlay.width, this.overlay.height);

    var x = this.x || 0;
    var y = this.y || 0;
    var scale = viewstate.scale || 1.0;

    var color = "#FFFF00";//'rgb(' + Math.round(Math.random()*255)+',' + Math.round(Math.random()*255)+','+ Math.round(Math.random()*255)+')'
    var radius = 6; //Math.round(10 * Math.random());

    var p = undefined;
    for (var i=0; (p=this.points[i]); ++i) {
        //var radius = Math.round(10 * Math.random());
        //var color = 'rgb(' + Math.round(Math.random()*255)+',' + Math.round(Math.random()*255)+','+ Math.round(Math.random()*255)+')'
        context.beginPath();
        context.arc(p.x*scale+x, p.y*scale+y, radius, 0, 2 * Math.PI, false);
        context.fillStyle = color;
        context.fill();
        //context.lineWidth = 5;
        //context.strokeStyle = 'rgb(' + Math.random()*255+',' + Math.random()*255+','+ Math.random()*255+')';
        context.stroke();
    }
};

TestRenderer.prototype.loadPreferences = function (p) {
    //this.showOverlay  = 'showOverlay' in p ? p.showOverlay  : this.default_showOverlay;
};

