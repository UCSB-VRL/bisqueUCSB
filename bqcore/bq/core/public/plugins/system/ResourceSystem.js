/*******************************************************************************
 Author: Dima Fedorov <dima@dimin.net>
 Copyright Center for Bio-Image Informatics, UCSB
*******************************************************************************/

Ext.define('Bisque.Resource.System.Page', {
    extend : 'Bisque.Resource.Page',

    initComponent : function() {
        this.addCls('systemio');
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
                xtype: 'bq_preferences_tagger',
                itemId: 'editor',
                //title: 'Viewer',
                cls: 'editor',
                region : 'center',
                border : false,
                layout: 'fit',

                //level: 'system',
                resource: this.resource,
            }],
        });

        this.toolbar.doLayout();
    },

});

Ext.define('Bisque.Resource.System.Compact', {
    extend : 'Bisque.Resource.Compact',
    initComponent : function() {
        this.addCls(['resicon', 'system']);
        this.callParent();
    },

});

Ext.define('Bisque.Resource.System.Card', {
    extend : 'Bisque.Resource.Card',
    initComponent : function() {
        this.addCls('system');
        this.callParent();
    },
});

Ext.define('Bisque.Resource.System.Full', {
    extend : 'Bisque.Resource.Full',
    initComponent : function() {
        this.addCls('system');
        this.callParent();
    },
});

Ext.define('Bisque.Resource.System.Grid', {
    extend : 'Bisque.Resource.Grid',

    initComponent : function() {
        this.addCls(['resicon', 'system']);
        this.callParent();
    },

    getFields : function(cb) {
        var fields = this.callParent();
        fields[0] = '<div class="resicon gridIcon system" />';
        return fields;
    },
});