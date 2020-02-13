// Page view for a File
Ext.define('Bisque.Resource.File.Page', {
    extend : 'Bisque.Resource.Page',

    downloadOriginal : function() {
        if (this.resource.src) {
            window.open(this.resource.src);
            return;
        }
        var exporter = Ext.create('BQ.Export.Panel');
        exporter.downloadResource(this.resource, 'none');
    },
});

Ext.define('Bisque.Resource.File.Compact', {
    extend : 'Bisque.Resource.Compact',
    initComponent : function() {
        this.addCls(['resicon','file']);
        this.callParent();
    },

    updateContainer : function() {
        var s = this.resource.name.split('.');
        if (s.length>1)
        this.add({
            xtype: 'tbtext',
            cls: 'format',
            text: s.slice(-1).pop(),
        });
        this.callParent();
    },

});

Ext.define('Bisque.Resource.File.Card', {
    extend : 'Bisque.Resource.Card',
    initComponent : function() {
        this.addCls('file');
        this.callParent();
    },
});

Ext.define('Bisque.Resource.File.Full', {
    extend : 'Bisque.Resource.Full',
    initComponent : function() {
        this.addCls('file');
        this.callParent();
    },
});

Ext.define('Bisque.Resource.File.Grid', {
    extend : 'Bisque.Resource.Grid',

    initComponent : function() {
        this.addCls(['resicon','file']);
        this.callParent();
    },

    getFields : function(cb) {
        var fields = this.callParent();
        fields[0] = '<div class="resicon gridIcon file" />';
        return fields;
    },
});

Ext.define('Bisque.Resource.File.Annotator', {
    extend : 'Bisque.Resource.Annotator',
});