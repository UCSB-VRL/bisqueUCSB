Ext.define('BQ.module.RowExpander', {
    extend: 'Ext.grid.plugin.RowExpander',
    requires: [
        'Ext.grid.feature.RowBody',
        'Ext.grid.feature.RowWrap'
    ],
    alias: 'plugin.modulerowexpander',

    bindView: function(view) {
        if (this.expandOnEnter) {
            view.on('itemkeydown', this.onKeyDown, this);
        }
        if (this.expandOnDblClick) {
            view.on('itemdblclick', this.onDblClick, this);
        }
        if (this.expandOnClick) {
            //view.on('itemclick', this.onClick, this);
            view.on('itemmousedown', this.onClick, this);
        }
    },
    addExpander: function(){ //remove the plus
        //this.grid.headerCt.insert(0, this.getHeaderConfig());
    },

    onClick: function(view, cell, rowIdx, cellIndex, e) {
        this.toggleRow(rowIdx);
    },

    getRowBodyFeatureData: function(record, idx, rowValues) {
        var me = this
        me.self.prototype.setupRowData.apply(me, arguments);

        // If we are lockable, the expander column is moved into the locked side, so we don't have to span it
        if (!me.grid.ownerLockable) {
            rowValues.rowBodyColspan = "100%";//rowValues.rowBodyColspan+1; //fits the entire panel
        }
        rowValues.rowBody = me.getRowBodyContents(record);
        rowValues.rowBodyCls = me.recordsExpanded[record.internalId] ? '' : me.rowBodyHiddenCls;
    },

    expandRow: function(rowIdx) { //costom expander
        var view = this.view,
            rowNode = view.getNode(rowIdx),
            row = Ext.get(rowNode),
            nextBd = Ext.get(row).down(this.rowBodyTrSelector),
            record = view.getRecord(rowNode),
            grid = this.getCmp();

        if (row.hasCls(this.rowCollapsedCls)) {
            row.removeCls(this.rowCollapsedCls);
            nextBd.removeCls(this.rowBodyHiddenCls);
            this.recordsExpanded[record.internalId] = true;
            rowNode.getElementsByClassName('x-grid-data-row')[0].hidden = true; //hides row
            view.refreshSize();
            view.fireEvent('expandbody', rowNode, record, nextBd.dom);
        }
    },

    collapeRow: function(rowIdx) { //custom collapse
        var view = this.view,
            rowNode = view.getNode(rowIdx),
            row = Ext.get(rowNode),
            nextBd = Ext.get(row).down(this.rowBodyTrSelector),
            record = view.getRecord(rowNode),
            grid = this.getCmp();

        if (!row.hasCls(this.rowCollapsedCls)) {
            row.addCls(this.rowCollapsedCls);
            nextBd.addCls(this.rowBodyHiddenCls);
            this.recordsExpanded[record.internalId] = false;
            rowNode.getElementsByClassName('x-grid-data-row')[0].hidden = false; //shows row
            view.refreshSize();
            view.fireEvent('collapsebody', rowNode, record, nextBd.dom);
        }
    },

    toggleRow: function(rowIdx) {
        var view = this.view,
            rowNode = view.getNode(rowIdx),
            row = Ext.get(rowNode),
            nextBd = Ext.get(row).down(this.rowBodyTrSelector),
            record = view.getRecord(rowNode),
            grid = this.getCmp();

        if (row.hasCls(this.rowCollapsedCls)) {
            this.expandRow(rowIdx)
        } else {
            this.collapeRow(rowIndex)
        }
    },
})


Ext.define('BQ.module.UnregisteredPanel', {
    extend: 'Ext.grid.Panel',
    title: 'Engine Modules',
    border: false,
    engineList: [],
    selModel: {
        allowDeselect: true,
    },
    viewConfig: {
        markDirty: false,
    },
    columns: {
        items: [/*
            {
                width: 20,
                lockable: false,
                sortable: false,
                resizable: false,
                draggable: false,
                hideable: false,
                menuDisabled: true,
                cls: Ext.baseCSSPrefix + 'grid-header-special',
                renderer: function(value, metadata) {
                    metadata.tdCls = Ext.baseCSSPrefix + 'grid-cell-special';
                    return '<div class="' + Ext.baseCSSPrefix + 'grid-row-expander"></div>';
                },
            },*/
            {dataIndex: 'thumbnail_uri',
                width: 45,
                renderer: function(value, meta, record){
                    if(record.get('registration') == 'Registered') {
                        return '<img style="opacity:0.4;" src="'+value+'" height="32" width="32"/>';
                    } else {
                        return '<img  src="'+value+'" height="32" width="32"/>';
                    }
                },
            },
            {text: 'Name', dataIndex: 'name', sortable: true, flex:1},
            {text: 'Authors', dataIndex: 'authors', sortable: true, flex:1},
            {text: 'Version', dataIndex: 'version', sortable: true, flex:1},
            {
                text: 'Registration Status',
                dataIndex: 'registration',
                sortable: true,
                flex:1,
                renderer: function (value, meta) {
                    if(value == 'Registered') {
                        //meta.style = "background-color:#B7FFD2;";
                        return '<span style="color:#cccccc; line-height:32px; text-align:center; height:32px;"><b>'+value+'</b></span>';
                    } else {
                        return '<span style="line-height:32px; text-align:center; height:32px;">'+value+'</span>';
                    }
                }
            },
        ],
        defaults: {
            renderer : function (value, meta, record) {
                if(record.get('registration') == 'Registered') {
                    //meta.style = "background-color:#B7FFD2;";
                    return '<span style="color:#cccccc; line-height:32px; text-align:center; height:32px;">'+value+'</span>';
                } else {
                    return '<span style="line-height:32px; text-align:center; height:32px;">'+value+'</span>';
                }
            }
        },
    },

    plugins: [{
        ptype: 'modulerowexpander',
        pluginId: 'modulerowexpander',
        selectRowOnExpand: true,
        expandOnEnter: false,
        expandOnDblClick: false,
        padding: '10px',
        //expandOnClick: true,

        rowBodyTpl : [
            '<tpl if="registration == \'Registered\'"><div style="margin:5px;opacity:0.4;"></tpl>',
            '<tpl if="registration != \'Registered\'"><div style="margin:5px;"></tpl>',
                '<h1 style="padding-top:10px; height:30px;  text-overflow:ellipsis;  white-space: nowrap; overflow:hidden; margin:0px;">{name}</h1>', //float:left;width:90%;
                '<div style="width: 100%; overflow: hidden;">',
                    '<img src="{thumbnail_uri}" alt="Not Found!" style="width:128px; height:128px; float:left; margin:11px"/>',
                    '<div style="margin-left:148px;">',
                        '<p><b>Title:</b> {title}</p>',
                        '<p><b>Description:</b> {description}</p>',
                        '<p><b>Authors:</b> {authors}</p>',
                        '<p><b>Version:</b> {version}</p>',
                        '<p><b>Engine:</b> {engine}</p>',
                        '<p><b>Registration Status:</b> {registration}</p>',
                    '</div>',
                '</div>',
            '</div>',
        ],

    }],

    initComponent: function(config) {
        var config = config || {};
        var me = this;
        var items = [];

        var store = new Ext.data.JsonStore({
            fields : [{
                name: 'title',
            },{
                name: 'name',
            },{
                name: 'resource_uniq',
            },{
                name: 'owner',
            },{
                name: 'owner_uri',
            },{
                name: 'visibility',
            },{
                name: 'status',
            },{
                name: 'authors',
            },{
                name: 'thumbnail_uri',
            },{
                name: 'description',
            },{
                name: 'definition',
            },{
                name: 'moduleXmlDoc',
            },{
                name: 'version',
            }, {
                name: 'module_uri',
            }, {
                name: 'engine',
            }, {
                name: 'registration'
            }],
            root   : 'records'
        });

        Ext.apply(me, {
            store: store,
        });

        //set the row expander as selector
        this.on('select', function(el, record, index, eOpt) {
            me.getPlugin('modulerowexpander').expandRow(index);
        });

        this.on('deselect', function(el, record, index, eOpt) {
            me.getPlugin('modulerowexpander').collapeRow(index);
        });

        this.store.on('add', function(store, records, index, eOpts) {
            for (var r=0; r<records.length;r++) {
                me.checkRegistrationModule(records[r]);
            }
        });

        this.callParent([config]);
    },

    searchForEngines: function(cb) {
        var me = this;
        Ext.Ajax.request({
            url: '/module_service',
            params: {view:'short'},
            method: 'GET',
            headers: {'Content-Type': 'text/xml' },
            disableCaching: false,
            success: function(response) {
                var xmlDoc = response.responseXML;
                var moduleNodes = BQ.util.xpath_nodes(xmlDoc, '//module');
                var engine_list =[];
                var engine_hash = {};
                for (var i = 0; i<moduleNodes.length; i++){
                    var engine = moduleNodes[i].attributes['value'].value;
                    var name = moduleNodes[i].attributes['name'].value;
                    if (engine && name) {
                        //strip the name from the engine
                        var engine = engine.replace(new RegExp("/" + name+ "+$", "g"), "");
                        engine_hash[engine] = engine;
                    }
                }
                for (var i in engine_hash) {
                    engine_list.push(i);
                }
                if (cb) {
                    cb(engine_list);
                }
            },
            failure: function(response) {
                BQ.ui.error('Failed to find module service');
            },
            scope: this,
        });
    },

    lookUpEngine: function(engine) {
        var me = this;
        var engine_httpless = engine.replace(/.*?:\/\//g, "");
        Ext.Ajax.request({
            url: '/proxy/'+engine_httpless+'/_services',
            method: 'GET',
            headers: { 'Content-Type': 'text/xml' },
            disableCaching: false,
            success: function(response) {
                var xmlDoc = response.responseXML;
                var moduleNodes = BQ.util.xpath_nodes(xmlDoc, '//service');
                for (var i=0; i<moduleNodes.length; i++) {
                    var engine_module = moduleNodes[i].attributes['value'].value;
                    var name = moduleNodes[i].attributes['name'].value;
                    if (engine_module && name) {
                        this.lookUpEngineModule(engine_module);
                    }
                }
            },
            failure: function(response) {
                BQ.ui.error('Failed to find engine');
            },
            scope: this,
        });
    },

    lookUpEngineModule: function(engine_module) {
        var me = this;
        var engine_httpless = engine_module.replace(/.*?:\/\//g, "");
        Ext.Ajax.request({
            url: '/proxy/'+engine_httpless+'/definition',
            method: 'GET',
            headers: { 'Content-Type': 'text/xml' },
            disableCaching: false,
            success: function(response) {
                var xml = response.responseXML;
                me.populateTable(engine_module, xml);
            },
            failure: function(response) {
                BQ.ui.error('Failed to find module');
            },
            scope: this,
        });
    },

    populateTable: function(engine_module, definition) {
        var me = this;
        var moduleList = []
        var moduleNodes = BQ.util.do_xpath(definition, '//module',  XPathResult.ORDERED_NODE_ITERATOR_TYPE);
        var i;
        var engine_httpless = engine_module.replace(/.*?:\/\//g, "");

        function getTagValues(node, name) {
            if(node) {
                var tag = node.querySelector('tag[name="'+name+'"]')
                if (tag) {
                    var value = tag.attributes['value']||'';
                    if (value) value = value.value;
                    else var value = ''
                }
            }
            return value||'';
        }

        function getVersion(node) {
            if(node) {
                var module_options = node.querySelector('tag[name="module_options"]')
                if (module_options) {
                    var version = module_options.querySelector('tag[name="version"]')
                    if (version) {
                        var value = version.attributes['value']||'';
                        if (value) value = value.value;
                        else value = ''
                    }
                }
            }
            return value||'';
        }

        function getThumbnail(node) {
            // var thumbnail = getTagValues(i,'thumbnail')
            // if (thumbnail) {
            //     //strip public
            //     var thumbnail = thumbnail.replace(new RegExp("^public+", "g"), "");
            //     //add proxy url
            //     return (i.attributes['value'].value || '')+thumbnail;
            // } else {
            //     return '';
            //}
            return '/proxy/'+engine_httpless+ '/thumbnail';


        }

        while (i = moduleNodes.iterateNext()) {
            var moduleNode = {
                title: getTagValues(i, 'title'),
                authors: getTagValues(i, 'authors'),
                description: getTagValues(i, 'description'),
                name: i.attributes['name'].value || '',
                engine: i.attributes['value'].value || '',
                type: i.attributes['type'].value || '',
                version: getVersion(i),
                definition: definition,

                groups: [],
                thumbnail_uri: getThumbnail(i),
            };
            var record = me.store.add(moduleNode);
        }
    },


    checkRegistrationModule: function(record) {
        var me = this;
        var engine = record.get('engine');
        if (!engine) {
            BQ.ui.error('Record does not have an engine!')
        } else if (engine && me.module_service_xml) {
            me.doCheckRegistrationModule(record, me.module_service_xml);
        } else if (engine) {
            Ext.Ajax.request({
                url: '/module_service',
                method: 'GET',
                headers: { 'Content-Type': 'text/xml' },
                disableCaching: false,
                success: function(response) {
                    me.module_service_xml = response.responseXML;
                    me.doCheckRegistrationModule(record, me.module_service_xml);
                },
                failure: function(response) {
                    BQ.ui.error('Failed to find module_service');
                    record.set('registration', '???')
                },
                scope: this,
            });
        }
    },

    doCheckRegistrationModule: function(record, xmlDoc) {
        var engine = record.get('engine');
        var moduleList = BQ.util.xpath_nodes(xmlDoc, '//module[@value="'+engine+'"]')
        if (moduleList.length<1){ //module was not registered
            record.set('registration', 'Not Registered')
        } else {
            record.set('registration', 'Registered')
            var uniq = moduleList[0].getAttribute('resource_uniq')
            record.set('resource_uniq', uniq)
        }
    },

    updateRegistration: function(cb) {
        var me = this;
        Ext.Ajax.request({
            url: '/module_service',
            method: 'GET',
            headers: { 'Content-Type': 'text/xml' },
            disableCaching: false,
            success: function(response) {
                var xml = response.responseXML;
                me.store.each(function(record) {
                    var engine = record.get('engine');
                    if (engine) {
                        var moduleList = BQ.util.xpath_nodes(xml, '//module[@value="'+engine+'"]');
                        if (moduleList.length<1){ //module was not registered
                            record.set('registration', 'Not Registered');
                        } else {
                            record.set('registration', 'Registered')
                            var uniq = moduleList[0].getAttribute('resource_uniq');
                            record.set('resource_uniq', uniq);
                        }
                    } else {
                        BQ.ui.error('Record does not have an engine!');
                    }
                });
                if(cb) cb();
            },
            failure: function(response) {
                BQ.ui.error('Failed to find module_service');
                record.set('registration', '???');
            },
            scope: this,
        });
    },

    reload: function(engine_url){
        if (engine_url) {
            //clear store
            this.store.loadData([]);
            this.lookUpEngine(engine_url);
            this.fireEvent('reload',this);
        }
    },
});


Ext.define('BQ.module.RegisteredPanel', {
    extend: 'Ext.grid.Panel',
    title: 'Registered Modules',
    border: false,
    selModel: {
        allowDeselect: true,
    },
    viewConfig: {
        markDirty: false,
        stripeRows: false,
        getRowClass: function (record, rowIndex, rp, store) {
            rp.tstyle += 'height: 50px;';
        }
    },

    columns: {
        items: [/*
            {
                width: 20,
                lockable: false,
                sortable: false,
                resizable: false,
                draggable: false,
                hideable: false,
                menuDisabled: true,
                cls: Ext.baseCSSPrefix + 'grid-header-special',
                renderer: function(value, metadata) {
                    metadata.tdCls = Ext.baseCSSPrefix + 'grid-cell-special';
                    return '<div class="' + Ext.baseCSSPrefix + 'grid-row-expander"></div>';
                },
            },*/
            {dataIndex: 'thumbnail_uri',
                width: 45,
                renderer: function(value, meta, record){
                    if(record.get('status') != 'Good!') {
                        meta.style = "background-color:#FFCECE;";
                    }
                    return '<img src="'+value+'" height="32" width="32"/>';
                },
            },
            {text: 'Name', dataIndex: 'name', sortable: true, flex:2},
            {text: 'Owner', dataIndex: 'owner', sortable: true, flex:1},
            {text: 'Visibility', dataIndex: 'visibility', sortable: true, flex:1},
            {
                text: 'Status',
                dataIndex: 'status',
                sortable: true,
                flex:1,
                renderer: function(value, meta, record) {
                    if(value == 'Good!') {
                        return '<div style="line-height:32px; text-align:center; height:32px;">'+ value + '</div>';
                    } else if (value) {
                        meta.style = "background-color:#FFCECE;";
                        return '<div style="color:red; line-height:32px; text-align:center; height:32px;"><b>'+ value + '</b></div>';
                    } else {
                        meta.style = "background-color:#FFCECE;";
                        return '<div style="color:red; line-height:32px; text-align:center; height:32px;"><b>'+ value + '</b></div>';
                    }
                },
            },
        ],
        defaults: {
            //padding: 15,
            renderer : function (value, meta, record) {
                if(record.get('status') != 'Good!') {
                    meta.style = "background-color:#FFCECE;";
                }
                return '<div style="line-height:32px; text-align:center; height:32px;">'+ value + '</div>';
            },
        },
    },

    initComponent: function(config) {
        var config = config || {};
        var me = this;

        this.store = new Ext.data.JsonStore({
            fields : [{
                name: 'title',
            },{
                name: 'name',
            },{
                name: 'resource_uniq',
            },{
                name: 'owner',
            },{
                name: 'owner_uri'
            },{
                name: 'visibility',
            },{
                name: 'status',
            },{
                name: 'authors',
            },{
                name: 'thumbnail_uri',
            },{
                name: 'description',
            },{
                name: 'definition',
            },{
                name: 'moduleXmlDoc',
            },{
                name: 'version',
            }, {
                name: 'module_uri',
            }, {
                name: 'engine',
            }, {
                name: 'registration'
            }],
            root   : 'records'
        });

        /*Ext.apply(me, {
            //items: items,
            //tbar: tbar,
            store: this.store,
        });*/


        this.store.on('add', function(store, records, index, eOpts) {
            var i=0, r=null;
            for (i=0; (r=records[i]); ++i) {
                if (r.data.loading || r.data.loaded) continue;
                me.updateEntry(r);
            }
        });

        //set the row expander as selector
        this.on('select', function(el, record, index, eOpt) {
            me.getPlugin('modulerowexpander').expandRow(index);
        });

        this.on('deselect', function(el, record, index, eOpt) {
            me.getPlugin('modulerowexpander').collapeRow(index);
        });

        //this.initTable();
        this.callParent([config]);
    },

    afterRender: function() {
        this.callParent();
        this.initTable();
    },

    plugins: [{
        ptype: 'modulerowexpander',
        pluginId: 'modulerowexpander',
        selectRowOnExpand: true,
        expandOnEnter: false,
        expandOnDblClick: false,
        padding: '10px',
        enableCaching:false,
        rowBodyTpl : [
            '<tpl if="status == \'Good!\'"><div style="margin:5px;"></tpl>',
            '<tpl if="status != \'Good!\'"><div style="margin:5px; background-color:#FFCECE;"></tpl>',
                '<h1 style="padding-top:10px; height:30px; text-overflow:ellipsis; white-space: nowrap; overflow:hidden; margin:0px;">{name}</h1>', //float:left;width:90%;
                '<div style="width: 100%; overflow: hidden;">',
                    '<img src="{thumbnail_uri}" alt="Not Found!" style="width:128px; height:128px; float:left; margin:11px"/>',
                    '<div style="margin-left:148px;">',
                        '<p><b>Title:</b> {title}</p>',
                        '<p><b>Owner:</b> {owner}</p>',
                        '<p><b>ID:</b> {resource_uniq}</p>',
                        '<p><b>Description:</b> {description}</p>',
                        '<p><b>Authors:</b> {authors}</p>',
                        '<p><b>Version:</b> {version}</p>',
                        '<p><b>Visibility:</b> {visibility}</p>',
                        '<p><b>URL:</b> {module_uri}</p>',
                        '<p><b>Engine URL:</b> {engine}</p>',
                        '<p><b>Status:</b> {status}</p>',
                    '</div>',
                '</div>',
            '</div>',
        ],
    }],


    initTable: function() { //search module service for registered modules
        var me = this;
        Ext.Ajax.request({
            url: '/module_service?tag_order=%22@name%22:asc&wpublic=owner,shared,public',
            //params: {wpublic: 'owner,shared,public', tag_order: '%22@name%22:asc', },
            method: 'GET',
            headers: { 'Content-Type': 'text/xml' },
            disableCaching: false,
            success: function(response) {
                var engine_list = [];
                var engine_hash = {};

                var xml = response.responseXML;
                var moduleNodes = BQ.util.xpath_nodes(xml, '//module');
                var node = null;
                for (var i=0; (node=moduleNodes[i]); ++i) {
                    var record = me.store.add({
                        moduleXmlDoc: node,
                        resource_uniq: node.getAttribute('resource_uniq') || '',
                        name: node.getAttribute('name') || '',
                        owner_uri: node.getAttribute('owner') ||'',
                        engine: node.getAttribute('value') ||'',
                        visibility : node.getAttribute('permission') ||'',
                    });
                    //this.updateEntry(record[0]);

                    var engine = node.getAttribute('value');
                    var name = node.getAttribute('name');
                    if (engine && name) {
                        //strip the name from the engine
                        var engine = engine.replace(new RegExp("/" + name+ "+$", "g"), "");
                        engine_hash[engine] = engine;
                    }
                }

                for (var i in engine_hash) {
                    engine_list.push(i);
                }
                me.main_panel.engineSearchBar.bindStore(engine_list);
                me.main_panel.unregisterPanel.module_service_xml = xml;
            },
            failure: function(response) {
                BQ.ui.error('Failed to find module service');
            },
            scope: this,
        });
    },

    /*
    *   addEntry
    *
    *   adds entry from another table
    */
    addEntry: function(uniq, record, cb) {
        var me = this;
        Ext.Ajax.request({
            url: '/data_service/'+uniq, //should check module service
            method: 'GET',
            headers: {'Content-Type': 'text/xml' },
            disableCaching: false,
            success: function(response) {
                var xml = response.responseXML;
                var moduleNodes = BQ.util.xpath_nodes(xml, '//module');
                if (moduleNodes.length>0) {
                    record.set('moduleXmlDoc', moduleNodes[0]);
                    record.set('resource_uniq', moduleNodes[0].attributes['resource_uniq'].value || '');
                    record.set('name', moduleNodes[0].attributes['name'].value || '');
                    record.set('owner_uri', moduleNodes[0].attributes['owner'].value||'');
                    record.set('engine', moduleNodes[0].attributes['value'].value||'');
                    record.set('visibility', moduleNodes[0].attributes['permission'].value||'');
                    me.updateEntry(record);
                    //me.setRecord(moduleNodes[0], record)
                    if (cb) cb();
                }
            },
            failure: function(response) {
                BQ.ui.error('Could not find module at data_service/'+uniq)
            },
        });
    },

    updateEntry: function(record) {
        var me = this;
        var owner_uri = record.get('owner_uri');
        var name = record.get('name');
        var engine = record.get('engine');
        if (owner_uri) me.setOwner(record, owner_uri);
        //if (name) me.setStatus(record, name);
        //if (engine) me.setEngine(record, engine); // dima, we only need to do this when needed

        // dima: fetch the whole thing from module service proxy
        if (name) me.fetchModuleDefinition(record, name);
    },

    removeEntry: function(record) {
        var me = this;
        var uniq = record.get('resource_uniq');
        var name = record.get('name');
        /*
        if (uniq) {
            var row = me.store.findRecord('resource_uniq', uniq);
        } else {
            var row = me.store.findRecord('name', uniq);
        }*/
        var row = (uniq)? me.store.findRecord('resource_uniq', uniq) : me.store.findRecord('name', name)
        me.store.remove(row);
    },

    setEngine: function(record, engine) {
        var me = this;
        var engine_httpless = engine.replace(/.*?:\/\//g, "");
        Ext.Ajax.request({
            url: '/proxy/'+engine_httpless+'/definition',
            method: 'GET',
            headers: { 'Content-Type': 'text/xml' },
            disableCaching: false,
            success: function(response) {
                var xml = response.responseXML;
                var definition = BQ.util.xpath_nodes(xml, '//module');
                if (definition.length>0) {
                    definition = definition[0];
                    function getTagValues(node, name) {
                        if(node) {
                            var tag = node.querySelector('tag[name="'+name+'"]')
                            if (tag) {
                                var value = tag.attributes['value']||'';
                                if (value) value = value.value;
                            } else {
                                var value = '';
                            }
                        } else {
                            var value = '';
                        }
                        return value;
                    }

                    function getVersion(node) {
                        if(node) {
                            var module_options = node.querySelector('tag[name="module_options"]')
                            if (module_options) {
                                var version = module_options.querySelector('tag[name="version"]')
                                if (version) {
                                    var value = version.attributes['value']||'';
                                    if (value) value = value.value;
                                    else var value = ''
                                }
                            }
                        }
                        return value||'';
                    }

                    function getThumbnail(node) {
                        return '/proxy/'+engine_httpless+ '/thumbnail';
                    }

                    record.set('title', getTagValues(definition, 'title'));
                    record.set('authors', getTagValues(definition, 'authors'));
                    record.set('description', getTagValues(definition, 'description'));
                    record.set('definition', definition);
                    record.set('groups', '');
                    record.set('thumbnail_uri', getThumbnail(definition));
                    record.set('version', getVersion(definition));

                } /*else {
                    BQ.ui.error('Failed to find module defintion at: '+ engine);
                }
                */
            },
            /*
            failure: function(response) {
                BQ.ui.error('Failed to find engine at: '+ engine);
            },*/
            scope: me,
        });
    },

    //sets the owner of all the nodes one node at a time
    setOwner: function(record, owner_uri) {
        var me = this;
        if (owner_uri) {
            BQUser.fetch_user(owner_uri, function(resource) {
                record.set('owner', resource.name || resource.user_name || resource.display_name); // set user name
            }, function() {
                BQ.ui.error('Failed to load user: '+ owner_uri);
            });
            /*
            Ext.Ajax.request({
                url: owner_uri,
                method: 'GET',
                headers: { 'Content-Type': 'text/xml' },
                disableCaching: false,
                success: function(response) {
                    var xml = response.responseXML;
                    var result = BQ.util.xpath_string(xml, '//user/@name');
                    if (result) {
                        record.set('owner', result)
                    }
                },
                failure: function(response) {
                    BQ.ui.error('Failed to find user at: '+ owner_uri);
                },
                scope: me,
            });
            */
        }
    },

    //sets the statuses of all the nodes
    /*
    setStatus: function(record, name) {
        var me = this;
        if (!name) return;
        setTimeout(function() {
            Ext.Ajax.request({
                url: '/module_service/'+name+'/definition',
                method: 'GET',
                headers: { 'Content-Type': 'text/xml' },
                disableCaching: false,
                success: function(response) {
                    record.set('status', 'Good!')
                },
                failure: function(response) {
                    record.set('status', 'Failed!')
                },
                scope: me,
            })
        }, 10 );
    },
    */

    fetchModuleDefinition: function(record, name) {
        var me = this;
        if (!name || record.data.loaded) return;
        record.data.loading = true;
        record.data.loaded = false;

        Ext.Ajax.request({
            url: '/module_service/'+name+'/definition',
            method: 'GET',
            headers: { 'Content-Type': 'text/xml' },
            disableCaching: false,
            success: function(response) {
                var definition = response.responseXML;
                function getTagValues(node, name) {
                    if(node) {
                        var tag = node.querySelector('tag[name="'+name+'"]')
                        if (tag) {
                            var value = tag.attributes['value']||'';
                            if (value) value = value.value;
                        } else {
                            var value = '';
                        }
                    } else {
                        var value = '';
                    }
                    return value;
                }

                function getVersion(node) {
                    if(node) {
                        var module_options = node.querySelector('tag[name="module_options"]')
                        if (module_options) {
                            var version = module_options.querySelector('tag[name="version"]')
                            if (version) {
                                var value = version.attributes['value']||'';
                                if (value) value = value.value;
                                else var value = ''
                            }
                        }
                    }
                    return value||'';
                }

                record.set('status', 'Good!');
                record.set('title', getTagValues(definition, 'title'));
                record.set('authors', getTagValues(definition, 'authors'));
                record.set('description', getTagValues(definition, 'description'));
                record.set('definition', definition);
                record.set('groups', '');
                record.set('module_uri', '/module_service/'+record.get('name') );
                record.set('thumbnail_uri', '/module_service/'+record.get('name')+'/thumbnail' );
                record.set('version', getVersion(definition));
                record.data.loading = false;
                record.data.loaded = true;
                //var idx = record.store.indexOf(record);
                //me.getView().refreshNode(idx);
            },
            failure: function(response) {
                record.set('status', 'Failed!');
            },
            scope: me,
        });
    },

    reload: function() {
        this.store.loadData([]);
        this.initTable();
        this.fireEvent('reload',this)
    },
});


Ext.define('BQ.module.ModuleManagerMain', {
    extend : 'Ext.container.Container',
    alias: 'widget.bq_module_manager',

    layout : 'border',
    border: false,
    initComponent: function(config) {
        var config = config || {};
        //items = [];
        var me = this;

        this.engineSearchBar = Ext.createWidget('combo',{
            //width: '90%',
            flex: 9,
            emptyText: ' Enter Engine URL',
            store: [],
        });


        //need unregister before register panel
        this.unregisterPanel = Ext.create('BQ.module.UnregisteredPanel', {
            ddGroup: 'registerGripDDGroup',
            layout: 'fit',
            width: '50%',
            enableDragDrop: true,
            plain : true,
            hidden : false,
            collapsible : true,
            region: 'east',
            split: true,
            resource: '',
            minimizable: true,
            viewConfig: {
                copy: true,
                markDirty: false,
                plugins: {
                    ptype: 'gridviewdragdrop',
                    pluginId: 'gridviewdragdrop',
                    dragGroup: 'unregisterGridDDGroup',
                    dropGroup: 'registerGridDDGroup',
                    dragText: 'Drag to Register',
                },
            },
            tbar : {
                xtype: 'container',
                padding: false,
                margin: false,
                border: false,
                width: '100%',
                frame: false,
                items: [
                    new Ext.Toolbar({
                        //padding: false,
                        margin: false,
                        border: false,
                        items: [{
                            text: 'Register',
                            xtype: 'button',
                            scale: 'large',
                            height: '50px',
                            disabled: true,
                            handler: function(el, event) {
                                var row = me.unregisterPanel.getSelectionModel().getSelection();
                                if (row.length==1) {
                                    var record = row[0];
                                    var registration = record.get('registration');
                                    if ('Registered' == registration) {
                                        setButton = function() {
                                            el.setText('Register');
                                        }
                                        me.unregisterModule(record, '', setButton);
                                    } else {
                                        setButton = function() {
                                            el.setText('Unregister');
                                        }
                                        me.registerModule(record, '', setButton);
                                    }
                                } else {
                                    BQ.ui.error('Expecting only one row selected at a time');
                                }
                            },
                            onSelect: function(el, record) {
                                this.setDisabled(false);
                                var registration = record.get('registration')
                                if (registration=='Not Registered') {
                                    this.setText('Register');
                                } else {
                                    this.setText('Unregister');
                                }
                            },
                            onRegister: function(el, record) {
                                var records = me.unregisterPanel.getSelectionModel().getSelection();
                                if (records.length==1) {
                                    var registration = records[0].get('registration');
                                    if (registration=='Not Registered') {
                                        this.setText('Register');
                                    } else {
                                        this.setText('Unregister');
                                    }
                                } else {
                                    this.setDisabled(true);
                                }
                            },
                            onUnregister: function(el, record) {
                                this.onRegister(el, record);
                            },
                        },'->',{
                            text: 'Register<br>All',
                            xtype: 'button',
                            scale: 'large',
                            height: '50px',
                            disabled: false,
                            handler: function() {
                                var win = Ext.MessageBox.show({
                                    title: 'Register All',
                                    msg: 'Are you sure you want to try to register all modules on this engine?',
                                    buttons: Ext.MessageBox.OKCANCEL,
                                    fn: function(buttonResponse) {
                                        if (buttonResponse === "ok") {
                                            me.registerAllModule();
                                        }
                                    },
                                });
                            },
                            listeners: {},
                        }],
                        defaults: {
                            listeners: { //disable buttons when deselected
                                afterrender: function(el) {
                                    var buttonEl = el

                                    me.unregisterPanel.on('select',
                                        function(el, record) {
                                            if (buttonEl.onSelect)
                                                buttonEl.onSelect(el,record);
                                    });

                                    me.unregisterPanel.on('deselect',
                                        function(el, record) {
                                            if (buttonEl.onDeselect)
                                                buttonEl.onDeselect(el,record);
                                    });
                                    var store = me.unregisterPanel.getStore();
                                    me.unregisterPanel.on('reload',
                                        function(el, record) {
                                            if (buttonEl.onLoad)
                                                buttonEl.onLoad(el,record);
                                    });
                                    me.on('registered',
                                        function ( el, record) {
                                            if (buttonEl.onRegister)
                                                buttonEl.onRegister(el, record);
                                        }
                                    )
                                    me.on('unregistered',
                                        function ( el, record) {
                                            if (buttonEl.onUnregister)
                                                buttonEl.onUnregister(el, record);
                                        }
                                    )
                                }
                            },
                            onSelect : function(el, record) {
                                this.setDisabled(false);
                            },
                            onDeselect: function(el, record) {
                                this.setDisabled(true);
                            },
                            onLoad: function() {
                                this.setDisabled(true);
                            },
                            onRegister: function() {
                            },
                            onUnregister: function() {
                            },
                            disabled: true,
                        },
                    }),
                    new Ext.Toolbar({
                        padding: false,
                        margin: false,
                        border: false,
                        items: [
                            me.engineSearchBar,
                            {
                                xtype: 'button',
                                text: 'Load',
                                flex: 1,
                                handler: function() {
                                    var engine_url = me.engineSearchBar.getValue()
                                    if (engine_url) {
                                        me.unregisterPanel.reload(engine_url);

                                    }
                                }
                            }
                        ],
                    }),
                ]
            },
        });

        this.registerPanel = Ext.create('BQ.module.RegisteredPanel', {
            //engineSearchBar: this.engineSearchBar,
            main_panel: this,

            ddGroup: 'unregisterGripDDGroup',
            split: true,
            region: 'center',
            autoScroll: true,
            enableDragDrop : true,
            plain : true,
            allowCopy: true,
            viewConfig: {
                markDirty: false,
                plugins: {
                    ptype: 'gridviewdragdrop',
                    pluginId: 'gridviewdragdrop',
                    dragGroup: 'registerGridDDGroup',
                    dropGroup: 'unregisterGridDDGroup',
                    dragText: 'Drag to Unregister',
                },
            },
            tbar: {
                xtype: 'container',
                padding: false,
                margin: false,
                border: false,
                width: '100%',
                frame: false,
                items: [
                    new Ext.Toolbar({
                        //padding: false,
                        margin: false,
                        border: false,
                        items:[{
                            text: 'Unregister',
                            xtype: 'button',
                            scale: 'large',
                            height: '50px',
                            handler: function(el, event) {
                                var row = me.registerPanel.getSelectionModel().getSelection()
                                if (row.length==1) {
                                    var record = row[0];
                                    me.unregisterModule(record);
                                } else {
                                    BQ.ui.error('Expecting only one row selected at a time')
                                }
                            },
                        },{
                            text: 'View<br>Module<br>Page',
                            xtype: 'button',
                            scale: 'large',
                            height: '50px',
                            handler: function() {
                                var row = me.registerPanel.getSelectionModel().getSelection()
                                if (row.length==1) {
                                    window.open('/module_service/'+row[0].get('name'))
                                } else {
                                    BQ.ui.error('Expecting only one row selected at a time')
                                }
                            },
                        },{
                            text: 'Edit<br>Module',
                            xtype: 'button',
                            scale: 'large',
                            height: '50px',
                            handler: function() {
                                var row = me.registerPanel.getSelectionModel().getSelection()
                                if (row.length==1) {
                                    window.open('/client_service/view?resource=/'+row[0].get('resource_uniq'))
                                } else {
                                    BQ.ui.error('Expecting only one row selected at a time')
                                }
                            },
                        },{ //toggles between public and private admin only?
                            text: 'Set<br>Public',
                            xtype: 'button',
                            scale: 'large',
                            height: '50px',
                            handler: function(el, event) {
                                var row = me.registerPanel.getSelectionModel().getSelection()
                                if (row.length==1) {
                                    var record = row[0];
                                    var visibility = record.get('visibility');
                                    var visibility = (visibility == 'private') ? 'published' : 'private';

                                    setButton = function() {
                                        var visibility = record.get('visibility');
                                        var text = (visibility=='published')? 'Set<br>Private': 'Set<br>Public';
                                        el.setText(text);
                                        /*
                                        if (visibility=='published') {
                                            el.setText('Set<br>Private');
                                        } else {
                                            el.setText('Set<br>Public');
                                        }*/
                                    }

                                    me.setVisibility(visibility, record, setButton);
                                } else {
                                    BQ.ui.error('Expecting only one row selected at a time')
                                }
                            },
                            onSelect: function(el, record) {
                                this.setDisabled(false)
                                var visibility = record.get('visibility')
                                if (visibility=='published') {
                                    this.setText('Set<br>Private');
                                } else {
                                    this.setText('Set<br>Public');
                                }
                            },
                        },{ //admin only not fully implemented
                            text: 'Owner: ',
                            scale: 'large',
                            height: '50px',
                            hidden: true,
                            menu: {
                                xtype: 'menu',
                                plain: true,
                                items: [{
                                    xtype: 'label',
                                    text: 'Select New Owner',
                                    padding: '15px 15px 0px 15px',
                                },{
                                    xtype: 'combo',
                                    emptyText: 'Search Users',
                                    padding: '15px 15px 10px 15px',
                                    width: '200px',
                                    displayField: 'name',
                                    valueField: 'name',
                                    store: Ext.create('Ext.data.Store',{
                                        //autoSync: false,
                                        noCache: false,
                                        proxy: {
                                            type: 'ajax',
                                            queryParam: null,
                                            limitParam: null,
                                            pageParam: null,
                                            startParam: null,
                                            url: '/admin/user',
                                            reader: {
                                                type: 'xml',
                                                root:'resource',
                                                record: 'user',
                                            }
                                        },
                                        fields: [{
                                            name: 'name',
                                            mapping: '@name',
                                        },{
                                            name: 'resource_uniq',
                                            mapping: '@resource_uniq',
                                        }],
                                    }),
                                    listeners: {
                                        select: function(el, records) {
                                            if (records.length>0) {
                                                var row = me.registerPanel.getSelectionModel().getSelection()
                                                if (row.length==1) {
                                                    var record = row[0];
                                                    var new_owner_url = '/'+records[0].get('resource_uniq');
                                                    setButton = function() {
                                                        var name = records[0].get('resource_uniq');
                                                        el.setText('Owner: '+name);
                                                    }
                                                    me.setModuleOwner(new_owner_url, record, setButton);
                                                 } else {
                                                    BQ.ui.error('Expecting only one row selected at a time');
                                                 }
                                            } else {
                                                BQ.ui.error('No records found!');
                                            }
                                        }
                                    },
                                }],
                            },
                            onSelect : function(el, record) {
                                this.setDisabled(false)
                                var owner = record.get('owner') || '';
                                this.setText('Owner: '+owner);
                            },
                        },{
                            text: 'Share',
                            xtype: 'button',
                            scale: 'large',
                            height: '50px',
                            disabled: true,
                            handler: function(el, event) {
                                var row = me.registerPanel.getSelectionModel().getSelection()
                                if (row.length==1) {
                                    var record = row[0];
                                    var uniq = record.get('resource_uniq');
                                    shareModule = function(resource) {
                                        var shareDialog = Ext.create('BQ.share.Dialog', {
                                            resource: resource,
                                        });
                                    }
                                    BQFactory.load('/'+uniq, shareModule);
                                } else {
                                    BQ.ui.error('No records found!');
                                }
                            },
                            //listeners: {},
                        },'->',{
                            text: 'Unregister<br>All',
                            xtype: 'button',
                            scale: 'large',
                            height: '50px',
                            disabled: false,
                            handler: function() {
                                var win = Ext.MessageBox.show({
                                    title: 'Unregister All',
                                    msg: 'Are you sure you want to unregister all your modules?',
                                    buttons: Ext.MessageBox.OKCANCEL,
                                    fn: function(buttonResponse) {
                                        if (buttonResponse === "ok") {
                                            me.unregisterAllModule();
                                        }
                                    },
                                });
                            },
                            listeners: { //overwrite defaults
                            },
                        },{
                            text: 'Reload',
                            xtype: 'button',
                            scale: 'large',
                            height: '50px',
                            disabled: false,
                            handler: function() {
                                me.registerPanel.reload()
                            },
                            listeners: { //overwrite defaults
                            },
                        }],
                        defaults: {
                            listeners: { //disable buttons when deselected
                                afterrender: function(el) {
                                    var buttonEl = el

                                    me.registerPanel.on('select',
                                        function(el, record) {
                                            if (buttonEl.onSelect)
                                                buttonEl.onSelect(el,record)
                                    });

                                    me.registerPanel.on('deselect',
                                        function(el, record) {
                                            if (buttonEl.onDeselect)
                                                buttonEl.onDeselect(el,record)
                                    });
                                    var store = me.registerPanel.getStore();
                                    me.registerPanel.on('reload',
                                        function(el, record) {
                                            if (buttonEl.onLoad)
                                                buttonEl.onLoad(el,record);
                                    });
                                    me.on('unregistered',
                                        function ( el, record) {
                                            if (buttonEl.onUnregister)
                                                buttonEl.onUnregister(el, record);
                                        }
                                    )
                                }
                            },
                            onSelect : function(el, record) {
                                this.setDisabled(false)
                            },
                            onDeselect: function(el, record) {
                                this.setDisabled(true);
                            },
                            onLoad: function() {
                                this.setDisabled(true);
                            },
                            onRegister: function() {
                            },
                            onUnregister: function() {
                                this.setDisabled(true);
                            },
                            disabled: true,
                        },
                    }),
                    new Ext.Toolbar({
                        padding: false,
                        margin: false,
                        border: false,
                        height: '22px',
                        items: [{
                            xtype: 'label',
                            text: 'Select a registered module to perform an operation.',
                            //textAlign: 'center',
                            style: 'margin: 5px',
                        }],
                    }),
                ]
            }
        });

        //listeners
        this.engineSearchBar.on('specialkey', function(field, e) {
            // e.HOME, e.END, e.PAGE_UP, e.PAGE_DOWN,
            // e.TAB, e.ESC, arrow keys: e.LEFT, e.RIGHT, e.UP, e.DOWN
            if (e.getKey() == e.ENTER) {
                var engine_url = field.getValue()
                if (engine_url) {
                    me.unregisterPanel.reload(engine_url);
                }
            }
        });

        this.engineSearchBar.on('select', function(el, records, eOpts) {
                var engine_url = records[0].get('field1');
                if (engine_url) {
                    me.unregisterPanel.reload(engine_url);
                }
        });

        this.engineSearchBar.on('afterrender', function() {
            /*
            function storeBind(store) {
                me.engineSearchBar.bindStore(store)
            }
            me.unregisterPanel.searchForEngines(storeBind);
            */
        });

        this.unregisterPanel.getView().on('beforedrop', function(node, data, overModel, dropPosition,  dropFunction,  eOpts){
                var record = data.records[0];
                var resource_uniq = record.get('resource_uniq');
                if (resource_uniq) { //requires a resource_uniq to unregister
                    var dropZone = me.unregisterPanel.view.getPlugin('gridviewdragdrop').dropZone;
                    dropFunction.processDrop = function () { //over write drop process
                        dropZone.invalidateDrop();
                        dropHandled = true;
                        dropZone.fireViewEvent('drop', node, data, overModel, dropPosition);
                    },
                    me.unregisterModule(record, dropFunction);
                } else {
                    BQ.ui.error('Module failed to be registered!');
                    dropFunction.cancelDrop();
                }
                dropFunction.wait = true;
            }
        );

        this.registerPanel.getView().on('beforedrop', function(node, data, overModel, dropPosition,  dropFunction,  eOpts){ //check whether the registration worked
            var record = data.records[0];
            var registration = record.get('registration');
            if (registration == 'Registered') { //checks for registration by state of the tag on the record
                BQ.ui.notification('Cannot register a module that is already registered.')
                return false //fails the drop proccess
            } else {
                me.registerModule(record, dropFunction);
                dropFunction.wait = true;
            }
        });

        var items = [
            this.registerPanel,
            this.unregisterPanel,
        ];

        Ext.apply(me, {
            items: items,
        });
        this.callParent([config]);
    },

    setVisibility: function(visibility, record, cb) {
        var me = this;
        var moduleXmlDoc = record.get('moduleXmlDoc');
        var uniq = record.get('resource_uniq');
        if (visibility && uniq && moduleXmlDoc) {
            var def_clone = moduleXmlDoc.cloneNode(true);
            def_clone.setAttribute('permission', visibility);
            def_clone.innerHTML = '';
            Ext.Ajax.request({
                disableCaching: false,
                method: 'POST',
                url: '/data_service/'+uniq,
                xmlData: new XMLSerializer().serializeToString(def_clone),
                success: function(response) {
                    var xml = response.responseXML;
                    xml  = xml.documentElement;
                    record.set('visibility', xml.attributes['permission'].value||'')
                    me.registerPanel.updateEntry(record);
                    if (cb) cb();
                },
                failure: function(response) {
                    BQ.ui.error('Failed to change visibility');
                }
            });
        }
    },

    setModuleOwner: function(new_owner_url, record, cb) {
        var me = this;
        var moduleXmlDoc = record.get('moduleXmlDoc');
        var uniq = record.get('resource_uniq');
        if (new_owner_url && uniq) { //} && definition) {
            var def_clone = moduleXmlDoc.cloneNode(true);
            def_clone.setAttribute('owner',new_owner_url);
            def_clone.innerHTML = '';
            Ext.Ajax.request({
                disableCaching: false,
                method: 'POST',
                url: '/data_service/'+uniq,
                params: {view:'deep'},
                xmlData: new XMLSerializer().serializeToString(def_clone),
                success: function(response) {
                     var xml = response.responseXML;
                     me.registerPanel.updateEntry(record);
                    if (cb) cb();
                },
                failure: function(response) {
                    BQ.ui.error('Failed to change owner');
                },
            });
        }
    },

    registerModule: function(record, dropFunction, cb) {
        var me = this;
        var definition = record.get('definition')
        if (definition) {
            Ext.Ajax.request({
                disableCaching: false,
                method: 'POST',
                url: '/module_service/register_engine',
                xmlData: new XMLSerializer().serializeToString(definition),
                success: function(response) {
                    var xml = response.responseXML;
                    var uniq = BQ.util.xpath_string(xml, '//module/@resource_uniq');
                    if (uniq) {
                        record.set('registration', 'Registered');
                        if (dropFunction) {
                            dropFunction.processDrop();
                            record = me.registerPanel.store.last();
                        } else {
                            var r = me.registerPanel.store.add(r);
                            record = r[0];
                        }

                        me.registerPanel.addEntry(uniq, record);
                        me.fireEvent('registered', me, record)
                        if (cb) cb();

                    } else {
                        if (dropFunction) {
                            dropFunction.cancelDrop();
                        }
                    }
                },
                failure: function(response) {
                    if (response.status == 405) {
                        BQ.ui.error('Only one module can be registered with that name at a time!');
                    } else {
                        BQ.ui.error('Module failed to be registered!');
                    }
                    if (dropFunction) {
                        dropFunction.cancelDrop();
                    }
                },
            })
        } else {
            BQ.ui.error('Module failed to be registered!');
            if (dropFunction) {
                dropFunction.cancelDrop();
            }
        }
    },

    unregisterModule: function(record, dropFunction, cb) {
        var me = this;
        Ext.Ajax.request({
            disableCaching: false,
            method: 'GET', //should be delete or a post, definitely not a delete
            url: '/module_service/unregister_engine/'+record.get('resource_uniq'),
            xmlData: this.moduleDefinition,
            success: function(response) {
                //nothing is added to the unregistered side, set registration status
                me.registerPanel.removeEntry(record); //remove the element from the registerPanel
                if (dropFunction) {
                    dropFunction.processDrop();
                }
                fireUnregisteredEvent = function() {
                    me.fireEvent('unregistered', me, record);
                }
                me.unregisterPanel.updateRegistration(fireUnregisteredEvent);
                if (cb) cb();
            },
            failure: function(response) {
                BQ.ui.error('Module failed to be unregistered!');
                if (dropFunction) {
                    dropFunction.cancelDrop();
                }
            },
        })
    },

    registerAllModule: function() {
        var me = this;
        this.unregisterPanel.store.each(function(record) {
            if (record.get('registration') == 'Not Registered')
                me.registerModule(record);
        });
    },

    unregisterAllModule: function() {
        var me = this;
        this.registerPanel.store.each(function(record) {
                me.unregisterModule(record);
        });
    },
});

//needs to check the user for credentials
Ext.define('BQ.module.ModuleManager', {
    extend : 'Ext.tab.Panel',
    layout: 'fit',
    border: false,
    //renderTo: Ext.getBody(),
    //tabPosition: 'left',
    //tabRotation: 90,
    initComponent: function(config) {
        var config = config || {};
        var me = this;
        var items = [{
            title: 'Manage Modules',
            layout: 'fit',
            items: [Ext.create('BQ.module.ModuleManagerMain')],
        },{ //allows for module registrations from engines
            title: 'Engine Manager',
            layout: 'fit',
            disabled: true,
            //items: [Ext.create('BQ.admin.EngineManager')],
        }, {
            title: 'Module Generator',
            disabled: true,
        }, {
            title: 'Mex Manager',
            disabled: true,
        }];

        Ext.apply(me, {
            items: items,
            //tbar: tbar,
        });
        this.callParent([config]);
    },
});