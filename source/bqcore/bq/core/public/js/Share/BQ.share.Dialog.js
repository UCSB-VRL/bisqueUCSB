/*******************************************************************************

  BQ.share.Panel  - sharing component to add shared users to the resource
  BQ.share.Dialog - window wrapper for the sharing panel

  Author: Dima Fedorov <dima@dimin.net>

  Parameters:
      resource - the BQResource object for the resource of interest

------------------------------------------------------------------------------

  Version: 1

  History:
    2014-05-02 13:57:30 - first creation

*******************************************************************************/

//--------------------------------------------------------------------------------------
// BQ.share.Dialog
// Events:
//    changedShare
//--------------------------------------------------------------------------------------

Ext.define('BQ.share.Dialog', {
    extend : 'Ext.window.Window',
    alias: 'widget.bqsharedialog',

    border: 0,
    layout: 'fit',
    modal : true,
    width : '70%',
    height : '85%',
    //minHeight: 350,
    //maxWidth: 900,
    buttonAlign: 'center',
    autoScroll: true,

    monitorResize: true,
    closable : true,
    closeAction: 'destroy',

    bodyCls: 'bq-share-dialog',

    constructor : function(config) {
        config = config || {};
        Ext.apply(this, {
            title  : 'Sharing - ' + (config.resource ? config.resource.name : ''),
            buttons: [{
                text: 'Done',
                scale: 'large',
                scope: this,
                handler: this.close
            }],
            items  : [{
                xtype: 'bqsharepanel',
                itemId: 'sharepanel',
                border: 0,
                resource: config.resource
            }]
        }, config);

        this.callParent(arguments);
        this.show();
    },

    afterRender : function() {
        this.callParent();

        this.on('beforeclose', this.onBeforeClose, this);

        // this is used for capturing window closing and promting the user if upload is in progress
        Ext.EventManager.addListener(window, 'beforeunload', this.onPageClose, this, {
            normalized:false //we need this for firefox
        });
    },

    onBeforeClose: function(el) {
        if (this.queryById('sharepanel').isChanged())
            this.fireEvent( 'changedShare' );
        Ext.EventManager.removeListener(window, 'beforeunload', this.onPageClose, this);
        return true; // enable closing
    },

    onPageClose : function(e) {
        var p = this.queryById('sharepanel');
        if (p.isChanged()) {
            var message = 'Some shares have not yet been saved, by closing the page you will discard all changes!';
            if (e) e.returnValue = message;
            if (window.event) window.event.returnValue = message;
            return message;
        }
    },


});

//--------------------------------------------------------------------------------------
// BQ.share.Panel
// Events:
//    changePermission
//--------------------------------------------------------------------------------------

Ext.namespace('BQ.share');

BQ.share.getName = function (v, record) {
    return BQ.util.xpath_string(record.raw, 'tag[@name="display_name"]/@value');
};

BQ.share.getFull = function (v, record) {
    var username = BQ.util.xpath_string(record.raw, '@name');
    var email = BQ.util.xpath_string(record.raw, '@value');
    var name = BQ.util.xpath_string(record.raw, 'tag[@name="display_name"]/@value');
    return Ext.util.Format.format('{0} - {1} - {2}', username, name, email);
}

Ext.define('BQ.model.Auth', {
    extend : 'Ext.data.Model',
    fields : [
        { name: 'user', mapping: "@user" },
        { name: 'email', mapping: '@email' },
        { name: 'action', mapping: '@action' },
    ],
});

Ext.define('BQ.model.Users', {
    extend : 'Ext.data.Model',
    fields : [ {name: 'username', mapping: '@name' },
               {name: 'name', convert: BQ.share.getName },
               {name: 'email', mapping: '@value' },
               {name: 'uri', mapping: '@uri' },
               {name: 'uniq', mapping: '@resource_uniq' },
               {name: 'full', convert: BQ.share.getFull },
               {name: 'mexs' },
             ],
    //belongsTo: 'BQ.model.Auth',
    proxy : {
        limitParam : undefined,
        pageParam: undefined,
        startParam: undefined,
        noCache: false,
        type: 'ajax',
        url : '/data_service/user?view=full&tag_order="@ts":desc&wpublic=true',
        reader : {
            type :  'xml',
            root :  'resource',
            record: 'user',
        },
    },
});

Ext.define('BQ.share.Panel', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.bqsharepanel',
    requires: ['Ext.toolbar.Toolbar', 'Ext.tip.QuickTipManager', 'Ext.tip.QuickTip', 'Ext.selection.CellModel' ],
    cls: 'bq-share-panel',

    layout: {
        type: 'vbox',
        align: 'stretch'
    },

    auto_reload: true,
    delay_timeout: 60000,
    mexs: [],

    initComponent : function() {
        var me = this;
        if (this.resource)
            this.url = this.resource.uri+'/auth';

        //this.setLoading('Fetching users...');
        this.store_users = Ext.create('Ext.data.Store', {
            model : 'BQ.model.Users',
            autoLoad : false,
            autoSync : false,
            listeners : {
                scope: this,
                load: this.onUsersStoreLoaded,
            },
        });

        this.store = Ext.create('Ext.data.Store', {
            model : 'BQ.model.Auth',
            autoLoad : false,
            autoSync : this.resource ? true : false,
            proxy : {
                type: 'bq-auth',
                url : this.url,
            },
            listeners : {
                scope: this,
                load: this.onStoreLoaded,
                datachanged: this.onStoreChange,
                write: this.onStoreWrite,
            },
        });

        //--------------------------------------------------------------------------------------
        // items
        //--------------------------------------------------------------------------------------
        this.cellEditing = new Ext.grid.plugin.CellEditing({
            clicksToEdit: 1
        });
        var me = this;
        var grid_panel = {
            xtype: 'gridpanel',
            itemId  : 'main_grid',
            cls: 'users',
            autoScroll: true,
            flex: 2,
            store: this.store,
            plugins: [this.cellEditing],
            viewConfig: {
                stripeRows: true,
                forceFit: true,
                preserveScrollOnRefresh: true,
            },

            listeners : {
                scope: this,
                cellclick: this.onCellClick,
            },

            columns: {
                defaults: {
                    tdCls: 'bq_row',
                    cls: 'bq_row',
                },
                items: [{
                    text: 'User',
                    flex: 1,
                    dataIndex: 'user',
                    sortable: true,
                    renderer: function(value, meta, record, row, col, store, view) {
                        if (me.users_xml)
                            return BQ.util.xpath_string(me.users_xml, '//user[@resource_uniq="'+value+'"]/@name');
                        // can't read directly from the store used for combobox due to filtering applied by it
                        //me.store_users.clearFilter(true);
                        //var r = me.store_users.findRecord( 'uri', value );
                        //if (r && r.data)
                        //    return r.data.username;
                        return '';
                    },
                }, {
                    text: 'Name',
                    flex: 2,
                    dataIndex: 'user',
                    sortable: true,
                    renderer: function(value) {
                        if (me.users_xml)
                            return BQ.util.xpath_string(me.users_xml, '//user[@resource_uniq="'+value+'"]/tag[@name="display_name"]/@value');
                        // can't read directly from the store used for combobox due to filtering applied by it
                        //me.store_users.clearFilter(true);
                        //var r = me.store_users.findRecord( 'uri', value );
                        //if (r && r.data)
                        //    return r.data.name;
                        return '';
                    },
                }, {
                    text: 'E-Mail',
                    flex: 2,
                    dataIndex: 'email',
                    sortable: true,
                    renderer: function(value, meta, record) {
                        if (value!=='') return value;
                        if (me.users_xml)
                            return BQ.util.xpath_string(me.users_xml, '//user[@resource_uniq="'+record.data.user+'"]/@value');
                        // can't read directly from the store used for combobox due to filtering applied by it
                        //me.store_users.clearFilter(true);
                        //var r = me.store_users.findRecord( 'uri', record.data.user );
                        //if (r && r.data)
                        //    return r.data.email;
                        return '';
                    },
                }, {
                    text: 'Permission',
                    width : 100,
                    tdCls: 'bq_row permission',
                    dataIndex: 'action',
                    sortable: true,
                    /*editor: new Ext.form.field.ComboBox({
                        triggerAction: 'all',
                        editable: false,
                        store: [
                            ['read','read'],
                            ['edit','edit']
                        ]
                    })*/
                }, {
                    //xtype : 'actioncolumn',
                    text: 'Analysis',
                    width : 80,
                    dataIndex: 'mexs',
                    menuDisabled : true,
                    sortable : false,
                    align : 'center',
                    scope: this,
                    renderer: this.renderer_mexs,
                }, {
                    xtype: 'actioncolumn',
                    text: 'Remove',
                    width: 80,
                    align : 'center',
                    sortable: false,
                    menuDisabled: true,
                    items: [{
                        iconCls: 'icon_remove',
                        tooltip: 'Delete share',
                        scope: this,
                        handler: this.onRemoveShare,
                    }]
                }],
            },
        };

        var new_share_cnt = {
            xtype: 'container',
            border: 0,
            layout: 'hbox',
            cls: 'bq-share-bar',
            //defaults: { scale: 'large'  },
            items: [{
                xtype: 'combobox',
                itemId: 'user_combo',
                cls: 'bq-user-picker',
                flex: 3,
                heigth: 30,
                //fieldLabel: 'Add new shares by user name or any e-mail',
                store: this.store_users,
                queryMode: 'local',
                displayField: 'full',
                valueField: 'email',
                anyMatch: true,
                autoSelect: false,
                hideTrigger: true,
                minChars: 2,
                listConfig: {

                },
                listeners : {
                    scope: this,
                    change: function(field) {
                        var v = field.getValue();
                        var p = field.getPicker();
                        var h = p && p.isVisible() ? p.getHeight() : 0;
                        if (!v || v.length<2 || h<5)
                            field.collapse();
                    },
                    select: this.onAddShare,
                    specialkey: function(field, e) {
                        if (e.getKey() === e.ENTER && !field.isExpanded) {
                            this.onAddShare();
                        }
                    },
                },
            }, {
                xtype: 'button',
                text: 'Add share',
                iconCls: 'icon-add',
                scale: 'medium',
                scope: this,
                handler: this.onAddShare,
            }, {
                xtype: 'tbfill',
            }, {
                xtype: 'checkbox',
                itemId  : 'notify_check',
                boxLabel: 'Notify users about new shares',
                //boxLabelAlign: 'before',
                //iconCls: 'icon-add',
                checked: true,
                scope: this,
                handler: this.onNotifyUsers,
            }],
        };

        var visibility_cnt = {
            xtype: 'container',
            border: 0,
            layout: 'hbox',
            cls: 'bq-visibility-bar',
            iconCls: 'bq-icon-visibility',
            items: [{
                xtype: 'container',
                html: this.resource ? '<h3>This resource is:</h3>' : '<h3>Set all resources to:</h3>',
            },{
                xtype: this.resource ? 'bqresourcepermissions' : 'bqmultipermissions',
                itemId : 'btn_permission',
                scale: 'large',
                resource: this.resource,
                permission: this.permission,
                prefix: '',
                listeners : {
                    changePermission: this.onChangePermission,
                    scope: this,
                },
            }, {
                xtype: 'container',
                flex: 1,
                html: '<p><b>Private</b> resources are only accessible by the owner and shared users.</p><p><b>Published</b> resources are visible to everybody but are only modifiable by owners and shared users.</p>',
            }],
        };

        this.items = [/*{
            xtype: 'container',
            html: '<h2>Also share associated analysis results</h2>',
        }, {
            xtype: 'bq_associated_mex_panel',
            resource: this.resource,
            listeners : {
                scope: this,
                //changePermission: this.onChangePermission,
            },
        },*/ {
            xtype: 'container',
            html: '<h2>Share with public</h2>',
        }, visibility_cnt, {
            xtype: 'container',
            html: '<h2>Share with collaborators</h2>',
        }, {
            xtype: 'container',
            html: '<p>Add new shares by <b>user name</b> or by any <b>e-mail</b>, if the e-mail is not registered with the system a new user will be created and notified.</p>',
        }, new_share_cnt, grid_panel ];

        this.callParent();
        this.on('show', this.updateAutoReload, this);
        this.on('hide', this.stopAutoReload, this);
        this.on('beforedestroy', this.stopAutoReload, this);
    },

    afterRender : function() {
        this.callParent();
        this.setLoading('Fetching users...');
        this.store_users.load();
    },

    onUsersStoreLoaded: function( store, records, successful, eOpts) {
        this.setLoading(false);
        this.users_xml = this.store_users.proxy.reader.rawData;
        if (this.resource)
            this.store.load();
    },

    onNotifyUsers: function(box) {
        var notify = box.getValue();
        this.store.getProxy().setExtraParam( 'notify', notify===true ? 'true' : 'false' );
    },

    onAddShare: function() {
        var email = this.queryById('user_combo').getValue();
        if (!email) {
            BQ.ui.notification('User must have an e-mail for sharing...');
            return;
        }
        if (!(/\S+@\S+\.\S+/.test(email))) {
            BQ.ui.notification('The e-mail seems malformed...');
            return;
        }

        var r = this.store.findRecord( 'email', email );
        if (r && r.data) {
            BQ.ui.notification('You are already sharing with this user...');
            return;
        }

        var user = '';
        r = this.store_users.findRecord( 'email', email );
        if (r && r.data)
            user = r.data.uniq;

        var self_user = BQSession.current_session && BQSession.current_session.user ? BQSession.current_session.user.uri : '';
        if (user === self_user) {
            BQ.ui.notification('You are trying to share with yourself, skipping...');
            return;
        }

        // Create a model instance
        var recs = this.store.add({
            user: user,
            email: email,
            action: 'read',
        });
        recs[0].setDirty();
        this.queryById('main_grid').view.refresh();

        // clear combo box when successfully added share
        this.queryById('user_combo').setValue('');
    },

    onRemoveShare: function(grid, rowIndex) {
        this.store.removeAt(rowIndex);
    },

    // this one deletes selected share
    onDeleteShare: function(){
        var selection = this.getView().getSelectionModel().getSelection()[0];
        if (selection) {
            this.store.remove(selection);
        }
    },

    onChangePermission: function(perm, btn) {
        this.fireEvent( 'changePermission', perm, this );
    },

    onStoreLoaded: function( store, records, successful, eOpts) {
        this.changed = undefined;
        this.updateRecordsWithMexs();
    },

    onStoreWrite: function() {
        this.store.load();
    },

    onStoreChange: function() {
        this.updateAutoReload();
        this.changed = true;
    },

    isChanged: function() {
        return this.changed === true;
    },

    renderer_mexs: function(v, metadata, record, rowIndex, colIndex, store) {
        var num_mexs = record.data.mexs ? Object.keys(record.data.mexs).length : 0,
            sharing_mexs = record.data.mexs_to_share || 0;
        if (num_mexs < 1) {
            metadata.css = 'icon_add'; // class
            return '';
        }

        if (sharing_mexs>0) {
            metadata.css = 'icon_sharing';
            return Ext.String.format('{0}/{1}', num_mexs-sharing_mexs, num_mexs);
        } else {
            metadata.css = 'icon_number';
        }
        return num_mexs;
    },

    onCellClick: function( grid, td, cellIndex, record, tr, rowIndex, e) {
        if (cellIndex === 3)
            this.onClickPermission( grid, td, cellIndex, record, tr, rowIndex, e);
        else
        if (cellIndex === 4)
            this.onClickMex( grid, td, cellIndex, record, tr, rowIndex, e);
    },

    onClickPermission: function( grid, td, cellIndex, record, tr, rowIndex, e) {
        record.set('action', record.data.action === 'read' ? 'edit' : 'read');
    },

    onClickMex: function( grid, td, cellIndex, record, tr, rowIndex, e) {
        if (cellIndex !== 4) return;
        var browser = Ext.create('Bisque.ResourceBrowser.Dialog', {
            width :  '85%',
            height : '85%',
            dataset: BQ.Server.url('/data_service/mex'),
            tagQuery: '"*'+this.resource.resource_uniq+'"&value=FINISHED',
            wpublic: 'false',
            //value: 'FINISHED',
            selection: record.data.mexs,
            listeners: {
                scope: this,
                Select: function(rb, mexs) {
                    this.onAddingMexs(rb, mexs, record, rowIndex);
                },
            },
        });
    },

    onAddingMexs : function(rb, mexs, record, rowIndex) {
        if (!(mexs instanceof Array)) {
            mexs = [mexs];
        }
        this.grid = this.grid || this.queryById('main_grid');

        var me = this,
            data = record.data,
            grid = this.grid;

        data.mexs = data.mexs || {};
        data.mexs_to_share = mexs.length;
        for (var i=0; (m=mexs[i]); ++i) {
            data.mexs[m.resource_uniq] = m.resource_uniq;
        }
        grid.getView().refresh();
        setTimeout(function(){ me.shareMexs(record); }, 100);
    },

    shareMexs : function(record) {
        var data = record.data,
            grid = this.grid,
            auth_record = Ext.String.format('<auth action="{0}" email="{1}" user="{2}" />', data.action, data.email, data.user);
        for (var m in data.mexs) {
            Ext.Ajax.request({
                url: Ext.String.format('/data_service/{0}/auth?notify=false', m),
                method: 'POST',
                //xmlData:
                rawData: auth_record,
                headers: {
                    'Content-Type': 'text/xml',
                },
                callback: function(opts, succsess, response) {
                    if (response.status>=400)
                        BQ.ui.error(response.responseText);
                    else {
                        if (data.mexs_to_share) data.mexs_to_share--;
                        grid.getView().refresh();
                    }
                },
                scope: this,
                disableCaching: false,
            });
        }
    },

    updateRecordsWithMexs: function() {
        //if (this.pre_loaded_mexs === true) return;
        var xml = this.store.proxy.reader.xmlData || this.store.proxy.reader.rawData,
            mexs_per_user = {},
            nodes = BQ.util.xpath_nodes(xml, "*/mex"),
            n=null, auths=null, nn=null;
        for (var i=0; (n=nodes[i]); ++i) {
            var uniq = n.getAttribute('resource_uniq'),
                auths = BQ.util.xpath_nodes(n, 'auth');
            for (var ii=0; (nn=auths[ii]); ++ii) {
                var user = nn.getAttribute('user'),
                    action = nn.getAttribute('action');
                mexs_per_user[user] = mexs_per_user[user] || {};
                mexs_per_user[user][uniq] = uniq;
            }
        }

        var records = this.store.data.items,
            r = null, mexs = null, user = null, data=null;
        for (var i=0; (r=records[i]); ++i) {
            data = r.data;
            user = data.user;
            if (user in mexs_per_user) {
                data.mexs = mexs_per_user[user];
            }
        }

        this.grid = this.grid || this.queryById('main_grid');
        this.grid.getView().refresh();
        //this.pre_loaded_mexs = true;
    },

    updateAutoReload : function(delay) {
        var me = this;
        if (!me.task_reload) {
            me.task_reload = new Ext.util.DelayedTask( function() {
                Ext.log(">>>>>>>>>> reload shares");
                me.store.reload();
                if (me.isVisible())
                    me.task_reload.delay(me.delay_timeout);
            });
        }
        if (me.auto_reload && me.isVisible()) {
            me.task_reload.delay(delay || me.delay_timeout);
        }
    },

    stopAutoReload : function() {
        var me = this;
        if (me.task_reload)
            me.task_reload.cancel();
    },

});

//--------------------------------------------------------------------------------------
// BQ.button.ResourceVisibility
// button that shows and changes resource visibility
// Parameters: resource
// events: changePermission
//--------------------------------------------------------------------------------------

Ext.define('BQ.button.ResourcePermissions', {
    extend: 'Ext.button.Button',
    alias: 'widget.bqresourcepermissions',
    cls: 'bq-button-visibility',
    iconCls: 'bq-icon-visibility',
    minWidth: 120,
    permission: 'private',
    prefix: 'Visibility: ',

    initComponent : function() {
        this.handler = this.toggleVisibility;
        this.scope = this;
        this.callParent();
        if (this.resource)
            this.permission = this.resource.permission;
    },

    afterRender : function() {
        this.callParent();
        this.setVisibility();
    },

    onSuccess: function(resource) {
        this.setLoading(false);
        this.permission = resource.permission;
        this.resource.permission = this.permission; // update currently loaded resource
        this.setVisibility();
        this.fireEvent( 'changePermission', this.permission, this );
    },

    onError: function() {
        this.setLoading(false);
        BQ.ui.warning('Could not change permission!');
    },

    toggleVisibility: function() {
        this.setLoading('');
        this.updatePermission(this.resource, this.resource.permission === 'private' ? 'published' : 'private');
    },

    updatePermission: function(res, perm) {
        var resource = BQFactory.makeShortCopy(res);
        resource.permission = perm;
        resource.save_(undefined,
                       callback(this, this.onSuccess),
                       callback(this, this.onError),
                       'post');
    },

    setVisibility : function() {
        var me = this;
        if (me.permission === 'published') {
            me.setText(this.prefix+'published');
            me.addCls('published');
        } else {
            me.setText(this.prefix+'private');
            me.removeCls('published');
        }
    },
});


//--------------------------------------------------------------------------------------
// BQ.data.writer.Share
// XML writer that writes auth records to the data store
//--------------------------------------------------------------------------------------

Ext.define('BQ.data.writer.Auth', {
    extend: 'Ext.data.writer.Xml',
    alias: 'writer.bq-auth',

    writeRecords: function(request, data) {
        var record = request.records[0],
            item = data[0],
            xml = [];
        if (request.action !== "destroy") {
            xml.push('<auth');
            for (key in item) {
                if (item.hasOwnProperty(key) && item[key]) {
                    xml.push(Ext.String.format('{0}="{1}"', key, item[key]));
                }
            }
            xml.push('/>');
            request.xmlData = xml.join(' ');
            //request.xmlData = Ext.String.format('<auth action="{0}" email="{1}" user="{2}" />', item.action, item.email, item.user);
        } else {
            request.xmlData = '';
        }
        return request;
    }

});

//--------------------------------------------------------------------------------------
// BQ.data.proxy.Auth
// Proxy to perform REST operations on auth records
//--------------------------------------------------------------------------------------

Ext.define('BQ.data.proxy.Auth', {
    extend: 'Ext.data.proxy.Rest',
    alias : 'proxy.bq-auth',

    batchActions: false,
    noCache : false,

    limitParam : undefined,
    pageParam: undefined,
    startParam: undefined,
    sortParam : undefined,
    filterParam : undefined,

    //appendId: true,
    //idParam: 'user',

    actionMethods: {
        create : 'POST', // 'PUT'
        read   : 'GET',
        update : 'POST',
        destroy: 'DELETE'
    },

    extraParams: {
        notify: 'true',
    },

    reader : {
        type : 'xml',
        root : 'resource',
        record: '>auth',
    },

    writer : {
        type : 'bq-auth',
        root : 'resource',
        record: '>auth',
        writeAllFields : true,
        writeRecordId: false,
    },

    buildUrl: function(request) {
        // extjs attempts adding ?node=NAME to all requests
        if (request.params && request.params.node) {
            delete request.params.node;
        }
        // extjs attempts adding sorters as well
        if (request.params && request.params.sort) {
            delete request.params.sort;
        }

        request.url = this.url;
        if (request.action !== 'read' && request.action !== 'create') {
            var record = request.records[0];
            request.url += '/' + record.data.user;
        } else if (request.action === 'read') {
            request.url += '?recurse=mex';
        }

        return request.url;
    }

});


//--------------------------------------------------------------------------------------
// BQ.mex.AssociatedPanel
// Parameters:
//     resource
//--------------------------------------------------------------------------------------

Ext.define('BQ.mex.AssociatedPanel', {
    extend: 'Ext.container.Container',
    alias: 'widget.bq_associated_mex_panel',
    componentCls: 'bq_associated_mex_panel',

    layout: 'fit',

    types_to_show: {
        'string':null,
        'number':null,
        'boolean':null
    },

    initComponent : function() {
        this.store = Ext.create('Ext.data.Store', {
            autoLoad: false,
            autoSync: false,
            fields: ['id', 'str'],
            data : [
                {'id':'None', 'str':'None'},
                {'id':'All', 'str':'All'},
            ]
        });

        this.items = [{
            xtype: 'combobox',
            itemId: 'mex_combo',
            cls: 'bq-user-picker',
            heigth: 30,
            //fieldLabel: 'Choose State',

            multiSelect: true,
            editable: false,
            forceSelection: true,
            hideTrigger: true,

            store: this.store,
            queryMode: 'local',
            displayField: 'str',
            valueField: 'id',

            listeners : {
                scope: this,
                change: this.onComboChanged,
            },
        }];
        this.callParent();
    },

    afterRender : function() {
        this.callParent();
        this.loadMexs();
    },

    selectedMexs: function() {
        var items = field.getSubmitValue();
        return [];
    },

    loadMexs: function() {
        var w = this.queryById('mex_combo');
        w.setLoading('Loading MEXs...');
        Ext.Ajax.request({
            url: '/data_service/mex',
            method: 'GET',
            params : {
                'offset': '0',
                'limit': '700',
                'tag_order': '"@ts:desc"',
                'wpublic': 'false',
                'view': 'inputs',
                //'name': '"%s"'%module_name,
                'value': 'FINISHED',
                'tag_query': '"*'+this.resource.resource_uniq+'"',
            },
            callback: function(opts, succsess, response) {
                w.setLoading(false);
                if (response.status>=400)
                    BQ.ui.error(response.responseText);
                else
                    this.onLoadedMexs(response.responseXML);
            },
            scope: this,
            disableCaching: false,
        });
    },

    onLoadedMexs: function(xml) {
        this.queryById('mex_combo').setLoading(false);
        var nodes = BQ.util.xpath_nodes(xml, "*/mex"),
            n=null, ins=null,
            inputs=[];
        for (var i=0; (n=nodes[i]); ++i) {
            var name = n.getAttribute('name'),
                id = n.getAttribute('resource_uniq'),
                ts = n.getAttribute('ts'),
                inputs = [];
                ins = BQ.util.xpath_nodes(n, 'tag[@name="inputs"]/tag');
            for (var ii=0; (nn=ins[ii]); ++ii) {
                var vt = nn.getAttribute('type'),
                    vn = nn.getAttribute('name'),
                    vv = nn.getAttribute('value');
                if (vt in this.types_to_show && typeof vv !== 'undefined') {
                    inputs.push(vn+':'+vv);
                }
            }
            ts = ts.replace('T', ' ').replace(/\.\d*$/, '');
            //var repr = Ext.String.format('{0}({1}) on {2}', name, inputs.join(', '), ts);
            var repr = Ext.String.format('{0}({1})', name, inputs.join(', '));
            this.store.add({
                id: id,
                str: repr,
            });
        }
    },

    onError: function() {
        this.queryById('mex_combo').setLoading(false);
        BQ.ui.warning('Could not change permission!');
    },

    onComboChanged: function(field, newValue, oldValue) {
        if (newValue === 'None') {
            field.clearValue();
        } else if (newValue === 'All') {
            //select( r )
        } else {

        }
        var items = field.getSubmitValue();
    },

});

