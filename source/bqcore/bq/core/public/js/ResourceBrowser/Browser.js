// Declare namespace for the modules in RecourseBrowser package
Ext.namespace('Bisque.ResourceBrowser');
Ext.require(['Ext.tip.*']);
Ext.tip.QuickTipManager.init();

/**
 * Browser: Main ResourceBrowser class which acts as an interface between
 * ResourceBrowser and other Bisque components
 *
 * @param {}
 *            browserParams : Initial config parameters such as URI, Offset etc.
 */

// ResourceBrowser in a Ext.Window container

Ext.define('Bisque.ResourceBrowser.Dialog', {
    extend : 'Ext.window.Window',
    alias: 'widget.bqbrowserdialog',

    constructor : function(config) {
        config = config || {
        };
        config.height = config.height || '85%';
        config.width = config.width || '85%';
        config.selType = config.selType || 'MULTI';
        var initial_state = config.selType === 'MULTI' ? 'SELECT' : 'ACTIVATE';
        config.selectState = config.selectState || initial_state;
        config.showOrganizer = ('showOrganizer' in config) ? config.showOrganizer : true;

        var bodySz = Ext.getBody().getViewSize();
        var height = parseInt((config.height.toString().indexOf("%") == -1) ? config.height : (bodySz.height * parseInt(config.height) / 100));
        var width = parseInt((config.width.toString().indexOf("%") == -1) ? config.width : (bodySz.width * parseInt(config.width) / 100));

        Ext.apply(this, {
            layout : 'fit',
            title : 'Resource Browser',
            modal : true,
            border : false,
            height : height,
            width : width,
            items : new Bisque.ResourceBrowser.Browser(config),
            buttonAlign: 'center',
            buttons: [{
                text : 'Select',
                iconCls : 'icon-select',
                handler : this.btnSelect,
                scale: 'large',
                scope: this,
            }, {
                text : 'Cancel',
                iconCls : 'icon-cancel',
                handler : this.destroy,
                scale: 'large',
                scope: this,
            }],
        }, config);

        this.callParent([arguments]);

        // Relay all the custom ResourceBrowser events to this Window
        //this.relayEvents(this.getComponent(0), ['Select']);

        this.browser = this.getComponent(0);
        this.browser.on('Select', function(resourceBrowser, resource) {
            this.destroy();
        }, this);

        var me = this;
        if (config.selection) {
            setTimeout( function() { me.doSelect(config.selection); }, 300 );
        }

        this.show();
    },

    btnSelect : function() {
        var selectedRes = this.browser.resourceQueue.selectedRes;
        if (selectedRes instanceof Bisque.Resource) {
            var selection = [selectedRes];
        } else {
            var selection = Ext.Object.getValues(selectedRes);
        }
        var dir = this.browser.getSelectedFolder();

        if (selection.length) {
            if (selection.length === 1)
                this.browser.fireEvent('Select', this, selection[0].resource);
            else {
                for (var i = 0, selectRes = []; i < selection.length; i++)
                    selectRes.push(selection[i].resource);
                this.browser.fireEvent('Select', this, selectRes);
            }
            return;
        } else if (selection.length===0 && dir) {
            this.browser.fireEvent('Select', this, dir);
            return;
        }

        BQ.ui.notification('Selection is empty. Please select an image or press cancel to abort.');
    },

    doSelect: function(selection) {
        if (!this.browser) return;
        this.browser.doSelect(selection);
    },
});

// Bisque.QueryBrowser.Dialog is a query select specialization of Bisque.ResourceBrowser.Dialog
Ext.define('Bisque.QueryBrowser.Dialog', {
    extend : 'Bisque.ResourceBrowser.Dialog',

    btnSelect : function() {
        var query = this.browser.commandBar.getComponent('searchBar').getValue();
        if (query && query.length > 1)
            this.browser.fireEvent('Select', this, query);
        else
            BQ.ui.message('Query is empty!', 'Please type a query or press cancel to abort.');
    },
});

// ResourceBrowser in a Ext.Panel container
Ext.define('Bisque.ResourceBrowser.Browser', {
    extend : 'Ext.panel.Panel',
    alias : 'widget.bq-resource-browser',
    componentCls: 'browser',

    width: '100%',
    height: '100%',

    constructor : function(config) {
        //Prefetch the loading spinner
        var me = this;
        var imgSpinner = new Image();
        imgSpinner.src = BQ.Server.url('/core/js/ResourceBrowser/Images/loading.gif');

        //organizer tab panel
        this.westPanel = Ext.create('Ext.tab.Panel', { //Ext.create('Ext.panel.Panel', {
            region : 'west',
            plain : true,
            width: 420,
            border: 0,
            activeTab : 0,
            split : true,
            layout : 'fit',
            cls : 'organizer-tabs',
            frame : true,
            header : false,
            hidden : true,
            collapsible : true,
            hideCollapseTool : true,
            //deferredRender: true,
            listeners : {
                beforecollapse : function(me) {
                    me.setTitle(me.getComponent(0).title);
                },
                tabchange : function(tabPanel, newCard, oldCard, eOpts) {
                    if (newCard.setActive)
                        newCard.setActive();
                },
            }
        });

        this.centerPanel = new Ext.Panel({
            region : 'center',
            border : false,
            layout : 'fit',
            flex: 1,
        });
        config = config || {};

        Ext.apply(this, {
            browserParams : config,
            layoutKey : parseInt(config.layout),
            viewMgr : Ext.create('Bisque.ResourceBrowser.viewStateManager', config.viewMode),
            organizerCt : null,
            datasetCt : null,
            layoutMgr : null,
            browserState : {},
            resourceQueue : [],
            msgBus : new Bisque.Misc.MessageBus(),
            gestureMgr : null,
            showGroups : false,
            preferenceKey : 'ResourceBrowser',

            //bodyCls : 'background-transparent',
            bodyCls : 'browser-main',
            // Panel related config
            border : false,
            title : config.title || '',
            layout : 'border',
            items : [this.westPanel, this.centerPanel],
            listeners : config.listeners || {},
        }, config);

        this.commandBar = new Bisque.ResourceBrowser.CommandBar({
            browser : this
        });
        this.tbar = this.commandBar;

        this.addEvents({
            'removed' : true,
        });

        this.callParent([arguments]);

        //load preferences
        var me = this;

        //need to be called before bq_ui_application onGotUser or a load preferences
        //needs to be called to initialize this component
        BQ.Preferences.on('update_user_pref', this.onPreferences, this);
        BQ.Preferences.on('onerror_user_pref', this.onPreferences, this);
        if ('user' in BQ.Preferences.preferenceXML) this.onPreferences();

        if (Ext.supports.Touch)
            this.gestureMgr = new Bisque.Misc.GestureManager();
    },


    onPreferences : function() {
        this.preferences = {};

        //this.applyPreferences();

        var accType = this.browserParams.accType || 'image';

        // defaults (should be loaded from system preferences)
        Ext.apply(this.browserParams, {
            layout : this.browserParams.layout || 1,
            dataset : this.browserParams.dataset || '/data_service/'+accType+'/',
            offset : this.browserParams.offset || 0,
            tagQuery : this.browserParams.tagQuery || '',
            tagOrder : this.browserParams.tagOrder || '"@ts":desc',
            wpublic : this.browserParams.wpublic,
            selType : (this.browserParams.selType || 'SINGLE').toUpperCase()
        });

        if (this.browserParams.tagOrder === '"@ts":desc')
            this.browserParams.tagOrder = BQ.Preferences.get('user', 'ResourceBrowser/Browser/Sorting', this.browserParams.tagOrder);
        this.browserState['offset'] = this.browserParams.offset;
        this.layoutKey = this.layoutKey || this.browserParams.layout;
        //this.showOrganizer = true;
        //if ('showOrganizer' in this.browserParams)
        this.showOrganizer = this.browserParams.showOrganizer || false;
        this.showModuleOrganizer = this.browserParams.showModuleOrganizer || false;
        this.selectState = this.browserParams.selectState || 'ACTIVATE';

        if (!this.browserParams.viewMode) {
            if (!this.browserParams.tagQuery)
                this.browserParams.tagQuery = BQ.Preferences.get('user', 'ResourceBrowser/Browser/Tag Query', this.browserParams.tagQuery);

            //all these check for backwards comparability; if there is not template a user can set any of the layout types
            var prefLayout = BQ.Preferences.get('user', 'ResourceBrowser/Browser/Layout', this.browserParams.layout);
            var layout = (parseInt(prefLayout)!=parseInt(prefLayout))? Bisque.ResourceBrowser.LayoutFactory.LAYOUT_KEYS[prefLayout] : parseInt(prefLayout);
            this.layoutKey = (!layout) ? this.browserParams.layout : layout; //layout key must be an int

            this.browserParams.wpublic = BQ.Preferences.get('user', 'ResourceBrowser/Browser/Default visibility', this.browserParams.wpublic);
        }

        this.commandBar.applyPreferences();

        // TODO: is the following even correct here? why does the dataset get loaded here in onPreferences?
        if (this.browserParams.dataset != "None" && !this.dataset_loaded) {
            this.dataset_loaded = true;    // prevent duplicate loads if onPreferences is called multiple times
            var baseURL = (this.browserParams.dataset instanceof BQDataset) ? this.browserParams.dataset.uri + '/value' : this.browserParams.dataset;
            this.loadData({
                baseURL : baseURL,
                offset : this.browserParams.offset,
                tag_query : this.browserParams.tagQuery,
                tag_order : this.browserParams.tagOrder
            });
            var btnOrganize = this.commandBar.getComponent("btnGear").menu.getComponent("btnOrganize");
            this.showOrganizer ? btnOrganize.handler.call(this.commandBar) : '';
            if (this.showModuleOrganizer) {
                this.initModuleOrganizer();
            }
        }
    },

    loadData : function(uri) {
        this.loading = true;
        this.on('afterlayout', function(me) {
            me.centerPanel.setLoading(me.loading);
        });

        this.centerPanel.setLoading({
            msg : ''
        });
        uri = uri || null;

        if (uri) {
            if (uri.tag_query == undefined)
                uri.tag_query = this.browserState.tag_query || '';
            if (uri.tag_order == undefined)
                uri.tag_order = this.browserState.tag_order || '';
            if (uri.offset == undefined)
                uri.offset = this.browserState.offset;
            if (uri.wpublic === undefined)
                uri.wpublic = this.browserParams.wpublic;

            if (!uri.baseURL)
                uri.baseURL = this.browserState.baseURL;

            if (uri.tag_order === undefined || !uri.tag_order.match(/"@(\w+)":(asc|desc|ASC|DESC)/)) {
                var btn = this.commandBar.getComponent("btnTS"),
                    sorting = Ext.String.format('"{0}":{1}', btn.sortAttribute, btn.sortOrder.toLowerCase());
                if (uri.tag_order && uri.tag_order != '') {
                    uri.tag_order += ',' + sorting;
                } else {
                    uri.tag_order = sorting;
                }
            }

            this.setBrowserState(uri);
        } else
            var uri = this.getURIFromState();

        if (uri.tag_order) {
            var order = uri.tag_order.split(','),
                tags = [],
                values = [],
                p = null;

            for (var i=0; (p=order[i]); ++i) {
                var m = p.match(/"@(\w+)":(asc|desc|ASC|DESC)/);
                if (!m || m.length!==3) {
                //if (p.indexOf('@')<0) {
                    p = p.split(':');
                    tags.push(p[0].replace(/"/g, ''));
                    values.push(p[1].toUpperCase());
                }
            }

            uri.view = tags.join(',');
            if (tags.length >= 1)
                this.showGroups = {
                    tags : tags,
                    order : values
                };
            else
                this.showGroups = false;
        } else
            //this.showGroups is used in LayoutFactory to group resources based on tag order
            this.showGroups = false;

        function loadQueue(membersTag) {
            if (membersTag)
                this.uri.baseURL = membersTag.uri + '/value';
            this.browserState['baseURL'] = this.uri.baseURL;

            for (var param in this.uri) {
                var p = this.uri[param];
                if (typeof p === "undefined" || p === null || (p.hasOwnProperty(length) && p.length<1))
                    delete this.uri[param];
            }

            this.resourceQueue = new Bisque.ResourceBrowser.ResourceQueue();
            this.resourceQueue.init({
                callBack : callback(this, 'dataLoaded'),
                browser : this,
                uri : this.uri
            });
        }


        this.uri = uri;
        // if baseURL is typeof BQResource (BQDataset etc.) then load its members
        if (uri.baseURL instanceof BQDataset)
            uri.baseURL.getMembers(Ext.bind(loadQueue, this));
        else
            loadQueue.call(this);
    },

    dataLoaded : function() {
        function doLayout() {
            this.ChangeLayout(this.layoutKey);

            if (!this.eventsManaged)
                this.ManageEvents();
        }


        this.fireEvent('browserLoad', this, this.resourceQueue);

        if (this.rendered)
            doLayout.call(this);
        else
            this.on('afterlayout', Ext.bind(doLayout, this), {
                single : true
            });
    },

    ChangeLayout : function(newLayoutKey, direction) {
        //console.time("Browser - ChangeLayout");
        this.loading = false;
        this.centerPanel.setLoading(this.loading);

        direction = direction || 'none';

        if (this.layoutMgr)
            this.layoutMgr.destroy();

        this.layoutKey = newLayoutKey == -1 ? this.layoutKey : newLayoutKey;

        this.layoutMgr = Bisque.ResourceBrowser.LayoutFactory.getLayout({
            browser : this,
            direction : direction
        });

        this.resourceQueue.changeLayout({
            key : this.layoutKey,
            layoutMgr : this.layoutMgr
        });

        this.layoutMgr.Init(this.resourceQueue.getMainQ(this.layoutMgr.getVisibleElements(direction), this.layoutMgr));
        this.centerPanel.add(this.layoutMgr);

        this.updateTbarItemStatus();

        //console.timeEnd("Browser - ChangeLayout");
    },

    /* Custom ResourceBrowser event management */
    ManageEvents : function() {
        this.eventsManaged = true;
        this.addEvents('Select');
        this.changeLayoutThrottled = Ext.Function.createThrottled(this.ChangeLayout, 400, this);
        this.centerPanel.on('resize', Ext.bind(this.ChangeLayout, this, [-1]));

        this.centerPanel.getEl().on('mousewheel', function(e) {
            if (this.layoutMgr.key != Bisque.ResourceBrowser.LayoutFactory.LAYOUT_KEYS.Full &&
                this.layoutMgr.key != Bisque.ResourceBrowser.LayoutFactory.LAYOUT_KEYS.Annotator) {
                if (e.getWheelDelta() > 0) {
                    var btnLeft = this.commandBar.getComponent("btnLeft");
                    if (!btnLeft.disabled)
                        btnLeft.handler.call(btnLeft.scope, btnLeft);
                } else {
                    var btnRight = this.commandBar.getComponent("btnRight");
                    if (!btnRight.disabled)
                        btnRight.handler.call(btnRight.scope, btnRight);
                }
            }
        }, this);

        Ext.create('Ext.util.KeyMap', {
            target : Ext.getDoc(),
            binding : [{
                key : "aA",
                ctrl : true,
                handler : function(key, e) {
                    this.layoutMgr.toggleSelectAll();
                },
                defaultEventAction : 'stopEvent',
                scope : this
            }, {
                key: 32,
                scope: this,
                fn: function() {
                    var btnRight = this.commandBar.getComponent("btnRight");
                    if (!btnRight.disabled)
                        btnRight.handler.call(btnRight.scope, btnRight);
                }
            }]
        });

        this.msgBus.mon(this.msgBus, {
            'ResourceDblClick' : function(resource) {
                // check if its dir or local
                if (resource.resource_type === 'dir' || resource.resource_type === 'store') {
                    //this.fireEvent('directory', this, resource);
                    if (!this.commandBar) return;
                    if (!this.commandBar.westPanel) return;
                    var ft = this.commandBar.westPanel.queryById('files');
                    var path = ft.getSelected();
                    if (resource.resource_type === 'store')
                        path += '/store';
                    path += '/'+ resource.name;
                    path = path.replace('//', '/');
                    ft.setPath(path);
                    return;
                }
                if (this.browserParams.selType == 'MULTI' && this.selectState == 'ACTIVATE')
                    this.fireEvent('Select', this, resource);
            },

            'ResourceSingleClick' : function(resource) {
                // check if its dir or local
                if (resource.resource_type === 'dir' || resource.resource_type === 'store') {
                    //this.fireEvent('directory', this, resource);
                    if (!this.commandBar) return;
                    if (!this.commandBar.westPanel) return;
                    var ft = this.commandBar.westPanel.queryById('files');
                    var path = ft.getSelected();
                    if (resource.resource_type === 'store')
                        path += '/store';
                    path += '/'+ resource.name;
                    path = path.replace('//', '/');
                    ft.setPath(path);
                    return;
                }
                if (this.browserParams.selType === 'SINGLE' && this.selectState === 'ACTIVATE')
                    this.fireEvent('Select', this, resource);
            },

            ResSelectionChange : function(selection) {
                this.fireEvent('ResSelectionChange', this, this.getSelection());
            },

            'Browser_ReloadData' : function(uri) {
                //var btnOrganize = this.commandBar.getComponent("btnGear").menu.getComponent("btnOrganize");
                //this.showOrganizer?btnOrganize.handler.call(this.commandBar, true):'';

                if (uri == "") {
                    this.resourceQueue = new Bisque.ResourceBrowser.ResourceQueue({
                        callBack : callback(this, 'ChangeLayout', this.layoutKey),
                        browser : this,
                        uri : ""
                    });
                } else if (uri == 'ReloadPrefs') {
                    var user = BQSession.current_session.user;

                    if (user) {
                        BQ.Preferences.load('user');
                        this.browserParams = {
                        };
                    }
                } else
                    this.loadData(uri);
            },

            scope : this
        });

        // HTML5 Gestures (iPad/iPhone/Android etc.)
        if (this.gestureMgr)
            this.gestureMgr.addListener({
                dom : this.centerPanel.getEl().dom,
                eventName : 'swipe',
                listener : Ext.bind(function(e, params) {
                    if (params.direction == "left") {
                        var btnRight = this.commandBar.getComponent("btnRight");
                        if (!btnRight.disabled)
                            btnRight.handler.call(btnRight.scope, btnRight);
                    } else {
                        var btnLeft = this.commandBar.getComponent("btnLeft");
                        if (!btnLeft.disabled)
                            btnLeft.handler.call(btnLeft.scope, btnLeft);
                    }
                }, this),

                options : {
                    swipeThreshold : 100
                }
            });
    },

    setBrowserState : function(uri) {
        this.browserState['baseURL'] = uri.baseURL;
        this.browserState['tag_query'] = uri.tag_query;
        this.browserState['wpublic'] = this.browserParams.wpublic;
        this.browserState['layout'] = this.layoutKey;
        this.browserState['tag_order'] = uri.tag_order;
    },

    updateTbarItemStatus : function() {
        var btnRight = this.commandBar.getComponent("btnRight"), btnLeft = this.commandBar.getComponent("btnLeft");
        var st = this.resourceQueue.getStatus();

        this.commandBar.setStatus(st);

        btnLeft.setDisabled(st.left || st.loading.left);
        btnRight.setDisabled(st.right || st.loading.right);

        this.commandBar.slider.slider.setDisabled(btnLeft.disabled && btnRight.disabled);
        this.commandBar.btnTSSetState(this.browserState.tag_order);
        this.commandBar.btnSearchSetState(this.browserState.tag_query);
        this.commandBar.btnActivateSetState(this.selectState);
    },

    getURIFromState : function() {
        var uri = {
            baseURL : this.browserState.baseURL,
            offset : this.browserState.offset,
            tag_query : this.browserState.tag_query || '',
            tag_order : this.browserState.tag_order || '',
            wpublic : this.browserParams.wpublic
        };

        for (var param in uri) {
            var v = uri[param];
            if (typeof v === 'undefined' || v === null || v === '')
                delete uri[param];
        }

        return uri;
    },

    findRecord : function(uri) {
        return this.resourceQueue.find(uri);
    },

    onOperationRemove : function(selection, needs_reload) {
        this.fireEvent( 'removed', selection, needs_reload );
    },

    getSelectedFolder : function() {
        if (!this.commandBar) return undefined;
        if (!this.commandBar.westPanel) return undefined;
        var ft = this.commandBar.westPanel.queryById('files');
        if (!ft) return undefined;
        var path = ft.getSelectedAsResource();
        return path;
    },

    initModuleOrganizer : function() {
        this.add({
            xtype: 'modulegroups',
            region : 'west',
            title: 'Groups',
            width: 300,
            border: 0,
            split : false,
            cls : 'organizer-modules',
            collapsible : true,
            hideCollapseTool : true,
            //deferredRender: true,
            listeners : {
                scope: this,
                selected_group : function(group) {
                    var q = this.browserState.tag_query,
                        and = encodeURIComponent(' and '),
                        pos = q.indexOf(and+'group:');

                    if (pos===-1) {
                        pos = q.indexOf('group:');
                    }

                    // remove group from query
                    if (pos>=0) {
                        q = q.substr(0, pos);
                    }

                    if (group) {
                        if (q.length>0) {
                            q += and;
                        }
                        q += 'group:"'+encodeURIComponent(group)+'"';
                    }

                    this.loadData({
                        tag_query: q,
                    });
                },
            }
        });
    },

    activateAutoReload: function() {
        var me = this,
            delay_timeout = 60000;
        if (!me.task_reload) {
            me.task_reload = new Ext.util.DelayedTask( function() {
                Ext.log(">>>>>>>>>> BROWSER RELOAD");
                me.loadData(me.uri);
                if (me.isVisible())
                    me.task_reload.delay(delay_timeout);
            });
        }
        me.task_reload.delay(delay_timeout);
    },

    doSelect: function(selection) {
        var rq = this.resourceQueue,
            r = null;
        for (var i=0; (r=rq[i]); ++i) {
            if (r.resource.resource_uniq in selection) {
                r.toggleSelect(true);
                rq.selectedRes[r.resource.uri] = r;
            }
        }
        // re-render
        this.ChangeLayout(this.layoutKey);
    },

    getSelection: function() {
        var selection = this.resourceQueue.selectedRes;
        if (selection instanceof Bisque.Resource) {
            selection = [selection];
        } else {
            selection = Ext.Object.getValues(selection);
        }

        if (selection.length) {
            for (var i = 0; i < selection.length; i++)
                selection[i] = selection[i].resource;
        }

        return selection;
    },

    doFullScreen: function () {
        var maximized = (document.fullscreenElement || document.mozFullScreenElement || document.webkitFullscreenElement || document.msFullscreenElement),
            vd = this.getEl().dom,
            me = this,
            has_fs = vd.requestFullscreen || vd.webkitRequestFullscreen || vd.msRequestFullscreen || vd.mozRequestFullScreen;
        if (!has_fs) return;

        if (!maximized) {
            if (vd.requestFullscreen) {
                vd.requestFullscreen();
            } else if (vd.webkitRequestFullscreen) {
                vd.webkitRequestFullscreen();
            } else if (vd.msRequestFullscreen) {
                vd.msRequestFullscreen();
            } else if (vd.mozRequestFullScreen) {
                vd.mozRequestFullScreen();
            }

            /*
            vd.style.width='100%';
            vd.style.height='100%';

            setTimeout( function() {
                var width = document.body.clientWidth,
                    height = document.body.clientHeight;
                console.log('Resizing to '+width+','+height);
                //vd.style.width='100%';
                //vd.style.height='100%';
                me.setSize(width, height);
                me.updateLayout({
                    defer: true,
                    isRoot: false,
                });
            }, 1000);
            */

        } else {
            if (document.exitFullscreen) {
                document.exitFullscreen();
            } else if (document.webkitExitFullscreen) {
                document.webkitExitFullscreen();
            } else if (document.msExitFullscreen) {
                document.msExitFullscreen();
            } else if (document.mozCancelFullScreen) {
                document.mozCancelFullScreen();
            }
        };
    },

});


//-----------------------------------------------------------------------
// BQ.grid.ModuleGroups
//-----------------------------------------------------------------------

Ext.define('BQ.grid.ModuleGroups', {
    extend: 'Ext.grid.Panel',
    alias: 'widget.modulegroups',

    componentCls: 'bq-organizer-module',
    hideHeaders: true,
    allowDeselect: true,
    viewConfig: {
        stripeRows: true,
        forceFit: true,
    },

    initComponent : function() {
        if (!BQ || !BQ.model || !BQ.model.ModuleGroups) {
            Ext.define('BQ.model.ModuleGroups', {
                extend: 'Ext.data.Model',
                fields: [{ name: 'value', mapping: '@value' }],
            });
        }
        this.store = Ext.create('Ext.data.Store', {
            model: 'BQ.model.ModuleGroups',
            autoLoad: true,
            autoSync: false,

            proxy: {
                noCache: false,
                headers : { 'Cache-Control': 'max-age' },
                type: 'rest',
                limitParam: undefined,
                pageParam: undefined,
                startParam: undefined,

                url: '/data_service/module?tag_values=group&wpublic=true',
                reader: {
                    type: 'xml',
                    root: 'resource',
                    record: '>tag',
                },
            },
        });

        this.columns = [{
            text: "Group",
            flex: 1,
            dataIndex: 'value',
            sortable: true
        }];

        this.callParent();
        this.on('selectionchange', this.onselected, this);
    },

    onError : function() {
        this.setLoading(false);
        BQ.ui.error('Problem fetching available module groups');
    },

    onselected: function(me, selected) {
        if (selected.length<1) {
            this.fireEvent('selected_group', undefined);
        } else {
            this.fireEvent('selected_group', selected[0].data.value);
        }
    },

});


//-----------------------------------------------------------------------
// wrapper for module browser to only load data after render
//-----------------------------------------------------------------------

Ext.define('Bisque.ModuleBrowser.Browser', {
    extend: 'Ext.container.Container',
    alias: 'widget.bq-module-browser',
    layout: 'fit',

    afterRender : function() {
        this.callParent();
        this.add({
            xtype: 'bq-resource-browser',
            itemId: 'analysis_organizer',

            layout: Bisque.ResourceBrowser.LayoutFactory.LAYOUT_KEYS.IconList,
            selType: 'SINGLE',
            viewMode: 'ModuleBrowser',
            //showOrganizer: true,
            showModuleOrganizer: true,

            baseURL: this.baseURL || '/module_service/',
            dataset: this.dataset || '/module_service/',
            offset: this.offset || 0,
            tag_order: '"@name":asc',
            tagOrder: '"@name":asc',
            tag_query: this.tag_query,
            wpublic: this.wpublic || 'owner',

        });
        this.relayEvents(this.queryById('analysis_organizer'), ['Select']);
    },

    initQuery : function(q) {
        var a = this.queryById('analysis_organizer');
        if (!a) {
            this.baseURL   = q.baseURL || this.baseURL;
            this.dataset   = q.dataset || this.dataset;
            this.offset    = q.offset || this.offset;
            this.tag_order = q.tag_order || this.tag_order;
            this.tagOrder = q.tagOrder || this.tagOrder;
            this.tag_query = q.tag_query || this.tag_query;
            this.wpublic   = q.wpublic || this.wpublic;
            return;
        }

        if (!a.preferences) {
            a.browserParams.dataset = q.dataset || this.dataset;
            a.browserParams.tagQuery = q.tag_query;
            a.browserParams.wpublic = q.wpublic || this.wpublic;
        } else {
            a.loadData({
                baseURL: q.baseURL || this.baseURL,
                dataset: q.dataset || this.dataset,
                offset: q.offset || this.offset,
                tag_order: q.tag_order || this.tag_order,
                tagOrder: q.tagOrder || this.tagOrder,
                tag_query: q.tag_query,
                wpublic: q.wpublic || this.wpublic,
            });
        }
    },

});
