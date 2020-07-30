/*******************************************************************************
bioWeb3D - a WebGL based volumue renderer component for the Bisque system
@author John Delaney

Configurations:
resource   - url string or bqimage (required)
phys       - image phys BQImagePhys (preferred)
preferences - BQPpreferences object (preferred)

Events:
loaded     - event fired when the viewer is loaded

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

Ext.require([
		'Ext.chart.*',
		'Ext.data.*',
		'Ext.Window',
		'BQ.viewer.Volume.ThreejsPanel',
		'Ext.tip.QuickTipManager',
		'Ext.menu.*',
		'Ext.form.field.ComboBox',
		'Ext.layout.container.Table',
		'Ext.layout.container.Accordion',
		'Ext.container.ButtonGroup',
		'Ext.fx.target.Sprite',
	]);

Ext.define('BQ.viewer.Volume.volumeScene', {
	mixins : {
		observable : 'Ext.util.Observable'
	},

	alias : 'widget.volumeScene',

	constructor : function (config) {
		// The Observable constructor copies all of the properties of `config` on
		// to `this` using Ext.apply. Further, the `listeners` property is
		// processed to add listeners.
		//
		this.mixins.observable.constructor.call(this, config);

		this.shaders = {};
		this.materials = {};
		this.uniforms = {};
        /*
		this.scene = new THREE.Scene();
		this.sceneData = new THREE.Scene();
		this.sceneDataColor = new THREE.Scene();

		var material = new THREE.MeshBasicMaterial({
				color : 0xffff00
		});

		this.cube = new THREE.CubeGeometry(1.0, 1.0, 1.0);
		this.cubeMesh = new THREE.Mesh(this.cube, material);
		this.scene.add(this.cubeMesh);

		this.light = new THREE.PointLight(0xFFFFFF, 1, 100);
		this.scene.add(this.light);
		this.canvas3D.scene = this.scene;

		this.canvas3D.scene = this.scene;

        this.oldScale = new THREE.Vector3(0.5, 0.5, 0.5);
		this.currentScale = new THREE.Vector3(0.5, 0.5, 0.5);
        */
	},

	initComponent : function () {},

	initUniform : function (name, type, value) {
		this.uniforms[name] = {
			type : type,
			value : value
		};
		this.canvas3D.rerender();
	},

	getMaterial : function (index) {
		return this.materials[index];
	},


	setUniform : function (name, value, reset, timeOut) {
		//console.log('bef',reset);
		if (typeof(reset) === 'undefined')
			reset = true;

        if(!this.uniforms[name]) return;
        var me = this;

        var timeFunc = function(){
            this.uniforms[name].value = value;
            this.fireEvent('setuniform', this);
            me.timeout = null;
        };
        if(this.timeout) clearTimeout(this.timeout);
        this.timeout = setTimeout(timeFunc, 50);

	},

	setUniformNoRerender : function (name, value, reset, timeOut) {
		if (typeof(reset) === 'undefined')
			reset = true;
        if(!this.uniforms[name]) return;
		this.uniforms[name].value = value;
	},


    setConfigurable : function(materialID, shaderType, config){
        var shader = this.materials[materialID][shaderType];
        shader.set(config);
        var fragmentKey = shader.getID();
		if (!this.shaders[fragmentKey]){
		    this.shaders[fragmentKey] = shader.getSource();
        };
        var threeShader = this.materials[materialID].threeShader;
		var type = shaderType + 'Shader';
        threeShader[type] = this.shaders[fragmentKey];
        threeShader.needsUpdate = true;
        this.updateMaterials();
        this.canvas3D.rerender();
    },

	constructMaterial : function (material) {

		//if (material.built === true)
		//	return true;

		var vertexKey   = material.vertex.getID();
		var fragmentKey = material.fragment.getID();
        this.shaders[vertexKey]   = material.vertex.getSource();
		this.shaders[fragmentKey] = material.fragment.getSource();

		material.threeShader.vertexShader = this.shaders[vertexKey];
		material.threeShader.fragmentShader = this.shaders[fragmentKey];
	},

	updateMaterials : function () {
		var me = this;
		for (var prop in this.materials) {
			this.constructMaterial(this.materials[prop]);
		}
	},
/*
	fetchFragments : function (url, storeId, manip) {
		var me = this;
		var manipulate = manip;
		var id = storeId;
		Ext.Ajax.request({
			url : url,
			callback : function (opts, succsess, response) {
				if (response.status >= 400)
					BQ.ui.error(response.responseText);
				else {
					var fetchedText = response.responseText;
					me.shaders[id] = fetchedText;
					if (manipulate) {
						var newText = manipulate(fetchedText);
						me.shaders[id] = newText;
					}
					me.updateMaterials();
				}
			},
			scope : this,
			disableCaching : false,
			listeners : {
				scope : this,
				beforerequest : function () {
					this.setLoading('Loading images...');
				},
				requestcomplete : function () {
					this.setLoading(false);
				},x
				requestexception : function () {
					this.setLoading(false);
				},
			},
		});
	},

	initFragment : function (url, id, manipulate) {

		if (!this.shaders[url]) {
			this.shaders[url] = ''; //placeholder so we don't fetch this fragment many times
			this.fetchFragments(url, id, manipulate);
		} else {
			if (manipulate) {
				var shader = this.shaders[url];
				var newText = manipulate(shader);
				this.shaders[id] = newText;
				this.updateMaterials();
			}
		}
	},
*/
    initFragmentByConfig : function (config, id) {
        this.shaders[id] = shaderConfig().rayCastShader(config);
        this.updateMaterials();
	},

	initMaterial : function (config) {
        var me = this;
		var name = config.name;
		var vertUrl = config.vertex.url;
		var fragUrl = config.fragment.url;
		var vertId = vertUrl;
		var fragId = fragUrl;
		var uniforms = config.uniforms ? config.uniforms : this.uniforms;

		if (config.vertex.id)
			vertId = config.vertex.id;
		if (config.fragment.id)
			fragId = config.fragment.id;

		var threeMaterial = new THREE.ShaderMaterial({
				uniforms : uniforms,
				vertexShader : "",
				fragmentShader : "",
				side : THREE.DoubleSide,
		});

		var newMaterial = {
			name : name,
			vertexId : vertId,
			fragmentId : fragId,
			built : false,
            shader : {},
			threeShader : threeMaterial,
			buildFunc : this.defaultBuildFunc,
		};
		this.materials[name] = newMaterial;
        /*
		this.initFragment(vertUrl, vertId, config.vertex.manipulate);
        */
        //init the fragment shader,
        var shaderTypes = ["fragment", "vertex"];
        for(var i = 0; i < shaderTypes.length; i++){
            var type = shaderTypes[i];

            if(config[type].url){ //here we hard code getting shader by URL for convenience
                var newConfig = {
			        url : config[type].url,
                    loader : me,
                    onloaded: function(){
                        me.updateMaterials();
                    }
                }
                var newShader = new UrlShader(newConfig);
                newMaterial[type] = newShader;
                this.shaders[newShader.getID()] = newShader.getSource();

            }
            else if(config[type].config){
                var ctor   = config[type].ctor;
                var fconfig = config[type].config;
                var newShader = new ctor(fconfig);
                newMaterial[type] = newShader;
                this.shaders[newShader.getID()] = newShader.getSource();
            }
        };

	},

	loadMaterial : function (object, name) {
		object.material = this.materials[name].threeShader;

        this.fireEvent('materialloaded', this);
		//this.canvas3D.rerender();
	}

});


function volumeObject() {
    this.uniforms = {};
};

volumeObject.prototype.initGeometry = function(){

    this.sceneData = new THREE.Scene();

    //------------------------------------------------------------------------
    // initialize the main rendering cube
    //------------------------------------------------------------------------

    this.cube = new THREE.BoxGeometry(1.0, 1.0, 1.0);
	this.cubeMesh = new THREE.Mesh(this.cube);

    //------------------------------------------------------------------------
    // Initialize the background for depth registration
    //------------------------------------------------------------------------
	var backGroundGeometry = new THREE.BoxGeometry(1.0, 1.0, 1.0);
    this.backGround = new THREE.Mesh(backGroundGeometry, this.backGroundShaderMaterial);
	//this.backGroundShaderMaterial.needsUpdate = true;
	//backGroundGeometry.buffersNeedUpdate = true;
	//backGroundGeometry.uvsNeedUpdate = true;
    this.sceneData.add(this.backGround);
};

volumeObject.prototype.initBuffers = function(){
	this.depthBuffer
		= new THREE.WebGLRenderTarget(this.canvas.getPixelWidth(), this.canvas.getPixelHeight(), {
			minFilter : THREE.LinearFilter,
			magFilter : THREE.NearestFilter,
			format : THREE.RGBAFormat
		});
	this.colorBuffer
		= new THREE.WebGLRenderTarget(this.canvas.getPixelWidth(), this.canvas.getPixelHeight(), {
			minFilter : THREE.LinearFilter,
			magFilter : THREE.NearestFilter,
			format : THREE.RGBAFormat
		});

	this.passBuffer
		= new THREE.WebGLRenderTarget(this.canvas.getPixelWidth(), this.canvas.getPixelHeight(), {
			minFilter : THREE.LinearFilter,
			magFilter : THREE.NearestFilter,
			format : THREE.RGBAFormat
		});

    this.initUniform('BACKGROUND_DEPTH', "t", this.depthBuffer);
	this.initUniform('BACKGROUND_COLOR', "t", this.colorBuffer);
};

volumeObject.prototype.initMaterials = function(){
    var me = this;
    this.maxSteps = 4096;
    //this.initUniforms();

	//-------------------------------------
	//Platform and browser version checking
	//-------------------------------------

	var OSX, fragUrl, usePow;
	if (Ext.isWindows) {
		if (Ext.isChrome) {
			if (Ext.chromeVersion < 37)
				usePow = false;
            else
                usePow = true;

		} else
			usePow = true;
	} else
		usePow = true;
    if(Ext.isMac)
        OSX = true;
        this.shaderConfig = {
            phong: false,
            deep: false,
            deepType: 'deep_shading',
            transfer: false,
            pow: true,
            highlight: false,
            //gradientType: 'sobel',
            //gradientType: 'directional',
            gradientType: 'finite_difference',
            maxSteps: this.maxSteps,
            usePow: usePow,
            OSX: OSX,
    };
/*
    this.shaderConfig = {
        lighting: {
            phong: false,
            deep: false,
            deepType: 'deep_shading'
        },
        transfer: false,
        pow: true,
        highlight: false,
        //gradientType: 'sobel',
        //gradientType: 'directional',
        gradientType: 'finite_difference',
        maxSteps: this.maxSteps,
        usePow: usePow,
        OSX: OSX,
    };
*/
	this.shaderManager.initMaterial({
		name : 'default_1',
		vertex : {
            ctor : UrlShader,
            config : {
				url : "/core/js/volume/shaders/rayCast.vs",
                loader: this.sceneVolume,
                onloaded: function(){
                    me.shaderManager.updateMaterials();
                }
            }
		},

		fragment : {
            ctor: VolumeShader,
			config: this.shaderConfig,
            //url : fragUrl,
		},
        uniforms: this.uniforms,
	});

    //------------------------------------------------------------------------
    // initialize the internal object compositing
    //------------------------------------------------------------------------

    var spriteTex = THREE.ImageUtils.loadTexture('/core/js/volume/icons/dot.png');
	this.near = 0.001;
    this.far = 20.0;
    this.useColor = 0;
	this.pointShaderMaterial = new THREE.ShaderMaterial({
		uniforms : {
			tex1 : {
				type : "t",
				value : spriteTex
			},
			zoom : {
				type : 'f',
				value : 100.0
			},
			near : {
				type : 'f',
				value : this.near
			},
			far : {
				type : 'f',
				value : this.far
			},
			USE_COLOR : {
				type : 'i',
				value : this.useColor
			}
		},
		attributes : {
			alpha : {
				type : 'f',
				value : null
			},
		},
		vertexShader : new DepthShader({
            poly: false,
            type: 'vertex',
        }).getSource(),
		fragmentShader : new DepthShader({
            poly: false,
            type: 'fragment',
        }).getSource(),
		side : THREE.DoubleSide,
		alphaTest : 0.5,
		transparent : true
	});

	this.polyShaderMaterial = new THREE.ShaderMaterial({
		uniforms : {
			near         : { type : 'f',value : this.near},
			far          : { type : 'f', value : this.far},
			CLIP_NEAR         : { type : 'f',value : this.near},
			CLIP_FAR          : { type : 'f', value : this.far},
            opacity : { type : 'f', value : 0.85},
            USE_COLOR    : { type : 'i', value : this.useColor}
		},
        //opacity: 1.0,
		vertexShader : new DepthShader({
            poly: true,
            type: 'vertex',
        }).getSource(),
		fragmentShader : new DepthShader({
            poly: true,
            type: 'fragment',
        }).getSource(),
		side : THREE.DoubleSide,

	});


	this.backGroundShaderMaterial = new THREE.ShaderMaterial({
		uniforms : {
			near : {
				type : 'f',
				value : this.near
			},
			far : {
				type : 'f',
				value : this.far
			},
			USE_COLOR : {
				type : 'i',
				value : this.useColor
			}
		},
        vertexShader : new DepthShader({
            poly: true,
            type: 'vertex',
        }).getSource(),
		fragmentShader : new DepthShader({
            poly: true,
            type: 'fragment',
            //back: true,
        }).getSource(),
		side : THREE.BackSide,
		//transparent: true
	});
    this.backGround.material = this.backGroundShaderMaterial;

};

volumeObject.prototype.init = function () {
    var me = this;

    //this.raycaster = new THREE.Raycaster();
	//this.raycaster.params.PointCloud.threshold = 0.005;
	/*
	  var sphereGeometry = new THREE.SphereGeometry( 0.01, 32, 32 );
	  var sphereMaterial = new THREE.MeshBasicMaterial( { color: 0xff0000, shading: THREE.FlatShading } );
	  this.sphere =  new THREE.Mesh( sphereGeometry, backGroundShaderMaterial );
	  this.sceneVolume.sceneData.add( this.sphere );
	*///var backGroundGeometry = new THREE.PlaneGeometry(10,10);
};

volumeObject.prototype.set = function(key, value){
    this[key] = value;
};

volumeObject.prototype.resetSampleRate = function () {
    //console.trace();
    this.steps = this.maxSteps/8;
},

volumeObject.prototype.setSampleRate = function (rate) {
    if(typeof(qual) === 'undefined') qual = 4096;
    this.steps = rate;
},

volumeObject.prototype.setMaxSampleRate = function (qual) {
    if(typeof(qual) === 'undefined') qual = 4096;
    this.maxSteps = qual;
    this.shaderConfig.maxSteps = qual;
    this.setUniform('maxSteps', qual);
    /*
    this.shaderManager.setConfigurable("default_1",
                                       "fragment",
                                       this.shaderConfig);
    */
},

volumeObject.prototype.removeSet = function (set, scene) {

	for (var item in set) {
		if (!item)
			continue;

		var curMesh = set[item].mesh;
		if (curMesh){
			scene.remove(curMesh); // remove current point set
            //curMesh.visible = false;
        }
	}
};

volumeObject.prototype.addMeshObject = function (object, clone) {
    if(clone) object = object.clone();
    object.material = this.polyShaderMaterial;
    this.sceneData.add(object);
    return object;
};

volumeObject.prototype.addSet = function (set, scene) {
	for (var item in set) {
		if (!item)
			continue;
		var curMesh = set[item].mesh;
		if (curMesh) {
			scene.add(curMesh); // remove current point set
			if (this.state === 1)
				curMesh.visible = true;
			else
				curMesh.visible = false;
		}
	}
};

volumeObject.prototype.setScale = function(scale){
    this.backGround.scale.copy(new THREE.Vector3(2.0*scale.x,
                                                 2.0*scale.y,
                                                 2.0*scale.z));

    this.scale = scale;
	this.setUniform('BOX_SIZE', scale);

	this.currentScale = scale.clone();
    this.cubeMesh.scale.copy(new THREE.Vector3(2.0*scale.x,
                                               2.0*scale.y,
                                               2.0*scale.z));
	this.canvas.rerender();
	//this.fireEvent('scale', scale,  this);
};

volumeObject.prototype.setUniform  = function (name, value, reset, timeOut) {
    this.resetSampleRate();
	if (typeof(reset) === 'undefined')
		reset = true;

    if(typeof(this.uniforms[name]) !== 'undefined'){
        var me = this;
        me.uniforms[name].value = value;
        if(this.uniformTimer) clearTimeout(this.uniformTimer);
        this.uniformTimer = setTimeout(function(){
            me.canvas.rerender();
        }, 50);
    }

    if(typeof(this.shaderConfig[name]) !== 'undefined'){
	    this.shaderConfig[name] = value;
        this.shaderManager.setConfigurable("default_1",
                                          "fragment",
                                          this.shaderConfig);
        this.canvas.rerender();
    }
    //this.fireEvent('setuniform', this);
},

volumeObject.prototype.setUniformNoRerender = function (name, value, reset, timeOut) {
	if (typeof(reset) === 'undefined')
		reset = true;
    if(!this.uniforms[name]) return;
	this.uniforms[name].value = value;
},

volumeObject.prototype.initUniform = function (name, type, value) {
	this.uniforms[name] = {
		type : type,
		value : value
	};
	this.canvas.rerender();
},

volumeObject.prototype.initUniforms = function (uniforms) {
    var me = this;
    uniforms.forEach(function(val,i,a){
        me.initUniform(val.uniform, val.type, val.value);
    });
},

volumeObject.prototype.initResolution = function(canvas){
    var res = new THREE.Vector2(canvas.getPixelWidth(), canvas.getPixelHeight());
	this.initUniform('iResolution', "v2", res);
};

volumeObject.prototype.setResolution = function(){
    var res = new THREE.Vector2(this.canvas.getPixelWidth(), this.canvas.getPixelHeight());
	this.setUniform('iResolution',  res);
    	this.depthBuffer
		= new THREE.WebGLRenderTarget(this.canvas.getPixelWidth(), this.canvas.getPixelWidth(), {
			minFilter : THREE.LinearFilter,
			magFilter : THREE.NearestFilter,
			format : THREE.RGBAFormat
		});
	this.colorBuffer
		= new THREE.WebGLRenderTarget(this.canvas.getPixelWidth(), this.canvas.getPixelWidth(), {
			minFilter : THREE.LinearFilter,
			magFilter : THREE.NearestFilter,
			format : THREE.RGBAFormat
		});

	this.passBuffer
		= new THREE.WebGLRenderTarget(this.canvas.getPixelWidth(), this.canvas.getPixelHeight(), {
			minFilter : THREE.LinearFilter,
			magFilter : THREE.NearestFilter,
			format : THREE.RGBAFormat
		});
};

volumeObject.prototype.loadMaterial = function (name) {
	this.shaderManager.loadMaterial(this.cubeMesh, name);
    this.canvas.rerender();
},

volumeObject.prototype.onAnimate = function () {

	if(!this.loaded) return;
    //if(!this.volume.sceneData) return;
    this.uniforms['BREAK_STEPS'].value = this.steps;

    var panel = this.volume;
	//move this to background plug-in
	var camPos = this.canvas.camera.position;
	//this.currentSet.points.sortParticles(camPos);
	this.canvas.renderer.clearTarget(this.accumBuffer0,
				                     true, true, true);
	var buffer = this.accumBuffer0;
	var bufferColor = this.accumBuffer1;

	this.pointShaderMaterial.uniforms.USE_COLOR.value = 0;
	this.polyShaderMaterial.uniforms.USE_COLOR.value = 0;
    this.backGroundShaderMaterial.uniforms.USE_COLOR.value = 0;

	this.polyShaderMaterial.transparent = false;

    this.canvas.renderer.render(this.sceneData,
				                this.canvas.camera,
				                this.depthBuffer);

	this.pointShaderMaterial.transparent = true;
	this.polyShaderMaterial.transparent = true;

    this.pointShaderMaterial.uniforms.USE_COLOR.value = 1;
	this.polyShaderMaterial.uniforms.USE_COLOR.value = 1;
	this.backGroundShaderMaterial.uniforms.USE_COLOR.value = 1;
	this.canvas.renderer.render(this.sceneData,
				                this.canvas.camera,
				                this.colorBuffer);


	this.setUniformNoRerender('BACKGROUND_DEPTH', this.depthBuffer, false);
	this.setUniformNoRerender('BACKGROUND_COLOR', this.colorBuffer, false);
    this.setUniformNoRerender('PASS', 0, false);
	this.canvas.renderer.render(this.canvas.scene,
				                this.canvas.camera,
				                this.passBuffer);

    this.setUniformNoRerender('BACKGROUND_COLOR', this.passBuffer, false);
    this.setUniformNoRerender('PASS', 1, false);
};

//-----------------------------------------------------------------------------------------------------------
//
//
//-----------------------------------------------------------------------------------------------------------

Ext.define('BQ.viewer.Volume.Panel', {
	alias : 'widget.bq_volume_panel',
	extend : 'Ext.panel.Panel',
	border : 0,
	cls : 'bq-three-container',
	layout : 'fit',

	initComponent : function () {
		this.update_delay_ms = 200;

		this.preMultiplyAlpha = false;
		this.currentTime = 0;
        this.maxSteps    = 64;
        this.numChannels = 3;
        this.mousedown = false;
        var me = this;

        this.cubeMesh; //initialize the

        this.minSampleRate = 32;
        this.autoRotateSampleRate = 32;
        var mousedown = function(event){
            if(event.button >= 0){
                me.mousedown = true;
                me.volumeObject.resetSampleRate();
                me.rerender();
                //me.rerender();
            }
        };
        var mousemove = function(event){
            if(me.mousedown){
                //console.log('move');
                me.volumeObject.resetSampleRate();
                me.rerender();
                //me.rerender();
            }
        };

        var mouseup = function(event){
            me.mousedown = false;
            me.rerender();
        };

        var mousewheel = function(event){
            if(event.button >= 0){
                me.mousedown = true;
                me.rerender();
            }

            var distFromCenter = me.canvas3D.camera.position.length();
			var newSliderVal = Math.floor((10.0 - distFromCenter) * 10.0);
			var curSliderVal = me.zoomSlider.getValue(0);
			if (newSliderVal != curSliderVal) {
				me.zoomSlider.setValue(newSliderVal);
			}
        };

        //-------------------------------------
        //create the threejs canvas
        //-------------------------------------
        this.volumeObject = new volumeObject();

        this.canvas3D = Ext.create('BQ.viewer.Volume.ThreejsPanel', {
		    itemId : 'canvas3D',
            listeners: {
                scope : me,
                resize: this.onresize,

                glcontextlost: function(event){
                    me.fireEvent('glcontextlost', event);
                },
                glcontextrestored: function(event){
                    me.fireEvent('glcontextrestored', event);
                }
            },

            handlers: {
                scope : me,
                mousemove : mousemove,
                mousedown : mousedown,
                mousewheel: mousewheel,
                mouseup : mouseup,
                mousewheelup : mouseup,
            },

            buildScene: function() {
		        me.scene = new THREE.Scene();
		        //this.scene = me.scene;
                me.sceneData = new THREE.Scene();
		        me.sceneDataColor = new THREE.Scene();

		        var material = new THREE.MeshBasicMaterial({
				    color : 0xffff00
		        });

		        me.cube = new THREE.BoxGeometry(1.0, 1.0, 1.0);
		        me.cubeMesh = new THREE.Mesh(me.cube, material);

                me.volumeObject.initGeometry();
                me.volumeObject.initMaterials();
                me.scene.add(me.volumeObject.cubeMesh);

		        //me.scene.add(me.cubeMesh);

		        me.light = new THREE.PointLight(0xFFFFFF, 1, 100);
		        me.scene.add(me.light);
		        me.canvas3D.scene = me.scene;
                me.volumeObject.maxSteps = me.minSampleRate;
		        me.oldScale = new THREE.Vector3(0.5, 0.5, 0.5);
		        me.currentScale = new THREE.Vector3(0.5, 0.5, 0.5);
                this.renderer.setClearColor(0x434343,0.000);
            }
		});
        this.canvas3D.animate_funcs[1] = callback(this.volumeObject, this.volumeObject.onAnimate);
		this.canvas3D.animate_funcs[2] = callback(this, this.onAnimate);


        //-------------------------------------
        //create the shader database
        //-------------------------------------

        this.sceneVolume = new BQ.viewer.Volume.volumeScene({
            canvas3D : this.canvas3D,
            listeners: {
                materialloaded : function(){
                    //me.volumeObject.maxSteps = me.minSampleRate;
                    me.rerender();
                },
                setuniform     : function(){
                    //me.volumeObject.maxSteps = me.minSampleRate;
                    me.rerender();
                },
                scope: this
            },
		});


        me.volumeObject.set('canvas', this.canvas3D);
        me.volumeObject.set('shaderManager', this.sceneVolume);

		//-------------------------------------
		//Platform and browser version checking
		//-------------------------------------

		var OSX, fragUrl, usePow;
		if (Ext.isWindows) {
			if (Ext.isChrome) {
				if (Ext.chromeVersion < 37)
					usePow = false;
                else
                	usePow = true;

			} else
				usePow = true;
		} else
				usePow = true;
        if(Ext.isMac)
            OSX = true;
        this.shaderConfig = {
            lighting: {
                phong: false,
                deep: false,
                deepType: 'deep_shading'
            },
            transfer: false,
            pow: true,
            highlight: false,
            gradientType: 'finite_difference',
            maxSteps: this.maxSteps,
            usePow: usePow,
            OSX: OSX,
        };

		this.sceneVolume.initMaterial({
			name : 'default',
			vertex : {
                ctor : UrlShader,
                config : {
				    url : "/core/js/volume/shaders/rayCast.vs",
                    loader: this.sceneVolume,
                    onloaded: function(){
                        me.sceneVolume.updateMaterials();
                    }
                }
			},

			fragment : {
                ctor: VolumeShader,
				config: this.shaderConfig,
                //url : fragUrl,
			}
		});


        //---------------------------------------------------------
        //register plugins for communicating with the image server
        //---------------------------------------------------------

		this.plug_ins = [new VolumeTime(this), new VolumeAtlas(this),
			new VolumeDisplay(this), new VolumeFormat(this)];


        //-------------------------------------
        //register non-exjs-standard screen widgets
        //-------------------------------------
        this.mainView = Ext.create('Ext.container.Container', {
            layout: 'fit',
            autoEl : {
				tag : 'div',
			},
            items: [{
                xtype: 'component',
                itemId: 'canvasBack',
                autoEl : {
                    tag: 'div',
                    cls: 'threejsBack'
                },
            }, this.canvas3D,{
			    xtype : 'component',
			    itemId : 'button-fullscreen-vol',
			    autoEl : {
				    tag : 'span',
				    cls : 'control fullscreen',
			    },
			    listeners : {
				    scope : this,
				    click : {
					    element : 'el', //bind to the underlying el property on the panel
					    fn : this.onFullScreenClick,
				    },
			    },
		    }, {
			    xtype : 'component',
			    itemId : 'button-menu',
			    autoEl : {
				    tag : 'span',
				    cls : 'control viewoptions',
			    },
			    listeners : {
				    scope : this,
				    click : {
					    element : 'el', //bind to the underlying el property on the panel
					    fn : this.onMenuClick,
				    },
			    },
		    }, {
			    xtype : 'component',
			    itemId : 'tool-menu',
			    autoEl : {
				    tag : 'span',
				    cls : 'control tooloptions',
			    },
			    listeners : {
				    scope : this,
				    click : {
					    element : 'el', //bind to the underlying el property on the panel
					    fn : this.onToolMenuClick,
				    },
			    },
		    }, {
	            xtype: 'component',
	            itemId: 'logo',
	            hidden: this.parameters && this.parameters.logo ? false : true,
	            autoEl: {
	                tag: 'a',
	                cls: 'control logo',
	            },
	        }]
        });

        this.items = [this.mainView];

		this.on({
            resize: this.onresize,

            //all this stuff happens after the layout occurs and the threejs canvas is available
            afterlayout: function () {
                if(me.firstLoad) return;
                me.firstLoad = true;

                me.createViewMenu();

                me.BQImageRequest();
                me.initHistogram();

		        me.createToolMenu();
                me.createToolPanel();
				me.createZoomSlider();


                //---------------------------------------------------------
                //register preferences
                //---------------------------------------------------------
                // preferences need to be retreived after ui has been built
                /*
                if (BQ.Preferences)
                    BQ.Preferences.get({
                        key : 'Viewer3D',
                        callback : Ext.bind(this.onPreferences, this),
                    });
                */
                BQ.Preferences.on('update_'+me.resource.resource_uniq+'_pref', me.onPreferences, me);
                BQ.Preferences.on('onerror_'+me.resource.resource_uniq+'_pref', me.onPreferences, me);
                BQ.Preferences.load(me.resource.resource_uniq);

				//this.setLoading(false);

            },

            //all this stuff happens after the layout occurs and the threejs canvas is available
			loaded : function () {
				console.log('loaded URL from: ', this.constructAtlasUrl());

				me.volumeObject.initUniforms([
                    {uniform: 'BREAK_STEPS', type: 'i', value: this.volumeObject.maxSteps},
                    {uniform: 'PASS',        type: 'i', value: 0},
                    {uniform: 'FOV',         type: 'f', value: this.canvas3D.fov},
                    {uniform: 'TEX_RES_X',   type: 'i', value: this.xTexSizeRatio * this.dims.slice.x},
                    {uniform: 'TEX_RES_Y',   type: 'i', value: this.yTexSizeRatio * this.dims.slice.y},
                    {uniform: 'ATLAS_X',   type: 'i', value: this.dims.atlas.x / this.dims.slice.x},
                    {uniform: 'ATLAS_Y',   type: 'i', value: this.dims.atlas.y / this.dims.slice.y},
                    {uniform: 'SLICES',    type: 'i', value: this.dims.slice.z},
                    {uniform: 'BLOCK_RES_X',   type: 'i', value: 1},
                    {uniform: 'BLOCK_RES_Y',   type: 'i', value: 1},
                    {uniform: 'BLOCK_RES_Z',   type: 'i', value: 1},
                    {uniform: 'textureAtlas',   type: 't', value: 1},

                ]);

                me.volumeObject.initResolution(this.canvas3D);
                me.volumeObject.loadMaterial('default_1');
                me.volumeObject.initBuffers();
                me.volumeObject.loaded = true;

				me.wipeTextureTimeBuffer();
				me.updateTextureUniform();
                me.fetchHistogram();
                me.canvas3D.doAnimate();
                me.canvas3D.controls.enabled = true;
			},
			scope : me,
 		});

//        console.log(shaderConfig().rayCastShader);

		this.callParent();
	},

	onresize : function (comp, w, h, ow, oh, eOpts) {
        //if(!this.sceneVolume) return;
        //if(!this.sceneVolume.uniforms) return;
		//if(!this.sceneVolume.uniforms['iResolution']) return;

		var pw = this.canvas3D.getPixelWidth();
		var ph = this.canvas3D.getPixelHeight();
        var w = this.canvas3D.getWidth();
		var h = this.canvas3D.getHeight();

		var newRes =
			new THREE.Vector2(pw, ph);
		//this.sceneVolume.setUniform('iResolution', newRes);
        this.volumeObject.setResolution();
        /*
		  this.screenBuffer
		  = new THREE.WebGLRenderTarget(pw, ph, {
		  minFilter : THREE.LinearFilter,
		  magFilter : THREE.NearestFilter,
		  format : THREE.RGBAFormat
		  });

		  this.accumBuffer1
		  = new THREE.WebGLRenderTarget(w, h, {
		  minFilter : THREE.LinearFilter,
		  magFilter : THREE.NearestFilter,
		  format : THREE.RGBAFormat
		  });

		  var materialScreen = this.sceneVolume.getMaterial('screen');
		  materialScreen.depthWrite = false;
		  materialScreen.threeShader.uniforms.tDiffuse.value = this.accumulationBuffer;
        */
        //this is necessary to update the quad which renders the scene and captures
        //the texture map to allow compositing
        /*
		  var quad = this.sceneScreen.children[0];

		  quad.geometry.width = pw;
		  quad.geometry.height = ph;
		  quad.geometry.vertices[0] = new THREE.Vector3(-pw / 2, ph / 2, 0);
		  quad.geometry.vertices[1] = new THREE.Vector3(pw / 2, ph / 2, 0);
		  quad.geometry.vertices[2] = new THREE.Vector3(-pw / 2, -ph / 2, 0);
		  quad.geometry.vertices[3] = new THREE.Vector3(pw / 2, -ph / 2, 0);

		  quad.geometry.verticesNeedUpdate = true;
		  quad.geometry.dynamic = true;
        */
		//this.sceneScreen.children[0] =

		//this.orthoCamera.left = -pw / 2;
		//this.orthoCamera.right = pw / 2;
		//this.orthoCamera.top = ph / 2;
		//this.orthoCamera.bottom = -ph / 2;
		//this.orthoCamera.updateProjectionMatrix();
        //this.sceneVolume.setConfigurable("default",
        //                                 "fragment",
        //                                 this.shaderConfig);
		this.rerender();

	},



	rerenderImmediate : function (input) {
        this.canvas3D.rerender();
    },

	rerender : function () {
        var me = this;
        me.volumeObject.resetSampleRate();
        me.canvas3D.rerender();
    },

	onAnimate : function () {
		//if (this.canvas3D.mousedown)
		//	this.setMaxSteps = 32;
        //this.setaPess(1);
        if(this.mousedown) this.volumeObject.resetSampleRate();
        if(this.canvas3D.getAutoRotate()){
            this.setSampleRate(this.minSampleRate);
            return;
        }

		if (this.volumeObject.steps < this.maxSteps) {
            this.volumeObject.steps *= 1.5;
            if(this.volumeObject.steps >= this.maxSteps){
                this.volumeObject.steps = this.maxSteps;
                this.canvas3D.stoprender();
            }
            //this.setSampleRate(this.volumeObject.newSampleRate);
            //this.volumeObject.maxSteps = newSampleRate;
		}
	},

    initHistogram : function() {
		var me = this;

        this.model = {
            histogramRaw: {r:[], g:[], b:[]},
            histogram: {r:[], g:[], b:[]},
            gamma: {min: 0, max: 1.0, scale: 1.0},
            loaded: false,
        }

        var model = this.model;

        var updateHist = function(){

            for(var chan in model.histogramRaw){
                var hist    = model.histogramRaw[chan];
                var newHist = model.histogram[chan];
                if(hist.length > 10000) return;
                var maxVal = 0;
                var minVal = 999;
                var min = model.gamma.min;
                var max = model.gamma.max;
                var C   = model.gamma.scale;
                //var C = 1.0;
                var start = Math.floor(model.gamma.min * hist.length);
                var end = Math.floor(model.gamma.max * hist.length);

                var lookUp = new Array();
                var avg = 0;
                hist.forEach(function(val,i,a){
                    avg += val;
                    minVal = val < minVal ? val : minVal;
                    maxVal = val > maxVal ? val : maxVal;
                });

                avg /= hist.length;
                var l = hist.length;
                for (var i = 0; i < newHist.length; i++) {
                    lookUp[i] = 0;
                    newHist[i] = 0;
                    if (i > start && i < end) {
                        var val = l*(i - start) / (end - start);
                        var plogy = C * Math.log(val);
                        var modVal = Math.exp(plogy);
                        modVal = modVal < 0 ? 0 : (modVal > hist.length ? hist.length : modVal);
                        var newBin = Math.floor(modVal);
                        newBin = newBin < hist.length - 1 ? newBin : hist.length - 1;
                        lookUp[i] = newBin;
                        if(C == 1) lookUp[i] = i;
                    }
                    if(i < start)
                        lookUp[i] = 0;
                    if(i > end)
                        lookUp[i] = newHist.length - 1;

                }
                var spread = Math.ceil(hist.length/(end - start));
                for (var i = 0; i < lookUp.length - spread; i++) {
                    newHist[lookUp[i]] += 1.0/spread * hist[i];
                }
            }
            me.fireEvent("histogramupdate", me);
        };
        this.model.updateHistogram = function(){
            if(me.histTimer) clearTimeout(me.histTimer);
            me.histTimer = setTimeout(updateHist, 50);
        }
    },

    BQImageRequest : function () {
        var me = this;

		if (!this.resource) {
			BQ.ui.error('No image defined...');
			return;
		}

		this.setLoading('Loading...');

		if (typeof this.resource === 'string') {
			BQFactory.request({
				uri : this.resource,
				uri_params : {
					view : 'short'
				},
				cb : callback(this, this.onImage),
				errorcb : callback(this, this.onerror),
			});
		} else if (this.resource instanceof BQImage) {
			this.onImage(this.resource);
		}
    },

    afterRender: function() {
        this.callParent();

        // add contextual video
        BQApp.setActiveHelpVideo('//www.youtube.com/embed/siEtbaNGxrk');
    },

	afterFirstLayout : function () {
        var me = this;

        /////////////////////////////////////////////////
		// begin setup backbuffer rendering:
		// putting it here for experimentation... this should get moved to extThree
		/////////////////////////////////////////////////

		this.screenBuffer
			 = new THREE.WebGLRenderTarget(this.getWidth(), this.getHeight(), {
				minFilter : THREE.LinearFilter,
				magFilter : THREE.NearestFilter,
				format : THREE.RGBAFormat
			});

	    this.toggle = true;

		this.orthoCamera = new THREE.OrthographicCamera(-this.getWidth() / 2,
				this.getWidth() / 2,
				this.getHeight() / 2,
				-this.getHeight() / 2,
				-10000, 10000);
		this.orthoCamera.position.z = 1000;

		var screenUniforms = {
			tDiffuse : {
				type : "t",
				value : this.screenBuffer
			}
		};

		this.sceneVolume.initMaterial({
			name : 'screen',
			vertex : {
				url : "/core/js/volume/shaders/screen.vs"
			},
			fragment : {
				url : "/core/js/volume/shaders/screen.fs",
			},
			uniforms : screenUniforms,
		});

		var materialScreen = this.sceneVolume.getMaterial('screen');
		materialScreen.depthWrite = false;
        /*
		this.sceneScreen = new THREE.Scene();

		var plane = new THREE.PlaneGeometry(this.getWidth(), this.getHeight());
		var quad = new THREE.Mesh(plane, materialScreen.threeShader);
		quad.position.z = -100;

		this.sceneScreen.add(quad);
		*/
        this.canvas3D.render_override = true;
		this.canvas3D.renderer.preserveDrawingBuffer = true;

		/////////////////////////////////////////////////
		/////////////////////////////////////////////////

		//query the maximum render buffer size from the gpu
		//

		this.callParent();
	},

	getMaxTextureSize : function () {
		if (!this.maxTextureSize) {
			var ctx = this.canvas3D.renderer.getContext();
			this.maxTextureSize = 0.5 * ctx.getParameter(ctx.MAX_TEXTURE_SIZE);
		}
        //return 2048;
		return this.maxTextureSize;
	},

    fetchHistogram : function () {
        var url = this.constructAtlasUrl().replace('format=jpeg','histogram');

        //console.log("hist url: ", url);
        if(!this.model)
            this.initHistogram();
        Ext.Ajax.request({
            url : url,
            scope : this,
            disableCaching : false,
            callback : function (opts, succsess, response) {
                if (response.status >= 400)
                    BQ.ui.error(response.responseText);
                else {
                    if (!response.responseXML)
                        return;
                    var xmlDoc = response.responseXML;
                    var rChan = BQ.util.xpath_nodes(xmlDoc, "resource/histogram[@name='channel']/value");

                    var dim = 0;
                    for (var chan in this.model.histogram) {
                        if(!rChan[dim]) continue;
                        var tmp;
                        var data = rChan[dim].innerHTML ?
                            rChan[dim].innerHTML : rChan[dim].textContent;
                        var tmp = data.split(",");
                        if (this.model.histogram.hasOwnProperty(chan)) {
                            var channel = this.model.histogram[chan];
                            if(channel.length == 0) channel == tmp;
                            tmp.forEach(function(e,i,a){
                                channel[i] = parseInt(tmp[i]);
                            });
                        }
                        dim++;
                        this.numChannels = dim;
                        this.model.histogramRaw[chan] = this.model.histogram[chan].slice(0);
                    }
                    this.model.loaded = true;
                    this.fireEvent("histogramloaded",this);
                    this.sceneVolume.initUniform('NUM_CHANNELS', "i", this.numChannels);
                    this.model.updateHistogram();

                }
            },
        });
    },

	fetchDimensions : function (url, type) {
		var xRes;
		var yRes;
		Ext.Ajax.request({
			url : url,
			scope : this,
			timeout : 120000, // two minutes timeout
			disableCaching : false,
			callback : function (opts, succsess, response) {
				if (response.status >= 400 || !response.responseXML)
					BQ.ui.error(response.responseText);
				else {
					var xmlDoc = response.responseXML;

					if (type == 'slice' || type == 'atlas' || type == 'resized' || type == 'update_dims') {
						var nx = parseInt(BQ.util.xpath_string(xmlDoc, "//tag[@name='image_num_x']/@value"));
						var ny = parseInt(BQ.util.xpath_string(xmlDoc, "//tag[@name='image_num_y']/@value"));

						if (type == 'atlas') {
                            this.loadedDimFullAtlas = true;
                            this.dims.atlas.x = nx;
                            this.dims.atlas.y = ny;

                            this.loadedDimResizedAtlas = true;
                            this.dims.atlasResized.x = nx;
                            this.dims.atlasResized.y = ny;
						} else if (type == 'resized') {
							this.loadedDimResizedAtlas = true;
							this.dims.atlasResized.x = nx;
							this.dims.atlasResized.y = ny;
						} else if (type == 'update_dims') {
							// dima: safeguard resize case may alter the the size of the perceived plane size
							this.loadedDimFull = true;
							var rx = this.dims.slice.x / nx;
							var ry = this.dims.slice.y / ny;
							this.dims.slice.x = nx;
							this.dims.slice.y = ny;
							this.dims.pixel.x *= rx;
							this.dims.pixel.y *= ry;
							//this.dims.pixel.z *= rx; // dima: scaling Z to keep aspect ratio
						}
					}

					if (this.loadedDimFullAtlas && this.loadedDimResizedAtlas && this.loadedDimFull) {

						this.xTexSizeRatio = this.dims.atlasResized.x / this.dims.atlas.x;
						this.yTexSizeRatio = this.dims.atlasResized.y / this.dims.atlas.y;

						//a lot of information is already loaded by the phys object:
						//this.setLoading(false);
						//this.sceneVolume.loadMaterial('forwardDiffuse');

						this.sceneVolume.loadMaterial(this.cubeMesh, 'default');
                        this.loaded = true;
						this.fireEvent('loaded', this);

					}
				}
			},
		});
	},

	//----------------------------------------------------------------------
	// texture loading
	//----------------------------------------------------------------------

	updateTextureUniform : function () {
		var me = this;

        if(!this.state)
            this.state = 0;

		if (!this.textureTimeBuffer[this.currentTime]) {
			//var textureAtlas' = new Array();
            this.loadedTextures++;
            if(me.loadedTextures == 1)
                this.fireEvent('loadinitiated',t);

            var t = this.currentTime;
            var currentState = this.state;
			var textureAtlas = new THREE.ImageUtils.loadTexture(
                this.constructAtlasUrl(),
                undefined,
                function () {
                //console.log(t, 'loaded!!!');
                //me.playBack.setLoaded(t);
                me.loadedTextures--;
                if(currentState != me.state) return;
                if(me.loadedTextures == 0)
                    me.fireEvent('loadcomplete',t);

                me.fireEvent('atlasloadedat',t);
                me.setLoading(false);
                //me.rerender();
                if(t == me.currentTime)
				    me.rerender();
			    },
                function(error, msg){
                    BQ.ui.error('Couldn\'t fetch image, please try reloading the page or check back later.');
                    me.setLoading(false);
                }
            );
			textureAtlas.generateMipmaps = false;
			textureAtlas.magFilter = THREE.LinearFilter;
			textureAtlas.minFilter = THREE.LinearFilter;
			textureAtlas.wrapS = THREE.MirroredRepeatWrapping;
			textureAtlas.wrapT = THREE.MirroredRepeatWrapping;

			this.textureTimeBuffer[this.currentTime] = textureAtlas;

			//this.uniforms.textureAtlas.value = textureAtlas;
		}
		//this.sceneVolume.setUniform('textureAtlas', this.textureTimeBuffer[this.currentTime]);
		this.volumeObject.setUniform('textureAtlas', this.textureTimeBuffer[this.currentTime]);
        this.update = true;
	},

	initTextures : function () {
        this.loadedTextures = 0;
		var resUniqueUrl = this.resource.src;
		var slice;
		this.dims.slice.x = this.phys.x;
		this.dims.slice.y = this.phys.y;
		this.dims.slice.z = this.phys.z;

		this.dims.t = this.phys.t;
		this.dims.pixel.x = this.phys.pixel_size[0] === 0 ? 1 : this.phys.pixel_size[0];
		this.dims.pixel.y = this.phys.pixel_size[1] === 0 ? 1 : this.phys.pixel_size[1];
		this.dims.pixel.z = this.phys.pixel_size[2] === 0 ? 1 : this.phys.pixel_size[2];
		if (this.dims.pixel.z < 0.1)
			this.dims.pixel.z = 0.1;

		if (this.dims.t > 1 && this.dims.slice.z == 1) {
			var z = this.dims.t;
			this.dims.t = this.dims.slice.z;
			this.dims.slice.z = z;
			slice = 'slice=,,,,';
			this.dims.timeSeries = true;
		} else {
			slice = 'slice=,,,1';
            if(this.dims.t === 1)
                this.useAnimation = false;
        }

        var compute_atlas_size = function(w, h, n){
            //w: image width
            //h: image height
            //n: numbe rof image planes, Z stacks or time points
            //start with atlas composed of a row of images
            var ww = w*n,
                hh = h,
                ratio = ww / hh;
            // optimize side to be as close to ratio of 1.0
            for (var r=2; r < n; ++r){
                var ipr = Math.ceil(n / r),
                    aw = w*ipr,
                    ah = h*r,
                    rr = Math.max(aw, ah) / Math.min(aw, ah);
                if (rr < ratio){
                    ratio = rr
                    ww = aw
                    hh = ah
                }
                else
                    break;
            }
            return {w: Math.round(ww/w), h: Math.round(hh/h)};
        }


        var
        x = this.dims.slice.x,
        y = this.dims.slice.y,
        z = this.dims.slice.z,
        t = this.dims.t;

        var atlasDims = compute_atlas_size(x, y, z<2 ? t : z);



		var dims = 'dims';
		var meta = 'meta';
		var atlas = 'textureatlas';
		//var resize_safeguard = 'resize=1024,1024,BC,MX'; // resize designed to safeguard against very large planar images
		// we probably need to add safeguard against very large Z series
		var maxTexture = this.getMaxTextureSize();
        var resizeX = Math.floor(this.maxTextureSize/atlasDims.w);
        var resizeY = Math.floor(this.maxTextureSize/atlasDims.h);
        this.max_texture_tile_size = { w: resizeX, h: resizeY };

		var resize = 'resize=' + resizeX + ',' + resizeY + ',BC,MX';

		var fullUrl = resUniqueUrl + '?' + [slice, resize, dims].join('&');
		var fullAtlasUrl = resUniqueUrl + '?' + [slice, resize, atlas, dims].join('&');
		//var resizeAtlasUrl = resUniqueUrl + '?' + [slice, resize, atlas, dims].join('&');

		this.loadedDimFullAtlas = false;
		this.loadedDimResizeAtlas = false;

		//Ajax request the values pertinent to the volume atlases
		this.fetchDimensions(fullUrl, 'update_dims');
		this.fetchDimensions(fullAtlasUrl, 'atlas');
		//this.fetchDimensions(resizeAtlasUrl, 'resized');
        //this.fetchHistogram();
	},

	wipeTextureTimeBuffer : function () {
		this.loadedTextures = 0;
        this.state++;
        this.textureTimeBuffer = new Array();
        this.fireEvent('wipetexturebuffer', this);
	},

	onImage : function (resource) {
		//build custom atlas dims here, maybe this can get cuter...

		this.dims = {
			slice : {
				x : 0,
				y : 0,
				z : 0
			},
			atlas : {
				x : 0,
				y : 0,
				z : 1
			},
			atlasResized : {
				x : 0,
				y : 0,
				z : 1
			},
			pixel : {
				x : 0,
				y : 0,
				z : 0
			},
			t : 0
		};

		if (!resource)
			return;
		this.resource = resource;

        var logo = this.queryById('logo');
        if (logo) {
            logo.getEl().dom.href = '/client_service/view?resource='+resource.uri;
        }

		if (!this.phys) {
			var phys = new BQImagePhys(this.resource);
			phys.load(callback(this, this.onPhys));
		}

		this.onPartFetch();
	},

	onPhys : function (phys) {
		if (!phys)
			return;
		this.phys = phys;
		this.onPartFetch();
	},

	onPartFetch : function () {
		if (!this.resource || !this.phys)
			return;
		this.initTextures();

		//this.createToolMenu();
		for (var i = 0; (plugin = this.plug_ins[i]); i++)
			plugin.init();
	},

	onerror : function (error) {

		if (this.hasListeners.error)
			this.fireEvent('error', error);
		else {
			console.log('error, bisque service not available.');
			//BQ.ui.error(error.message_short);
			/*
			this.xTexSizeRatio = 1.0;
			this.yTexSizeRatio = 1.0;
			this.initUniforms();
			this.uniforms.TEX_RES_X.value = 1;
			this.uniforms.TEX_RES_Y.value = 1;
			this.uniforms.ATLAS_X.value   = 1;
			this.uniforms.ATLAS_Y.value   = 1;
			this.uniforms.SLICES.value    = 1;

			this.setLoading(false);

			this.canvas3D.initScene(this.uniforms);
			var dataBase0 = new Array();
			dataBase0[0] = null;
			this.uniforms.dataBase0.value = dataBase0;
			this.fireEvent('loaded', this);
			this.textureTimeBuffer = new Array();
			this.textureTimeBuffer[0] = null;
			this.setLoading(false);
			this.canvas3D.doAnimate();
			 */
		}
	},

	constructAtlasUrl : function (opts) {
		var command = [];
		var plugin = undefined;
		for (var i = 0; (plugin = this.plug_ins[i]); i++)
			plugin.addCommand(command, opts);
        var atlas = this.resource.src + '?' + command.join('&');
        //console.log('atlas: ', atlas);
		return atlas;
	},

/*
	constructAtlasUrlNoJpg : function (opts) {
		var command = [];
		var plugin = undefined;
		for (var i = 0; (plugin = this.plug_ins[i]); i++)
			plugin.addCommand(command, opts);
		return (this.hostName ? this.hostName : '') + '/image_service/image/'
		 + this.resource.resource_uniq + '?' + command.join('&');
	},
*/


    /////////////////////////////////////////////
    //Sets which emit Events after setting
    /////////////////////////////////////////////

    setMaxSampleRate : function (qual) {
        this.volumeObject.setMaxSampleRate(qual);
        this.fireEvent('setquality', this);
        this.rerender();
    },

	setCurrentTime : function (time) {
		if (this.dims.t == 1)
			return;
		else {
			if (this.currentTime != time) {
				this.currentTime = time;
				this.needs_update();
				this.fireEvent('time', this);
			}

		}
	},

	setCurrentTimeRatio : function (k) {
		if (this.dims.t == 1)
			return;
		else {
			if (this.currentTime != time) {
				var time = Math.floor((this.dims.t-1) * k);
				this.currentTime = time;
				//this.updateFrameLabel(time);
				this.needs_update();
				this.fireEvent('time', this);
			}

		}
	},

	setVolumeScale : function (inScale) {
        this.volumeObject.setScale(inScale);
        this.scale = inScale;
		this.volumeObject.setUniform('BOX_SIZE', inScale, true, true);

		this.currentScale = inScale.clone();
        this.cubeMesh.scale.copy(new THREE.Vector3(2.0*inScale.x,
                                                   2.0*inScale.y,
                                                   2.0*inScale.z));
		this.rerender();
		this.fireEvent('scale', inScale,  this);
	},

    /////////////////////////////////////////////
    //Sets which do NOT emit Events after setting
    /////////////////////////////////////////////

    setModel : function (field, value){
        this.shaderConfig[field] = value;
        this.sceneVolume.updateShader
    },

    setAutoRotate : function (rotate){
        this.canvas3D.setAutoRotate(rotate);
    },

    setSampleRate : function(sampleRate){
        this.volumeObject.steps = sampleRate;
		//this.volumeObject.setUniformNoRerender('BREAK_STEPS', sampleRate, false);
    },

    setPass : function(pass){
        this.volumeObject.setUniform('PASS', pass, false);
    },

	doUpdate : function () {
		this.update_needed = undefined;
		// dima: image service is serving bad h264 right now
		//this.viewer.src = this.constructAtlasUrl();
		this.updateTextureUniform();
        this.fetchHistogram();
		//this.sourceH264.setAttribute('src', this.constructMovieUrl('h264'));
		//this.sourceWEBM.setAttribute('src', this.constructMovieUrl('webm'));
	},

    update_image : function (){
        this.fetchHistogram();
    },

	needs_update : function () {
		this.requires_update = undefined;

		if (this.update_needed)
			clearTimeout(this.update_needed);
		this.update_needed = setTimeout(callback(this, this.doUpdate), this.update_delay_ms);
	},

    onPreferences: function(pref) {
        this.preferences = pref;
        var resource_uniq = this.resource.resource_uniq;

        //this.preferences.
        for (var key in this.tools) {
            if (!this.tools.hasOwnProperty(key)) {
                //The current property is not a direct property of p
                continue;
            }

            var tool = this.tools[key],
                path = 'Viewer3D/' + key;
            if (tool.loadPreferences)
                tool.loadPreferences(path, resource_uniq);
        }

        if (this.preferences.title)
            this.queryById('menu_title').setText( '<h3><a href="/">'+this.preferences.title+'</a></h3>' );

    },


	//----------------------------------------------------------------------
	// Add fadeout to a panel
	//---------------------------------------------------------------------

	addFade : function (Panel) {
		var panel = Panel;
		Panel.usingPanel = false;
		Panel.getEl().dom.addEventListener('mouseenter', function () {
			panel.usingPanel = true;
			panel.getEl().fadeIn({
				opacity : 0.8,
				duration : 200
			});
		}, false);

		Panel.getEl().dom.addEventListener('mouseleave', function () {
			panel.usingPanel = false;
			setTimeout(function () {
				if (!panel.usingPanel) {
					panel.getEl().fadeOut({
						opacity : 0.1,
						duration : 2000
					});
				}
			}, 3000);

		}, false);
	},

	//----------------------------------------------------------------------
	// Tool Panel
	//---------------------------------------------------------------------

	createToolPanel : function () {
        var me = this;
		var items = [];

        this.toolPanelButtons = Ext.create('Ext.toolbar.Toolbar',{
            itemId: 'toolbar-buttons',
            //height: 32,
            layout: {
                type: 'table',
                columns: 6
            },
        });

        var tools = [
            new ditherTool(this),
            new boxTool(this),
            new gammaTool(this),
            new materialTool(this),
            //new lightTool(this),
        ];

        if (Ext.isWindows) {
			if (Ext.isChrome && Ext.chromeVersion >= 37) {
                tools.push(new lightTool(this));
			}
		}

        else {
			tools.push(new lightTool(this));
		}

        if(window.location.hash == "#debug"){
            tools.push(new loseContextTool(this));
        }

        tools.push(new transferTool(this),
                   new gObjectTool(this),
                   new clipTool(this),
                   new animationTool(this),
                   new saveTool(this),

                   //Tools in the settings menu
                   //new showGraphTool(this),
                   new autoRotateTool(this),
                   new qualityTool(this),

                   //Tools in the Div
                   new VolScaleBarTool(this),
                   new VolAxisTool(this),
                   new VolSpinnerTool(this));

        this.tools = {};

        tools.forEach(function(e,i,a){
            me.tools[e.name] = e;
            e.init();
            e.addButton();
		    //e.addControls();
        });

        //tools factory function
		if (!this.toolPanel) {
			var thisDom = this.mainView.getEl().dom;

			this.toolPanel = Ext.create('Ext.panel.Panel', {
				renderTo : thisDom,
			    tbar: this.toolPanelButtons,

                //layout : 'fit',
                layout : 'auto',
                //layout : {
			    //    type : 'vbox',
			    //    align : 'stretch',
			    //    pack : 'start',
		        //},
                title : 'Settings',
				cls : 'bq-volume-toolbar',
				collapsible : true,
                collapseDirection: 'right',
                autoScroll: true,
                width: 240,
                //resizeable: true,
                //resizeHandles: 's',
                listeners:{
                    expand: function(p,opts){
                        this.doLayout();
                    }
                }

			});
			this.addFade(this.toolPanel);
            //this.addDocked(this.toolPanel);

            tools.forEach(function(e,i,a){
		        e.addControls();
            });

		}

	},
    //----------------------
	// Zoom Slider
	//---------------------------------------------------------------------

	createZoomSlider : function () {
		if(this.zoomSlider) return;
        var me = this;
		var thisDom = this.mainView.getEl().dom;
        this.zoomSlider = Ext.create('Ext.slider.Single', {
			renderTo : thisDom,
			//id : 'zoom-slider',
			cls : 'bq-zoom-slider',
			hideLabel : true,
			minValue : 0,
			maxValue : 100,
			increment : 1,
			height : 300,
			x : 10,
			y : 10,
			style : {
				position : 'absolute',
				'z-index' : 9999999
			},
			layout : {
				type : 'vbox',
				align : 'left',
				clearInnerCtOnLayout : true,
				bindToOwnerCtContainer : false
			},
			vertical : true,
			value : 0,
			animation : false,
			listeners : {
				change : function (slider, value) {

					if (!this.canvas3D.zooming) {
						var scale = 10.0 * (1.0 - value / slider.maxValue);
						scale = scale < 0.25 ? 0.25 : scale;
						me.canvas3D.controls.enabled = false;
						me.canvas3D.controls.setRadius(scale);
                        console.log('zoom');
                        //me.canvas3D.controls.enabled = false;;
						//me.canvas3D.controls.noPan = true;
						me.rerender();
					}
				},
				changecomplete : function (slider, value) {
					me.canvas3D.controls.enabled = true;
					me.canvas3D.controls.update();
                    me.rerender();
				},
				scope : me,
			}
		});

        /*
		thisDom.addEventListener('mousewheel', function () {
			var distFromCenter = me.canvas3D.camera.position.length();
			var newSliderVal = Math.floor((10.0 - distFromCenter) * 10.0);
			var curSliderVal = me.zoomSlider.getValue(0);
			if (newSliderVal != curSliderVal) {
				me.zoomSlider.setValue(newSliderVal);
			}
		}, false);
        */

		this.zoomSlider.setValue(50);
		this.canvas3D.controls.noRoate = false;
		this.canvas3D.controls.noPan = false;
		this.addFade(this.zoomSlider);
	},


	//----------------------------------------------------------------------
	// tool combo
	//---------------------------------------------------------------------

	createToolMenu : function () {
        var me = this;
	    if (this.toolMenu)return;

        var menubutton = this.queryById('tool-menu');
		this.toolMenu = Ext.create('Ext.tip.ToolTip', {
			target : menubutton.getEl(),
			anchor : 'top',
			anchorToTarget : true,
			cls : 'bq-volume-menu',
			maxWidth : 460,
			anchorOffset : -5,
			autoHide : false,
			shadow : false,
			closable : true,
			layout : {
				type : 'vbox',
                align: 'stretch',
			},

		});

		this.toolMenu.add([{
			boxLabel : 'settings',
			checked : true,
			width : 200,
			cls : 'toolItem',
			xtype : 'checkbox',
			handler : function (item, checked) {

                if (checked) {
					me.toolPanel.show();
				} else
					me.toolPanel.hide();
			},
		},/*{
            xtype: 'glinfo',
            canvas3D: this.canvas3D
        }*/]);
//        showAnimPanel();

	},

	onToolMenuClick : function (e, btn) {
		e.preventDefault();
		e.stopPropagation();
		if (this.toolMenu.isVisible())
			this.toolMenu.hide();
		else
			this.toolMenu.show();
	},

	//----------------------------------------------------------------------
	// view menu
	//----------------------------------------------------------------------

	createCombo : function (label, items, def, scope, cb, id, min_width) {
		var ot
		var options = Ext.create('Ext.data.Store', {
				fields : ['value', 'text'],
				data : items
			});
		var combo = this.menu.add({
				xtype : 'combobox',
				itemId : id ? id : undefined,
				width : 380,
				fieldLabel : label,
				store : options,
				queryMode : 'local',
				displayField : 'text',
				valueField : 'value',
				forceSelection : true,
				editable : false,
				value : def,
	            listConfig : {
	                minWidth: min_width || 70,
	            },
				listeners : {
					scope : scope,
					'select' : cb,
				},
			});
		return combo;
	},

	createViewMenu : function () {

		if (!this.menu) {
			var menubutton = this.queryById('button-menu');
			this.menu = Ext.create('Ext.tip.ToolTip', {
					target : menubutton.getEl(),
					anchor : 'top',
					anchorToTarget : true,
					cls : 'bq-volume-menu',
					maxWidth : 460,
					anchorOffset : -5,
					autoHide : false,
					shadow : false,
					closable : true,
					layout : {
						type : 'vbox',
						//align: 'stretch',
					},
					defaults : {
						labelSeparator : '',
						labelWidth : 200,
					},
				});
		}
	},

	onMenuClick : function (e, btn) {
		e.preventDefault();
		e.stopPropagation();
		if (this.menu.isVisible())
			this.menu.hide();
		else
			this.menu.show();
	},

    onFullScreenClick: function (e, btn) {
        e.preventDefault();
        e.stopPropagation();
        this.doFullScreen();
    },

    doFullScreen: function () {
        var maximized = (document.fullscreenElement || document.mozFullScreenElement || document.webkitFullscreenElement || document.msFullscreenElement),
        vd = this.getEl().dom,
            has_fs = vd.requestFullscreen || vd.webkitRequestFullscreen || vd.msRequestFullscreen || vd.mozRequestFullScreen;
        if (!has_fs) return;

        if (!maximized) {
            if (vd.requestFullscreen) {
                vd.requestFullscreen();
            } else if (vd.webkitRequestFullscreen) {
                vd.webkitRequestFullscreen();
            } else if (vd.msRequestFullscreen) {
                vd.msRequestFullscreen();
            } else if (vd.mozRequestFullScreen) {
                vd.mozRequestFullScreen();
            }
        } else {
            if (document.exitFullscreen) {
                document.exitFullscreen();
            } else if (document.webkitExitFullscreen) {
                document.webkitExitFullscreen();
            } else if (document.msExitFullscreen) {
                document.msExitFullscreen();
            } else if (document.mozCancelFullScreen) {
                document.mozCancelFullScreen();
            }
        }
    },

    updateGobs: function () {
        var gobtool = this.tools['gobjects'];
        if (!gobtool) return;
        gobtool.updateColor();
        this.rerender();
    },

});

//--------------------------------------------------------------------------------------
// Dialogue Box
//--------------------------------------------------------------------------------------

Ext.define('BQ.viewer.Volume.Dialog', {
	extend : 'Ext.window.Window',
	alias : 'widget.bq_volume_dialog',
	//border : 0,
	layout : 'fit',
	modal : true,
	border : 0,
	width : '75%',
	height : '75%',
	buttonAlign : 'center',
	autoScroll : true,
	title : 'volume viewer',

	constructor : function (config) {
		config = config || {};

		Ext.apply(this, {
			title : 'Move for ' + config.resource.name,
			items : [{
					xtype : 'bq_volume_panel',
					hostName : config.hostName,
					resource : config.resource
				}
			],
		}, config);

		this.callParent(arguments);
		this.show();
	},
});

//--------------------------------------------------------------------------------------
// Plug-ins - base
//--------------------------------------------------------------------------------------

function VolumePlugin(volume) {
	this.volume = volume;
};

VolumePlugin.prototype.init = function () {};

VolumePlugin.prototype.addCommand = function (command, pars) {};

VolumePlugin.prototype.changed = function () {
	if (!this.update_check || (this.update_check && this.update_check.checked))
	{
        this.volume.needs_update();

        this.volume.wipeTextureTimeBuffer();
        this.volume.setLoading("fetching new texture...");

    }
};

/*
VolumePlugin.prototype.changed = function () {
	if (!this.update_check || (this.update_check && this.update_check.checked))
		this.volume.needs_update();
	this.volume.wipeTextureTimeBuffer();
    this.volume.setLoading("fetching new texture...");
};
*/

function VolumeSize(player) {
	this.base = VolumePlugin;
	this.base(player);

	this.resolutions = {
		'SD' : {
			w : 720,
			h : 480,
		},
		'HD720' : {
			w : 1280,
			h : 720,
		},
		'HD' : {
			w : 1920,
			h : 1080,
		},
		'4K' : {
			w : 3840,
			h : 2160,
		},
	};
};

function VolumeFormat(volume) {
	this.base = VolumePlugin;
	this.base(volume);
};
VolumeFormat.prototype = new VolumePlugin();

VolumeFormat.prototype.init = function () {};

VolumeFormat.prototype.addCommand = function (command, pars) {
	command.push('format=jpeg');
};

function VolumeTime(volume) {
	this.base = VolumePlugin;
	this.base(volume);
};
VolumeTime.prototype = new VolumePlugin();

VolumeTime.prototype.init = function () {};

VolumeTime.prototype.onTime = function () {

	//var nt = parseInt(this.volume.dims.t);
	//var t = this.volume.getValue();
	var t = this.volume.currentTime;
	this.changed();
};

VolumeTime.prototype.addCommand = function (command, pars) {

	if (this.volume.dims)
		if (this.volume.dims.timeSeries)
			command.push('slice=,,,,');
		else {
			var t = this.volume.currentTime + 1;
			command.push('slice=,,,' + (t > 0 ? t : ''));
		}
};

function VolumeAtlas(volume) {
	this.base = VolumePlugin;
	this.base(volume);
};
VolumeAtlas.prototype = new VolumePlugin();

VolumeAtlas.prototype.init = function () {};

VolumeAtlas.prototype.addCommand = function (command, pars) {
	var maxsz = this.volume.max_texture_tile_size;
    //command.push('resize=1024,1024,BC,MX'); // resize designed to safeguard against very large planar images
    command.push('resize=' + maxsz.w + ',' + maxsz.h + ',BC,MX');
	command.push('textureatlas');
	//var maxTexture = this.volume.getMaxTextureSize();
	//command.push('resize=' + maxTexture + ',' + maxTexture + ',BC,MX');
};

//--------------------------------------------------------------------------------------
// Plug-ins - display
//--------------------------------------------------------------------------------------

function VolumeDisplay(volume) {
	this.base = VolumePlugin;
	this.base(volume);
    this.uuid = this.volume.resource.resource_uniq;
    this.phys = this.volume.phys;
};

VolumeDisplay.prototype = new VolumePlugin();

VolumeDisplay.prototype.init = function () {
    this.def = {
        enhancement      : BQ.Preferences.get(this.uuid, 'Viewer/enhancement') || 'd', // values: 'd', 'f', 't', 'e'
        enhancement_8bit : BQ.Preferences.get(this.uuid, 'Viewer/enhancement-8bit') || 'f',
        negative         : BQ.Preferences.get(this.uuid, 'Viewer/negative') || '',  // values: '', 'negative'
        rotate           : BQ.Preferences.get(this.uuid, 'Viewer/rotate') || 0,   // values: 0, 270, 90, 180
        fusion           : BQ.Preferences.get(this.uuid, 'Viewer/fusion'),
        fusion_method    : BQ.Preferences.get(this.uuid, 'Viewer/fusion_method') || 'm', // values: 'a', 'm'
        brightness       : BQ.Preferences.get(this.uuid, 'Viewer/brightness') || 0, // values: [-100, 100]
        contrast         : BQ.Preferences.get(this.uuid, 'Viewer/contrast') || 0, // values: [-100, 100]
        autoupdate       : false,
    };
	if (!this.menu)
		this.createMenu();
};

VolumeDisplay.prototype.addCommand = function (command, pars) {

	if (!this.menu)
		return;

    var enh = this.combo_enhancement.getValue();
    if (enh.indexOf('hounsfield') != 0) {
        command.push ('depth=8,' + this.combo_enhancement.getValue() + ',u');
    } else {
        var a = enh.split(':');
        command.push ('depth=8,hounsfield,u,,'+a[1]);
    }

    var fusion = this.phys.fusion2string() + ':'+this.combo_fusion.getValue();
    command.push ('fuse='+fusion);

	if (this.combo_negative.getValue()) {
		command.push(this.combo_negative.getValue());
	}
};

VolumeDisplay.prototype.createMenu = function () {
	if (this.menu)
		return;

	this.menu = this.volume.menu;

	this.createChannelMap();
	var phys = this.volume.phys,
        enhancement = phys && parseInt(phys.pixel_depth)===8 ? this.def.enhancement_8bit : this.def.enhancement;

    this.menu.add({
		xtype : 'displayfield',
		fieldLabel : 'View',
		cls : 'heading',
	});

    // fusion
    this.combo_fusion = this.volume.createCombo( 'Fusion', [
        {"value":"a", "text":"Average"},
        {"value":"m", "text":"Maximum"},
    ], this.def.fusion_method, this, function() {
        BQ.Preferences.set(this.uuid, 'Viewer/fusion_method', this.combo_fusion.value);
        this.changed();
    });

    // enhancement
    var enhancement_options = phys.getEnhancementOptions();
    enhancement = enhancement_options.prefferred || enhancement;
    this.combo_enhancement = this.volume.createCombo( 'Enhancement', enhancement_options, enhancement, this, function() {
        BQ.Preferences.set(this.uuid, 'Viewer/enhancement', this.combo_enhancement.value);
        this.changed();
    }, undefined, 300);

    // negative
    this.combo_negative = this.volume.createCombo( 'Negative', [
        {"value":"", "text":"No"},
        {"value":"negative", "text":"Negative"},
    ], this.def.negative, this, function() {
        BQ.Preferences.set(this.uuid, 'Viewer/negative', this.combo_negative.value);
        this.changed();
    });

};

VolumeDisplay.prototype.createChannelMap = function () {
	var phys = this.volume.phys,
        channel_names = phys.getDisplayNames(this.uuid),
        channel_colors = phys.getDisplayColors(this.uuid);

	this.menu.add({
		xtype : 'displayfield',
		fieldLabel : 'Channels',
		cls : 'heading',
	});

	for (var ch = 0; ch < phys.ch; ch++) {
		this.menu.add({
			xtype : 'colorfield',
			fieldLabel : '' + channel_names[ch],
			name : 'channel_color_' + ch,
			channel : ch,
			value : channel_colors[ch].toString().replace('#', ''),
			listeners : {
				scope : this,
				change : function (field, value) {
					channel_colors[field.channel] = Ext.draw.Color.fromString('#' + value);
                    phys.prefsSetFusion (this.uuid);
					this.changed();
				},
			},
		});
	}
};
