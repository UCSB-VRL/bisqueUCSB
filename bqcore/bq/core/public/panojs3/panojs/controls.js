/*******************************************************************************
  Controls - creates buttons for zooming and, full screen

  GSV 3.0 : PanoJS3
  @author Dmitry Fedorov  <fedorov@ece.ucsb.edu>

  Copyright (c) 2010 Dmitry Fedorov, Center for Bio-Image Informatics

  using: isClientTouch() and isClientPhone() from utils.js

*******************************************************************************/

PanoJS.CONTROL_ZOOMIN = {
    className : "control zoomIn",
    title : "Zoom in",
    id: 'zoomIn'
};

PanoJS.CONTROL_ZOOM11 = {
    className : "control zoom11",
    title : "Zoom 1:1",
    id: 'zoom11'
};

PanoJS.CONTROL_ZOOMOUT = {
    className : "control zoomOut",
    title : "Zoom out",
    id: 'zoomOut'
};

PanoJS.CONTROL_MAXIMIZE = {
    className : "control maximize",
    title : "Maximize",
    id: 'maximize'
};

function PanoControls(viewer) {
    this.viewer = viewer;
    this.initControls();
    this.createDOMElements();
}

PanoControls.prototype.initControls = function() {
};

PanoControls.prototype.createDOMElements = function() {
    this.dom_element = this.viewer.viewerDomElement();

    this.createButton (PanoJS.CONTROL_ZOOMIN);
    this.createButton (PanoJS.CONTROL_ZOOM11);
    this.createButton (PanoJS.CONTROL_ZOOMOUT);
    this.createButton (PanoJS.CONTROL_MAXIMIZE);
};

PanoControls.prototype.createButton = function(control) {
    var btn = document.createElement('span');
    btn.className = control.className;
    this.dom_element.appendChild(btn);

    btn.onclick = callback(this.viewer, this.viewer[control.id + 'Handler']);
    btn.addEventListener("touchstart", callback(this.viewer, this.viewer[control.id + 'Handler']));

    return btn;
};
