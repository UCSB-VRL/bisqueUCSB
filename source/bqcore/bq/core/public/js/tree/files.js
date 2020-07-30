/*******************************************************************************

  BQ.tree.files.Panel  - blob service directory tree store panel

  This is used to navigate in the directory view and create/delete directories
  and files

  Author: Dima Fedorov
  Version: 1

  History:
    2014-09-04 13:57:30 - first creation

*******************************************************************************/

Ext.namespace('BQ.tree.files');

//--------------------------------------------------------------------------------------
// misc
//--------------------------------------------------------------------------------------

BQ.tree.files.computePath = function(node) {
    var path = [];
    while (node) {
        if (node.data) {
            path.push(node.data.name || node.data.id);
        }
        node = node.parentNode;
    }
    path.reverse();
    return path;
};

BQ.tree.files.path2url = function(path) {
    var p=[],
        i=0;
    for (i=0; i<path.length; ++i) {
        p.push(encodeURIComponent(path[i]));
    }
    return p.join('/');
};

//--------------------------------------------------------------------------------------
// BQ.data.reader.Files
// XML reader that reads path records from the data store
//--------------------------------------------------------------------------------------

Ext.define('BQ.data.reader.Files', {
    extend: 'Ext.data.reader.Xml',
    alias : 'reader.bq-files',

    root : 'resource',
    record : '>store,>dir,>link',

    getRoot: function(data) {
        // in blob service doc the root of the document is our root
        if (Ext.DomQuery.isXml(data) && !data.parentElement) {
            return data;
        } else if (data.tagName === 'link') {
            return data;
        }
    }

    /*extractData: function(root) {
        var recordName = this.record;

        //<debug>
        if (!recordName) {
            Ext.Error.raise('Record is a required parameter');
        }
        //</debug>

        if (recordName != root.nodeName) {
            root = Ext.DomQuery.select(recordName, root);
        } else {
            root = [root];
        }
        //return this.callParent([root]);
        return this.callSuper([root]);
    },*/

});

//--------------------------------------------------------------------------------------
// BQ.data.writer.Files
// XML writer that writes path records to the data store
//--------------------------------------------------------------------------------------

Ext.define('BQ.data.writer.Files', {
    extend: 'Ext.data.writer.Xml',
    alias: 'writer.bq-files',

    writeRecords: function(request, data) {
        var me = request.proxy.ownerPanel,
            url = me.getSelectedAsUrl(),
            record = request.records[0];
        // selected url does not contain leaf link nodes, add if needed
        //if (record.data && record.data.type === 'link') {
        if (record.data && record.data.type !== 'dir' && record.data.name) {
            url += '/' + encodeURIComponent(record.data.name);
        }
        request.url = url;
        request.xmlData = '';
        return request;
    }
});

//--------------------------------------------------------------------------------------
// BQ.data.proxy.Files
// Proxy to perform true REST fetches from blob service
//--------------------------------------------------------------------------------------

Ext.define('BQ.data.proxy.Files', {
    extend: 'Ext.data.proxy.Rest',
    alias : 'proxy.bq-files',

    batchActions: false,
    noCache : false,
    appendId: false,
    limitParam : 'limit',
    pageParam: undefined,
    startParam: 'offset',

    sortParam : undefined,
    filterParam : undefined,

    actionMethods: {
        create : 'POST', // 'PUT'
        read   : 'GET',
        update : 'POST',
        destroy: 'DELETE'
    },

    buildUrl: function(request) {
        // extjs attempts adding ?node=NAME to all requests
        if (request.params && request.params.node) {
            delete request.params.node;
        }
        // extjs attempts adding sorters as well
        if (request.params && request.params.sort) {
            delete request.params.sort;
        }

        // create a URL path traversing through the parents
        var node = request.operation.node,
            path = BQ.tree.files.computePath(node);
        request.url = this.getUrl(request) + BQ.tree.files.path2url(path);
        return request.url;
    }

});

//--------------------------------------------------------------------------------------
// BQ.tree.files.Panel
// events:
//    selected -
//--------------------------------------------------------------------------------------

BQ.tree.files.icons = {
   store: 'icon-store',
   dir: 'icon-folder',
   link: 'icon-file'
};

BQ.tree.files.order = {
   store: 0,
   dir: 1,
   link: 2
};

BQ.tree.files.getType = function(o) {
    var t = o.get('type');
    if (t in BQ.tree.files.order) {
        return BQ.tree.files.order[t];
    }
    return 3;
};

Ext.define('BQ.tree.files.Panel', {
    extend: 'Ext.tree.Panel',
    alias: 'widget.bq-tree-files-panel',
    requires: ['Ext.button.Button', 'Ext.tree.*', 'Ext.data.*'],

    path: undefined, // initial path

    cls: 'files',
    //pageSize: 100,          // number of records to fetch on every request
    //trailingBufferZone: 20, // Keep records buffered in memory behind scroll
    //leadingBufferZone: 20,  // Keep records buffered in memory ahead of scroll

    animate: false,
    animCollapse: false,
    deferRowRender: true,
    displayField: 'name',
    folderSort: false,
    singleExpand : false,
    viewConfig : {
        stripeRows : true,
        enableTextSelection: false,
    },
    multiSelect: false,
    lines : false,
    columnLines : true,
    rowLines : true,
    useArrows : true,
    frame : true,
    hideHeaders : true,
    border : false,
    rootVisible : false,
    disableSelection: false,
    allowDeselect: false,
    sortableColumns: false,
    defaults: {
        border : false,
    },

    plugins: [{
        ptype: 'bufferedrenderer'
    }],

    initComponent : function() {
        this.url = this.url || '/blob_service/';
        this.url_selected = this.url;

        this.dockedItems = [{
            xtype: 'toolbar',
            itemId: 'tool_bar',
            dock: 'top',
            defaults: {
                scale: 'medium',
            },
            items: [{
                itemId: 'btnCreateFolder',
                text: 'Create',
                //scale: 'medium',
                iconCls: 'icon-add-folder',
                handler: this.createFolder,
                scope: this,
                tooltip: 'Create a new folder',
            }, {
                itemId: 'btnDeleteSelected',
                text: 'Delete',
                //scale: 'medium',
                iconCls: 'icon-trash',
                handler: this.deleteSelected,
                scope: this,
                tooltip: 'Delete selected',
            }],
        }, {
            xtype:'bq-picker-path',
            itemId: 'path_bar',
            dock: 'top',
            height: 35,
            //prefix: 'Upload to: ',
            path: '/',
            listeners: {
                scope: this,
                //browse: this.browsePath,
                changed: function(el, path) {
                    this.setPath(path);
                },
            },
        }];

        this.store = Ext.create('Ext.data.TreeStore', {
            defaultRootId: 'store',
            //autoLoad: false,
            autoSync: true,
            //lazyFill: true,
            remoteSort: false,
            folderSort: true,
            sortOnLoad: true,

            proxy : {
                type : 'bq-files',
                url : this.url,
                ownerPanel: this,
                //noCache : false,
                //appendId: false,
                //limitParam : 'limit',
                //pageParam: undefined,
                //startParam: 'offset',

                reader : {
                    type : 'bq-files',
                    root : 'resource',
                },
                writer : {
                    type : 'bq-files',
                },
                listeners: {
                    scope: this,
                    exception: this.onError
                }
            },
            fields : [{
                name : 'name',
                mapping : '@name',
            }, {
                name : 'value',
                mapping : '@value',
            }, {
                name : 'type',
                convert : function(value, record) {
                    return record.raw.tagName;
                },
            }, {
                name : 'iconCls',
                type : 'string',
                convert : function(value, record) {
                    if (record.data && record.data.type && record.data.type in BQ.tree.files.icons)
                        return BQ.tree.files.icons[record.data.type];
                }
            }],

            sorters: [{
                sorterFn: function(o1, o2) {
                    var s1 = BQ.tree.files.getType(o1);
                    var s2 = BQ.tree.files.getType(o2);
                    if (s1 === s2) {
                        s1 = o1.get('name').toLowerCase();
                        s2 = o2.get('name').toLowerCase();
                    }
                    if (s1 === s2) return 0;
                    return s1 < s2 ? -1 : 1;
                },
            }],

            listeners: {
                scope: this,
                load: function () {
                    if (this.initialized) return;
                    this.initialized = true;
                    if (this.path)
                        this.setPath(this.path);
                },
            },
        });

        this.on('select', this.onSelect, this);
        this.on('afteritemexpand', this.onAfterItemExpand, this);
        this.on('afteritemcollapse', this.onAfterItemExpand, this);

        this.callParent();
    },

    /*afterRender : function() {
        this.store.load();
        this.store.autoLoad = true;
        this.callParent();
    },*/

    setActive : function() {
        var url = this.url_selected === this.url ? this.url + 'store' : this.url_selected;
        this.fireEvent('selected', url, this);
    },

    getUrl : function(node) {
        if (!node) {
            return this.url_selected;
        }
        var path = BQ.tree.files.computePath(node);
        var url = this.url + BQ.tree.files.path2url(path);
        //var url = path.join('/');
        return url;
    },

    onSelect : function(me, record, index, eOpts) {
        if (this.no_selects===true) return;
        var node = record;
        var path = [];
        while (node) {
            if (node.data && node.data.type !== 'link')
                path.push(node.data.name || node.data.id);
            node = node.parentNode;
        }
        path.reverse();
        var url = this.url + BQ.tree.files.path2url(path);
        path.shift();
        this.queryById('path_bar').setPath( '/'+path.join('/') );

        if (this.url_selected !== url) {
            this.url_selected = url;
            this.fireEvent('selected', url, this);
        }
        record.expand();
    },

    getSelected : function() {
        var sel = this.getSelectionModel().getSelection();
        if (sel.length<1) return;
        return sel[0];
    },

    getSelectedAsUrl : function() {
        return this.url_selected;
    },

    getSelectedAsResource : function() {
        var sel = this.getSelectionModel().getSelection();
        if (sel.length<1) return;
        var node = sel[0];
        if (!node) return;
        var r = BQFactory.parseBQDocument(node.raw);
        return r;
    },

    onAfterItemExpand : function( node, index, item, eOpts ) {
        this.getSelectionModel().select(node);
    },

    onPath: function(node, p) {
        if (!node) return;
        p.shift();

        if (p.length<=0) {
            this.getSelectionModel().select(node);
            return;
        }

        var name = p[0];
        node = node.findChildBy(
            function(n) {
                if (n.data.name === name) return true;
            },
            this,
            true
        );
        if (node)
            node.expand(false, function(nodes) {
                if (!nodes || nodes.length<1) return;
                this.onPath(nodes[0].parentNode, p);
            }, this);
    },

    setPath: function(path) {
        path = path.replace('/blob_service/store', '');
        var p = path === '/' ? [''] : path.split('/');
        this.onPath(this.getRootNode(), p);
    },

    onError: function(proxy, response, operation, eOpts) {
        BQ.ui.error('Error: '+response.statusText );
    },

    reset: function () {
        this.no_selects = true;
        this.queryById('path_bar').setPath( '/' );
        this.url_selected = this.url;

        var root = this.getRootNode();
        this.store.suspendAutoSync();
        root.removeAll(false);
        this.store.resumeAutoSync();
        this.store.load();
        this.no_selects = undefined;
        this.getSelectionModel().select(root);
    },

    createFolder: function() {
        //Ext.Msg.prompt('Create folder', 'Please enter new folder\' name:', function(btn, text) {
        BQ.MessageBox.prompt('Create folder', 'Please enter new folder\' name:', function(btn, text) {
            if (btn !== 'ok') return;
            var me = this,
                selection = me.getSelectionModel().getSelection(),
                parent=null;
            if (selection.length>0) {
                parent = selection[0];
            } else {
                parent = me.getRootNode();
            }

            var node = parent.appendChild({
                name : text,
                //value : '',
                type : 'dir',
            });
            me.getSelectionModel().select(node);
        }, this, undefined, undefined, function(v) {
            //| ; , ! @ # $ ( ) / \ " ' ` ~ { } [ ] = + & ^ <space> <tab>
            var regex = /[\n\f\r\t\v\0\*\?\|;,!@#$\(\)\\\/\"\'\`\~\{\}\[\]=+&\^]|^\s+/gi;
            if (regex.test(v))
                return 'Invalid characters are present';
            else
                return true;
        });
    },

    deleteSelected: function() {
        var me = this;
        Ext.Msg.confirm('Deletion', 'Are you sure to delete?', function(btn) {
            if (btn !== 'yes') {
                return;
            }
            var selection = me.getSelectionModel().getSelection();
            if (selection) {
                var node = selection[0];
                var parent = node.parentNode;
                node.remove();
                me.getSelectionModel().select(parent);
            }
        });
    },

});

