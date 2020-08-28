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

/*
ViewerPlugin.prototype.updatePosition = function (){
};

ViewerPlugin.prototype.setSize = function (size)
{
    if (size.height)
        this.imagediv.style.height = size.height+"px";
    if (size.width)
        this.imagediv.style.width = size.width+"px";
};
*/

function VolScaleBar ( parent, new_pix_size ) {
	this.parent = parent;
	this.dragging = false;
	this.pix_phys_size = 0;
	this.bar_size_in_pix = 0;


	this.bar = document.createElementNS(xhtmlns, 'div');
    this.bar.setAttributeNS (null, 'id', 'scalebar_bar_vol');
	this.bar.innerHTML = "&#xA0;";
    this.bar.style.width = "100%";
    this.bar.style.height = "5px";
    this.bar.style.background =  '#FFFFFF';
	this.caption = document.createElementNS(xhtmlns, 'div');
    this.caption.setAttributeNS (null, 'id', 'scalebar_caption_vol');
	this.caption.innerHTML = '0.00 um';

	this.setValue( new_pix_size );

	this.parent.appendChild(this.bar);
	this.parent.appendChild(this.caption);
	//this.parent.appendChild(this.widget);
}

VolScaleBar.prototype.setPos = function ( x,y ) {
	this.widget.style.left = x + "px";
	this.widget.style.top = y + "px";
}

VolScaleBar.prototype.setValue = function ( val ) {
  if (this.pix_phys_size==val && this.bar_size_in_pix==this.bar.clientWidth) return;

  this.pix_phys_size = val;
  this.bar_size_in_pix = this.bar.clientWidth;
  var bar_size_in_um  = this.bar_size_in_pix * this.pix_phys_size;
  var capt = '' + bar_size_in_um.toFixed(4) + ' um';

  this.caption.innerHTML = capt;
}

function VolScaleBarTool (volume){
    this.name = 'scale_bar';
    this.base = renderingTool;
    this.base (volume, null);
}

VolScaleBarTool.prototype = new renderingTool();

VolScaleBarTool.prototype.addButton = function () {
    //blank since we don't actually add anything
};

VolScaleBarTool.prototype.initControls = function () {
    var me = this;
    var thisDom = this.volume.mainView.getEl().dom;

    this.volume.on('loaded', function () {
        if(me.scalePanel) return;
        var dim = me.volume.dim;
        var imgphys = me.volume.phys;

        if (imgphys==null || imgphys.pixel_size[0]==undefined || imgphys.pixel_size[0]==0.0000) {
            return;
        }

        me.scalePanel = Ext.create('Ext.panel.Panel', {
		    collapsible : false,
		    header : false,
		    renderTo : thisDom,
            layout : 'fit',
		    cls : 'vol-scalebar',

            listeners : {
                afterlayout: function(){

                    me.parentdiv = this.getEl().dom;
                    me.volume.addFade(this);
                    me.updateImage();
                }
            }
	    });
        me.volume.canvas3D.on({
            scope: me,
            render: me.updatePosition
        });
        //me.updateImage();
    });
};

VolScaleBarTool.prototype.updateImage = function () {
    //var view = this.viewer.current_view;
    var dim = this.volume.dim;
    var imgphys = this.volume.phys;

    if (imgphys==null || imgphys.pixel_size[0]==undefined || imgphys.pixel_size[0]==0.0000) {
      if (this.scalebar != null) {
        this.div.removeChild (this.scalebar.widget);
        delete this.scalebar;
      }
      this.scalebar = null;
      return;
    }

    var surf = this.parentdiv;
    //if (this.viewer.viewer_controls_surface) surf = this.viewer.viewer_controls_surface;

    if (this.scalebar == null)
        this.scalebar = new VolScaleBar ( surf, imgphys.pixel_size[0] );
    //this.scalebar.setValue( imgphys.pixel_size[0]/view.scale );
    this.scalebar.setValue( imgphys.pixel_size[0]);
};

VolScaleBarTool.prototype.updatePosition = function () {
    if (this.scalebar == null) return;
    var dims = this.volume.dims;

    var min = Math.min(dims.pixel.x, Math.min(dims.pixel.y,dims.pixel.z));
    var max = Math.max(dims.pixel.x, Math.max(dims.pixel.y,dims.pixel.z));
    var boxMin = Math.min(dims.slice.x, Math.min(dims.slice.y,dims.slice.z));
    var boxMax = Math.max(dims.slice.x, Math.max(dims.slice.y,dims.slice.z));

    var camPos = this.volume.canvas3D.camera.position;
    var fov = this.volume.canvas3D.fov;
    var d = camPos.length();
    var tanHalf = 2.0*Math.tan(Math.PI*fov/2/180);
    var l = d*tanHalf;
    var imgphys = this.volume.phys;
    var y = this.volume.canvas3D.getHeight();
    this.scalebar.setValue( l * dims.slice.y/y*dims.pixel.y);
    //this.scalebar.setValue( l );
    //this.scalebar.setValue( d*imgphys.pixel_size[0] );
};

/*******************************************************************************
Temp home for the axis tool
*******************************************************************************/

function VolAxisTool (volume){
    this.name = 'axis';
    this.base = renderingTool;
    this.base (volume, null);
}

VolAxisTool.prototype = new renderingTool();

VolAxisTool.prototype.addButton = function () {
    //blank since we don't actually add anything
};

VolAxisTool.prototype.initControls = function () {
    var me = this;
    var thisDom = this.volume.mainView.getEl().dom;

    this.Panel = Ext.create('Ext.container.Container', {
		collapsible : false,
		header : false,
		renderTo : thisDom,
        layout : 'fit',
		cls : 'vol-axis',
        items: [{xtype: 'threejs_panel',
                 itemId: 'axis_panel',
                 doAnimate : function() {
                     var me = this;
                     if(this.needs_render){
                         this.renderer.render(this.scene, this.camera);
                         this.axisHelper.rotation.setFromRotationMatrix(this.followingCam.matrixWorldInverse);
                         this.cubeMesh.rotation.setFromRotationMatrix(this.followingCam.matrixWorldInverse);
                         requestAnimationFrame(function() {
                             me.doAnimate()
                         });
                     }
                 },

                 buildScene: function() {
                     var thisDom = this.getEl().dom;

                     this.scene = new THREE.Scene();
		             var material = new THREE.MeshBasicMaterial({
			             color : 0xffff00
		             });

                     this.cube = new THREE.BoxGeometry(0.25, 0.25, 0.25);
		             this.cubeMesh = new THREE.Mesh(this.cube, material);
		             this.scene.add(this.cubeMesh);

                     this.axisHelper = new THREE.AxisHelper( 1 );
                     this.scene.add( this.axisHelper );
                     this.camera = new THREE.OrthographicCamera( -this.getWidth()/100, this.getWidth()/100,
                                                                 this.getHeight()/100, -this.getHeight()/100, 1, 20 );
                     //this.setClearColor(0xC0C0C0, 0.0);
                     //this.setClearColor(0xC0C0C0,1.0);
                     this.renderer.setClearColor(0x808080,0.001);

                     this.camera.position.set(0,0,10);
                 }

                }],
        listeners : {
            afterlayout: function(){
                var canvas = this.queryById('axis_panel');
                canvas.followingCam = me.volume.canvas3D.camera;
                canvas.doAnimate();
                me.parentdiv = this.getEl().dom;
                me.volume.addFade(this);
                me.volume.canvas3D.on({
                    scope: me,
                    mousedown: function(){
                        canvas.rerender();
                    },
                    //mousemove: function(){},
                    mouseup: function(){
                        canvas.stoprender();
                    },
                    //render: me.updatePosition
                });

            }
        }
	});

    this.volume.on('loaded', function () {
        //var me = this;
        //var canvas = this.queryById('axis_panel');
        //me.updateImage();


    });
};


/*******************************************************************************
Temp home for the axis tool
*******************************************************************************/

function VolSpinnerTool (volume){
    this.name = 'spinner';
    this.base = renderingTool;
    this.base (volume, null);
}

VolSpinnerTool.prototype = new renderingTool();

VolSpinnerTool.prototype.addButton = function () {
    //blank since we don't actually add anything
};

VolSpinnerTool.prototype.start = function () {
    this.go = true;
    var canvas = this.spinner.queryById('spinner_panel');
    canvas.needs_render = true;
    this.spinner.show();
};


VolSpinnerTool.prototype.stop = function () {
    this.go = false;
    var canvas = this.spinner.queryById('spinner_panel');
    canvas.needs_render = false;
    this.spinner.hide();
};


VolSpinnerTool.prototype.initControls = function () {
    var me = this;
    var thisDom = this.volume.mainView.getEl().dom;
    this.go = false;
    this.small = 1;
    this.spinner = Ext.create('Ext.panel.Panel', {
		collapsible : false,
		header : false,
		renderTo : thisDom,
        layout : 'fit',
		cls : 'vol-spinner',
        items: [{xtype: 'threejs_panel',
                 itemId: 'spinner_panel',
                 handlers :{
                     mousedown: function(){
                         if(me.small==0){
                             me.small = 1;
                             me.spinner.setSize(24,24);
                         }
                         else{
                             me.small = 0;
                             me.spinner.setSize(72,72);
                         }

                     }
                 },

                 doAnimate : function() {
                     if(this.uniforms.small)
                         this.uniforms.small.value = me.small;

                     if(me.go){
                         this.renderer.render(this.scene, this.camera);
                         this.t += 0.01;
                         this.uniforms.t.value = this.t;
                     }
                     if(this.needs_render && me.go){
                         var canvas = this;
                         requestAnimationFrame(function() {
                             canvas.doAnimate()
                         });
                     }
                 },

                 buildScene: function() {
                     var thisDom = this.getEl().dom;
                     this.t = 0;
                     this.scene = new THREE.Scene();
		             var material = new THREE.MeshBasicMaterial({
			             color : 0xffff00
		             });


                     this.camera = new THREE.OrthographicCamera( -0.5, 0.5,
                                                                  0.5,-0.5, 1, 20 );
                     //this.setClearColor(0xC0C0C0, 0.0);
                     //this.setClearColor(0xC0C0C0,1.0);

		             var pw = this.getPixelWidth();
		             var ph = this.getPixelHeight();
                     var frag = [
                         'uniform int small;',
		                 'uniform float t;',
                         'uniform vec2 ires;',
                         '#define M_PI 3.14159265358979323846',
		                 'void main() {',
                         'if(small == 1){',
                         'gl_FragColor = vec4(vec3(0.5 + 0.5*cos(4.0*t), 0.0, 0.0), 1.0);',
                         'return;',
                         '}',
	                     'vec2 uv = gl_FragCoord.xy / ires.xy;',
                         'vec2 p = uv - 0.5 + 0.05*vec2(cos(t), sin(t));',
	                     'float a = atan(p.x, p.y);',
                         'float l = length(p);',
   	                     'float ct  = cos(t);',
                         'float ct0 = sin(t);',
                         'float rady = cos(1.5*log(1.0*l) + 0.1*t)*sin(1.5*a + 1.0*ct*log(l));',
                         'float radx = sin(1.5*log(1.0*l) + 0.1*t)*cos(1.5*a + 1.0*ct*log(l));',
                         'float a2 = atan(radx, rady);',
                         'float l2 = length(vec2(radx, rady));',
                         'float rad2 = sin(log(1.0*l2)+0.1*t)*cos(1.0*a2 - 8.0*l*ct0*log(0.5*l2));',
                         'float but = l - 0.5;',
                         'gl_FragColor = vec4(vec3(rad2*rad2),1.0-l2);',

                         '}'
	                 ].join('\n');

	                 var vert = [
		                 'void main() {',
		                 '  gl_Position = projectionMatrix * modelViewMatrix * vec4( position, 1.0 );',
		                 '}'
	                 ].join('\n');

		             this.uniforms = {
			             small : {
				             type : "i",
				             value : me.small
			             },
			             t : {
				             type : "f",
				             value : this.t
			             },
                         ires : {
				             type : "v2",
				             value : new THREE.Vector2(pw,ph)
			             }
		             };

		             var shader = new THREE.ShaderMaterial({
				         uniforms : this.uniforms,
				         vertexShader : vert,
				         fragmentShader : frag,
				         //side : THREE.DoubleSide,
			         });
                     this.plane = new THREE.Mesh(new THREE.PlaneBufferGeometry(1, 1, 8, 8), shader);
                     this.scene.add(this.plane);
                     var sphereGeometry = new THREE.SphereGeometry(0.05);

	                 //var sphereMaterial = new THREE.MeshBasicMaterial( { color: 0x1A1A1A, shading: THREE.FlatShading } );
	                 this.spheres = [];
                     this.colors = [];

                     this.renderer.setClearColor(0x808080,0.001);

                     this.camera.position.set(0,0,10);
                 }

                }],
        listeners : {
            afterlayout: function(){
                var canvas = this.queryById('spinner_panel');
                var pw = canvas.getPixelWidth();
		        var ph = canvas.getPixelHeight();
                canvas.uniforms.ires.value.x = pw;
                canvas.uniforms.ires.value.y = ph;
                canvas.doAnimate();
                me.parentdiv = this.getEl().dom;
                me.volume.addFade(this);
                me.volume.canvas3D.on({
                    scope: me,
                    mousedown: function(){
                        canvas.rerender();
                    },
                    //mousemove: function(){},
                    mouseup: function(){
                        canvas.stoprender();
                    },
                    //render: me.updatePosition
                });
            }
        }
	});

    this.volume.on({
        loadinitiated: function() {
            me.start();
        },

        loadcomplete: function(){
            me.stop();
        },
        scope: me,
    });
};


function qualityTool(volume, cls) {
	//renderingTool.call(this, volume);
    this.name = 'render_quality';
/*


    this.label = 'save png';
    //this.cls = 'downloadButton';
*/
	this.base = renderingTool;
    this.base(volume, this.cls);
};

qualityTool.prototype = new renderingTool();


qualityTool.prototype.init = function(){
    //override the init function,
    var me = this;
    // all we need is the button which has a menu
    this.createButton();
};

qualityTool.prototype.addButton = function () {
    //we override where we'll add this button, we send it to the settings menu, currently called toolMenu
    this.volume.toolMenu.add(this.button);
};

qualityTool.prototype.addUniforms = function(){
};

qualityTool.prototype.loadPreferences = function(path, resource_uniq) {
    var quality = BQ.Preferences.get(resource_uniq, path),
        idx = this.button.getStore().find('text', quality),
        rcd = this.button.getStore().getAt(idx);
    this.button.setValue(rcd.get('value'));
    this.setQuality();
};

qualityTool.prototype.setQuality = function() {
    var val = this.button.getValue();
    var minVal = val/4;
    this.volume.minSampleRate = minVal;
    this.volume.maxSteps = val;
    this.volume.volumeObject.maxSteps = val;
    this.volume.setMaxSampleRate(val);
};

qualityTool.prototype.createButton = function(){
    var me = this;

    var options = Ext.create('Ext.data.Store', {
		fields : ['value', 'text'],
		data : [
            {"value" : 16,   "text" : "minimal"},
            {"value" : 32,  "text" : "low"},
            {"value" : 256,  "text" : "medium"},
            {"value" : 1024, "text" : "high"},
        ]
	});
    /*
    this.button = this.volume.createCombo('rendering quality', options, 'medium', this, this.quality, 'quality-combo') ;
    */
    this.button = Ext.create('Ext.form.ComboBox',{

		fieldLabel : 'rendering quality',
		store : options,
		queryMode : 'local',
		displayField : 'text',
		valueField : 'value',
		forceSelection : true,
		editable : false,
		//value : def,

		listeners : {
			scope : this,
			'select' : this.setQuality,
		},

	});

    this.button.tooltip = 'set maximum rendering quality';
};


function autoRotateTool(volume, cls) {
	//renderingTool.call(this, volume);

    this.name = 'autoRotate';
/*
    this.label = 'save png';
    //this.cls = 'downloadButton';
*/
	this.base = renderingTool;
    this.base(volume, this.cls);
};

autoRotateTool.prototype = new renderingTool();

autoRotateTool.prototype.init = function(){
    //override the init function,
    var me = this;
    // all we need is the button which has a menu
    this.createButton();
};

autoRotateTool.prototype.addButton = function () {
    this.volume.toolMenu.add(this.button);
};

autoRotateTool.prototype.createButton = function(){
    var me = this;

    this.button = Ext.create('Ext.form.field.Checkbox', {
        boxLabel : 'Autorotate Camera',
        cls : 'volume-button',
        checked: false,
		handler : function (item, checked) {
			me.volume.setAutoRotate(checked);
		},
        scope : me,
    });

    this.button.tooltip = 'Allows the camera to automatically rotate after manipulation';
};



function loseContextTool(volume, cls) {
	//renderingTool.call(this, volume);

    this.name = 'autoRotate';
/*
    this.label = 'save png';
    //this.cls = 'downloadButton';
*/
	this.base = renderingTool;
    this.base(volume, this.cls);
};

loseContextTool.prototype = new renderingTool();

loseContextTool.prototype.init = function(){
    //override the init function,
    var me = this;
    // all we need is the button which has a menu
    this.createButton();
};

loseContextTool.prototype.addButton = function () {
    this.volume.toolMenu.add(this.button);
};

loseContextTool.prototype.createButton = function(){
    var me = this;

    this.button = Ext.create('Ext.Button', {
        width : 36,
        height : 36,
        cls : 'volume-button',
		handler : function (item, checked) {
            me.volume.canvas3D.loseContext();
		},
        scope : me,
    });

    this.button.tooltip = 'kaboom goes the dynamite';
};


function showGraphTool(volume, cls) {
	//renderingTool.call(this, volume);

    this.name = 'autoRotate';
/*
    this.label = 'save png';
    //this.cls = 'downloadButton';
*/
	this.base = renderingTool;
    this.base(volume, this.cls);
};

showGraphTool.prototype = new renderingTool();

showGraphTool.prototype.init = function(){
    //override the init function,
    var me = this;
    // all we need is the button which has a menu
    this.createButton();
};

showGraphTool.prototype.addButton = function () {
    this.volume.toolMenu.add(this.button);
};

showGraphTool.prototype.createButton = function(){
    var me = this;

    this.button = Ext.create('Ext.Button', {
        width : 36,
        height : 36,
        cls : 'volume-button',
		handler : function (item, checked) {
            Ext.create('BQ.viewer.graphviewer.Dialog', {
                title : 'gl info',
                height : 500,
                width : 960,
                layout : 'fit',
                resource: this.volume.resource,
            }).show();
		},
        scope : me,
    });

    this.button.tooltip = 'graph viewer temp';
};
