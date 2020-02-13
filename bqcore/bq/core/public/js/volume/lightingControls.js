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

function lightTool(volume, cls) {
	//renderingTool.call(this, volume);vect
    //this.label = 'gamma';
    this.label = 'lighting';
    this.name = 'light_loc';
    this.cls = 'lightButton';

	this.base = renderingTool;
    this.base(volume, this.cls);
};

lightTool.prototype = new renderingTool();

lightTool.prototype.addUniforms = function(){

      ////////////////////////////////
     //Light position
    ////////////////////////////////

    this.uniforms['lightPos'] = {name: 'LIGHT_POSITION', type: 'v3', val: this.lightObject.position};

      ////////////////////////////////
     //Phong uniforms
    ////////////////////////////////

    this.uniforms['ambient']    = {name: 'KA',
                                   type: 'f',
                                   val: 0.5,
                                   slider: true,
                                   min: 0,
                                   max: 100,
                                   def: 50,
                                   K: 0.01};
    this.uniforms['diffuse']    = {name: 'KD',
                                   type: 'f',
                                   val: 0.5,
                                   slider: true,
                                   min: 0,
                                   max: 100,
                                   def: 50,
                                   K: 0.01};
    this.uniforms['size']    = {name: 'SPEC_SIZE',
                                type: 'f',
                                val: 0.5,
                                slider: true,
                                min: 1,
                                max: 100,
                                def: 50,
                                K: 1.0};
    this.uniforms['intensity']    = {name: 'SPEC_INTENSITY',
                                     type: 'f',
                                     val: 0.5,
                                     slider: true,
                                     min: 0,
                                     max: 100,
                                     def: 50,
                                     K: 0.25};

      ////////////////////////////////
     //Deep Shading uniforms
    ////////////////////////////////

    this.uniforms['samples']    = {name: 'LIGHT_SAMPLES',
                                   type: 'i',
                                   val: 4};
    this.uniforms['depth']    = {name: 'LIGHT_DEPTH',
                                 type: 'f',
                                 val: 0.5,
                                 slider: true,
                                 min: 0,
                                 max: 100,
                                 def: 50,
                                 K: 0.02};

    this.uniforms['dispersion']    = {name: 'DISPERSION',
                                      type: 'f',
                                      val: 0.5,
                                      slider: true,
                                      min: 0,
                                      max: 100,
                                      def: 50,
                                      K: 0.02};

    this.uniforms['absorption']    = {name: 'ABSORPTION',
                                      type: 'f',
                                      val: 0.5,
                                      slider: true,
                                      min: 0,
                                      max: 100,
                                      def: 50,
                                      K: 0.05};
    //this.initUniforms();
};

lightTool.prototype.initControls = function(){
    this.button.tooltip = 'Lighting controls';

      ////////////////////////////////////////////
     //Manipulate the lighting of the object
    ////////////////////////////////////////////
    var me = this;

    this.sceneVolume = this.volume.sceneVolume;
    this.canvas3D = this.volume.canvas3D;

    var sphere = new THREE.SphereGeometry(0.05, 16, 16);
    this.lightObject = new THREE.Mesh(sphere,
                                      new THREE.MeshBasicMaterial({
                                          color : 0xFFFF33,
                                          wireframe : false,
                                      }));

    this.plane = new THREE.Mesh(new THREE.PlaneBufferGeometry(2000, 2000, 8, 8),
                                new THREE.MeshBasicMaterial({
                                    color : 0x000000,
                                    opacity : 0.25,
                                    transparent : true,
                                    wireframe : true
                                }));
    this.plane.visible = false;
    this.lightObject.visible = false;

    this.volume.scene.add(this.plane);
    this.lightObject.position.x = 0.0;
    this.lightObject.position.y = 0.0;
    this.lightObject.position.z = 1.0;
    //this.lightClone = this.lightObject.clone();
    this.volume.scene.add(this.lightObject);
    //this.volume.scene.add(this.lightClone);
    this.lightClone = this.volume.volumeObject.addMeshObject(this.lightObject, true);

    var onMouseUp = function () {
        if (!me.lightObject.visible)
            return;

        this.selectLight = false;
    };

    var onMouseDown = function (event) {
        if (!me.lightObject.visible)
            return;

        var width = this.canvas3D.getWidth();
        var height = this.canvas3D.getHeight();
        var cx = this.canvas3D.getX();
        var cy = this.canvas3D.getY();
        var x = ((event.clientX - cx) / width) * 2 - 1;
        var y =  - ((event.clientY - cy) / height) * 2 + 1;

        var vector = new THREE.Vector3(x, y, 0.5);
        var camera = this.canvas3D.camera;
        //this.canvas3D.projector.unprojectVector(vector, camera);
        vector.unproject(camera);
        var raycaster
            = new THREE.Raycaster(camera.position,
                                  vector.sub(camera.position).normalize());
        var objects = [this.lightObject];
        var intersects = raycaster.intersectObjects(objects);
        if (intersects.length > 0) {
            this.canvas3D.controls.enabled = false;
            this.selectLight = true;
            this.canvas3D.getEl().dom.style.cursor = 'move';
        } else {
            this.canvas3D.getEl().dom.style.cursor = 'auto';
        }
    };

    var onMouseMove = function (event) {
        event.preventDefault();

        if (!me.lightObject.visible)
            return;

        var width = this.canvas3D.getWidth();
        var height = this.canvas3D.getHeight();
        var cx = this.canvas3D.getX();
        var cy = this.canvas3D.getY();
        var x = ((event.clientX - cx) / width) * 2 - 1;
        var y =  - ((event.clientY - cy) / height) * 2 + 1;

        var vector = new THREE.Vector3(x, y, 0.5);

        var camera = this.canvas3D.camera;
        //this.canvas3D.projector.unprojectVector(vector, camera);
        vector.unproject(camera);
        var raycaster
            = new THREE.Raycaster(camera.position,
                                  vector.sub(camera.position).normalize());

        var objects = [this.lightObject];
        var intersects = raycaster.intersectObjects(objects);

        if (this.selectLight) {
            var intersects = raycaster.intersectObject(this.plane);
            this.lightObject.position.copy(intersects[0].point.sub(this.offset));
            this.lightClone.position.copy(intersects[0].point.sub(this.offset));
            return;
        }
        if (intersects.length > 0) {
            this.canvas3D.getEl().dom.style.cursor = 'move';
            this.plane.position.copy(intersects[0].object.position);
            this.plane.lookAt(camera.position);
        } else {
            this.canvas3D.getEl().dom.style.cursor = 'auto';
        }
    };

    this.canvas3D.getEl().dom.addEventListener('mousemove', onMouseMove.bind(this), true);
    this.canvas3D.getEl().dom.addEventListener('mouseup', onMouseUp.bind(this), true);
    this.canvas3D.getEl().dom.addEventListener('mousedown', onMouseDown.bind(this), true);
    this.offset = new THREE.Vector3();


    var differenceHandler = function(item, checked){

        if(checked){
            me.volume.volumeObject.setUniform('gradientType', item.text);
        }
	};

    var gradMenu = Ext.create('Ext.menu.Menu', {
        itemId: 'gradMenu',
        style: {
            overflow: 'visible'     // For the Combo popup
        },
        items: [
            {
                text: 'finite_difference',
                checked: true,
                group: 'grad',
                tooltip : 'standard difference gradient calculation (slow)',
                checkHandler: differenceHandler
            }, {
                text: 'sobel',
                checked: false,
                group: 'grad',
                tooltip : 'smoothed difference gradient calculation (very slow)',
                checkHandler: differenceHandler
            }, {
                text: 'directional',
                checked: false,
                group: 'grad',
                tooltip : 'approximate calculation using directional gradient.  Highlights not supported. (fast)',
                checkHandler: differenceHandler
            },

        ]
    });

    this.gradButton = {
		xtype : 'button',
        text : 'gradient type',
		//checked : false,
		width : 100,
		cls : 'toolItem',
        menu : gradMenu,
	};

    var shadingToggle = function(item, checked){
        if(checked === false) return;
        me.volume.volumeObject.setUniform('deepType', item.text);
    };

    var typeMenu = Ext.create('Ext.menu.Menu', {
        itemId: 'shadingType',
        style: {
            overflow: 'visible'     // For the Combo popup
        },
        items: [
            {
                text: 'deep_shading',
                checked: true,
                group: 'theme',
                checkHandler: shadingToggle
            }, {
                text: 'soft_shading',
                checked: false,
                group: 'theme',
                checkHandler: shadingToggle
            }
        ]
    });


    var sampleField = Ext.create('Ext.form.field.Number', {
        name : 'numberfield2',
        fieldLabel : 'samples',
        value : 4,
        minValue : 0,
        maxValue : 16,
        width : 150,
        listeners : {
            change : function (field, newValue, oldValue) {
                this.volume.sceneVolume.setUniform('LIGHT_SAMPLES', newValue, true, true);
            },
            scope : me
        },
    }).hide();


      ////////////////////////////////////////////
     //Show the various lighting functions
    ////////////////////////////////////////////

    var showLight = Ext.create('Ext.form.field.Checkbox',{
        itemId: 'show-light',
        boxLabel: 'show light',
        handler: function(item, checked){
            me.lightObject.visible = checked;
            me.lightClone.visible = checked;
            me.volume.rerender();

        }
    });


    var showPhong = Ext.create('Ext.form.field.Checkbox',{
        itemId: 'show-phong',
        boxLabel: 'show phong',
        handler: function(item, checked){
            var menubutton = me.controls.queryById('grad-type');
            me.volume.volumeObject.setUniform('phong', checked);

            if (checked) {
                menubutton.show();
                me.sliders['ambient'].show();
                me.sliders['diffuse'].show();
                me.sliders['size'].show();
                me.sliders['intensity'].show();
            } else {
                menubutton.hide();
                me.sliders['ambient'].hide();
                me.sliders['diffuse'].hide();
                me.sliders['size'].hide();
                me.sliders['intensity'].hide();
            }
            me.volume.rerender();
        }
    });

    var showDeep = Ext.create('Ext.form.field.Checkbox',{
        itemId: 'show-deep',
        boxLabel: 'show deep',
        handler: function(item, checked){

            var l = me.volume.canvas3D.camera.position.length();

            if( !checked && l < 2.2){
                BQ.ui.error("setting the deep rendering tool while too close </br>" +
                            "to the objet being rendered can result in context loss.</br>" +
                            "zoom out and try again.");
                this.setValue(false);
                return;
            }
            me.volume.volumeObject.setUniform('deep', checked);

            var menubutton = me.controls.queryById('shade-type');
            if (checked) {
                menubutton.show();
                me.sliders['depth'].show();
                me.sliders['dispersion'].show();
                me.sliders['absorption'].show();
            } else {
                menubutton.hide();
                me.sliders['depth'].hide();
                me.sliders['dispersion'].hide();
                me.sliders['absorption'].hide();
            }
            me.volume.rerender();
        }
    });

    this.controls.add(
        showLight,
        showPhong,
        showDeep,
        {
            itemId: 'grad-type',
		    xtype : 'button',
            text : 'gradient type',
		    width : 100,
            menu : gradMenu,
        }, {
            itemId: 'shade-type',
            xtype: 'button',
            width : 100,
            text:'shading model',
            menu: typeMenu  // assign menu by instance
        });
    var firstLayout = false;
    this.controls.on('afterlayout', function () {
        if(!firstLayout){
            firstLayout = true;
            me.controls.queryById('grad-type').hide();
            me.controls.queryById('shade-type').hide();

            me.sliders['ambient'].hide();
            me.sliders['diffuse'].hide();
            me.sliders['size'].hide();
            me.sliders['intensity'].hide();
            me.sliders['depth'].hide();
            me.sliders['dispersion'].hide();
            me.sliders['absorption'].hide();
        }

    });
    //we need to save the state of the lighting tool
    this.state = {light: false, phong: false, deep: false }

};

lightTool.prototype.toggle = function(button){
    var light = this.controls.queryById('show-light');
    var phong = this.controls.queryById('show-phong');
    var deep = this.controls.queryById('show-deep');

    if (button.pressed) {
        light.setValue(this.state.light);
        phong.setValue(this.state.phong);
        deep.setValue(this.state.deep);

    } else {
        this.state.light = light.getValue();
        this.state.phong = phong.getValue();
        this.state.deep  = deep.getValue();

        light.setValue(false);
        phong.setValue(false);
        deep.setValue(false);
    }


    this.base.prototype.toggle.call(this,button);
    //this.volume.rerender();

    };

function phongTool(volume, cls) {
	//renderingTool.call(this, volume);
    this.label = 'phong rendering';
    this.cls = 'phongButton';
    this.name = 'phong_rendering';
	this.base = renderingTool;
    this.base(volume, this.cls);
};
