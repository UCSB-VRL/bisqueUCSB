Ext.define('Bisque.TemplateTagger', {
    extend : 'Bisque.ResourceTagger',
    full_load_on_creation: true,

    constructor : function(config) {
        config = config || {};

        Ext.apply(config, {
            tree : {
                btnAdd : false,
                btnDelete : false,
                btnImport : true,
                btnExport : true,
            },
            importDataset : '/data_service/template',
        });

        this.tagRenderers = Ext.ClassManager.getNamesByExpression('BQ.TagRenderer.*'), this.tagTypes = {};
        for (var i = 0; i < this.tagRenderers.length; i++)
            if (Ext.ClassManager.get(this.tagRenderers[i]).componentName)
                this.tagTypes[Ext.ClassManager.get(this.tagRenderers[i]).componentName] = this.tagRenderers[i];

        this.callParent([config]);
    },

    setResource : function(resource) {
        this.resource = resource || new BQTemplate();
        this.loadResourceTags(this.resource.tags);
        this.testAuth(BQApp.user, false);
    },

    importMenu : function() {
        var rb = new Bisque.ResourceBrowser.Dialog({
            height : '85%',
            width : '85%',
            dataset : this.importDataset,
            viewMode : 'ViewerLayouts',
            selType : 'SINGLE',
            listeners : {
                'Select' : function(me, resource) {
                    resource.loadTags({
                        depth : 'deep',
                        cb : Ext.bind(this.appendTags, this),
                    });
                },

                scope : this
            },
        });
    },

    saveTags : function() {
        this.store.applyModifications();
    },

    updateQueryTagValues : Ext.emptyFn,

    // finish editing on a new record
    finishEdit : function(_editor, me) {
        this.callParent(arguments);

        var tag = me.record.raw;
        var template = tag.find_children('template');

        if ((me.newValues.value != me.originalValues.value) || Ext.isEmpty(template)) {
            if (!Ext.isEmpty(template))
                tag.remove_resource(template.uri);

            var newTemplate = Ext.ClassManager.get(this.tagTypes[me.record.get('value')]).getTemplate();
            tag.addchild(newTemplate);
        }
    },

    populateComboStore : function() {
        this.store_names = [];

        this.store_values = Ext.create('Ext.data.ArrayStore', {
            fields : ['value'],
        });

        var tagTypes = Ext.Object.getKeys(this.tagTypes);
        Ext.Array.forEach(tagTypes, function(item, index, orgArray) {
            orgArray[index] = [item];
        });

        this.store_values.loadData(tagTypes);
        this.defaultTagValue = this.store_values.getAt(0).get('value');
    },

    getTreeColumns : function() {
        return [{
            xtype : 'treecolumn',
            text : 'Field name',
            flex : 1,
            dataIndex : 'name',
            field : {
                tabIndex : 0,
                allowBlank : false,
                blankText : 'Field name is required!',
                listeners: {
                    'change': {
                        fn: function (field, newValue, oldValue, eOpts) {
                            if (this.rowEditor)
                                this.rowEditor.editor.onFieldChange();
                        },
                        buffer: 250,
                    },

                    scope: this,
                },
            }
        }, {
            text : 'Type',
            flex : 1,
            sortable : true,
            dataIndex : 'value',
            renderer : Bisque.ResourceTagger.BaseRenderer,
            editable: false,
            field : {
                xtype : 'combobox',
                displayField : 'value',
                tabIndex : 1,
                store : this.store_values,
                editable : false,
                queryMode : 'local',
            },
        }];
    },
});