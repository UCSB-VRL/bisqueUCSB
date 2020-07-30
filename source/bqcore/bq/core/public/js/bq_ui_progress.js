/******************************************************************************
  BQProgressBar
  parent - div where to show progress, if null the full window is used
  title - string showing the process description
  parames - parameters dictionary:
              'delay' - do not start on creation 
******************************************************************************/

function BQProgressBar( parent, title, params ) {
  if (typeof parent == 'string')
    this.parent = document.getElementById(parent);
  else
    this.parent = parent;
  this.title = title;
  this.params = params;
  if (params && 'delay' in params) return;
  this.start();  
}

BQProgressBar.prototype.stop = function () {
  if (this.timeout) clearTimeout(this.timeout);
  if (this.stop_spinning) this.stop_spinning();  
  if (this.modal) { document.body.removeChild(this.surface); }
  if (this.mysurf) { this.parent.removeChild(this.surface); }  
}

BQProgressBar.prototype.start = function () {
   // this will allow skippig showing progress alltogether for fast operations
   this.timeout = setTimeout(callback(this, 'dostart'), 250);
}

BQProgressBar.prototype.dostart = function () {
  this.stop(); 
  this.surface = this.parent;  
  if (this.parent && this.params && 'float' in this.params) {
    this.mysurf = true;
    this.surface = document.createElement('div');
    this.surface.className = 'xmask';
    this.surface.style.position = 'absolute';
    this.surface.style.zIndex   = '14999';
    this.surface.style.left     = this.parent.offsetLeft+'px';
    this.surface.style.top      = this.parent.offsetTop+'px';
    this.surface.style.width    = this.parent.offsetWidth+'px';
    this.surface.style.height   = this.parent.offsetHeight+'px';
    this.surface.style.float    = 'left';
    this.parent.appendChild(this.surface);     
  }      
  
  if (!this.surface) {
    this.modal = true;
    this.surface = document.createElement('div');
    this.surface.className = 'xmask';
    this.surface.style.position = 'fixed';
    this.surface.style.zIndex   = '14999';
    this.surface.style.left     = '0px';
    this.surface.style.top      = '0px';
    this.surface.style.width    = '100%';
    this.surface.style.height   = '100%'; 
    document.body.appendChild(this.surface);     
  }

  this.stop_spinning = this.spinner(this.surface, 13, 20, 12, 4, "#fff");
}

BQProgressBar.prototype.spinner = function (holderid, R1, R2, count, stroke_width, colour) {
    var sectorsCount = count || 12,
        color = colour || "#fff",
        width = stroke_width || 15,
        r1 = Math.min(R1, R2) || 35,
        r2 = Math.max(R1, R2) || 60,
        cx = r2 + width,
        cy = r2 + width,
        sectors = [],
        opacity = [],
        beta = 2 * Math.PI / sectorsCount,
        pathParams = {stroke: color, "stroke-width": width, "stroke-linecap": "round"};
        
    //r = Raphael(holderid, r2 * 2 + width * 2, r2 * 2 + width * 2),
    var r = Raphael(holderid, "100%", "100%");
    this.r = r;
    Raphael.getColor.reset();
        
    var bckg = r.rect(0, 0, '100%', '100%', 5);
    bckg.attr({fill: "#000", opacity: 0.6});
    var ox = this.surface.offsetWidth/2 - (r2 + width);
    var oy = this.surface.offsetHeight/2 - (r2 + width);
        
    if (this.title)
        this.t = r.text(ox+(r2 + width), oy+3*(r2 + width), this.title).attr(
            {font: '100 12px "Helvetica Neue", Helvetica, "Arial Unicode MS", Arial, sans-serif', fill: "#fff"});
    for (var i = 0; i < sectorsCount; i++) {
        var alpha = beta * i - Math.PI / 2,
            cos = Math.cos(alpha),
            sin = Math.sin(alpha);
        opacity[i] = 1 / sectorsCount * i;
        sectors[i] = r.path([["M", cx + r1 * cos + ox, cy + r1 * sin + oy], ["L", cx + r2 * cos + ox, cy + r2 * sin + oy]]).attr(pathParams);
        if (color == "rainbow") {
            sectors[i].attr("stroke", Raphael.getColor());
        }
    }
    var tick;
    (function ticker() {
        opacity.unshift(opacity.pop());
        for (var i = 0; i < sectorsCount; i++) {
            sectors[i].attr("opacity", opacity[i]);
        }
        r.safari();
        tick = setTimeout(ticker, 1000 / sectorsCount);
    })();
    return function () {
        clearTimeout(tick);
        r.remove();
    };
}

