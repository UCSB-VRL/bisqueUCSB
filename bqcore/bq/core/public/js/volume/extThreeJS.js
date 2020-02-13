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

function get_string_from_URL (url) {
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.open ("GET", url, false);
    xmlhttp.send ();
    return xmlhttp.responseText;
}



Ext.define('BQ.viewer.Volume.ThreejsPanel', {
    //extend: 'Ext.container.Container',
    extend : 'Ext.Component',
    alias : 'widget.threejs_panel',
    border : 0,
    frame : false,
   // layout : 'fit',

    autoEl: {
        tag: 'canvas',
        cls: 'threejsComponent',
    },

    listeners: {
        scope: this,
    },

    initComponent : function() {
        this.on('resize', this.onresize);
	    this.zooming     = false;
        this.selectLight = false;
	    this.animate_funcs = new Array();
        this.mousedown = false;
        this.needs_render = true;
        this.callParent();


    },

    initScene : function(uniforms) {
        //this.fireEvent("initscene");
    },

    afterRender : function() {
        this.callParent();
    },

    afterFirstLayout : function() {
        var me = this;

        var thisDom = this.getEl().dom;
        if(window.location.hash == "#debug"){
            thisDom = WebGLDebugUtils.makeLostContextSimulatingCanvas(thisDom);
            this.loseContext = function(){
                thisDom.loseContext();
            }
        }

        this.renderer = new THREE.WebGLRenderer({
            canvas: thisDom,
            preserveDrawingBuffer : true,
            alpha: true,
            premultipliedAlpha: false,
            sortObjects: true,

        });
        this.renderer.setBlending(THREE.NormalBlending);
        //this.setClearColor(0xC0C0C0, 1.0);

        var aspect = this.getWidth() / this.getHeight();
        this.fov = 20;
        this.camera = new THREE.PerspectiveCamera(this.fov, aspect, .001, 20);

        this.camera.position.z = 5.0;
        //this.controls = new THREE.TrackballControls(this.camera, thisDom);
        //this.controls = new THREE.OrbitControls(this.camera, thisDom);
        this.controls = new THREE.RotationControls(this.camera, thisDom);
        this.controls.autoRotate = false;
        this.controls.enabled = true;
        this.getEl().on({
            scope : this,
            //resize : this.onresize,
            mouseup : this.onMouseUp,
            mousedown : this.onMouseDown,
            mousemove : this.onMouseMove,
            mousewheel: this.onMouseWheel,
            DOMMouseScrool: this.onMouseWheel,
            touchstart: this.onMouseDown,
            touchend: this.onMouseUp,
            touchmove: this.onMouseMove,

        } );

        //this.anaglyph = new THREE.AnaglyphEffect( this.renderer );
		//this.anaglyph.setSize( this.getWidth(), this.getHeight() );
        this.fireEvent('loaded', this);
        this.callParent();
        if(this.buildScene)
            this.buildScene();


        //handle context loss and restoration...
        this.renderer.context.canvas.addEventListener("webglcontextlost", function(event) {
            event.preventDefault();
            // animationID would have been set by your call to requestAnimationFrame
            me.fireEvent('glcontextlost', event);
            BQ.ui.error(event.statusMessage)
            cancelAnimationFrame(me.animationID);
        }, false);

        this.renderer.context.canvas.addEventListener("webglcontextrestored", function(event) {
            me.fireEvent('glcontextrestored', event);
            //rebuild the scene
            //this.buildScene();
        }, false);

        this.renderer.render(this.scene, this.camera);
    },

    setAutoRotate: function(rotate){
        this.controls.autoRotate = rotate;
    },

    getAutoRotate: function(){
        return this.controls.autoRotate;
    },

    getCanvas : function() {
        return this.getEl().dom;
    },

    setClearColor: function(color, alpha){
        this.renderer.setClearColor(color, alpha);
    },

    getPixelWidth : function(){
        return this.renderer.context.canvas.width;
        //return this.getWidth();
    },

    getPixelHeight : function(){
        return this.renderer.context.canvas.height;
        //return this.getHeight();
    },

    triggerHandler : function(handler, event){
        if(!this.handlers) return;
        if(this.handlers[handler])
            this.handlers[handler](event);

    },

    onMouseWheel : function(event) {
	    this.zooming = true;
        this.mousedown = true;
        this.needs_render = true;
        var me = this;

        setTimeout(function() {
	        me.zooming = false;
	        me.mousedown = false;
            me.controls.enabled = true;
            me.controls.update();
            me.triggerHandler('mousewheelup', event);

        }, 200);

        //this.fireEvent('mousewheel', event);
        this.triggerHandler('mousewheel', event);

    },

    onMouseDown : function(event) {
        this.mousedown = true;
        this.zooming = false;
		this.controls.noRotate = false;
		this.controls.noPan = false;

        this.controls.update();
        var me = this;
	    if(event.button == 1){
	        this.zooming = true;
	    }
        this.needs_render = true;
        //console.log(event);
        this.triggerHandler('mousedown', event);
        this.fireEvent('mousedown', event);

        this.doAnimate();

        /*
        if(event.button == 0 || event.button == 1 ){
            //this.handlers.mousedown(event);
            this.triggerHandler('mousedown', event);

        }
        if(event.button == 2)
            this.triggerHandler('rightclick', event);
            */
    },

    onMouseUp : function(event) {
        this.controls.enabled = true;
        this.mousedown   = false;
        this.needs_render = true;
        this.fireEvent('mouseup', event);
        this.triggerHandler('mouseup', event);

    },

    onMouseMove : function(event){
        //this.fireEvent('mousemove', event);

        this.triggerHandler('mousemove', event);

    },

    onresize : function(comp, w, h, ow, oh, eOpts) {
        //console.log(args);
        var aspect = w / h;
        this.camera.aspect = aspect;
        this.camera.updateProjectionMatrix();

        this.renderer.setSize(w, h);
        //this.anaglyph.setSize(w, h);
        this.mousedown = false;
    },

    rerender : function() {
        this.needs_render = true;
        if(!this.animationID)
            this.doAnimate();
    },

    stoprender : function() {
        this.needs_render = false;
    },

    render : function(){
        this.renderer.render(this.scene, this.camera);
        this.fireEvent('render', this);
        //me.triggerHandler('mousewheelup', event);
    },

    doAnimate : function() {
        var me = this;
        this.controls.update();
	    if(this.onAnimate)
	        this.onAnimate();
        if(this.needs_render){
            //if(this.render_override)
                //this.onAnimateOverride();
            //else
            for(var i = 0; i < this.animate_funcs.length; i++){
                if(this.animate_funcs[i])
                    this.animate_funcs[i](this);
            }
            this.render();
            //this.anaglyph.render(this.scene, this.camera);
            //this.controls.update();
            this.animationID = requestAnimationFrame(function() {
                me.doAnimate()
            });
        } else
            this.animationID = null;


    },

    savePng : function(){
        var c = this.getEl().dom;
        var d=c.toDataURL("image/png");
        var w=window.open('about:blank','image from canvas');
        w.document.write("<img src='"+d+"' alt='from canvas'/>");
    }

});
