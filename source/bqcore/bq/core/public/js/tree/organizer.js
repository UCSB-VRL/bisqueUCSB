/*******************************************************************************

  BQ.tree.files.Panel  - blob service directory tree store panel

  This is used to navigate in the directory view and create/delete directories
  and files

  Author: Dima Fedorov
  Version: 1

  History:
    2014-09-04 13:57:30 - first creation

*******************************************************************************/

//--------------------------------------------------------------------------------------
// BQ.data.proxy.OrganizerProxy
// Proxy to perform queries for tag_values, tag_names, gob_names, gob_types
//--------------------------------------------------------------------------------------

/*

Ext.define('BQ.data.proxy.OrganizerProxy', {
    extend: 'Ext.data.proxy.Ajax',
    alternateClassName: 'BQ.data.OrganizerProxy',
    alias : 'proxy.bq-organizer',

    batchActions: false, // true
    noCache : true,
    appendId: false,
    //limitParam : 'limit',
    limitParam : undefined,
    pageParam: undefined,
    //startParam: 'offset',
    startParam: undefined,

    filterParam : undefined,
    sortParam : undefined,
    idParam : undefined,

    projections: {
        'tag_values': null,
        'gob_names': null,
        'tag_names': 'true',
        'gob_types': 'true'
    },
    projections_order : ['tag_values', 'gob_names', 'tag_names', 'gob_types'],
    query : '',

    doRequest: function (operation, callback, scope) {
        if (operation.action !== 'read') { return; }
        this.loaded = true;

        var url = this.url;
        if (this.query && this.query.length>0) {
            url += '?tag_query='+this.query+'&';
        } else {
            url += '?';
        }

        this.requests_fired = 0;
        this.responses = [];
        var name=null,
            i=0;
        for (i=0; (name=this.projections_order[i]); i++ ) {
            if (!this.projections[name]) continue;

            var r = this.buildRequest(operation);
            delete r.params[this.idParam];
            Ext.apply(r, {
                binary        : this.binary,
                headers       : this.headers,
                timeout       : this.timeout,
                scope         : this,
                callback      : this.createRequestCallback(r, operation, callback, scope),
                method        : this.getMethod(r),
                disableCaching: false, // explicitly set it to false, ServerProxy handles caching
                url           : url+name+'='+this.projections[name]+'&wpublic='+this.browserParams.wpublic,
                order         : i
            });

            this.requests_fired++;
            Ext.Ajax.request(r);
        }
        return r;
    },

    createRequestCallback: function (request, operation, callback, scope) {
        var me = this;
        return function (options, success, response) {
            this.requests_fired--;
            if (success) {
                this.responses[response.request.options.order] = response;
            }
            if (this.requests_fired>0) { return; }
            response = undefined;

            // need to assemble a combined response body
            var to=null;
            for (var i=0; i<this.responses.length; ++i) {
                var r = this.responses[i];
                if (!r) continue;
                if (!to) {
                    to = r.responseXML.firstChild;
                    response = r;
                    continue;
                }
                var from = r.responseXML.firstChild;
                while (from.firstChild) {
                    to.appendChild(from.firstChild);
                }
            }

            me.processResponse(success, operation, request, response, callback, scope);
        };
    },

    // dima: fix the absence of local filtering by replacing processResponse
    // with our version with filtering added, this may require updates for
    // extjs 5
    processResponse: function (success, operation, request, response, callback, scope) {
        if (Ext.getVersion().major>=5) {
            Ext.log({ level: "warn" }, 'Overwrite of processResponse is designed for ExtJS 4.2.1, needs replacement!');
        }

        var me = this,
            reader,
            result;

        if (success === true) {
            reader = me.getReader();

            // Apply defaults to incoming data only for read operations.
            // For create and update, there will already be a client-side record
            // to match with which will contain any defaulted in values.
            reader.applyDefaults = operation.action === 'read';

            result = reader.read(me.extractResponseData(response));

            if (result.success !== false) {
                //see comment in buildRequest for why we include the response object here
                Ext.apply(operation, {
                    response: response,
                    resultSet: result
                });

                // dima: begin adding filters
                var filters = operation.filters;
                if (filters && filters.length) {
                    result.records = Ext.Array.filter(result.records, Ext.util.Filter.createFilterFn(filters));
                }
                // dima: end adding filters

                operation.commitRecords(result.records);
                operation.setCompleted();
                operation.setSuccessful();
            } else {
                operation.setException(result.message);
                me.fireEvent('exception', this, response, operation);
            }
        } else {
            me.setException(operation, response);
            me.fireEvent('exception', this, response, operation);
        }

        //this callback is the one that was passed to the 'read' or 'write' function above
        if (typeof callback == 'function') {
            callback.call(scope || me, operation);
        }

        me.afterRequest(request, success);
    },

});

*/

Ext.define('BQ.data.proxy.OrganizerProxy', {
    extend: 'Ext.data.proxy.Rest',
    alternateClassName: 'BQ.data.OrganizerProxy',
    alias : 'proxy.bq-organizer',

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

    projections: {
        'tag_values': null,
        'gob_names': null,
        'tag_names': 'true',
        'gob_types': 'true'
    },
    projections_order : ['tag_values', 'gob_names', 'tag_names', 'gob_types'],
    query : '',
    projections_map: {
        'tag_values': 'tag[value,name="{0}"]',
        'gob_names': 'gobject[name,type="{0}"]',
        'tag_names': 'tag[name]',
        'gob_types': 'gobject[type]'
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

        // create a URL with all required projections
        var url = this.url;
        if (this.query && this.query.length>0) {
            url += '?tag_query='+this.query+'&';
        } else {
            url += '?';
        }

        var extracts = [];
        for (i=0; (name=this.projections_order[i]); i++ ) {
            if (!this.projections[name]) continue;
            var v = this.projections[name].replace('"', '\\"').replace("'", "\\'");
            extracts.push( Ext.String.format(this.projections_map[name], encodeURIComponent(v)));
        }
        //    /data_service/image?extract=tag[name],tag[value,name=qqq],gobject[type],gobject[name,type=aa]
        url += "extract=" + extracts.join(',');

        request.url = url + '&wpublic='+this.browserParams.wpublic;
        return request.url;
    },

    doRequest: function (operation, callback, scope) {
        if (operation.action == 'destroy') return;
        this.callParent(arguments);
    },

    // dima: fix the absense of local filtering by replacing processResponse
    // with our version with filering added, this may require updates for
    // extjs 5
    processResponse: function (success, operation, request, response, callback, scope) {
        if (Ext.getVersion().major>=5) {
            Ext.log({ level: "warn" }, 'Overwrite of processResponse is designed for ExtJS 4.2.1, needs replacement!');
        }

        var me = this,
            reader,
            result;

        if (success === true) {
            reader = me.getReader();

            // Apply defaults to incoming data only for read operations.
            // For create and update, there will already be a client-side record
            // to match with which will contain any defaulted in values.
            reader.applyDefaults = operation.action === 'read';

            result = reader.read(me.extractResponseData(response));

            if (result.success !== false) {
                //see comment in buildRequest for why we include the response object here
                Ext.apply(operation, {
                    response: response,
                    resultSet: result
                });

                // dima: begin adding filters
                var filters = operation.filters;
                if (filters && filters.length) {
                    result.records = Ext.Array.filter(result.records, Ext.util.Filter.createFilterFn(filters));
                }
                // dima: end adding filters

                operation.commitRecords(result.records);
                operation.setCompleted();
                operation.setSuccessful();
            } else {
                operation.setException(result.message);
                me.fireEvent('exception', this, response, operation);
            }
        } else {
            me.setException(operation, response);
            me.fireEvent('exception', this, response, operation);
        }

        //this callback is the one that was passed to the 'read' or 'write' function above
        if (typeof callback == 'function') {
            callback.call(scope || me, operation);
        }

        me.afterRequest(request, success);
    },
});


//--------------------------------------------------------------------------------------
// BQ.tree.files.Panel
// events:
//    selected -
//--------------------------------------------------------------------------------------

Ext.namespace('BQ.tree.organizer');
BQ.tree.organizer.icons = {
    tag_type:      'icon-tag-type',
    tag_name:      'icon-tag-name',
    tag_value:     'icon-tag-value',
    gobject_type:  'icon-gob-type',
    gobject_name:  'icon-gob-name',
    gobject_value: 'icon-gob-value',
};

BQ.tree.organizer.path2type = {
    t: 'tag',
    g: 'gobject',
};

BQ.tree.organizer.path2attr = {
    t: 'type',
    n: 'name',
    v: 'value',
};

Ext.define('BQ.tree.organizer.Panel', {
    extend: 'Ext.tree.Panel',
    alias: 'widget.bq-tree-organizer-panel',
    requires: ['Ext.button.Button', 'Ext.tree.*', 'Ext.data.*'],

    path: undefined, // initial path
    url: '/data_service/image', // base url

    componentCls: 'organizer',
    //pageSize: 100,          // number of records to fetch on every request
    //trailingBufferZone: 20, // Keep records buffered in memory behind scroll
    //leadingBufferZone: 20,  // Keep records buffered in memory ahead of scroll

    displayField: 'text',

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
    allowDeselect: false,
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
            var t = record.data.type==='tag' ? 'tag' : 'gobject',
                icon = t+'_'+record.data.attribute;
            if (icon in BQ.tree.organizer.icons)
                return BQ.tree.organizer.icons[icon];
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
        dataIndex: 'value',
        sortable: true,
        renderer: function(value, meta, record) {
            if (record.data.negated)
                meta.tdCls = 'negated';
            return value;
        },
    }, {
        xtype: 'actioncolumn',
        text: 'Count',
        width: 50,
        dataIndex: 'count',
        sortable: true,
        tdCls: 'counts',
        stopSelection : true,
        //align: 'center',
        align: 'right',
        tooltip: 'Toggle to find resources WITHOUT this annotation',
        renderer: function(value, meta, record) {
            if (record.data.negated)
                meta.tdCls = 'negated';
            if (value<Math.pow(10, 3))
                return value;
            else if (value>=Math.pow(10, 3) && value<Math.pow(10, 6)) // K
                return (value/Math.pow(10, 3)).toFixed(2)+'K';
            else if (value>=Math.pow(10, 6) && value<Math.pow(10, 9)) // G
                return (value/Math.pow(10, 6)).toFixed(2)+'M';
            else
                return (value/Math.pow(10, 9)).toFixed(2)+'G';
        },
        handler: function(view, rowIndex, colIndex, item, e, record, row) {
            // if (record.data.attribute === 'name') {
            //     BQ.ui.notification('Not queries on "name" attributes are currently disabled' );
            //     return;
            // }
            if (record.data.negated)
                record.data.negated = false;
            else
                record.data.negated = true;

            var tree = view;
                //selection = tree.getSelectionModel(),
                //sel = selection.getSelection();

            // the query for this node has changed and thus childer are no loger valid
            // we need to force the reload of the store for this node since query has changed
            tree.getSelectionModel().deselectAll();
            //record.collapse(); // dima: removing all the children is enough
            view.refreshNode(rowIndex); // re-render the node itself

            record.removeAll(true);
            record.data.loaded = false;
            record.data.expanded = false;
            tree.getSelectionModel().select(record);

            /*if (sel[0] === record) {
                tree.setActiveNode(record);
            } else {
                tree.getSelectionModel().select(record);
            }*/
        },

    }],

    initComponent : function () {
        this.url_selected = this.url;

        var btn_sort = {
            xtype: 'button',
            itemId: 'btnSort',
            //text: 'Sort',
            iconCls: 'icon-sorting',
            tooltip: 'Sort columns',
            enableToggle: false,
            pressed: false,
            cls: 'sort_button',
            width: 40,
            height: 35,

            menu: {
                plain: true,
                cls: 'organizer',
                defaults: {
                    iconCls: 'icon-sort',
                    group: 'sort',
                    scope: this,
                },
                items: [{
                    xtype: 'tbtext',
                    text: '<span class="menu-heading">Sort by:</span>',
                }, {
                    text: 'Text',
                    //scope: this,
                    checked: false,
                    //group: 'sort',
                    cls: 'DESC',
                    direction: 'DESC',
                    handler: function(item) {
                        item.direction = item.direction === 'DESC' ? 'ASC' : 'DESC';
                        if (item.direction === 'DESC')
                            item.addCls('DESC');
                        else
                            item.removeCls('DESC');
                        //this.store.sort('value', item.direction);
                        this.store.sort([{
                            property : 'value',
                            direction: item.direction
                        }, {
                            property : 'type',
                            direction: item.direction
                        }, {
                            property : 'attribute',
                            direction: item.direction
                        }, {
                            property : 'count',
                            direction: item.direction
                        }]);
                    },
                }, {
                    text: 'Counts',
                    //scope: this,
                    checked: false,
                    //group: 'sort',
                    direction: 'ASC',
                    handler: function(item) {
                        item.direction = item.direction === 'DESC' ? 'ASC' : 'DESC';
                        if (item.direction === 'DESC')
                            item.addCls('DESC');
                        else
                            item.removeCls('DESC');
                        //this.store.sort('count', item.direction);
                        this.store.sort([{
                            property : 'count',
                            direction: item.direction
                        }, {
                            property : 'type',
                            direction: item.direction
                        }, {
                            property : 'attribute',
                            direction: item.direction
                        }, {
                            property : 'value',
                            direction: item.direction
                        }]);
                    },
                }, {
                    text: 'Type',
                    //scope: this,
                    checked: true,
                    //group: 'sort',
                    cls: 'DESC',
                    direction: 'DESC',
                    handler: function(item) {
                        item.direction = item.direction === 'DESC' ? 'ASC' : 'DESC';
                        if (item.direction === 'DESC')
                            item.addCls('DESC');
                        else
                            item.removeCls('DESC');
                        this.store.sort([{
                            property : 'type',
                            direction: item.direction
                        }, {
                            property : 'attribute',
                            direction: item.direction
                        }, {
                            property : 'value',
                            direction: item.direction
                        }, {
                            property : 'count',
                            direction: item.direction
                        }]);
                    },
                }],
            },
        };

        this.dockedItems = [{
            xtype: 'toolbar',
            itemId: 'tool_bar',
            dock: 'top',
            hidden: true,
            defaults: {
                scale: 'medium',
                enableToggle: true,
                pressed: true,
                scope: this,
                cls: 'btn-pressable',
            },
            items: [{
                itemId: 'btnShowTags',
                text: 'Textual',
                iconCls: 'icon-tags',
                handler: this.onTags,
                tooltip: 'Organize based on textual annotations',
            }, {
                itemId: 'btnShowGobs',
                text: 'Graphical',
                iconCls: 'icon-gobs',
                handler: this.onGobs,
                tooltip: 'Organize based on graphical annotations',
            }, ' ', {
                hidden: true,
                itemId: 'btnShowTypes',
                iconCls: 'icon-types',
                handler: this.updateVisibility,
                tooltip: 'Use types for organization',
            }, {
                hidden: true,
                itemId: 'btnShowNames',
                iconCls: 'icon-names',
                handler: this.updateVisibility,
                tooltip: 'Use names for organization',
            }, {
                hidden: true,
                itemId: 'btnShowValues',
                iconCls: 'icon-values',
                handler: this.updateVisibility,
                tooltip: 'Use values for organization',
            }/*, '->',
            btn_sort*/],
        }, /*{
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
        },*/ {
            xtype:'container',
            dock: 'top',
            height: 35,
            cls: 'sort_bar',
            layout: {
                type: 'hbox',
                //align: 'stretch',
            },
            items: [{
                xtype:'bq-picker-path',
                itemId: 'path_bar',
                dock: 'top',
                flex: 10,
                height: 35,
                path: '/',
                listeners: {
                    scope: this,
                    //browse: this.browsePath,
                    changed: function (el, path) {
                        this.setPath(path);
                    },
                },
            }, btn_sort],
        }];

        var me = this;
        this.store = Ext.create('Ext.data.TreeStore', {
            defaultRootId: 'organizer',
            autoLoad: false,
            autoSync: false,
            appendId: false,
            //lazyFill: true,
            filterOnLoad: true,
            remoteFilter: false,
            remoteSort: false,

            proxy : {
                type : 'bq-organizer',
                url : this.url,
                batchActions: false,
                ownerPanel: this,
                browserParams: this.browserParams,
                reader : {
                    type : 'xml',
                    root : 'resource',
                    record: '>*',
                },
            },

            fields : [{
                name : 'type',
                convert : function (value, record) {
                    if (!(record.raw instanceof Node)) return '';
                    var r = record.raw,
                        t = r.getAttribute('type') || r.tagName;
                    return t==='tag' ? 'tag' : 'gobject';
                },
            }, {
                name : 'attribute',
                convert : function (value, record) {
                    if (!(record.raw instanceof Node)) return '';
                    var r = record.raw;
                    if (r.getAttribute('name') && r.getAttribute('value'))
                        return 'value';
                    if (r.getAttribute('name') && !r.getAttribute('value'))
                        return 'name';
                    return 'type';
                },
            }, {
                name : 'value',
                convert : function (value, record) {
                    if (!(record.raw instanceof Node)) return '';
                    var r = record.raw;
                    if (r.getAttribute('name') && r.getAttribute('value'))
                        return r.getAttribute('value');
                    if (r.getAttribute('name') && !r.getAttribute('value'))
                        return r.getAttribute('name');
                    return r.getAttribute('type') || r.tagName;
                },
            }, {
                name : 'count',
                type: 'int',
                convert : function (value, record) {
                    if (!(record.raw instanceof Node)) return '';
                    var r = record.raw;
                    return parseInt(r.textContent);
                },
            }/*, {
                name : 'text',
                convert : function (value, record) {
                    if (!(record.raw instanceof Node)) return '';
                    return Ext.String.format('{0}<span class="counts">{1}</span>', record.data.value, record.data.count);
                    //return record.data.value;
                },
            }*/],

            filters: [
                function (item) {
                    if (me.active_query && item.data.value in me.active_query &&
                        me.active_query[item.data.value] === item.data.type+':'+item.data.attribute)
                        return false;
                    return true;
                }
            ],

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

    getQuery : function () {
        return this.store.getProxy().query;
    },

    getOrder : function () {
        return this.order;
    },

    getUrl : function () {
        return this.url;
    },

    setActive : function () {
        this.fireEvent('selected', this.url_selected, this);
    },

    setActiveNode : function (record) {
        if (this.no_selects===true) return; // || node.data.loaded===true) return;
        var node = record,
                   nodes=[];
        while (node) {
            if (!(node.raw instanceof Node)) break;
            nodes.push(node);
            node = node.parentNode;
        }
        nodes.reverse();

        this.active_query = {};
        var path=[], query=[], order=[], i=0;
        for (i=0; (node=nodes[i]); ++i) {
            var sep='', pt='', neg = '';
            if (node.data.type === 'tag') {
                pt += 't:';
            } else {
                pt += 'g:';
            }
            if (node.data.attribute === 'type') {
                sep = '::';
                pt += 't:';
            } else if (node.data.attribute === 'name') {
                sep = ':';
                pt += 'n:';
            } else {
                pt += 'v:';
            }
            if (node.data.negated === true) {
                neg = '~';
            }
            this.active_query[node.data.value] = node.data.type+':'+node.data.attribute;

            if ( (node.data.attribute==='value' && node.data.type==='tag')
                 || (node.data.attribute==='name' && node.data.type!=='tag') ) {
                query[query.length-1] += neg+encodeURIComponent('"'+node.data.value+'"' + sep);
            } else {
                query.push(neg+encodeURIComponent('"'+node.data.value+'"')+sep);
                if (node.data.type==='tag' && node.data.negated !== true)
                    order.push( '"'+encodeURIComponent(node.data.value)+'":asc' );
            }

            path.push(pt+node.data.value);
        }
        this.queryById('path_bar').setPath( '/'+path.join('/') );
        this.order = order.join(',');

        var proxy = this.store.getProxy();
        proxy.query = query.join(encodeURIComponent(' AND '));

        if (record.data.type === 'tag' && record.data.attribute !== 'value') {
            proxy.projections.gob_names = null;
            proxy.projections.tag_values = record.data.value;
        } else if (record.data.attribute !== 'name') {
            proxy.projections.gob_names = record.data.value;
            proxy.projections.tag_values = null;
        } else {
            proxy.projections.tag_values = null;
            proxy.projections.gob_names = null;
        }

        // test projection buttons
        if (!this.queryById('btnShowTags').pressed) {
            proxy.projections.tag_names = null;
            proxy.projections.tag_values = null;
        }
        if (!this.queryById('btnShowGobs').pressed) {
            proxy.projections.gob_names = null;
            proxy.projections.gob_types = null;
        }
        if (!this.queryById('btnShowTypes').pressed) {
            proxy.projections.gob_types = null;
        }
        if (!this.queryById('btnShowNames').pressed) {
            proxy.projections.tag_names = null;
            proxy.projections.gob_names = null;
        }
        if (!this.queryById('btnShowValues').pressed) {
            proxy.projections.tag_values = null;
        }

        this.url_selected = path.join('/');
        this.fireEvent('selected', this.url_selected, this);
    },

    onSelect : function (me, record, index, eOpts) {
        if (record.isExpanded()) {
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
        this.getSelectionModel().select(node);
    },

    onPath: function (node, p) {
        if (!node) return;
        p.shift();

        if (p.length<=0) {
            this.getSelectionModel().select(node);
            return;
        }

        var txt = p[0].split(':'),
            type = BQ.tree.organizer.path2type[txt[0]],
            attr = BQ.tree.organizer.path2attr[txt[1]],
            value = txt[2];
        node = node.findChildBy(
            function (n) {
                if (n.data.type === type &&
                    n.data.attribute === attr &&
                    n.data.value === value) return true;
            },
            this,
            true
        );
        if (node)
            node.expand(false, function (nodes) {
                if (!nodes || nodes.length<1) return;
                this.onPath(nodes[0].parentNode, p);
            }, this);
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
        this.store.getProxy().query = undefined;
        proxy.projections.tag_values = null;
        proxy.projections.gob_names = null;

        this.getSelectionModel().deselectAll();
        var root = this.getRootNode();
        this.store.suspendAutoSync();
        root.removeAll(true);
        this.store.resumeAutoSync();
        this.store.load();
        this.no_selects = undefined;
        this.getSelectionModel().select(root);
    },

    onTags: function (btn) {
        var btn_t = this.queryById('btnShowTags'),
            btn_g = this.queryById('btnShowGobs');
        if (!btn_t.pressed && !btn_g.pressed) {
            BQ.ui.notification('You need at least one type to organize upon, enabling graphical...');
            btn_g.toggle(true);
            this.updateVisibility();
        } else {
            this.updateVisibility();
        }
    },

    onGobs: function (btn) {
        var btn_t = this.queryById('btnShowTags'),
            btn_g = this.queryById('btnShowGobs');
        if (!btn_t.pressed && !btn_g.pressed) {
            BQ.ui.notification('You need at least one type to organize upon, enabling textual...');
            btn_t.toggle(true);
            this.updateVisibility();
        } else {
            this.updateVisibility();
        }
    },

    updateVisibility: function (noreload) {
        var proxy = this.store.getProxy();

        proxy.projections.tag_names = 'true';
        proxy.projections.gob_types = 'true';
        proxy.projections.tag_values = null;
        proxy.projections.gob_names = null;

        if (!this.queryById('btnShowTags').pressed) {
            proxy.projections.tag_names = null;
            proxy.projections.tag_values = null;
        }
        if (!this.queryById('btnShowGobs').pressed) {
            proxy.projections.gob_names = null;
            proxy.projections.gob_types = null;
        }
        if (!this.queryById('btnShowTypes').pressed) {
            proxy.projections.gob_types = null;
        }
        if (!this.queryById('btnShowNames').pressed) {
            proxy.projections.tag_names = null;
            proxy.projections.gob_names = null;
        }
        if (!this.queryById('btnShowValues').pressed) {
            proxy.projections.tag_values = null;
        }
        //this.reset();
        this.store.reload();
    },

});

