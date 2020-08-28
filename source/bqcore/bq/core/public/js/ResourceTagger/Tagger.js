Ext.define('Bisque.ResourceTagger', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.bq-tagger',
    layout: 'fit',
    silent: true,
    animate: false,

    constructor: function (config) {
        config = config || {};

        Ext.apply(this, {
            border: false,

            rootProperty: config.rootProperty || 'tags',
            autoSave: (config.autoSave == undefined) ? true : false,
            resource: {},
            editable: true,
            tree: config.tree || {
                btnAdd: true,
                btnDelete: true,
                btnImport: true,
                //btnExport : true,
            },
            store: {},
            dirtyRecords: []
        });
        this.callParent([config]);
    },

    initTagger : function() {
        if (this.fully_loaded) return;
        this.viewMgr = Ext.create('Bisque.ResourceTagger.viewStateManager', this.viewMode);
        if (!(this.viewMode in {'ReadOnly':undefined, 'GObjectTagger':undefined}))
            this.populateComboStore();
        this.setResource(this.resource);
        this.fully_loaded = true;
    },

    initComponent : function() {
        this.callParent();
        this.viewMgr = Ext.create('Bisque.ResourceTagger.viewStateManager', this.viewMode);
        if (this.full_load_on_creation)
            this.initTagger();
    },

    afterRender : function() {
        this.callParent();
        this.initTagger();
    },

    populateComboStore: function () {
        // dima - datastore for the tag value combo box
        //var TagValues = Ext.ModelManager.getModel('TagValues');
        //if (!TagValues) {
        if (!BQ || !BQ.model || !BQ.model.TagValues) {
            Ext.define('BQ.model.TagValues', {
                extend: 'Ext.data.Model',
                fields: [{ name: 'value', mapping: '@value' }],
            });
        }

        this.store_values = Ext.create('Ext.data.Store', {
            model: 'BQ.model.TagValues',
            autoLoad: false,
            autoSync: false,

            proxy: {
                noCache: false,
                type: 'ajax',
                limitParam: undefined,
                pageParam: undefined,
                startParam: undefined,

                //url : '/data_service/image?tag_values=mytag',
                url: '/core/xml/dummy_tag_values.xml', // a dummy document just to inhibit initial complaining
                reader: {
                    type: 'xml',
                    root: 'resource',
                    record: 'tag',
                },
            },

        });

        // dima - datastore for the tag name combo box
        //var TagNames = Ext.ModelManager.getModel('TagNames');
        //if (!TagNames) {
        if (!BQ || !BQ.model || !BQ.model.TagNames) {
            Ext.define('BQ.model.TagNames', {
                extend: 'Ext.data.Model',
                fields: [{ name: 'name', mapping: '@name' }],
            });
        }
        this.store_names = Ext.create('Ext.data.Store', {
            model: 'BQ.model.TagNames',
            autoLoad: true,
            autoSync: false,

            proxy: {
                noCache: false,
                type: 'ajax',
                limitParam: undefined,
                pageParam: undefined,
                startParam: undefined,

                url: '/data_service/image/?tag_names=1',
                reader: {
                    type: 'xml',
                    root: 'resource',
                    record: 'tag',
                },
            },
        });
    },

    setResource: function (resource, template) {
        var uri_params = null,
            me = this;
        this.setLoading(true);

        if (resource instanceof BQObject)
            this.loadResourceInfo(resource);
        else {
            if (!this.disableAuthTest) {
                uri_params = {view: 'deep'};
            }

            // assume it is a resource URI otherwise
            this.resource_fully_loaded = true;
            BQFactory.request({
                uri: resource,
                cb: Ext.bind(this.loadResourceInfo, this),
                errorcb: function(error) {
                    //BQ.ui.error('Error fetching resource:<br>'+error.message_short, 4000);
                    me.loadResourceInfo(new BQResource());
                },
                uri_params: uri_params,
            });
        }
    },

    loadResourceInfo: function (resource) {
        this.fireEvent('beforeload', this, resource);

        this.resource = resource;
        this.editable = false;
        if (!this.disableAuthTest)
            this.testAuth(BQApp.user, false);

        if (this.resource.tags.length > 0 || this.resource_fully_loaded === true)
            this.loadResourceTags(this.resource.tags);
        else
            this.resource.loadTags(
            {
                cb: callback(this, "loadResourceTags"),
                depth: 'deep&wpublic=1'
            });
    },

    reload: function () {
        this.setResource(this.resource.uri);
    },

    loadResourceTags: function (data, template) {
        var type = this.resource.type || this.resource.resource_type;

        // Check to see if resource was derived from a template
        if (type && type.indexOf('/data_service/') != -1 && !template && this.rootProperty != 'gobjects') {
            BQFactory.request({
                uri: this.resource.type + '?view=deep',
                cb: Ext.bind(this.initCopy, this),
                errorcb: Ext.bind(this.loadResourceTags, this, [this.resource.tags, true])
            });

            return;
        }

        this.setLoading(false);

        var root = {};
        root[this.rootProperty] = data;

        this.removeAll(true);
        //this.addDocked(this.getToolbar());
        this.add(this.getTagTree(root));

        this.fireEvent('onload', this, this.resource);
        this.relayEvents(this.tree, ['itemclick']);
        if (this.onLoaded) this.onLoaded();
    },

    initCopy: function (template) {
        var resource = this.copyTemplate(template, this.resource);
        this.resource = resource;
        this.loadResourceTags(this.resource.tags, template);
    },

    copyTemplate: function (template, resource) {
        for (var i = 0; i < resource.tags.length; i++) {
            var matchingTag = template.findTags({ attr: 'uri', value: window.location.origin + resource.tags[i].type });

            if (!Ext.isEmpty(matchingTag)) {
                matchingTag = (matchingTag instanceof Array) ? matchingTag[0] : matchingTag;
                resource.tags[i].template = matchingTag.template;
                this.copyTemplate(matchingTag, resource.tags[i]);
            }
        }

        return resource;
    },

    getTagTree: function (data) {
        this.rowEditor = Ext.create('BQ.grid.plugin.RowEditing', {
            autoCancel: false,
            clicksToEdit: 2,
            clicksToMoveEditor: 1,
            tagger: this,
            errorSummary: false,
            //triggerEvent: 'rowfocus',
            listeners: {
                'edit': this.finishEdit,
                'cancelEdit': this.cancelEdit,
                scope: this
            },

            beforeEdit: function (editor) {

                if (this.tagger.editable) {
                    this.tagger.updateQueryTagValues(editor.record.get('name'));

                    if (!isEmptyObject(editor.record.raw.template) && this.tagger.resource.resource_type != 'template') {
                        if (editor.record.raw.template.Editable) {
                            var editor = BQ.TagRenderer.Base.getRenderer({
                                tplType: editor.record.get('type'),
                                tplInfo: editor.record.raw.template,
                                valueStore: this.tagger.store_values,
                            });
                            this.tagger.tree.columns[1].setEditor(editor);
                            return true;
                        } else {
                            return false;
                        }
                    } else {
                        var editor = BQ.TagRenderer.Base.getRenderer({
                            tplType: '',
                            tplInfo: '',
                            valueStore: this.tagger.store_values,
                        });
                        this.tagger.tree.columns[1].setEditor(editor);
                    }
                }
                return this.tagger.editable;
            },
        });

        var plugins = [];
        /*plugins.push({
            ptype: 'bufferedrenderer',
        });*/

        if (this.viewMgr && this.viewMgr.state && this.viewMgr.state.editable)
            plugins.push(this.rowEditor);

        this.tree = Ext.create('Ext.tree.Panel', {
            layout: 'fit',
            flex: 2,
            useArrows: true,
            rootVisible: false,
            border: false,
            columnLines: true,
            rowLines: true,
            lines: true,
            iconCls: 'icon-grid',
            //animate: this.animate,
            animate: false,
            header: false,
            //deferRowRender: true,
            draggable: false,
            enableColumnMove: false,
            allowDeselect: true,
            //hideHeaders: this.hide_headers === true,

            store: this.getTagStore(data),
            multiSelect: true,
            tbar: this.getToolbar(),
            columns: this.getTreeColumns(),

            selModel: this.getSelModel(),
            plugins: plugins,

            /*viewConfig: {
                plugins: {
                    ptype: 'treeviewdragdrop',
                    allowParentInserts: true,
                }
            },*/
            listeners: {
                scope: this,
                select: function ( tree, record, index, eOpts) {
                    this.fireEvent('select', this, record, index, eOpts);
                },
                deselect: function ( tree, record, index, eOpts) {
                    this.fireEvent('deselect', this, record, index, eOpts);
                },
                checkchange: function (node, checked) {
                    if (!(node.raw instanceof BQObject) && !node.raw.loaded && this.onExpand) {
                        this.onExpand(node);
                        return;
                    }

                    this.fireEvent(checked ? 'checked' : 'unchecked', this, node);
                },
                itemcontextmenu: function( me, record, item, index, e, eOpts ) {
                    e.stopEvent();
                    if (this.onmenucontext) this.onmenucontext(me, record, item, index, e, eOpts);
                        //this.menu_context.showAt(e.getXY());
                },
                cellkeydown : function(me, td, cellIndex, record, tr, rowIndex, e) {
                    if (e.keyCode === 46) {
                        console.log('hit delete');
                        this.onDeleteElement();
                    }
                },
            }
        });


        this.store.tagTree = this.tree;

        return this.tree;
    },

    getSelModel: function () {
        return null;
    },

    updateQueryTagValues: function (tag_name) {
        var proxy = this.store_values.getProxy();
        proxy.url = '/data_service/'+this.resource.resource_type+'?tag_values=' + encodeURIComponent(tag_name);
        this.store_values.load();
    },

    getTreeColumns: function () {
        var clmn = [{
            xtype: 'treecolumn',
            dataIndex: 'name',
            text: this.colNameText || 'Name',
            flex: 0.8,
            sortable: true,
            draggable: false,

            field: {
                // dima: combo box instead of the normal text edit that will be populated with existing tag names
                xtype: 'bqcombobox',
                tabIndex: 0,

                store: this.store_names,
                displayField: 'name',
                valueField: 'name',
                queryMode: 'local',

                allowBlank: false,
                //fieldLabel: this.colNameText || 'Name',
                //labelAlign: 'top',

                validateOnChange: false,
                blankText: 'Tag name is required!',
                msgTarget: 'none',
                listeners: {
                    'change': {
                        fn: function (field, newValue, oldValue, eOpts) {
                            this.updateQueryTagValues(newValue);
                            if (this.rowEditor)
                                this.rowEditor.editor.onFieldChange();
                        },
                        buffer: 250,
                    },

                    scope: this,
                },
            },
            renderer: function(value, meta, record) {
                if (record && record.raw && record.raw instanceof BQGObject) {
                    var g = record.raw,
                       c = g.getColor();
                    if (c.r===255 && c.g===255 && c.b===255 ) {
                        c.r = 0; c.g = 0; c.b = 0;
                    }
                    meta.style = 'color: '+BQGObject.color_rgb2html(c)+';';
                }
                return value;
            },
        }];
        if (!this.hide_value) {
            clmn.push({
                text: this.colValueText || 'Value',
                itemId: 'colValue',
                dataIndex: 'value',
                flex: 1,
                sortable: true,
                editor: {
                    xtype : 'bqcombobox',
                    valueStore: this.store_values,
                    allowBlank: false,
                },
                renderer: Bisque.ResourceTagger.BaseRenderer,
            });
        }
        return clmn;
    },

    getTagStore: function (data) {
        this.store = Ext.create('Ext.data.TreeStore',
        {
            defaultRootProperty: this.rootProperty,
            root: data,
            //lazyFill: true, // dima: may not be working in teh current config

            fields: [
            {
                name: 'name',
                type: 'string',
                convert: function (value, record) {
                    // dima: show type and name for gobjects
                    if (record.raw instanceof BQGObject) {
                        var txt = [];
                        if (record.raw.type && record.raw.type != 'gobject') txt.push(record.raw.type);
                        if (record.raw.name) txt.push(record.raw.name);
                        if (txt.length > 0) return txt.join(': ');
                    }
                    return value || record.data.type;
                }
            },
            {
                name: 'value',
                type: 'string',
                convert: function (value, record) {
                    var valueArr = [];

                    if (record.raw instanceof BQObject)
                        if (!Ext.isEmpty(record.raw.values) && !record.editing)
                            for (var i = 0; i < record.raw.values.length; i++)
                                valueArr.push(record.raw.values[i].value);

                    if (!Ext.isEmpty(value))
                        valueArr.unshift(value);

                    return valueArr.join(", ");
                }
            },
            {
                name: 'type',
                type: 'string'
            },
            {
                name: 'iconCls',
                type: 'string',
                convert: Ext.bind(function (value, record) {
                    var o = record.raw;
                    if (!o)
                        return 'icon-folder';

                    if (o instanceof BQGObject) {
                        if (o.resource_type in BQGObject.primitives || o.type in BQGObject.primitives)
                            return 'icon-gobject';
                        else
                            return 'icon-folder';
                    } else if (o instanceof BQObject) {
                        if (o.tags.length > 0)
                            return 'icon-folder';
                    }
                    return 'icon-tag';
                }, this)

            },
            {
                name: 'qtip',
                type: 'string',
                convert: this.getTooltip
            }, this.getStoreFields()],

            indexOf: function (record) {
                return this.tagTree.getView().indexOf(record);
            },

            applyModifications: function () {
                var nodeHash = this.tree.nodeHash, status = false, valueArr;

                for (var node in nodeHash)
                    if (nodeHash[node].dirty) {
                        status = true;

                        if (nodeHash[node].raw.values && nodeHash[node].raw.values.length > 0) { // parse csv to multiple value elements
                            valueArr = nodeHash[node].get('value').split(',');
                            nodeHash[node].raw.values = [];

                            for (var i = 0; i < valueArr.length; i++)
                                nodeHash[node].raw.values.push(new BQValue('string', valueArr[i].trim()));

                            Ext.apply(nodeHash[node].raw, { 'name': nodeHash[node].get('name'), 'value': undefined });
                            delete nodeHash[node].raw.value;
                        } else {
                            Ext.apply(nodeHash[node].raw, { 'name': nodeHash[node].get('name'), 'value': nodeHash[node].get('value') });
                        }

                        nodeHash[node].commit();
                    }

                if (this.getRemovedRecords().length > 0)
                    return true;

                return status;
            },

            /* Modified function so as to not delete the root nodes */
            onNodeAdded: function (parent, node) {
                var me = this,
                    proxy = me.getProxy(),
                    reader = proxy.getReader(),
                    data = node.raw || node[node.persistenceProperty],
                    dataRoot;

                Ext.Array.remove(me.removed, node);

                if (!node.isLeaf()) {
                    dataRoot = reader.getRoot(data);
                    if (dataRoot) {
                        me.fillNode(node, reader.extractData(dataRoot));
                        //delete data[reader.root];
                    }
                }

                if (me.autoSync && !me.autoSyncSuspended && (node.phantom || node.dirty)) {
                    me.sync();
                }
            }
        });

        return this.store;
    },

    getTooltip: function (value, record) {
        if (record.raw instanceof BQGObject) {
            var txt = [];
            if (record.raw.type && record.raw.type != 'gobject') txt.push(record.raw.type);
            if (record.raw.name) txt.push(record.raw.name);
            if (txt.length > 0) return txt.join(' : ');
        }

        return Ext.String.htmlEncode(record.data.name + ' : ' + record.data.value);
    },

    getStoreFields: function () {
        return { name: 'dummy', type: 'string' };
    },

    getToolbar: function () {
        var tbar = [
        {
            xtype: 'buttongroup',
            itemId: 'grpAddDelete',
            hidden: (this.viewMgr.state.btnAdd && this.viewMgr.state.btnDelete),
            items: [
            {
                itemId: 'btnAdd',
                text: 'Add',
                hidden: this.viewMgr.state.btnAdd,
                scale: 'small',
                iconCls: 'icon-add',
                handler: this.addTags,
                disabled: this.tree.btnAdd,
                scope: this
            },
            {
                itemId: 'btnDelete',
                text: 'Delete',
                hidden: this.viewMgr.state.btnDelete,
                scale: 'small',
                iconCls: 'icon-delete',
                handler: this.deleteTags,
                disabled: this.tree.btnDelete,
                scope: this
            }]
        },
        {
            xtype: 'buttongroup',
            itemId: 'grpImportExport',
            hidden: (this.viewMgr.state.btnImport && this.viewMgr.state.btnExport),
            items: [
            {
                itemId: 'btnImport',
                text: 'Import',
                hidden: this.viewMgr.state.btnImport,
                scale: 'small',
                iconCls: 'icon-import',
                handler: this.importMenu,
                disabled: this.tree.btnImport,
                scope: this
            },
            {
                text: 'Export',
                scale: 'small',
                hidden: this.viewMgr.state.btnExport,
                disabled: this.tree.btnExport,
                iconCls: 'icon-export',
                menu:
                {
                    items: [
                    {
                        text: 'as XML',
                        handler: this.exportToXml,
                        hidden: this.viewMgr.state.btnXML,
                        scope: this
                    },
                    {
                        text: 'as CSV',
                        handler: this.exportToCsv,
                        hidden: this.viewMgr.state.btnCSV,
                        scope: this
                    },
                    {
                        text: 'to Google Docs',
                        handler: this.exportToGDocs,
                        hidden: true,//this.viewMgr.state.btnGDocs,
                        scope: this
                    }]
                }
            }]
        },
        {
            xtype: 'buttongroup',
            hidden: (this.viewMgr.state.btnSave || this.autoSave),
            items: [
            {
                text: 'Save',
                hidden: this.viewMgr.state.btnSave || this.autoSave,
                scale: 'small',
                iconCls: 'icon-save',
                handler: this.saveTags,
                scope: this
            }]
        }, {
            xtype:'tbtext',
            itemId: 'toolbar_progress',
            cls: 'bq_tagger_progress',
            flex: 2,
            //text: 'Saving',
        }];

        return tbar;
    },

    setProgress: function(msg) {
        var p = this.queryById('toolbar_progress');
        if (!p) return;
        if (msg === undefined || msg === false) {
            p.setText('');
            p.removeCls('bq_inprogress');
        } else {
            p.setText(msg);
            p.addCls('bq_inprogress');
        }
    },

    addTags: function () {
        var currentItem = this.tree.getSelectionModel().getSelection();
        var editor = this.rowEditor || this.tree.plugins[1];

        if (currentItem.length)// None selected -> add tag to parent document
            currentItem = currentItem[0];
        else
            currentItem = this.tree.getRootNode();

        // Adding new tag to tree
        var child = { name: this.defaultTagName || '', value: this.defaultTagValue || '' };
        child[this.rootProperty] = [];

        var newNode = currentItem.appendChild(child);
        this.newNode = newNode;
        currentItem.expand();
        editor.startEdit(newNode, 0);
    },

    cancelEdit: function (grid, eOpts) {
        if (eOpts.record && eOpts.record.dirty) {
            eOpts.record.parentNode.removeChild(eOpts.record);
        }
    },

    finishEdit: function (_editor, me) {
        if (me.record.raw instanceof BQObject) {
            if (this.autoSave) {
                this.saveTags(me.record.raw);
                me.record.data.qtip = this.getTooltip('', me.record);
                me.record.commit();
            }

            return;
        }

        this.editing = true;
        var newTag = new BQTag();

        newTag = Ext.apply(newTag,
        {
            name: me.record.data.name,
            value: me.record.data.value,
        });

        var parent = (me.record.parentNode.isRoot()) ? this.resource : me.record.parentNode.raw;
        parent.addtag(newTag);

        if (this.isValidURL(newTag.value)) {
            newTag.type = 'link';
            me.record.data.type = 'link';
        }

        if (this.autoSave)
            this.saveTags(parent, undefined, newTag);

        me.record.raw = newTag;
        me.record.loaded = true;
        me.record.data.qtip = this.getTooltip('', me.record);
        me.record.commit();

        //me.record.parentNode.data.iconCls = 'icon-folder';
        me.view.refresh();

        this.editing = false;
    },

    onDeleteElement: function () {
        this.deleteTags();
    },

    deleteTags: function () {
        var selectedItems = this.tree.getSelectionModel().getSelection(), parent;

        var cb = Ext.bind(function () {
            this.tree.setLoading(false);
        }, this);

        if (selectedItems.length) {
            this.tree.setLoading(true);

            for (var i = 0; i < selectedItems.length; i++) {
                parent = (selectedItems[i].parentNode.isRoot()) ? this.resource : selectedItems[i].parentNode.raw;
                parent.deleteTag(selectedItems[i].raw, cb, cb);

                if (selectedItems[i].parentNode.childNodes.length <= 1)
                    selectedItems[i].parentNode.data.iconCls = 'icon-tag';

                selectedItems[i].parentNode.removeChild(selectedItems[i], true);
            }

            BQ.ui.notification(selectedItems.length + ' record(s) deleted!');
            this.tree.getSelectionModel().deselectAll();
        }
    },

    saveTags: function (parent, silent) {
        if (silent === undefined)
            silent = this.silent !== undefined ? this.silent : false;

        var resource = (typeof parent == BQObject) ? parent : this.resource;
        var me = this;
        if (this.store.applyModifications()) {
            this.setProgress('Saving');
            resource.save_(
                undefined,
                function() { me.ondone('Changes were saved successfully!', silent); },
                callback(this, 'onerror')
            );
        } else
            BQ.ui.notification('No records modified!');
    },

    ondone : function(message, silent) {
        this.setProgress(false);
        if (!silent) BQ.ui.notification(message);
    },

    onerror : function(error) {
        this.setProgress(false);
        BQ.ui.error(error.message);
    },

    importMenu: function (btn, e) {
        if (!btn.menu) {
            var menuItems = [];

            for (var i = 0; i < BQApp.resourceTypes.length; i++) {
                menuItems.push({
                    text: 'from <b>' + BQApp.resourceTypes[i].name + '</b>',
                    name: '/data_service/' + BQApp.resourceTypes[i].name,
                    handler: this.importTags,
                    scope: this
                });
            }

            btn.menu = Ext.create('Ext.menu.Menu', {
                items: menuItems
            });
        }

        btn.showMenu();
    },

    importTags: function (menuItem) {
        var met = this,
        rb = new Bisque.ResourceBrowser.Dialog(
        {
            height: '85%',
            width: '85%',
            dataset: menuItem.name,
            viewMode: 'ViewerLayouts',
            selType: 'SINGLE',
            original: this.resource,
            offline:  this.viewMode === "Offline",
            listeners:
            {
                'Select': function (me, resource) {
                    if (resource instanceof BQTemplate) {
                        function applyTemplate(response) {
                            if (response == 'yes')
                                //BQ.TemplateManager.createResource({ name: '', noSave: true }, Ext.bind(this.onResourceCreated, this), resource.uri + '?view=deep');
                                BQ.TemplateManager.createResource({ name: '', noSave: (me.offline === true), }, function(R, T) {
                                    if (me.offline !== true) {
                                        location.reload();
                                    } else {
                                        met.onResourceCreated(R, T);
                                    }
                                }, me.original, resource.uri);
                        }

                        if (this.resource.type)
                            Ext.MessageBox.confirm('Reapply template', 'This resource is already templated. Do you wish to reapply selected template?', Ext.bind(applyTemplate, this));
                        else
                            applyTemplate.apply(this, ['yes']);
                    }
                    else
                        resource.loadTags(
                        {
                            cb: callback(this, "appendTags"),
                        });
                },

                scope: this
            },
        });
    },

    onResourceCreated: function (resource, template) {
        if (resource.type === this.resource.type)
            this.mergeTags(resource.tags);
        else {
            this.resource.type = resource.type;
            this.appendTags(resource.tags);
        }

        var R = this.copyTemplate(template, this.resource),
            RR = resource.clone(true);
        R.gobjects = R.gobjects.concat(RR.gobjects);
        this.resource = R;
    },

    mergeTags: function (data) {
        this.tree.setLoading(true);

        if (data.length > 0) {
            var cleanData = this.stripURIs(data);

            for (var i = 0; i < data.length; i++) {
                var matchingTag = this.resource.findTags({ attr: 'type', value: data[i].type });

                if (Ext.isEmpty(matchingTag)) {
                    this.resource.tags.push(cleanData[i]);
                    this.addNode(this.tree.getRootNode(), cleanData[i]);
                }
            }

            if (this.autoSave)
                this.saveTags(null);
        }

        this.tree.setLoading(false);
    },

    appendTags: function (data) {
        this.tree.setLoading(true);

        if (data.length > 0) {
            data = this.stripURIs(data);
            var currentItem = this.tree.getSelectionModel().getSelection();

            if (currentItem.length) {
                currentItem = currentItem[0];
                currentItem.raw.tags = currentItem.raw.tags.concat(data);
            }
            else {
                currentItem = this.tree.getRootNode();
                if (this.resource.tags)
                    this.resource.tags = this.resource.tags.concat(data);
            }

            this.addNode(currentItem, data);
            currentItem.expand();

            if (this.autoSave)
                this.saveTags(null);
        }

        this.tree.setLoading(false);
    },

    stripURIs: function (tagDocument) {
        var treeVisitor = Ext.create('Bisque.ResourceTagger.OwnershipStripper');
        treeVisitor.visit_array(tagDocument);
        return tagDocument;
    },

    updateNode: function (loaded, node, data) {
        if (!loaded)
            node.raw.loadTags(
            {
                cb: callback(this, "updateNode", true, node),
                depth: 'full'
            });
        else
            for (var i = 0; i < data.length; i++)
                if (data[i].uri != node.childNodes[i].raw.uri)
                    // Assuming resources come in order
                    alert('Tagger::updateNode - URIs not same!');
                else
                    this.addNode(node.childNodes[i], data[i][this.rootProperty]);
    },

    addNode: function (parent, children) {
        if (!(children instanceof Array))
            children = [children];
        var newnode = undefined;
        for (var i = 0; i < children.length; i++) {
            var node = Ext.ModelManager.create(children[i], this.store.model);
            //Ext.data.NodeInterface.decorate(node); // dima: apparently should not be applied top a child but to a model
            node.raw = children[i];
            newnode = parent.appendChild(node);
            //parent.data.iconCls = 'icon-folder';
        }
        //this.tree.getView().refresh(); // dima: tree is reloaded automatically
        return newnode;
    },

    testAuth: function (user, loaded, permission) {
        if (user) {
            if (!loaded)
                this.resource.testAuth(user.uri, Ext.bind(this.testAuth, this, [user, true], 0));
            else {
                if (permission) {
                    // user is authorized to edit tags
                    this.tree.btnAdd = false;
                    this.tree.btnDelete = false;
                    this.tree.btnImport = false;

                    this.editable = true;

                    if (this.tree instanceof Ext.Component) {
                        var tbar = this.tree.getDockedItems('toolbar')[0];

                        tbar.getComponent('grpAddDelete').getComponent('btnAdd').setDisabled(false);
                        tbar.getComponent('grpAddDelete').getComponent('btnDelete').setDisabled(false);
                        tbar.getComponent('grpImportExport').getComponent('btnImport').setDisabled(false);
                    }
                }
            }
        }
        else if (user === undefined) {
            // User autentication hasn't been done yet
            BQApp.on('gotuser', Ext.bind(this.testAuth, this, [false], 1));
        }
    },

    isValidURL: function (url) {
        var pattern = /(ftp|http|https):\/\/(\w+:{0,1}\w*@)?(\S+)(:[0-9]+)?(\/|\/([\w#!:.?+=&%@!\-\/]))?/;
        return pattern.test(url);
    },

    exportToXml: function () {
        var url = '/export/stream?urls=';
        url += encodeURIComponent(this.resource.uri + '?view=deep');
        url += '&filename=' + (this.resource.name || 'document');

        window.open(url);
    },

    exportToCsv: function () {
        var url = '/stats/csv?url=';
        url += encodeURIComponent(this.resource.uri);
        url += '&xpath=%2F%2Ftag&xmap=tag-name-string&xmap1=tag-value-string&xreduce=vector';
        url += '&title=Name&title1=Value';
        url += '&filename=' + (this.resource.name || 'document') + '.csv';
        window.open(url);
    },

    exportToGDocs: function () {
        var url = '/export/to_gdocs?url=' + encodeURIComponent(this.resource.uri);
        window.open(url);
    },
});

//-----------------------------------------------------------------------
// Bisque.GObjectTagger
// events:
// gob_projection
//-----------------------------------------------------------------------
Ext.define('Bisque.GObjectTagger', {
    extend: 'Bisque.ResourceTagger',
    alias: 'widget.bq-tagger-gobs',
    animate: false,
    layout: 'fit',
    cls: 'bq-gob-tagger',

    requires: ['Ext.Date'],

    colNameText: 'Type:Name',
    //colValueText: 'Vertices',
    hide_value: true,
    hide_headers: true,

    constructor: function (config) {
        config.rootProperty = 'gobjects';
        config.tree = { btnExport: true, };
        this.callParent(arguments);
    },

    initComponent : function() {
        this.callParent();
    },

    afterRender : function() {
        this.callParent();
        this.showChildrenCount();
        this.tree.on('itemappend', this.showChildrenCount, this );
        this.tree.on('iteminsert', this.showChildrenCount, this );
        this.tree.on('itemremove', this.showChildrenCount, this );
        this.tree.on('selectionchange', this.showChildrenCount, this );
    },

    loadResourceTags: function (data, template) {
        this.callParent(arguments);
        this.store.on('beforeexpand', this.onExpand, this );
    },

    onLoaded: function () {
        this.tree.addDocked([/*{
            xtype: 'gobspanel',
            itemId: 'panelGobTypes',
            title: 'Graphical annotations',
            collapsible: true,
            border: 0,
            dock: 'top',
            height: 300,
            //flex: 1,
            listeners: {
                scope: this,
                select: this.fireGobEvent,
            }
        }, */{
            xtype: 'tbtext',
            cls: 'bq-gob-header',
            itemId: 'GobsHeader',
            text: '<h3>Tree of annotations</h3>',
            border: 0,
            dock: 'top',
        },{
            xtype: 'toolbar',
            cls: 'bq-gob-toolbar',
            itemId: 'AnnoToolbar',
            border: 0,
            dock: 'top',
            items: [{
                //xtype: 'splitbutton',
                arrowAlign: 'right',
                text: 'Visibility',
                scale: 'medium',
                iconCls: 'icon-check',
                //handler: this.toggleCheckTree,
                checked: true,
                scope: this,
                menu: {
                    plain: true,
                    items: [{
                        xtype:'tbtext',
                        text: 'Visibility',
                        indent: true,
                        cls: 'menu-heading',
                    }, {
                        text: 'Toggle each',
                        handler: function() {this.toggleCheck(); },
                        scope: this,
                    }, {
                        text: 'Check all',
                        handler: function() {this.toggleCheck('checked'); },
                        scope: this,
                    }, {
                        text: 'Uncheck all',
                        handler: function() {this.toggleCheck('unchecked'); },
                        scope: this,
                    }, {
                        xtype:'tbtext', text: 'Projections',
                        indent: true,
                        cls: 'menu-heading',
                    }, {
                        itemId: 'projectionNone',
                        text: 'Project none',
                        handler: this.onProjection,
                        scope: this,
                        group: 'projections',
                        checked: true,
                        projection: 'none',
                    }, {
                        itemId: 'projectionAll',
                        text: 'Project all',
                        handler: this.onProjection,
                        scope: this,
                        group: 'projections',
                        checked: false,
                        projection: 'all',
                    }, {
                        itemId: 'projectionT',
                        text: 'Project all for current T',
                        handler: this.onProjection,
                        scope: this,
                        group: 'projections',
                        checked: false,
                        projection: 'Z',
                    }, {
                        itemId: 'projectionZ',
                        text: 'Project all for current Z',
                        handler: this.onProjection,
                        scope: this,
                        group: 'projections',
                        checked: false,
                        projection: 'T',
                    }, '-', {
                        itemId: 'gobTolerance',
                        text: 'Set projection tolerance (in planes)',
                        handler: this.onGobTolerance,
                        scope: this,
                    }, '-', {
                        xtype:'tbtext',
                        text: 'Coloring',
                        indent: true,
                        cls: 'menu-heading',
                    }, {
                        itemId: 'coloring_class',
                        text: 'Class name',
                        handler: this.onColoring,
                        scope: this,
                        group: 'coloring',
                        checked: true,
                        coloring: 'class',
                    }, {
                        itemId: 'coloring_confidence',
                        text: 'Confidence',
                        handler: this.onColoring,
                        scope: this,
                        group: 'coloring',
                        checked: false,
                        coloring: 'confidence',
                    }/*, '-', {
                        itemId: 'coloring_tag',
                        text: 'Set confidence tag name',
                        handler: this.onColoringTag,
                        scope: this,
                    }*/]
                }
            }, {
                itemId: 'btnCreateFolder',
                text: 'Add',
                scale: 'medium',
                iconCls: 'icon-add-folder',
                handler: this.createGroupGob,
                scope: this,
                tooltip: 'Add a new group graphical object into the tree',
            },{
                itemId: 'btnDeleteSelected',
                text: 'Delete',
                scale: 'medium',
                iconCls: 'icon-trash',
                handler: this.deleteSelectedGobs,
                scope: this,
                tooltip: 'Delete selected annotations in the tree',
            },{
                itemId: 'btnColorSelected',
                text: 'Color',
                scale: 'medium',
                iconCls: 'icon-color-picker ',
                handler: this.onColorSelectedGobs,
                scope: this,
                tooltip: 'Select color for selected annotations in the tree',
            },{
                itemId: 'btnStatsSelected',
                text: 'Stats',
                scale: 'medium',
                iconCls: 'icon-stats',
                scope: this,
                tooltip: 'Compute statistics for selected annotations in the tree',
                menu: [{
                    text: 'Counts',
                    handler: function(){ this.onStats('counts'); },
                    scope: this,
                },{
                    text: 'Perimeter',
                    handler: function(){ this.onStats('perimeter'); },
                    scope: this,
                },{
                    text: 'Area',
                    handler: function(){ this.onStats('area'); },
                    scope: this,
                }],
            }],
        }]);
    },

    loadResourceInfo: function (resource) {
        this.fireEvent('beforeload', this, resource);

        this.resource = resource;
        // dima: the following should never happen because we only load gobtagger in full page and image is pre-loaded view-deep
        if (!this.resource.gobjects || this.resource.gobjects.length<=0) {
            this.resource.loadGObjects({
                cb: callback(this, "loadResourceTags"),
                depth: 'deep&wpublic=1'
            });
        } else {
            this.loadResourceTags(this.resource.gobjects);
        }
    },

    getStoreFields: function () {
        return {
            name: 'checked',
            type: 'bool',
            defaultValue: true
        };
    },

    onDeleteElement: function () {
        this.deleteSelectedGobs();
    },

    getToolbar: function () {
        this.viewMgr.state.btnImport = true;
        this.viewMgr.state.btnExport = true;
        var toolbar = this.callParent(arguments);
        return [];
        /*var buttons = [{
            itemId: 'btnCreate',
            text: 'Create custom',
            scale: 'medium',
            iconCls: 'icon-add',
            handler: this.createComplexGobject,
            scope: this,
            tooltip: 'Create a new custom graphical annotation wrapping any primitive annotation',
        }];

        return buttons.concat(toolbar);*/
    },

    toggleCheckTree: function (button) {
        button.checked = !button.checked;
        button.check = button.checked;
        button.setIconCls(button.checked ? 'icon-check' : 'icon-uncheck');
        this.toggleCheck(button.checked ? 'checked' : 'unchecked');
    },

    toggleCheck: function (mode) {
        var sel = this.tree.getSelectionModel().getSelection();
        if (sel.length<=1)
            sel = this.tree.getRootNode().childNodes;
        var r=undefined;
        for (var i=0; (r=sel[i]); i++) {
            if (mode === undefined)
                r.set('checked', !r.get('checked'));
            else
                r.set('checked', mode === 'checked');
            this.fireEvent(r.get('checked') ? 'checked' : 'unchecked', this, r);
        }
    },

    findGObjects: function (resource, imageURI) {
        if (resource.value && resource.value == imageURI)
            return resource.gobjects;

        var gobjects = null;
        var t = null;
        for (var i = 0; (t = resource.tags[i]) && !gobjects; i++)
            gobjects = this.findGObjects(t, imageURI);

        return gobjects;
    },

    findNodeByGob: function (gob) {
        return this.tree.getRootNode().findChildBy(
            function(n) { if (n.raw === gob) return true; },
            this,
            true
        );
    },

    deleteGObject: function (gob) {
        var node = this.findNodeByGob(gob);
        if (node)
            node.remove();
    },

    appendMex: function (mex) {
        if (!mex || mex.value !== 'FINISHED') return;
        var parent = this.tree.getRootNode(),
            dt = Ext.Date.parse(mex.ts, BQ.Date.patterns.BisqueTimestamp);
        parent.insertChild(0, {
            name: mex.name + ' ('+Ext.Date.format(dt, BQ.Date.patterns.ISO8601Long)+')',
            //value: Ext.Date.format(dt, BQ.Date.patterns.ISO8601Long),
            mex_uri: mex.uri,
            gobjects: [false],
            checked: false,
            expandable: true,
            expanded: false,
            leaf: false,
            loaded: false,
        });
    },

    appendGObject: function (gob) {
        parent = gob.parent;
        var parent_node = this.findNodeByGob(parent);
        if (!parent_node)
            parent_node = this.tree.getRootNode();

        var node = Ext.ModelManager.create(gob, this.store.model);
        node.raw = gob;
        return parent_node.appendChild(node);
    },

    exportToXml: function () {
        //var gobject=this.tree.getRootNode(), selection = this.tree.getChecked();
        //debugger
        //this.exportTo('xml');
    },

    //exportToGDocs : Ext.emptyFn,

    exportToCsv: function () {
        //this.exportTo('csv');
    },

    exportTo: function (format) {
        format = format || 'csv';

        var gobject, selection = this.tree.getChecked();
        this.noFiles = 0, this.csvData = '';

        function countGObjects(node, i) {
            if (node.raw)
                this.noFiles++;
        }

        selection.forEach(Ext.bind(countGObjects, this));

        for (var i = 0; i < selection.length; i++) {
            gobject = selection[i].raw;

            if (gobject) {
                Ext.Ajax.request({
                    url: gobject.uri + '?view=deep&format=' + format,
                    success: Ext.bind(this.saveCSV, this, [format], true),
                    disableCaching: false
                });
            }
        }
    },

    saveCSV: function (data, params, format) {
        this.csvData += '\n' + data.responseText;
        this.noFiles--;

        if (!this.noFiles)
            location.href = "data:text/attachment," + encodeURIComponent(this.csvData);
    },

    updateViewState: function (state) {

    },

    fireButtonEvent: function (button) {
        this.fireEvent(button.eventName, this);
    },

    fireGobEvent: function (type) {
        this.fireEvent('createGob', type, this);
    },

    createComplexGobject: function () {
        Ext.MessageBox.prompt('Create graphical annotation', 'Please enter a new graphical type:', this.onNewType, this);
    },

    onNewType: function (btn, mytype) {
        if (btn !== 'ok') return;
        var p = this.queryById('panelGobTypes');
        if (p)
            p.addType(mytype);
    },

    deselectGobCreation: function () {
        var p = this.queryById('panelGobTypes');
        if (p) p.deselect();
    },


    deselectAll: function () {
        this.tree.getSelectionModel().deselectAll();
    },

    onExpand: function(node, eOpts) {
        var me = this;
        function callOnMexLoaded(mex) {
            me.onMexLoaded( mex, node );
        };

        if (node.isRoot()) return;
        if (node.raw && node.raw.loaded === false && node.raw.mex_uri) {
            node.data.gobjects = undefined;
            node.removeAll();
            node.set('loading', true);
            BQFactory.request({
                uri : node.raw.mex_uri + '?view=deep',
                cb : Ext.bind(callOnMexLoaded, this)
            });
        }
    },

    onMexLoaded: function(mex, node) {
        // load sub-mexs
        if (mex.children.length>0) {
            var m=undefined;
            for (var i=0; (m=mex.children[i]); i++) {
                this.onMexLoaded(m, node);
            }
            return;
        }

        // load single mex
        node.raw.loaded = true;
        node.raw.uri = mex.uri;
        node.raw.gobjects = [];
        node.raw.parent = undefined;
        node.raw.children = [];
        node.raw.tags = [];
        node.raw.getkids = BQObject.prototype.getkids;

        node.set('checked', true);
        node.set('loading', false);

        if (!mex.outputs || mex.outputs.length<=0) return;
        var o=undefined;
        for (var i=0; (o=mex.outputs[i]); i++) {
            if (o.gobjects.length>0 && o.value === this.resource.uri) {
                //this.addNode(node, { name: 'outputs', value: '', gobjects: o.gobjects }); // dima: future, show both inputs and outputs
                var gobs = o.gobjects;
                var name = o.name;
                var value = '';
                var uri   = o.uri;
                node.raw.gobjects.push.apply(node.raw.gobjects, gobs);

                // if there's only one child gobject it's probably a wrapper
                if (o.gobjects.length===1) {
                    gobs = o.gobjects[0].gobjects;
                    name = o.gobjects[0].type;
                    value = o.gobjects[0].value;
                    uri   = o.gobjects[0].uri;
                }
                // append an imitation of a gobject
                var g = {
                    name: name,
                    value: value,
                    gobjects: gobs,
                    uri: uri,
                    //parent: mex,
                    parent: undefined,
                    children: [],
                    tags: [],
                    getkids: BQObject.prototype.getkids,
                    loaded: true,
                };
                node.raw.gobjects.push(g);
                this.addNode(node, g);
            }
        }
        if (node.raw.gobjects.length>0)
            this.fireEvent('onappend', this, node.raw.gobjects);
    },

    createGroupGob: function() {
        Ext.MessageBox.prompt('Create a group of graphical annotations', 'Please enter a group name:', this.onNewGroupGob, this);
    },

    onNewGroupGob: function (btn, name) {
        if (btn !== 'ok') return;
        var sel = this.tree.getSelectionModel().getSelection();
        var parent = (sel.length<1) ? this.tree.getRootNode() : sel[0];
        var g_parent = (sel.length<1) ? undefined : parent.raw;

        var g = new BQGObject (name);
        g.name = name;
        if (g_parent)
            g_parent.addgobjects(g);

        var node = this.addNode(parent, [g]);
        this.tree.expandNode( parent );
        this.tree.getSelectionModel().select(node);
        //this.viewerContainer.viewer.set_parent_gobject(gobject); // selection activates this
        this.fireEvent('create_gobject', g);
    },

    deleteSelectedGobs: function() {
        var sel = this.tree.getSelectionModel().getSelection();
        if (sel.length<1) {
            BQ.ui.notification('You first need to select some annotations in the tree...');
            return;
        }
        var gobs = [];
        var r=undefined;
        for (var i=0; (r=sel[i]); i++) {
            gobs.push(r.raw);
            //this.deleteGObject(r.raw);
        }
        this.tree.getSelectionModel().deselectAll();
        this.fireEvent('delete_gobjects', gobs);
    },

    onmenucontext: function( me, record, item, index, e, eOpts ) {
        this.selectColor(item);
    },

    selectColor: function(el) {
        //this.menu_context.showAt(e.getXY());
        var w = 540;
        var h = 85;
        Ext.create('Ext.tip.ToolTip', {
            target: el,
            anchor: 'left',
            cls: 'bq-viewer-tip',
            width :  w,
            minWidth: w,
            //maxWidth: w,
            //height:  h,
            minHeight: h,
            autoDestroy: true,
            layout: 'fit',
            autoHide: false,
            shadow: false,
            items: [{
                xtype: 'bqcolorpicker',
                //width :  500,
                //height:  100,
                listeners: {
                    select: function(picker, selColor) {
                        this.onColorSelected(picker, selColor);
                    },
                    hide: function(e){
                        this.close();
                    },
                    scope: this,
                },
                colors : [ '000000', // trasparent
                           'FF0000', '00FF00', '0000FF', // RGB
                           'FFFFFF', // GRAY
                           '00FFFF', // CYAN
                           'FF00FF', // MAGENTA
                           'FFFF00', // YELLOW
                           'FF6600'  // custom orange
                ],
                titles : [ 'Default', // trasparent
                           'Red', 'Green', 'Blue', // RGB
                           'Gray', //GRAY
                           'Cyan', 'Magenta', 'Yellow', // YMC
                           'Custom' // custom orange
                ],
            }],
        }).show();
    },

    onColorSelected: function(picker, color) {
        var gobs = [];
        var sel = this.tree.getSelectionModel().getSelection();
        if (sel.length<1) return;
        var view = this.tree.getView();
        var r=undefined;
        for (var i=0; (r=sel[i]); i++) {
            if (!r.raw.getkids) {
                BQ.ui.notification('Annotations are not yet loaded in the tree. Expand to load first...');
                continue;
            }
            gobs.push(r.raw);
            var node = view.getNode(r);
            if (node)
                node.style.setProperty( 'color', '#'+color);
        }
        if (color==='000000')
            color = undefined;
        this.fireEvent('color_gobjects', gobs, color);
        if (picker) picker.ownerCt.destroy();
    },

    onColorSelectedGobs: function() {
        var me = this;

        var sel = this.tree.getSelectionModel().getSelection();

        if (sel.length<1) {
            BQ.ui.notification('You first need to select some annotations in the tree...');
            return;
        }
        var item = this.tree.getView().getNode(sel[0]);
        var selvis;
        sel.forEach(function(e,i,a){
            me.tree.expandNode(e);
            var item = me.tree.getView().getNode(e);
            if(item)
                selvis = item;
            //me.selectColor(item);
        });
        selvis = selvis ? selvis : this.queryById('AnnoToolbar').getEl();
        this.selectColor(selvis);
        //if(selvis) //JD: this is a quick fix, but still doesn't work properly


    },

    onStats: function(type) {
        var sel = this.tree.getSelectionModel().getSelection();
        if (sel.length<1) {
            BQ.ui.notification('You first need to select some annotations in the tree...');
            return;
        }
        var types = {
            counts    : 'gobject-number',
            perimeter : 'gobject-length',
            area      : 'gobject-area',
        };
        var url    = [];
        var titles = [];
        var r=undefined;
        for (var i=0; (r=sel[i]); i++) {
            url.push(r.raw.uri);
            var name = r.raw.type || r.raw.resource_type;
            name += r.raw.name ? ':'+ r.raw.name : '';
            titles.push(name);
        }

        // define xpath to search for all possible gobject types
        var selectors = ['//gobject'];
        for (var p in BQGObject.primitives)
            selectors.push('//'+p);
        var xpath = selectors.join(' | ');

        var xmap    = types[type] || 'gobject-number';
        var xreduce = type==='counts'? 'count' : 'vector';
        var title   = 'Stats: '+type;

        var spreadsheet = Ext.create('BQ.stats.Dialog', {
        //var spreadsheet = Ext.create('BQ.spreadsheet.Dialog', {
            url     : url,
            xpath   : xpath,
            xmap    : xmap,
            xreduce : xreduce,
            title   : title,
            //root    : this.root,
            opts    : { titles: titles, },
        });
    },

    onProjection: function(el, e) {
        this.fireEvent('gob_projection', this, el.projection);
    },

    onColoring: function(el, e) {
        this.fireEvent('gob_coloring', this, el.coloring);
    },

    onColoringTag: function(el, e) {
        this.fireEvent('gob_coloring_tag', this);
    },

    onGobTolerance: function(el, e) {
        this.fireEvent('gob_tolerance', this);
    },

    doChildrenCount: function() {
        var sel = this.tree.getSelectionModel().getSelection(),
            node = sel.length<1 ? this.tree.getRootNode() : sel[0];
        if (node && node.raw && node.raw.gobjects) {
            var l = node.raw.gobjects.length,
                h = this.tree.queryById('GobsHeader');
            if (h)
                h.setText(Ext.String.format('<h3>Current children: {0}</h3>', l));
        }
    },

    showChildrenCount: function() {
        var me = this;
        if (me.childrenCountTimer) clearTimeout(me.childrenCountTimer);
        me.childrenCountTimer = setTimeout(function() {
            me.doChildrenCount();
        }, 50);

    },

});

//-----------------------------------------------------------------------
// OwnershipStripper
//-----------------------------------------------------------------------

Ext.define('Bisque.ResourceTagger.OwnershipStripper',
{
    extend: BQVisitor,

    visit: function (node, args) {
        Ext.apply(node,
        {
            uri: undefined,
            ts: undefined,
            owner: undefined,
            perm: undefined,
            index: undefined
        });
    }
});

Ext.define('Bisque.ResourceTagger.viewStateManager',
{
    constructor: function (mode) {
        //  ResourceTagger view-state
        this.state =
        {
            btnAdd: true,
            btnDelete: true,

            btnToggleCheck: true,

            btnImport: true,
            btnExport: true,
            btnXML: true,
            btnCSV: true,
            btnGDocs: true,

            btnSave: true,
            editable: true,
        };

        function setHidden(obj, bool) {
            var result = {};

            for (i in obj)
                result[i] = bool;

            return result;
        }

        switch (mode) {
            case 'ViewerOnly':
                {
                    // all the buttons are hidden
                    this.state = setHidden(this.state, true);
                    this.state.editable = false;
                    break;
                }
            case 'PreferenceTagger':
                {
                    this.state.btnAdd = false;
                    this.state.btnDelete = false;
                    break;
                }
            case 'ReadOnly':
                {
                    this.state.btnExport = false;
                    this.state.btnXML = false;
                    this.state.btnCSV = false;
                    this.state.btnGDocs = false;
                    this.state.editable = false;
                    break;
                }
            case 'Offline':
                {
                    this.state.btnAdd = false;
                    this.state.btnDelete = false;
                    this.state.btnImport = false;
                    break;
                }
            case 'GObjectTagger':
                {
                    // all the buttons are hidden except export
                    this.state = setHidden(this.state, true);
                    this.state.editable = false;

                    this.state.btnExport = false;
                    this.state.btnCSV = false;
                    this.state.btnGDocs = false;
                    this.state.btnXML = false;

                    break;
                }
            default:
                {
                    // default case: all buttons are visible (hidden='false')
                    this.state = setHidden(this.state, false);
                    this.state.editable = true;
                }
        }

    }
});
