Ext.define('Bisque.DatasetBrowser.Dialog', {
    extend : 'Ext.window.Window',
    alias: 'widget.bq-dataset-dialog',
    modal : true,
    border : false,
    width : '85%',
    height : '85%',
    layout: 'fit',
    buttonAlign: 'center',

    selType: 'SINGLE',

    initComponent : function() {
        this.title = this.title || 'Select a dataset...',
        this.items = [{
            xtype: 'bq-dataset-browser',
            itemId: 'browser-dataset',
            selType: this.selType,
        }];
        this.buttons = [{
            text: 'Select',
            iconCls : 'icon-select',
            scale: 'large',
            scope: this,
            width: 100,
            handler: this.onDone,
        }, {
            text: 'Close',
            iconCls : 'icon-cancel',
            scale: 'large',
            scope: this,
            width: 100,
            handler: this.close,
        }];

        this.callParent();
        this.show();
    },

    onDone: function() {
        var browser = this.queryById('browser-dataset');
        if (browser.selected_dataset) {
            this.fireEvent( 'DatasetSelect', this, browser.selected_dataset );
            this.close();
        }
    },

});

Ext.define('Bisque.DatasetBrowser.Browser', {
    extend : 'Ext.panel.Panel',
    alias: 'widget.bq-dataset-browser',
    layout: 'border',
    selType: 'SINGLE',

    initComponent : function() {
        this.items = [{
            xtype: 'bq-resource-browser',
            itemId: 'browser-dataset',
            region: 'center',
            //region: 'west',
            //split: true,
            title: 'Datasets',
            flex: 1,
            dataset : '/data_service/dataset',
            selType: this.selType,
            selectState: this.selType === 'SINGLE' ? 'ACTIVATE' : 'SELECT',
            showOrganizer : true,
            listeners : {
                Select : this.onSelect,
                ResSelectionChange: this.onSelect,
                scope : this
            },
        }, {
            xtype: 'bq-resource-browser',
            itemId  : 'browser-preview',
            //region: 'center',
            region: 'east',
            split: true,
            showOrganizer : false,
            dataset : 'None',
            layout: Bisque.ResourceBrowser.LayoutFactory.LAYOUT_KEYS.Compact,
            viewMode: 'ViewerOnly',
            title: 'Preview',
            //flex: 1,
            width: 400,
        }];

        this.callParent();
    },

    onSelect: function(me, resource) {
        this.selected_dataset = resource;
        if (resource && resource instanceof Array && resource.length>0) {
            resource = resource[0];
        }

        var preview = this.queryById('browser-preview');
        preview.loadData({
            baseURL: resource.uri + '/value',
            offset: 0,
            tag_order: '"@ts":desc',
            tag_query: '',
        });
        this.fireEvent('Select', this, this.selected_dataset);
    },

});
