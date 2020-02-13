//////////////////////////////////////////////////////////////////
//
// transfer slider
//
//////////////////////////////////////////////////////////////////


Ext.define('BQ.viewer.Volume.transferSlider', {
  extend : 'Ext.slider.Multi',
  alias : 'widget.transfer-slider',
  cls : 'key-slider',
  height : 40,
  constructor : function (config) {
    this.callParent(arguments);
    return this;
  },

  initComponent : function () {
    this.keyArray = new Array();
    this.autoKey = false;
    this.insertDist = 2;
    this.sampleRate = 8;
    this.timeValue = 0;
    var me = this;
    this.lastClicked = 0;
    this.stops = [{
        color : [0, 0, 0, 0],
        offset : 0
      }
    ];
    this.callParent();
    me.addEvents('clicked');
    this.addStop([256, 256, 256, 1.0], 100);
  },

  afterRender : function () {
    this.svgUrl = "http://www.w3.org/2000/svg";
    this.svgdoc = document.createElementNS(this.svgUrl, "svg");
    this.svgdoc.setAttributeNS(null, 'class', 'grad-slider');
    this.el.dom.appendChild(this.svgdoc);
    this.svgBackGround = document.createElementNS(this.svgUrl, "g");
    this.svgBackGround.setAttributeNS(null, 'class', 'grad-slider');
    this.svgdoc.appendChild(this.svgBackGround);

    var me = this;

    //this.addStop([50, 15, 20, 0.15],25);
    //this.addStop([80, 10, 10, 0.75],32);
    //this.addStop([50, 10, 1, 0.55],45);
    //this.addStop([40, 10, 1, 0.5],72);
    //this.addStop([50,50,50, .95],82);
    //this.addStop([50,50,50, 0.95],100);
    this.drawBackGround();
    this.callParent();
  },

  drawBackGround : function (canvas) {
    var svgStops = '<defs> <linearGradient id="Gradient1">\n';
    for (var i = 0; i < this.stops.length; i++) {
      var stop = this.stops[i];
      svgStops += '<stop offset="' + stop.offset +
      '%" stop-color="rgba(' +
      stop.color[0] + ', ' +
      stop.color[1] + ', ' +
      stop.color[2] + ', ' +
      stop.color[3] + ')"/>\n';
    }
    svgStops += '</linearGradient> </defs>'
    var rect = ['<rect id="rect1"',
      'x="0" y="0"',
      'rx="3" ry="3"',
      'width="100%"',
      'height="100%"',
      'fill="url(#Gradient1)"',
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
      svgStops,
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

  setValue : function (index, value, animate, changeComplete) {

    if (index == 0)
      return;
    if (index == this.stops.length - 1)
      return;
    this.callParent(arguments);
    this.stops[index].offset = value;

    this.drawBackGround();
    this.lastClicked = index;
  },

  onMouseDown : function (e) {
    var me = this,
    thumbClicked = false,
    i = 0,
    thumbs = me.thumbs,
    len = thumbs.length,
    trackPoint;

    if (me.disabled) {
      return;
    }

    //see if the click was on any of the thumbs
    var thumb = 0;
    for (; i < len; i++) {
      thumbClicked = thumbClicked || e.target == thumbs[i].el.dom;
      thumb = e.target == thumbs[i].el.dom ? i : thumb;
    }

    if (thumbClicked) {
      this.lastClicked = thumb;
      me.fireEvent('clicked', me, thumb);
      var thisThumb = this.thumbs[thumb].el;
    }

    if (me.clickToChange && !thumbClicked) {
      trackPoint = me.getTrackpoint(e.getXY());
      if (trackPoint !== undefined) {
        me.onClickChange(trackPoint);
      }
    }
    me.focus();
  },

  sortKeys : function () {
    this.stops.sort(function (a, b) {
      return (a.offset - b.offset);
    });

    this.thumbs.sort(function (a, b) {
      return (a.value - b.value);
    });

    for (var i = 0; i < this.thumbs.length; i++) {
      this.thumbs[i].index = i;
    }
  },

  scaleKeys : function (newScale) {
    var oldScale = this.maxValue;
    if (oldScale == 0)
      return;
    var scale = newScale / oldScale;

    for (var i = 0; i < this.thumbs.length; i++) {
      var newVal = this.thumbs[i].value * scale;
      this.thumbs[i].value = newVal;
    }
  },

  addStop : function (rgba, offset) {
    this.addThumb(offset);
    this.stops.push({
      color : rgba,
      offset : offset
    });
    this.sortKeys();
  },

  removeStop : function (it) {

    if (it >= 0) {
      var innerEl = this.thumbs[it].ownerCt.innerEl.dom;
      innerEl.removeChild(this.thumbs[it].el.dom);
      this.thumbs.splice(it, 1);
      for (var i = 0; i < this.thumbs.length; i++) {
        this.thumbs[i].index = i;
      }

      this.stops.splice(it, 1);
    }
  },

  removeCurrentStop : function () {
    this.removeStop(this.lastClicked);
    this.drawBackGround();
  },

  addNextStop : function () {
    var i0 = this.lastClicked;
    var i1 = i0 + 1;
    if (i0 == this.thumbs.length - 1)
      i1 = i0 - 1;
    var o0 = this.thumbs[i0].value;
    var o1 = this.thumbs[i1].value;
    var c0 = this.stops[i0].color;
    var c1 = this.stops[i1].color;
    var cA = [0.5 * (c0[0] + c1[0]),
      0.5 * (c0[1] + c1[1]),
      0.5 * (c0[2] + c1[2]),
      0.5 * (c0[3] + c1[3])];
    this.addStop(cA, 0.5 * (o0 + o1));
    this.drawBackGround();
  },

  setStopColor : function (value, i, thumb) {
    thumb = typeof thumb == 'undefined' ? this.lastClicked : thumb;
    this.stops[thumb].color[i] = value;
    this.drawBackGround();
  },

});



Ext.define('BQ.viewer.Volume.transferGraph', {
  //extend : 'Ext.Component',
  extend : 'Ext.container.Container',
  alias : 'widget.transfer-graph',
  layout : 'fit',

  getStop : function (offset, color) {
    svgStop = '<stop offset="' + offset +
      '%" stop-color="rgba(' +
      color[0] + ', ' +
      color[1] + ', ' +
      color[2] + ', ' +
      color[3] + ')"/>\n';
    return svgStop;
  },

  getGradSvg : function (stops) {
    var me = this;
    var grad1 = ['<defs>',
      '<linearGradient id="transfer" ',
      'x1="0%" y1="0%" x2="0%" y2="100%">\n'
    ].join(' ');

    stops.each(function (record) {
      var color = record.data.color;
      color[3] = 1.0;
      grad1 += me.getStop(record.data.offset, color);
    });

    grad1 += '</linearGradient> </defs>';
    return grad1;
  },

  getGrad : function (id, angle, stops) {
    var stopSvg = {};

    stops.each(function (record) {
      var color = record.data.color;
      stopSvg[record.data.offset / 100] = {
        color : 'rgb(' +
        color[0] + ', ' +
        color[1] + ', ' +
        color[2] + ')'
      }
    });
    /*
    for (var i = 0; i < stops.length; i++) {
    stopSvg[stops[i].offset] = {
    color : 'rgb(' +
    stops[i].color[0] + ', ' +
    stops[i].color[1] + ', ' +
    stops[i].color[2] + ')'
    }
    };
     */
    gradSvg = {
      id : id,
      angle : angle,
      stops : stopSvg,
    };
    return gradSvg;
  },

  updateChartSurface : function () {
    var defs = this.chart.surface.getDefs();
    var oldGrad = this.chart.surface.getDefs().childNodes[0];

    this.chart.surface.getDefs().removeChild(oldGrad);
    var newGrad = this.getGrad('transfer', 0, this.store);
    this.chart.gradients[0] = newGrad;

    gradientEl = this.chart.surface.createSvgElement("linearGradient");
    gradientEl.setAttribute("x1", 0);
    gradientEl.setAttribute("y1", 0);
    gradientEl.setAttribute("x2", 1);
    gradientEl.setAttribute("y2", 0);

    gradientEl.id = newGrad.id;
    this.chart.surface.getDefs().appendChild(gradientEl);
    var me = this;
    this.store.each(function (record) {
      //var color = record.data.color;
      var stop = record.data;
      var color=
         'rgb(' +
        stop.color[0] + ', ' +
        stop.color[1] + ', ' +
        stop.color[2] + ')';

      var stopEl = me.chart.surface.createSvgElement("stop");
      stopEl.setAttribute("offset", stop.offset + "%");
      stopEl.setAttribute("stop-color", color);
      stopEl.setAttribute("stop-opacity", 1.0);
      gradientEl.appendChild(stopEl);
    });
    this.chart.redraw();

  },

  getCount : function(){
    return this.store.getCount()
  },

  getStop : function(i){
    return this.store.getAt(i).data;
  },

  constructor: function(config){

    this.addEvents('selected');
    this.listeners = config.listeners;
    this.callParent(arguments);
  },

  initComponent : function () {
    this.lastClicked = 0;

    Ext.define('transferStops', {
      extend : 'Ext.data.Model',
      fields : ['color', 'alpha', 'offset']
    });

    this.stops = [{
        color : [0, 0, 0],
        alpha : 0,
        offset : 0
      }, {
        color : [255, 255, 255],
        alpha : 1,
        offset : 100
      }, ];

    var fields = ['offset', 'alpha'];

    this.store = Ext.create('Ext.data.JsonStore', {
        model : 'transferStops',
        fields : fields,
        data : this.stops,
        sorters : [{
            sorterFn : function (o1, o2) {
              var off1 = o1.get('offset');
              var off2 = o2.get('offset');
              if (off1 === off2) {
                return 0;
              }
              return off1 < off2 ? -1 : 1;
            }
          }
        ],

      });

    selectedNode = null;
    var me = this;
    var moveNode = function (e, eOpts) {
      var mxy = e.getXY();
      var cxy = me.chart.getXY();
      var dxy = [mxy[0] - cxy[0], mxy[1] - cxy[1]];
      var bcx = selectedNode.series.bbox.x;
      var bcy = selectedNode.series.bbox.y;
      var blx = selectedNode.series.bbox.width;
      var bly = selectedNode.series.bbox.height;

      var axes = selectedNode.series.chart.axes;
      var xmin = axes.get("bottom").minimum;
      var xmax = axes.get("bottom").maximum;
      var ymin = axes.get("left").minimum;
      var ymax = axes.get("left").maximum;
      var dx = (xmax - xmin) / blx;
      var dy = (ymax - ymin) / bly;

      var offset = dx * (dxy[0] - bcx);
      var alpha = dy * (bly - (dxy[1] - bcy));
      offset = offset >= 100 ? 100 : offset;
      offset = offset <=   0 ?   0 : offset;
      alpha = alpha >= 1 ? 1 : alpha;
      alpha = alpha <= 0 ? 0 : alpha;
      var data = selectedNode.storeItem.data;

      if(me.lastClicked != 0 && me.lastClicked != me.store.getCount() - 1){
        data.offset = offset;
      }
      data.alpha = alpha;
      //clamp values

      me.fireEvent('update', me, me.lastClicked);
      me.updateChartSurface();
      //console.log(me.chart);
      me.chart.redraw();
    };

    this.chart = Ext.create('Ext.chart.Chart', {
        style : 'background:#fff',
        animate : false,
        //theme : 'Browser:gradients',
        defaultInsets : 30,
        store : this.store,
        gradients : [this.getGrad('transfer', 0, this.store)],
        axes : [{
            type : 'Numeric',
            position : 'left',
            fields : ['alpha'],
            minimum : 0,
            maximum : 1
          }, {
            type : 'Numeric',
            position : 'bottom',
            fields : ['offset'],
            minimum : 0,
            maximum : 100
          }
        ],
        series : [{
            type : 'line',
            axis : 'left',
            //highlight : true,
            markerConfig : {
              type : 'circle',
              size : 4,
              radius : 4,
              fill : 'rgb(0,0,0)',
              'stroke-width' : 0
            },
            listeners : {
              itemmousedown : function (curRecord, eopts) {
                selectedNode = curRecord;

                var oldRecord = me.chart.series.items[0].items[me.lastClicked];
                //oldRecord.sprite.fill =  "rgb(0,0,0)";
                oldRecord.sprite.setStyle('fill','rgb(1,0,0)');
                oldRecord.sprite.setAttributes({
                  scale:{x: 1.0, y: 1.0}
                });

                me.lastClicked = me.store.data.indexOf(selectedNode.storeItem);
                selectedNode.sprite.setStyle('fill','rgb(1,0,0)');
                selectedNode.sprite.setAttributes({
                  scale:{x: 1.5, y: 1.5}
                });

                me.chart.redraw();
                me.fireEvent('selected', me, me.lastClicked);
                me.chart.on('mousemove', moveNode, null);

              },

              itemmouseup : function (item, eopts) {
                selectedNode = null;
                me.fireEvent('finishupdate', me, me.lastClicked);
                me.chart.un('mousemove', moveNode);
              }
            },
            /*
            tips : {
            trackMouse : true,
            renderer : function (storeItem, item) {
            var d = Ext.Date.format(new Date(storeItem.get('date')), 'M y'),
            percent = storeItem.get(item.storeField) + '%';

            this.setTitle(item.storeField + ' - ' + d + ' - ' + percent);
            }
            },
             */
            xField : 'offset',
            yField : 'alpha',
            fill : true,
            style : {
              fill : 'url(#transfer)',
              lineWidth : 0.5,
              stroke : '#666',
              opacity : 0.86
            }
          }
        ],
        /*
        listeners:{
        mousemove: function(e, eOpts){
        console.log(selectedNode, e);

        },

        }
         */
      });
    this.transferGradient = document.getElementById('transfer');

    this.items = [this.chart];

    this.callParent();
  },

  afterFirstLayout : function () {

    var sprite = this.chart.series.items[0].items[0].sprite;
    console.log("sprite: ", sprite);
    sprite.setAttributes({
      fill : 'url(#transfer)'
    }, true);
    this.updateChartSurface();
  },

  sortKeys : function () {
    this.stops.sort(function (a, b) {
      return (a.offset - b.offset);
    });
  },

  scaleKeys : function (newScale) {
    var oldScale = this.maxValue;
    if (oldScale == 0)
      return;
    var scale = newScale / oldScale;

    for (var i = 0; i < this.thumbs.length; i++) {
      var newVal = this.thumbs[i].value * scale;
      this.thumbs[i].value = newVal;
    }
  },

  addStop : function (rgb, alpha, offset) {
    var data = Ext.create('transferStops', {
        color : rgb,
        alpha : alpha,
        offset : offset,
      });
    //this.stops.push(data);
    //this.sortKeys();
    this.store.addSorted(data);

    this.updateChartSurface();
    //console.log(grad, this.chart.el, this.chart.el.dom.firstChild);

    this.store.fireEvent('refresh');
    this.chart.redraw();

    console.log(this.chart);

  },

  removeStop : function (it) {
    var rec = this.store.getAt(it);
    this.store.remove(rec);

    console.log(this.store);
  },

  removeCurrentStop : function () {
    this.removeStop(this.lastClicked);
    this.store.fireEvent('refresh');
    this.chart.redraw();
    this.updateChartSurface();

    //this.drawBackGround();
  },

  getRgb : function(i){
  var col = this.store.getAt(i).data.color;
  col[3] = this.store.getAt(i).data.alpha;
    return col;
  },

  addNextStop : function () {
    var i0 = this.lastClicked;
    var i1 = i0 + 1;

    if (i0 == this.stops.length - 1)
      i1 = i0 - 1;
    var o0 = this.store.getAt(i0).data.offset;
    var o1 = this.store.getAt(i1).data.offset;
    var a0 = this.store.getAt(i0).data.alpha;
    var a1 = this.store.getAt(i1).data.alpha;
    var c0 = this.store.getAt(i0).data.color;
    var c1 = this.store.getAt(i1).data.color;

    var cA = [Math.floor(0.5 * (c0[0] + c1[0])),
              Math.floor(0.5 * (c0[1] + c1[1])),
              Math.floor(0.5 * (c0[2] + c1[2]))]

    //var cA = [Math.random(), Math.random(), Math.random()];
    this.addStop(cA, 0.5 * (a0 + a1), 0.5 * (o0 + o1));
    //this.lastClicked++;
    //this.drawBackGround();
  },

  setStopColor : function (value,thumb) {
    thumb = typeof thumb == 'undefined' ? this.lastClicked : thumb;

    this.store.getAt(thumb).data.color[0] = value[0];
    this.store.getAt(thumb).data.color[1] = value[1];
    this.store.getAt(thumb).data.color[2] = value[2];
    this.store.getAt(thumb).data.alpha = value[3];


    this.updateChartSurface();
    //this.stops[thumb].color[i] = value;
    //this.drawBackGround();
  },
});

Ext.define('BQ.viewer.Volume.transfer', {
  extend : 'Ext.container.Container',
  //cls : 'materialcontroller',
  alias : 'widget.transfer',

  mixins : ['BQ.viewer.Volume.uniformUpdate'],
  addUniforms : function () {
    this.tSize = 64;
    this.sceneVolume.initUniform('transfer', "t", null);
    this.sceneVolume.initUniform('TRANSFER_SIZE', "i", this.tSize);
    this.sceneVolume.initUniform('USE_TRANSFER', "i", this.transfer);
  },

  changed : function () {
    if (this.transferGraph.getCount() < 2)
      return;
    var pixels = new Uint8Array(4*this.tSize);
    var cStop = 0;
    var ci = 0;
    var l = this.transferGraph.getCount();
    var stop0 = this.transferGraph.getStop(0);
    var stop1 = this.transferGraph.getStop(l-1);

    if (this.transferGraph.getStop(0).offset != 0)
      return;
    if (this.transferGraph.getStop(l - 1).offset != 100)
      return;

    for (var i = 0; i < this.tSize; i++) {
      var stop = this.transferGraph.getStop(cStop);
      var nstop = this.transferGraph.getStop(cStop + 1);

      var per = ci / this.tSize * 100;

      if (per > nstop.offset - stop.offset) {
        ci = 0;
        cStop++;
        stop = this.transferGraph.getStop(cStop);
        nstop = this.transferGraph.getStop(cStop + 1);
        console.log("new stops: ", cStop, stop, nstop);
      }

      var t = ci / this.tSize * 100 / (nstop.offset - stop.offset);
      //console.log(t, cStop, per, stop, nstop);
      var c0 = stop.color;
      var c1 = nstop.color;
      c0[3] = stop.alpha;
      c1[3] = nstop.alpha;
      //console.log(i,ci, per,t,nstop.offset,stop.offset);
      pixels[4 * i + 0] = (1 - t) * c0[0] + t * c1[0];
      pixels[4 * i + 1] = (1 - t) * c0[1] + t * c1[1];
      pixels[4 * i + 2] = (1 - t) * c0[2] + t * c1[2];
      pixels[4 * i + 3] = 255 * ((1 - t) * c0[3] + t * c1[3]);
      ci++;
    }
    //conso
    var rampTex = this.panel3D.rampTex;
    rampTex = new THREE.DataTexture(pixels, this.tSize, 1, THREE.RGBAFormat);
    rampTex.needsUpdate = true;
    this.sceneVolume.setUniform('transfer', rampTex);
    this.sceneVolume.setUniform('TRANSFER_SIZE', this.tSize);

  },

  initComponent : function () {
    var me = this;
    this.transfer = 0;
    this.title = 'transfer';
    var controlBtnSize = 22;

    var useTransfer = Ext.create('Ext.form.field.Checkbox', {
        boxLabel : 'use transfer function',
        height : controlBtnSize,
        checked : false,
        handler : function () {
          this.transfer ^= 1;
          this.changed();
          this.sceneVolume.setUniform('USE_TRANSFER', this.transfer);
          if (this.transfer == 1) {
            this.showButton.show();
          } else
            this.showButton.hide();

        },
        scope : me,
      });

    this.transferGraph = Ext.create('BQ.viewer.Volume.transferGraph', {
      listeners : {
        selected : function(graph, i){
            var c = graph.getRgb(i);
            if(me.colorWindow)
              me.colorPicker.setColorRgb(c[0] / 255, c[1] / 255, c[2] / 255, c[3]);
        },
        finishupdate : function(graph, i){
            var c = graph.getRgb(i);
            if(me.colorWindow)
              me.colorPicker.setColorRgb(c[0] / 255, c[1] / 255, c[2] / 255, c[3]);
        }
      }
    });

    this.transferSlider = Ext.create('BQ.viewer.Volume.transferSlider', {
        //tic:      this.tic,
        panel3D : this.panel3D,
        flex : 1,
        animate : false,
        margin : '2 2 2 2',
        listeners : {
          clicked : function (slider, thumb) {
            console.log(slider, thumb);
            var c = slider.stops[thumb].color;
            me.colorPicker.setColorRgb(c[0] / 255, c[1] / 255, c[2] / 255, c[3]);
          },
          change : function (slider, value, thumb) {
            var l = slider.thumbs.length;
            if (thumb.index == 0) {
              slider.setValue(0, 0);
            }
            if (thumb.index == l - 1) {
              slider.setValue(l - 1, 100);
            }
            me.changed();
          },
          scope : me
        },
        useTips : true,
      });
    this.addUniforms();
    this.isLoaded = true;

    this.showButton = Ext.create('Ext.Button', {
        text : 'edit transfer function',
        handler : function (button, pressed) {
          console.log("twindow: ", this.transferWindow);

          if (!this.transferWindow)
            me.displayTransferWindow();
          else
            this.transferWindow.show();
        },
        scope : me,
      });

    this.colorPicker = Ext.create('BQ.viewer.Volume.excolorpicker', {
        listeners:{
        change : function (picker) {
          var rgb = picker.getColorRgb();
          var color = [Math.floor(rgb[0]), Math.floor(rgb[1]), Math.floor(rgb[2]), rgb[3]]
          me.transferGraph.setStopColor(color);
          me.changed();
        }
        }
      });

    this.showButton.hide();
    this.addUniforms();
    Ext.apply(this, {
      items : [useTransfer, this.showButton],
    });

    this.callParent();
  },

  displayTransferWindow : function () {
    var me = this;
    var addButton = Ext.create('Ext.Button', {
        text : '+',
        //cls: 'volume-button',
        handler : function (button, pressed) {
          me.transferGraph.addNextStop();
        },
        scope : me,
      });

    var subButton = Ext.create('Ext.Button', {
        text : '-',
        //cls: 'volume-button',
        handler : function (button, pressed) {
          me.transferGraph.removeCurrentStop();
          //me.displayParameterWindow();
        },
        scope : me,
      });

    var showColorButton = Ext.create('Ext.Button', {
        text : 'show color',
        handler : function (button, pressed) {
          if (!this.colorWindow)
            me.displayColorWindow();
          else
            this.colorWindow.show();

        },
        scope : me,
      });

    this.transferWindow = Ext.create('Ext.window.Window', {
        title : 'transfer function',
        height : 250,
        width : 800,
        layout : 'fit',
        items : [this.transferGraph],
        bbar : {
          items : [addButton, subButton, showColorButton]
        },
        closeAction : 'hide',
      }).show();

  },

  displayColorWindow : function () {
    var me = this;
    this.colorWindow = Ext.create('Ext.window.Window', {
        title : 'color window',
        height : 250,
        width : 300,
        layout : 'fit',
        items : [this.colorPicker],

        closeAction : 'hide',
      }).show();

  },

  afterFirstLayout : function () {
    //this.transferSlider.show();
    this.changed();
  },
});