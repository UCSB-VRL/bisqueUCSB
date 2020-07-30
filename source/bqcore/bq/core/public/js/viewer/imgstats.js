//  Img Viewer plugin for dealing with GOBjects statistics
//
function ImgStatistics (viewer,name){
    this.base = ViewerPlugin;
    this.base (viewer, name);
    this.menu = null;
    this.menu_elements = {};
    this.viewer.addCommand ('Statistics', callback (this, 'toggleMenu'));
    this.gobjects = null;
}
ImgStatistics.prototype = new ViewerPlugin();

ImgStatistics.prototype.create = function (parent) {
    this.parent = parent;
    return parent;
}
ImgStatistics.prototype.newImage = function () {
    //this.gobjects = new Array(0);
    ///this.viewer.image.load_gobjects(callback(this,'on_gobject_load'));
}
ImgStatistics.prototype.on_gobject_load = function (g) {
    //g.visitall ('render', [ this.viewer.current_view, this.viewer.renderer ]);
    //this.gobjects.push(g);
}
ImgStatistics.prototype.updateImage = function () {
}
ImgStatistics.prototype.toggleMenu = function () {
    if (this.menu == null) {
        this.menu = document.createElementNS(xhtmlns, "div");
        this.menu.className = "imgview_statsdiv";
        this.menu.style.display = "none";
        this.parent.appendChild(this.menu);
        this.gobjects = this.viewer.gobjects();
    } 

    this.viewer.active_submenu(this.menu);

    if (this.menu.style.display  == "none" ) {
        if (this.gobjects == null || this.gobjects.length == 0) {
            alert ("This image has no graphical annotations");
            return;
        }
        this.generate ();
        this.menu.style.display = "";
    }else
        this.menu.style.display = "none";
}
ImgStatistics.prototype.generate = function () {
    var gobjects = this.gobjects;
    var visit = new StatsVisitor();
    removeAllChildren(this.menu);
    visit.visit_special_array(gobjects);
    for ( ty in visit.groups ) {
        var stats = visit.groups[ty];
        var gobdiv = document.createElementNS(xhtmlns, "div");
        gobdiv.className = "imgview_stats_el";
        gobdiv.innerHTML = stats.toHTML();
        this.menu.appendChild (gobdiv);
    }
    var gobdiv = document.createElementNS(xhtmlns, "div");
    gobdiv.className = "imgview_stats_el";
    gobdiv.innerHTML = visit.stats.toHTML();
    this.menu.appendChild (gobdiv);
    
}
///////////////////////////////////////////////////////////////////////////
// Stats accumulator for a complex gobject or unassociated simple gobjects.
function Stats (nm, ty) {
    this.name = nm;
    this.type = ty;
    this.gobs = {};
}
Stats.prototype.add_gobject = function (gobty, stats) {
    if (! (gobty in this.gobs)) this.gobs[gobty] = new Array();
    this.gobs[gobty].push (stats);
}
Stats.prototype.avg = function (gobty, f) {
    var a = this.gobs[gobty];
    var s=0;
    if (a.length>0){
        for (var i=0; i < a.length; i++)
            s += a[i][f];
        s = s/a.length;
    }
    return s;
}                                

Stats.prototype.toHTML = function () {
    var HTML = "statistics for " + this.type +"<br/>";
    for (ty in this.gobs) {
        var a = this.gobs[ty];
        var count = a.length;
        var avgarea = this.avg(ty, 'area');
        var avgperim = this.avg(ty, 'perimeter');
        HTML += "statistics for " + ty +"<br/>";
//         for (var i=0; i < a.length; i++){
//        HTML += (" " + i + " area="+a[i]['area'].toFixed(2) 
//                 + " perimeter=" + a[i]['perimeter'].toFixed(2) + "<br/>");
//         }
        HTML += " average count="+count+" area="+avgarea.toFixed(2) + " perimeter=" + avgperim.toFixed(2)+"<br/>";
    }
    return HTML;
}

////////////////////////////////////////////////
// A visitor for collecting gobject statistics.
function StatsVisitor  () {
    // A table index by the type of the gobject with 
    //  Area, perimeter and 
    this.base = BQClassVisitor;
    this.base ();

    // Top level Complex gobjects (Structures) 
    this.groups = {};
    //  Current stats accumulator (initialy non complex objects)
    this.stats = new Stats('', 'simple types'); 
    this.parent_stats = new Array();
}
StatsVisitor.prototype = new BQClassVisitor ();
StatsVisitor.prototype.default_visit = function (gob) {
    if (this.state == this.START){
        var stats = this.groups[gob.type];
        if (stats == null) {
            stats = new Stats (gob.name, gob.type);
            this.groups[gob.type] = stats;
        }
        
        this.parent_stats.push(this.stats);
        this.stats = stats;
    }
    else if (this.state == this.FINISH){
        var stats= this.parent_stats.pop();
        this.stats = stats
    }
}

StatsVisitor.prototype.point = function (gob, view) {
    this.stats.add_gobject ('point', { area: 0, perimeter:0 });
}
StatsVisitor.prototype.rectangle = function (gob, view) {
    //clog('rectangle');
    var p1x = gob.vertices[0].x;
    var p1y = gob.vertices[0].y;
    var p2x = gob.vertices[1].x;
    var p2y = gob.vertices[1].y;
	 
    var centroidX = Math.abs(p1x - p2x)/2;
    var centroidY = Math.abs(p1y - p2y)/2;
	
    //calculate the perimiter
    var width = Math.abs(p1x - p2x);
    var height = Math.abs(p1y - p2y);
    var perimeter = (2 *(Math.abs(p1x -p2x)))  + (2 *(Math.abs(p1y - p2y)));
    var area = ((Math.abs(p1x - p2x)))  * ((Math.abs(p1y - p2y)));
    this.stats.add_gobject ('rectangle', { area: area, perimeter: perimeter });
}
StatsVisitor.prototype.polygon = function (gob, view) {
    //clog('polygon');
    var l = gob.vertices.length;
    var area =0;
    var perimeter = 0;
    for (var i=0; i < l; i++){
        var p1 = gob.vertices[i];
        var p2 = gob.vertices[(i+1)%l];

        area += p1.x*p2.y + p2.x*p1.y;
        perimeter += Math.sqrt(Math.abs(p1.x-p2.x)*Math.abs(p1.x-p2.x)
                               +Math.abs(p1.y-p2.y)*Math.abs(p1.y-p2.y));
    }
    this.stats.add_gobject ('polygon', { area: area/2, perimeter: perimeter });
}
StatsVisitor.prototype.polyline = function (gob) {
    //clog('polyline');
    var l = gob.vertices.length;
    var area =0;
    var perimeter = 0;
    for (var i=0; i < l-1; i++){
        var p1 = gob.vertices[i];
        var p2 = gob.vertices[(i+1)];

        area += p1.x*p2.y + p2.x*p1.y;
        perimeter += Math.sqrt(Math.abs(p1.x-p2.x)*Math.abs(p1.x-p2.x)
                               +Math.abs(p1.y-p2.y)*Math.abs(p1.y-p2.y));
    }
    this.stats.add_gobject ('polyline', { area:area/2, perimeter: perimeter });
}
StatsVisitor.prototype.circle = function (gob, view) {
    var cx = gob.vertices[0].x;
    var cy = gob.vertices[0].y;
    var rx = gob.vertices[1].x;
    var ry = gob.vertices[1].x;
    
    var radius = Math.sqrt(((cy-ry)*(cy-ry)) + ((cx-rx)*(cx-rx)));
    var circumference = Math.PI * radius * 2;
    var area = Math.PI * (radius*radius);
    this.stats.add_gobject ('circle', { area:area, perimeter: circumference });
}
