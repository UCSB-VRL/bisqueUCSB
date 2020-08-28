// a patch resource tagger to view and modify xml
// in the admin service (needs to be replaced with the
// updated tag viewer)
Ext.define('BQ.ResourceTagger.User', {
    extend: 'Bisque.ResourceTagger',
    mainService: 'admin/user',
    border: false,
    setResource: function (resource, template) {
        this.setLoading(true);

        if (resource instanceof BQObject)
            this.loadResourceInfo(resource);
        else if (resource) {
            // assume it is a resource URI otherwise
            BQFactory.request({
                uri: resource,
                cb: Ext.bind(this.loadResourceInfo, this),
                errorcb: function(error) {
                    BQ.ui.error('Error fetching resource:<br>'+error.message_short, 4000);
                },
            });
        } else {
            this.setLoading(false);
        }
    },

    loadResourceTags: function(data, template) {
        var type = this.resource.type || this.resource.resource_type;

        // Check to see if resource was derived from a template
        if (type && type.indexOf('/data_service/') != -1 && !template && this.rootProperty != 'gobjects') {
            BQFactory.request({
                uri: this.resource.type + '?view=deep',
                cb: Ext.bind(this.initCopy, this),
                errorcb: Ext.bind(this.loadResourceTags, this, [this.resource.tags, true])
            });
            return;
        }

        this.setLoading(false);

        var root = {};
        root[this.rootProperty] = data;

        this.removeAll(true);
        //this.addDocked(this.getToolbar());
        this.add(this.getTagTree(root));

        this.fireEvent('onload', this, this.resource);
        this.relayEvents(this.tree, ['itemclick']);
        if (this.onLoaded) this.onLoaded();
    },

    updateQueryTagValues: function(tag_name) {
        //var proxy = this.store_values.getProxy();
        //proxy.url = '/data_service/'+this.resource.resource_type+'?tag_values=' + encodeURIComponent(tag_name);
        //this.store_values.load(); // dima: why???
    },

    importMenu: function (btn, e) {
        if (!btn.menu) {
            var menuItems = [];

            for (var i = 0; i < BQApp.resourceTypes.length; i++) {
                menuItems.push({
                    text: 'from <b>' + BQApp.resourceTypes[i].name + '</b>',
                    name: '/data_service/' + BQApp.resourceTypes[i].name,
                    handler: this.importTags,
                    scope: this
                });
            }

            btn.menu = Ext.create('Ext.menu.Menu', {
                items: menuItems
            });
        }
        btn.showMenu();
    },

    loadResourceInfo: function (resource) {
        this.fireEvent('beforeload', this, resource);
        this.resource = resource;
        //this.editable = false;
        if (!this.disableAuthTest)
            this.testAuth(BQApp.user, false);
        if (this.resource.tags.length > 0)
            this.loadResourceTags(this.resource.tags);
        else
            this.resource.loadTags({
                cb: callback(this, "loadResourceTags"),
                depth: 'deep&wpublic=1'
            });
    },

    //delete will be a removal of the node and putting the rest of the body back
    // this will be changed in the next iteration when deltas are added and hopefully
    // this custom component can be removed
    deleteTags: function () {
        var me = this;
        var selectedItems = this.tree.getSelectionModel().getSelection(), parent;

        // removes elements for the xml
        if (selectedItems.length) {
            this.tree.setLoading(true);

            for (var i = 0; i < selectedItems.length; i++) {
                //parent = (selectedItems[i].parentNode.isRoot()) ? this.resource : selectedItems[i].parentNode.raw; //this resource will always be parent
                this.resource.remove(selectedItems[i].raw); //removes child node

                if (selectedItems[i].parentNode.childNodes.length <= 1)
                    selectedItems[i].parentNode.data.iconCls = 'icon-tag';
                selectedItems[i].parentNode.removeChild(selectedItems[i], true);

            }

            //PUT the modified xml back into the db
            var id = this.resource.resource_uniq;
            var xmlBody = this.resource.toXML();
            Ext.Ajax.request({
                url: '/admin/user/'+id,
                method: 'PUT',
                xmlData: xmlBody,
                headers: { 'Content-Type': 'text/xml' },
                success: function(response) {
                    var xml = response.responseXML;
                    this.setProgress(false);
                    //BQ.ui.notification('Tag(s) successfully deleted');
                    //update the list
                    //this.reload()
                    this.tree.setLoading(false);
                    BQ.ui.notification(selectedItems.length + ' record(s) deleted!');
                    me.fireEvent('onDone', me, xml.documentElement)
                },
                failure: function(response) {
                    this.setProgress(false);
                    this.tree.setLoading(false);
                    BQ.ui.error('Failed to delete resource tag on: '+id);
                    this.setResource('/admin/user/'+id) //reset resource
                    me.fireEvent('onError', me, response)
                },
                scope: this,
            });

            this.tree.getSelectionModel().deselectAll();
        } else
            BQ.ui.notification('No records modified!');
    },

    //saveTags will put the entire body back
    // this will be changed in the next iteration when deltas are added
    saveTags: function (parent, silent) {
        var me = this;
        if (silent === undefined)
            silent = this.silent !== undefined ? this.silent : false;

        var resource = (typeof parent == BQObject) ? parent : this.resource;
        var me = this;
        if (this.store.applyModifications()) {
            this.setProgress('Saving');
            var xmlBody = resource.toXML();
            var id = resource.resource_uniq; //we want to put the entire body back for now
            Ext.Ajax.request({
                url: '/admin/user/'+id,
                method: 'PUT',
                params: {view:'deep'},
                xmlData: xmlBody,
                headers: { 'Content-Type': 'text/xml' },
                success: function(response) {
                    var xml = response.responseXML;
                    this.setProgress(false);

                    BQ.ui.notification('Tag(s) successfully modified');
                    me.fireEvent('onDone', me, xml.documentElement)
                },
                failure: function(response) {
                    BQ.ui.error('Failed to modify resource: '+id);
                    this.setProgress(false);
                    //this.reload()
                    this.setResource('/admin/user/'+id)
                    //this.reload()
                    me.fireEvent('onError', me, response)
                },
                scope: this,
            });
        } else
            BQ.ui.notification('No records modified!');
    },
});


Ext.define('BQ.admin.UserTable', {
    extend : 'Ext.grid.Panel',
    xtype: 'BQAdminUserTable',
    //title: 'Users',
    userInfoPanel: null,
    border: false,
    componentCls: 'bq_users_manager',

    viewConfig: {
        markDirty: false,
    },
    selModel: {  allowDeselect: true },
    columns: {
        items: [/*{
            dataIndex:'profile_picture',
            width: 45,
            renderer: function(value, meta, record){
                if (value) {
                    var image_url = '/'+value+'/pixels?thumbnail';
                    return '<img  src="'+image_url+'" height="32" width="32"/>';
                } else {
                    return '<div class="icon_user" />';
                }
            },
        }, {
            text: 'ID', dataIndex: 'resource_uniq', sortable: true, flex:1,
        }, */{
            text: 'User name', dataIndex: 'name', sortable: true, flex:2,
        }, {
            text: 'E-mail', dataIndex: 'email', sortable: true, flex:2,
        }, {
            text: 'Display name', dataIndex: 'display_name', sortable: true, flex:2,
        }],
        defaults: {
            renderer : function (value, meta, record) {
                var value = value || '';
                return '<div style="line-height:32px; text-align:center; height:32px; overflow:hidden; text-overflow:ellipsis">'+value+'</div>';
            }
        }
    },

    plugins: {
        ptype: 'bufferedrenderer',
        trailingBufferZone: 20,  // Keep 20 rows rendered in the table behind scroll
        leadingBufferZone: 50   // Keep 50 rows rendered in the table ahead of scroll
    },
    renderTo: Ext.getBody(),
    initComponent: function(config) {
        var config = config || {};
        var me = this;

        var tbar = new Ext.Toolbar({
            margin: false,
            border: false,
            defaults: {
                disabled: true,
                scale: 'large',
                listeners: { //disable buttons when deselected
                    afterrender: function(el) {
                        var buttonEl = el;
                        me.on('select',
                            function(el, record) {
                                buttonEl.setDisabled(false);
                        });
                        me.on('deselect',
                            function(el, record) {
                                buttonEl.setDisabled(true);
                        });
                        var store = me.getStore();
                        store.on('load',
                            function(el,record) {
                                buttonEl.setDisabled(true);
                        });
                    }
                }
            },
            items:[{
                xtype: 'button',
                text: 'Login as',
                iconCls : 'icon login',
                tooltip: 'Login as selected user',
                handler: this.loginUserMessage,
                scope: this,
            }, ' ', {
                xtype: 'button',
                text: 'Add',
                iconCls : 'icon add',
                tooltip: 'Add new user',
                handler: this.addUserWin,
                disabled: false,
                scope: this,
                listeners: {}, //remove default listeners
            }, {
                xtype: 'button',
                text: 'Delete',
                iconCls : 'icon remove',
                tooltip: 'Delete existing user',
                handler: this.deleteUserWin,
                scope: this,
            }, {
                xtype: 'button',
                text: 'Clear user data',
                iconCls : 'icon clear',
                tooltip: 'Removes all data from selected user',
                handler: this.deleteUserImagesMessage,
                scope: this,
            }, '->', {
                xtype:'textfield',
                itemId: 'search',
                cls: 'search_field',
                disabled: false,

                flex: 2,
                name: 'search',

                default_string: 'Filter users',
                value: 'Filter users',

                //minWidth: 100,
                tooltip: 'Query for images using Bisque expressions',
                enableKeyEvents: true,
                listeners: {
                    scope: this,
                    afterrender: function() {},
                    focus: function(c) {
                        //c.flex = 2;
                        //this.doLayout();
                        if (c.value === c.default_string) {
                            c.setValue('');
                        }
                    },
                    // specialkey: function(f, e) {
                    //     if (e.getKey()==e.ENTER && f.value!='' && f.value != c.default_string) {
                    //         document.location = BQ.Server.url('/client_service/browser?tag_query='+escape(f.value));
                    //     }
                    // },
                    blur: function(c) {
                        //c.flex = 0;
                        //this.doLayout();
                    },
                    change: function ( c, newValue, oldValue ) {
                        if (newValue !== '' && newValue !== c.default_string) {
                            this.store.clearFilter(true);
                            var re = new RegExp(newValue, 'i');
                            this.store.filter(new Ext.util.Filter({
                                filterFn: function (object) {
                                    var match = false;
                                    Ext.Object.each(object.data, function (property, value) {
                                        match = match || re.test(String(value));
                                    });
                                    return match;
                                  }
                            }));
                        } else {
                            this.store.clearFilter();
                        }
                    },
                }
            }, '', {
                xtype: 'button',
                //text: 'Refresh',
                iconCls : 'icon refresh',
                tooltip: 'Refresh information in the list',
                handler: this.reload,
                disabled: false,
                scope: this,
                listeners: {}, //remove default listeners
            }],
        });
        if (BQApp.user && BQApp.user.is_admin()) { //the way to check for admin needs to be changed
            this.initTable();
        }
        Ext.apply(me, {
            store: me.store,
            tbar: tbar
        });
        this.callParent([config]);
    },

    initTable: function() {
        Ext.define('BQ.model.adminUsers', {
            extend: 'Ext.data.Model',
            fields: [{
                name: 'name' ,
                mapping: '@name',
            },{
                name: 'resource_uniq',
                mapping: '@resource_uniq',
            },{
                name: 'email',
                mapping: "tag[@name='email']/@value",
            },{
                name: 'profile_picture',
                mapping: "tag[@name='profile_picture']/@value",
            },{
                name: 'display_name',
                mapping: "tag[@name='display_name']/@value",
            }],
        });

        this.store = Ext.create('Ext.data.Store', {
            model: 'BQ.model.adminUsers',
            storeID: 'BQUsers',
            autoLoad: false, //dont know yet why this doesnt work
            //autoLoad: true,
            autoSync: false,
            proxy: {
                type: 'rest',
                noCache: false,
                type: 'ajax',
                limitParam: undefined,
                pageParam: undefined,
                startParam: undefined,
                url: '/admin/user',
                extraParams: {
                    view: 'clean,full',
                },
                reader: {
                    type: 'xml',
                    root: 'resource',
                    record: 'user',
                },
            },
            sorters: [{
                property:   'name',
                direction:  'ASC',
                transform:  function (v) { return v.toLowerCase(); }
            }, {
                property:   'display_name',
                direction:  'ASC',
                transform:  function (v) { return v.toLowerCase(); }
            }]
        });
        this.store.load();
        //this.store.reload();
    },

    addUserWin : function() {
        var me = this;
        var userForm = Ext.create('Ext.form.Panel', {
            //padding: '8px',
            padding: '20px',
            layout: 'anchor',
            border: false,
            defaultType: 'textfield',
            items: [{
                padding: '5px',
                fieldLabel: 'User name',
                name: 'username',
                allowBlank: false,
            },{
                padding: '5px',
                fieldLabel: 'Password',
                name: 'password',
                inputType: 'password',
                allowBlank: false,
                //invalidText:
            },{
                padding: '5px',
                fieldLabel: 'Display Name',
                name: 'displayname',
                allowBlank: false,
            },{
                padding: '5px',
                fieldLabel: 'E-mail',
                name: 'email',
                allowBlank: false,
            }],
        });

        var win = Ext.create('Ext.window.Window', {
            border: false,
            modal : true,
            buttonAlign: 'center',
            title: 'Create New User',
            bodyStyle: 'background-color:#FFFFFF',
            layout : 'fit',
            items: userForm,
            scope: this,
            buttons: [{
                //formBind: true, //only enabled once the form is valid
                //disabled: true,
                text: 'Submit',
                handler: function() {
                    var form = userForm.getForm();
                    if (form.isValid()) {
                        var values = form.getValues()
                        me.addUser(values.username, values.password, values.displayname, values.email)
                        win.close();

                    }
                },
            },{
                text: 'Cancel',
                handler: function() {
                    win.close();
                },
            }]
        });
        win.show();
    },

    addUser: function(username, password, display_name, email) {
        var user = document.createElement("user");
        user.setAttribute('name',username);
        var passwordTag = document.createElement("tag");
        passwordTag.setAttribute('name','password');
        passwordTag.setAttribute('value',password);
        user.appendChild(passwordTag);
        var emailTag = document.createElement("tag");
        emailTag.setAttribute('name','email');
        emailTag.setAttribute('value',email);
        user.appendChild(emailTag);
        var display_nameTag = document.createElement("tag");
        display_nameTag.setAttribute('name','display_name');
        display_nameTag.setAttribute('value',display_name);
        user.appendChild(display_nameTag);

        Ext.Ajax.request({
            url: '/admin/user',
            xmlData: user.outerHTML,
            method: 'POST',
            headers: { 'Content-Type': 'text/xml' },
            success: function(response) {
                var xml = response.responseXML;
                this.reload()
            },
            failure: function(response) {
                BQ.ui.error('Failed to add new user!')
            },
            scope: this
        })
    },

    deleteUserWin : function() {
        var record = this.getSelectionModel().getSelection();
        if (record.length>0) {
            var resource_uniq = record[0].data.resource_uniq;
            var userName = record[0].data.name;
            var win = Ext.MessageBox.show({
                title: 'Delete User',
                msg: 'Are you sure you want to delete User: '+userName+'? (This operation can take awhile to complete)',
                buttons: Ext.MessageBox.OKCANCEL,
                fn: function(buttonResponse) {
                    if (buttonResponse === "ok") {
                        this.deleteUser(resource_uniq)
                        record.remove()
                    }
                },
                scope: this,
            });
        } else {
            var win = Ext.MessageBox.show({
                title: 'Delete User',
                msg: 'No users were selected to be deleted.',
                buttons: Ext.MessageBox.OK,
                scope: this,
            });
        }
    },

    deleteUser: function(uniq) {
        var me = this;
        Ext.Ajax.request({
            url: '/admin/user/'+uniq,
            method: 'DELETE',
            headers: { 'Content-Type': 'text/xml' },
            success: function(response) {
                var xml = response.responseXML;
                //update the list
                BQ.ui.notification('Resource: '+uniq+' deleted succesfully!')
                this.reload()
            },
            failure: function(response) {
                BQ.ui.error('Failed to delete resource: '+uniq)
            },
            scope: this,
        })
    },

    deleteUserImagesMessage: function() {
        var record = this.getSelectionModel().getSelection();
        if (record.length>0) {
            var resource_uniq = record[0].data.resource_uniq;
            var userName = record[0].data.name;
            var win = Ext.MessageBox.show({
                title: 'Delete User\'s Images',
                msg: 'Are you sure you want to delete User: '+userName+'\'s Images? (This operation can take awhile to complete)',
                buttons: Ext.MessageBox.OKCANCEL,
                fn: function(buttonResponse) {
                    if (buttonResponse === "ok") {
                        this.deleteUserImages(resource_uniq)
                        record.remove()
                    }
                },
                scope: this,
            });
        } else {
            var win = Ext.MessageBox.show({
                title: 'Delete User\'s Images ',
                msg: 'No users were selected.',
                buttons: Ext.MessageBox.OK,
                scope: this,
            });
        }
    },

    deleteUserImages: function() {
         Ext.Ajax.request({
            url: '/admin/user/'+uniq+'/image',
            method: 'DELETE',
            headers: { 'Content-Type': 'text/xml' },
            success: function(response) {
                var xml = response.responseXML;
                //update the list
                BQ.ui.notification('All images were successfully deleted')
            },
            failure: function(response) {
                BQ.ui.error('Failed to delete all of users: '+uniq+' images')
            },
            scope: this,
        })
    },

    loginUserMessage : function(){
        var record = this.getSelectionModel().getSelection();
        if (record.length==1) {
            var resource_uniq = record[0].data.resource_uniq;
            var userName = record[0].data.name;
            var win = Ext.MessageBox.show({
                border: false,
                title: 'Login As',
                msg: 'Are you sure you want to login as '+userName+'? (Warning: Your admin session will be closed the page will be reloaded)',
                buttons: Ext.MessageBox.OKCANCEL,
                fn: function(buttonResponse) {
                    if (buttonResponse === "ok") {
                        this.loginUser(resource_uniq)
                    }
                },
                scope: this,
            });
        } else if (record.length>1){ //in the case that multiselect is allowed
            var win = Ext.MessageBox.show({
                border: false,
                title: 'Login As',
                msg: 'Only one user can be login at a time.',
                buttons: Ext.MessageBox.OK,
                scope: this,
            });
        } else {
            var win = Ext.MessageBox.show({
                border: false,
                title: 'Login As',
                msg: 'No user was selected to be login as.',
                buttons: Ext.MessageBox.OK,
                scope: this,
            });
        }
    },

    loginUser : function(userUniq) {
         Ext.Ajax.request({
            url: '/admin/user/'+userUniq+'/login',
            method: 'GET',
            headers: { 'Content-Type': 'text/xml' },
            headers: { 'Content-Type': 'text/xml' },
            success: function(response) {
                var xml = response.responseXML;
                location = '/client_service'; //reloads with new credentials
                //update the list
            },
            failure: function(response) {
                BQ.ui.error('An issue occured when tryin to log in as '+userUniq)
            },
            scope: this,
        })
    },

    reload : function() {
        if (this.userInfoPanel) {
            this.userInfoPanel.deselectUser();
        }
        this.getStore().load();
    },
});

Ext.define('BQ.admin.UserInfo', {
    extend: 'Ext.panel.Panel',
    title: 'User info',
    //layout : 'fit',
    layout: 'card',
    border: false,
    initComponent: function(config) {
        items = [];
        var me = this;

        this.tagger = Ext.create('BQ.ResourceTagger.User', {
            layout : 'fit',
            editable: true,
            disableAuthTest: true,
            tree: {
                btnAdd: false, //enable add button
                btnDelete: false, //enable delete button
            },
            //hidden: true,
            //viewMode: 'ReadOnly',
            resource: '',
            //flex: 1,
        });

        this.userManagerWelcomePage = Ext.createWidget('box',{
            border: false,
            padding: '10px',
            layout: 'fit',
            tpl: [
                '<h2>Welcome to the Administrator\'s User Manager</h2>',
                '<p>This page allows for an admin to create, delete, modify and manage users in the system with normal bisque credentials. If the user is registered to bisque with another system like cas or google this page will not be able to modify those users with the current iteration. Below is some information on how this page can be used to manage users.</p>',
                '<p><b>Create User:</b> Select the add button at the top of the User List and a form will pop up. Enter the neccessary user information.</p>',
                '<p><b>Delete User:</b> Select a user and then select the Delete at the top of the User List</p>',
                '<p><b>Modify User:</b> Select a user and tags for the user will appear in the User View. Modify the tags you want to modify. <i>Note: The email, password and display name tags cannot be delete.</i></p>',
                '<p><b>Login As User:</b> Select a user and press the Login As button at the top of the User List. This will log in the currect user as the selected user and return to the front page.</p>',
            ],
            data: {},
        });
        var items = [
            this.userManagerWelcomePage,
            this.tagger,
        ];
        Ext.apply(me, {
            items: items,
        });
        this.callParent([config]);
    },

    selectUser: function(resource_uri) {
        this.layout.setActiveItem(this.tagger);
        this.tagger.setResource(resource_uri+'?view=deep');

    },
    deselectUser: function() {
        this.layout.setActiveItem(this.userManagerWelcomePage);
        //this.tagger.setResource('');
    },
});


Ext.define('BQ.admin.UserManager', {
    extend: 'Ext.container.Container',
    alias: 'widget.bq_user_manager',

    layout: 'border',
    border: false,
    //renderTo: Ext.getBody(),
    initComponent: function(config) {
        var config = config || {};
        items = [];
        var me = this;

        this.userInfo = Ext.create('BQ.admin.UserInfo',{
            width: '35%',
            plain : true,
            border: false,
            hidden : false,
            collapsible : true,
            region: 'east',
            split: true,
            resource: '',
            minimizable: true,
        });

        this.userTable = Ext.create('BQ.admin.UserTable', {
            split: true,
            region: 'center',
            autoScroll: true,
            plain : true,
            border: false,
            userInfoPanel: this.userInfo,
        });

        this.userTable.on('select',
            function(el, record) {
                var resource_uniq = record.get('resource_uniq');
                me.userInfo.selectUser('/admin/user/'+resource_uniq);
        });

        this.userTable.on('deselect',
            function(el, record) {
                me.userInfo.deselectUser();
        });

        this.userInfo.tagger.on('onDone',
            function(el, xmlResponse) {
                var userName = xmlResponse.attributes['name'].value;
                var record = me.userTable.store.findRecord('name', userName);
                var email = xmlResponse.querySelector('tag[name="email"]');
                record.set('email', email ? email.attributes['value'].value: '');
                var resource_uniq = xmlResponse.attributes['resource_uniq'];
                record.set('resource_uniq', resource_uniq ? resource_uniq.value: '');
                var profile_picture = xmlResponse.querySelector('tag[name="profile_picture"]');
                record.set('profile_picture', profile_picture ?  profile_picture.attributes['value'].value : '');
                var display_name = xmlResponse.querySelector('tag[name="display_name"]');
                record.set('display_name', display_name ?  display_name.attributes['value'].value : '');
        });

        items.push(this.userTable);
        items.push(this.userInfo);

        Ext.apply(me, {
            items: items,
        });
        this.callParent([config]);

    },
});

//--------------------------------------------------------------------------------
// Notifications
// available variables in messages:
//     $display_name
//     $user_name
//     $service_name - the name of the system
//     $service_url - and A HREF with the name and URL to the system
//--------------------------------------------------------------------------------

Ext.define('BQ.admin.notifications.Manager', {
    extend: 'Ext.container.Container',
    alias: 'widget.bq_notifications_manager',

    componentCls: 'bq_notifications',

    layout: {
        type: 'vbox',
        align : 'stretch',
        pack  : 'start',
    },

    messages: {
        'immediate_outage': '\nThe $service_name team has to perform an unscheduled maintenance on the system. This update will bring higher stability and fix encountered issues. The system will not be available from X to Y.',
        'scheduled_maintenance': '\nThe $service_name team is planning a scheduled maintenance on the system. This update will bring improvements and higher stability. The system will not be available from X to Y.',
    },
    header: 'Dear $display_name,\n',
    footer: '\n\nWe are sorry for the inconvenience and hope you will like the upgraded service! You are receiving this message because you are a registered user at $service_url.\n\nThe $service_url team.',

    initComponent: function(config) {
        this.period = 30;
        this.items = [{
            xtype: 'container',
            cls: 'block',
            layout: {
                type: 'hbox',
                align : 'stretch',
                pack  : 'start',
            },
            defaults: {
                xtype: 'button',
                cls: 'button',
                width: 150,
                scale: 'medium',
                enableToggle: true,
                toggleGroup: 'users',
                scope: this,
                handler: this.setUsers,
            },
            items: [{
                xtype: 'container',
                width: 250,
                html: '<h2>Users mailing list:</h2>',
            }, {
                itemId: 'users_all',
                text: 'All',
                period: 0,
            }, {
                itemId: 'users_30',
                text: 'Active last month',
                period: 30,
                pressed: true,
            }, {
                itemId: 'users_7',
                text: 'Active last week',
                period: 7,
            }, {
                itemId: 'users_1',
                text: 'Active last day',
                period: 1,
            }],
        }, {
            xtype: 'textareafield',
            itemId: 'mailinglist',
            grow: true,
            //name: 'mailinglist',
            flex: 1,
        }, {
            xtype: 'container',
            html: '<h2>Send a message to all users</h2>',
        }, {
            xtype: 'container',
            cls: 'block',
            layout: {
                type: 'hbox',
                align : 'stretch',
                pack  : 'start',
            },
            defaults: {
                xtype: 'button',
                cls: 'button',
                scale: 'medium',
                scope: this,
                handler: this.setMessage,
            },
            items: [{
                xtype: 'container',
                html: '<h3>Templates:</h3>',
            }, {
                itemId: 'immediate_outage',
                text: 'Temporary outage',
            }, {
                itemId: 'scheduled_maintenance',
                text: 'Scheduled maintenance',
            }],
        }, {
            xtype: 'container',
            cls: 'block',
            flex: 3,
            layout: {
                type: 'hbox',
                align : 'stretch',
                pack  : 'start',
            },
            items: [{
                xtype: 'textareafield',
                itemId: 'message',
                grow: true,
                //name: 'message',
                flex: 4,
                listeners: {
                    scope: this,
                    change: function ( me, newValue, oldValue, eOpts ) {
                        this.queryById('send_btn').setDisabled(newValue=='');
                    },
                },
            }, {
                xtype: 'textareafield',
                itemId: 'variables',
                grow: true,
                flex: 1,
            }],
        }, {
            xtype: 'container',
            layout: {
                type: 'hbox',
                align : 'stretch',
                pack  : 'start',
            },
            items: [{
                xtype: 'button',
                itemId: 'send_btn',
                text: 'Send message to all users',
                scale: 'large',
                disabled: true,
                scope: this,
                handler: this.sendMessage,
            }],
        }];
        this.callParent();
    },

    afterRender: function() {
        this.callParent();
        this.loadUsers();
    },

    setUsers: function(btn) {
        this.period = btn.period;
        this.loadUsers();
    },

    loadUsers: function() {
        var list_w = this.queryById('mailinglist'),
            vars_w = this.queryById('variables'),
            url = '/data_service/user?view=full&tag_order="@ts":desc&wpublic=true',
            dt = Ext.Date.subtract(new Date(), Ext.Date.DAY, this.period),
            ts = Ext.Date.format(dt, 'Y-m-d\\TH:i:s');

        list_w.setLoading('Loading users...');
        if (this.period>0) {
            url = Ext.String.format('{0}&ts=>{1}', url, ts);
        }
        Ext.Ajax.request({
            url: url,
            callback: function(opts, succsess, response) {
                list_w.setLoading(false);
                if (response.status>=400)
                    BQ.ui.error(response.responseText);
                else
                    this.onUsersLoaded(response.responseXML);
            },
            scope: this,
            disableCaching: false,
        });

        vars_w.setLoading('Loading variables...');
        Ext.Ajax.request({
            url: '/admin/message_variables',
            callback: function(opts, succsess, response) {
                vars_w.setLoading(false);
                if (response.status>=400)
                    BQ.ui.error(response.responseText);
                else
                    this.onVarsLoaded(response.responseXML);
            },
            scope: this,
            disableCaching: false,
        });
    },

    onUsersLoaded: function(xml) {
        this.users = {};
        var nodes = BQ.util.xpath_nodes(xml, "*/user"),
            u = null,
            message = [];
        for (var i=0; (u=nodes[i]); ++i) {
            var username = u.getAttribute('name'),
                email = u.getAttribute('value'),
                display_name = BQ.util.xpath_string(u, 'tag[@name="display_name"]/@value');
            this.users[u.getAttribute('name')] = {
                username: username,
                name: display_name,
                email: email,
            };
            message.push(display_name+' <'+email+'>');
        }
        this.queryById('mailinglist').setValue( message.join(', ') );
    },

    onVarsLoaded: function(xml) {
        var nodes = BQ.util.xpath_nodes(xml, "*/tag"),
            t = null,
            vars = [];
        for (var i=0; (t=nodes[i]); ++i) {
            var n = t.getAttribute('name'),
                v = t.getAttribute('value');
            vars.push('$'+n+': "'+v+'"');
        }
        this.queryById('variables').setValue( vars.join('\n') );
    },

    setMessage: function(btn) {
        var message_body = this.messages[btn.itemId],
            message = this.header + message_body + this.footer;
        this.queryById('message').setValue( message );
    },

    sendMessage: function() {
        var msg_w = this.queryById('message'),
            message = msg_w.getValue(),
            userlist =this.queryById('mailinglist').getValue(),
            resource = BQFactory.make('message');
        msg_w.setLoading('Sending...');
        resource.addtag( { name:'message', value: message });
        resource.addtag( { name:'users', value:userlist } );
        //resource.setValues([message]);
        resource.save_('/admin/notify_users',
                       callback(this, this.onSendDone),
                       callback(this, this.onSendError),
                       'POST');

        /*msg_w.setLoading('Sending message...');
        Ext.Ajax.request({
            url: '/admin/notify_users',
            method: 'POST',
            params: {
                //ajax_req: Ext.util.JSON.encode(myObj),
                ajax_req: message,
            },

            callback: function(opts, succsess, response) {
                msg_w.setLoading(false);
                if (response.status>=400)
                    BQ.ui.error(response.responseText);
                else
                    BQ.ui.notification('Message sent');
            },
            scope: this,
            disableCaching: false,
        });*/
    },

    onSendDone: function() {
        this.queryById('message').setLoading(false);
        BQ.ui.notification('Message sent');
    },

    onSendError: function(m) {
        this.queryById('message').setLoading(false);
        BQ.ui.error(m.message_short);
    },

});

//--------------------------------------------------------------------------------
// Loggers
//--------------------------------------------------------------------------------

Ext.namespace('BQ.admin.loggers');

BQ.admin.loggers.getName = function (v, record) {
    //record.raw
    return 'myname';
};

BQ.admin.loggers.getLevel = function (v, record) {
    //record.raw
    return 'DEBUG';
};

Ext.define('BQ.model.Loggers', {
    extend : 'Ext.data.Model',
    fields : [{
        name: 'name',
        mapping: '@name',
        //convert: BQ.admin.loggers.getName,
    }, {
        name: 'level',
        mapping: '@value',
        //convert: BQ.admin.loggers.getLevel,
    }],
    proxy : {
        type: 'ajax',
        url : '/admin/loggers',

        batchActions: true,
        noCache : false,

        limitParam : undefined,
        pageParam: undefined,
        startParam: undefined,
        sortParam : undefined,
        filterParam : undefined,

        actionMethods: {
            create : 'POST', // 'PUT'
            read   : 'GET',
            update : 'POST',
            destroy: 'DELETE'
        },

        reader : {
            type :  'xml',
            root :  'resource',
            record: '>logger',
        },

        writer : {
            type : 'bq-logger',
            root : 'resource',
            record: '>logger',
            writeAllFields : true,
            writeRecordId: false,
        },
    },
});

Ext.define('BQ.admin.loggers.Manager', {
    extend: 'Ext.container.Container',
    alias: 'widget.bq_loggers_manager',

    componentCls: 'bq_loggers',

    layout: {
        type: 'vbox',
        align : 'stretch',
        pack  : 'start',
    },

    initComponent: function() {

        this.store = Ext.create('Ext.data.Store', {
            model : 'BQ.model.Loggers',
            autoLoad : false,
            autoSync : true,
            listeners : {
                scope: this,
                //load: this.onUsersStoreLoaded,
            },
        });

        this.cellEditing = new Ext.grid.plugin.CellEditing({
            clicksToEdit: 1
        });

        this.items = [{
            xtype: 'toolbar',
            margin: false,
            border: false,
            defaults: {
                scale: 'large',
            },
            items:[{
                xtype: 'container',
                html: '<h2>Loggers</h2>',
            }, '->', {
                xtype:'textfield',
                itemId: 'search',
                cls: 'search_field',
                disabled: false,

                flex: 2,
                name: 'search',

                default_string: 'Filter loggers',
                value: 'Filter loggers',

                //minWidth: 100,
                //tooltip: 'Query for images using Bisque expressions',
                enableKeyEvents: true,
                listeners: {
                    scope: this,
                    afterrender: function() {},
                    focus: function(c) {
                        //c.flex = 2;
                        //this.doLayout();
                        if (c.value === c.default_string) {
                            c.setValue('');
                        }
                    },
                    // specialkey: function(f, e) {
                    //     if (e.getKey()==e.ENTER && f.value!='' && f.value != c.default_string) {
                    //         document.location = BQ.Server.url('/client_service/browser?tag_query='+escape(f.value));
                    //     }
                    // },
                    blur: function(c) {
                        //c.flex = 0;
                        //this.doLayout();
                    },
                    change: function ( c, newValue, oldValue ) {
                        if (newValue !== '' && newValue !== c.default_string) {
                            this.store.clearFilter(true);
                            var re = new RegExp(newValue, 'i');
                            this.store.filter(new Ext.util.Filter({
                                filterFn: function (object) {
                                    var match = false;
                                    Ext.Object.each(object.data, function (property, value) {
                                        //match = match || re.test(String(value));
                                        match = match || value.indexOf(newValue)===0;
                                    });
                                    return match;
                                  }
                            }));
                        } else {
                            this.store.clearFilter();
                        }
                    },
                },
            }, '', {
                xtype: 'button',
                //text: 'Refresh',
                iconCls : 'icon refresh',
                tooltip: 'Refresh information in the list',
                disabled: false,
                scope: this,
                handler: function() {
                    this.store.reload();
                },
            }],
        }, {
            xtype: 'gridpanel',
            itemId  : 'grid_loggers',
            cls: 'loggers',
            autoScroll: true,
            flex: 2,
            store: this.store,
            plugins: [this.cellEditing],
            viewConfig: {
                stripeRows: true,
                forceFit: true,
            },

            /*listeners : {
                scope: this,
                cellclick: this.onCellClick,
            },*/

            columns: {
                defaults: {
                    tdCls: 'bq_row',
                    cls: 'bq_row',
                },
                items: [{
                    text: 'Name',
                    flex: 3,
                    dataIndex: 'name',
                    sortable: true,
                    renderer: this.renderer_logger,
                }, {
                    text: 'Level',
                    flex: 1,
                    //width : 100,
                    //tdCls: 'bq_row permission',
                    dataIndex: 'level',
                    sortable: true,
                    renderer: this.renderer_logger,
                    editor: new Ext.form.field.ComboBox({
                        triggerAction: 'all',
                        editable: false,
                        store: [
                            ['NOTSET','NOTSET'],
                            ['DEBUG','DEBUG'],
                            ['INFO','INFO'],
                            ['WARN','WARN'],
                            ['ERROR','ERROR'],
                        ]
                    })
                }],
            },
        }];
        this.callParent();
    },

    afterRender: function() {
        this.callParent();
        this.store.load();
        this.queryById('search').setValue('bq');
    },

    renderer_logger: function(v, metadata, record, rowIndex, colIndex, store) {
        metadata.css = record.data.level.toLowerCase();
        return v;
    },

});

//--------------------------------------------------------------------------------------
// BQ.data.writer.Loggers
// XML writer that writes logger levels
//--------------------------------------------------------------------------------------

Ext.define('BQ.data.writer.Loggers', {
    extend: 'Ext.data.writer.Xml',
    alias: 'writer.bq-logger',

    writeRecords: function(request, data) {
        var record = request.records[0],
            item = null,
            xml = ['<resource>'];

        for (var i=0; (item=data[i]); ++i) {
            xml.push(Ext.String.format('<logger name="{0}" value="{1}" />', item.name, item.level));
        }
        xml.push('</resource>');
        request.xmlData = xml.join('');
        return request;
    }

});

//--------------------------------------------------------------------------------
// Logs
// TODO: add timestamp based append of log lines
//--------------------------------------------------------------------------------

Ext.define('BQ.admin.logs.Manager', {
    extend: 'Ext.container.Container',
    alias: 'widget.bq_logs_manager',

    componentCls: 'bq_logs',

    layout: {
        type: 'vbox',
        align : 'stretch',
        pack  : 'start',
    },

    initComponent: function() {

        this.items = [{
            xtype: 'toolbar',
            margin: false,
            border: false,
            defaults: {
                scale: 'large',
            },
            items:[{
                xtype: 'container',
                html: '<h2>Logs</h2>',
            }, '->', {
                xtype: 'button',
                //text: 'Refresh',
                iconCls : 'icon refresh',
                tooltip: 'Refresh logs',
                disabled: false,
                scope: this,
                handler: function() {
                    this.loadLogs();
                },
            }],
        }, /*{
            xtype: 'container',
            itemId: 'log_text',
            cls: 'editor',
            flex: 2,
            border : false,
            layout: 'fit',
            autoEl: {
                tag: 'textarea',
            },
        }*/];
        this.callParent();
    },

    afterRender: function() {
        this.callParent();
        this.loadConfig();
    },

    loadConfig: function() {
        this.setLoading('Loading...');
        Ext.Ajax.request({
            url: '/admin/logs/config',
            callback: function(opts, succsess, response) {
                if (response.status>=400 || !succsess)
                    BQ.ui.error(response.responseText);
                else
                    this.onConfig(response.responseXML);
            },
            scope: this,
            disableCaching: false,
        });
    },

    onConfig: function(xml) {
        var node = xml.firstChild,
            log_type = node.getAttribute('type'),
            log_uri = node.getAttribute('uri');
        if (log_type === 'local') {
            this.add({
                xtype: 'container',
                itemId: 'log_text',
                cls: 'editor',
                flex: 2,
                border : false,
                layout: 'fit',
                autoEl: {
                    tag: 'textarea',
                },
            });
            this.loadLogs();
        } else {
            this.add({
                xtype: 'container',
                itemId: 'log_iframe',
                flex: 2,
                border : false,
                layout: 'fit',
                autoEl: {
                    tag: 'iframe',
                    src: log_uri,
                },
            });
            this.setLoading(false);
        }
    },

    loadLogs: function() {
        this.setLoading('Loading...');
        Ext.Ajax.request({
            url: '/admin/logs/read',
            callback: function(opts, succsess, response) {
                if (response.status>=400 || !succsess)
                    BQ.ui.error(response.responseText);
                else
                    this.onLogs(response.responseText);
            },
            scope: this,
            disableCaching: false,
        });
    },

    onLogs: function(txt) {
        this.setLoading(false);
        var textarea = this.queryById('log_text'),
            ta = textarea.el.dom;
        //textarea.setValue(txt);
        ta.value = txt;
        ta.scrollTop = ta.scrollHeight;
    },

    appendLogs: function(ts) {

    },

});


//--------------------------------------------------------------------------------
// Groups
//--------------------------------------------------------------------------------

Ext.namespace('BQ.admin.groups');

Ext.define('BQ.model.Groups', {
    extend : 'Ext.data.Model',
    fields : [{
        name: 'name',
        mapping: '@name',
    }],
    proxy : {
        type: 'ajax',
        url : '/admin/group',

        batchActions: true,
        noCache : false,

        limitParam : undefined,
        pageParam: undefined,
        startParam: undefined,
        sortParam : undefined,
        filterParam : undefined,

        actionMethods: {
            create : 'POST', // 'PUT'
            read   : 'GET',
            update : 'POST',
            destroy: 'DELETE'
        },

        reader : {
            type :  'xml',
            root :  'resource',
            record: '>group',
        },

        writer : {
            type : 'bq-group',
            root : 'resource',
            record: '>group',
            writeAllFields : true,
            writeRecordId: false,
        },
    },
});

Ext.define('BQ.admin.groups.Manager', {
    extend: 'Ext.container.Container',
    alias: 'widget.bq_groups_manager',

    componentCls: 'bq_groups',

    layout: {
        type: 'vbox',
        align : 'stretch',
        pack  : 'start',
    },

    initComponent: function() {

        this.store = Ext.create('Ext.data.Store', {
            model : 'BQ.model.Groups',
            autoLoad : false,
            autoSync : true,
            listeners : {
                scope: this,
                //load: this.onUsersStoreLoaded,
            },
        });

        this.items = [{
            xtype: 'toolbar',
            margin: false,
            border: false,
            defaults: {
                scale: 'large',
            },
            items:[{
                xtype: 'button',
                itemId: 'ButtonAdd',
                text: 'Add',
                iconCls : 'icon add',
                tooltip: 'Add new group',
                handler: this.addGroupDlg,
                disabled: false,
                scope: this,
            }, {
                xtype: 'button',
                itemId: 'ButtonDelete',
                text: 'Delete',
                iconCls : 'icon remove',
                tooltip: 'Delete existing group',
                handler: this.deleteGroupDlg,
                scope: this,
                disabled: true,
            }, '->', {
                xtype:'textfield',
                itemId: 'search',
                cls: 'search_field',
                disabled: false,

                flex: 2,
                name: 'search',

                default_string: 'Filter groups',
                value: 'Filter groups',

                //minWidth: 100,
                //tooltip: 'Query for images using Bisque expressions',
                enableKeyEvents: true,
                listeners: {
                    scope: this,
                    afterrender: function() {},
                    focus: function(c) {
                        //c.flex = 2;
                        //this.doLayout();
                        if (c.value === c.default_string) {
                            c.setValue('');
                        }
                    },
                    // specialkey: function(f, e) {
                    //     if (e.getKey()==e.ENTER && f.value!='' && f.value != c.default_string) {
                    //         document.location = BQ.Server.url('/client_service/browser?tag_query='+escape(f.value));
                    //     }
                    // },
                    blur: function(c) {
                        //c.flex = 0;
                        //this.doLayout();
                    },
                    change: function ( c, newValue, oldValue ) {
                        if (newValue !== '' && newValue !== c.default_string) {
                            this.store.clearFilter(true);
                            var re = new RegExp(newValue, 'i');
                            this.store.filter(new Ext.util.Filter({
                                filterFn: function (object) {
                                    var match = false;
                                    Ext.Object.each(object.data, function (property, value) {
                                        //match = match || re.test(String(value));
                                        match = match || value.indexOf(newValue)===0;
                                    });
                                    return match;
                                  }
                            }));
                        } else {
                            this.store.clearFilter();
                        }
                    },
                },
            }, '', {
                xtype: 'button',
                //text: 'Refresh',
                iconCls : 'icon refresh',
                tooltip: 'Refresh groups',
                disabled: false,
                scope: this,
                handler: function() {
                    this.store.reload();
                },
            }],
        }, {
            xtype: 'gridpanel',
            itemId  : 'grid_groups',
            cls: 'groups',
            autoScroll: true,
            flex: 2,
            store: this.store,
            //plugins: [this.cellEditing],
            viewConfig: {
                stripeRows: true,
                forceFit: true,
            },

            listeners : {
                scope: this,
                selectionchange: function( me, selected, eOpts ) {
                    var btn = this.queryById('ButtonDelete');
                    btn.setDisabled(selected.length===0);
                },
            },

            columns: {
                defaults: {
                    tdCls: 'bq_row',
                    cls: 'bq_row',
                },
                items: [{
                    text: 'Name',
                    flex: 3,
                    dataIndex: 'name',
                    sortable: true,
                    //renderer: this.renderer_group,
                }],
            },
        }];
        this.callParent();
    },

    afterRender: function() {
        this.callParent();
        this.store.load();
        //this.queryById('search').setValue('');
    },

    renderer_group: function(v, metadata, record, rowIndex, colIndex, store) {
        //metadata.css = record.data.level.toLowerCase();
        return v;
    },

    addGroupDlg: function() {
        Ext.MessageBox.prompt(
            'Create group',
            'Please enter a new group name:',
            function(btn, name) {
                if (btn !== 'ok' || !name) return;
                this.onAddGroup(name);
            },
            this
        );
    },

    onAddGroup: function(name) {
        // Create a model instance
        var recs = this.store.add({
            name: name,
        });
        //recs[0].setDirty();
        //this.queryById('main_grid').view.refresh();

        // clear combo box when successfully added share
        //this.queryById('user_combo').setValue('');
    },

    deleteGroupDlg: function() {
        var record = this.queryById('grid_groups').getView().getSelectionModel().getSelection()[0];
        var win = Ext.MessageBox.show({
            title: 'Delete group',
            msg: 'Are you sure you want to delete group '+record.data.name+'?',
            buttons: Ext.MessageBox.OKCANCEL,
            fn: function(buttonResponse) {
                if (buttonResponse === "ok") {
                    //this.onDeleteGroup(resource_uniq)
                    //record.remove();
                    this.store.remove(record);
                }
            },
            scope: this,
        });
    },

    onDeleteGroup: function() {
        var selection = this.queryById('grid_groups').getView().getSelectionModel().getSelection()[0];
        if (selection) {
            this.store.remove(selection);
        }
    },

});

//--------------------------------------------------------------------------------------
// BQ.data.writer.groups
// XML writer that writes group levels
//--------------------------------------------------------------------------------------

Ext.define('BQ.data.writer.Groups', {
    extend: 'Ext.data.writer.Xml',
    alias: 'writer.bq-group',

    writeRecords: function(request, data) {
        var record = request.records[0],
            item = null,
            xml = ['<resource>'];

        if (request.action === 'destroy') {
            request.url += '/' + encodeURIComponent(record.data.name);
        } else {
            for (var i=0; (item=data[i]); ++i) {
                xml.push(Ext.String.format('<group name="{0}" />', item.name));
            }
            xml.push('</resource>');
            request.xmlData = xml.join('');
        }


        return request;
    }

});


