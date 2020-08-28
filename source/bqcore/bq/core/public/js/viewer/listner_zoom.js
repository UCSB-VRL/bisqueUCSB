/*******************************************************************************
  Zoom listner - listens to the viewer and updates view states
  
  GSV 3.0 : PanoJS3
  @author Dmitry Fedorov  <fedorov@ece.ucsb.edu>   
  
  Copyright (c) 2010 Dmitry Fedorov, Center for Bio-Image Informatics

*******************************************************************************/

function ZoomListner(viewerTiled, viewer5d) {
  this.viewerTiled = viewerTiled;  
  this.viewer5d = viewer5d      

  this.viewerTiled.addViewerZoomedListener(this);    
}

ZoomListner.prototype.viewerZoomed = function(e) {
  if (e.scale == this.viewer5d.current_view.scale) return;
  this.viewer5d.current_view.scaleTo (e.scale);
  this.viewer5d.need_update(); 
}
