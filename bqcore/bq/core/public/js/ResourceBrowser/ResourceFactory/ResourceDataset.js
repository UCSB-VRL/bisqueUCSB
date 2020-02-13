/* Abstract Dataset resource definition (inherits from Resource abstract class) */
Ext.define('Bisque.Resource.Dataset', {
    extend : 'Bisque.Resource',
    operationBarClass: 'Bisque.ResourceBrowser.OperationBar.dataset',

    initComponent : function() {
        this.addCls('dataset');
        this.callParent();
    },

    afterRenderFn : function() {
        this.setData('renderedRef', this);

        if (this.getData('fetched') == 1)
            this.updateContainer();
    },
});

Ext.define('Bisque.Resource.Dataset.Compact', {
    extend : 'Bisque.Resource.Dataset',
    alias: 'widget.bq.resource.dataset.compact',

    constructor : function() {
        Ext.apply(this, {
            layout : {
                type : 'vbox',
                align : 'stretch'
            }
        });
        this.callParent(arguments);
        this.addCls('compact');
    },

    prefetch : function(layoutMgr) {
        this.callParent(arguments);
        if (!this.getData('fetched')) {
            this.setData('fetched', -1);
            // -1 = Loading
            this.fetchMembers(this.resource);
        }
    },

    fetchMembers : function(memberTag) {
        BQFactory.request({
            uri : memberTag.uri + '/value?limit=4',
            cb : Ext.bind(this.loadResource, this),
            errorcb : Ext.emptyFn
        });
    },

    loadResource : function(resource) {
        var imgs = '<div style = "margin-left:4px; margin-top:-1px; width:152px;height:152px">';
        var thumbnail, margin;

        for (var i = 0; i < resource.children.length && i < 4; i++) {
            switch (resource.children[i].resource_type) {
                case 'image': {
                    //thumbnail = resource.children[i].src + '?slice=,,1,1&thumbnail=280,280';
                    thumbnail = resource.children[i].src + this.getImageParams({
                        width : this.layoutMgr.layoutEl.stdImageWidth, //280,
                        height : this.layoutMgr.layoutEl.stdImageHeight, //280,
                    });
                    break;
                }
                case 'dataset': {
                    thumbnail = BQ.Server.url('/export/images/folder-large.png');
                    break;
                }
                default :
                    thumbnail = BQ.Server.url('/export/images/file-large.png');
            }

            margin = (i == 1 ? 'margin:0px 0px 0px 2px;' : (i == 2 ? 'margin:2px 2px 0px 0px;' : ''));
            imgs += '<img style="display:inline-block;height:75px;width:75px;' + margin + '" src=' + thumbnail + ' />';
        }

        imgs += '</div>';

        this.setData('fetched', 1);
        // 1 = Loaded
        this.setData('previewDiv', imgs);

        var renderedRef = this.getData('renderedRef');
        if (renderedRef)
            renderedRef.updateContainer();
    },

    updateContainer : function() {
        var date = Ext.Date.parse(this.resource.ts, BQ.Date.patterns.BisqueTimestamp);
        this.update('<div class="labelOnImage" style="width:160px;">' + this.resource.name + '<br><span class="smallLabelOnImage">' + Ext.Date.format(date, BQ.Date.patterns.ISO8601Long) + '</span></div>' + this.getData('previewDiv'));
        this.setLoading(false);
    },
});

Ext.define('Bisque.Resource.Dataset.Card', {
    extend : 'Bisque.Resource.Dataset.Compact',

    fetchMembers : function(memberTag) {
        BQFactory.request({
            uri : memberTag.uri + '/value?limit=12',
            cb : Ext.bind(this.loadResource, this),
            errorcb : Ext.emptyFn
        });
    },

    loadResource : function(resource) {
        var imgs = '<div style = "margin:0px 0px 0px 12px;width:258px;height:310px">';
        var thumbnail, margin;

        for (var i = 0; i < resource.children.length && i < 12; i++) {
            switch (resource.children[i].resource_type) {
                case 'image': {
                    thumbnail = resource.children[i].src + this.getImageParams({
                        width : this.layoutMgr.layoutEl.stdImageWidth, //280,
                        height : this.layoutMgr.layoutEl.stdImageHeight, //280,
                    });
                    break;
                }
                case 'dataset': {
                    thumbnail = BQ.Server.url('/export/images/folder-large.png');
                    break;
                }
                default :
                    thumbnail = BQ.Server.url('/export/images/file-large.png');
            }

            margin = 'margin:0px 3px 2px 0px;';
            imgs += '<img style="display:inline-block;height:75px;width:75px;' + margin + '" src=' + thumbnail + ' />';
        }

        imgs += '</div>';

        this.setData('fetched', 1);
        // 1 = Loaded
        this.setData('previewDiv', imgs);

        var renderedRef = this.getData('renderedRef');
        if (renderedRef)
            renderedRef.updateContainer();
    },

    updateContainer : function() {
        var date = Ext.Date.parse(this.resource.ts, BQ.Date.patterns.BisqueTimestamp);
        this.update('<div class="labelOnImage" style="width:260px;">' + this.resource.name + '<br><span class="smallLabelOnImage">' + Ext.Date.format(date, BQ.Date.patterns.ISO8601Long) + '</span></div>' + this.getData('previewDiv'));
        this.setLoading(false);
    },
});

Ext.define('Bisque.Resource.Dataset.Full', {
    extend : 'Bisque.Resource.Dataset.Compact',
    alias: 'widget.bq.resource.dataset.full',

    constructor : function() {
        this.callParent(arguments);

        Ext.apply(this, {
            layout : 'fit',
        });
    },

    fetchMembers : function(memberTag) {
        BQFactory.request({
            uri : memberTag.uri + '/value?limit=12',
            cb : Ext.bind(this.loadResource, this),
            errorcb : Ext.emptyFn
        });
    },

    loadResource : function(resource) {
        var imgs = '<div style = "margin:0px 0px 0px 12px;width:99%;">';
        var thumbnail, margin;

        for (var i = 0; i < resource.children.length; i++) {
            switch (resource.children[i].resource_type) {
                case 'image': {
                    thumbnail = resource.children[i].src + this.getImageParams({
                        width : this.layoutMgr.layoutEl.stdImageWidth, //280,
                        height : this.layoutMgr.layoutEl.stdImageHeight, //280,
                    });
                    break;
                }
                case 'dataset': {
                    thumbnail = BQ.Server.url('/export/images/folder-large.png');
                    break;
                }
                default :
                    thumbnail = BQ.Server.url('/export/images/file-large.png');
            }

            margin = 'margin:0px 3px 2px 0px;';
            imgs += '<img style="display:inline-block;height:75px;width:75px;' + margin + '" src=' + thumbnail + ' />';
        }

        imgs += '</div>';

        this.setData('fetched', 1);
        // 1 = Loaded
        this.setData('previewDiv', imgs);

        var renderedRef = this.getData('renderedRef');
        if (renderedRef)
            renderedRef.updateContainer();
    },

    updateContainer : function() {
        var date = Ext.Date.parse(this.resource.ts, BQ.Date.patterns.BisqueTimestamp);
        var imgDiv = new Ext.get(document.createElement('div'));
        imgDiv.update('<div class="labelOnImage" style="width:99%;">' + this.resource.name + '<br><span class="smallLabelOnImage">' + Ext.Date.format(date, BQ.Date.patterns.ISO8601Long) + '</span></div>' + this.getData('previewDiv'));

        this.add(Ext.create('Ext.panel.Panel', {
            border : 0,
            autoScroll : true,
            contentEl : imgDiv,
        }));

        this.setLoading(false);

    },
});

Ext.define('Bisque.Resource.Dataset.List', {
    extend : 'Bisque.Resource.Dataset.Compact',

    constructor : function() {
        this.callParent(arguments);

        Ext.apply(this, {
            layout : {
                type : 'hbox',
                align : 'middle'
            }
        });
        this.addCls('list');
    },

    updateContainer : function() {
        var datasetName = new Ext.form.Label({
            text : ' ' + this.resource.name + ' ',
            cls : 'title',
        });

        var datasetOwner = new Ext.form.Label({
            text : this.getData('owner'),
            padding : '0 0 0 4',
            cls : 'lblModuleOwner',
        });

        var date = Ext.Date.parse(this.resource.ts, BQ.Date.patterns.BisqueTimestamp);

        var datasetDate = new Ext.form.Label({
            text : Ext.Date.format(date, BQ.Date.patterns.ISO8601Long),
            cls : 'lblModuleDate',
            flex : 1,
            //padding:'0 0 0 8',
            //style:'color:#444;font-size:11px;font-family: tahoma, arial, verdana, sans-serif !important;'
        });

        this.add([datasetName, datasetOwner, datasetDate]);
        this.setLoading(false);
    },
});

// Page view for a dataset
Ext.define('Bisque.Resource.Dataset.Page', {
    extend : 'Bisque.Resource',
    layout : 'fit',
    
    updateContainer : function() {
        this.setLoading(false);

        this.add({
            xtype: 'renderersdataset',
            resource : this.resource,
            loadmap : true,
        });        

        var download = BQApp.getToolbar().queryById('button_download'),
            url = this.resource.uri,
            url_kml = url.replace('/data_service/', '/export/') + '?format=kml',
            url_geojson = url.replace('/data_service/', '/export/') + '?format=geojson';
        download.menu.add(['-', {
            itemId: 'download_annotations_as_xml',
            text: 'Graphical annotations as XML',
            handler: function() {
                window.open(url+'/value?view=deep,clean');
            },
        }, {
            itemId: 'download_annotations_as_kml',
            text: 'Graphical annotations as KML',
            handler: function() {
                window.open(url_kml);
            },
        }, {
            itemId: 'download_annotations_as_geojson',
            text: 'Graphical annotations as GeoJson',
            handler: function() {
                window.open(url_geojson);
            },
        }]);
    }
});


//-----------------------------------------------------------------------------
// Operation bar for dataset
//-----------------------------------------------------------------------------

Ext.define('Bisque.ResourceBrowser.OperationBar.dataset', {
    extend : 'Bisque.ResourceBrowser.OperationBar',

    initComponent : function() {
        this.items = [{
            xtype: 'button',
            icon : BQ.Server.url('/core/js/ResourceBrowser/Images/down.png'),
            tooltip : 'Available operations for this resource.',
            handler : this.menuHandler,
            scope : this
        }, {
            xtype: 'button',
            itemId : 'btn_delete_full',
            text: 'Delete',
            //icon : BQ.Server.url('/core/js/ResourceBrowser/Images/close.gif'),
            tooltip : 'Delete this dataset and its elements',
            handler : this.deleteDataset,
            scope : this,
        }, {
            xtype: 'button',
            itemId : 'btn_delete',
            icon : BQ.Server.url('/core/js/ResourceBrowser/Images/close.gif'),
            tooltip : 'Delete this dataset, keep elements',
            handler : this.deleteResource,
            scope : this,
        }];
        this.dataset_service = Ext.create('BQ.dataset.Service', {
            listeners: {
                //'running': this.onDatasetRunning,
                //'success': this.onDatasetSuccess,
                'error': this.onDatasetError,
                scope: this,
            },
        });
        this.callParent();
    },

    onDatasetError: function() {
        BQ.ui.error('Error while deleteing dataset');
    },

    deleteDataset : function(me, e) {
        e.stopPropagation();
        Ext.MessageBox.confirm( 'Delete dataset?', 'Just confirming that you are deleting this dataset and all of its elements?', function(btn) {
            if (btn != 'yes') return;
            var list = Ext.Object.getSize(this.browser.resourceQueue.selectedRes);
            if (list > 1) {
                this.fireEvent( 'removed', this.browser.resourceQueue.selectedRes );
                var members = [];

                for (var res in this.browser.resourceQueue.selectedRes) {
                    this.browser.resourceQueue.selectedRes[res].setLoading({
                        msg : 'Deleting...'
                    });
                    members.push(this.browser.resourceQueue.selectedRes[res]);
                }

                for (var i=0; i<members.length; i++)
                    this.dataset_service.run_delete(members[i].resource.uri);

                //this.browser.msgBus.fireEvent('Browser_ReloadData', {});
                var msgbus = this.browser.msgBus; // dima: a hack just to get this working before the rewrite
                setTimeout(function(){ msgbus.fireEvent('Browser_ReloadData', {}); }, 1000);
            } else {
                var selected = {};
                selected[this.resourceCt.resource.uri] = this.resourceCt.resource;
                this.fireEvent( 'removed', selected );

                this.resourceCt.setLoading({
                    msg : 'Deleting...'
                });
                this.dataset_service.run_delete(this.resourceCt.resource.uri);
                //this.browser.msgBus.fireEvent('Browser_ReloadData', {});
                var msgbus = this.browser.msgBus; // dima: a hack just to get this working before the rewrite
                setTimeout(function(){ msgbus.fireEvent('Browser_ReloadData', {}); }, 1000);
            }
        }, this );
    },

});
