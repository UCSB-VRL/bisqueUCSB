/*******************************************************************************

  BQ.selectors.SpreadsheetMatching

  Author: Dima Fedorov

  Version: 1

  History:
    2015-11-25 13:57:30 - first creation

*******************************************************************************/

Ext.onReady( function() {
    BQ.selectors.parameters.spreadsheet_matching = 'BQ.selectors.SpreadsheetMatching';
});

/*******************************************************************************
BQ.selectors.SpreadsheetMatching relies on BQ.selectors.Resource and although
it is instantiated directly it needs existing BQ.selectors.Resource to listen to
and read data from!

*******************************************************************************/

Ext.define('BQ.SpreadsheetMatching.Model', {
    extend: 'Ext.data.Model',
    fields: [{
        name: 'header',
        type: 'string',
    }, {
        name: 'tag',
        type: 'string',
    }, {
        name: 'value',
        type: 'string',
    }, {
        name: 'ignored',
        type: 'boolean',
    }, {
        name: 'system',
        type: 'boolean',
    }, {
        name: 'readonly',
        type: 'boolean',
    }, {
        name: 'description',
        type: 'string',
    }]
});

Ext.define('BQ.selectors.SpreadsheetMatching', {
    alias: 'widget.selector_spreadsheet_matching',
    extend: 'BQ.selectors.Selector',
    requires: ['Ext.data.Store', 'Ext.form.field.ComboBox', 'Ext.tip.*'],
    componentCls: 'bq_selector_spreadsheet_matching',

    height: 600,
    layout: 'fit',

    system_tags: [{
        search: null,
        tag: 'file.name',
        system: true,
        readonly: true,
        description: 'Required annotation defining the file name being annotated',
    }, {
        search: /lat/ig,
        tag: 'geo.latitude',
        system: true,
        description: 'System interpretable annotation defining geographical position',
    }, {
        search: /long/ig,
        tag: 'geo.longitude',
        system: true,
        description: 'System interpretable annotation defining geographical position',
    }, {
        search: /alt/ig,
        tag: 'geo.altitude',
        system: true,
        description: 'System interpretable annotation defining geographical position',
    }, {
        search: /width/ig,
        tag: 'res.width',
        system: true,
        description: 'System interpretable annotation defining image resolution',
    }, {
        search: /height/ig,
        tag: 'res.height',
        system: true,
        description: 'System interpretable annotation defining image resolution',
    }, {
        search: /unit/ig,
        tag: 'res.units',
        system: true,
        description: 'System interpretable annotation defining image resolution',
    }],

    initComponent : function() {
        var resource = this.resource;
        var template = resource.template || {};
        this.dataset = template.dataset;

        var reference_dataset = this.module.inputs_index[template.reference_dataset];
        if (reference_dataset && reference_dataset.renderer) {
            this.reference_dataset = reference_dataset.renderer;
            this.reference_dataset.on( 'changed', this.onNewResource, this );
        }

        this.tag_matches = resource.find_tags('matches');
        this.tag_spreadsheet_uuid = resource.find_tags('spreadsheet_uuid');

        this.matches = [];
        this.store = Ext.create('Ext.data.Store', {
            autoLoad: false,
            autoSync: true,
            data: this.matches,
            model: 'BQ.SpreadsheetMatching.Model',
            proxy: {
                type: 'memory',
                reader: 'json',
                writer: 'json',
            },

        });

        this.cellEditing = new Ext.grid.plugin.CellEditing({
            clicksToEdit: 1,
            listeners: {
                scope: this,
                beforeedit: function(e, editor) {
                    if (editor.colIdx === 0 && editor.record.get('system') !== true)
                        return false;
                    if (editor.colIdx === 1 && editor.record.get('system') === true)
                        return false;
                    if (editor.colIdx === 2 && !editor.record.get('value'))
                        return false;
                },
                edit: function( editor, context ) {
                    // dima: update original vector
                    // seems i'm doing something wrong but writes do not propagate back to the original array
                    var record = context.record;
                    record.raw.header = this.copyStringNonEmpty(record.data.header);
                    record.raw.tag = this.copyStringNonEmpty(record.data.tag);
                    record.raw.value = this.copyStringNonEmpty(record.data.value);
                    this.update_resource();
                },
            },
        });

        this.columns = {
            defaults: {
                tdCls: 'bq_row',
                cls: 'bq_row',
            },
            items: [{
                text: 'Spreadsheet column',
                dataIndex: 'header',
                flex: 6,
                renderer: this.rowRenderer,
                tdCls: 'bq_row bq_spreadsheet',
                editor: new Ext.form.field.ComboBox({
                    typeAhead: true,
                    triggerAction: 'all',
                    queryMode: 'local',
                    displayField: 'header',
                    valueField: 'header',
                    store: this.store,
                    forceSelection: true,
                }),
            }, {
                text: 'Annotation name',
                dataIndex: 'tag',
                flex: 6,
                renderer: this.rowRenderer,
                editor: {
                    allowBlank: false,
                },
            }, {
                text: 'Value',
                dataIndex: 'value',
                flex: 1,
                renderer: this.rowRenderer,
                editor: {
                    allowBlank: true,
                },
            }, {
                xtype: 'actioncolumn',
                text: 'Ignore',
                width: 80,
                align : 'center',
                sortable: false,
                menuDisabled: true,
                items: [{
                    iconCls: 'icon_remove',
                    tooltip: 'Ignore this column',
                    scope: this,
                    handler: this.onIgnoreColumn,
                }]
            }],
        };

        this.items = [{
            xtype: 'gridpanel',
            itemId  : 'table',
            //title: 'Table',
            flex: 5,
            autoScroll: true,
            border: 0,
            viewConfig: {
                stripeRows: true,
                forceFit: true,
                preserveScrollOnRefresh: true,
            },
            plugins: [this.cellEditing],
            store: this.store,
            columns: this.columns,

            /*listeners: {
                scope: this,
                select : function(o, record, index ) {
                    //var idx = record.get('id_original') || record.get('id');
                    //this.fireEvent('selected_class', idx);
                },
            },*/
        }];


        this.callParent();
    },

    onNewResource : function(el, res) {
        if (!(res instanceof BQDataset))
            return;
        this.dataset = res.uri;
        this.setLoading('Fetching spreadsheet...');
        Ext.Ajax.request({
            url: this.dataset + '/value?limit=100000&view=short',
            callback: function(opts, succsess, response) {
                if (response.status>=400)
                    this.onError();
                else
                    this.onDataset(response.responseXML);
            },
            scope: this,
            disableCaching: false,
        });
    },

    copyStringNonEmpty: function(v) {
        if (v==='') return undefined;
        return v;
    },

    setValueUI : function(v) {
        //this.combo.setValue(v);
        //this.queryById('combobox').setValue(v);
    },

    onError : function() {
        this.setLoading(false);
        BQ.ui.error('Problem fetching spreadsheet');
    },

    onDataset : function(xml) {
        var tables = BQ.util.xpath_nodes(xml, '*/resource[@resource_type="table"]');
        if (tables.length<1) {
            BQ.ui.error('Could not detect a compatible spreadsheet in this dataset');
            return;
        }
        this.spreadsheet_uuid = tables[0].getAttribute('resource_uniq');
        Ext.Ajax.request({
            url: tables[0].getAttribute('uri').replace('data_service', 'table') + '/info/format:json',
            callback: function(opts, succsess, response) {
                if (response.status>=400)
                    this.onError();
                else
                    this.onHeaders(response.responseText);
            },
            scope: this,
            disableCaching: false,
        });
    },

    onHeaders : function(txt) {
        this.setLoading(false);
        var json = Ext.JSON.decode(txt);
        this.headers = json.headers;
        this.parseHeaders();
    },

    parseHeaders : function() {
        var i=0, j=0, h=null, tag=null, resolution_width=null, ignored=false, s=null;
        //this.matches = [];
        this.matches.length = 0;

        // define the file name column
        this.system_tags[0].search = this.headers[0];

        // iterate through the rest of annotations
        for (i=0; (h=this.headers[i]); ++i) {
            tag = h;
            ignored = false;

            for (j=0; (s=this.system_tags[j]); ++j) {
                if (h.search(s.search)>=0) {
                    this.matches.push({
                        header: h,
                        tag: s.tag,
                        system: s.system,
                        readonly: s.readonly,
                        ignored: s.ignored,
                        description: s.description,
                    });
                    ignored=true;
                    if (s.tag === 'res.width') resolution_width = h;
                    break;
                }
            }

            this.matches.push({
                header: h,
                tag: tag,
                ignored: ignored,
            });
        }

        // detect image extent units
        if (resolution_width) {
            var els = resolution_width.split(/[ ,;_-]/);
            for (i=0; (h=els[i]); ++i) {
                if (h in BQ.api.Phys.units) {
                    this.matches.push({
                        //header: h,
                        tag: 'res.units',
                        value: h,
                        system: true,
                        description: 'System interpretable annotation automatically detected and defining units of image resolution',
                    });
                    break;
                }
            }
        }

        //this.store.loadData( this.matches );
        this.store.reload();
        this.update_resource();
    },

    rowRenderer: function (value, meta, record) {
        var cls = '';
        if (record.get('system') === true)
            cls += ' system';
        if (record.get('ignored') === true)
            cls += ' ignored';
        meta.tdCls = cls;

        if (record.get('description'))
            meta.tdAttr = Ext.String.format('data-qtip="{0}"', record.get('description'));
        return value;
    },

    onIgnoreColumn: function(grid, rowIndex, colIndex) {
        var record = grid.getStore().getAt(rowIndex);
        if (record.get('readonly')===true) {
            BQ.ui.notification('This is a required annotation');
            return;
        }
        if (record.get('ignored')===true)
            record.set('ignored', false);
        else
            record.set('ignored', true);

        // dima: update original vector
        // seems i'm doing something wrong but writes do not propagate back to the original array
        record.raw.ignored = record.data.ignored;

        this.update_resource();
    },

    update_resource: function() {
        var i=0, m=0;
        this.tag_spreadsheet_uuid.value = this.spreadsheet_uuid;
        this.tag_matches.tags = [];
        for (i=0; (m=this.matches[i]); ++i) {
            if (m.ignored === true) continue;

            this.tag_matches.addtag({
                type: m.tag,
                name: m.header,
                value: m.value,
            });
        }
    },

    select: function(resource) {
        this.resource.value = resource.value;
        this.resource.values = resource.values;
        //this.setValueUI(resource.value);
        this.setValueUI(this.getValue());
    },

    isValid: function() {
        if (this.tag_matches.tags.length === 0) {
            var template = this.resource.template || {},
                msg = template.fail_message || 'You need to select an option!';
            if (template.allowBlank) return true;
            BQ.ui.tip(this.getId(), msg, {anchor:'left',});
            return false;
        }
        return true;
    },

});

