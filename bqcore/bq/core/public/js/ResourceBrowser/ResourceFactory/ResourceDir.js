
// Dir

Ext.define('Bisque.Resource.Dir.Compact', {
    extend : 'Bisque.Resource.Compact',
    //cls: 'folder', //dima: unfortunately overwritten somewhere later
    initComponent : function() {
        this.addCls(['resicon','folder']);
        this.callParent();
    },
});

Ext.define('Bisque.Resource.Dir.Card', {
    extend : 'Bisque.Resource.Dir.Compact',
});

Ext.define('Bisque.Resource.Dir.Full', {
    extend : 'Bisque.Resource.Dir.Compact',
});

Ext.define('Bisque.Resource.Dir.Grid', {
    extend : 'Bisque.Resource.Grid',
    //cls: 'folder', //dima: unfortunately overwritten somewhere later
    initComponent : function() {
        this.addCls(['resicon','folder']);
        this.callParent();
    },

    getFields : function(cb) {
        var fields = this.callParent();
        fields[0] = '<div class="resicon gridIcon folder" />';
        return fields;
    },
});

Ext.define('Bisque.Resource.Dir.Annotator', {
    extend : 'Bisque.Resource.Annotator',
});

// Store

Ext.define('Bisque.Resource.Store.Compact', {
    extend : 'Bisque.Resource.Compact',
    //cls: 'folder', //dima: unfortunately overwritten somewhere later
    initComponent : function() {
        this.addCls(['resicon', 'store']);
        this.callParent();
    },
});

Ext.define('Bisque.Resource.Store.Card', {
    extend : 'Bisque.Resource.Store.Compact',
});

Ext.define('Bisque.Resource.Store.Full', {
    extend : 'Bisque.Resource.Store.Compact',
});

Ext.define('Bisque.Resource.Store.Grid', {
    extend : 'Bisque.Resource.Grid',
    //cls: 'folder', //dima: unfortunately overwritten somewhere later
    initComponent : function() {
        this.addCls(['resicon','store']);
        this.callParent();
    },

    getFields : function(cb) {
        var fields = this.callParent();
        fields[0] = '<div class="resicon gridIcon store" />';
        return fields;
    },
});

Ext.define('Bisque.Resource.Store.Annotator', {
    extend : 'Bisque.Resource.Annotator',
});

