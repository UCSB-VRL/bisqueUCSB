//modification to imageview
/*
*	ImgOverlayEditor Viewer Plugin
*
*   Custom selector placed in the image meta to maniuplate
*   a dot template. Only instantiated if the user has set
*   the dot template in the view image layouts
*
*	@param: viewer -
*	@param: name -
*/
function ImgOverlayEditor(viewer, name) {

    this.base = ViewerPlugin;
    this.base(viewer, name);
    var p = viewer.parameters || {};
    var me = this;
    var operation_menu = this.viewer.toolbar.queryById('menu_viewer_operations')
    if (operation_menu) {
        var image = this.viewer.image;
        var resource = image? image.uri : ''
        operation_menu.menu.add({
                xtype  : 'menuitem',
                itemId : 'menu_viewer_operation_overlayEditor',
                text   : 'Overlay Editor',
                handler: function() {
                    if (!me.overlayEditorWin) {
                        var image = this.viewer.image;
                        var resource = image? image.uri : ''
                        me.overlayEditorWin = Ext.create('BQ.overlayEditor.Window',{
                            title: 'Overlay Editor',
                            height: '80%',
                            width: '80%',
                            modal: true,
                            closeAction:'hide',
                            viewer: me.viewer,
                            phys: me.viewer.imagephys,
                            image_resource:resource,
                        });
                    }
                    me.overlayEditorWin.show();
                },
        });
    } else {
        //print error message
    }
};

ImgOverlayEditor.prototype = new ViewerPlugin();

ImgOverlayEditor.prototype.create = function (parent) {
    this.parent = parent;
    return parent;
};

ImgOverlayEditor.prototype.newImage = function () {
    var me = this;
    if (me.overlayEditorWin) {
        this.phys_inited = false;
        var image = this.viewer.image;
        var resource = image? image.uri : ''
        me.overlayEditorWin.miniViewer.resource = resource;
    }
};

ImgOverlayEditor.prototype.updateImage = function () {

};

ImgOverlayEditor.prototype.getParams = function () {
    return this.params || {};
};


Ext.define('BQ.overlayEditor.Window', {
    extend: 'Ext.window.Window',
    image_resource: '',
    layout: 'vbox',
    initComponent: function(config) {
        var config = config || {};
        var me = this;

        this.miniViewer =  Ext.create('BQ.viewer.Image',{
            width:'100%',
            height: '75%',
            flex: 6,
            resource: me.image_resource,
            parameters: {
                onlyedit: true,
                nosave: true,
                editprimitives: 'point',
                semantic_types: false,
            },
            listeners: {
                'changed': function(el) {
                    var gobs = el.getGobjects();
                    if (gobs.length>4) {
                        var editor   = el.viewer.plugins_by_name.edit;
                        var renderer = el.viewer.plugins_by_name.renderer;

                        editor.remove_gobject(gobs[0]);
                        renderer.updateVisible();
                    }
                }
            },
        });
        var items = [{
            xtype: 'container',
            padding: '10px',
            html: [
                '<h3>Layout Editor</h3>',
                '<p>Set the position of the template size and orientation by selecting 4 points on the image.</p>',
            ],
            flex: 1,
        },
            this.miniViewer,
        ];


        var fbar = [{
            scale: 'large',
            xtype: 'button',
            margin: '0 8 0 8',
            text: 'Set',
            handler: function() {
                var gobs = me.miniViewer.getGobjects();
                if (gobs.length!=4) {
                    BQ.ui.notification('For points are required to set the overlay')
                    return
                }


                view = me.viewer.view();

                corners = [
                    {x:0,y:0},
                    {x:view.original_width,y:0},
                    {x:0, y:view.orginial_height},
                    {x:view.original_width, y:view.orginial_height}
                ];

                var points = []

                for (var c=0; c<4; c++) {
                    var lengths = [];
                    for (var g = 0;g<gobs.length;g++) {
                        lengths.push(Math.sqrt(Math.pow(gobs[g].vertices[0].x-corners[c].x,2) + Math.pow(gobs[g].vertices[0].y-corners[c].y,2)))
                    }
                    var i = lengths.indexOf(Math.max.apply(Math, lengths));
                    points.push(gobs.splice(i, 1)[0]);
                }

                var x1 = '';
                var y1 = '';
                var x2 = '';
                var y2 = '';
                var x3 = '';
                var y3 = '';
                var x4 = '';
                var y4 = '';


                var preferenceTag = document.createElement('preference');

                var viewerTag = document.createElement('tag');
                viewerTag.setAttribute('name', 'Viewer');
                preferenceTag.appendChild(viewerTag);

                var layoutTag = document.createElement('tag');
                layoutTag.setAttribute('name', 'Overlay');
                viewerTag.appendChild(layoutTag);

                var enableTag = document.createElement('tag');
                enableTag.setAttribute('name', 'enable');
                enableTag.setAttribute('value', 'true');
                layoutTag.appendChild(enableTag);

                var positionTag = document.createElement('tag');
                positionTag.setAttribute('name', 'position');
                positionTag.setAttribute('value', points[0].vertices[0].x+','+points[0].vertices[0].y+';'+points[1].vertices[0].x+','+points[1].vertices[0].y+';'+points[2].vertices[0].x+','+points[2].vertices[0].y+';'+points[3].vertices[0].x+','+points[3].vertices[0].y);
                layoutTag.appendChild(positionTag);

                BQ.Preferences.updateResource(preferenceTag.outerHTML)
            },
        }, { //toggles disable enable of the mask
            scale: 'large',
            margin: '0 8 0 8',
            xtype: 'button',
            text: 'Disable',
        }]

        Ext.apply(me, {
            items: items,
            fbar: fbar,
        });
        this.callParent([config]);

    },


})
