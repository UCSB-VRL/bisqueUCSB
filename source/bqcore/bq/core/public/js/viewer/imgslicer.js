/*
  Slice a multiplane image while keeping a few frames around.
*/


function ImgSlicer (viewer, name){
    var p = viewer.parameters || {};
    // default values for projection are: '', 'projectmax', 'projectmin'
    // only in the case of 5D image: 'projectmaxt', 'projectmint', 'projectmaxz', 'projectminz'
    this.default_projection  = p.projection || '';
    this.plane_buffer_sz = 80;  // number of tiles to cache in both z and t
    this.cache_tile_delay_ms = 10; // Delay before requesting a specific tile
    this.update_delay_ms = 30; // Delay before requesting new frames, 150
    this.cache_delay_ms = 200;  // Delay before pre-caching new frames

    this.base = ViewerPlugin;
    this.base (viewer, name);
}

ImgSlicer.prototype = new ViewerPlugin();

ImgSlicer.prototype.create = function (parent) {
    this.parent = parent;

    //this.div  = document.createElementNS(xhtmlns, "div");
    //this.div.id =  'imgviewer_slicer';
    //this.div.className = "image_viewer_slicer";
    this.div  = parent;
    this.tslider = null;
    this.zslider = null;
    this.t = -1;
    this.z = -1;
    this.buffer_len = this.plane_buffer_sz; // Buffer X images
    this.dim = null;           // Last loaded image dimensions

    // pre-cache buffers for both Z and T dimensions
    this.image_buffer_z = [];
    this.image_buffer_t = [];

    //this.cacher_z = new Worker('/core/js/viewer/cacher.js');
    //this.cacher_t = new Worker('/core/js/viewer/cacher.js');

    //parent.appendChild(this.div);
    return this.div;
};

ImgSlicer.prototype.getParams = function () {
    return this.params || {};
};

ImgSlicer.prototype.updateView = function (view) {

    var zMax = view.imagedim.z;
    var tMax = view.imagedim.t;

    if(view.z >= zMax){
        BQ.ui.error('gobject z-dimension exceeds viewing plane');
        this.z = zMax-1;
    }
    if(view.t >= tMax){
        BQ.ui.error('gobject t-dimension exceeds viewing plane');
        this.t = tMax-1;
    }

    if (this.z<0 && this.t<0) {
        this.z = view.z;
        this.t = view.t;
    } else {
        view.z = this.z;
        view.t = this.t;
    }

    var projection = this.default_projection;
    if (!this.menu && this.viewer.viewer_controls_surface) this.createMenu();
    if (this.menu) {
        projection = this.projection_combo.getValue();
    }
    view.projection = projection;

    this.params = {};

    // '', 'projectmax', 'projectmin', 'projectmaxt', 'projectmint', 'projectmaxz', 'projectminz'
    if (!projection || projection==='') {
        if (this.prev) {
            view.z = this.z = this.prev.z;
            view.t = this.t = this.prev.t;
            this.prev = undefined;
        }
        this.params.z1 = view.z+1;
        this.params.t1 = view.t+1;
        view.addParams ( 'slice=,,'+(view.z+1)+','+(view.t+1) );
        if (this.zslider) this.zslider.show();
        if (this.tslider) this.tslider.show();
    } else {
        var showzslider = false,
            showtslider = false,
            newdimz = 1,
            newdimt = 1,
            prjtype = projection,
            dim = view.imagedim;

        if (!this.prev)
            this.prev = {z: view.z, t: view.t};

        if (prjtype.indexOf('projectmax')===0)
            projection = 'intensityprojection=max';
        else if (prjtype.indexOf('projectmin')===0)
            projection = 'intensityprojection=min';

        // now take care of required pre-slicing for 4D/5D cases
        if (prjtype==='projectmaxz' || prjtype==='projectminz') {
            this.params.z1 = 1;
            this.params.z2 = dim.z;
            this.params.t1 = view.t+1;
            //view.addParams ( 'slice=,,1-'+(dim.z)+','+(view.t+1) );
            view.addParams ( 'slice=,,,'+(view.t+1) );
            showtslider = true;
            newdimt = dim.t;
        } else if (prjtype==='projectmaxt' || prjtype==='projectmint') {
            this.params.z1 = dim.z+1;
            this.params.t1 = 1;
            this.params.t2 = view.t;
            //view.addParams ( 'slice=,,'+(view.z+1)+',1-'+(dim.t) );
            view.addParams ( 'slice=,,'+(view.z+1)+',' );
            showzslider = true;
            newdimz = dim.z;
        }
        this.params.projection = projection;

        view.addParams (projection);
        view.imagedim.t = newdimt;
        view.imagedim.z = newdimz;
        view.imagedim.project = prjtype;
        if (this.zslider) this.zslider.setVisible(showzslider);
        if (this.tslider) this.tslider.setVisible(showtslider);
    }
};

ImgSlicer.prototype.updateImage = function () {
    var view = this.viewer.current_view,
        dim = view.imagedim.clone(),
        imgphys = this.viewer.imagephys;

    if (!this.pixel_info_z) {
      this.pixel_info_z = [undefined,undefined];
      if (imgphys) this.pixel_info_z = imgphys.getPixelInfoZ();
    }
    if (!this.pixel_info_t) {
      this.pixel_info_t = [undefined,undefined];
      if (imgphys) this.pixel_info_t = imgphys.getPixelInfoT();
    }

    // recompute sliders
    if (this.dim === null || this.dim.t !== dim.t) {
        if (this.tslider) {
            this.tslider.destroy();
            this.tslider=null;
        }
        if (dim.t<=1) {
            if (this.tslider) { this.tslider.destroy(); this.tslider=null; }
            this.t = 0;
        }
    }
    if (this.dim === null || this.dim.z !== dim.z) {
        if (this.zslider) {
            this.zslider.destroy();
            this.zslider=null;
        }
        if (dim.z<=1) {
            if (this.zslider) { this.zslider.destroy(); this.zslider=null; }
            this.z = 0;
        }

    }
    this.dim = dim;

    if (this.cache_timeout) clearTimeout (this.cache_timeout);
    if (this.dim.z>1 || this.dim.t>1)
        this.cache_timeout = setTimeout(callback(this, 'preCacheNeighboringImages'), this.cache_delay_ms);
};

ImgSlicer.prototype.updatePosition = function () {
    var view = this.viewer.current_view,
        dim = view.imagedim.clone(),
        surf = this.viewer.viewer_controls_surface || this.div;

    if (!this.tslider && dim.t>1) {
        this.tslider = Ext.create('BQ.slider.TSlider', {
            renderTo: surf,
            autoShow: true,
            hysteresis: this.update_delay_ms,
            value: view.t,
            minValue: 0,
            maxValue: dim.t-1,
            listeners: {
                scope: this,
                change: function(newValue) {
                    this.sliceT(newValue);
                },
            },
            resolution: this.pixel_info_t[0],
            unit: this.pixel_info_t[1],
        });
    }

    if (!this.zslider && dim.z>1) {
        this.zslider = Ext.create('BQ.slider.ZSlider', {
            renderTo: surf,
            autoShow: true,
            hysteresis: this.update_delay_ms,
            value: view.z,
            minValue: 0,
            maxValue: dim.z-1,
            listeners: {
                scope: this,
                change: function(newValue) {
                    this.sliceZ(newValue);
                },
            },
            resolution: this.pixel_info_z[0],
            unit: this.pixel_info_z[1],
        });
    }

};

ImgSlicer.prototype.sliceT = function (val) {
    if (this.t === val) return;
    this.t = val;
    this.viewer.need_update();
};

ImgSlicer.prototype.sliceZ = function (val) {
    if (this.z === val) return;
    this.z = val;
    this.viewer.need_update();
};

ImgSlicer.prototype.setPosition = function (z, t) {
    if(this.z === z && this.t === t) return;
    if (typeof z !== "undefined") {
        this.z = z;
        if (this.zslider)
            this.zslider.setValue(z);
    }
    if (typeof t !== "undefined") {
        this.t = t;
        if (this.tslider)
            this.tslider.setValue(t);
    }
    this.viewer.need_update();
};

ImgSlicer.prototype.ensureVisible = function (gob) {
    if (!gob || !gob.vertices || gob.vertices.length<1) return;
    var z = gob.vertices[0].z,
        t = gob.vertices[0].t;
    /*var v=undefined;
    if (gob.vertices.length>1 && gob.resource_type in {polyline: undefined, polygon: undefined}) {
        for (var i=1; (v=gob.vertices[i]); i++) {
            z += v.z;
            t += v.t;
        }
        z /= gob.vertices.length;
        t /= gob.vertices.length;
    }*/

    this.setPosition (z, t);
};

//-------------------------------------------------------------------------
// Z/T cache
//-------------------------------------------------------------------------

ImgSlicer.prototype.doCacheTile = function (buf, pos, url) {
    try {
        buf[pos].src = url;
    } catch (e) {
        var I = new Image();
        I.validate = "never";
        I.src = url;
        buf[pos] = I;
    }
};

/*
ImgSlicer.prototype.doCacheTile = function (cacher, pos, url) {
    cacher.postMessage({
        url: url,
        pos: pos,
    });
};
*/

ImgSlicer.prototype.queueCacheTile = function (buf, pos, url) {
    setTimeout(callback(this, 'doCacheTile', buf, pos, url), this.cache_tile_delay_ms);
};

ImgSlicer.prototype.cacheTiles = function (pos, posmax, buf, index, slice, nslice, tiles) {
    if (pos<0) return 0;
    if (pos>=posmax) return 0;
    var num_tiles = tiles.length;
    for (var p=0; p<num_tiles; p++) {
        var url = tiles[p].replace(slice, nslice);
        this.queueCacheTile(buf, index+p, url);
    }
    return num_tiles;
};

ImgSlicer.prototype.preCacheNeighboringImages = function () {
    this.cache_timeout = null;
    var view = this.viewer.current_view,
        projection = view.projection,
        template = 'slice=,,{Z},{T}';

    if (projection==='projectmaxz' || projection==='projectminz') {
        template = 'slice=,,,{T}';
    } else if (projection==='projectmaxt' || projection==='projectmint') {
        template = 'slice=,,{Z},';
    }

    var tiles = this.viewer.tiles.getLoadedTileUrls(),
        //slice = 'slice=,,'+(this.z+1)+','+(this.t+1),
        slice = template.replace('{Z}', this.z+1).replace('{T}', this.t+1),
        dim = this.dim,
        i=1, szz=0, szt=0; // i=0 for halfs
    while (szz+szt<this.buffer_len) {
        //var hp = Math.floor(i/2)+1;
        var dz=0;
        if (dim.z>1 && projection!=='projectmaxz' && projection!=='projectminz') {
            //var z = i%2 ? this.z-hp : this.z+hp;
            var z = this.z+i;
            var nslice = template.replace('{Z}', z+1).replace('{T}', this.t+1);
            dz += this.cacheTiles(z, dim.z, this.image_buffer_z, szz, slice, nslice, tiles);

            var z = this.z-i;
            var nslice = template.replace('{Z}', z+1).replace('{T}', this.t+1);
            dz += this.cacheTiles(z, dim.z, this.image_buffer_z, szz+dz, slice, nslice, tiles);

            szz += dz;
        }

        var dt=0;
        if (dim.t>1 && projection!=='projectmaxt' && projection!=='projectmint') {
            //var t = i%2 ? this.t-hp : this.t+hp;

            var t = this.t+i;
            var nslice = template.replace('{Z}', this.z+1).replace('{T}', t+1);
            dt += this.cacheTiles(t, dim.t, this.image_buffer_t, szt, slice, nslice, tiles);

            var t = this.t-i;
            var nslice = template.replace('{Z}', this.z+1).replace('{T}', t+1);
            dt += this.cacheTiles(t, dim.t, this.image_buffer_t, szt+dt, slice, nslice, tiles);

            szt += dt;
        }
        if (dz+dt<1) return;
        i++;
    }
};

//-------------------------------------------------------------------------
// Menu GUI for projections
//-------------------------------------------------------------------------

ImgSlicer.prototype.doUpdate = function () {
    this.viewer.need_update();
};

ImgSlicer.prototype.changed = function () {
  //if (!this.update_check || (this.update_check && this.update_check.checked) )
    BQ.Preferences.set(this.viewer.image.resource_uniq, 'Viewer/projection', this.projection_combo.value);
    this.viewer.need_update();
};

//-------------------------------------------------------------------------
// Menu for projections
//-------------------------------------------------------------------------

ImgSlicer.prototype.createMenu = function () {
    if (this.menu) return;
    this.menu = this.viewer.createViewMenu();

    this.loadPreferences(this.viewer.preferences);

    var dim = this.viewer.imagedim;
    //var planes_title = 'Image planes [W:'+dim.x+', H:'+dim.y+', Z:'+dim.z+', T:'+dim.t+']';
    var planes_title = 'Image planes [Z:'+dim.z+', T:'+dim.t+']';


    var combo_options = [ {'value':'', 'text':'None'} ];

    // only add projection options for 3D images
    if (dim.z>1 || dim.t>1) {
        combo_options.push({'value':'projectmax', 'text':'Max'});
        combo_options.push({'value':'projectmin', 'text':'Min'});
    }

    // only add these additional options for 4D/5D images
    if (dim.z>1 && dim.t>1) {
        combo_options.push({'value':'projectmaxz', 'text':'Max for current T'});
        combo_options.push({'value':'projectminz', 'text':'Min for current T'});
        combo_options.push({'value':'projectmaxt', 'text':'Max for current Z'});
        combo_options.push({'value':'projectmint', 'text':'Min for current Z'});
    }

    this.projection_heading = this.menu.add({
        xtype: 'displayfield',
        fieldLabel: planes_title,
        cls: 'heading',
    });

    this.projection_combo = this.viewer.createCombo( 'Intensity projection', combo_options, this.default_projection, this, this.changed);

    if (dim.z*dim.t===1) {
        this.projection_heading.setVisible(false);
        this.projection_combo.setVisible(false);
    }
};

ImgSlicer.prototype.loadPreferences = function (p) {
    if (!p) return;
    this.default_projection  = 'projection'  in p ? p.projection  : this.default_projection;
};

ImgSlicer.prototype.onPreferences = function () {
    var resource_uniq = this.viewer.image.resource_uniq;
    this.default_projection  = BQ.Preferences.get(resource_uniq, 'Viewer/projection', this.default_projection);
};

