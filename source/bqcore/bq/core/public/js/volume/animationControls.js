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


//////////////////////////////////////////////////////////////////
//
// Load slider
//
//////////////////////////////////////////////////////////////////


Ext.define('BQ.viewer.Volume.loadSlider',{
    extend: 'Ext.slider.Multi',
    alias: 'widget.load_slider',
    cls: 'key-slider',
    height: 40,
    constructor : function(config) {
        this.callParent(arguments);
        return this;
    },

    initComponent : function(){
	    this.frameArray = new Array();
	    this.callParent();
    },

    setSize : function(N){
        this.N = N;
        for(var i = 0; i < this.N; i++){
            this.frameArray.push(0);
        }
	    var me = this;

    },

    afterRender: function(){
	    this.svgUrl = "http://www.w3.org/2000/svg";
	    this.svgdoc = document.createElementNS(this.svgUrl, "svg");
	    this.svgdoc.setAttributeNS(null, 'class', 'tick-slider');
	    this.svgdoc.setAttributeNS(null, 'width', this.getWidth());
	    this.svgdoc.setAttributeNS(null, 'height', this.getHeight());

        this.el.dom.appendChild(this.svgdoc);
	    this.svgTicks = document.createElementNS(this.svgUrl, "g");
	    this.svgTicks.setAttributeNS(null, 'class', 'tick-slider');
	    this.svgdoc.appendChild(this.svgTicks);
	    this.drawTicks();
	    this.callParent();
    },

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
        var defs = document.createElementNS(this.svgUrl, "defs");
        var grad = document.createElementNS(this.svgUrl, "linearGradient");
        grad.setAttributeNS(null, 'id', config.id);

        if (config.vertical){
            grad.setAttributeNS(null, 'x1', '0%');
            grad.setAttributeNS(null, 'y1', '0%');
            grad.setAttributeNS(null, 'x2', '0%');
            grad.setAttributeNS(null, 'y2', '100%');
        }
        grad.setAttributeNS(null, 'gradientTransform', 'rotate(' + config.angle + ')');
        defs.appendChild(grad);
        for (var i = 0; i < stops.length; i++) {
            var color = stops[i].color;
            var stop = document.createElementNS(this.svgUrl, "stop");
            stop.setAttributeNS(null, 'offset', stops[i].offset + '%');
            stop.setAttributeNS(null, 'stop-color', 'rgba(' +
            color[0] + ', ' +
            color[1] + ', ' +
            color[2] + ', ' +
            color[3] + ')');
            grad.appendChild(stop);
        }
        return defs;
    },

    drawTicks : function(canvas){
        if (this.frameArray.length == 1) return;
       while (this.svgdoc.lastChild) {
            this.svgdoc.removeChild(this.svgdoc.lastChild);
        }

        var grad1 = this.genGradient({
            id : 'Load-Tick',
            angle : 0,
            vertical : true
        },[{
            offset : 0,
            color : [0, 0, 0, 0.0]
        },{
            offset : 20,
            color : [200, 200, 200, 1.0]
        },{
            offset : 60,
            color : [200, 200, 200, 1.0]
        },{
            offset : 100,
            color : [0, 0, 0, 0.0]
        } ]);

        this.svgdoc.appendChild(grad1);

        var N = this.frameArray.length;
        var w = this.getWidth();
	    var h = this.getHeight();
        var path = '';

        var tic = this.tic;
        var xstart = 6;
        var xrem = w - xstart-8;
	    for(var i = 0; i < this.frameArray.length; i++){
	        var x0, y0, x1, y1;
	        //x0 = 0.87 + 98.2*i/(N-1) + '%';
	        var op = this.frameArray[i] ? 0.9 : 0.2;

            x0 = xstart + xrem*i/(N-1);
            x1 = x0;
            var wi = 0.6*1/N*w;
            var rect = document.createElementNS(this.svgUrl, "rect");
	        rect.setAttributeNS(null, 'x', x0);
            rect.setAttributeNS(null, 'y', 0.25*h);
            rect.setAttributeNS(null, 'width', wi);
            rect.setAttributeNS(null, 'height', 0.5*h);
            rect.setAttributeNS(null, 'fill-opacity', op);
            rect.setAttributeNS(null, 'stroke', 'none');
            //rect.setAttributeNS(null, 'stroke', 'gray');
            rect.setAttributeNS(null, 'fill', 'url(#Load-Tick)');
            //rect.setAttributeNS(null, 'fill', 'rgba(255,0,0,1)');

            this.svgdoc.appendChild(rect);
            //path += '<line x1=' + x0 + ' y1=' + y0 + ' x2=' + x1 + ' y2=' + y1 +
		    //    ' stroke = gray stroke-width=1.5 opacity = 0.7 fill="none" /></line>';
	    }
/*
	    var Start = this.startFrame;
	    var End   = this.endFrame;
	    var tic = this.tic;
	    var N = this.frameArray.length;
	    var path = '';
	    for(var i = 0; i < this.frameArray.length; i++){
	        var x0, y0, x1, y1, w;
	        x0 = 0.83 + 98.2*i/(N-1) + '%';
	        w = 60*1/N + '%';
            x1 = x0;
	        if(i%tic == 0){
		        y0 = '25%';
		        y1 = '75%';
	        } else {
		        y0 = '40%';
		        y1 = '60%';
	        }
            var op = this.frameArray[i] ? 0.9 : 0.2;
            path += '<rect x="'+x0+'" y="30%" width="'+w+'" height="40%"' +
                'style="fill:url(#Load-Tick);stroke:none;stroke-width:1;fill-opacity:'+op+';stroke-opacity:0.9" />';

	    }
*/
        var back = ['<rect ',
                    'x="0" y="25%"',
                    'rx="6" ry="6"',
                    'width="100%"',
                    'height="50%"',
                    'fill="#E5E5E3"',
                    '/>'].join(' ');
        //var back = '<rect x="0%" y="25%" rx="6" ry="6" width="100%" height="50%" style="fill:#FAEBD7"></rect>';

	    //this.svgTick.innerHTML = grad1 + back + path;
    },
});


//////////////////////////////////////////////////////////////////
//
// playback controller
//
//////////////////////////////////////////////////////////////////


Ext.define('BQ.viewer.Volume.playbackcontroller',{
    extend: 'Ext.container.Container',
    alias: 'widget.playback_control',
    border: false,
    endFrame: 1,
    enableTextSelection: false,
    layout: {
	    type: 'vbox',
	    align : 'stretch',
	    //pack  : 'start',
    },

    initComponent : function(){
	    var numFrames = 128;
	    this.loop = false;
	    this.sampleRate = 16;
	    var me = this;

	    this.timeSlider = Ext.create('BQ.viewer.Volume.loadSlider', {
	        minValue: 0,
	        flex: 1,

	        listeners: {
		        change: function(slider, value) {
		            var ratio = (value)/(this.timeSlider.maxValue-1);
		            //this.panel3D.setCurrentTimeRatio(ratio);
                    this.panel3D.setCurrentTime(value);
                    if(this.playButton.pressed){
                        this.panel3D.updateTextureUniform();
                        this.panel3D.setSampleRate(this.sampleRate);
                        this.panel3D.canvas3D.render();
                    }
                        else
		                    this.panel3D.rerender(this.sampleRate);
		            this.frameNumber.setText((value+1) + "/" + this.endFrame);
		        },
		        scope:me
	        }
	    });

	    this.playButton = Ext.create('Ext.Button', {
	        cls: 'bq-btn-play',
	        enableToggle: true,
	        handler: function(){
		        requestAnimationFrame(function() {me.doAnimate()});

	        },

	        scope:me,
	    });

	    this.frameNumber = Ext.create('Ext.toolbar.TextItem', {
	        text: "1/1",
	    });

        this.endFrame = this.panel3D.dims.t;
        this.timeSlider.setSize(this.endFrame);
		this.timeSlider.setMaxValue(this.endFrame - 1);
		this.frameNumber.setText("1/" + this.endFrame);
	    var toolbar = {
            xtype: 'toolbar',
            cls: 'tool-2',
	        items:[this.playButton,
                   this.timeSlider,
		           this.frameNumber,
                  ],
	    };
	    Ext.apply(this, {
	        items:[toolbar]
	    });

	    this.setLoading(true);

        this.panel3D.on({
            setquality: function(vol){
                me.sampleRate = vol.maxSteps;
            }
        });
	    this.panel3D.on({
	        loaded: function(){

	        },
	        scope: me,
	    });
	    this.callParent();
    },

    setLoaded : function(t){
        this.timeSlider.frameArray[t] = 1;
        this.timeSlider.drawTicks();
    },

    resetBuffers : function(t){
        this.timeSlider.frameArray = [];
        this.timeSlider.setSize(this.endFrame);
        this.timeSlider.drawTicks();
    },

    doAnimate : function(){
	    var me = this;
	    if(this.playButton.pressed == true){
	        var newVal = parseInt(this.timeSlider.getValue())+1;
	        var maxVal = this.timeSlider.maxValue;
	        newVal = newVal > maxVal ? 0 : newVal;
	        this.timeSlider.setValue(0,newVal,false);

	        requestAnimationFrame(function() {me.doAnimate()});
	    }
    },

});

//////////////////////////////////////////////////////////////////
//
// keyframe Thumb
//
//////////////////////////////////////////////////////////////////


Ext.define('BQ.viewer.Volume.Thumb',{
    extend: 'Ext.slider.Thumb',

    mixins : {
	    observable : 'Ext.util.Observable'
	},

    constructor: function (config) {
        this.callParent(arguments);
        this.mixins.observable.constructor.call(this, config);
        this.addEvents('dblclick');
    },

    render : function(){
        this.callParent(arguments);
        var me = this;
        this.el.dom.ondblclick = function(){
            me.fireEvent('dblclick', me);
        };
    },

    bringToFront: function() {
        this.callParent(arguments);
        this.fireEvent('click', this);
    },
});

//////////////////////////////////////////////////////////////////
//
// keyframe slider
//
//////////////////////////////////////////////////////////////////


Ext.define('BQ.viewer.Volume.keySlider',{
    extend: 'Ext.slider.Multi',
    alias: 'widget.key_slider',
    cls: 'key-slider',
    height: 40,
    constructor : function(config) {
        this.callParent(arguments);
        return this;
    },

    initComponent : function(){
	    this.keyArray = new Array();
	    this.autoKey = false;
	    this.editKey = false;
	    this.addKey = false;
	    this.removeKey = false;

        this.insertDist = 2;
	    this.sampleRate = 128;
	    this.timeValue = 0;
	    var me = this;
        this.on('resize', this.onresize);
	    this.callParent();
    },

    dragFunc: function(){
	    var me = this;
	    if(!me.drag) return;
	    var dx = event.clientX - me.currentX;
	    me.currentMatrix[4] += dx;
	    var newMatrix = "matrix(" + me.currentMatrix.join(' ') + ")";
	    me.svgSlider.setAttributeNS(null, "transform", newMatrix);
	    me.currentX = window.event.clientX;

	    me.dragFunc();
    },

    afterRender: function(){
	    this.svgUrl = "http://www.w3.org/2000/svg";
	    this.svgdoc = document.createElementNS(this.svgUrl, "svg");
	    this.svgdoc.setAttributeNS(null, 'class', 'tick-slider');
	    //this.svgdoc.setAttributeNS(null, 'width', "100%");
	    //this.svgdoc.setAttributeNS(null, 'height',"100%");

        this.el.dom.appendChild(this.svgdoc);
	    //this.svgTicks = document.createElementNS(this.svgUrl, "g");
	    //this.svgTicks.setAttributeNS(null, 'class', 'tick-slider');
	    //this.svgdoc.appendChild(this.svgTicks);
	    this.drawTicks();

	    var me = this;
	    this.timeThumb = new Ext.slider.Thumb({
            ownerCt     : me,
            ownerLayout : me.getComponentLayout(),
            value       : 0,
            slider      : me,
            index       : 999,
            constrain   : me.constrainThumbs,
            disabled    : !!me.readOnly,
	        cls : 'x-slider-head',
        });
	    this.timeThumb.render();
	    this.thumbs.forEach(function(e,i,a){
            e.render();
        });
        this.callParent();
    },

    drawTicks : function(canvas){
	    var Start = this.startFrame - 1;
	    var End   = this.endFrame + 1;
	    var tic = this.tic;
	    var N = End - Start;
        var w = this.getWidth();
	    var h = this.getHeight();
        var path = '';

       while (this.svgdoc.lastChild) {
            this.svgdoc.removeChild(this.svgdoc.lastChild);
        }

        var xstart = 7;
        var xrem = w - xstart-7;
	    for(var i = 0; i < N; i++){
	        var x0, y0, x1, y1;
	        //x0 = 0.87 + 98.2*i/(N-1) + '%';
	        x0 = xstart + xrem*i/(N-1);
            x1 = x0;
            y0 = (i%tic == 0) ? 0.25*h : 0.4*h;
	        y1 = (i%tic == 0) ? 0.75*h : 0.6*h;
            var line = document.createElementNS(this.svgUrl, "line");
	        line.setAttributeNS(null, 'x1', x0);
            line.setAttributeNS(null, 'y1', y0);
            line.setAttributeNS(null, 'x2', x1);
            line.setAttributeNS(null, 'y2', y1);
            line.setAttributeNS(null, 'opacity', 0.7);
            line.setAttributeNS(null, 'stroke-width', 1.5);
            line.setAttributeNS(null, 'stroke', 'gray');
            line.setAttributeNS(null, 'fill', 'none');
            this.svgdoc.appendChild(line);
            //path += '<line x1=' + x0 + ' y1=' + y0 + ' x2=' + x1 + ' y2=' + y1 +
		    //    ' stroke = gray stroke-width=1.5 opacity = 0.7 fill="none" /></line>';
	    }

	    //this.svgdoc.innerHTML = path;

    },


    //----------------------------------------------------------------------
    // event handlers
    //----------------------------------------------------------------------


    changecomplete: function(){
	    this.sortKeys();
	    this.callParent();
    },

    onresize: function(){
        this.drawTicks();
    },

    /**
     * Creates a new thumb and adds it to the slider
     * @param {Number} [value=0] The initial value to set on the thumb.
     * @return {Ext.slider.Thumb} The thumb
     */
    addThumb: function(value) {
        var me = this,
            thumb = new BQ.viewer.Volume.Thumb({
                ownerCt     : me,
                ownerLayout : me.getComponentLayout(),
                value       : value,
                slider      : me,
                index       : me.thumbs.length,
                constrain   : me.constrainThumbs,
                disabled    : !!me.readOnly,
                listeners : {
                    click : function(thumb){
                        var val = thumb.value;
                        me.setValue(999, val, false, false);
                        me.fireEvent('cursormove', me);
                    },
                    scope: me,
                }
            });

        me.thumbs.push(thumb);

        //render the thumb now if needed
        if (me.rendered) {
            thumb.render();
        }

        return thumb;
    },

    setValue : function(index, value, animate, changeComplete) {
        var me = this,
        thumbs = me.thumbs,
        thumb, len, i, values;

        if(index === 0) return; // can't move the 0th key.  Ext

        if(index === 999){
	        thumb = me.timeThumb;
	    }

	    else{
            if (Ext.isArray(index)) {
		        values = index;
		        animate = value;

		        for (i = 0, len = values.length; i < len; ++i) {
                    thumb = thumbs[i];
                    if (thumb) {
			            me.setValue(i, values[i], animate);
                    }
		        }
		        return me;
            }

            thumb = me.thumbs[index];
	    }
        // ensures value is contstrained and snapped
        value = me.normalizeValue(value);

        if (value !== thumb.value && me.fireEvent('beforechange', me, value, thumb.value, thumb) !== false) {
            thumb.value = value;
            if (me.rendered) {
                // TODO this only handles a single value; need a solution for exposing multiple values to aria.
                // Perhaps this should go on each thumb element rather than the outer element.
                me.inputEl.set({
                    'aria-valuenow': value,
                    'aria-valuetext': value
                });

                thumb.move(me.calculateThumbPosition(value), Ext.isDefined(animate) ? animate !== false : me.animate);

                me.fireEvent('change', me, value, thumb);
                me.checkDirty();
                if (changeComplete) {
                    me.fireEvent('changecomplete', me, value, thumb);
                }
            }
        }
        return me;
    },


    onClickChange : function(trackPoint) {
        var me = this,
        thumb, index;

        // How far along the track *from the origin* was the click.
        // If vertical, the origin is the bottom of the slider track.

        //find the nearest thumb to the click event
        //console.log(trackPoint);
        thumb = me.getNearest(trackPoint);
	    if (thumb.index == 999)
            if (!thumb.disabled) {
                index = thumb.index;
                me.setValue(index, Ext.util.Format.round(me.reversePixelValue(trackPoint),
						                                 me.decimalPrecision), undefined, true);
	        }
    },

    getCurrentTime : function(){

	    return this.timeThumb.value;
    },

    setHeadValue : function( value, animate ){
	    this.setValue(999,value,animate,true);
    },

    getNearest: function(trackPoint){
	    var me = this;

	    clickValue = me.reversePixelValue(trackPoint);
	    var value = this.timeThumb.value;
	    dist = Math.abs(value - clickValue);
	    if (dist < 10) return this.timeThumb;
	    else {
	        return this.callParent(arguments);
	    }
    },

    onMouseDown : function(e) {
        //we override the onMouseDown listener and detect if we're within a certain part of the slider
        //if we are we emit an event: onClickKey, else we move the track thumb
	    var ymin    = this.getY();
	    var height = this.getHeight();
	    var yclick = e.getPageY();
	    var yrel = yclick - ymin;
	    var rat = yrel/height;
	    var me = this;

	    var trackPoint = this.getTrackpoint(e.getXY());
	    var newVal =  Ext.util.Format.round(me.reversePixelValue(trackPoint), me.decimalPrecision);

	    if(rat < 0.75 && rat > 0.25){
	        this.callParent(arguments);
            var thumb = this.getNearest(trackPoint);
            this.fireEvent('clickkey', this, newVal, thumb);
	    }else{

	        this.setValue(999, newVal, undefined, true);
	    }
        if(this.addKey){

        }
    },


    //----------------------------------------------------------------------
    // get keyframe info
    //----------------------------------------------------------------------

    getFloorFrame : function(value){
	    var i0 = 0; //zero is the default floor frame

	    for(var i = 0; i < this.keyArray.length - 1; i++){
	        var x0 = this.keyArray[i].time.value;
	        var x1 = this.keyArray[i+1].time.value;
	        if(value == x0){
		        i0 = i;
	        }
	        else if(value > x0 && value < x1){
		        i0 = i;
	        }
	        else if(value >= x1){
		        i0 = i+1;
	        }
	    }
	    //console.log('floor: ', i0);
	    return i0;
    },

    getNearestFrame : function(inTime){
        //unlike the getNearest function, this just returns an index
	    var i0 = 0, dist = 9999;
	    for(var i = 0; i < this.keyArray.length; i++){
	        var itTime = this.keyArray[i].time.value;
	        var cdist = Math.abs(inTime-itTime);
	        if(cdist < dist){
		        dist = cdist;
		        i0 = i;
	        }
	    }
	    return i0;
    },

    //----------------------------------------------------------------------
    // Get interpolated state at a given point
    //----------------------------------------------------------------------

    getInterpolatedValue : function(val, scope){
	    //if(scope.keyArray.length < 2) return;

        var i = scope.getFloorFrame(val);

        if(i == scope.keyArray.length - 1){

            var q0 = (new THREE.Quaternion).setFromEuler(scope.keyArray[i].rotation);
            var r0 = new THREE.Euler(0,0,0,'XYZ').setFromQuaternion(q0,'XYZ');
            var t0 = scope.keyArray[i].target.clone();
            var p0 = scope.keyArray[i].position.clone();
            return {pos:  p0,
                    targ: t0,
		            rot:  r0,
                    quat: q0};
        }

        var i0 = i;
	    var i1 = i >= scope.keyArray.length-1 ? i : i+1;
	    //console.log(i, i0, i1, this.keyArray.length);
	    var t1 = scope.keyArray[i1].time.value;
	    var t0 = scope.keyArray[i0].time.value;

	    var t = i >= scope.keyArray.length-1 ? 1 : (val-t0)/(t1-t0);

	    var q0 = (new THREE.Quaternion).setFromEuler(scope.keyArray[i0].rotation);
	    var q1 = (new THREE.Quaternion).setFromEuler(scope.keyArray[i1].rotation);
	    var qi = q0.clone();
	    qi.slerp(q1,t);
	    var ri = new THREE.Euler(0,0,0,'XYZ').setFromQuaternion(qi,'XYZ');

        /*
	      var q0 = (new THREE.Quaternion).setFromEuler(this.keyArray[i+0].rotation);
	      var q1 = (new THREE.Quaternion).setFromEuler(this.keyArray[i+1].rotation);
	      var x0 = q0.x;
	      var x1 = q1.x;
	      var y0 = q0.y;
	      var y1 = q1.y;
	      var z0 = q0.z;
	      var z1 = q1.z;
	      var w0 = q0.w;
	      var w1 = q1.w;

	      var qi = new THREE.Quaternion(x0*(1.0-t) + x1*(t), y0*(1.0-t) + y1*(t), z0*(1.0-t) + z1*(t), w0*(1.0-t) + w1*(t));
	      qi.normalize();
	      var ri = new THREE.Euler(0,0,0,'XYZ');
	      ri.setFromQuaternion(qi,'XYZ');
        */
        /*
	      var x0 = this.keyArray[i+0].rotation.x;
	      var x1 = this.keyArray[i+1].rotation.x;
	      var y0 = this.keyArray[i+0].rotation.y;
	      var y1 = this.keyArray[i+1].rotation.y;
	      var z0 = this.keyArray[i+0].rotation.z;
	      var z1 = this.keyArray[i+1].rotation.z;
	      var ri = new THREE.Euler(x0*(1.0-t) + x1*(t), y0*(1.0-t) + y1*(t), z0*(1.0-t) + z1*(t), 'XYZ');
        */


	    var t0 = scope.keyArray[i0].target.clone();
	    var t1 = scope.keyArray[i1].target.clone();
	    var ti = t0.clone(); ti.lerp(t1,t);

	    var p0 = scope.keyArray[i0].position.clone();
	    var p1 = scope.keyArray[i1].position.clone();

	    var d0 = p0.clone(); d0.sub(t0);
	    var d1 = p1.clone(); d1.sub(t1);

	    var l0 = d0.length();
	    var l1 = d1.length();
	    var li = l0*(1.0-t) + l1*(t);

	    var pi = new THREE.Vector3(0.0,0.0,li);
	    pi.applyQuaternion(qi).add(ti);
	    //p0.lerp(p1,t);
	    return {pos:  pi,
                targ: ti,
		        rot:  ri,
                quat: qi};
    },

    //----------------------------------------------------------------------
    // Get the cameras current state
    //----------------------------------------------------------------------

    getCameraState: function(value, scope){
	    var rot  = scope.panel3D.canvas3D.camera.rotation.clone();
	    var pos  = scope.panel3D.canvas3D.controls.posLocal.clone();
	    var targ = scope.panel3D.canvas3D.controls.target.clone();
        var quat = scope.panel3D.canvas3D.camera.quaternion.clone();
        return {pos:  pos,
                targ: targ,
		        rot:  rot,
                quat: quat};
    },

    //----------------------------------------------------------------------
    // update the current keyframe array
    //----------------------------------------------------------------------

    updateCurrentKeyFrame: function(updateFunc, insert){
	    var curTime = this.getCurrentTime();
	    var nearestFrame = this.getNearestFrame(curTime);
	    var nearestTime = this.keyArray[nearestFrame].time.value;

	    var dif = Math.abs(curTime - nearestTime);
	    //if(!this.autoKey) return;

	    if(dif < this.insertDist){
            //here we are cloning the current key frame
	        var state = updateFunc(curTime, this);
            this.keyArray[nearestFrame].rotation = state.rot.clone();
	        this.keyArray[nearestFrame].position = state.pos.clone();
	        this.keyArray[nearestFrame].target   = state.targ.clone();
	        var lastFrame = this.keyArray.length-1;
	        if(nearestFrame == 0 && this.loop == true ){
		        this.keyArray[lastFrame].rotation = state.rot.clone();
		        this.keyArray[lastFrame].position = state.pos.clone();
		        this.keyArray[lastFrame].target   = state.targ.clone();
	        }
	        if(nearestFrame == lastFrame && this.loop == true ){
		        this.keyArray[0].rotation = state.rot.clone();
		        this.keyArray[0].position = state.pos.clone();
		        this.keyArray[0].target   = state.targ.clone();
	        }
	    }
	    else{
	        if(!insert) return;
            this.addKeyFrame(curTime, updateFunc);
        }
    },

    sortKeys : function(){
	    this.keyArray.sort(function(a,b){
	        return (a.time.value-b.time.value);
	    });

	    this.thumbs.sort(function(a,b){
	        return (a.value-b.value);
	    });

	    for(var i = 0; i < this.thumbs.length; i++){
	        this.thumbs[i].index = i;
	    }
    },

    scaleKeys : function(newScale){
	    var oldScale = this.maxValue;
	    if(oldScale == 0) return;
	    var scale = newScale/oldScale;

	    for(var i = 0; i < this.thumbs.length; i++){
	        var newVal = this.thumbs[i].value*scale;
	        this.thumbs[i].value = newVal;
	    }
    },

    //----------------------------------------------------------------------
    // add and remove key frames frome array
    //----------------------------------------------------------------------

    addKeyFrame : function(frame, addFunc){
	    //this adds a keyframe based given an input slider value
	    var hit = false;

	    var outKey;
	    for(var i = 0; i < this.keyArray.length; i++){
	        var pos   = this.keyArray[i].time.value;
	        var fudge = 0.01*this.maxValue;
	        var dist  = Math.abs(pos-frame);
	        if(dist < fudge){
		        hit = true;
		        outKey =  this.keyArray[i];
	        }
	    }
        if(hit) return;

        //var up = this.panel3D.canvas3D.controls.position.up.clone();
	    var thumb;
	    if(frame == 0) {
		    thumb = this.thumbs[0];
	    }
	    else thumb = this.addThumb(frame);

        var state = addFunc(thumb.value, this);

        var rot  = state.rot;
	    var pos  = state.pos;
	    var targ = state.targ;

        var newKey = {time:thumb,
			          rotation: rot,
			          position: pos,
			          target: targ,}
	    this.keyArray.push(newKey);
	    this.current = this.keyArray.length - 1;
	    outKey = newKey;

        this.sortKeys();
	    return outKey;
    },

    removeKeyFrame : function(frame){

	    if(frame < 1) return;
	    var it = -1;
	    var minDist = 999;
	    for(var i = 0; i < this.thumbs.length; i++){
		    var dist = Math.abs(frame - this.thumbs[i].value);
		    if(dist < this.insertDist){
		        it = i;
		        minDist = dist;
		    }
	    }

	    if(minDist > this.insertDist) return;
        if(it < 1) return;

		var innerEl = this.thumbs[it].ownerCt.innerEl.dom;
		innerEl.removeChild(this.thumbs[it].el.dom);
		this.thumbs.splice(it,1);
		for(var i = 0; i < this.thumbs.length; i++){
		    this.thumbs[i].index = i;
		}

	    var ik = this.getNearestFrame(frame);
	    this.keyArray.splice(ik,1);

	},

});

//////////////////////////////////////////////////////////////////
//
// animation controller
//
//////////////////////////////////////////////////////////////////

Ext.define('BQ.viewer.Volume.animationcontroller',{
    extend: 'Ext.container.Container',
    alias: 'widget.anim_control',
    border: false,
    enableTextSelection: false,
    layout: {
	    type: 'vbox',
	    align : 'stretch',
	    //pack  : 'start',
    },

    initComponent : function(){
	    var numFrames = 128;
	    //console.log("number of frames: ", numFrames);
	    this.startFrame = 1;
	    this.endFrame = numFrames > 1 ? numFrames :128;
	    this.chk      = 0;
	    this.tic      = 10;
	    this.lastX    = 0;
	    this.current  = 0;
	    this.renderSteps = 8;
	    this.overCanvas = false;
	    this.insertDist = 3;
	    if(this.panel3D.dims)
	        this.volumeEndFrame = this.panel3D.dims.t;
	    else
	        this.volumeEndFrame = 1;
	    this.loop = false;
	    this.sampleRate = 128;
	    var me = this;
		var controls = this.panel3D.canvas3D.controls;
        var curCamera = this.panel3D.canvas3D.camera;

        var clearState = function(){
            me.editKey = false;
            me.addKey = false;
            me.removeKey = false;
            me.autoKey = false;
        };


	    this.keySlider = Ext.create('BQ.viewer.Volume.keySlider', {
	        startFrame: this.startFrame,
	        endFrame: this.endFrame,
	        tic:      this.tic,
	        panel3D: this.panel3D,
	        autoKey: false,
	        addKey: false,
	        removeKey: false,
	        editKey: false,

            flex: 1,
            listeners: {
                //beforechange: f
		        change: function(slider, value, thumb) {
		            //console.log(slider, value);
		            if(thumb.index === 999){
			            if (this.keySlider.keyArray.length < 2) return;
			            //var rat = value/slider.maxValue;
                        controls.enabled = false;


                        var ratio = (value)/(slider.maxValue);
			            this.panel3D.setCurrentTimeRatio(ratio);
			            this.panel3D.setSampleRate(this.sampleRate);
                        this.panel3D.rerender(this.sampleRate);


			            var interp = this.keySlider.getInterpolatedValue(value, this.keySlider);
                        //curCamera.rotation.copy(interp.rot);
                        curCamera.quaternion.copy(interp.quat);
			            curCamera.position.copy(interp.pos);


                        var newTarg = new THREE.Vector3(0,0,1);
                        var newUp   = new THREE.Vector3(0,1,0);
                        //newTarg.applyQuaternion(interp.quat);
                        //newUp.applyQuaternion(interp.quat);
                        controls.target.copy(interp.targ);
                        controls.object.quaternion.copy(interp.quat);
                        controls.posLocal.copy(interp.pos);

                        //this.panel3D.canvas3D.controls.update();

			            this.keySlider.panelCamera.position.copy( this.panel3D.canvas3D.camera.position );
			            this.keySlider.panelCamera.quaternion.copy( this.panel3D.canvas3D.camera.quaternion );
			            this.keySlider.panel3D.canvas3D.camera = this.keySlider.panelCamera;

                        this.panel3D.updateTextureUniform();
                        this.panel3D.setSampleRate(this.sampleRate);
                        this.panel3D.canvas3D.render();

			            var volFrame = Math.floor(ratio*this.volumeEndFrame);
			            this.frameNumber.setText(volFrame+1 + "/" + this.volumeEndFrame);
		            }
		        },
		        changeComplete: function(slider, value, thumb){
                    this.panel3D.canvas3D.controls.enabled = true;
                    //this.panel3D.canvas3D.controls.update();
		            this.panel3D.canvas3D.controls.object = this.panel3D.canvas3D.camera;
		            this.panel3D.canvas3D.controls.noRotate = false;
		            this.panel3D.canvas3D.controls.noPan = false;
                },
                clickkey: function(slider, value, key){
                    if(this.addKey){
                        var frame = this.keySlider.keyArray[this.keySlider.getNearestFrame(value)];
                        if(Math.abs(frame.time.value - value) > 3){
                            this.keySlider.addKeyFrame(value, this.keySlider.getInterpolatedValue);
                        }
                    }
		            if(this.removeKey){
                        var frame = this.keySlider.keyArray[this.keySlider.getNearestFrame(value)];
                        if(Math.abs(frame.time.value - value) < 3){
                            this.keySlider.removeKeyFrame(value);
                        }
                    }
                },
                cursormove: function(slider){
                    if(this.removeKey) return;
                    setTimeout(function(){
                        clearState();
                        me.queryById('anim-edit').toggle(true);
                        me.editKey = true;
                    },10);
                },
		        scope:me
            },
	    });

        var editKeyButton = Ext.create('Ext.Button', {
	        text: 'edit',
            itemId: 'anim-edit',
            enableToggle: true,
            toggleGroup: 'anim-edit',
	        toggleHandler: function(button){
                clearState();
		        this.editKey = button.pressed;
                //this.keySlider.addKeyFrame(this.keySlider.getCurrentTime());

	        },
	        scope:me,
	    });

	    var addKeyButton = Ext.create('Ext.Button', {
	        text: '+',
            itemId: 'anim-add',
            enableToggle: true,
            toggleGroup: 'anim-edit',
	        toggleHandler:function(button){
                clearState();
		        this.addKey = button.pressed;
            },
	        scope:me,
	    });

	    var removeKeyButton = Ext.create('Ext.Button', {
	        text: '-',
            itemId: 'anim-sub',
            enableToggle: true,
            toggleGroup: 'anim-edit',
	        toggleHandler:function(button){
                clearState();
                this.removeKey = button.pressed;
            },
	        scope:me,
	    });

	    var autoKeyButton = Ext.create('Ext.Button', {
	        enableToggle: true,
            itemId: 'anim-auto',
	        text: 'auto',
            toggleGroup: 'anim-edit',
	        toggleHandler: function(button, pressed) {
                clearState();
                this.autoKey = button.pressed;
		        //this.keySlider.autoKey = this.keySlider.autoKey ? false:true;

	        },
	        scope:me,
	    });


	    var playButton = Ext.create('Ext.Button', {
	        //iconCls: 'playbutton',
            cls: 'bq-btn-play',
	        enableToggle: true,

	        handler: function(button){
		        if(button.pressed) {
		            this.keySlider.panelCamera.position.copy( this.panel3D.canvas3D.camera.position );
		            this.keySlider.panelCamera.rotation.copy( this.panel3D.canvas3D.camera.rotation );
		            this.keySlider.panel3D.canvas3D.camera = this.keySlider.panelCamera;
		            this.isPlaying = true;
                    requestAnimationFrame(function() {me.doAnimate()});
                    //if() button.iconCls = 'pausebutton';
		            //else button.setText('autokey on');
		        }
		        else this.isPlaying = false;

	        },

	        scope:me,
	    });



	    var pauseButton = Ext.create('Ext.Button', {
	        iconCls: 'pausebutton',
	        handler: function(){
		        this.isPlaying = false;
		        this.isRecording = false;
		        this.keySlider.timeSlider.setValue(0,false);
		        this.keySlider.panelCamera.position.copy( this.panel3D.canvas3D.camera.position );
		        this.keySlider.panelCamera.rotation.copy( this.panel3D.canvas3D.camera.rotation );
		        this.keySlider.panel3D.canvas3D.camera = this.keySlider.panelCamera;
	        },
	        scope:me,
	    });

	    var recordButton = Ext.create('Ext.Button', {
            itemId: 'btn_record',
	        iconCls: 'recordbutton',
	        text: 'Record',
	        handler: function(btn) {
                if(!Ext.isChrome){
                    BQ.ui.warning("Unfortunately exporting movies is currently not supported on your Browser.  </br>" +
                                "Please use Chrome.</br>");
                    return;
                }

                btn.disable();
                this.keySlider.timeThumb.value = 0;
		        this.isRecording = true;
		        var video = new Whammy.Video(15);
		        this.renderSteps = 256;
		        this.doRecord(video);
	        },
	        scope:me,
	    });


	    this.numKeyFramesField = Ext.create('Ext.form.field.Number', {
            name: 'numberfield1',
            fieldLabel: 'Frames',
            value: this.endFrame,
            minValue: 4,
            maxValue: 10000,
            width: 200,
            listeners: {
		        change: function(field, newValue, oldValue) {
		            this.updateEndFrame(newValue);
		        },
		        scope:me
            },
	    });

	    this.frameNumber = Ext.create('Ext.toolbar.TextItem', {
	        text: "1/" + this.volumeEndFrame,
	    });
	    var toolbar1 = {
            xtype: 'toolbar',
			//cls : 'toolItem',
	        items:[recordButton,
	               { xtype: 'tbspacer', cls: 'record-spacer' },
                   editKeyButton,
                   addKeyButton,
		           removeKeyButton,
		           autoKeyButton,
		           '->',
		           this.numKeyFramesField
		          ],
	    };
	    var toolbar2 = {
            xtype: 'toolbar',
            cls: 'tool-2',
	        items:[playButton,this.keySlider,
		           this.frameNumber],
	    };

        this.panel3D.on({
            setquality: function(vol){
                me.sampleRate = vol.maxSteps;
            }
        });

	    Ext.apply(this, {
	        items:[toolbar1,
		           toolbar2,
		          ],
	    });

	    this.callParent();
    },



    afterRender : function(){
	    this.callParent();
	    var me = this;
	    var listener = function(){
            if(me.editKey || me.autoKey)
	            me.keySlider.updateCurrentKeyFrame(me.keySlider.getCameraState, false);
            if(me.autoKey)
                me.keySlider.updateCurrentKeyFrame(me.keySlider.getCameraState, true);
        }

        //this.keySlider.panel3D.canvas3D.el.addListener('mouseup',listener, me);
        this.keySlider.panel3D.canvas3D.getEl().on({
            //scope : this,
            mouseup : listener,
            mousewheel: listener,
            DOMMouseScrool: listener,
        });
    },

    afterFirstLayout : function(){
	    this.callParent();
	    this.keySlider.addKeyFrame(0, this.keySlider.getCameraState);
	    var me = this;
	    var width = this.panel3D.canvas3D.getWidth();
	    var height = this.panel3D.canvas3D.getHeight();

	    var aspect = width/height;

	    this.keySlider.animCamera = new THREE.PerspectiveCamera(20, aspect, .01, 100);
	    this.keySlider.animCamera.position.copy( this.keySlider.panel3D.canvas3D.camera.position );
	    this.keySlider.animCamera.rotation.copy( this.keySlider.panel3D.canvas3D.camera.rotation );
	    this.keySlider.panelCamera = this.keySlider.panel3D.canvas3D.camera;

        var defaultTime = this.panel3D.dims.t == 1 ? 128 : this.panel3D.dims.t;
        this.numKeyFramesField.setValue(defaultTime);
        //this.keySlider.drawTicks();
    },

    //----------------------------------------------------------------------
    // Animate and record stuff
    //----------------------------------------------------------------------
    updateEndFrame : function(newValue){
	    if(newValue > 9){
	        this.keySlider.scaleKeys(newValue);
	        this.keySlider.endFrame = newValue - 1;
	        this.keySlider.setMaxValue(newValue - 1);
	        this.keySlider.drawTicks();
	        this.numKeyFramesField.setValue(newValue);
	    }
    },



    doAnimate : function(){
	    var me = this;
	    if(this.isPlaying){
            this.panel3D.canvas3D.controls.enabled = false;
	        var maxTime = this.keySlider.maxValue;
	        var increment = maxTime/this.keySlider.endFrame;
	        var currentTime = (this.keySlider.timeThumb.value + increment)%maxTime;

	        this.keySlider.setHeadValue(currentTime,false);
	        requestAnimationFrame(function() {me.doAnimate()});
	    }
        this.panel3D.canvas3D.controls.enabled = true;
        this.panel3D.canvas3D.controls.update();
    },

    doRecord : function(video) {
	    var me = this;
	    //var context = this.panel3D.canvas3D.renderer.domElement.getContext('webgl');
	    var context = this.panel3D.canvas3D.renderer.context;
        video.add(context);
	    this.chk += 1;

	    var maxTime = this.keySlider.maxValue;
	    var increment = maxTime/this.keySlider.endFrame;
	    var currentTime = (this.keySlider.timeThumb.value + increment)%maxTime;
	    this.keySlider.setHeadValue(currentTime,false);
	    this.timeValue = currentTime;
	    if(currentTime > maxTime-2) {
	        var start_time = +new Date;
	        var output = video.compile();

	        var end_time = +new Date;
	        var url = webkitURL.createObjectURL(output);
	        window.open(url);
	        this.isRecording = false;
	        this.renderSteps = 8;
	        this.queryById('btn_record').enable();
	    }
	    if (this.isRecording) {
	        requestAnimationFrame(function() {me.doRecord(video)});
	    }

    },
});


function animationTool(volume, cls) {
	//renderingTool.call(this, volume);
    this.name = 'animation';
	this.cls = 'animateButton';
    this.base = renderingTool;
    this.base(volume, this.cls);
};

animationTool.prototype = new renderingTool();

animationTool.prototype.addUniforms = function(){
};


	//----------------------------------------------------------------------
	// Animation Panel
	//---------------------------------------------------------------------

animationTool.prototype.createAnimPanel = function () {
	var thisDom = this.volume.getEl().dom;
	this.animPanel = Ext.create('Ext.panel.Panel', {
		collapsible : false,
		header : false,
		renderTo : thisDom,
		cls : 'bq-volume-playback',
		items : [{
			xtype : 'anim_control',
			panel3D : this.volume,
		}],
	});
	this.volume.addFade(this.animPanel);
};

	//----------------------------------------------------------------------
	// Playback Panel
	//---------------------------------------------------------------------

animationTool.prototype.createPlaybackPanel = function () {
		var thisDom = this.volume.getEl().dom;
        this.playBack = Ext.create('BQ.viewer.Volume.playbackcontroller', {
		    panel3D: this.volume
        });
		this.playbackPanel = Ext.create('Ext.panel.Panel', {
				collapsible : true,
				header : false,
				renderTo : thisDom,
				cls : 'bq-volume-playback',
				items : [
                    this.playBack
				],
			});
		this.volume.addFade(this.playbackPanel);

};

animationTool.prototype.initControls = function(){
    var me = this;
    me.button.tooltip = 'Animation and time series playback';
    //this.volume.on('loaded', function () {});


    var showAnimPanel = function() {
        if(me.useAnimation == false){
            //this.
            me.playbackPanel.hide();
			me.animPanel.hide();
            return;
        }

        if(me.animStyle == 1) {
            me.playbackPanel.hide();
			me.animPanel.show();
        } else {
            me.playbackPanel.show();
			me.animPanel.hide();
        }
    };

	var toolMenuRadioHandler = function () {
		var
        radio1 = me.controls.queryById('toolRadio1'),
		radio2 = me.controls.queryById('toolRadio2');
		if (radio2.getValue()) {
            me.animStyle = 1;
		} else {
            me.animStyle = 2;
		}

        showAnimPanel();
		return;
	};

    var radioOpts = Ext.create('Ext.container.Container',{

		defaults : {
			xtype : 'radio',
			width : 200,
			name : 'tools',
			cls : 'toolItem',
            handler : toolMenuRadioHandler,
            scope : me,
        },

        items:[{
			fieldLabel : 'standard player',
			itemId : 'toolRadio1',
		}, {
			fieldLabel : 'animation player',
            checked : me,
			itemId : 'toolRadio2',
		},]
    });

    this.controls.add([radioOpts]);
    this.volume.on({
        loaded: function(){

            me.createPlaybackPanel();
            me.createAnimPanel();
            me.playbackPanel.hide();
            me.animPanel.hide();

            if(me.volume.dims.t > 1){
                me.button.toggle(true);
            }
            else
                me.button.toggle(false);
        },

        atlasloadedat: function (t) {
            me.playBack.setLoaded(t);
        },
        wipetexturebuffer: function () {
            if(me.playback)
                me.playBack.resetBuffers();
        }
    });
};

animationTool.prototype.toggle = function(button){
    radio1 = this.controls.queryById('toolRadio1'),
	radio2 = this.controls.queryById('toolRadio2');
    if(button.pressed){
        if(this.volume.dims.t == 1){
            radio2.setValue(true);
            this.animPanel.show();
        }
        else{
            radio1.setValue(true);
            this.playbackPanel.show();
        }
    }
    else{
        this.animPanel.hide();
        this.playbackPanel.hide();

    }
    /*
        this.transfer ^= 1;
        this.changed();
        //this..sceneVolume.setUniform('USE_TRANSFER', this.transfer);

        if (button.pressed) {
            this.volume.shaderConfig.transfer = true;
            this.volume.sceneVolume.setConfigurable("default",
                                             "fragment",
                                             this.volume.shaderConfig);

            this.volume.setModel('transfer', true);
        } else{
            this.volume.shaderConfig.transfer = false;
            this.volume.sceneVolume.setConfigurable("default",
                                             "fragment",
                                             this.volume.shaderConfig);

            this.volume.setModel('false', true);
        }

    if(this.transfer){
        var me = this;

        var data = this.transferData;
        this.transferEditor = Ext.create('BQ.viewer.volume.transfer.editor',{
            data: data,
            histogram: this.volume.model.histogram,
            gamma:     this.volume.model.gamma,
            dock : 'bottom',
            collapseDirection: 'bottom',
            expandDirection: 'top',
            height: 250,
            collapsible: true,
            cls : 'bq-volume-transfer',
            listeners: {
                change: function(){
                    me.changed();
                }
            }
        });

        this.volume.addDocked(this.transferEditor);
        //this.volume.southView.expand(true);
    }
    else{
        this.volume.removeDocked(this.transferEditor);
        //this.volume.southView.collapse();
        //this.volume.southView.remove(this.transferEditor);
    }
*/
    this.base.prototype.toggle.call(this,button);

};
