/* Abstract Module resource definition (inherits from Resource abstract class) */
Ext.define('Bisque.Resource.Module', {
    extend : 'Bisque.Resource',

    afterRenderFn : function() {
        this.setData('renderedRef', this);

        if (this.getData('fetched') == 1)
            this.updateContainer();
    },
});

Ext.define('Bisque.Resource.Module.Compact', {
    extend : 'Bisque.Resource.Module',

    constructor : function() {
        Ext.apply(this, {
            layout : {
                type : 'vbox',
                align : 'stretch'
            }
        });

        this.callParent(arguments);
        this.addCls('compact');
        this.addCls(['resicon', 'module']);
    },

    prefetch : function() {
        if (!this.getData('fetched')) {
            this.setData('fetched', -1);
            //Loading

            BQFactory.request({
                uri : this.resource.owner,
                cb : Ext.bind(this.loadResource, this),
                errorcb : Ext.emptyFn
            });
        }
    },

    loadResource : function(ownerInfo) {
        this.setData('owner', ownerInfo.display_name);
        this.setData('fetched', 1);
        //Loaded

        var renderedRef = this.getData('renderedRef');
        if (renderedRef)
            renderedRef.updateContainer();
    },

    updateContainer : function() {
        var name = Ext.create('Ext.container.Container', {
            cls : 'lblHeading1',
            html : this.resource.name,
        });

        var type = Ext.create('Ext.container.Container', {
            cls : 'lblHeading2',
            html : this.getData('owner'),
        });

        var value = Ext.create('Ext.container.Container', {
            cls : 'lblContent',
            html : this.resource.value,
        });

        this.add([name, type, value]);

        this.thumbnail = BisqueServices.getURL('module_service') + this.resource.name +'/thumbnail';
        this.getEl().dom.style.backgroundImage = "url('"+this.thumbnail+"')";

        this.setLoading(false);
    },
});

Ext.define('Bisque.Resource.Module.List', {
    extend : 'Bisque.Resource.Module',

    layout : {
        type : 'hbox',
        align : 'middle',
    },

    afterRenderFn : function(me) {
        if (!this.ttip) {
            this.ttip = Ext.create('Ext.tip.ToolTip', {
                target : me.id,
                width : 278,
                cls : 'LightShadow',
                style : 'background-color:#FAFAFA;border: solid 3px #E0E0E0;',
                layout : 'hbox',
                autoHide : false,
                listeners : {
                    "afterrender" : function(me) {
                        if (!this.tagsLoaded)
                            me.setLoading({
                                msg : ''
                            });
                    },
                    scope : this
                }
            });
        }

        this.callParent(arguments);

    },

    onMouseEnter : function() {
        if (!this.tagsLoaded) {
            BQFactory.request({
                uri : this.resource.uri + '/tag',
                cb : Ext.bind(this.tagData, this)
            });
        }
        this.callParent(arguments);
    },

    tagData : function(data) {
        this.tagsLoaded = true;
        this.resource.tags = data.tags;

        var tagArr = [], tags = {
        }, found = '';

        for (var i = 0; i < this.resource.tags.length; i++) {
            found = this.resource.tags[i].value;
            tags[this.resource.tags[i].name] = (found == null || found == "" ? 'None' : found);
            tagArr.push(new Ext.grid.property.Property({
                name : this.resource.tags[i].name,
                value : tags[this.resource.tags[i].name]
            }));
        }

        var propsGrid = this.GetPropertyGrid({
            width : 270
        }, tagArr);

        this.ttip.add(propsGrid);
        this.ttip.setLoading(false);
    },

    prefetch : function() {
        if (!this.getData('fetched')) {
            this.setData('fetched', -1);
            // -1 = Loading

            BQFactory.request({
                uri : this.resource.uri,
                cb : Ext.bind(this.loadResourceTags, this),
                errorcb : Ext.emptyFn,
                cache: true,
                uri_params: {view:'deep'},
                //uri_params: {view:'module_options,display_options,thumbnail,title,description'},
            });
        }
    },

    loadResourceTags : function(resource) {
        this.setData('tags', resource.tags);
        this.resource = resource;
        /*BQFactory.request({
            uri : this.resource.owner,
            cb : Ext.bind(this.loadResource, this),
            errorcb : Ext.emptyFn
        });*/

        BQUser.fetch_user(this.resource.owner, callback(this, this.loadResource), Ext.emptyFn);
    },

    loadResource : function(ownerInfo) {
        this.setData('owner', ownerInfo.display_name);
        this.setData('fetched', 1);
        // 1 = Loaded

        var renderedRef = this.getData('renderedRef');
        if (renderedRef) {
            renderedRef.resource = this.resource;
            renderedRef.updateContainer();
        }
    },

    updateContainer : function() {
        var moduleName = new Ext.form.Label({
            text : ' ' + this.resource.name + ' ',
            //padding:5,
            cls : 'lblModuleName',
        });

        var moduleOwner = new Ext.form.Label({
            text : this.getData('owner'),
            //padding:'0 0 0 5',
            cls : 'lblModuleOwner'
        });

        var moduleType = new Ext.form.Label({
            text : this.resource.type,
            padding : 5,
            style : 'color:#444'
        });

        this.add([moduleName, moduleOwner, moduleType]);
        this.setLoading(false);
    },
});

Ext.define('Bisque.Resource.Module.IconList', {
    extend : 'Bisque.Resource.Module.List',

    initComponent : function() {
        this.addCls('icon-list');
        this.addCls('mex');
        this.callParent();
    },

    afterRenderFn : function() {
        this.ttip = 1;
        this.tagsLoaded = 1;
        this.callParent(arguments);
    },

    updateContainer : function() {
        var serviceURL = BisqueServices.getURL('module_service') + this.resource.name;
        var tags = this.getData('tags'), description;

        for (var i = 0; i < tags.length; i++)
            if (tags[i].name == "description")
                description = tags[i].value;

        var imgCt = {
            xtype: 'component',
            itemId: 'thumbnail',
            cls: 'thumbnail',
            autoEl: {
                tag: 'img',
                src: serviceURL + '/thumbnail',
            },
            listeners: {
                scope: this,
                error: {
                    element: 'el',
                    fn: this.onThumbnailError,
                },
            },
        };

        var moduleName = new Ext.form.Label({
            text : this.resource.name,
            //padding:'0 0 1 3',
            cls : 'lblModuleName',
        });

        var html = '';
        var v = this.resource.tags_index['module_options/version'];
        var o = this.getData('owner');
        if (v) html += 'Version: '+v+', ';
        if (o) html += 'Owner: ' + o;
        var moduleInfo = new Ext.form.Label({
            html : html,
            //padding:'0 0 0 3',
            maxHeight : 18,
            cls : 'lblModuleOwner'
        });

        var moduleDesc = new Ext.form.Label({
            html : description,
            padding : '7 2 0 3',
        });

        var rightCt = Ext.create('Ext.container.Container', {
            layout : {
                type : 'vbox',
                align : 'stretch'
            },
            margin : '2 0 0 2',
            height : 120,
            flex : 1,

            items : [moduleName, moduleInfo, moduleDesc]
        });

        this.add([imgCt, rightCt]);
        this.setLoading(false);
    },

    onThumbnailError : function() {
        this.addCls('disabled');
        this.resource.available = false;
        var cmp = this.queryById('thumbnail');
        cmp.getEl().dom.src = '/core/js/ResourceBrowser/Images/stop.svg';
    },
});

Ext.define('Bisque.Resource.Module.Page', {
    extend : 'Bisque.Resource.Page',

    /*downloadOriginal : function() {
        var exporter = Ext.create('BQ.Export.Panel');
        exporter.downloadResource(this.resource, 'none');
    },*/

    createDefaultViewer: function() {
        var url = Ext.String.format('/module_service/{0}/?embed=true', this.resource.name);
        return {
            xtype: 'component',
            layout: 'fit',
            border: 0,
            autoEl: {
                tag: 'iframe',
                src: url,
                frameborder: "0",
            },
        };
    },

});
