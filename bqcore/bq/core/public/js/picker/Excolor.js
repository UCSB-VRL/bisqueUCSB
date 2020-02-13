/*******************************************************************************

@author John Delaney


 *******************************************************************************/

/*
LICENSE

Center for Bio-Image Informatics, University of California at Santa Barbara

Copyright (c) 2007-2014 by the Regents of the University of California
All rights reserved

Redistribution and use in source and binary forms, in whole or in parts, with or without
modification, are permitted provided that the following conditions are met:

Redistributions of source code must retain the above copyright
notice, this list of conditions, and the following disclaimer.

Redistributions in binary form must reproduce the above copyright
notice, this list of conditions, and the following disclaimer in
the documentation and/or other materials provided with the
distribution.

Use or redistribution must display the attribution with the logo
or project name and the project URL link in a location commonly
visible by the end users, unless specifically permitted by the
license holders.

THIS SOFTWARE IS PROVIDED BY THE REGENTS OF THE UNIVERSITY OF CALIFORNIA ''AS IS'' AND ANY
EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE REGENTS OF THE UNIVERSITY OF CALIFORNIA OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */


// dima: polyfill for chrome>48
SVGElement.prototype.getTransformToElement = SVGElement.prototype.getTransformToElement || function(elem) {
    return elem.getScreenCTM().inverse().multiply(this.getScreenCTM());
};

Ext.define('BQ.viewer.Volume.fieldSlider', {
  extend : 'Ext.Component',
  alias : 'widget.field-slider',
  getStop : function (stop) {
    var color = stop.color;
    var offset = stop.offset;
    svgStop = '<stop offset="' + offset +
      '%" stop-color="rgba(' +
      color[0] + ', ' +
      color[1] + ', ' +
      color[2] + ', ' +
      color[3] + ')"/>\n';
    return svgStop;
  },

  genGradient : function (config, stops) {

    var orient;
    if (config.vertical)
      orient = 'x1="0%" y1="0%" x2="0%" y2="100%"\n';
    else
      orient = '';

    var grad = '<defs> <linearGradient id="' + config.id + '">\n';
    var grad = ['<defs>',
      '<linearGradient id="' + config.id + '" ',
      orient,
      'gradientTransform="rotate(' + config.angle + ')">\n'
    ].join(' ');
    for (var i = 0; i < stops.length; i++) {
      grad += this.getStop(stops[i]);
    }
    grad += '</linearGradient> </defs>';
    return grad;
  },

  getPolar : function (x, y) {

    var dx = x - this.wheelCenter[0];
    var dy = y - this.wheelCenter[1];
    var rxy = dx * dx + dy * dy;
    var phi = Math.atan2(dx, dy);
    //return r^2, since square roots are slow.  probably won't matter, but on principle.
    return [phi, rxy]
  },

  setWheelRadius : function (canvas) {
    var width = canvas.width;
    var height = canvas.height;
    var cen = [width / 2, height / 2];
    var margin = 4;
    var r = width < height ? width / 2 : height / 2;
    r -= margin;
    this.wheelRadius = r;
    this.wheelCenter = cen;
  },

  initialized : function(){
    return(wheelRadius || wheelCenter);
  },

  getRgbWheel : function (x, y) {

    var r = this.wheelRadius;
    var cen = this.wheelCenter;
    var polar = this.getPolar(x, y);
    var phi = polar[0];
    var rxy = polar[1];

    //phi = 3 * phi / Math.PI + 3;
      var s = Math.sqrt(rxy / (r * r));
      var h = 180*phi/Math.PI + 179.99999;
      var v = 1.0;
      col = this.HSVtoRGB(h, s, v);

      var col1 = [];
      col1[0] = Math.floor(255*col.r);
      col1[1] = Math.floor(255*col.g);
      col1[2] = Math.floor(255*col.b);
      col1[3] = 255;

      return col1;
/*
    if (rxy < r * r) {
      var s = Math.sqrt(rxy / (r * r));
      var h = 180*phi/Math.PI + 179.99999;
      var v = 1.0;
      col = this.HSVtoRGB(h, s, v);

      var col1 = [];
      col1[0] = Math.floor(255*col.r);
      col1[1] = Math.floor(255*col.g);
      col1[2] = Math.floor(255*col.b);
      col1[3] = 255;

      return col1;
    } else {
      return [0, 0, 0, 0];
    }
*/
  },

    generateColorWheel : function () {

        var canvas = document.getElementById('wheel-canvas');
        var context = canvas.getContext("2d");
        var c=document.getElementById("myCanvas");
        var r = this.wheelRadius;
        var cen = this.wheelCenter;
        //draw a circle to create a mask, so the graphics processor
        //handles antialiasing
        context.fillStyle = "RGBA(255,255,255,1)";
        context.beginPath();
        context.arc(cen[0],cen[1],r,0,2*Math.PI);
        context.fill();
        var width = canvas.width;
        var height = canvas.height;
        var imageData = context.getImageData(0, 0, width, height);

        for (var x = 0; x < width; x++) {
            for (var y = 0; y < height; y++) {
                var i = x + y * width;
                var col = this.getRgbWheel(x, y, canvas);
                //replace colors with computed HSL
                imageData.data[4 * i + 0] = col[0];
                imageData.data[4 * i + 1] = col[1];
                imageData.data[4 * i + 2] = col[2];
                //imageData.data[4 * i + 3] = a; // leave the alpha channel alone

            }

        }

        context.putImageData(imageData, 0, 0);

    },

  generateHsv : function () {
    var grad1 = this.genGradient({
        id : 'HSV',
        angle : 0,
        vertical : false
      },
        [{
            offset : 0,
            color : [255, 0, 0, 1.0]
          }, {
            offset : Math.floor(60 / 360 * 100),
            color : [255, 255, 0, 1.0]
          }, {
            offset : Math.floor(120 / 360 * 100),
            color : [0, 255, 0, 1.0]
          }, {
            offset : Math.floor(180 / 360 * 100),
            color : [0, 255, 255, 1.0]
          }, {
            offset : Math.floor(240 / 360 * 100),
            color : [0, 0, 255, 1.0]
          }, //blue
          {
            offset : Math.floor(300 / 360 * 100),
            color : [255, 0, 255, 1.0]
          }, //magenta
          {
            offset : Math.floor(360 / 360 * 100),
            color : [255, 0, 0, 1.0]
          }, //red
        ]);

    var grad2 = this.genGradient({
        id : 'overlay',
        angle : 0,
        vertical : true
      },
        [{
            offset : 0,
            color : [255, 255, 255, 0.0]
          }, {
            offset : 100,
            color : [255, 255, 255, 1.0]
          },
        ]);

    var rect = ['<rect id="rect1"',
      'x="0" y="0"',
      'rx="0" ry="0"',
      'width="100%"',
      'height="100%"',
      'fill="url(#HSV)"',
      '/>'].join(' ');

    var rectOverlay = ['<rect id="rect2"',
      'x="0" y="0"',
      'rx="0" ry="0"',
      'width="100%"',
      'height="100%"',
      'fill="url(#overlay)"',
      '/>'].join(' ');

    var svg = [' <svg width=100% height=100% >',
      grad1,
      grad2,
      rect,
      rectOverlay,
      '</svg>'].join('\n');

    this.svgField.innerHTML = svg;
  },

  afterRender : function () {
    this.callParent();

    var canvas = document.createElement("canvas");
    canvas.setAttribute('class', 'color-field');
    canvas.setAttribute('id', 'wheel-canvas');
    this.el.dom.appendChild(canvas);

    this.svgUrl = "http://www.w3.org/2000/svg";
    this.svgdoc = document.createElementNS(this.svgUrl, "svg");
    this.svgdoc.setAttributeNS(null, 'class', 'color-field');

    this.el.dom.appendChild(this.svgdoc);
    this.svgField = document.createElementNS(this.svgUrl, "g");
    this.svgField.setAttributeNS(null, 'class', 'color-field');
    this.svgdoc.appendChild(this.svgField);

    //this.svgdoc.appendChild(this.svgField);


    //this.generateHsv();


      this.rect = document.createElementNS(this.svgUrl, "rect");
      this.rect.setAttributeNS(null, 'class', 'color_chooser');
    this.rect.setAttributeNS(null, 'width', '100%');
    this.rect.setAttributeNS(null, 'height', '100%');
    this.rect.setAttributeNS(null, 'opacity', '0.0');
    this.svgdoc.appendChild(this.rect);

    this.dot = document.createElementNS(this.svgUrl, "circle");
      this.dot.setAttributeNS(null, 'class', 'color_chooser');
    this.dot.setAttributeNS(null, 'cx', '40');
    this.dot.setAttributeNS(null, 'cy', '20');
    this.dot.setAttributeNS(null, 'r', '5');
    this.dot.setAttributeNS(null, 'fill', 'rgba(0,0,0,0.5)');
    this.dot.setAttributeNS(null, 'stroke', 'black');
    this.dot.setAttributeNS(null, 'stroke-width', '2');
    this.svgdoc.appendChild(this.dot);


    var me = this;
    var cursorPoint = function (evt) {
      pt.x = evt.clientX;
      pt.y = evt.clientY;
      return pt.matrixTransform(me.svgdoc.getScreenCTM().inverse());
    }

    var offsetPoint = function (evt) {
      pt.x = evt.offsetX;
      pt.y = evt.offsetY;
      //return pt.matrixTransform(me.svgdoc.getScreenCTM().inverse());
      return pt;
    }

    var onMove;
    var pt = this.svgdoc.createSVGPoint();

    this.rect.addEventListener('mousedown', function (e) {
      var el = me.dot;
      var x = 'cx';
      var y = 'cy';
      //debugger;
      var elementStart = {
        x : el[x].animVal.value,
        y : el[y].animVal.value
      };
      var current = offsetPoint(e);
      pt.x = current.x;
      pt.y = current.y;

        var phi = me.getPolar(current.x, current.y);
        var r = me.wheelRadius;

        if (phi[1] >= r * r)
            return;
      var m = el.getTransformToElement(me.svgdoc).inverse();
      m.e = m.f = 0;
      pt = pt.matrixTransform(m);
      el.setAttribute(x, pt.x);
      el.setAttribute(y, pt.y);
      me.fireEvent('change', me);

    }, false);
/*
    this.dot.addEventListener('mousedown', function (e) {
      var el = me.dot;
      var x = 'cx';
      var y = 'cy';
      var mouseStart = cursorPoint(e);
      var elementStart = {
        x : el[x].animVal.value,
        y : el[y].animVal.value
      };
      onMove = function (e) {
        var current = cursorPoint(e);
        pt.x = current.x - mouseStart.x;
        pt.y = current.y - mouseStart.y;
        var phi = me.getPolar(current.x, current.y);
        var r = me.wheelRadius;

        if (phi[1] >= r * r)
          return;
        var m = el.getTransformToElement(me.svgdoc).inverse();
        m.e = m.f = 0;
        pt = pt.matrixTransform(m);
        el.setAttribute(x, elementStart.x + pt.x);
        el.setAttribute(y, elementStart.y + pt.y);
        var dragEvent = document.createEvent("Event");
        dragEvent.initEvent("dragged", true, true);
        el.dispatchEvent(dragEvent);
        me.fireEvent('change', me);
      };
      document.body.addEventListener('mousemove', onMove, false);
    }, false);

    document.body.addEventListener('mouseup', function () {
      document.body.removeEventListener('mousemove', onMove, false);
    }, false);
    var me = this;
    */
      //this.width = this.height;
  },

  afterFirstLayout : function () {
      this.addListener('resize', this.onresize, this);
      console.log('color');
      this.onresize();
  },

    onresize: function(){

        var w = this.getWidth();
        var h = this.getHeight();
        //this component should be a square, so we check the aspect ratio and change accordingly.
        if(w == 0 && h > 0) this.setWidth(h);
        if(h == 0 && w > 0) this.setHeight(w);
        if(h == 0 && w == 0){
            this.setWidth(300);
            this.setHeight(300);
        }
        //take the minimum dimension
        if(w < h) this.setHeight(w);
        if(h < w) this.setWidth(h);


        var canvas = document.getElementById('wheel-canvas');
        var context = canvas.getContext("2d");
        canvas.width = this.getWidth();
        canvas.height = this.getHeight();

        this.setWheelRadius(canvas);

        var width = canvas.width;
        var height = canvas.height;
        var imageData = context.createImageData(width, height);
        this.generateColorWheel();
        this.setColorRgb(0.75, 0.86, 1.0);
    },

  setValue : function (x, y) {
    var w = this.getWidth();
    var h = this.getHeight();

    this.dot.setAttribute('cx', x);
    this.dot.setAttribute('cy', (h - y));
  },

  getValue : function () {
    var w = this.getWidth();
    var h = this.getHeight();
    var x = this.dot.getAttribute('cx');
    var y = this.dot.getAttribute('cy');
    return {
      x : x / w,
      y : y / h
    }
  },

  setColorRgb : function (r, g, b) {
    var hsv = this.RGBtoHSV(r, g, b);
    this.setColorHsv(hsv.h,hsv.s,hsv.v);
  },

  setColorHsv : function (h, s, v) {
    var r = this.wheelRadius;
    var cen = this.wheelCenter;
    var phi = 2*Math.PI*(h + 90) / 360;

    var x = cen[0] + r*s*Math.cos(phi);
    var y = cen[1] + r*s*Math.sin(phi);
    this.setValue(x, y);
  },

  getHsv : function () {
    var val = this.getValue();
    return {
      h : 360 * val.x,
      s : 1.0 - val.y,
      v : 1.0
    }
  },

  getRgb : function () {
    var val = this.getValue();
    var canvas = document.getElementById('wheel-canvas');
    var context = canvas.getContext("2d");
    var width = canvas.width;
    var height = canvas.height;
    return this.getRgbWheel(width * val.x, height * val.y, canvas);
    /*
    var imageData = context.getImageData(width*val.x, height*val.y, 1, 1);
    console.log(imageData.data[0],imageData.data[1],imageData.data[2],imageData.data[3], val.x, val.y);
    return {
    h : 360 * val.x,
    s : 1.0 - val.y,
    v : 1.0
    }
    var rgb = this.HSVtoRGB(360 * val.x, 1.0 - val.y, 1.0);


    return rgb;
     */
  },

  RGBtoHSV : function (r, g, b) {
    //lazy, just grabbed code
    //http://www.cs.rit.edu/~ncs/color/t_convert.html
    var h,
    s,
    v;
    var min = Math.min(r, Math.min(g, b));
    var max = Math.max(r, Math.max(g, b));

    v = max; // v
    var delta = max - min;

    if (max != 0)
      s = delta / max; // s
    else {
      // r = g = b = 0		// s = 0, v is undefined
      s = 0;
      h = -1;
      return;
    }
    if (r == max)
      h = (g - b) / delta; // between yellow & magenta
    else if (g == max)
      h = 2 + (b - r) / delta; // between cyan & yellow
    else
      h = 4 + (r - g) / delta; // between magenta & cyan
    h *= 60; // degrees
    if (h < 0)
      h += 360;
    if(delta == 0) h = 0;
    return {
      h : h,
      s : s,
      v : v
    };
  },

  HSVtoRGB : function (h, s, v) {
    var r,
    g,
    b;
    var i;
    var f,
    p,
    q,
    t;
    if (s == 0) {
      // achromatic (grey)
      return {
        r : v,
        g : v,
        b : v
      };
    }
    h /= 60; // sector 0 to 5
    i = Math.floor(h);
    f = h - i; // factorial part of h
    p = v * (1 - s);
    q = v * (1 - s * f);
    t = v * (1 - s * (1 - f));
    //console.log(h, f,p,q,t);
    switch (i) {
    case 0:
      r = v;
      g = t;
      b = p;
      break;
    case 1:
      r = q;
      g = v;
      b = p;
      break;
    case 2:
      r = p;
      g = v;
      b = t;
      break;
    case 3:
      r = p;
      g = q;
      b = v;
      break;
    case 4:
      r = t;
      g = p;
      b = v;
      break;
    default: // case 5:
      r = v;
      g = p;
      b = q;
      break;
    }
    return {
      r : r,
      g : g,
      b : b
    };
  },

  HSVtoRGB2 : function(h, s, v){
       var phi = Math.PI*h/180;
       col = {r: 0.5*(1.0+Math.cos(phi)),
              g: 0.5*(1.0+Math.cos((phi + 2.0/3.0*Math.PI))),
              b: 0.5*(1.0+Math.cos((phi + 4.0/3.0*Math.PI)))};

      var t = phi - Math.floor(phi);

      col.r = v*(s * col.r + (1.0 - s));
      col.g = v*(s * col.g + (1.0 - s));
      col.b = v*(s * col.b + (1.0 - s));
      return col;
  },

   RGBtoHSV2 : function(r, g, b){
      //can't determin inverse without newton's method or gauss-seidel
  }
});

//////////////////////////////////////////////////////////////////
//
// alpha slider
//
//////////////////////////////////////////////////////////////////


Ext.define('BQ.viewer.Volume.alphaSlider', {
  extend : 'Ext.slider.Multi',
  alias : 'widget.alpha-slider',
  cls : 'key-slider',

  constructor : function (config) {
    this.callParent(arguments);
    return this;
  },

  initComponent : function () {
    this.callParent();
  },

  afterRender : function () {
    this.svgUrl = "http://www.w3.org/2000/svg";
    this.svgdoc = document.createElementNS(this.svgUrl, "svg");
    this.svgdoc.setAttributeNS(null, 'class', 'val-slider-back');
    this.el.dom.appendChild(this.svgdoc);
    this.svgBackGround = document.createElementNS(this.svgUrl, "g");
    this.svgBackGround.setAttributeNS(null, 'class', 'val-slider-back');
    this.svgdoc.appendChild(this.svgBackGround);

    var me = this;
    this.rgbColor = [25, 10, 90, 1.0];
    this.drawBackGround();
    this.callParent();
  },

  setColor : function (r, g, b, a) {
    this.rgbColor = [r, g, b, a];
    this.drawBackGround();
  },

  setValue : function (index, value, animate) {
    this.callParent(arguments);
    this.drawBackGround();
  },

  getStop : function (offset, color) {
    svgStop = '<stop offset="' + offset +
      '%" stop-color="rgba(' +
      color[0] + ', ' +
      color[1] + ', ' +
      color[2] + ', ' +
      color[3] + ')"/>\n';
    return svgStop;
  },

  drawBackGround : function (canvas) {
    var grad1 = ['<defs>',
      '<linearGradient id="toAlpha" ',
      'x1="0%" y1="0%" x2="0%" y2="100%">\n'
    ].join(' ');

    grad1 += this.getStop(0, this.rgbColor); //full color
    grad1 += this.getStop(100, [0, 0, 0, 0]); //zero color
    grad1 += '</linearGradient> </defs>';

    var rect = ['<rect id="rectVal"',
      'x="0" y="0"',
      'rx="3" ry="3"',
      'width="100%"',
      'height="100%"',
      'fill="url(#toAlpha)"',
      '/>'].join(' ');

    var checkRect = [
      '<defs>',
      ' <pattern id="checkerPattern" width="20" height="20"',
      'patternUnits="userSpaceOnUse">',
      '<rect fill="black" x="0" y="0" width="10" height="10" />',
      '<rect fill="white" x="10" y="0" width="10" height="10" />',
      '<rect fill="black" x="10" y="10" width="10" height="10" />',
      '<rect fill="white" x="0" y="10" width="10" height="10" />',
      '</pattern>',
      '</defs>',
      '<rect fill="url(#checkerPattern)" style="stroke:white"',
      'x="0"',
      'y="0"',
      'rx="3"',
      'ry="3"',
      'width="100%" height="100%" />',
      '</g>',
    ].join('\n');

    var svg = [' <svg width=100% height=100% >',
      grad1,
      checkRect,
      rect,
      '</svg>'].join('\n');

    this.svgBackGround.innerHTML = svg;
  },

  //----------------------------------------------------------------------
  // event handlers
  //----------------------------------------------------------------------
  changecomplete : function () {
    this.sortKeys();
    this.callParent();
  },

});

//////////////////////////////////////////////////////////////////
//
// value slider
//
//////////////////////////////////////////////////////////////////


Ext.define('BQ.viewer.Volume.valueSlider', {
  extend : 'Ext.slider.Multi',
  alias : 'widget.value-slider',
  cls : 'key-slider',

  constructor : function (config) {
    this.callParent(arguments);
    return this;
  },

  initComponent : function () {
    this.callParent();
  },

  afterRender : function () {
    this.svgUrl = "http://www.w3.org/2000/svg";
    this.svgdoc = document.createElementNS(this.svgUrl, "svg");
    this.svgdoc.setAttributeNS(null, 'class', 'val-slider-back');
    this.el.dom.appendChild(this.svgdoc);
    this.svgBackGround = document.createElementNS(this.svgUrl, "g");
    this.svgBackGround.setAttributeNS(null, 'class', 'val-slider-back');
    this.svgdoc.appendChild(this.svgBackGround);

    var me = this;
    this.rgbColor = [25, 10, 90, 1.0];
    this.drawBackGround();
    this.callParent();
  },

  setColor : function (r, g, b, a) {
    this.rgbColor = [r, g, b, a];
    this.drawBackGround();
  },

  setValue : function (index, value, animate) {
    this.callParent(arguments);
    this.drawBackGround();
  },

  getStop : function (offset, color) {
    svgStop = '<stop offset="' + offset +
      '%" stop-color="rgba(' +
      color[0] + ', ' +
      color[1] + ', ' +
      color[2] + ', ' +
      color[3] + ')"/>\n';
    return svgStop;
  },

  drawBackGround : function (canvas) {
    var grad1 = ['<defs>',
      '<linearGradient id="toBlack" ',
      'x1="0%" y1="0%" x2="0%" y2="100%">\n'
    ].join(' ');

    grad1 += this.getStop(0, this.rgbColor); //yellow
    grad1 += this.getStop(100, [0, 0, 0, this.rgbColor[3]]); //green
    grad1 += '</linearGradient> </defs>';

    var rect = ['<rect id="rectVal"',
      'x="0" y="0"',
      'rx="3" ry="3"',
      'width="100%"',
      'height="100%"',
      'fill="url(#toBlack)"',
      '/>'].join(' ');

    var svg = [' <svg width=100% height=100% >',
      grad1,
      rect,
      '</svg>'].join('\n');

    this.svgBackGround.innerHTML = svg;
  },

  //----------------------------------------------------------------------
  // event handlers
  //----------------------------------------------------------------------
  changecomplete : function () {
    this.sortKeys();
    this.callParent();
  },

});

Ext.define('BQ.viewer.Volume.excolorpicker', {
    extend : 'Ext.container.Container',
    alias : 'widget.excolorpicker',

    layout : {
        type : 'hbox',
        align : 'stretch',
        pack : 'end',
    },

    initComponent : function () {
        this.title = 'excolorpicker';
        var me = this;
        this.rampSvg = Ext.create('BQ.viewer.Volume.fieldSlider', {
            //margin : '0 2 0 2',
            flex : 1,
            listeners : {
                change : function (e, slider) {
                    //var hsv = me.rampSvg.getHsv();
                    var rgb = me.rampSvg.getRgb();
                    //var rgb = me.rampSvg.HSVtoRGB(hsv.h, hsv.s, 1.0);
                    me.valueSlider.setColor(Math.floor(rgb[0]),
                                            Math.floor(rgb[1]),
                                            Math.floor(rgb[2]), 1.0);
                    if(me.alphaSlider)
                        me.alphaSlider.setColor(Math.floor(rgb[0]),
                                                Math.floor(rgb[1]),
                                                Math.floor(rgb[2]), 1.0);
                    me.fireEvent('change', me);
                    if (me.handler)
                        me.handler(e, me);
                }
            }
        });

        this.valueSlider = Ext.create('BQ.viewer.Volume.valueSlider', {
        cls : 'val-slider',
        vertical : true,
        minValue : 0.00,
        maxValue : 100,
        values : [50],
        margin : '0 2 0 2',
        listeners : {
          change : function (slider, value, thumb) {
            me.fireEvent('change', me);

          },

          scope : me,
        }
    });
      if(this.alphaSlider)
          this.alphaSlider = Ext.create('BQ.viewer.Volume.alphaSlider', {
              cls : 'val-slider',
              vertical : true,
              minValue : 0.00,
              maxValue : 100,
              values : [50],
              margin : '0 2 0 2',
              listeners : {
                  change : function (slider, value, thumb) {
                      me.fireEvent('change', me);
                  },
                  scope : me,
              }
          });

      Ext.apply(this, {
          items : [this.rampSvg, this.valueSlider, this.alphaSlider],
      });

    this.callParent();
  },

  setColorRgb : function (r, g, b, a) {

    //var rgb = this.rampSvg.getRgb();
    var hsv = this.rampSvg.RGBtoHSV(r,g,b);
    if (hsv) {
      var rgb = this.rampSvg.HSVtoRGB(hsv.h, hsv.s, 1.0);

      this.rampSvg.setColorHsv(hsv.h, hsv.s, hsv.v);

      this.valueSlider.setColor(Math.floor(255 * rgb.r),
        Math.floor(255 * rgb.g),
        Math.floor(255 * rgb.b), 1.0);

      this.valueSlider.setValue(0, 100 * hsv.v, true);
    }
      if(this.alphaSlider)
          this.alphaSlider.setValue(0, 100 * a, true);
  },

  getColorRgb : function () {
    //this needs updating:
    var val = this.valueSlider.getValue(0);
    var rgb = this.rampSvg.getRgb();
    rgb[0] *= val / 100;
    rgb[1] *= val / 100;
    rgb[2] *= val / 100;
      if(this.alphaSlider)
          rgb[3] = this.alphaSlider.getValue(0) / 100;
      else rgb[3] = 1.0;
    return rgb;
  },

  afterFirstLayout : function () {
    //this.setColorRgb(1.0,0.0,0.0);
    this.callParent();
  },
});
