/*******************************************************************************

  BQ.renderers.dataset  -

  Author: Dima Fedorov

  Version: 1

  History:
    2011-09-29 13:57:30 - first creation

*******************************************************************************/

Ext.define('BQ.renderers.dataset', {
    alias: 'widget.renderersdataset',
    extend: 'Bisque.Resource.Page',
    requires: ['Ext.toolbar.Toolbar', 'Ext.tip.QuickTipManager', 'Ext.tip.QuickTip', 'BQ.dataset.Panel'],

    border: 0,
    autoScroll: false,
    layout : 'border',
    heading: 'Dataset',
    cls : 'bq-dataset',
    defaults: { border: 0, },

    onResourceRender : function() {
        this.setLoading('Fetching members...', true);
        this.tagger = Ext.create('Bisque.ResourceTagger', {
            resource : this.resource,
            title : 'Annotations',
        });

        /*
        this.operations = Ext.create('BQ.dataset.Panel', {
            title : 'Operations',
            dataset : this.resource,
            listeners: { 'done': this.onDone,
                         'error': this.onError,
                         'removed': this.onremoved,
                         'chnaged': this.changedOk,
                         scope: this },
        });*/

        //var mexs = Ext.create('Bisque.ResourceBrowser.Browser', {
        var mexs = {
            xtype: 'bq-resource-browser',
            layout : 5,
            title : 'Analysis',
            viewMode : 'MexBrowser',
            dataset : '/data_service/mex',
            tagQuery : '"'+this.resource.uri+'"',
            wpublic : true,
            mexLoaded : false,
            listeners : {
                'browserLoad' : function(me, resQ) {
                    me.mexLoaded = true;
                },
                'Select' : function(me, resource) {
                    window.open(BQ.Server.url('/module_service/'+resource.name+'/?mex='+resource.uri));
                },
                scope:this
            },
        };

        var map = undefined;
        if (this.loadmap) map = {
            xtype: 'bqmap',
            title: 'Map',
            zoomLevel: 16,
            gmapType: 'map',
            autoShow: true,
            resource: this.resource,
        };

        var tabber = {
            xtype: 'tabpanel',
            region : 'east',
            activeTab : 0,
            border : false,
            bodyBorder : 0,
            collapsible : true,
            split : true,
            flex: 1,
            plain : true,
            title : 'Annotate and modify',
            //collapsed: true,

            //items : [this.tagger, mexs, this.operations, map]
            items : [this.tagger, mexs, map]
        };

        this.preview = Ext.create('Bisque.ResourceBrowser.Browser', {
            xtype: 'bq-resource-browser',
            region:'center',
            flex: 3,
            dataset: this.resource?this.resource:'None',
            //title : 'Item browser',
            tagOrder: '"@ts":desc',
            //selType: 'SINGLE',
            //wpublic: false,
            showOrganizer : true,
            viewMode: 'ViewerLayouts',
            updateItems : this.updateOperationItems,
            listeners: {
                'Select': function(me, resource) {
                    window.open(BQ.Server.url('/client_service/view?resource='+resource.uri));
                },
                'SelectMode_Change': Ext.bind(this.onmodechange, this),
                removed: this.removeResources,
                scope: this,
            },
        });

        //--------------------------------------------------------------------------------------
        // toolbars
        //--------------------------------------------------------------------------------------
        var n = this.toolbar.items.getCount()-4;
        this.toolbar.insert( n, [{
                itemId: 'menu_add_images',
                xtype:'splitbutton',
                text: 'Add images',
                iconCls: 'icon_plus',
                scope: this,
                //disabled: true,
                tooltip: 'Add resources into the dataset',
                //cls: 'x-btn-default-medium',
                handler: function() { this.browseResources('image'); },
            }, /*{
                itemId: 'menu_delete_selected',
                text: 'Remove selected',
                tooltip: 'Remove selected resource from the dataset, keeps the resource untouched',
                scope: this,
                iconCls: 'icon_minus',
                disabled: true,
                //cls: 'x-btn-default-medium',
                handler: this.removeSelectedResources,
            }, { itemId: 'menu_delete',
                text: 'Delete',
                //icon: this.images_base_url+'upload.png',
                handler: this.remove,
                scope: this,
                iconCls: 'icon_x',
                tooltip: 'Delete current dataset, keeps all the elements untouched',
            },*/
            '-',
            /*'->',
            {
                itemId: 'menu_rename',
                text: 'Dataset: <b>'+this.resource.name+'</b>',
                cls: 'heading',
                scope: this,
                tooltip: 'Rename the dataset',
                //cls: 'x-btn-default-medium',
                handler: this.askRename,
            },*/
        ]);

        // setup dataset service
        this.dataset_service = Ext.create('BQ.dataset.Service', {
            listeners: {
                'running': this.onDatasetRunning,
                'success': this.onDatasetSuccess,
                'error': this.onDatasetError,
                scope: this,
            },
        });

        // modify buttons
        var btn_delete = this.toolbar.queryById('btnDelete');
        btn_delete.setHandler(undefined);
        btn_delete.menu = Ext.create('Ext.menu.Menu', {
            items: [{
                text: 'Delete dataset and all its elements',
                handler: this.remove,
                scope: this,
            },{
                text: 'Delete dataset only and keep elements',
                handler: this.deleteResource,
                scope: this,
            }],
        });

        var btn_permissions = this.toolbar.queryById('btn_permission');
        btn_permissions.on('changePermission', this.onChangePermission, this);


        // finish setup
        this.add( [this.preview, tabber] );
        this.setLoading(false);

        this.fetchResourceTypes();

        if (!BQSession.current_session)
            BQFactory.request( {uri: '/auth_service/session', cb: callback(this, 'onsession') });
        else
            this.onsession(BQSession.current_session);

    },

    onsession: function (session) {
        this.user_uri = session && session.user_uri?session.user_uri:null;
        if (this.user_uri) return;
        var tb = this.toolbar;
        tb.child('#menu_add_images').setDisabled(true);
        //tb.child('#menu_query').setDisabled(true);
        //tb.child('#menu_delete_selected').setDisabled(true);
        //tb.child('#menu_delete').setDisabled(true);
        //this.operations.setDisabled(true);
    },

    onDone: function(panel) {
        BQ.ui.notification('Done<br><br>'+panel.getStatus());
    },

    onError: function(panel) {
        BQ.ui.error('Error<br><br>'+panel.getStatus());
    },

    fetchResourceTypes : function() {
        BQFactory.request ({uri : '/data_service/',
                            cb : callback(this, 'onResourceTypes'),
                            cache : false});
    },

    onResourceTypes : function(resource) {
        //this.addResourceTypes(resource, '#menu_add_images', 'addResourceTypeMenu');
        //this.addResourceTypes(resource, '#menu_query', 'addResourceQueryMenu');
        this.addResourceTypes(resource, '#menu_add_images');
    },

    addResourceTypes : function(resource, button_id, f) {
        var ignore = { 'user':null, 'module':null, 'service':null, 'system':null, };
        var menu = Ext.create('Ext.menu.Menu');
        var r=null;
        for (var i=0; (r=resource.children[i]); i++) {
            if (r.name in ignore) continue;
            //this[f](menu, r.name);
            this.addResourceTypeMenu(menu, r.name);
        }

        //
        menu.add('-');
        for (var i=0; (r=resource.children[i]); i++) {
            if (r.name in ignore) continue;
            this.addResourceQueryMenu(menu, r.name);
        }

        this.toolbar.child(button_id).menu = menu;
    },

    addResourceTypeMenu : function(menu, name) {
        menu.add( {text: 'Add <b>'+name+'</b>',
                   handler: function() { this.browseResources(name); },
                   scope: this,
                  } );
    },

    addResourceQueryMenu : function(menu, name) {
        menu.add( {text: 'Add <b>'+name+'</b> from query',
                   handler: function() { this.browseQuery(name); },
                   scope: this,
                  } );
    },

    changedOk : function() {
        this.setLoading(false);
        // reload the browser
        this.preview.msgBus.fireEvent('Browser_ReloadData', { offset: 0, });
        // reload resource for tagger
        this.tagger.reload();

        //this.toolbar.child('#menu_rename').setText('Dataset: <b>'+this.resource.name+'</b>');
    },

    changedError : function(o) {
        this.setLoading(false);
        BQ.ui.error('Error creating resource: <br>'+o.message_short);
    },

    checkAllowWrites : function(warn) {
        var session = BQSession.current_session;
        this.user_uri = session && session.user_uri?session.user_uri:null;
        // dima: this is an incomplete solution, will return true for every logged-in user, even without write ACL!
        if (warn && !this.user_uri)
            BQ.ui.warning('You don\'t have enough access to modify this resource!');
        return this.user_uri;
    },

    browseResources: function(resource_type) {
        if (!this.checkAllowWrites(true)) return;
        var resourceDialog = Ext.create('Bisque.ResourceBrowser.Dialog', {
            'height'  : '85%',
            'width'   :  '85%',
            //wpublic   : 'true',
            dataset   : '/data_service/'+resource_type,
            listeners : {
                'Select' : this.addResources,
                scope: this
            },
        });
    },

    addResources : function(browser, sel) {
        if (!this.checkAllowWrites(true)) return;
        this.setLoading('Appending resources');
        if (!(sel instanceof Array)) {
            sel = [sel];
        }

        var members = this.resource.values || [];
        var r = null;
        for (var i=0; (r=sel[i]); i++)
            members.push(new BQValue('object', r.uri ));
        // append elements to current values
        this.resource.setMembers(members);
        this.resource.save_(undefined,
                            callback(this, 'changedOk'),
                            callback(this, 'changedError'));
    },

    browseQuery: function(resource_type) {
        if (!this.checkAllowWrites(true)) return;
        var resourceDialog = Ext.create('Bisque.QueryBrowser.Dialog', {
            'height'  : '85%',
            'width'   :  '85%',
            //wpublic   : 'true',
            dataset   : '/data_service/'+resource_type,
            query_resource_type: resource_type,
            listeners : {
                'Select' : this.addQuery,
                scope: this
            },
        });
    },

    addQuery: function(browser, query) {
        if (!this.checkAllowWrites(true)) return;
        this.setLoading('Adding query to the dataset');
        var l = [
            'duri='+encodeURIComponent(this.resource.uri),
            'resource_tag='+encodeURIComponent(browser.query_resource_type), // dima: set to resource type
            'tag_query='+encodeURIComponent(query),
        ];
        var uri = '/dataset_service/add_query?' + l.join('&');
        BQFactory.request ({uri : uri,
                            cb : callback(this, 'changedOk'),
                            errorcb: callback(this, 'changedError'), });
    },

    onmodechange: function(mode) {
        var ena = (mode != 'SELECT');
        //this.toolbar.child('#menu_add_images').setDisabled(ena);
        //this.toolbar.child('#menu_delete_selected').setDisabled(ena);
    },

    removeSelectedResources : function() {
        if (!this.checkAllowWrites(true)) return;
        var sel = this.preview.resourceQueue.selectedRes;
        var m = this.resource.getMembers();
        var members = m.values; // has to be in two lines, otherwise some optimization happens...
        if (!members || members.length<1 || sel.length<1) return;

        this.setLoading('Removing selected resources');
        for (var j=members.length-1; j>=0; j--) {
            var m = members[j];
            m.index = undefined;
            if (m.value in sel)
                members.splice(j, 1);
        }

        this.resource.setMembers(members);
        this.resource.save_(undefined,
                            callback(this, 'changedOk'),
                            callback(this, 'changedError'));
    },

    removeResources : function(sel, needs_reload) {
        var m = this.resource.getMembers();
        var members = m.values; // has to be in two lines, otherwise some optimization happens...
        if (!members || members.length<1 || sel.length<1) return;

        this.setLoading('Removing selected resources');
        for (var j=members.length-1; j>=0; j--) {
            var m = members[j];
            m.index = undefined;
            if (m.value in sel)
                members.splice(j, 1);
        }

        this.resource.setMembers(members);
        if (!needs_reload) {
            var me = this;
            this.resource.save_(undefined,
                function() { me.setLoading(false); },
                callback(this, 'changedError'));
        } else {
            this.resource.save_(undefined,
                callback(this, 'changedOk'),
                callback(this, 'changedError'));
        }
    },

    // -------------------------------------------------------------------
    // Dataset ops
    // -------------------------------------------------------------------

    onDatasetRunning: function() {
        this.setLoading('Running dataset '+ this.dataset_service.getOperation());
    },

    onDatasetSuccess: function() {
        this.setLoading(false);
        if (this.dataset_service.getOperation() === 'delete')
            this.onremoved();
    },

    onDatasetError: function() {
        this.setLoading(false);
        BQ.ui.error('Error while running dataset '+ this.dataset_service.getOperation());
    },

    // -------------------------------------------------------------------
    // Removing whole dataset
    // -------------------------------------------------------------------

    onremoved: function() {
        Ext.MessageBox.show({
            title   :   'Success',
            msg     :   'Dataset deleted successfully! You will be redirected to the Bisque homepage.',
            buttons :   Ext.MessageBox.OK,
            icon    :   Ext.MessageBox.INFO,
            fn      :   function(){ window.location = BQ.Server.url('/'); },
        });
    },

    doRemoveElements: function() {
        this.dataset_service.run_delete(this.resource.uri);
    },

    remove: function() {
        if (!this.checkAllowWrites(true)) return;

        var text = 'Are you sure you want to delete dataset "'+this.resource.name+'" and all of its elements?';
        Ext.Msg.confirm('Delete dataset', text, function(btn, text) {
            if (btn != 'yes') return;
            this.doRemoveElements();
        }, this);
    },

    // -------------------------------------------------------------------
    // permissions and shares
    // -------------------------------------------------------------------

    onChangePermission: function() {
        this.dataset_service.run_permission(this.resource.uri, this.resource.permission);
    },

    onChangeShare: function() {
        this.dataset_service.run_share(this.resource.uri);
    },

    // -------------------------------------------------------------------
    // permissions and shares
    // -------------------------------------------------------------------

    shareResource : function() {
        var shareDialog = Ext.create('BQ.share.Dialog', {
            resource: this.resource,
            /*listeners : {
                changedShare: this.onChangeShare,
                scope: this,
            },*/
        });
    },

    downloadOriginal : function() {
        window.open(this.resource.uri+'?view=deep');
    },

    updateOperationItems : function(items, opbar) {
        items.splice(1, 0, {
            xtype: 'button',
            itemId : 'btn_remove',
            text: 'Remove',
            tooltip : 'Remove this resource from dataset, keeps resources in the system',
            handler : opbar.removeResource,
            scope : opbar,
        });
    },


/*
    askRename: function() {
        Ext.Msg.prompt('Dataset name', 'Please enter a new name:', function(btn, text){
            if (btn == 'ok'){
                this.rename(text);
            }
        }, this, false, this.resource.name);
    },

    rename: function(name) {
        if (!this.checkAllowWrites(true)) return;
        this.setLoading('Renaming...');
        this.resource.name = name;
        this.resource.save_(undefined,
                            callback(this, 'changedOk'),
                            callback(this, 'changedError'));
    },
*/

});

