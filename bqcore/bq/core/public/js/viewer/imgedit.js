// Imageviewer plugin enabling gobject editing functions
/*
  Used input parameters:
    noedit         - read-only view for gobjects
	  alwaysedit     - instantiates editor right away and disables hiding it
	  nosave         - disables saving gobjects
	  editprimitives - only load edit for given primitives, 'editprimitives':'point,polyline'
*/

ImgViewer.gobFunction = {
    'point'     : 'new_point',
    'rectangle' : 'new_rectangle',
    'square'    : 'new_square',
    'line'      : 'new_line',
    'polyline'  : 'new_polyline',
    'polygon'   : 'new_polygon',
    'freehand_line'  : 'new_freehand_open',
    'freehand_shape'  : 'new_freehand_closed',
    'smart_shape'  : 'new_smart_shape',
    'circle'    : 'new_circle',
    'ellipse'   : 'new_ellipse',
    'label'     : 'new_label',
};

function ImgEdit (viewer,name){
  this.base = ViewerPlugin;
  this.base (viewer, name);
  this.mode = null;
  this.current_gob = null;

  this.zindex_high = 25;
  this.zindex_low  = 15;

  //parse input parameters
  /*
  var primitives = 'Point,Rectangle,Square,Polyline,Line,Polygon,freehand_line,freehand_shape,Circle,Ellipse,Label'.toLowerCase().split(',');
  if ('editprimitives' in this.viewer.parameters && this.viewer.parameters.editprimitives)
    primitives = this.viewer.parameters.editprimitives.toLowerCase().split(',');
  this.editprimitives = {};
  this.semantic_types = this.viewer.parameters.semantic_types;
  for (var i=0; i < primitives.length; i++)
    this.editprimitives[ primitives[i] ] = '';
*/
}
ImgEdit.prototype = new ViewerPlugin();

ImgEdit.prototype.newImage = function () {
    this.renderer = this.viewer.renderer;
    this.renderer.set_select_handler( callback(this, this.on_selected) );
    //this.renderer.set_hover_handler( callback(this, this.on_hover) );
    this.renderer.set_move_handler( callback(this, this.on_move) );
    this.gobjects = this.viewer.image.gobjects;
    this.visit_render = new BQProxyClassVisitor (this.renderer);

};

ImgEdit.prototype.updateImage = function () {
  var primitives = 'Point,Rectangle,Square,Polyline,Line,Polygon,freehand_line,freehand_shape,Circle,Ellipse,Label'.toLowerCase().split(',');
  if ('editprimitives' in this.viewer.parameters && this.viewer.parameters.editprimitives)
    primitives = this.viewer.parameters.editprimitives.toLowerCase().split(',');
  this.editprimitives = {};
  this.semantic_types = this.viewer.parameters.semantic_types;
  for (var i=0; i < primitives.length; i++)
    this.editprimitives[ primitives[i] ] = '';
};

ImgEdit.prototype.createButtonsDeselect = function() {
    var c=undefined;
    for (var i=0; (c=this.button_controls[i]); i++)
        c.setSelected(false);
},

ImgEdit.prototype.createButton = function(surf, basecls, cls, cb, sel, ctrls, tooltip) {
    var btn = document.createElement('span');

    // temp fix to work similar to panojs3, will be updated to media queries
    var clsa = [basecls];
    if (isClientTouch())
        clsa.push('touch');
    else if (isClientPhone())
        clsa.push('phone');
    clsa.push(cls);
    cls = clsa.join(' ');

    btn.className = cls;
    surf.appendChild(btn);

    btn.selected = false;
    btn.base_cls = cls;
    btn.operation = cb;
    btn.setSelected = function(selected) {
        this.selected = selected;
        if (this.selected)
            this.className = this.base_cls + ' selected';
        else
            this.className = this.base_cls;
    };
    btn.setSelected(sel);

    if (!cb)
        return btn;

    var el = Ext.get(btn);
    //prevent editing while the database is being pinged
    el.disabled = false;
    el.on('mousedown', function(e, btn) {
        if(el.disabled) return;
        e.preventDefault();
        e.stopPropagation();
        var c=undefined;
        for (var i=0; (c=ctrls[i]); i++)
            c.setSelected(false);
        btn.setSelected(true);
        btn.operation();
    });

    el.on('touchstart', function(e, btn) {
        if(el.disabled) return;
        e.preventDefault();
        e.stopPropagation();
        var c=undefined;
        for (var i=0; (c=ctrls[i]); i++)
            c.setSelected(false);
        btn.setSelected(true);
        btn.operation();
    });


    if (tooltip)
    var tip = Ext.create('Ext.tip.ToolTip', {
        target: el,
        html: tooltip,
    });

    return btn;
};

ImgEdit.prototype.setButtonLoading = function(disabled){
    //set buttons to be transparent during loading and disable their callback
    this.button_controls.forEach(function(btn) {
        if (btn.setDisabled) {
            btn.setDisabled(disabled);
        } else {
            var el = Ext.get(btn);
            el.disabled = disabled;
            if(disabled)
                el.dom.style.opacity = 0.25;
            else
                el.dom.style.opacity = 1.0;
        }
    });
}

ImgEdit.prototype.createEditMenu = function(surf) {
    if (this.editbutton) return;
    this.editbutton = Ext.create('BQ.editor.GraphicalMenu', {
        renderTo: surf,
        widget: this.viewer.widget,
        editprimitives: this.editprimitives,
        semantic_types: this.semantic_types,
        listeners: {
            scope: this,
            selected: this.onSelectedType,
        }
    });
};

ImgEdit.prototype.onSelectedType = function(primitive, semantic, selector) {
    this.onCreateGob(primitive);
    if (semantic)
        this.onCreateGob(semantic);
};

ImgEdit.prototype.createEditControls = function(surf) {
    if (!this.button_controls) {
        this.button_controls = [];
        this.button_controls[0] = this.createButton(surf, 'editcontrol', 'btn-navigate',
            callback(this, this.navigate), true, this.button_controls, 'Pan and zoom the image');
        this.button_controls[1] = this.createButton(surf, 'editcontrol', 'btn-select',
            callback(this, this.select), false, this.button_controls, 'Select a graphical annotation on the screen' );
        this.button_controls[2] = this.createButton(surf, 'editcontrol', 'btn-delete',
            callback(this, this.remove), false, this.button_controls, 'Delete a graphical annotation by selecting it on the screen' );
        this.button_controls.push(this.editbutton);
    }
};

ImgEdit.prototype.updateView = function (view) {
    var v = this.viewer;
    var surf = v.viewer_controls_surface ? v.viewer_controls_surface : this.parent;
    if (surf) {
        //if (!v.parameters.hide_create_gobs_menu)
            this.createEditMenu(surf);
        this.createEditControls(surf);
    }
};

ImgEdit.prototype.onCreateGob = function (type) {
    this.renderer.setMode('add');
    if (type in ImgViewer.gobFunction) {
        this.mode_primitive = null;
        var f = ImgViewer.gobFunction[type];
        this.setmode(type, callback(this, f, null));
    } else { // creating a complex gob
        // With a little more work here, we could have nested
        // complex objects.. It's hard to decide when the user
        // is nesting vs choosing a new top-level complex object.
        // for now we allow only simply objects to be nested.
        var internal_gob = callback(this, 'new_point');
        if (this.mode_type in ImgViewer.gobFunction) {
            var f = ImgViewer.gobFunction[this.mode_type];
            internal_gob = callback(this, f);
        }
        this.setmode('complex', callback(this, 'newComplex', type, internal_gob, null));
    }
};

ImgEdit.prototype.cancelEdit = function () {
    this.endEdit();
    this.viewer.need_update();
};

ImgEdit.prototype.startEdit = function () {
    if (this.editing_gobjects) return;
    var surf = this.viewer.viewer_controls_surface;
    this.editing_gobjects = true;
    this.renderer.stage.content.style.zIndex = this.zindex_high;
    surf.style.zIndex = this.zindex_low;

    //this.renderer.setmousedown(null);
    this.renderer.setmousedown(callback(this, this.mousedown));
    this.surface_original_onmousedown = surf.onmousedown;
    surf.onmousedown = callback(this, this.mousedown);

    this.renderer.setmousemove(callback(this, this.mousemove));
    surf.onmousemove = callback(this, this.mousemove);
    /*
    this.renderer.setmouseup(callback(this, function(e){
        this.renderer.setMode('edit');
        this.renderer.selectLayer.moveToBottom();
    }));
    */

    //this.renderer.setdblclick(callback(this, this.mousedblclick));
    //surf.ondblclick = callback(this, this.mousedblclick);

    //this.renderer.setclick(callback(this, this.mousedown));
    //this.surface_original_onclick = surf.onclick;
    //surf.onclick = callback(this, this.mousedown);


    this.renderer.setkeyhandler(callback(this, this.keyhandler));
    //surf.contentEditable=true;
    //surf.focus();
    //surf.addEventListener('keydown', callback(this, this.keyhandler), false);
    this.renderer.enable_edit (true);
};

ImgEdit.prototype.endEdit = function () {
    var surf = this.viewer.viewer_controls_surface;
    this.renderer.stage.content.style.zIndex = this.zindex_low;
    surf.style.zIndex = this.zindex_high;

    if (this.surface_original_onmousedown)
        surf.onmousedown = this.surface_original_onmousedown;
    this.renderer.setmousedown(null);
    this.renderer.setmousemove(null);

    //this.renderer.setdblclick(null);
    //surf.ondblclick = null;

    //if (this.surface_original_onclick)
    //    surf.onclick = this.surface_original_onclick;
    //this.renderer.setclick(null);


    //this.renderer.setmousemove(null);
    this.renderer.setkeyhandler(null);
    this.renderer.enable_edit (false);

    this.mode = null;
    this.current_gob = null;

    if (this.tageditor) {
        this.tageditor.destroy();
        delete this.tageditor;
    }
    this.editing_gobjects = false;
};

ImgEdit.prototype.dochange = function () {
    if (this.viewer.parameters.gobjectschanged)
        this.viewer.parameters.gobjectschanged(this.gobjects);
};

ImgEdit.prototype.mousedown = function (e) {
    if(!e.evt) return;
    e.evt.cancelBubble = true;
    if (!e) e = window.event;  // IE event model
    if (e == null) return;
    /*
    if (!(e.target===this.renderer.currentLayer.getCanvas()._canvas ||
          e.target===this.renderer.svggobs ||
          (this.current_gob && e.target===this.current_gob.shape.svgNode))) return;
    */
    if (this.mode) {
        var svgPoint = this.renderer.getUserCoord(e);
        this.mode (e, svgPoint.x, svgPoint.y);
        // this will disable all propagation while in edit selected
        if (e.stopPropagation) e.stopPropagation(); // DOM Level 2
        else e.cancelBubble = true;                 // IE
    } else if (this.viewer.parameters.onposition) {
        //this.renderer.setMode('select');
        var view = this.viewer.current_view,
            phys = this.viewer.imagephys,
            p = this.renderer.getUserCoord(e),
            pt = view.inverseTransformPoint(p.x, p.y),
            pt = phys.coordinate_to_phys(pt, true);
        this.viewer.parameters.onposition(pt);
    }
};

ImgEdit.prototype.hover = function (e) {

},

ImgEdit.prototype.mousemove = function (e) {
    //console.log(this, e);
    if (!e) e = window.event;  // IE event model
    if (e == null) return;
    var me = this;
    var evt = e.evt ? e.evt : e;
    //if (!(e.target===this.renderer.svgdoc ||
     //     e.target===this.renderer.svggobs ||
     //     (this.current_gob && e.target===this.current_gob.shape.svgNode))) return;

    var view = this.viewer.current_view,
    p = this.renderer.getUserCoord(e),
    pt = view.inverseTransformPoint(p.x, p.y);
    this.viewer.print_coordinate(pt, true, true);
    //this.renderer.focus();

    if(!this.trackpt)
        this.trackpt = pt;
/*
    var tpt = this.trackpt;
    var dpt = {x: pt.x - tpt.x, y: pt.y - tpt.y};
    var dl = dpt.x*dpt.x + dpt.y*dpt.y;

    this.trackpt = pt;
    if(this.hoverTimeout) clearTimeout(this.hoverTimeout);
    if(dl < 2){
        this.hoverTimeout = setTimeout(function(){
            var shape = me.renderer.findNearestShape(tpt.x, tpt.y);
            if(shape){
                evt.type = 'hover';
                me.viewer.parameters.onhover(shape.gob, evt);
                console.log(shape);
            }

            //me.onhover(e);
        },750);
    }
*/
};

ImgEdit.prototype.mousedblclick = function (e) {
    if (!e) e = window.event;  // IE event model
    if (!e || !this.current_gob) return;
    if (e.type !== 'dblclick') return;
    //if (!(e.target===this.renderer.svgdoc || e.target===this.renderer.svggobs)) return;

    if (this.mode) {
        // this will disable all propagation while in edit selected
        if (e.stopPropagation) e.stopPropagation(); // DOM Level 2
        else e.cancelBubble = true;                 // IE

        var p = this.renderer.getUserCoord(e);
        this.mode (e, p.x, p.y);
    }
};

ImgEdit.prototype.keyhandler = function (e) {
    e = e ? e : window.event;  // IE event model
    if (e.target !== BQApp.main.getEl().dom) return;
    var key = e.keyCode ? e.keyCode : e.which,
        nav_keys = {
            33: 33, 34: 34, 37: 37, 38: 38, 39: 39, 40: 40, 107: 107, 109: 109, 187: 187, 189: 189,
        };

    if (key in nav_keys) {
      this.viewer.tiles.tiled_viewer.keyboardHandler(e);
      return;
    }

    if (this.mode && this.current_gob) {
        // this will disable all propagation while in edit selected
        if (e.stopPropagation) e.stopPropagation(); // DOM Level 2
        else e.cancelBubble = true;                 // IE

        if (e.type === 'keydown' && e.keyCode === 46) { // delete
            this.remove_gobject(this.current_gob);
            return;
        }

        //var p = this.renderer.getUserCoord(e);
        this.mode (e, NaN, NaN);
    }
};

ImgEdit.prototype.display_gob_info = function (gob) {
    if (!gob) return;
    var view = this.viewer.current_view;
    var phys = this.viewer.imagephys;

    var text = '';

    var perimeter_px = gob.perimeter();

    if (perimeter_px>0)
        text += ' Length: '+perimeter_px.toFixed(2)+'px';
    if (perimeter_px>0 && phys.pixel_size[0]>0 && phys.pixel_size[1]>0) {
        text += ' '+gob.perimeter({x: phys.pixel_size[0], y: phys.pixel_size[1]}).toFixed(2)+phys.units;
    }

    var area_px = gob.area();
    if (area_px>0)
        text += ' Area: '+area_px.toFixed(2)+'px²';
    if (area_px>0 && phys.pixel_size[0]>0 && phys.pixel_size[1]>0) {
        text += ' '+gob.area({x: phys.pixel_size[0], y: phys.pixel_size[1]}).toFixed(2)+phys.units+'²';
    }

    var ip = this.viewer.plugins_by_name['infobar'];
    ip.posbar.innerText = text;

};


ImgEdit.prototype.display_gob_info_group = function (gobs) {

    var view = this.viewer.current_view;
    var phys = this.viewer.imagephys;

    var text = 'group: ';

    var perimeter_px = 0;
    var area_px = 0;

    var perimeter_px_sz = 0;
    var area_px_sz = 0;

    gobs.forEach(function(e){
        perimeter_px += e.gob.perimeter();
        area_px += e.gob.area();
        if (perimeter_px>0 && phys.pixel_size[0]>0 && phys.pixel_size[1]>0) {
            perimeter_px_sz += e.gob.perimeter({x: phys.pixel_size[0], y: phys.pixel_size[1]});
        }
        if (area_px>0 && phys.pixel_size[0]>0 && phys.pixel_size[1]>0) {
            area_px_sz += e.gob.area({x: phys.pixel_size[0], y: phys.pixel_size[1]});
        }
    });

    if (perimeter_px>0)
        text += ' Length: '+perimeter_px.toFixed(2)+'px';
    if (perimeter_px>0 && phys.pixel_size[0]>0 && phys.pixel_size[1]>0) {
        text += ' ' + perimeter_px_sz.toFixed(2) + phys.units;
    }

    if (area_px>0)
        text += ' Area: '+area_px.toFixed(2)+'px²';
    if (area_px>0 && phys.pixel_size[0]>0 && phys.pixel_size[1]>0) {
        text += ' ' + area_px_sz.toFixed(2) + phys.units + '²';
    }

    var ip = this.viewer.plugins_by_name['infobar'];
    ip.posbar.innerText = text;

};

ImgEdit.prototype.test_save_permission = function (uri) {
    var pars = this.viewer.parameters || {};
    if ('nosave' in pars)
        return false;

    // dima: a hack to stop writing into a MEX
    if (uri && uri.indexOf('/mex/')>=0) {
        BQ.ui.warning('Can\'t save annotations into a Module EXecution document...');
        return false;
    }

    // dima - REQUIRES CHANGES TO SUPPORT PROPER ACLs!!!!
    /* if (this.viewer.user)
    if (!(this.viewer.user_uri && (this.viewer.image.owner == this.viewer.user_uri))) {
        BQ.ui.notification('You do not the permission to save graphical annotations to this document...');
        // dima: write permissions need to be properly red here
        //return false;
    }*/

    if(!BQApp.user){
        if(!this.issuedUserWarning)
            BQ.ui.warning('You not currently logged in.  Any changes made during this session will not be saved.');
        this.issuedUserWarning = true;
        return false;
    }
    //Hack which stores flag after permissions have been tested
    if(this.insufficientPrivelage){
        return false;
    }

    return true;
};

ImgEdit.prototype.on_error = function(gob, e){
    if (e.request.status === 403 &&
       !this.issuedPrivelageWarning){

        if(e.message.length > 256)
            BQ.ui.warning('You have insufficient privelages to edit this document. Any changes made during this session will not be saved.');
        else
            BQ.ui.warning(e.message + ' Any changes made during this session will not be saved.');
        this.insufficientPrivelage = true;
        this.issuedPrivelageWarning = true;
    } else if (e.request.status < 300) {
       this.remove_gobject(gob);
    } else {
        this.viewer.parameters.onerror(e);
    }

    //this is here because its required to release the ui from working state
    this.viewer.parameters.ondone();
};

ImgEdit.prototype.store_new_gobject = function (gob) {
    this.display_gob_info(gob);
    //if (this.viewer.parameters.gobjectCreated)
    //    this.viewer.parameters.gobjectCreated(gob);

    // save to DB
    if (!this.test_save_permission(this.viewer.image.uri + '/gobject')) {
        if (this.viewer.parameters.gobjectschanged)
            this.viewer.parameters.gobjectschanged(gob);
        return;
    }

    var pars = this.viewer.parameters || {};
    if (pars.onworking)
        pars.onworking('Saving annotations...');

    // create a temporary backup object holding children in order to properly hide shapes later to prevent blinking
    var bck = new BQGObject ('Temp');
    bck.gobjects = gob.gobjects;

    var uri = this.viewer.image.uri + '/gobject';
    if (gob.parent && (gob.parent instanceof BQGObject) && gob.parent.uri)
        uri = gob.parent.uri;

    var me = this;
    gob.save_reload(
        uri,
        function(resource) {
            // show the newly returned object from the DB, here gob and resource point to the same things
            me.visit_render.visitall(gob, [me.viewer.current_view]);
            // remove all shapes from old children because save_reload replaces gobjects vector
            me.visit_render.visitall(bck, [me.viewer.current_view, false]);

            if (me.viewer.parameters.gobjectCreated)
                me.viewer.parameters.gobjectCreated(gob);

            pars.ondone();
        },
        callback(this, 'on_error', gob)
    );

};

ImgEdit.prototype.get_gobs_w_shapes = function (gob, shapes) {
    shapes = shapes || [];
    if (gob.shape) shapes.push(gob);
    var g = null,
        i = 0;
    for (i=0; (g=gob.gobjects[i]); ++i) {
        this.get_gobs_w_shapes(g, shapes);
    }

    return shapes;
},

ImgEdit.prototype.remove_gobject = function (gob) {
    // dima: a hack to stop writing into a MEX

    if (!gob) {
        // dima: there's some bug here
        //BQ.ui.warning('Some problem removing annotation...');
        return;
    }

    this.current_gob = null;
    this.renderer.setmousemove(null);
    this.renderer.unselectCurrent();
    //this.renderer.quadtree.remove(gob.shape);
    var gobs = this.get_gobs_w_shapes(gob),
        i = 0,
        g = null;
    for (i=0; (g=gobs[i]); ++i) {
        this.renderer.quadtree.remove(g.shape);
    }

    if (gob.uri && gob.uri.indexOf('/mex/')>=0) {
        BQ.ui.warning('Can\'t delete annotation from a Module EXecution document...');
        return;
    }

    // remove rendered shape first
    this.renderer.hideShape(gobs, this.viewer.current_view);
    this.visit_render.visitall(gob, [this.viewer.current_view, false]); // make sure to hide all the children if any
    this.renderer.rerender();


    //test privelages and abort if we don't, we still want to reflect changes in renderer, though

    //if (!this.test_save_permission(this.viewer.image.uri + '/gobject')) {
    //    if (this.viewer.parameters.gobjectschanged)
     //       this.viewer.parameters.gobjectschanged(gob);
     //   return;
    //}

    var pars = this.viewer.parameters || {};
    if (this.test_save_permission(gob.uri))
        if (pars.onworking)
            pars.onworking('Saving annotations...');

    // try to find parent gobject and if it have single child, remove parent
    //var p = gob.findParentGobject();
    var p = gob.parent;
    if (p && p instanceof BQGObject && p.gobjects.length === 1)
        gob = p;

    // remove gob
    var v = (gob.parent ? gob.parent.gobjects : undefined) || this.gobjects;
    var index = v.indexOf(gob);
    v.splice(index, 1);
    if (this.viewer.parameters.gobjectDeleted)
        this.viewer.parameters.gobjectDeleted(gob);

    // save to DB
    if (!this.test_save_permission(gob.uri))
        return;

    var pars = this.viewer.parameters || {};
    if(gob.uri)
        gob.delete_(pars.ondone, callback(this, 'on_error', null));
};

ImgEdit.prototype.on_selected = function (gobs) {
    if(gobs.length === 0) return;
    var me = this;
    if (this.mode_type === 'delete') {
        this.remove_gobject(gob);
    } else if (this.mode_type === 'select') {
        if (this.viewer.parameters.onselect)
            this.viewer.parameters.onselect(gobs);
        if(gobs.length > 1)
            me.display_gob_info_group(gobs);
        else{
            me.display_gob_info(gobs[0].gob);
        }
    }
};


ImgEdit.prototype.color_gobject = function(gob, color) {
    //gob.color_override = color; //this.renderer.setcolor(gob, color);

    var skip_save = false;
    if (!this.test_save_permission(this.viewer.image.uri + '/gobject')) {
        if (this.viewer.parameters.gobjectschanged)
            this.viewer.parameters.gobjectschanged(gob);
        //return;
        skip_save = true;
    }

    gob.setColor(color, skip_save);

    this.renderer.rerender([gob], [this.current_view, true]);
    //console.log(gob.uri + '?view=deep');
};


ImgEdit.prototype.on_move = function (gob) {
    if(!gob.shape.postEnabled) return;


    if (!this.test_save_permission(this.viewer.image.uri + '/gobject')) {
        if (this.viewer.parameters.gobjectschanged)
            this.viewer.parameters.gobjectschanged(gob);
        return;
    }

    this.display_gob_info(gob);
    var me = this;
    var pars = this.viewer.parameters || {};
    if(!this.gobQueue) this.gobQueue = {};
    if(gob.uri)//only save if object has been awarded a uri from the database
        this.gobQueue[gob.uri] = gob; //store a unique

    if(this.saveTimeout) clearTimeout(this.saveTimeout);
    var timeout = function() {
        //console.log('post');
        var keys = Object.keys(me.gobQueue);
        keys.forEach(function(k){
            var gob = me.gobQueue[k];
            gob.save_me(pars.ondone,
                        callback(this, 'on_error', null)); // check why save_ should not be used

        });

        me.gobQueue = {};
    }

    this.saveTimeout = setTimeout( timeout, 500 );
    /*
    if (this.saving_timeout) clearTimeout (this.saving_timeout);
    this.saving_timeout = setTimeout( function() {
        me.saving_timeout=undefined;
        if (!me.test_save_permission(gob.uri))
            return;
        gob.save_me(pars.ondone, pars.onerror ); // check why save_ should not be used
    }, 10 );*/
};

ImgEdit.prototype.setmode = function (type, mode_fun) {
    if (mode_fun) this.startEdit();
    this.mode = mode_fun;
    if(type)
        this.renderer.setMode('add');

    this.mode_type = type;
    if (type) {
        this.createButtonsDeselect();
        this.editbutton.setSelected(true);
    }
    this.viewer.parameters.onmodechange(type);
};

ImgEdit.prototype.select = function (e, x, y) {
    this.setmode (null);
    this.mode_type = 'select';
    this.renderer.setMode('edit');

    this.current_gob = null;
    this.startEdit();
    if (this.viewer.parameters.oneditcontrols)
        this.viewer.parameters.oneditcontrols();
};

ImgEdit.prototype.remove = function (e, x, y) {
    this.setmode (null);
    this.mode_type = 'delete';
    this.renderer.setMode('delete');
    this.renderer.delete_fun = callback(this, 'remove_gobject');

    this.current_gob = null;
    this.startEdit();
    if (this.viewer.parameters.oneditcontrols)
        this.viewer.parameters.oneditcontrols();
};

ImgEdit.prototype.navigate = function (e, x, y) {

    this.setmode (null);
    this.mode_type = 'navigate';
    this.renderer.setMode('navigate');

//this.setmode ('navigate');
    this.endEdit();
    if (this.viewer.parameters.oneditcontrols)
        this.viewer.parameters.oneditcontrols();
};

ImgEdit.prototype.on_edit = function (parent, e, x, y) {
    var view = this.viewer.current_view,
    phys = this.viewer.imagephys,
    p = this.renderer.getUserCoord(e),
    pt = view.inverseTransformPoint(p.x, p.y),
    pt = phys.coordinate_to_phys(pt, true);
    this.viewer.parameters.onposition(pt);
},

ImgEdit.prototype.new_point = function (parent, e, x, y) {
    e.evt.cancelBubble = true;

    var v = this.viewer.current_view;
    var g = new BQGObject('point');
    parent = parent || this.global_parent;

    if (parent)
        parent.addgobjects(g);
    else
        this.viewer.image.addgobjects(g);

    var pt = v.inverseTransformPoint(x,y);
    g.vertices.push (new BQVertex (pt.x, pt.y, v.z, v.t, null, 0));

    this.current_gob = null;
        this.renderer.unselectCurrent();
    this.visit_render.visitall(g, [v]);

    this.renderer.selectedSet = [g.shape];
    this.renderer.select(this.renderer.selectedSet);
    this.store_new_gobject ((parent && !parent.uri) ? parent : g);
    this.renderer.unselectCurrent();
};

ImgEdit.prototype.begin_add = function(g, parent){
    this.renderer.unselectCurrent();
    this.renderer.selectedSet = [g.shape];
    this.renderer.select(this.renderer.selectedSet);
}


ImgEdit.prototype.finish_add = function(g, parent){
    g.shape.postEnabled = true;
    if(this.current_gob)
        this.on_move(this.current_gob);
    this.current_gob = null;
    this.renderer.setmousemove(null);
    this.renderer.setmouseup(null);
    //this.renderer.toggleWidgets('show');
    this.store_new_gobject ((parent && !parent.uri) ? parent : g);
    this.renderer.unselectCurrent();
}

ImgEdit.prototype.basic_drag_callback = function(g, parent, x, y){
    var me = this;
    var v =  this.viewer.current_view;
    this.current_gob = g;
    this.visit_render.visitall(g, [v]);

    this.renderer.setmousemove(function(e){
        g.shape.onDragCreate(e, [x,y]);
        me.display_gob_info(g);
    });

    this.renderer.setmouseup(callback(this, function(e){
        this.finish_add(g, parent);
        //if (this.viewer.parameters.onselect)
        //    this.viewer.parameters.onselect([g]);
    }));

    if(g.shape){
        this.begin_add(g, parent);
    }

}

ImgEdit.prototype.basic_shape  = function (shape, parent, e, x, y) {
    if (e.type === 'keydown') return;
    e.evt.cancelBubble = true;

    var me = this;
    var v =  this.viewer.current_view;
    var g =  new BQGObject(shape);
    parent = parent || this.global_parent;

    if (parent)
        parent.addgobjects(g);
    else
        this.viewer.image.addgobjects(g);

    var pt = v.inverseTransformPoint(x,y);
    var pt2 = v.inverseTransformPoint(x+1,y+1);
    g.vertices.push (new BQVertex (pt.x, pt.y, v.z, v.t, null, 0));
    g.vertices.push (new BQVertex (pt2.x, pt2.y, v.z, v.t, null, 1));
    this.basic_drag_callback(g,parent,x,y);
};

ImgEdit.prototype.new_rectangle = function (parent, e, x, y) {
    this.basic_shape('rectangle', parent, e, x, y);
};

ImgEdit.prototype.new_square = function (parent, e, x, y) {
    this.basic_shape('square', parent, e, x, y);
};

ImgEdit.prototype.new_circle = function (parent, e, x, y) {
    this.basic_shape('circle', parent, e, x, y);
};

//ImgEdit.prototype.new_ellipse = function (parent, e, x, y) {
//    this.basic_shape('ellipse', parent, e, x, y);
//};

ImgEdit.prototype.new_ellipse = function (parent, e, x, y) {
    if (e.type === 'keydown') return;
    e.evt.cancelBubble = true;

    var me = this;
    var v = this.viewer.current_view;
    var g = new BQGObject('ellipse');

    parent = parent || this.global_parent;

    if (parent)
        parent.addgobjects(g);
    else
        this.viewer.image.addgobjects(g);

    var pt = v.inverseTransformPoint(x,y);
    var ptX = v.inverseTransformPoint(x,y);
    var ptY = v.inverseTransformPoint(x,y);
    g.vertices.push (new BQVertex (pt.x, pt.y, v.z, v.t, null, 0));
    g.vertices.push (new BQVertex (ptX.x + 1, ptX.y, v.z, v.t, null, 1));
    g.vertices.push (new BQVertex (ptY.x, ptY.y + 1, v.z, v.t, null, 2));
    this.basic_drag_callback(g,parent,x,y);

};

ImgEdit.prototype.basic_polygon = function (type, parent, e, x, y) {

    var v = this.viewer.current_view,
        g = this.current_gob,
        me = this;
    parent = parent || this.global_parent;

    if (g == null) {
        g = new BQGObject(type);
        if (parent) {
            parent.addgobjects(g);
            g.edit_parent = parent;
        } else
            this.viewer.image.addgobjects(g);
        this.current_gob = g;
        this.renderer.setmousemove(function(e){
            g.shape.onDragCreate(e,[x,y]);
            me.display_gob_info(g);
        });
    }

    var pt = v.inverseTransformPoint(x,y);
    var index = g.vertices.length;
    var prev = index>0?g.vertices[index-1]:{x:-1,y:-1};


    //if we want to close this sucker without adding more points
    /*if(index > 2){
        //var ip = v.inverseTransformPoint(g.vertices[0].x,g.vertices[0].y);
        var dx = g.vertices[0].x - pt.x;
        var dy = g.vertices[0].y - pt.y;
        var dp = dx*dx + dy*dy;

        if(dp < 128/this.renderer.scale()){
            this.finish_add(g, g.edit_parent);
            this.renderer.resetShapeCornerFill();


            return;
        };
    }
    */

    var detail = e.evt ? e.evt.detail : e.detail;

    if (e.type === 'keydown' && e.keyCode === 27 && g.shape && g.shape.getLastPoint) { // escape
        pt = g.shape.getLastPoint();
        detail = 1;
    }

    if (e.type === 'keydown' && e.keyCode === 8 && g.shape && g.shape.removeLastPoint) { // backspace
        g.shape.removeLastPoint();
        g.shape.redraw();
        return;
    }

    if (detail==1 && pt.x && pt.y && !isNaN(pt.x) && !isNaN(pt.y) && pt.x!==prev.x && pt.y!==prev.y) {
        g.vertices.push (new BQVertex (pt.x, pt.y, v.z, v.t, null, index));
    }

    // Double click or Escape ends the object otherwise add points
    if (detail > 1 ||
        e.type === 'dblclick' ||
        e.type === 'keydown' && e.keyCode === 27
    ) {
        this.finish_add(g, g.edit_parent);
        return;
    }

    if (g.shape)
        g.shape.sprite.remove();
    this.visit_render.visitall(g, [v]);
    g.shape.postEnabled = false;
    this.begin_add(g, g.edit_parent);
};


ImgEdit.prototype.new_polygon = function (parent, e, x, y) {
    this.basic_polygon('polygon', parent, e, x, y);
};

ImgEdit.prototype.new_polyline = function (parent, e, x, y) {
    this.basic_polygon('polyline', parent, e, x, y);
};


ImgEdit.prototype.new_freehand = function (type, parent, e, x, y) {
    if (e.type === 'keydown') return;
    var me = this;
    var v = this.viewer.current_view;
    var g = this.current_gob;
    parent = parent || this.global_parent;

    if (g == null) {
        g = new BQGObject(type);
        if (parent) {
            parent.addgobjects(g);
            g.edit_parent = parent;
        } else
            this.viewer.image.addgobjects(g);
    }

    var pt = v.inverseTransformPoint(x,y);
    var index = g.vertices.length;
    var prev = index>0?g.vertices[index-1]:{x:-1,y:-1};


    //if we want to close this sucker without adding more points
    //var ip = v.inverseTransformPoint(g.vertices[0].x,g.vertices[0].y);

    var detail = e.evt ? e.evt.detail : e.detail;
    if (detail==1 && pt.x && pt.y && !isNaN(pt.x) && !isNaN(pt.y) && pt.x!==prev.x && pt.y!==prev.y)
        g.vertices.push (new BQVertex (pt.x, pt.y, v.z, v.t, null, index));

    // Double click ends the object otherwise add points
    this.current_gob = (e.evt.detail > 1)?null:g;

    this.visit_render.visitall(g, [v]);
    g.shape.postEnabled = false;
    this.renderer.unselectCurrent();
    this.renderer.selectedSet = [g.shape];
    this.renderer.select(this.renderer.selectedSet);
    //var n = g.vertices.length;
    //var dx = g.vertices[n-1].x - pt.x;
    //var dy = g.vertices[n-1].y - pt.y;
    //var dp = dx*dx + dy*dy;
    this.renderer.setmousemove(function(e){
        g.shape.onDragFree(e, [x,y]);
        me.display_gob_info(g);
    });

    this.renderer.setmouseup(callback(this,function(e){
        g.shape.postEnabled = true;
        me.on_move(me.current_gob);
        me.current_gob = null;
        me.renderer.setmousemove(null);
        me.renderer.setmouseup(null);
        g.shape.visvalingamSimplify();
        g.shape.moveLocal();

        me.store_new_gobject ((g.edit_parent && !g.edit_parent.uri) ? g.edit_parent : g);
        this.renderer.drawEditLayer();
        //this.renderer.updateVisible();
    }));
};

ImgEdit.prototype.new_freehand_closed = function (parent, e, x, y) {
    this.new_freehand('polygon', parent, e, x, y);
};

ImgEdit.prototype.new_freehand_open = function (parent, e, x, y) {
    this.new_freehand('polyline', parent, e, x, y);
};

ImgEdit.prototype.new_line = function (parent, e, x, y) {
    if (e.type === 'keydown') return;
    var v = this.viewer.current_view,
        g = this.current_gob,
        me = this;
    parent = parent || this.global_parent;
    var finish=false;
    if (g == null) {
        g = new BQGObject('line');
        if (parent) {
            parent.addgobjects(g);
            g.edit_parent = parent;
        } else
            this.viewer.image.addgobjects(g);
    } else
       finish = true;

    var pt = v.inverseTransformPoint(x,y);
    var index = g.vertices.length;
    g.vertices.push (new BQVertex (pt.x, pt.y, v.z, v.t, null, index));

    this.current_gob = finish?null:g;
    if (!this.current_gob) {
        this.store_new_gobject ((g.edit_parent && !g.edit_parent.uri) ? g.edit_parent : g);
        g.shape.postEnabled = true;
        this.renderer.setmousemove(null);
        this.renderer.unselectCurrent();
    } else {
        if(g.shape)
            g.shape.sprite.remove();
        this.visit_render.visitall(g, [v]);
        g.shape.postEnabled = false;
        this.renderer.unselectCurrent();
        this.renderer.selectedSet = [g.shape];
        this.renderer.select(this.renderer.selectedSet);
        this.renderer.setmousemove( function(e){
            g.shape.onDragCreate(e,[x,y]);
            me.display_gob_info(g);
        });

    }
    this.visit_render.visitall(g, [v]);

};

ImgEdit.prototype.new_label = function (parent, e, x, y) {
    if (e.type === 'keydown') return;
    var v = this.viewer.current_view;
    var g = new BQGObject('label');
    parent = parent || this.global_parent;

    var pt = v.inverseTransformPoint(x,y);
    g.vertices.push (new BQVertex (pt.x, pt.y, v.z, v.t, null, 0)); //label location
    g.vertices.push (new BQVertex (pt.x+10, pt.y+10, v.z, v.t, null, 1)); //label offset

    this.current_gob = null;
    var me = this;
    Ext.Msg.prompt('Label', 'Please enter your text:', function(btn, text) {
        if (btn == 'ok'){
            if (parent)
                parent.addgobjects(g);
            else
                me.viewer.image.addgobjects(g);
            g.value = text;
            me.store_new_gobject ((parent && !parent.uri) ? parent : g);
            me.visit_render.visitall(g, [v]);

            me.renderer.unselectCurrent();
            me.renderer.selectedSet = [g.shape];
            me.renderer.select(me.renderer.selectedSet);
            me.renderer.unselectCurrent();
        }
    });
};


ImgEdit.prototype.matchShape = function(parent, points, eigs, layer){

    var v = this.viewer.current_view;
    var g;
    var shape = {name: '', attributes: {}};
    if(points.length === 1){
        shape.name = 'point';
        shape.vertices = [points[0]];
        return shape;
    }

    var c = eigs.center;
    var r = eigs.vals;
    var v = eigs.vecs;
    var bb = eigs.bbox;

    var A = eigs.area;
    var testRect = new ShapeAnalyzer();

    var dl = testRect.projectToLine(points, eigs);
    var dr = testRect.projectToRect(points, eigs, layer, this.renderer.scale());
    var de = testRect.projectToEllipse(points, eigs);
    if(isNaN(dl)) dl = 99999999;
    if(isNaN(dr)) dr = 99999999;
    if(isNaN(de)) de = 99999999;
//    console.log(dl, dr, de);
    if(dl < de && dl < dr){
        shape.name = 'line';
        shape.vertices = [{x: c[0] + r[0]*v[0][0], y: c[1] + r[0]*v[0][1]},
                          {x: c[0] - r[0]*v[0][0], y: c[1] - r[0]*v[0][1]}]
    }

    else if(de < dr){
       if(Math.abs(1.0 - r[0]/r[1]) < 0.2){
            shape.name = 'circle';
            shape.vertices = [{x: c[0], y: c[1]},
                              {x: c[0] + r[0]*v[0][0], y: c[1] + r[0]*v[0][1]}];

        }

        else{
            shape.name = 'ellipse';
            shape.vertices = [{x: c[0], y: c[1]},
                              {x: c[0] + r[0]*v[0][0], y: c[1] + r[0]*v[0][1]},
                              {x: c[0] + r[1]*v[1][0], y: c[1] + r[1]*v[1][1]}];
        }
    }
    else {
        if(Math.abs(1.0 - r[0]/r[1]) < 0.2){
            shape.name = 'square';

        }

        else{
            shape.name = 'rectangle';
        }
        shape.vertices = [{x: bb.min[0], y: bb.min[1]},
                          {x: bb.max[0], y: bb.max[1]}];
    }
    return shape;
};

ImgEdit.prototype.make_from_gesture = function(parent, gesture){
    g = new BQGObject(gesture.name);
    parent = parent || this.global_parent;

    if (parent) {
        parent.addgobjects(g);
        g.edit_parent = parent;
    } else
        this.viewer.image.addgobjects(g);

    var v = this.viewer.current_view;
    for(var i = 0; i < gesture.vertices.length; i++){
        var c = gesture.vertices[i];
        g.vertices.push (new BQVertex (c.x, c.y, v.z, v.t, null, i));
    }

    this.visit_render.visitall(g, [v]);
    this.renderer.updateVisible();
    g.shape.postEnabled = true;
    this.store_new_gobject ((parent && !parent.uri) ? parent : g);
};

ImgEdit.prototype.new_smart_shape = function (parent, e, x, y) {

    var me = this;
    var v = this.viewer.current_view;
    var g = this.current_gob;
    parent = parent || this.global_parent;

    var points = [];
    var gpoints = [];

    var ept = me.renderer.getUserCoord(e);
    var pte = v.inverseTransformPoint(ept.x, ept.y);
    points.push(pte);


    var gestureLayer = new Kinetic.Layer();
    this.renderer.stage.add(gestureLayer);
    var scale = this.renderer.scale();

    var gesture = new Kinetic.Line({
        points: gpoints,
        close: true,
        //fill: ,
        //fillAlpha: 0.5,
        stroke: 'rgb(255,0,0)',
        strokeWidth: 2/scale,
    });

    var line = new Kinetic.Line({
        points: [],
        fill: 'rgba(128,128,128, 0.25)',
        stroke: 'rgb(128,128,128)',
        strokeWidth: 2/scale,
    });

    var ellipse = new Kinetic.Ellipse({
        fill: 'rgba(128,128,128,0.5)',
        stroke: 'rgba(128,128,128,0.25)',
        strokeWidth: 1/scale,
    });

    var circle = new Kinetic.Circle({
        fill: 'rgba(128,128,128,0.5)',
        stroke: 'rgba(128,128,128,0.25)',
        strokeWidth: 1/scale,
    });

    var rect = new Kinetic.Rect({
        fill: 'rgba(128,128,128,0.5)',
        stroke: 'rgba(128,128,128,0.25)',
        strokeWidth: 1/scale,
    });

    gestureLayer.add(gesture);
    var cshape = line;
    gestureLayer.add(cshape);

    var drag = function(e){
        e.evt.cancelBubble = true;

        var me = this.context;
        var v = me.renderer.viewer.current_view;

        var ept = me.renderer.getUserCoord(e);
        var pte = v.inverseTransformPoint(ept.x, ept.y);
        points.push(pte);
        gpoints.push(pte.x, pte.y);
        gestureLayer.removeChildren();

        var testShape = new ShapeAnalyzer();
        var L = testShape.PCA(points);
        var shape = me.matchShape(parent, points, L, gestureLayer);
        cshape.remove();
        switch(shape.name){
            case 'line': {
                line.points([shape.vertices[0].x, shape.vertices[0].y,
                             shape.vertices[1].x, shape.vertices[1].y]);
                cshape = line;
                break;
            }

            case 'ellipse': {
                var p1 = shape.vertices[0];
                var p2 = shape.vertices[1];
                var p3 = shape.vertices[2];
                var rx =  L.vals[0];
                var ry =  L.vals[1];
                var ang = Math.atan2(p1.y-p2.y, p1.x-p2.x) * 180.0/Math.PI;
                ellipse.x(p1.x);
                ellipse.y(p1.y);
                ellipse.radiusX(rx);
                ellipse.radiusY(ry);
                ellipse.rotation(ang + 180);
                cshape = ellipse;
                break;
            }

            case 'circle': {
                var p1 = shape.vertices[0];
                var p2 = shape.vertices[1];
                var r =  L.vals[0];
                var ang = Math.atan2(p1.y-p2.y, p1.x-p2.x) * 180.0/Math.PI;
                circle.x(p1.x);
                circle.y(p1.y);
                circle.radius(r);
                circle.rotation(ang + 180);
                cshape = circle;
                break;
            }

            case 'rectangle': {
                var p1 = shape.vertices[0];
                var p2 = shape.vertices[1];
                var r =  L.vals[0];
                var ang = Math.atan2(p1.y-p2.y, p1.x-p2.x) * 180.0/Math.PI;
                rect.width(L.width);
                rect.height(L.height);
                rect.x(p1.x);
                rect.y(p1.y);
                cshape = rect;
                break;
            }

            case 'square': {
                var p1 = shape.vertices[0];
                var p2 = shape.vertices[1];
                var r =  L.vals[0];
                var ang = Math.atan2(p1.y-p2.y, p1.x-p2.x) * 180.0/Math.PI;
                rect.width(L.width);
                rect.height(L.height);
                rect.x(p1.x);
                rect.y(p1.y);
                cshape = rect;
                break;
            }

        }

        gestureLayer.add(gesture);
        gestureLayer.add(cshape);
        gestureLayer.draw();
    };


    this.renderer.setmousemove(callback({context: this, points: points},drag));
    this.renderer.setmouseup(callback(this,function(e){
        //me.on_move(me.current_gob);
        me.current_gob = null;
        me.renderer.setmousemove(null);
        me.renderer.setmouseup(null);
        me.renderer.unselectCurrent();

        var testShape = new ShapeAnalyzer();
        var L = testShape.PCA(points);
        var shape = me.matchShape(parent, points, L, gestureLayer);
        me.make_from_gesture(parent, shape);
        setTimeout(function(){
            gestureLayer.remove();
            gesture.remove();
            delete gestureLayer;
            delete gesture;
            delete points;
            delete rect;
            delete circle;
            delete ellipse;
            delete line;
            delete gpoints;
        },300);

        me.renderer.unselectCurrent();
    }));

};

ImgEdit.prototype.newComplex = function (type, internal_gob, parent, e, x, y) {
    parent = parent || this.global_parent;
    var v = this.viewer.current_view;
    // Check if we are constructing a polygon or other multi-point object
    // and if so then skip the creation
    if ( this.current_gob == null) {
        var g = new BQGObject (type);
        if (parent)
            parent.addgobjects (g);
        else
            this.viewer.image.addgobjects(g); //this.gobjects.push(g);
    }
    // This is tricky.. if a primitive type then it receives this g as a parent
    // if internal_gob is complex, then callback already has type, and internal_gob
    // as its first arguments
    internal_gob (g, e, x, y);
};
