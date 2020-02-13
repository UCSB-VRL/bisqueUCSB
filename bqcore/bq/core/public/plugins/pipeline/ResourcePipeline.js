/*******************************************************************************
Pipeline resource viewer
required inputs:
    resource
*******************************************************************************/

Ext.define('BQ.viewers.Dream3d_pipeline', {
    alias: 'widget.viewer_dream3d_pipeline',
    extend: 'Ext.Component',
    componentCls: 'dream3d_pipeline',
/*
    initComponent : function() {
        this.callParent();
        this.addListener('resize', this.doResize, this);
    },

    afterRender : function() {
        this.callParent();
        var resource = this.resource;
        if (!resource || !resource.value) return;
        if (resource.resource_type === 'tag' && resource.value.startsWith('http')) {
            // resource is a reference from a tag
            var path = resource.value.split('/'),
                resource_uniq = path.slice(-1)[0];
            this.fetchFileContents(resource_uniq);
        } else if (resource.resource_type === 'dream3d_pipeline') {
            // pipeline in JSON file resource
            this.fetchFileContents(resource.resource_uniq);
        }
    },

    fetchFileContents : function(resource_uniq) {
        this.setLoading('Loading data...');
        Ext.Ajax.request({
            url: '/blob_service/' + resource_uniq,
            callback: function(opts, succsess, response) {
                this.setLoading(false);
                if (response.status>=400 || !succsess)
                    BQ.ui.error(response.responseText);
                else
                    this.doPlot(response.responseText);
            },
            scope: this,
            disableCaching: false,
        });
    },

    doPlot : function(val) {
        var me = this;
        // TODO!!!
    },

    doResize : function(me, width, height) {
        // TODO!!!
    },
*/
});

Ext.define('Bisque.Resource.Dream3d_pipeline.Page', {
    extend : 'Bisque.Resource.Page',

    initComponent : function() {
        this.addCls('pipelineio');
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

        var resourceTagger = {
            xtype: 'bq-tagger',
            resource : this.resource,
            title : 'Annotations',
        };

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
                items : [resourceTagger],
            }, {
                xtype: 'bq_pipelineviewer_panel',
                itemId: 'pipelineViewer',
                region : 'center',
                flex: 2,
                border : false,
                resource: this.resource,
                resourceType: 'blobservice_url',
                rankdir: 'TB',
            }],
        });

        this.toolbar.doLayout();

        this.setLoading(false);
    },

});

Ext.define('Bisque.Resource.Dream3d_pipeline.Compact', {
    extend : 'Bisque.Resource.Compact',
    initComponent : function() {
        this.addCls(['resicon', 'dream3d_pipeline']);
        this.callParent();
    },

});

Ext.define('Bisque.Resource.Dream3d_pipeline.Card', {
    extend : 'Bisque.Resource.Card',
    initComponent : function() {
        this.addCls('dream3d_pipeline');
        this.callParent();
    },
});

Ext.define('Bisque.Resource.Dream3d_pipeline.Full', {
    extend : 'Bisque.Resource.Full',
    initComponent : function() {
        this.addCls('dream3d_pipeline');
        this.callParent();
    },
});




Ext.define('BQ.viewers.Cellprofiler_pipeline', {
    alias: 'widget.viewer_cellprofiler_pipeline',
    extend: 'Ext.Component',
    componentCls: 'cellprofiler_pipeline',
});

Ext.define('Bisque.Resource.Cellprofiler_pipeline.Page', {
    extend : 'Bisque.Resource.Page',

    initComponent : function() {
        this.addCls('pipelineio');
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

        var resourceTagger = {
            xtype: 'bq-tagger',
            resource : this.resource,
            title : 'Annotations',
        };

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
                items : [resourceTagger],
            }, {
                xtype: 'bq_pipelineviewer_panel',
                itemId: 'pipelineViewer',
                region : 'center',
                flex: 2,
                border : false,
                resource: this.resource,
                resourceType: 'blobservice_url',
                rankdir: 'TB',
            }],
        });

        this.toolbar.doLayout();

        this.setLoading(false);
    },

});

Ext.define('Bisque.Resource.Cellprofiler_pipeline.Compact', {
    extend : 'Bisque.Resource.Compact',
    initComponent : function() {
        this.addCls(['resicon', 'cellprofiler_pipeline']);
        this.callParent();
    },

});

Ext.define('Bisque.Resource.Cellprofiler_pipeline.Card', {
    extend : 'Bisque.Resource.Card',
    initComponent : function() {
        this.addCls('cellprofiler_pipeline');
        this.callParent();
    },
});

Ext.define('Bisque.Resource.Cellprofiler_pipeline.Full', {
    extend : 'Bisque.Resource.Full',
    initComponent : function() {
        this.addCls('cellprofiler_pipeline');
        this.callParent();
    },
});




Ext.define('BQ.viewers.Imagej_pipeline', {
    alias: 'widget.viewer_imagej_pipeline',
    extend: 'Ext.Component',
    componentCls: 'imagej_pipeline',
});

Ext.define('Bisque.Resource.Imagej_pipeline.Page', {
    extend : 'Bisque.Resource.Page',

    initComponent : function() {
        this.addCls('pipelineio');
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

        var resourceTagger = {
            xtype: 'bq-tagger',
            resource : this.resource,
            title : 'Annotations',
        };

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
                items : [resourceTagger],
            }, {
                xtype: 'bq_pipelineviewer_panel',
                itemId: 'pipelineViewer',
                region : 'center',
                flex: 2,
                border : false,
                resource: this.resource,
                resourceType: 'blobservice_url',
                rankdir: 'TB',
            }],
        });

        this.toolbar.doLayout();

        this.setLoading(false);
    },

});

Ext.define('Bisque.Resource.Imagej_pipeline.Compact', {
    extend : 'Bisque.Resource.Compact',
    initComponent : function() {
        this.addCls(['resicon', 'imagej_pipeline']);
        this.callParent();
    },

});

Ext.define('Bisque.Resource.Imagej_pipeline.Card', {
    extend : 'Bisque.Resource.Card',
    initComponent : function() {
        this.addCls('imagej_pipeline');
        this.callParent();
    },
});

Ext.define('Bisque.Resource.Imagej_pipeline.Full', {
    extend : 'Bisque.Resource.Full',
    initComponent : function() {
        this.addCls('imagej_pipeline');
        this.callParent();
    },
});



Ext.define('BQ.viewers.Bisque_pipeline', {
    alias: 'widget.viewer_bisque_pipeline',
    extend: 'Ext.Component',
    componentCls: 'bisque_pipeline',
});

Ext.define('Bisque.Resource.Bisque_pipeline.Page', {
    extend : 'Bisque.Resource.Page',

    initComponent : function() {
        this.addCls('pipelineio');
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

        var resourceTagger = {
            xtype: 'bq-tagger',
            resource : this.resource,
            title : 'Annotations',
        };

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
                items : [resourceTagger],
            }, {
                xtype: 'bq_pipelineviewer_panel',
                itemId: 'pipelineViewer',
                region : 'center',
                flex: 2,
                border : false,
                resource: this.resource,
                resourceType: 'blobservice_url',
                rankdir: 'TB',
            }],
        });

        this.toolbar.doLayout();

        this.setLoading(false);
    },

});

Ext.define('Bisque.Resource.Bisque_pipeline.Compact', {
    extend : 'Bisque.Resource.Compact',
    initComponent : function() {
        this.addCls(['resicon', 'bisque_pipeline']);
        this.callParent();
    },

});

Ext.define('Bisque.Resource.Bisque_pipeline.Card', {
    extend : 'Bisque.Resource.Card',
    initComponent : function() {
        this.addCls('bisque_pipeline');
        this.callParent();
    },
});

Ext.define('Bisque.Resource.Bisque_pipeline.Full', {
    extend : 'Bisque.Resource.Full',
    initComponent : function() {
        this.addCls('bisque_pipeline');
        this.callParent();
    },
});



/*******************************************************************************
Pipeline renderer
*******************************************************************************/

/*
Ext.onReady( function() {
    BQ.renderers.resources.dream3d_pipeline = 'BQ.renderers.Dream3d_pipeline';
});

Ext.define('BQ.renderers.Dream3d_pipeline', {
    alias: 'widget.pipeline_panel',
    extend: 'BQ.viewer.Graph.Panel',

    height: 600,
    layout: 'fit',
    defaults: { border: null, },

    initComponent : function() {
        this.items = [{
            xtype: 'viewer_dream3d_pipeline',
            itemId: 'dream3d_pipelineViewer',
            resource: this.resource,
        }];
        this.callParent();
    },

});
*/