/*******************************************************************************
  ProgressBar - shows progress of executing actions
  
  @author Dmitry Fedorov  <fedorov@ece.ucsb.edu>   
  
  Copyright (c) 2011 Dmitry Fedorov, Center for Bio-Image Informatics

*******************************************************************************/

//ImgViewer.INFO_CONTROL_STYLE = "padding: 5px; text-shadow: 1px 1px 1px #000000; font-size: 12px;";

function ProgressBar (viewer,name){
    this.base = ViewerPlugin;
    this.base (viewer, name);
    this.bar = null;    
    this.p = null;    
    this.ops = {};    
}

ProgressBar.prototype = new ViewerPlugin();
ProgressBar.prototype.create = function (parent) {
    this.surface = parent;
    return parent;
}

ProgressBar.prototype.newImage = function () {
  // create info bar
  if (!this.bar) {
    var surf = this.surface;
    if (this.viewer.viewer_controls_surface) surf = this.viewer.viewer_controls_surface;

    this.bar = document.createElement('div');
    this.bar.className = 'progress';
    surf.appendChild(this.bar);
  }
}

ProgressBar.prototype.start = function ( o ) {
  this.ops[o.op] = o.message;
  var text = this.ops[o.op];
  this.p = new BQProgressBar( this.bar, text );  
}

ProgressBar.prototype.end = function ( o ) {
  if (o.op in this.ops) delete this.ops[o.op];
  
  var empty = true;
  for (i in this.ops) { 
    empty = false;
    break;
  }  

  if (empty && this.p) {
    this.p.stop();
    this.p = null;
  }
}

