Ext.define('Bisque.ResourceFactory', {
    statics : {
        baseClass : 'Bisque.Resource',

        getResource : function(config) {
            var layoutKey = Ext.Object.getKey(Bisque.ResourceBrowser.LayoutFactory.LAYOUT_KEYS, config.layoutKey);
            // resource naming convention : baseClass.resourceType.layoutKey
            var className = Bisque.ResourceFactory.baseClass + '.' + Ext.String.capitalize(config.resource.resource_type.toLowerCase()) + '.' + layoutKey;

            if (Ext.ClassManager.get(className))
                return Ext.create(className, config);
            else {
                Ext.log({
                    msg : Ext.String.format('Unknown class: {0}, type: {1}, layoutKey: {2}. Initializing with base resource class.', className, config.resource.resource_type, layoutKey),
                    level : 'warn',
                    stack : true
                });
                return Ext.create(Bisque.ResourceFactory.baseClass + '.' + layoutKey, config);
            }
        }
    }
});


// Returns standalone resources
Ext.define('Bisque.ResourceFactoryWrapper', {
    statics : {
        getResource : function(config) {
            config.resourceManager = Ext.create('Ext.Component', {
                store : {},

                storeMyData : function(uri, tag, value) {
                    this.store[tag] = value;
                },

                getMyData : function(uri, tag) {
                    if (this.store[tag])
                        return this.store[tag];
                    return 0;
                }
            });

            Ext.apply(config, {
                layoutKey : config.layoutKey || Bisque.ResourceBrowser.LayoutFactory.DEFAULT_LAYOUT,
                msgBus : config.msgBus || config.resourceManager,
                resQ : config.resQ || config.resourceManager,
                browser : config.browser || {},
            });

            function preferencesLoaded(preferences, resource, layoutCls) {
                Ext.apply(resource, {
                    preferences : preferences,
                    getImagePrefs : function(key) {
                        if (this.preferences && this.preferences.Images && this.preferences.Images[key])
                            return this.preferences.Images[key];
                        return '';
                    },
                });
                resource.prefetch(layoutCls);
            }

            var resource = Bisque.ResourceFactory.getResource(config);
            var layoutCls = Bisque.ResourceBrowser.LayoutFactory.getLayout({
                browser : {
                    layoutKey : config.layoutKey
                }
            });
            resource.setSize({
                width : layoutCls.layoutEl.width,
                height : layoutCls.layoutEl.height
            });
            resource.addCls(layoutCls.layoutCSS || '');

            preferencesLoaded(BQ.Preferences.get('user','ResourceBrowser',{}), resource, layoutCls);
            /*
            BQ.Preferences.get({
                type : 'user',
                key : 'ResourceBrowser',
                callback : Ext.bind(preferencesLoaded, this, [resource, layoutCls], true)
            });
            */
            return resource;
        }
    }
});


/**
 * BaseLayout: Abstract base resource, extends Ext.Container, parent of all other
 * resource types
 *
 * @param {}
 *            config : Includes {resource, layoutKey}. Resource: Passed resource
 *            object, layoutKey : layout key according to which the resource
 *            object will be formatted
 */
Ext.define('Bisque.Resource', {
    extend:'Ext.container.Container',
    operationBarClass: 'Bisque.ResourceBrowser.OperationBar',

    componentCls: 'bq_resource',
    default_view: 'short',

    constructor : function(config)
    {
        Ext.apply(this,
        {
            resource : config.resource,
            browser : config.browser,
            layoutKey : config.layoutKey,
            msgBus : config.msgBus,
            resQ : config.resQ,

            border : false,
            cls : 'LightShadow',
            overCls : 'resource-view-over',
			style: 'float:left;'
        });

        this.callParent(arguments);
        this.manageEvents();
    },

    setLoadingMask : function()
    {
        if (this.getData('fetched')!=1)
            this.setLoading({msg:''});
    },

    GetImageThumbnailRel : function(params, actualSize, displaySize) {
        var ratio = Math.max(actualSize.width/displaySize.width, actualSize.height/displaySize.height);
        var topmargin = ratio<1 ? Math.abs(actualSize.height-displaySize.height)*0.5 : Math.abs(actualSize.height/ratio-displaySize.height)*0.5;
        return  Ext.String.format('<img class="imageCenterHoz" style="\
                    max-width   :   {0}px;  \
                    max-height  :   {1}px;  \
                    margin-top  :   {2}px;" \
                    src         =   "{3}"   \
                    id          =   "{4}"   />',
                    displaySize.width,
                    displaySize.height,
                    topmargin,
                    this.getThumbnailSrc(params),
                    this.resource.uri);
    },

    getThumbnailSrc : function(params)
    {
        return this.resource.src + this.getImageParams(params);
    },

    getImageParams : function(config) {
        var prefs = this.getImagePrefs('ImageParameters') || '?slice=,,{sliceZ},{sliceT}&thumbnail={width},{height}';
        if (config.sliceZ || config.sliceT) {
            prefs = prefs.replace('{sliceZ}', config.sliceZ ? Math.max(config.sliceZ || 1, 1) : '');
            prefs = prefs.replace('{sliceT}', config.sliceT ? Math.max(config.sliceT || 1, 1) : '');
        } else {
            prefs = prefs.replace('slice=,,{sliceZ},{sliceT}&', '');
        }
        prefs = prefs.replace('{width}',  config.width || 280);
        prefs = prefs.replace('{height}', config.height || 280);
        return prefs;
    },

    getImagePrefs : function(key)
    {
        if (this.browser.preferences && this.browser.preferences.Images && this.browser.preferences.Images[key])
            return this.browser.preferences.Images[key];
        return '';
    },

    GetPropertyGrid : function(configOpts, source)
    {
        var propsGrid=Ext.create('Ext.grid.Panel',
        {
            autoHeight : configOpts.autoHeight,
            style : "text-overflow:ellipsis;"+configOpts.style,
            width : configOpts.width,
            store : Ext.create('Ext.data.Store',
            {
                model: 'Ext.grid.property.Property',
                data: source
            }),
            border : false,
            padding : 1,
            multiSelect: true,
            plugins : new Ext.ux.DataTip(
            {
                tpl : '<div>{value}</div>'
            }),

            columns:
            [{
                text: 'Tag',
                flex: 0.8,
                dataIndex: 'name'
            },
            {
                text: 'Value',
                flex: 1,
                dataIndex: 'value'
            }]
        });

        return propsGrid;
    },

    getData : function(tag)
    {
        if (this.resQ)
            return this.resQ.getMyData(this.resource.uri, tag);
    },
    setData : function(tag, value) {this.resQ.storeMyData(this.resource.uri, tag, value);},
    // Resource functions
    prefetch : function(layoutMgr)	//Code to prefetch resource data
    {
    	this.layoutMgr=layoutMgr;
    },
    loadResource : Ext.emptyFn,	//Callback fn when data is loaded

    //Render a default resource view into container when resource data is loaded
    //(can be overridden for a customized view of the resource)
    updateContainer : function()
    {
        // default data shown
        var name = Ext.create('Ext.container.Container', {
            cls : 'lblHeading1',
            html : this.resource.name,
        });

        var type = Ext.create('Ext.container.Container', {
            cls : 'lblHeading2',
            html : this.resource.resource_type,
        });

        var owner = BQApp.userList[this.resource.owner] || {};

        var value = Ext.create('Ext.container.Container', {
            cls : 'lblContent',
            html : owner.display_name,
        });
        var date = Ext.Date.parse(this.resource.ts, BQ.Date.patterns.BisqueTimestamp);
        var ts = Ext.create('Ext.container.Container', {
            cls : 'lblContent',
            html : Ext.Date.format(date, BQ.Date.patterns.ISO8601Long),
        });

        this.add([name, type, value, ts]);
        this.setLoading(false);
    },

    // getFields : returns an array of data used in the grid view
    getFields : function()
    {
        var resource = this.resource, record = BQApp.userList[this.resource.owner];
        var display_name = record ? record.find_tags('display_name') : undefined;
        var name = display_name ? display_name.value : '';
        return ['', resource.name || '', name || '', resource.resource_type, resource.ts, this, {height:21}];
    },

    testAuth1 : function(btn, loaded, permission)
    {
        if (loaded!=true)
        {
            var user = BQSession.current_session.user_uri;
            this.resource.testAuth(user, Ext.bind(this.testAuth1, this, [btn, true], 0));
        }
        else
        {
            if (permission)
                btn.operation.call(this, btn);
            else
                BQ.ui.attention('You do not have permission to perform this action!');
        }
    },

    afterRenderFn : function()
    {
        this.updateContainer();
    },

    manageEvents : function()
    {
    	this.on('afterrender', Ext.Function.createInterceptor(this.afterRenderFn, this.preAfterRender, this));
    },

    preAfterRender : function()
    {
		this.setLoadingMask();	// Put a mask on the resource container while loading
		var el=this.getEl();

        el.on('mouseenter', Ext.Function.createSequence(this.preMouseEnter, this.onMouseEnter, this), this);
		el.on('mousemove', this.onMouseMove, this);
		el.on('mouseleave', Ext.Function.createSequence(this.preMouseLeave, this.onMouseLeave, this), this);
		el.on('click', Ext.Function.createSequence(this.preClick, this.onClick, this), this);
		el.on('contextmenu', this.onRightClick, this);
		el.on('dblclick', Ext.Function.createSequence(this.preDblClick, this.onDblClick, this), this);

		/*
		// dima: taps are really not needed: double should not be needed anymore with edit mode on the browser
		// and single is being imitated as a click, otherwise we're getting multiple clicks...
		if (this.browser.gestureMgr)
			this.browser.gestureMgr.addListener(
			[
				{
					dom: el.dom,
					eventName: 'doubletap',
					listener: Ext.bind(Ext.Function.createSequence(this.preDblClick, this.onDblClick, this), this),
					//options: {holdThreshold:500}
				},
				{
					dom: el.dom,
					eventName: 'singletap',
					listener: Ext.bind(Ext.Function.createSequence(this.preClick, this.onClick, this), this),
				}
			]);
	   */
    },

    preClick : function()
    {
        this.msgBus.fireEvent('ResourceSingleClick', this.resource);
        if (this.browser.selectState !== 'SELECT') return;
        if (!this.el) return; // dima: not sure what this is but it may not exist
    	if (this.el.hasCls('resource-view-selected'))
    	{
    		this.toggleSelect(false);
    		this.fireEvent('unselect', this);
    	}
    	else
    	{
    		this.toggleSelect(true);
    		this.fireEvent('select', this);
    	}
    },

    toggleSelect : function(state)
    {
    	if (state)
    	{
            this.removeCls('LightShadow');
            this.addCls('resource-view-selected')
        }
    	else
    	{
    		this.removeCls('resource-view-selected');
			this.addCls('LightShadow');
    	}
    },

    preDblClick : function()
    {
		this.msgBus.fireEvent('ResourceDblClick', this.resource);
    },

    preMouseEnter : function() {
        this.removeCls('LightShadow');

        if (this.browser.selectState == 'SELECT') {
            if (!this.operationBar) {
                this.operationBar = Ext.create(this.operationBarClass, {
                    renderTo : this.getEl(),
                    resourceCt : this,
                    browser : this.browser,
                    updateItems: this.browser.updateItems,
                    listeners : {
                        removed: this.browser.onOperationRemove,
                        scope: this.browser,
                    },
                });

                this.operationBar.alignTo(this, "tr-tr");
            }

            this.operationBar.setVisible(true);
        }
    },

    preMouseLeave : function()
    {
        if (this.browser.selectState == 'SELECT')
            this.operationBar.setVisible(false);

		if (!this.el.hasCls('resource-view-selected'))
			this.addCls('LightShadow');
    },

    onMouseMove : Ext.emptyFn,

    onMouseEnter : Ext.emptyFn,
    onMouseLeave : Ext.emptyFn,
    onDblClick : Ext.emptyFn,
    onClick : Ext.emptyFn,
    onRightClick : Ext.emptyFn,


    /* Resource operations */
    shareResource : function() {
        var shareDialog = Ext.create('BQ.share.Dialog', {
            resource: this.resource,
        });
    },

    downloadOriginal : function()
    {
        var exporter = Ext.create('BQ.Export.Panel');
        exporter.downloadResource(this.resource, 'none');
    },

    changePrivacy : function(permission, success, failure)
    {
        function loaded(resource, permission, success, failure)
        {
            if  (permission)
                resource.permission = permission;
            else
                resource.permission = (this.resource.permission=='private')?'published':'private';

            resource.append(Ext.bind(success, this), Ext.bind(failure, this));
        }

        BQFactory.request({
            uri :   this.resource.uri + '?view=short',
            cb  :   Ext.bind(loaded, this, [permission, success, failure], 1)
        });
    }
});


Ext.define('Bisque.Resource.Compact', {
    extend : 'Bisque.Resource',
});

Ext.define('Bisque.Resource.Card', {
    extend : 'Bisque.Resource',

    constructor : function() {
        Ext.apply(this, {
            layout : 'fit'
        });

        this.callParent(arguments);
    },

    prefetch : function(layoutMgr) {
        this.callParent(arguments);

        if (!this.getData('fetched')) {
            this.setData('fetched', -1);
            //Loading
            BQFactory.load(this.resource.uri + '/tag?limit=10', Ext.bind(this.loadResource, this));
        }
    },

    loadResource : function(data) {
        this.resource.tags = data.tags;
        var tag, tagProp, tagArr = [], tags = this.getSummaryTags();

        // Show preferred tags first
        for (var i = 0; i < this.resource.tags.length; i++) {
            tag = this.resource.tags[i];
            tagProp = new Ext.grid.property.Property({
                name : tag.name,
                value : tag.value
            });
            (tags[tag.name]) ? tagArr.unshift(tagProp) : tagArr.push(tagProp);
        }

        this.setData('tags', tagArr.slice(0, 7));
        this.setData('fetched', 1);
        //Loaded

        var renderedRef = this.getData('renderedRef')
        if (renderedRef && !renderedRef.isDestroyed)
            renderedRef.updateContainer();
    },

    afterRenderFn : function() {
        this.setData('renderedRef', this);

        if (this.getData('fetched') == 1 && !this.isDestroyed)
            this.updateContainer();
    },

    getSummaryTags : function() {
        return {};
    },

    updateContainer : function() {
        var propsGrid = this.GetPropertyGrid({/*autoHeight:true}*/}, this.getData('tags'));
        propsGrid.determineScrollbars = Ext.emptyFn;

        this.add([propsGrid]);
        this.setLoading(false);
    },

    onMouseMove : Ext.emptyFn,
});



Ext.define('Bisque.Resource.PStrip', {
    extend : 'Bisque.Resource'
});

Ext.define('Bisque.Resource.PStripBig', {
    extend : 'Bisque.Resource',
});

Ext.define('Bisque.Resource.Full', {
    extend : 'Bisque.Resource',

    constructor : function() {
        Ext.apply(this, {
            layout : 'fit'
        });

        this.callParent(arguments);
    },

    afterRenderFn : function() {
        this.setData('renderedRef', this);

        if (this.getData('fetched') == 1 && !this.isDestroyed)
            this.updateContainer();
    },

    prefetch : function(layoutMgr) {
        this.callParent(arguments);

        if (!this.getData('fetched')) {
            this.setData('fetched', -1);
            //Loading
            BQFactory.load(this.resource.uri + '/tag?view=full&limit=100', Ext.bind(this.loadResource, this));
        }
    },

    loadResource : function(data) {
        this.setData('tags', data.tags);
        this.setData('fetched', 1);
        //Loaded

        var renderedRef = this.getData('renderedRef')
        if (renderedRef && !renderedRef.isDestroyed)
            renderedRef.updateContainer();
    },

    updateContainer : function() {
        var propsGrid = this.GetPropertyGrid({/*autoHeight:true}*/}, this.getData('tags'));
        propsGrid.determineScrollbars = Ext.emptyFn;

        this.add([propsGrid]);
        this.setLoading(false);
    },

    onMouseMove : Ext.emptyFn,

});

Ext.define('Bisque.Resource.List', {
    extend : 'Bisque.Resource'
});

// Default page view is a full page ResourceTagger
Ext.define('Bisque.Resource.Page',
{
    extend   :'Ext.panel.Panel',
    defaults : { border: false, },
    layout   : 'fit',
    componentCls: 'bq_resource_page',

    constructor : function(config)
    {
        var name = config.resource.name || '';
        var type = config.resource.resource_type || config.resource.type;

        Ext.apply(this,
        {
            border  :   false,

            tbar    :   Ext.create('Ext.toolbar.Toolbar',
                        {
                            defaults    :   {
                                                scale       :   'medium',
                                                scope       :   this,
                                                needsAuth   :   true,
                                            },
                            items       :   this.getOperations(config.resource).concat([
                                                '-', '->',
                                                {
                                                    itemId      :   'btnOwner',
                                                    iconCls     :   'icon-owner',
                                                    href        :   '/',
                                                    tooltip     :   'Contact the owner of this resource.',
                                                    hidden      :   true,
                                                    needsAuth   :   false,
                                                }, '-',
                                                {
                                                    itemId  :   'btnRename',
                                                    text    :   type + ': <b>' + name + '</b>',
                                                    handler :   this.promptName,
                                                    scope   :   this,
                                                    cls     :   'heading',
                                                },
                                             ])
                        }),
        }, config);

        this.callParent(arguments);

        this.toolbar = this.getDockedComponent(0);

        if (Ext.isEmpty(BQApp.userList))
            BQApp.on('userListLoaded', function(){this.testAuth(BQApp.user, false)}, this);
        else
            this.testAuth(BQApp.user, false);

        //this.addListener('afterlayout', this.onResourceRender, this, {single:true});
        this.addListener('afterlayout', this.onAfterLayout, this, {single:true});
    },

    onAfterLayout : function() {
        this.onResourceRender();
        this.addProvenanceViewer();
    },

    onResourceRender : function()
    {
        this.setLoading(true);

        var resourceTagger = new Bisque.ResourceTagger(
        {
            itemId      :   'resourceTagger',
            title       :   'Annotations',
            resource    :   this.resource,
            split       :   true,
        });

        var resTab = {
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
            items : [resourceTagger]
        };

		// PLEASE REVIEW:
		// default resource viewer: show msg "No viewer associated..."
        var default_viewer = {
            xtype     : 'label',
            text      : 'No viewer is associated with this resource.'
        };
        if (this.createDefaultViewer) {
            default_viewer = this.createDefaultViewer();
        }
        this.add({
            xtype : 'container',
            itemId: 'viewer_container',
            layout : 'border',
            items : [resTab, {
                xtype: 'container',
                itemId: 'main_container',
                region : 'center',
                layout: 'fit',
                items : [default_viewer]
            }]
        });

        //this.add(resourceTagger);
        this.setLoading(false);
    },

    addProvenanceViewer : function() {
        if (!BQ.Preferences.isLoaded('user')) {
            BQ.Preferences.on('update_user_pref', this.addProvenanceViewer, this);
            return;
        }

        // if user preferences request provenance, add this tab now
        // if user wants to see provenance tab, add it now
        var show_provenance = BQ.Preferences.get('user', 'ResourceViewer/Show Provenance', false),
            tabPanel = this.queryById('tabs');
        if (tabPanel && show_provenance) {
            tabPanel.add({
                xtype : 'bq_graphviewer_panel',
                itemId: 'graph',
                title : 'Provenance',
                resource: this.resource,
                resourceType: 'graph_url',
                rankdir: 'LR',
                listeners:{
                    'context' : function(res, div, graph) {
                        var node = graph.g.node(res);
                        window.open(BQ.Server.url(node.card.getUrl(res)));
                    },
                },
            });
        }
    },

    testAuth : function(user, loaded, permission, action)
    {
        function disableOperations(action)
        {
            // user is not authorized
            var tbar = this.getDockedItems('toolbar')[0];
            for (var i=0;i<tbar.items.getCount();i++)
            {
                var cmp = tbar.items.getAt(i);
                if (cmp.needsAuth)
                    cmp.setDisabled(true);
                if (cmp.itemId=='btnDelete' && action=='read')
                    cmp.setDisabled(false);
            }
        }

        if (user)
        {
            if (user.uri!=this.resource.owner)
            {
                var owner = BQApp.userList[this.resource.owner] || {};
                var btn = this.toolbar.getComponent('btnOwner');
                var mailto = Ext.String.format('mailto:{0}?subject={1}&body=Bisque resource -  {2} + ({3}) %0A%0A', owner.email_address,
                    '[Bisque] Regarding ' + this.resource.name, this.resource.name, document.URL);

                btn.setText(owner.display_name || '');

                function setMailTo(btn, mailto) {
                    if (btn.setHref) // works with ExtJS 4.2.1+
                        btn.setHref(mailto);
                    else // dima: Remove once moved away from 4.1
                        btn.getEl().down('a', true).setAttribute('href', mailto);
                    btn.setVisible(true);
                }

                if (btn.getEl())
                    setMailTo(btn, mailto);
                else
                    btn.mon('afterrender', Ext.bind(setMailTo, this, [mailto], 1), this, { single:true });
            }

            if (!loaded)
                this.resource.testAuth(user.uri, Ext.bind(this.testAuth, this, [user, true], 0));
            else
                if (!permission)
                    disableOperations.call(this, action);
        }
        else if (user===undefined)
            // User autentication hasn't been done yet
            BQApp.on('gotuser', Ext.bind(this.testAuth, this, [false], 1));
        else if (user == null)
            disableOperations.call(this)
    },

    getOperations : function(resource)
    {
        // new interface
        var items = [{
            xtype       : 'menuitem',
            itemId      : 'download_original',
            compression : 'none',
            text        : 'Original',
            scope       :   this,
            handler     :   this.downloadResource,
            operation   :   this.downloadResource,
        }, {
            xtype       : 'menuseparator',
            itemId      : 'download_separator',
        }, {
            itemId      : 'download_tar',
            compression : 'tar',
            text        : 'as TARball',
            scope       :   this,
            handler     :   this.downloadResource,
            operation   :   this.downloadResource,
        }, {
            itemId      : 'download_gzip',
            compression : 'gzip',
            text        : 'as GZip archive',
            scope       :   this,
            handler     :   this.downloadResource,
            operation   :   this.downloadResource,
        }, {
            itemId      : 'download_bz2',
            compression : 'bz2',
            text        : 'as BZip2 archive',
            scope       :   this,
            handler     :   this.downloadResource,
            operation   :   this.downloadResource,
        }, {
            itemId      : 'download_zip',
            compression : 'zip',
            text        : 'as (PK)Zip archive',
            scope       :   this,
            handler     :   this.downloadResource,
            operation   :   this.downloadResource,
        }];
        BQApp.add_to_toolbar_menu('button_download', items);

        // old stuff
        var items=[];
        items.push({
            xtype       :   'button',
            text        :   'Download',
            itemId      :   'btnDownload',
            hidden : true,
            iconCls     :   'icon-download-small',
            needsAuth   :   false,
            compression :   'tar',
            menu        :   {
                                defaults    :   {
                                                    group       :   'downloadGroup',
                                                    groupCls    :   Ext.baseCSSClass + 'menu-group-icon',
                                                    scope       :   this,
                                                    handler     :   this.downloadResource,
                                                    operation   :   this.downloadResource,
                                                },
                                items       :   [{
                                                    xtype       :   'menuitem',
                                                    compression :   'none',
                                                    text        :   'Original'
                                                }, {
                                                    xtype       :   'menuseparator'
                                                }, {
                                                    compression :   'tar',
                                                    text        :   'as TARball',
                                                },{
                                                    compression :   'gzip',
                                                    text        :   'as GZip archive',
                                                },{
                                                    compression :   'bz2',
                                                    text        :   'as BZip2 archive',
                                                },{
                                                    compression :   'zip',
                                                    text        :   'as (PK)Zip archive',
                                                },]
                            }
        }, {
            xtype: 'bqresourcepermissions',
            itemId : 'btn_permission',
            resource: resource,
        }, {
            itemId      :   'btnShare',
            text        :   'Share',
            iconCls     :   'icon-group',
            operation   :   this.shareResource,
            handler     :   this.testAuth1
        }, {
            itemId : 'btnDelete',
            text   : 'Delete',
            iconCls: 'icon-delete',
            handler: this.deleteResource,
        });


        return items;
    },

    testAuth1 : function(btn, loaded, permission) {
        if (loaded != true) {
            var user = BQSession.current_session.user_uri;
            this.resource.testAuth(user, Ext.bind(this.testAuth1, this, [btn, true], 0));
        } else {
            if (permission)
                btn.operation.call(this, btn);
            else
                BQ.ui.attention('You do not have permission to perform this action!');
        }
    },

    /* Resource operations */

    shareResource : function() {
        var shareDialog = Ext.create('BQ.share.Dialog', {
            resource: this.resource,
        });
    },

    deleteResource : function() {
        function success() {
            this.setLoading(false);

            Ext.MessageBox.show({
                title : 'Success',
                msg : 'Resource deleted successfully! You will be redirected to your BISQUE homepage.',
                buttons : Ext.MessageBox.OK,
                icon : Ext.MessageBox.INFO,
                fn : function() {
                    window.location = BQ.Server.url('/')
                }
            });
        }

        function deleteRes(response) {
            if (response == 'yes') {
                this.setLoading({
                    msg : 'Deleting...'
                });
                this.resource.delete_(Ext.bind(success, this), Ext.Function.pass(this.failure, ['Delete operation failed!']));
            }
        }

        Ext.MessageBox.confirm('Confirm operation', 'Are you sure you want to delete ' + this.resource.name + '?', Ext.bind(deleteRes, this));
    },

    renameResource : function(btn, name, authRecord) {
        function success(msg) {
            BQ.ui.notification(msg);
            var type = this.resource.resource_type || this.resource.type;
            this.toolbar.getComponent('btnRename').setText(type + ': <b>' + (this.resource.name || '') + '</b>');
        }

        if (btn == 'ok' && this.resource.name != name) {
            var type = this.resource.resource_type || this.resource.type;
            var successMsg = type + ' <b>' + this.resource.name + '</b> renamed to <b>' + name + '</b>.';
            this.resource.name = name;
            this.resource.save_(undefined, success.call(this, successMsg), Ext.bind(this.failure, this));
        }
    },

    downloadResource : function(btn) {
        if (btn.compression == 'none')
            this.downloadOriginal();
        else {
            var exporter = Ext.create('BQ.Export.Panel');
            exporter.downloadResource(this.resource, btn.compression);
        }
    },

    downloadOriginal : function() {
        window.open(this.resource.uri+'?view=deep');
        //var exporter = Ext.create('BQ.Export.Panel');
        //exporter.downloadResource(this.resource, 'none');
    },

    changePrivacy : function(btn) {
        function loaded(resource) {
            resource.permission = (this.resource.permission == 'private') ? 'published' : 'private';
            resource.append(Ext.bind(success, this), Ext.bind(this.failure, this));
        }

        function success(resource) {
            this.setLoading(false);

            // can also broadcast 'reload' event on the resource, once apps start listening to it.
            this.resource.permission = resource.permission;
            var btnPerm = this.toolbar.getComponent('btnPerm');
            btnPerm.setBtnText.call(this, btnPerm);
        };

        this.setLoading({
            msg : ''
        });

        BQFactory.request({
            uri : this.resource.uri + '?view=short',
            cb : Ext.bind(loaded, this)
        });
    },

    promptName : function(btn) {
        Ext.MessageBox.prompt('Rename "' + this.resource.name + '"', 'Please, enter new name:', this.renameResource, this, false, this.resource.name);
    },

    success : function(resource, msg) {
        BQ.ui.notification(msg || 'Operation successful.');
    },

    failure : function(msg) {
        BQ.ui.error(msg || 'Operation failed!');
    },

    prefetch : Ext.emptyFn
});

Ext.define('Bisque.Resource.Grid', {
    extend:'Bisque.Resource',
});

Ext.define('Bisque.Resource.Annotator', {
    extend:'Bisque.Resource',
});

