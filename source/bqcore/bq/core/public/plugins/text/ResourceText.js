/*******************************************************************************
 Author: Dima Fedorov <dima@dimin.net>
 Copyright Center for Bio-Image Informatics, UCSB
*******************************************************************************/

Ext.define('Bisque.Resource.Text.Page', {
    extend : 'Bisque.Resource.Page',

    initComponent : function() {
        this.addCls('textio');
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
        this.setLoading(true);

        this.add({
            xtype : 'container',
            itemId: 'main_container',
            layout : 'border',
            items : [{
                xtype: 'tabpanel',
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
                    resource : this.resource,
                    title : 'Annotations',
                }]
            }, {
                xtype: 'container',
                itemId: 'editor',
                title: 'Viewer',
                cls: 'editor',
                region : 'center',
                border : false,                
                layout: 'fit',
                autoEl: {
                    tag: 'textarea',
                },
            }],
        });

        this.toolbar.doLayout();

        Ext.Ajax.request({
            url: '/blob_service/' + this.resource.resource_uniq,
            callback: function(opts, succsess, response) {
                if (response.status>=400 || !succsess)
                    BQ.ui.error(response.responseText);
                else
                    this.onFileContents(response.responseText);
            },
            scope: this,
            disableCaching: false,
            listeners: {
                scope: this,
                beforerequest   : function() { this.setLoading('Loading data...'); },
                requestcomplete : function() { this.setLoading(false); },
                requestexception: function() { this.setLoading(false); },
            },
        });
    },

    onFileContents: function(txt) {
        this.setLoading(false);
        var a = this.queryById('editor');
        a.el.dom.value = txt;
    },

});

Ext.define('Bisque.Resource.Text.Compact', {
    extend : 'Bisque.Resource.Compact',
    initComponent : function() {
        this.addCls(['resicon', 'text']);
        this.callParent();
    },

});

Ext.define('Bisque.Resource.Text.Card', {
    extend : 'Bisque.Resource.Card',
    initComponent : function() {
        this.addCls('text');
        this.callParent();
    },
});

Ext.define('Bisque.Resource.Text.Full', {
    extend : 'Bisque.Resource.Full',
    initComponent : function() {
        this.addCls('text');
        this.callParent();
    },
});

Ext.define('Bisque.Resource.Text.Grid', {
    extend : 'Bisque.Resource.Grid',

    initComponent : function() {
        this.addCls(['resicon', 'text']);
        this.callParent();
    },

    getFields : function(cb) {
        var fields = this.callParent();
        fields[0] = '<div class="resicon gridIcon text" />';
        return fields;
    },
});