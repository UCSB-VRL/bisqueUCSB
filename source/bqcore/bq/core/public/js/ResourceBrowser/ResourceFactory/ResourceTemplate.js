// Page view for a template
Ext.define('Bisque.Resource.Template.Page', {
    extend : 'Bisque.Resource.Page',

    onResourceRender : function() {
        this.setLoading(false);

        var tplMan = new BQ.TemplateManager.create({
            resource : this.resource,
            tplToolbar : this.toolbar
        });
        this.add(tplMan);

        this.toolbar.insert(0, [{
            xtype : 'tbspacer',
            width : 8
        }, {
            itemId : 'tbTplSave',
            text : 'Save',
            width : 75,
            textAlign : 'left',
            border : 2,
            style : {
                borderColor : '#0178C1',
                borderStyle : 'dotted'
            },
            iconCls : 'icon-save',
            handler : tplMan.saveTemplate,
            scope : tplMan
        }, '-']);
    },
});
