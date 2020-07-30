/*
*   SVGRenderer imageViewer Plugin
*
*
*/
function SVGRenderer (viewer,name) {
    var p = viewer.parameters || {};
    this.default_overlayPref  = {
        enable    : false,
        position  : '',  //position reads p1;p2;p3;p4 p=x,y
        shape     : 'dots',
    };
    this.base = ViewerPlugin;
    this.base (viewer, name);
    this.events  = {};

    //overlay Editor
    var me = this;
    if (this.viewer.toolbar) { //required toolbar to initialize and the user to be signed in
        var operation_menu = this.viewer.toolbar.queryById('menu_viewer_operations');
        if (operation_menu) {
            var image = this.viewer.image;
            var resource = image ? image.uri : '';
            overlayEditor = operation_menu.menu.add({
                xtype   : 'menuitem',
                itemId  : 'menu_viewer_operation_overlayEditor',
                text    : 'Overlay Editor',
                disabled: !BQApp.hasUser(),
                disabled: true,
                handler: function() {
                    if (!me.overlayEditorWin) {
                        var image = this.viewer.image;
                        var resource = image? image.uri : '';
                        me.overlayEditorWin = Ext.create('BQ.overlayEditor.Window',{
                            title: 'Overlay Editor',
                            height: '90%',
                            width: '90%',
                            modal: true,
                            closeAction: 'hide',
                            viewer: me.viewer,
                            phys: me.viewer.imagephys,
                            image_resource:resource,
                        });
                    }
                    me.overlayEditorWin.show();
                },

            });
            BQApp.on('gotuser', function() {
                overlayEditor.setDisabled(false);
            }); //enable editor since user was found
            if (BQApp.hasUser()) { //checks for user
                overlayEditor.setDisabled(false);
            }
        }
    }
};

SVGRenderer.prototype = new ViewerPlugin();

SVGRenderer.prototype.create = function (parent) {
    this.overlay = document.createElementNS(svgns, "svg");
    this.overlay.setAttributeNS(null, 'class', 'gobjects_overlay');
    this.overlay.setAttributeNS(null, 'id', 'overlay');
    parent.appendChild(this.overlay);
    this.overlay.style.position = "absolute";
    this.overlay.style.top = "0px";
    this.overlay.style.left = "0px";
    this.parent = parent;
    return parent;
};

SVGRenderer.prototype.newImage = function () {
    var me = this;
    if (me.overlayEditorWin) {
        this.phys_inited = false;
        var image = this.viewer.image;
        var resource = image? image.uri : ''
        me.overlayEditorWin.miniViewer.resource = resource;
        // adds gobjects if the preferences already have overlay points

        var pattern =/([A-Za-z0-9_.]+),([A-Za-z0-9_.]+);([A-Za-z0-9_.]+),([A-Za-z0-9_.]+);([A-Za-z0-9_.]+),([A-Za-z0-9_.]+);([A-Za-z0-9_.]+),([A-Za-z0-9_.]+)/;
        var points = this.overlayPref.position.match(pattern);
        var editor = me.overlayEditorWin.miniViewer.plugins_by_name.edit;
        var gobs = me.overlayEditorWin.miniViewer.getGobjects();
        for (var g = 0;g<gobs.length;g++) { //remove all existing gobs on the viewer
            editor.remove_gobject(gobs[g]);
        }
    }
};

SVGRenderer.prototype.updateView = function (view) {
    if (this.initialized || !this.viewer.tiles.tiled_viewer) return;
    this.initialized = true;
    this.myListener = new SvgControl( this.viewer.tiles.tiled_viewer, this.overlay );
    if (this.overlayPref.enable)
        this.populate_overlay(this.showOverlay);
};


SVGRenderer.prototype.updateImage = function () {
    var viewstate = this.viewer.current_view;
    this.overlay.setAttributeNS( null, 'width', viewstate.width);
    this.overlay.setAttributeNS( null, 'height', viewstate.height);
    this.updateTransform();
};

//----------------------------------------------------------------------------
// preferences and overlays
//----------------------------------------------------------------------------

SVGRenderer.prototype.onPreferences = function() {
    this.overlayPref = {};
    var resource_uniq = this.viewer.image.resource_uniq;
    this.overlayPref.enable   = BQ.Preferences.get(resource_uniq, 'Viewer/Overlay/enable',   this.default_overlayPref.enable);
    this.overlayPref.position = BQ.Preferences.get(resource_uniq, 'Viewer/Overlay/position', this.default_overlayPref.position);
    this.overlayPref.shape    = BQ.Preferences.get(resource_uniq, 'Viewer/Overlay/shape',    this.default_overlayPref.shape);
    if (this.overlay) //check to see if the overlay is attached to the viewer
        this.populate_overlay();
};


/*
*   Functions for finding the homography matrix
*
*/
SVGRenderer.prototype.det2D = function(x) {
    return x[0]*x[3] - x[1]*x[2];
};

SVGRenderer.prototype.det3x3 = function(x) {
    return (x[0]*x[4]*x[8] + x[1]*x[5]*x[6] + x[2]*x[3]*x[7]) - (x[2]*x[4]*x[6] + x[1]*x[3]*x[8] + x[0]*x[5]*x[7]);
};

/*
*   adj3x3
*   3 by 3 Adjugate matrix
*/
SVGRenderer.prototype.adj3x3 = function(x) {
    return [
        this.det2D([x[4],x[5],x[7],x[8]]),
        -this.det2D([x[3],x[5],x[6],x[8]]),
        this.det2D([x[3],x[4],x[6],x[7]]),
        -this.det2D([x[1],x[2],x[7],x[8]]),
        this.det2D([x[0],x[2],x[6],x[8]]),
        -this.det2D([x[0],x[1],x[6],x[7]]),
        this.det2D([x[1],x[2],x[4],x[5]]),
        -this.det2D([x[0],x[2],x[3],x[5]]),
        this.det2D([x[0],x[1],x[3],x[4]]),
    ];
};

SVGRenderer.prototype.scaleMult3x3 = function(scalar, mat) {
    return [
        scalar*mat[0],
        scalar*mat[1],
        scalar*mat[2],
        scalar*mat[3],
        scalar*mat[4],
        scalar*mat[5],
        scalar*mat[6],
        scalar*mat[7],
        scalar*mat[8],
    ];
};

SVGRenderer.prototype.inv3x3 = function(x) {
    return this.scaleMult3x3(1/this.det3x3(x), this.trans3x3(this.adj3x3(x)));
};

SVGRenderer.prototype.trans3x3 = function(x) {
    return [
        x[0],x[3],x[6],
        x[1],x[4],x[7],
        x[2],x[5],x[8],
    ]
};

SVGRenderer.prototype.matMultiply3x3 = function(x, y) {
    var z = Array(9);
    for (var i =0; i<3; ++i) {
        for (var j =0; j<3; ++j) {
            var c = 0;
            for  (var k = 0; k<3; ++k) {
                c += x[3*i + k]*y[3*k + j];
            }
            z[3*i + j] = c;
        }
    }
    return z;
};

SVGRenderer.prototype.mapMat = function(x1,y1,x2,y2,x3,y3,x4,y4) {
    var d = this.det3x3([x1,x2,x3,y1,y2,y3,1.0,1.0,1.0]);
    var x = this.det3x3([x4,x2,x3,y4,y2,y3,1.0,1.0,1.0])/d;
    var y = this.det3x3([x1,x4,x3,y1,y4,y3,1.0,1.0,1.0])/d;
    var z = this.det3x3([x1,x2,x4,y1,y2,y4,1.0,1.0,1.0])/d;
    return [
        x*x1,y*x2,z*x3,
        x*y1,y*y2,z*y3,
        x,y,z
    ];
};

SVGRenderer.prototype.fourPointsHomographyMat = function(x11,y11,x12,y12,x13,y13,x14,y14,x21,y21,x22,y22,x23,y23,x24,y24) {
    var A = this.mapMat(x11,y11,x12,y12,x13,y13,x14,y14);
    var B = this.mapMat(x21,y21,x22,y22,x23,y23,x24,y24);
    return this.matMultiply3x3(B, this.inv3x3(A));
};


SVGRenderer.prototype.distance = function(x1,y1,x2,y2) {
    return Math.sqrt(Math.pow(x1-x2,2)+Math.pow(y1-y2,2));
};

SVGRenderer.prototype.slope = function(x1,y1,x2,y2) {
    return (y2-y1)/(x2-x1);
};

SVGRenderer.prototype.radian2degrees = function(radians) {
    return radians * 180 / Math.PI;
};

SVGRenderer.prototype.updateTransform = function() {

    var view = this.viewer.view();
    if (view&&this.overlayPref.enable) {
        t = [ //initial transform
            1, 0, 0, 0,
            0, 1, 0, 0,
            0, 0, 1, 0,
            0, 0, 0, 1,
        ];
        if (this.overlayPref.position) {
            var pattern = /([A-Za-z0-9_.]+),([A-Za-z0-9_.]+);([A-Za-z0-9_.]+),([A-Za-z0-9_.]+);([A-Za-z0-9_.]+),([A-Za-z0-9_.]+);([A-Za-z0-9_.]+),([A-Za-z0-9_.]+)/;
            var points = this.overlayPref.position.match(pattern);
            if (points && (points.length == 9)) {
                var h = this.fourPointsHomographyMat(
                    0,0,view.width,0,0,view.height,view.width,view.height,
                    points[1]*(view.width/view.original_width),points[2]*(view.height/view.original_height),
                    points[3]*(view.width/view.original_width),points[4]*(view.height/view.original_height),
                    points[5]*(view.width/view.original_width),points[6]*(view.height/view.original_height),
                    points[7]*(view.width/view.original_width),points[8]*(view.height/view.original_height)
                );

                t = [
                    h[0], h[3], 0, h[6],
                    h[1], h[4], 0, h[7],
                    0,       0, 1,    0,
                    h[2], h[5], 0, h[8],
                ];
            }
        }
        var transform = 'matrix3d('+t.join(',')+')';
        this.overlay.style['transform-origin'] = '0 0';
        this.overlay.style['-webkit-transform-origin'] = '0 0';
        this.overlay.style['transform'] = transform;
        this.overlay.style['-webkit-transform'] = transform;
    }
};

SVGRenderer.render_defaults = {
    dots: {
        x_beg: 9,
        x_end: 95,
        x_step: 9,
        y_beg: 12,
        y_end: 95,
        y_step: 9,
    },
    dots_medium: {
        x_beg: 9,
        x_end: 95,
        x_step: 9,
        y_beg: 15,
        y_end: 90,
        y_step: 8,
    },
    dots_narrow: {
        x_beg: 15,
        x_end: 90,
        x_step: 8,
        y_beg: 20,
        y_end: 85,
        y_step: 7,
    },
    dots_custom: {
        x_beg: 2,
        x_end: 98,
        x_step: 10,
        y_beg: 2,
        y_end: 98,
        y_step: 10,
    },
    dots_dense: {
        x_beg: 2,
        x_end: 99,
        x_step: 6,
        y_beg: 2,
        y_end: 99,
        y_step: 6,
    },
    dots_12: {
        x_beg: 12,
        x_end: 95,
        x_step: 25,
        y_beg: 20,
        y_end: 95,
        y_step: 30,
    },
};

SVGRenderer.prototype.populate_overlay = function () {
    if (this.overlayPref.enable) {
        removeAllChildren (this.overlay);
        var gobs = document.createElementNS(svgns, "g");
        this.overlay.appendChild(gobs);
        this.updateTransform();

        if (this.overlayPref.shape in SVGRenderer.render_defaults) {
            var p = SVGRenderer.render_defaults[this.overlayPref.shape];
            for (var x=p.x_beg; x<=p.x_end; x+=p.x_step)
            for (var y=p.y_beg; y<=p.y_end; y+=p.y_step) {
                var circ = document.createElementNS( svgns, 'circle');
                circ.setAttributeNS(null, 'fill-opacity', 0.0);
                circ.setAttributeNS(null, 'fill', 'black');
                circ.setAttributeNS(null, 'stroke', 'black');
                circ.setAttributeNS(null, 'stroke-width', 2);
                circ.setAttributeNS(null, 'cx', ''+x+'%' );
                circ.setAttributeNS(null, 'cy', ''+y+'%');
                circ.setAttributeNS(null, 'r', '1%' );
                gobs.appendChild(circ);

                var circ = document.createElementNS( svgns, 'circle');
                circ.setAttributeNS(null, 'fill-opacity', 0.0);
                circ.setAttributeNS(null, 'fill', 'black');
                circ.setAttributeNS(null, 'stroke', 'white');
                circ.setAttributeNS(null, 'stroke-width', 1);
                circ.setAttributeNS(null, 'cx', ''+x+'%' );
                circ.setAttributeNS(null, 'cy', ''+y+'%');
                circ.setAttributeNS(null, 'r', '1%' );
                gobs.appendChild(circ);
            }
        } else if (this.overlayPref.shape === 'grid') {
            for (var y=12; y<=95; y+=9) {
                var circ = document.createElementNS( svgns, 'line');
                circ.setAttributeNS(null, 'fill-opacity', 0.0);
                circ.setAttributeNS(null, 'fill', 'black');
                circ.setAttributeNS(null, 'stroke', 'black');
                circ.setAttributeNS(null, 'stroke-width', 2);
                circ.setAttributeNS(null, 'x1', '0%' );
                circ.setAttributeNS(null, 'x2', '100%' );
                circ.setAttributeNS(null, 'y1', ''+y+'%');
                circ.setAttributeNS(null, 'y2', ''+y+'%');
                gobs.appendChild(circ);

                var circ = document.createElementNS( svgns, 'line');
                circ.setAttributeNS(null, 'fill-opacity', 0.0);
                circ.setAttributeNS(null, 'fill', 'black');
                circ.setAttributeNS(null, 'stroke', 'white');
                circ.setAttributeNS(null, 'stroke-width', 1);
                circ.setAttributeNS(null, 'x1', '0%' );
                circ.setAttributeNS(null, 'x2', '100%' );
                circ.setAttributeNS(null, 'y1', ''+y+'%');
                circ.setAttributeNS(null, 'y2', ''+y+'%');
                gobs.appendChild(circ);
            }
        }
    }
};

Ext.define('BQ.overlayEditor.Window', {
    extend: 'Ext.window.Window',
    title: 'Layout Editor',
    image_resource: '',
    layout: {
        type: 'vbox',
        align: 'stretch',
    },
    viewer: undefined,
    buttonAlign: 'center',
    bodyStyle: 'background-color:#FFFFFF', //set background to white
    initComponent: function(config) {
        var config = config || {};
        var me = this;

        var items = [{
            xtype: 'container',
            //padding: '10px',
            html: '<p>Place 4 points on the viewer and click Save to place the overlay over the image.</p>',
            //flex: 1,
        }, {
            xtype:'imageviewer',
            itemId: 'miniViewer',
            flex: 6,
            resource: me.image_resource,
            parameters: {
                nosave: true,
                onlyedit: true,
                editprimitives: 'point',
                showmanipulators: false,
                intialMode: 'point',
                semantic_types: false,
                widget: this,
            },
            listeners: {
                'afterPhys': me.onAfterPhys.bind(me),
                'changed': me.onChanged.bind(me),
                'delete': me.onChanged.bind(me),
                'moveend': me.onChanged.bind(me),
            },
        }];


        var fbar = [{
            scale: 'large',
            xtype: 'button',
            margin: '0 8 0 8',
            text: 'Save',
            handler: function() {
                var gobs = me.miniViewer.getGobjects();
                var gobs = gobs.slice();
                if (gobs.length!=4) {
                    BQ.ui.notification('Four points are required to set the overlay');
                    return
                }

                view = me.viewer.view();

                corners = [
                    {x:0,y:0},
                    {x:view.original_width,y:0},
                    {x:0, y:view.original_height},
                    {x:view.original_width, y:view.original_height}
                ];

                //select and order the points
                var points = gobs;

                var points = me.mapPoints(gobs);

                //create put to the preference
                var overlayTag = document.createElement('tag');
                overlayTag.setAttribute('name', 'Overlay');

                var enableTag = document.createElement('tag');
                enableTag.setAttribute('name', 'enable');
                enableTag.setAttribute('value', 'true');
                overlayTag.appendChild(enableTag);

                var positionTag = document.createElement('tag');
                positionTag.setAttribute('name', 'position');
                positionTag.setAttribute('value', points.x1+','+points.y1+';'+points.x2+','+points.y2+';'+points.x3+','+points.y3+';'+points.x4+','+points.y4);
                overlayTag.appendChild(positionTag);

                var shapeTag = document.createElement('tag');
                shapeTag.setAttribute('name', 'shape');
                shapeTag.setAttribute('value', 'dots_custom');
                overlayTag.appendChild(shapeTag);


                BQ.Preferences.set(me.miniViewer.resource.resource_uniq, 'Viewer/Overlay', overlayTag.outerHTML,
                function() {
                    BQ.ui.notification('Successfully updated overlay');
                },
                function() {
                    BQ.ui.notification('Failed to updated overlay');
                });
                //BQ.Preferences.updateResource(me.miniViewer.resource.resource_uniq, preferenceTag.outerHTML, function() {BQ.ui.notification('Successfully updated overlay');});
            },
        }, { //toggles disable, enable of the mask
            scale: 'large',
            margin: '0 8 0 8',
            xtype: 'button',
            text: me.viewer.plugins_by_name.overlay.overlayPref.enable?'Disable':'Enable',
            handler: function (el) {
                var enableTag = document.createElement('tag');
                enableTag.setAttribute('name', 'enable');
                el.setText(me.viewer.plugins_by_name.overlay.overlayPref.enable ? 'Enable':'Disable');
                enableTag.setAttribute('value', me.viewer.plugins_by_name.overlay.overlayPref.enable ? 'false':'true');

                BQ.Preferences.set(me.miniViewer.resource.resource_uniq, 'Viewer/Overlay/enable', enableTag.outerHTML, function() {
                    if (me.viewer.plugins_by_name.overlay.overlayPref.enable) me.onChanged(me.miniViewer);
                    BQ.ui.notification((me.viewer.plugins_by_name.overlay.overlayPref.enable?'Enabled':'Disabled')+' Overlay');
                });
            },
        }, {
            scale: 'large',
            margin: '0 8 0 8',
            xtype: 'button',
            text: 'User Default',
            handler: function () {
                BQ.Preferences.set(me.miniViewer.resource.resource_uniq, 'Viewer/Overlay', undefined,
                    function() {
                        me.removeAllGobjects(me.miniViewer);
                        BQ.ui.notification('Set overlay to user preference');
                    },
                    function() {
                        BQ.ui.notification('Already set to user default');
                    }
                );
            },
        }];

        Ext.apply(me, {
            items: items,
            fbar: fbar,
        });
        this.callParent([config]);
        this.miniViewer = this.queryById('miniViewer');

    },

    onChanged: function(el, gob) {
        var me = this;
        var gobs = el.getGobjects();
        var overlay = el.viewer.plugins_by_name.overlay;
        if (gobs.length>4) {
            var editor   = el.viewer.plugins_by_name.edit;
            var renderer = el.viewer.plugins_by_name.renderer;
            editor.remove_gobject(gobs[0]);
            renderer.updateVisible();
        }
        if (gobs.length==4) {
            var points = me.mapPoints(gobs);
            overlay.overlayPref.position = points.x1+','+points.y1+';'+points.x2+','+points.y2+';'+points.x3+','+points.y3+';'+points.x4+','+points.y4; //update preference for this view only
            overlay.populate_overlay();
        } else {
            overlay.overlayPref.position = '';
            overlay.populate_overlay();
        }
    },

    removeAllGobjects: function(el) {
        var me = this;
        var gobs = el.getGobjects();
        var overlay = el.viewer.plugins_by_name.overlay;
        var editor   = el.viewer.plugins_by_name.edit;
        var renderer = el.viewer.plugins_by_name.renderer;
        while (gobs.length>0) {
            editor.remove_gobject(gobs[0]);
        }
        renderer.updateVisible();
    },

    onAfterPhys: function(el) {
        var me = this;
        var gobs = el.getGobjects();
        var overlay = me.viewer.plugins_by_name.overlay; //pull the preference from the main viewer
        var editor   = el.viewer.plugins_by_name.edit;
        if (overlay.overlayPref.position) {
            var pattern = /([A-Za-z0-9_.]+),([A-Za-z0-9_.]+);([A-Za-z0-9_.]+),([A-Za-z0-9_.]+);([A-Za-z0-9_.]+),([A-Za-z0-9_.]+);([A-Za-z0-9_.]+),([A-Za-z0-9_.]+)/;
            var points = overlay.overlayPref.position.match(pattern);
            if (points && (points.length == 9)) {
                var g1 = new BQGObject('point');
                g1.vertices.push (new BQVertex (points[1], points[2], null, null, null, 0));
                el.setGobjects(g1);
                var g2 = new BQGObject('point');
                g2.vertices.push (new BQVertex (points[3], points[4], null, null, null, 0));
                el.setGobjects(g2);
                var g3 = new BQGObject('point');
                g3.vertices.push (new BQVertex (points[7], points[8], null, null, null, 0));
                el.setGobjects(g3);
                var g4 = new BQGObject('point');
                g4.vertices.push (new BQVertex (points[5], points[6], null, null, null, 0));
                el.setGobjects(g4);
            }
        }
    },

    mapPoints: function(gobsList) {
        var x1 = gobsList[0].vertices[0].x;
        var y1 = gobsList[0].vertices[0].y;
        var x2 = gobsList[1].vertices[0].x;
        var y2 = gobsList[1].vertices[0].y;
        var x4 = gobsList[2].vertices[0].x;
        var y4 = gobsList[2].vertices[0].y;
        var x3 = gobsList[3].vertices[0].x;
        var y3 = gobsList[3].vertices[0].y;

        return {
            x1:x1, y1:y1,
            x2:x2, y2:y2,
            x3:x3, y3:y3,
            x4:x4, y4:y4,
        };
    },

});