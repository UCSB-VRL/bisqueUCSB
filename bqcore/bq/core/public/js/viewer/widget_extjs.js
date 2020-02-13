/*******************************************************************************
  ExtJS wrapper for the Bisque image viewer
  Author: Dima Fedorov <dima@dimin.net>

  Configurations:
      resource   - url string or bqimage
      user       - url string
      parameters - viewer configuration object describied later

  Events:
      loaded     - event fired when the viewer is loaded
      changed    - event fired when the gobjects in the viewer have changed
      loadedPhys - event fired when image physics is loaded
      working
      done
      error
      delete     - event fired when gobject(s) is(are) deleted
      moveend    - event fired when mouse up on selected gobject
      afterPhys  - event fired after phys is loaded

  Parameters:
    simpleviewer   - sets a minimal set of plug-ins and also read-only view for gobjects
    onlyedit       - only sets plug-in needed for editing of gobjects

    nogobects      - disable loading gobjects by default
    gobjects       - load gobjects from the givel URL, 'gobjects':'http://gobejcts_url' or a BQGobject or a vector of BQGObject

    noedit         - read-only view for gobjects
    alwaysedit     - instantiates editor right away and disables hiding it
    nosave         - disables saving gobjects
    editprimitives - only load edit for given primitives, 'editprimitives':'point,polyline'
                     can be one of: 'Point,Rectangle,Polyline,Polygon,Circle'
                     may contain semantic types as well
    semantic_types - false - hides the gobject types list
                     true - shows the gobject types list
                     'require' - shows and does not permit non-semantic types from being selected

    gobjectDeleted
    gobjectCreated

    gobjectMove      - returns shape object when manipulating a gobject, shape object has pointer to gob
    gobjectMoveStart - returns shape object when beginning a gobject manipulation, shape object has pointer to gob
    gobjectMoveEnd   - returns shape object when ending a gobject manipulation, shape object has pointer to gob

    blockforsaves  - set to true to show saving of gobjects, def: true
    showmanipulators - turns off advanced manipulators in the canvas renderer
       jrd: this should really be more advanced and allow you to customize what options you want to show on
            the renderer ie: toggle shape corners, manipulators, bounding boxes, debugging tree, etc

  Example:
    var myviewer = Ext.create('BQ.viewer.Image', {
        resource: 'http://image_url',
        user: 'user_name',
        parameters: {
            'gobjects': 'http://gobejcts_url',
            'noedit': '',
        },
    });
*******************************************************************************/

Ext.define('BQ.viewer.Image', {
    alias: 'widget.imageviewer',
    extend: 'Ext.container.Container',
    requires: ['ImgViewer'],
    border: 0,
    cls: 'bq-image-viewer',
    layout: 'fit',

    constructor: function(config) {
        this.addEvents({
            'loaded': true,
            'changed': true,
        });
        this.callParent(arguments);
        return this;
    },

    initComponent : function() {
        this.addListener( 'resize', function(me, width, height) {
            if (me.viewer) me.viewer.resize();
        });
        this.callParent();
    },

    onDestroy : function(){
        if (this.viewer)
            this.viewer.cleanup();
        this.callParent();
    },

    afterRender : function() {
        this.callParent();
        this.setLoading('Loading image resource');
        if (this.resource && typeof this.resource === 'string')
            BQFactory.request({
                uri: this.resource,
                uri_params: {view: 'short'},
                cb: callback(this, this.loadViewer),
                errorcb: callback(this, this.onerror),
            });
        else
            this.loadViewer(this.resource);

        // this.keyNav = Ext.create('Ext.util.KeyNav', { //document.body, {
        //     target:   document.body,
        //     left:     this.onkeyboard,
        //     right:    this.onkeyboard,
        //     up:       this.onkeyboard,
        //     down:     this.onkeyboard,
        //     pageUp:   this.onkeyboard,
        //     pageDown: this.onkeyboard,
        //     scope : this
        // });
    },

    loadViewer: function(resource) {
        //this.setLoading(false);
        if (!resource) return;
        if (this.loaded) return;
        this.loaded = true;
        this.resource = resource;

        this.parameters = this.parameters || {};
        this.parameters.blockforsaves = 'blockforsaves' in this.parameters ? this.parameters.blockforsaves : true;
        if (this.toolbar)
            this.parameters.toolbar = this.toolbar;
        this.parameters.widget = this;

        this.parameters.gobjectCreated  = callback(this, 'oncreate')
        this.parameters.gobjectschanged = callback(this, 'onchanged');
        this.parameters.gobjectDeleted  = callback(this, 'ondelete');
        this.parameters.gobjectMove     = callback(this, 'onmove');
        this.parameters.gobjectMoveEnd  = callback(this, 'onmoveend'); //mouse up on gobject

        this.parameters.onworking       = callback(this, 'onworking');
        this.parameters.ondone          = callback(this, 'ondone');
        this.parameters.onerror         = callback(this, 'onerror');
        this.parameters.onselect        = callback(this, 'onselect');
        this.parameters.onhover         = callback(this, 'onhover');
        this.parameters.onmodechange    = callback(this, 'onmodechange');

        //this.parameters.gobjectMoveStart= callback(this, 'onmovestart'); on mouse down
        //this.parameters.gobjectMove          = callback(this, 'onmove'); expensive
        this.parameters.onloaded        = callback(this, this.onloaded);
        this.parameters.onphys          = callback(this, this.onphys);
        this.parameters.afterphys       = callback(this, this.afterphys);
        this.parameters.oneditcontrols  = callback(this, this.oneditcontrols);
        this.parameters.onposition      = callback(this, this.onposition);

        this.parameters.tagsChanged     = callback(this, this.onTagsChanged);

        //var id = Ext.getVersion('core').isGreaterThan('4.2.0') ? this.getId()+'-innerCt' : this.getId();
        var id = this.getId();
        this.viewer = new ImgViewer(id, this.resource, this.parameters);
        //this.viewer.resize();

        // dima: ultra ugly fix laying out toolbar on delay - NEEDS PROPER FIX!!!!
        if (this.toolbar) {
            var element = this.toolbar;
            setTimeout(function(){ element.updateLayout(); }, 1000);
        }
        this.fireEvent( 'loaded', this );
    },

    onloaded : function() {
        this.setLoading(false);
        this.viewer.resize();
    },

    setButtonLoading : function(msg) {
        if(this.viewer.plugins_by_name.edit)
            this.viewer.plugins_by_name.edit.setButtonLoading(msg);
    },

    onphys : function() {
        this.fireEvent( 'loadedPhys', this, this.viewer.imagephys, this.viewer.imagedim );
    },


    afterphys : function() {
        this.fireEvent( 'afterPhys', this, this.viewer.imagephys, this.viewer.imagedim );

    },

    onchanged : function(gobs) {
        this.fireEvent( 'changed', this, gobs );
    },

    oncreate : function(gobs) {
        this.fireEvent( 'create', this, gobs );
    },


    ondelete: function(gobs) {
        this.fireEvent( 'delete', this, gobs );
    },


    onmove : function(gobs) {
        this.fireEvent( 'gobmove', this, gobs );
    },

    onmoveend : function(gobs) {
        this.fireEvent( 'moveend', this, gobs );
    },

    getGobjects : function() {
        if (!this.viewer) return undefined;
        return this.viewer.gobjects();
    },

    // g can be either a url, BQGobject or an array of BQGobject
    setGobjects : function(g) {
        if (!this.viewer) return;
        this.viewer.loadGObjects(g);
    },

    select_plane: function(z, t)  {
        this.viewer.select_plane(z, t);
    },

    rerender : function() {
        if (!this.viewer) return;
        this.viewer.rerender();
    },

    onworking : function(msg) {
        if (this.parameters.blockforsaves) this.setLoading(msg);
        this.fireEvent( 'working', this, msg );
    },

    ondone : function() {
        //if (this.parameters.blockforsaves)
        this.setLoading(false);
        this.fireEvent( 'done', this );
    },

    onerror : function(error) {
        //if (this.parameters.blockforsaves)
        this.setLoading(false);
        if (this.hasListeners.error)
            this.fireEvent( 'error', error );
        else
            BQ.ui.error(error.message_short);
    },

    onhover : function(gob, e) {
        //this.fireEvent( 'hover', this, gob, e );
        /*if (!gob) {
            if (this.hoverMenu)
                this.hoverMenu.hide();
            return;
        }*/

        tagData  = function(gob) {
            var g = gob,
                tree = [],
                found = '',
                level = 0,
                cls = '',
                text = '',
                t = null;

            while (g && g.parent) {
                tree.push(g);
                g = g.parent;
            }
            tree.reverse();

            level = tree.length;
            for (var i=0; (t=tree[i]); ++i) {
                cls = level<=2 ? 'emph' : '';
                text = (t.type || t.name);
                if (t instanceof BQGObject && t.name) {
                    text += ': ' + t.name;
                }
                if (t instanceof BQGObject && t.type==='label' && t.value) {
                    text += ': ' + t.value;
                }

                //text += t.value ? ': '+t.value : '';
                found += '<p class="'+cls+'" style="margin-left: '+(i*10)+'px;">' + text + '</p>';
                level -= 1;
            }

            // add sub-tags
            level = tree.length+1;
            if (gob && gob.tags) {
                var N = Math.min(10, gob.tags.length);
                for (var i=0; i<N; ++i) {
                    t = gob.tags[i];
                    if (t.type in BQ.annotations.types_ignore_user_presentation)
                        continue;
                    if (t.value && t.value.startsWith && (t.value.startsWith('http') || t.value.startsWith('/'))) {
                        if (t.type in BQ.resources.all)
                            text = Ext.String.format('<a href="/client_service/view?resource={1}">{0}</a>', t.name, t.value);
                        else
                            text = Ext.String.format('<a href="{1}">{0}: {1}</a>', t.name, t.value);
                    } else {
                        text = t.name + ': ' + t.value;
                    }

                    cls = 'tags';
                    if (t.type)
                       cls += ' '+t.type;
                    found += Ext.String.format('<p class="{0}" style="margin-left: {1}px;">{2}</p>', cls, level*10, text);
                }
            }

            return found;
        }
        if (!gob) return;
        if (!this.hoverMenu) {
            this.hoverMenu = Ext.create('Ext.tip.ToolTip', {
                cls: 'viewer_tooltip',
                anchor : 'left',
                anchorToTarget : true,
                autoHide: true,
                autoShow: false,
                showDelay: 0,
                hideDelay: 0,
                dismissDelay: 10000,
                trackMouse: false,
                gob: gob,

                //maxWidth : 200,
                layout: 'fit',
                items: [{
                    xtype:'tbtext',
                    itemId: 'text',
                    text: tagData(gob),
                }],
            });
            this.hover_text = this.hoverMenu.queryById('text');
            this.hoverMenu.showAt([e.clientX+15, e.clientY-10]);
        } else if (this.hoverMenu.gob !== gob || this.hoverMenu.isVisible() === false) {
            this.hover_text.setText(tagData(gob));
            this.hoverMenu.showAt([e.clientX+15, e.clientY-10]);
        }
        //console.log(e.clientX, e.clientY);
        //this.hoverMenu.showAt([e.clientX+15, e.clientY-10]);
    },

    onmodechange : function(type) {
        //console.log(gob,e);
        this.fireEvent( 'modechange', this, type );
    },

    onselect : function(gob) {
        this.fireEvent( 'select', this, gob );
    },

    oneditcontrols : function() {
        this.fireEvent( 'edit_controls_activated', this );
    },

    onkeyboard: function(e) {
        this.viewer.onkeyboard(e);
    },

    onposition : function(pt) {
        this.fireEvent( 'position_selected', pt, this );
    },

    onTagsChanged : function() {
        this.fireEvent( 'tags_changed', this );
    },

});
