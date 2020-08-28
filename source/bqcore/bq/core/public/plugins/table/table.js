/*******************************************************************************
Author: Dmitry Fedorov
Copyright: 2015 (C) Center for Bio-Image Informatics, University of California at Santa Barbara

Exportable classes:
    BQ.table.Panel - renders the table resource
    BQ.table.View - renders a given sub-table of a table resource

Browser components:
    Bisque.Resource.Table.Page
    ...
    Bisque.Resource.Table.Grid

*******************************************************************************/

Ext.namespace('BQ.data');
Ext.namespace('BQ.table');

BQ.data.pageSize = 500;
BQ.table.icons = {
    //group:    'icon-group', use default icons
    table:    'icon-table',
    matrix:   'icon-matrix',
    //vector:   'icon-vector',
    //image:    'icon-image', // not sure how we will identify this
};

Ext.require([
    'Ext.grid.*',
    'Ext.data.*',
    'Ext.util.*',
    'Ext.grid.plugin.BufferedRenderer'
]);

//--------------------------------------------------------------------------------------
// Table json proxy
//--------------------------------------------------------------------------------------

Ext.define('BQ.data.proxy.Table', {
    extend: 'Ext.data.proxy.Ajax',
    alternateClassName: 'BQ.data.TableProxy',
    alias : 'proxy.bq-table',

    noCache : false,
    batchActions: false,

    pageParam: undefined,
    startParam: undefined,
    limitParam: undefined,

    actionMethods: {
        create : 'POST',
        read   : 'GET',
        update : 'PUT',
        destroy: 'DELETE'
    },

    buildUrl: function(request) {
        var me        = this,
            operation = request.operation,
            records   = operation.records || [],
            record    = records[0],
            format    = me.format,
            url       = me.getUrl(request),
            id        = record ? record.getId() : operation.id;

        if (operation.limit>1) {
            url += '/'+operation.start+';'+(operation.start+operation.limit-1);
        } else if (operation.limit==1) {
            url += '/'+operation.start;
        }
        url += ',;'; // request all the columns
        url += '/format:extjs';
        request.url = url;
        return me.callParent(arguments);
    },

});

Ext.define('BQ.data.proxy.TableTree', {
    extend: 'Ext.data.proxy.Ajax',
    alternateClassName: 'BQ.data.TableTreeProxy',
    alias : 'proxy.bq-table-tree',

    noCache : false,
    batchActions: false,

    pageParam: undefined,
    startParam: undefined,
    limitParam: undefined,

    actionMethods: {
        create : 'POST',
        read   : 'GET',
        update : 'PUT',
        destroy: 'DELETE'
    },

    buildUrl: function(request) {
        var me        = this,
            operation = request.operation,
            records   = operation.records || [],
            record    = records[0],
            format    = me.format,
            url       = me.getUrl(request),
            id        = record ? record.getId() : operation.id;

        if (request.params && request.params.node)
            delete request.params.node;

        /*if (operation.limit>1) {
            url += '/'+operation.start+';'+(operation.start+operation.limit-1);
        } else if (operation.limit==1) {
            url += '/'+operation.start;
        }*/
        url += '/info/format:extjs';
        request.url = url;
        return me.callParent(arguments);
    },

});

//--------------------------------------------------------------------------------------
// Table json reader
//--------------------------------------------------------------------------------------

Ext.define('BQ.data.reader.Table', {
    extend: 'Ext.data.reader.Json',
    alternateClassName: 'BQ.data.TableReader',
    alias : 'reader.bq-table',

    pageSize: BQ.data.pageSize,

    readRecords: function(data) {
        var me = this;
        if (data.data && data.data.length >= me.pageSize) {
            data.total = data.data.length + me.pageSize;
            data.total += data.offset || 0;
        } else if (data.data) {
            data.total = data.data.length;
            data.total += data.offset || 0;
        }

        // in case of a single column data, need to wrap it into a vector
        if (data.headers.length===1 && !Array.isArray(data.data[0])) {
            for (var i=0; i<data.data.length; ++i) {
                data.data[i] = [data.data[i]];
            }
        }

        return me.callParent([data]);
    },
});

Ext.define('BQ.data.reader.TableTree', {
    extend: 'Ext.data.reader.Json',
    alternateClassName: 'BQ.data.TableTreeReader',
    alias : 'reader.bq-table-tree',

    root: 'group',

    readRecords: function(data) {
        var me = this,
            e = null;
        if (data.group)
        for (var i=0; (e=data.group[i]); ++i) {
            if (e.type && e.type === 'group') {
                e.leaf = false;
            } else {
                e.leaf = true;
            }
        }
        return me.callParent([data]);
    },
});

//--------------------------------------------------------------------------------------
// Table grid view - renders actual grid content for one given table
// required parameters:
//     resource - the table resource
//     path - sub table path
//--------------------------------------------------------------------------------------

BQ.table.encodeURIpath = function(p) {
    p = encodeURIComponent(p).replace(/%2F/g, '/');
    if (p[0] == '/') return p; else return '/'+p;
}

Ext.define('BQ.table.View', {
    extend: 'Ext.container.Container',
    alias: 'widget.bq_table_view',
    componentCls: 'bq_table_view',
    //layout: 'fit',
    layout: {
        type: 'vbox',
        align: 'stretch',
    },

    filter_text: 'Filter table contents',
    url: null,
    query_string: null,

    initComponent : function() {
        // temporary columns and store needed to init empty gridpanel without errors
        this.store = Ext.create('Ext.data.Store', {
            fields:['name'],
            data:{ 'items': [{ 'name': '' }, ]},
            proxy: {
                type: 'memory',
                reader: {
                    type: 'json',
                    root: 'items'
                }
            }
        });


        // init image viewer list
        this.image_viewers = [{
            class: 'Ext.grid.Panel',
            xtype: 'gridpanel',

            text: 'Table',
            icon_class: 'icon_table',
            item_id: 'main_view_table',
            tooltip: 'View current table',

            need_destruction: false,
            container: null,
            creator: null,

            min_p: 1,
            min_z: 1,
            min_t: 1,
            min_x: 0,
            min_y: 0,
            max_x: null,
            max_y: null,
        }, {
            xtype: 'tbspacer',
            width: 15,
        }/*, {
            class: 'BQ.renderers.Plotly',
            xtype: 'rendererplotly',

            text: 'Plot',
            icon_class: 'icon_plot',
            item_id: 'main_view_plot',
            tooltip: 'View current table as a Plot',

            need_destruction: false,
            container: null,
            creator: null,

            min_p: 1,
            min_z: 1,
            min_t: 1,
            min_x: 0,
            min_y: 0,
            max_x: 1,
            max_y: 1,
        }, {
            xtype: 'tbspacer',
            width: 15,
        }*/];
        var viewer_menu_items = [],
            v=null;
        for (var i=0; (v=BQ.image_viewers.available[i]); ++i) {
            v.container = undefined;
            this.image_viewers.push(Ext.clone(v));
        }

        for (var i=0; (v=this.image_viewers[i]); ++i) {
            if (v && v.text) {
                viewer_menu_items.push({
                    xtype  : 'button',
                    itemId: 'menu_view_'+v.text.toLowerCase(),
                    pressed: i==0 ? true : false,
                    mode: v.text,
                    iconCls: v.icon_class,
                    tooltip: v.tooltip,
                    toggleGroup: 'viewers',
                    frame: false,
                    scope: this,
                    toggleHandler: this.onViewerMenu,
                    focusCls: '',
                });
            } else {
                viewer_menu_items.push(v);
            }
        }

        // and query string
        viewer_menu_items.push({
            xtype: 'tbspacer',
            width: 30,
        });
        viewer_menu_items.push({
            xtype  : 'textfield',
            itemId: 'menu_filter',
            cls: 'search_field',
            flex: 1, // 2
            name: 'search',
            value: this.filter_text,
            minWidth: 100,
            tooltip: 'Find cells based on their content, ex: DAPI > 12.5',
            enableKeyEvents: true,
            listeners: {
                scope: this,
                focus: function(c) {
                    if (c.value === this.filter_text) {
                        c.setValue('');
                    }
                    var tip = Ext.create('Ext.tip.ToolTip', {
                        target: c.el,
                        anchor: 'top',
                        minWidth: 650,
                        width: 650,
                        maxHeight: 550,
                        autoHide: true,
                        dismissDelay: 20000,
                        shadow: false,
                        autoScroll: true,
                        loader: { url: '/core/plugins/table/help.html', renderer: 'html', autoLoad: true },
                    });
                    tip.show();
                },
                // blur: function(c) {
                // },
                specialkey: function(f, e) {
                    if (e.getKey()==e.ENTER && f.value!='' && f.value != this.filter_text) {
                        this.do_filter(f.value);
                    }
                },
            }
        });
        viewer_menu_items.push({
            xtype: 'tbspacer',
            width: 5,
        });

        // create view components: grid and tagger
        this.items = [{
            xtype: 'toolbar',
            itemId  : 'toolbar',
            height: 40,
            border: 0,
            defaults: {
                scale: 'medium',
                scope: this,
            },
            items: viewer_menu_items,
        }, {
            xtype: 'container',
            itemId  : 'main_container',
            layout: 'fit',
            border: 0,
            flex: 1,
            items: [{
                xtype: 'gridpanel',
                itemId  : 'table',
                autoScroll: true,
                border: 0,
                //flex: 1,
                viewConfig: {
                    stripeRows: true,
                    forceFit: true,
                },
                plugins: 'bufferedrenderer',
                store: this.store,
                columns: [
                    { text: '',  dataIndex: 'name' },
                ],
            }],
        },

        ];


        this.callParent();
        this.toolbar = this.queryById('toolbar');
        this.gridpanel = this.queryById('table');

        for (var i=0; (v=this.image_viewers[i]); ++i) {
            if (v.text === 'Table') {
                v.container = this.gridpanel;
            } else if (v.text === '2D') {
                v.creator = this.show2D;
            } else if (v.text === '3D') {
                v.creator = this.show3D;
            } else if (v.text === 'Movie') {
                v.creator = this.showMovie;
            }
        }

        this.image = new BQImage();
        this.image.initFromObject(this.resource);
        this.image.setPath(this.path);

        var phys = new BQImagePhys (this.image);
        phys.load (callback (this, this.onPhys), callback (this, this.onPhysError) );
    },

    afterRender : function() {
        this.callParent();
        if (this.info && !this.query_string) {
            this.url = this.constructUrl();
            this.onTableInfo();
            return;
        }

        this.update();
    },

    onPhys: function(phys) {
        this.phys = phys;
        var me = this;
        setTimeout(function(){
            me.doCheckLimits();
        }, 50);
        if (this.phys.x>0 && this.phys.y>0) {
            this.fireEvent('new_meta_image', this.image.src+'?meta');
        }
    },

    onPhysError: function() {
        this.phys = {
            x: 0,
            y: 0,
            t: 1,
            z: 1,
        };
        var me = this;
        setTimeout(function(){
            me.doCheckLimits();
        }, 50);
    },

    constructUrl: function() {
        var url = '/table/' + this.resource.resource_uniq;
        url += (this.path ? BQ.table.encodeURIpath(this.path) : '');
        if (this.query_string) {
            url += '/' + this.query_string;
        }
        return url;
    },

    update: function() {
        var url = this.constructUrl();
        if (this.url === url) return;
        this.url = url;

        // load table info to configure columns and the store
        this.setLoading('Loading table...');
        Ext.Ajax.request({
            url: this.url + '/info/format:extjs',
            callback: function(opts, succsess, response) {
                this.setLoading(false);
                if (response.status>=400 || !succsess)
                    BQ.ui.error(response.responseText);
                else
                    this.onTableInfo(response.responseText);
            },
            disableCaching: false,
            scope: this,
            // listeners: {
            //     scope: this,
            //     beforerequest   : function() { this.setLoading('Loading table...'); },
            //     requestcomplete : function() { this.setLoading(false); },
            //     requestexception: function() { this.setLoading(false); },
            // },
        });
    },

    onTableInfo: function(txt) {
        //this.setLoading(false);
        var json = this.info,
            h = null;
        if (!this.info && txt) {
            json = Ext.JSON.decode(txt);
        }
        this.fields = [];
        this.columns = [];
        for (var i=0; i<json.headers.length; ++i) {
            var h = json.headers[i],
                t = json.types[i],
                tt = 'string';

            if (t.indexOf('int')>=0)
                tt = 'int';
            else if (t.indexOf('float')>=0)
                tt = 'float';

            this.fields.push({
                name: i, // need to use numbers for reading from json array
                type: tt,
                useNull: true,
            });

            this.columns.push({
                text: h,
                flex: 1,
                dataIndex: i, // need to use numbers for reading from json array
                sortable: false, //true,
                autoSizeColumn : true,
                renderer: function(value) {
                    return value;
                },
            });
        }

        this.store = Ext.create('Ext.data.Store', {
            autoLoad: true,
            autoSync: true,
            fields: this.fields,

            buffered: true,
            leadingBufferZone: 100, // 300
            pageSize: BQ.data.pageSize,

            proxy: {
                //type: 'rest',
                type: 'bq-table',
                url: this.url,
                //noCache : false,
                //pageParam: undefined,
                //startParam: undefined,
                //limitParam: undefined,
                reader: {
                    type: 'bq-table', // 'json',
                    root: 'data'
                },
                //writer: {
                //    type: 'json'
                //}
            },
        });
        var table = this.queryById('table');
        table.reconfigure(this.store, this.columns);
    },

    do_filter: function(qstr) {
        this.query_string = qstr;
        // might need to do some parsing or encoding here
        this.update();
    },

    // -----------------------------------------------------------------------------------------
    // additional viewers
    // -----------------------------------------------------------------------------------------

    doCheckLimits : function() {
        var x = this.phys.x,
            y = this.phys.y,
            t = this.phys.t,
            z = this.phys.z,
            p = t*z,
            v=null,
            dis=false,
            cnt=null;

        for (var i=0; (v=this.image_viewers[i]); ++i) {
            if (!v.text) continue;
            dis=false;

            if (v.max_x && v.max_x<x) dis=true;
            if (v.max_y && v.max_y<y) dis=true;
            if (v.min_x>x) dis=true;
            if (v.min_y>y) dis=true;
            if (v.min_p>p) dis=true;
            if (v.min_t>t) dis=true;
            if (v.min_z>z) dis=true;

            cnt = this.toolbar.queryById('menu_view_'+v.text.toLowerCase());
            if (cnt)
                cnt.setDisabled(dis);
        }

        if (x>15000 && y>15000) {
            BQApp.getToolbar().queryById('download_as_ometiff').setDisabled( true );
            BQApp.getToolbar().queryById('download_as_omebigtiff').setDisabled( true );
        }

        if (!BQ.util.isWebGlAvailable()) {
            //if webgl isn't available then we'll disable the command.
            var button3D = this.toolbar.queryById('menu_view_3d');
            //button3D.setText('3D (WebGl not available)');
            button3D.setTooltip('WebGL is not available');
            button3D.setDisabled( true );
        }
    },

    onViewerMenu: function(m) {
        var me = this,
            selected = null,
            v = null;
        if (!m.pressed) return;

        for (var i=0; (v=this.image_viewers[i]); ++i) {
            if (m.mode === v.text) {
                selected = v;
                continue;
            }
            if (v.container) {
                //v.container.stop();
                v.container.setVisible(false);
                if (v.need_destruction) {
                    v.container.destroy();
                    v.container = null;
                }
            }
        }

        if (!selected) return;
        if (selected.container && selected.container.isVisible()) return;
        //m.toggle(true);

        if (!selected.container) {
            if (selected.creator) {
                selected.container = selected.creator.call(this);
            } else {
                var cnt = this.queryById('main_container');
                selected.container = cnt.add({
                    xtype: selected.xtype,
                    itemId: selected.item_id,
                    resource: this.image,
                    toolbar: this.toolbar,
                    phys: this.phys,
                    //preferences: this.viewerContainer.viewer.preferences,
                    listeners: {
                        // select_gobject : function(viewer, gob) {
                        //     var node = me.gobjectTagger.findNodeByGob(gob);
                        //     if (!node) {
                        //         console.log('No node found!');
                        //         return;
                        //     }
                        //     // dima: here expand to expose the selected node
                        //     var parent = node;
                        //     for (var i=0; i<node.getDepth()-1; i++)
                        //         parent = parent.parentNode;
                        //     me.gobjectTagger.tree.expandNode( parent, true );
                        //     me.gobjectTagger.tree.getSelectionModel().select(node);
                        // },
                        // select_plane : function(viewer, z, t) {
                        //     me.viewerContainer.select_plane(z, t);
                        //     me.show2D();
                        // },
                    },
                });
            }
        }
        selected.container.setVisible(true);
    },

    show2D : function() {
        var cnt = this.queryById('main_container');
        var viewer = cnt.add({
            xtype: 'imageviewer',
            itemId: 'main_view_2d',
            main : this,
            parameters : {
                simpleview: true,
                hide_create_gobs_menu: true,
                hide_file_name_osd: true,
                blockforsaves: false,
                main: this,
                render_plugins: ['color', 'corners', 'bbox'],
                //plugins_skip: {download: null, external: null, pixelcounter: null, },
            },
            resource: this.image,
            toolbar: this.toolbar,
            phys: this.phys,
            //preferences: this.viewerContainer.viewer.preferences,
        });

        // var items = [{
        //     xtype: 'menuseparator',
        //     itemId: 'download_movie_separator',
        // }, {
        //     itemId: 'download_movie_h264',
        //     text: 'Movie as MPEG4 H264',
        //     handler: function() { movie.export('h264'); },
        // }, {
        //     itemId: 'download_movie_qt',
        //     text: 'Movie as Apple QuickTime (MOV)',
        //     handler: function() { movie.export('quicktime'); },
        // }, {
        //     itemId: 'download_movie_webm',
        //     text: 'Google WebM',
        //     handler: function() { movie.export('webm'); },
        // }, {
        //     itemId: 'download_movie_avi',
        //     text: 'Microsoft AVI (MPEG4)',
        //     handler: function() { movie.export('avi'); },
        // }, {
        //     itemId: 'download_movie_wmv',
        //     text: 'Windows Media Video',
        //     handler: function() { movie.export('wmv'); },
        // }, {
        //     itemId: 'download_movie_flv',
        //     text: 'Adobe Flash Video',
        //     handler: function() { movie.export('flv'); },
        // }];
        // BQApp.add_to_toolbar_menu('button_download', items);
        return viewer;

    },

    showMovie : function() {
        var cnt = this.queryById('main_container');
        var movie = cnt.add({
            xtype: 'bq_movie_viewer',
            itemId: 'main_view_movie',
            resource: this.image,
            toolbar: this.toolbar,
            phys: this.phys,
            //preferences: this.viewerContainer.viewer.preferences,
        });

        var items = [{
            xtype: 'menuseparator',
            itemId: 'download_movie_separator',
        }, {
            itemId: 'download_movie_h264',
            text: 'Movie as MPEG4 H264',
            handler: function() { movie.export('h264'); },
        }, {
            itemId: 'download_movie_qt',
            text: 'Movie as Apple QuickTime (MOV)',
            handler: function() { movie.export('quicktime'); },
        }, {
            itemId: 'download_movie_webm',
            text: 'Google WebM',
            handler: function() { movie.export('webm'); },
        }, {
            itemId: 'download_movie_avi',
            text: 'Microsoft AVI (MPEG4)',
            handler: function() { movie.export('avi'); },
        }, {
            itemId: 'download_movie_wmv',
            text: 'Windows Media Video',
            handler: function() { movie.export('wmv'); },
        }, {
            itemId: 'download_movie_flv',
            text: 'Adobe Flash Video',
            handler: function() { movie.export('flv'); },
        }];
        BQApp.add_to_toolbar_menu('button_download', items);
        return movie;
    },

    show3D : function() {
        var me = this;
        if (!BQ.util.isWebGlAvailable()) {
            BQ.ui.error('WebGL is not available in your browser, sorry...');
            return;
        }

        var cnt = this.queryById('main_container');
        var view3d = cnt.add({
            xtype: 'bq_volume_panel',
            itemId: 'main_view_3d',
            resource: this.image,
            toolbar: this.toolbar,
            phys: this.phys,
            //preferences: this.viewerContainer.viewer.preferences,
            listeners: {
                // select_gobject : function(viewer, gob) {
                //     var node = me.gobjectTagger.findNodeByGob(gob);
                //     if (!node) {
                //         console.log('No node found!');
                //         return;
                //     }
                //     // dima: here expand to expose the selected node
                //     var parent = node;
                //     for (var i=0; i<node.getDepth()-1; i++)
                //         parent = parent.parentNode;
                //     me.gobjectTagger.tree.expandNode( parent, true );
                //     me.gobjectTagger.tree.getSelectionModel().select(node);
                // },

                glcontextlost: function(event){
                    var msgText = " ";
                    var link = " mailto:me@example.com"
                        + "?cc=myCCaddress@example.com"
                        + "&subject=" + escape("This is my subject")
                        + "&body=" + msgText + "";

                    BQ.ui.error("Hmmm... WebGL seems to hit a snag: <BR/> " +
                                "error: " + event.statusMessage +
                                "<BR/>Do you want to report this problem?" +
                                "<a href = " + link + "> send mail </a>");

                    var image3d = me.queryById('main_view_3d');
                    var toolMenu = image3d.toolMenu;
                    toolMenu.destroy();
                    image3d.destroy();
                    //this should destroy the 3D viewer
                    me.show2D();
                },

            }
        });
        return view3d;
    },

});

//--------------------------------------------------------------------------------------
// Table tree view - tree navigation in the hierarchical table resource
// required parameters:
//     resource - the table resource
//     info - dictionary with table service info object
// Events:
//     selected - returning selected leaf node
//--------------------------------------------------------------------------------------

Ext.define('BQ.table.Tree', {
    extend: 'Ext.tree.Panel',
    alias: 'widget.bq-table-tree',
    requires: ['Ext.button.Button', 'Ext.tree.*', 'Ext.data.*'],

    path: undefined, // initial path
    url: undefined, // base url

    componentCls: 'table_tree',
    //pageSize: 100,          // number of records to fetch on every request
    //trailingBufferZone: 20, // Keep records buffered in memory behind scroll
    //leadingBufferZone: 20,  // Keep records buffered in memory ahead of scroll

    //displayField: 'text',
    displayField: 'path',

    animate: false,
    animCollapse: false,
    deferRowRender: true,
    folderSort: false,
    singleExpand : false,
    multiSelect: false,
    lines : false,
    columnLines : false,
    rowLines : true,
    useArrows : true,
    frame : true,
    hideHeaders : true, // true
    border : false,
    rootVisible : false,
    disableSelection: false,
    allowDeselect: true,
    sortableColumns: false,
    draggable: false,
    enableColumnMove: false,
    defaults: {
        border : false,
    },

    viewConfig : {
        stripeRows : true,
        enableTextSelection: false,
        getRowClass: function(record, rowIndex, rowParams, store) {
            var icon = record.data.type;
            if (icon in BQ.table.icons)
                return BQ.table.icons[icon];
        },
        /*plugins: {
            ptype: 'treeviewdragdrop',
            allowParentInserts: true,
        },*/
    },

    /*plugins: [{ // dima: unfortunately this is giving issues in the tree
        ptype: 'bufferedrenderer'
    }],*/

    columns: [{
        xtype: 'treecolumn', //this is so we know which column will show the tree
        text: '',
        flex: 2,
        dataIndex: 'path',
        sortable: false, //true,
        renderer: function(value) {
            return value.split('/').slice(-1)[0];
        },
    }],

    initComponent : function () {
        this.url_selected = this.url;

        this.dockedItems = [{
            xtype:'bq-picker-path',
            itemId: 'path_bar',
            dock: 'top',
            height: 35,
            path: '/',
            listeners: {
                scope: this,
                //browse: this.browsePath,
                changed: function (el, path) {
                    this.setPath(path);
                },
            },
        }];

        var me = this;
        this.store = Ext.create('Ext.data.TreeStore', {
            defaultRootId: 'table_root',
            autoLoad: false,
            autoSync: false,
            appendId: false,
            //lazyFill: true,
            filterOnLoad: true,
            remoteFilter: false,
            remoteSort: false,

            proxy : {
                type : 'bq-table-tree',
                url : this.url,
                path: '',
                reader: {
                    type: 'bq-table-tree', //'bq-table-tree' 'json'
                    root: 'group',
                },
            },

            fields : [{
                name : 'type',
                convert : function (value, record) {
                    return (record.raw && record.raw.type) ? record.raw.type : '';
                },
            }, {
                name : 'path',
                convert : function (value, record) {
                    return (record.raw && record.raw.path) ? record.raw.path : '';
                },
            }, {
                name : 'meta',
                convert : function (value, record) {
                    return (record.raw && record.raw.meta) ? record.raw.meta : null;
                },
            }],

            listeners: {
                scope: this,
                load: function () {
                    //this.setLoading(false);
                    if (this.initialized) return;
                    this.initialized = true;
                    if (this.path)
                        this.setPath(this.path);
                },
            },
        });

        this.callParent();
        this.on('select', this.onSelect, this);
        this.on('beforeitemexpand', this.onBeforeItemExpand, this);
        this.on('afteritemexpand', this.onAfterItemExpand, this);
        this.on('afteritemcollapse', this.onAfterItemExpand, this);
    },

    /*afterRender : function () {
        this.callParent(arguments);
        if (!this.store.getProxy().loaded) {
        if (!this.initialized) {
            this.setLoading(true); //'Loading...');
            this.store.load();
        }
    },*/

    getSelected : function () {
        return this.url_selected;
    },

    getUrl : function () {
        return this.url;
    },

    setActive : function () {
        this.fireEvent('selected', this.url_selected, this);
    },

    setActiveNode : function (record) {
        if (this.no_selects===true) return; // || node.data.loaded===true) return;
        var path = record.raw.path,
            url  = this.url + path;

        this.queryById('path_bar').setPath(path);

        var proxy = this.store.getProxy();
        proxy.path = path;
        proxy.url = url;

        this.url_selected = path;
        this.fireEvent('selected', {
            node: record,
            url: url,
            path: path,
        }, this);
    },

    activateFirstChild : function () {
        var root = this.getRootNode(),
            node = root.childNodes[0];
        if (node) {
            this.setActiveNode(node);
            this.getSelectionModel().select(node);
        }
    },

    onSelect : function (me, record, index, eOpts) {
        if (record.isExpanded() || record.raw.type != 'group') {
            this.setActiveNode(record);
        } else {
            record.expand();
        }
    },

    onBeforeItemExpand: function (record, eOpts) {
        if (this.no_selects===true) return; // || record.data.loaded===true) return;
        this.setActiveNode(record);
    },

    onAfterItemExpand : function ( node, index, item, eOpts ) {
        this.selectTreeNode(node);
    },

    selectTreeNode : function ( node ) {
        this.getSelectionModel().select(node);
    },

    onPath: function (node, p) {
        if (!node) return;
        if (p.length<=0) {
            this.getSelectionModel().select(node);
            return;
        }

        var path = p.join('/');
        /*node = node.findChildBy(
            function (n) {
                if (n.data.path === path) return true;
            },
            this,
            true
        );*/

        // we are guaranteed that path is related to the currently selected node, it's faster to walk up the parent chain
        node = this.getSelectionModel().selected.first();
        while (node.data.path !== path && node.parentNode) {
            node = node.parentNode;
        }

        // select the node
        if (node && node.data.path === path)
            this.selectTreeNode(node);
    },

    setPath: function (path) {
        var p = path === '/' ? [''] : path.split('/');
        this.onPath(this.getRootNode(), p);
    },

    onError: function (r) {
        BQ.ui.error('Error: '+r.statusText );
    },

    reset: function () {
        this.no_selects = true;
        this.queryById('path_bar').setPath( '/' );
        this.active_query = {};
        this.url_selected = this.url;
        this.order = undefined;

        var proxy = this.store.getProxy();
        proxy.path = null;

        this.getSelectionModel().deselectAll();
        var root = this.getRootNode();
        this.store.suspendAutoSync();
        root.removeAll(true);
        this.store.resumeAutoSync();
        this.store.load();
        this.no_selects = undefined;
        this.getSelectionModel().select(root);
    },

});



//--------------------------------------------------------------------------------------
// Table viewer - renders all tables present in the table resource
// required parameters:
//     resource - the table resource
//--------------------------------------------------------------------------------------

Ext.define('BQ.table.Panel', {
    extend: 'Ext.container.Container',
    alias: 'widget.bq_table_panel',
    componentCls: 'bq_table_panel',
    //deferredRender: true,
    //activeTab : 0,
    //plain : true,
    layout : 'border',

    initComponent : function() {
        this.callParent();
    },

    afterRender : function() {
        this.callParent();
        this.setLoading('Loading table...');
        // load table info to configure columns and the store
        this.setLoading('Loading table...');
        Ext.Ajax.request({
            url: '/table/' + this.resource.resource_uniq + '/info/format:extjs',
            callback: function(opts, succsess, response) {
                this.setLoading(false);
                if (response.status>=400 || !succsess)
                    BQ.ui.error(response.responseText);
                else
                    this.onTableInfo(response.responseText);
            },
            disableCaching: false,
            scope: this,
            // listeners: {
            //     scope: this,
            //     beforerequest   : function() { this.setLoading('Loading table...'); },
            //     requestcomplete : function() { this.setLoading(false); },
            //     requestexception: function() { this.setLoading(false); },
            // },
        });
    },

    onTableInfo: function(txt) {
        this.setLoading(false);
        var json = Ext.JSON.decode(txt),
            me = this;
        this.tables = json.tables;
        this.groups = json.group;

        // select a first node if we have a multi-table spreadseet
        if (json && json.headers && json.headers.length>0) {
            this.needs_loading_first_child = true;
        }

        // select a first node in a hierarchical document with only one level of tables
        if (json && json.group && json.group.length>0 && !this.needs_loading_first_child) {
            this.needs_loading_first_child = true;
            var g = null,
                i = 0;
            for (i=0; (g=json.group[i]); ++i) {
                if (g.type !== 'table') {
                    this.needs_loading_first_child = undefined;
                    break;
                }
            }
        }

        if (this.groups && (this.groups.length>1 || (this.groups.length===1 && !json.headers))) {
            this.tabs = this.add({
                xtype: 'tabpanel',
                cls: 'tabs',
                itemId: 'tabs',
                flex: 2,
                region : 'center',

                deferredRender: true,
                activeTab : 0,
                border : false,
                bodyBorder : 0,
                plain : true,

                listeners: {
                    scope: this,
                    tabchange: this.onTabChanged,
                },

            });
            this.tree = this.add({
                xtype: 'bq-table-tree',
                region : 'west',
                split : true,
                collapsible : true,
                width : 300,
                border: 0,

                resource: this.resource,
                url: this.resource.uri.replace('/data_service/', '/table/'),
                info: json,
                listeners: {
                    scope: this,
                    selected: this.onTableTreeSelected,
                    load: function(o, node, records, successful) {
                        if (successful && me.needs_loading_first_child) {
                            me.needs_loading_first_child = undefined;
                            me.tree.activateFirstChild();
                        }
                    },
                },
            });
        /*} else if (this.tables && this.tables.length>1) {
            this.tabs = this.add({
                xtype: 'tabpanel',
                itemId: 'tabs',
                flex: 2,
                region : 'center',

                deferredRender: true,
                activeTab : 0,
                border : false,
                bodyBorder : 0,
                plain : true,
            });

            var p=undefined,
                i=undefined;
            for (i=0; (p=this.tables[i]); ++i) {
                this.tabs.add({
                    xtype: 'bq_table_view',

                    border: 0,
                    resource: this.resource,
                    path: p,
                    title: p,
                    listeners: {
                        scope: this,
                        new_meta: function(meta_url) {
                            this.fireEvent('new_meta', meta_url);
                        },
                    },
                });
            }*/
        } else {
            this.add({
                xtype: 'bq_table_view',
                border: 0,
                flex: 2,
                region : 'center',

                resource: this.resource,
                //path: p,
                info: json,
                listeners: {
                    scope: this,
                    new_meta: function(meta) {
                        this.fireEvent('new_meta', meta);
                    },
                    new_meta_image: function(meta) {
                        this.fireEvent('new_meta_image', meta);
                    },
                },
            });
        }
    },

    onTableTreeSelected: function(r) {
        this.fireEvent('new_meta', r.url + '/info/format:xml');
        if (r.node.data.type === 'group') {
            //this.fireEvent('new_meta', r.url + '/info/format:xml');
            return;
        };
        var path = r.path,
            id = encodeURIComponent(path).replace(/\%/g, ''),
            t = this.tabs.queryById(id);
        if (!t)
            t = this.tabs.add({
                xtype: 'bq_table_view',
                itemId: id,
                border: 0,
                closable: true,
                title: path,

                resource: this.resource,
                path: path,
                //info: r.node.raw,
                tree_node: r.node,
                listeners: {
                    scope: this,
                    new_meta: function(meta) {
                        this.fireEvent('new_meta', meta);
                    },
                    new_meta_image: function(meta) {
                        this.fireEvent('new_meta_image', meta);
                    },
                },
            });
        this.tabs.setActiveTab(t);
    },

    onTabChanged: function ( tabPanel, newCard, oldCard ) {
        if (!this.tree) return;
        this.tree.selectTreeNode( newCard.tree_node );
    },


});

//--------------------------------------------------------------------------------------
// Resource renderer
//--------------------------------------------------------------------------------------

Ext.define('Bisque.Resource.Table.Page', {
    extend : 'Bisque.Resource.Page',

    initComponent : function() {
        this.addCls('tableio');
        this.callParent();
    },

    downloadOriginal : function() {
        if (this.resource.src) {
            window.open(this.resource.src);
            return;
        }
        var exporter = Ext.create('BQ.Export.Panel');
        exporter.downloadResource(this.resource, 'none');
    },

    onResourceRender : function() {
        // create view components: grid and tagger

        this.add({
            xtype : 'container',
            itemId: 'main_container',
            cls: 'table_main',
            layout : 'border',
            items : [{
                xtype: 'tabpanel',
                cls: 'tabs',
                itemId: 'tabs',
                title : 'Metadata',
                deferredRender: true,
                region : 'east',
                activeTab : 0,
                border : false,
                bodyBorder : 0,
                collapsible : true,
                split : true,
                width : 400,
                plain : true,
                items : [{
                    xtype: 'bq-tagger',
                    itemId: 'tagger',
                    resource : this.resource,
                    title : 'Annotations',
                }, {
                    xtype: 'bq-tagger',
                    itemId: 'tagger_meta',
                    title : 'Metadata',
                    viewMode : 'ReadOnly',
                    disableAuthTest: true,
                    resource_fully_loaded: true,
                }, {
                    xtype: 'bq-tagger',
                    itemId: 'tagger_image',
                    title : 'Image',
                    viewMode : 'ReadOnly',
                    disableAuthTest: true,
                    resource_fully_loaded: true,
                }],
            }, {
                xtype: 'bq_table_panel',
                flex: 2,
                region : 'center',
                border: 0,
                resource: this.resource,
                //path: '',
                listeners: {
                    scope: this,
                    new_meta: this.onNewMeta,
                    new_meta_image: this.onNewMetaImage,
                },
            }],
        });
        //this.toolbar.doLayout();
        this.tabs = this.queryById('tabs');
        this.tagger_meta = this.queryById('tagger_meta');
        this.tagger_image = this.queryById('tagger_image');
    },

    onNewMeta: function(meta) {
        if (typeof meta === "string") {
            this.tagger_meta.setResource(meta);
        } else {
            // construct resource here

        }
    },

    onNewMetaImage: function(meta) {
        if (typeof meta === "string") {
            this.tagger_image.setResource(meta);
        } else {
            // construct resource here

        }
    },
});

Ext.define('Bisque.Resource.Table.Compact', {
    extend : 'Bisque.Resource.Compact',
    initComponent : function() {
        this.addCls(['resicon', 'table']);
        this.callParent();
    },

});

Ext.define('Bisque.Resource.Table.Card', {
    extend : 'Bisque.Resource.Card',
    initComponent : function() {
        this.addCls('table');
        this.callParent();
    },
});

Ext.define('Bisque.Resource.Table.Full', {
    extend : 'Bisque.Resource.Full',
    initComponent : function() {
        this.addCls('table');
        this.callParent();
    },
});

Ext.define('Bisque.Resource.Table.Grid', {
    extend : 'Bisque.Resource.Grid',

    initComponent : function() {
        this.addCls(['resicon', 'table']);
        this.callParent();
    },

    getFields : function(cb) {
        var fields = this.callParent();
        fields[0] = '<div class="resicon gridIcon table" />';
        return fields;
    },
});
