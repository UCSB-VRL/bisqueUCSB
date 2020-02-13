
//--------------------------------------------------------------------------------------
// Toolbar actions
//--------------------------------------------------------------------------------------

var urlAction = function(url) {
    window.open(url);
};

var pageAction = function(url) {
    document.location = url;
};

var iframeAction = function( url, title ) {
   var w = Ext.create('Ext.window.Window', {
       title: (title && typeof title == 'string') ? title : undefined,
       modal: true,
       width: BQApp?BQApp.getCenterComponent().getWidth()/1.05:document.width/1.05,
       height: BQApp?BQApp.getCenterComponent().getHeight()/1.05:document.height/1.05,

       buttonAlign: 'center',
       //autoScroll: true,
       border: 0,
       html: Ext.String.format('<iframe style="border: 0px; width: 100%; height: 100%; padding: 10px;" src="{0}"></iframe>', url),
       buttons: [{
           text: 'Ok',
           handler: function () { w.close(); }
       }],
   });
   w.show();
};

var htmlAction = function( url, title ) {
    var w = Ext.create('Ext.window.Window', {
        title: (title && typeof title == 'string') ? title : undefined,
        width: BQApp?BQApp.getCenterComponent().getWidth()/1.6:document.width/1.6,
        height: BQApp?BQApp.getCenterComponent().getHeight()/1.1:document.height/1.1,

        modal: true,
        buttonAlign: 'center',
        plain : true,
        layout: 'fit',
        border: 0,

        items: [{
            xtype: 'component',
            layout: 'fit',
            border: 0,
            autoEl: {
                tag: 'iframe',
                src: url,
                frameborder: "0",
            },
        }],

        buttons: [{
            text: 'Ok',
            handler: function () { w.close(); }
        }],
    });
    w.show();
};

function analysisAction(o, e) {
    var w = Math.round(Math.min(500, BQApp?BQApp.getCenterComponent().getWidth()*0.8:document.width*0.8));
    var h = Math.round(BQApp?BQApp.getCenterComponent().getHeight()*0.99:document.height*0.99);

    var resourceBrowser = Ext.create('Bisque.ResourceBrowser.Browser', {
        layout: Bisque.ResourceBrowser.LayoutFactory.LAYOUT_KEYS.IconList,
        wpublic: true,
        selType: 'SINGLE',
        viewMode: 'ModuleBrowser',
        showOrganizer: false,
        dataset : '/module_service/',
        listeners : {
            'Select' : function(rb, module) {
                if (module.available === false) return;
                if (BQApp.resource)
                    pageAction('/module_service/' + module.name + '/?wpublic=1&resource=' + BQApp.resource.uri );
                else
                    pageAction('/module_service/' + module.name + '/?wpublic=1');
            },
        }
    });

    var tip = Ext.create('Ext.tip.ToolTip', {
        target: o.el,
        //anchor: "right",
        anchor: 'bottom',
        width :  w,
        maxWidth: w,
        minWidth: w,
        height:  h,
        layout: 'fit',
        autoHide: false,
        shadow: true,
        items: [resourceBrowser]
    });
    tip.show();
}

//------------------------------------------------------------------------------
// BQ.help.Video
//------------------------------------------------------------------------------

Ext.define('BQ.help.Video', {
    extend: 'Ext.Component',
    alias: 'widget.bq_help_video',
    componentCls: 'bq-help-video',

    border: false,
    layout: 'fit',
    autoEl: {
        //tag: 'div',
        tag: 'iframe',
        src: '',
        frameborder: "0",
        allowfullscreen: '',
    },

    iframe_youtube: '<iframe src="{1}" frameborder="0" allowfullscreen></iframe>',

    afterRender: function() {
        this.callParent();
        if (this.video) {
        	this.setVideo(this.video);
        }
    },

    setVideo : function(url) {
        this.setVideoYoutube(url);
    },

    setVideoYoutube : function(url) {
    	this.video = url;
    	var el = this.getEl();
    	if (el && el.dom) {
    	    //el.dom.innerHTML = this.iframe_youtube.replace('{1}', url);
            el.dom.src = url;
    	}
    },
});


//--------------------------------------------------------------------------------------
// Main Bisque toolbar menu
//--------------------------------------------------------------------------------------

Ext.define('BQ.Application.Toolbar', {
    extend: 'Ext.toolbar.Toolbar',
    requires: ['Ext.toolbar.Toolbar', 'Ext.tip.QuickTipManager', 'Ext.tip.QuickTip', 'Ext.toolbar.Spacer'],

    // default toolbar config
    region: 'north',
    border: false,
    layout: { overflowHandler: 'Menu',  },
    defaults: { scale: 'large',  },
    cls: 'toolbar-main',
    preferences : {},

    title: 'Bisque demo',
    toolbar_opts: { 'browse':true, 'upload':true, 'download':true, 'services':true, 'query':true },
    image_query_text: 'Find resources using tags',

    tools_big_screen: [ 'button_upload', 'button_download' ],

    tools_none: [ 'menu_user_signin', 'menu_user_register', 'menu_user_register_sep','menu_user_recover' ],
    tools_user: ['menu_user_name', 'menu_user_profile', 'menu_user_signout', 'menu_user_prefs',
                 'menu_user_signout_sep', 'menu_resource_template', 'menu_resource_create', 'button_create', 'button_upload',
                  'menu_module', 'menu_module_developer','menu_preference', 'menu_user_admin_separator'], //chris's new stuff
    tools_admin: ['menu_user_admin', 'menu_user_admin_prefs', 'menu_user_manager',
                  'menu_system',],

    initComponent : function() {
        this.images_base_url = this.images_base_url || BQ.Server.url('/core/images/toolbar/');
        this.title = BQ.Server.title || this.title;

        Ext.QuickTips.init();
        Ext.tip.QuickTipManager.init();
        var toolbar = this;

        /*
        BQ.Preferences.get({
            key : 'Toolbar',
            callback : Ext.bind(this.onPreferences, this),
        });
        */
        //--------------------------------------------------------------------------------------
        // Services menu
        //--------------------------------------------------------------------------------------

        this.menu_services = {
            xtype: 'menu',
            cls: 'toolbar-menu',
            plain: true,
            items: [{
                text: 'Analysis',
                handler: analysisAction,
            }, '-', {
                text: 'Import',
                iconCls: 'icon-import',
                handler: Ext.Function.pass(pageAction, '/import/'),
            }, {
                text: 'Export',
                iconCls: 'icon-export',
                handler: Ext.Function.pass(pageAction, '/export/'),
            }, '-', {
                text: 'Statistics',
                handler: Ext.Function.pass(pageAction, '/stats/'),
            }],
        };

        //--------------------------------------------------------------------------------------
        // Create menu
        //--------------------------------------------------------------------------------------

        this.menu_create = {
            xtype: 'menu',
            cls: 'toolbar-menu',
            itemId  : 'menu_create',
            plain: true,
            hidden: true,
            items: [{
                text    : 'Create a new <b>dataset</b>',
                itemId  : 'menu_create_dataset',
                handler: Ext.Function.pass(this.createNewResource, ['dataset'], this),
                scope   : this,
            },{
                text    : 'Create a new <b>template</b>',
                itemId  : 'menu_create_template',
                handler: Ext.Function.pass(this.createNewResource, ['template'], this),
                scope   : this,
            }, '-', '-', {
                text    : 'Create a new resource',
                itemId  : 'menu_create_resource',
                handler : this.createResource,
                scope   : this,
            }/*, {
                itemId  : 'menu_create_from_template',
                text    : 'Create resource from template',
                handler : function() {this.createResourceFromTemplate()}, //this.createResourceFromTemplate, Utkarsh : arg passed to that function should be blank
                scope   : this,
            }*/],
        };

        //--------------------------------------------------------------------------------------
        // User menu
        //--------------------------------------------------------------------------------------

        // Sign in menu item
        /*
        var signin = {
            itemId: 'menu_user_signin',
            plain: true,
            xtype: 'form',
            id: 'login_form',
            layout: 'form', // uncomment for extjs 4.1
            cls: 'loginmenu',
            standardSubmit: true,
            border: false,
            bodyBorder: false,
            url: '/auth_service/login_check',
            width: 350,
            fieldDefaults: {
                msgTarget: 'side',
                border: 0,
            },
            items: [{
                xtype: 'hiddenfield',
                name: 'came_from',
                value: document.location,
                allowBlank: true,
            }, {
                xtype: 'textfield',
                fieldLabel: 'User name',
                name: 'login',
                //id: 'loginusername',
                inputId: 'loginusername',
                allowBlank: false,

                fieldSubTpl: [ // note: {id} here is really {inputId}, but {cmpId} is available
                    '<input id="{id}" type="{type}" {inputAttrTpl}',
                        ' size="1"', // allows inputs to fully respect CSS widths across all browsers
                        '<tpl if="name"> name="{name}"</tpl>',
                        '<tpl if="value"> value="{[Ext.util.Format.htmlEncode(values.value)]}"</tpl>',
                        '<tpl if="placeholder"> placeholder="{placeholder}"</tpl>',
                        '<tpl if="maxLength !== undefined"> maxlength="{maxLength}"</tpl>',
                        '<tpl if="readOnly"> readonly="readonly"</tpl>',
                        '<tpl if="disabled"> disabled="disabled"</tpl>',
                        '<tpl if="tabIdx"> tabIndex="{tabIdx}"</tpl>',
                        '<tpl if="fieldStyle"> style="{fieldStyle}"</tpl>',
                    ' class="{fieldCls} {typeCls} {editableCls}" autocomplete="on" autofocus="true" />',
                    {
                        disableFormats: true,
                    }
                ],

                listeners: {
                    specialkey: function(field, e){
                        if (e.getKey() == e.ENTER) {
                            var form = field.up('form').getForm();
                            form.submit();
                        }
                    }
                },
            }],

            buttons: [{
                xtype: 'button',
                text: 'Sign in',
                formBind: true, //only enabled once the form is valid
                disabled: true, // uncomment for extjs 4.1
                handler: function() {
                    var form = this.up('form').getForm();
                    if (form.isValid())
                        form.submit();
                }
            }],

            autoEl: {
                tag: 'form',
            },

            listeners: {
                render: function() {
                    this.el.set({ autocomplete: 'on' });
                },
            },
        };
        */

        var signin = {
            itemId:  'menu_user_signin',
            xtype:   'button',
            text:    'Sign in',
            scale:   'medium',
            //iconCls: 'icon-user',
            handler: Ext.Function.pass(pageAction, BQ.Server.url('/auth_service/login')),
        };

        this.menu_user = {
            xtype: 'menu',
            cls: 'toolbar-menu',
            plain: true,
            items: [{
                plain: true,
                cls: 'toolbar-menu',
            }, {
                xtype:'tbtext',
                itemId: 'menu_user_name',
                text: 'Sign in',
                indent: true,
                hidden: true,
                cls: 'menu-heading',
            }, {
                text: 'Profile',
                itemId: 'menu_user_profile',
                hidden: true,
                handler: Ext.Function.pass(pageAction, BQ.Server.url('/registration/edit_user')), // preferences loaded in onPreferences
            }, {
                xtype:'menuseparator',
                itemId: 'menu_user_admin_separator',
                hidden: true,
            }, {
                text: 'Users',
                itemId: 'menu_user_manager',
                hidden: true,
                handler: this.settingUserPage,
            }, {
                text: 'Module Manager',
                itemId: 'menu_module',
                hidden: true,
                handler: this.settingModuleManagerPage,
            }, {
                text: 'Module Developer',
                itemId: 'menu_module_developer',
                hidden: true,
                handler: this.settingModuleDeveloperPage,
            }, {
                text: 'Preferences',
                itemId: 'menu_preference',
                hidden: true,
                handler: this.settingPreferencePage,
            }, {
                xtype: 'menuseparator',
                itemId: 'menu_user_signout_sep',
                hidden: true,
            }, {
                text: 'Sign out',
                itemId: 'menu_user_signout',
                hidden: true,
                handler: Ext.Function.pass(pageAction, BQ.Server.url('/auth_service/logout_handler')),
            }, signin, {
                xtype: 'menuseparator',
                itemId: 'menu_user_register_sep',
            }, {
                text: 'Register new user',
                itemId: 'menu_user_register',
                handler: Ext.Function.pass(pageAction, BQ.Server.url('/auth_service/login')),  // preferences loaded in onPreferences
            }, {
                text: 'Recover Password',
                itemId: 'menu_user_recover',
                handler: Ext.Function.pass(pageAction, BQ.Server.url('/auth_service/login')), // preferences loaded in onPreferences
            }],
        };

        //--------------------------------------------------------------------------------------
        // Help menu
        //--------------------------------------------------------------------------------------
        var menu_help = {
            xtype: 'menu',
            cls: 'toolbar-menu',
            plain: true,
            items: [{
                xtype:'tbtext',
                text: '<div class="image-about-bisque"></div>',
                indent: true,
            }, {
                xtype:'tbtext', text: 'Contextual help video:',
                indent: true,
                cls: 'menu-heading',
            }, {
                xtype:'bq_help_video',
                itemId: 'help_video_contextual',
                video: '//www.youtube.com/embed/_tq62SJ8SCw?list=PLAaP7tKanFcyR5cjJsPTCa0CDmWp9unds', // set default bisque overview help video
                indent: true,
            }, '-', {
                text: 'About',
                itemId: 'menu_help_about',
                handler: Ext.Function.pass(htmlAction, [BQ.Server.url('/client_service/about'), 'About'] ),
            }, {
                text: 'Privacy policy',
                itemId: 'menu_help_privacy_policy',
                handler: Ext.Function.pass(htmlAction, BQ.Server.url('/client_service/about/privacypolicy.html')),
            }, {
                text: 'Terms of use',
                itemId: 'menu_help_terms_of_use',
                handler: Ext.Function.pass(htmlAction, BQ.Server.url('/client_service/about/termsofuse.html') ),
            }, {
                text: 'License',
                itemId: 'menu_help_license',
                handler: Ext.Function.pass(htmlAction, BQ.Server.url('/client_service/about/license.html') ),
            }, '-', {
                text: 'Usage statistics',
                itemId: 'menu_help_usage_statistics',
                handler: Ext.Function.pass(pageAction, BQ.Server.url('/usage/') ),
            }, '-', {
                text: 'Online Help',
                itemId: 'menu_help_help',
                handler: Ext.Function.pass(urlAction, BQ.Server.url('/client_service/help')),
            }, {
                text: 'Project website',
                itemId: 'menu_help_project_website',
                handler: Ext.Function.pass(urlAction, 'http://bioimage.ucsb.edu/bisque'),
            }, '-', {
                xtype:'tbtext', text: 'Problems with Bisque?',
                indent: true,
                cls: 'menu-heading',
            }, {
                text: 'Developers website',
                itemId: 'menu_help_developers_website',
                handler: Ext.Function.pass(urlAction, 'http://biodev.ece.ucsb.edu/projects/bisquik'),
            }, {
                text: 'Submit a bug or suggestion',
                itemId: 'menu_help_submit_bug',
                handler: Ext.Function.pass(urlAction, 'http://biodev.ece.ucsb.edu/projects/bisquik/newticket'),
            }, {
                text: 'Send us e-mail',
                itemId: 'menu_help_email',
                handler: Ext.Function.pass(urlAction, 'mailto:bisque-bioimage@googlegroups.com'),
            }],
        };


        //--------------------------------------------------------------------------------------
        // Toolbar items
        //--------------------------------------------------------------------------------------
        // window.innerWidth window.innerHeight document.body.clientWidth document.body.clientHeight
        var w = Math.round(Math.min(800, (typeof BQApp !== 'undefined') ? BQApp.getCenterComponent().getWidth()*0.8 : window.innerWidth*0.8));
        var h = Math.round(Math.max(400,  (typeof BQApp !== 'undefined') ? BQApp.getCenterComponent().getHeight()*0.8 : window.innerHeight*0.8));
        var browse_vis = (this.toolbar_opts && this.toolbar_opts.browse===false) ? false : true;
        this.items = [{
                xtype:'tbtext',
                text: '<a href="/" class="main-logo"></a>',
            }, /*{
                xtype:'tbtext',
                itemId: 'menu_title',
                text: '<h3><a href="/">'+this.title+'</a></h3>',
            },*/ {
                xtype: 'tbspacer',
                width: 20,
            }, {
                xtype : 'button',
                itemId: 'button_create',
                menu  : this.menu_create,
                iconCls : 'icon-create',
                text  : 'Create',
                hidden: true, // should only be visible for logged-in users
            }, {
                text: 'Upload',
                itemId: 'button_upload',
                iconCls : 'icon-import',
                tooltip: '',
                hidden: true, // should only be visible for logged-in users
                //handler: Ext.Function.pass(pageAction, BQ.Server.url('/import/upload')),
                handler: function() {
                    var uploader = Ext.create('BQ.upload.Dialog', {
                        destory_on_upload: false,
                        /*listeners: {
                            scope: this,
                            uploaded: function(reslist) {
                                   var i = this; var r = reslist[0];
                                   setTimeout(function() { i.onselected(r); }, 100);
                            },
                        },*/
                    });
                },
            }, {
                text: 'Download',
                itemId: 'button_download',
                iconCls : 'icon-export',
                //handler: Ext.Function.pass(pageAction, '/export/'),
                tooltip: '',
                menu: {
                    xtype: 'menu',
                    cls: 'toolbar-menu',
                    plain: true,
                    items: [{
                        text: 'Download manager',
                        handler: function() {
                            //pageAction('/export/' + (BQApp.resource ? '?resource=' + BQApp.resource.uri : '') );
                            var downloader = Ext.create('BQ.export.Dialog', {
                                resource: BQApp.resource ? BQApp.resource.uri : undefined,
                            }).show();
                        },
                    }, '-',
                    ],
                },
            }, {
                xtype : 'button',
                itemId: 'button_analysis',
                //menu  : this.menu_services,
                iconCls : 'icon-analysis',
                text  : 'Analyze',
                //handler: analysisAction,
                menu: {
                    xtype: 'menu',
                    cls: 'toolbar-menu',
                    plain: true,
                    items: [{
                        //xtype: 'bq-resource-browser',
                        xtype: 'bq-module-browser',
                        itemId: 'analysis_browser',
                        width :  w,
                        height:  h,
                        layout: Bisque.ResourceBrowser.LayoutFactory.LAYOUT_KEYS.IconList,
                        wpublic: true,
                        selType: 'SINGLE',
                        viewMode: 'ModuleBrowser',
                        //showOrganizer: true,
                        showModuleOrganizer: true,
                        dataset : '/module_service/',
                        wpublic: 'true',
                        listeners : {
                            scope: this,
                            Select : this.dispatch_module,
                        }
                    }],
                },
            }, {
                xtype : 'button',
                itemId: 'button_services',
                menu  : this.menu_services,
                iconCls : 'icon-services',
                text  : 'Services',
                hidden: true,
            }, {
                itemId: 'menu_images',
                xtype:'button',
                text: 'Browse',
                iconCls : 'icon-browse',
                //hidden: !browse_vis,
                tooltip: 'Browse resources',
                menu: {
		            xtype: 'menu',
		            cls: 'toolbar-menu',
		            plain: true,
		            items: [],
		        },
                /*handler: function(c) {
                    var q = '';
                    var m = toolbar.queryById('menu_query');
                    if (m && m.value != toolbar.image_query_text) { q = '?tag_query='+escape(m.value); }
                    document.location = BQ.Server.url('/client_service/browser'+q);
                },*/
            }, {
                itemId: 'menu_resources',
                text: 'Resources',
                iconCls : 'icon-browse',
                tooltip: 'Browse resources',
                //hidden: browse_vis,
                hidden: true,
                menu: {
		            xtype: 'menu',
		            cls: 'toolbar-menu',
		            plain: true,
		            items: [],
		        },
            }, {
                xtype: 'tbspacer',
                width: 10,
                hidden: !browse_vis,
            }, {
                itemId: 'menu_query',
                xtype:'textfield',
                cls: 'search_field',
                flex: 0, // 2
                name: 'search',
                value: this.image_query_text,
                hidden: !browse_vis,
                minWidth: 100,
                tooltip: 'Query for images using Bisque expressions',
                enableKeyEvents: true,
                listeners: {
                    scope: this,
                    focus: function(c) {
                        c.flex = 2;
                        this.doLayout();
                        if (c.value === toolbar.image_query_text) {
                            c.setValue('');
                        }
                        var tip = Ext.create('Ext.tip.ToolTip', {
                            target: c.el,
                            anchor: 'top',
                            minWidth: 500,
                            width: 500,
                            autoHide: true,
                            dismissDelay: 20000,
                            shadow: true,
                            autoScroll: true,
                            loader: { url: '/core/html/querying.html', renderer: 'html', autoLoad: true },
                        });
                        tip.show();
                    },
                    specialkey: function(f, e) {
                        if (e.getKey()==e.ENTER && f.value!='' && f.value != toolbar.image_query_text) {
                            document.location = BQ.Server.url('/client_service/browser?tag_query='+escape(f.value));
                        }
                    },
                    blur: function(c) {
                        c.flex = 0;
                        this.doLayout();
                    },
                }
            }, '->', {
                itemId: 'menu_user',
                menu: this.menu_user,
                iconCls: 'icon-user',
                text: 'Sign in',
                tooltip: 'Edit your user account',
                plain: true,
            }, {
                menu: menu_help,
                iconCls: 'icon-help',
                tooltip: 'All information about Bisque',
            },
        ];

        //--------------------------------------------------------------------------------------
        // final touches
        //--------------------------------------------------------------------------------------
        //this.addListener( 'resize', this.onResized, this);
        this.callParent();
        BQ.Preferences.on('update_user_pref', this.onPreferences, this);
        BQ.Preferences.on('onerror_user_pref', this.onPreferences, this);
        //checks to see if preference has been loaded already
        if (BQ.Preferences.isLoaded('user'))
            this.onPreferences();

        // update user menu based on application events
        Ext.util.Observable.observe(BQ.Application);
        BQ.Application.on('gotuser', function(u) {
            this.queryById('menu_user').setText( u.display_name );
            this.queryById('menu_user_name').setText( u.display_name+' - '+u.email_address );

            // hide no user menus
            for (var i=0; (p=this.tools_none[i]); i++)
                this.setSubMenuVisibility(p, false);

            // show user menus
            for (var i=0; (p=this.tools_user[i]); i++)
                this.setSubMenuVisibility(p, true);

            // show admin menus
            if (u && u.is_admin())
            for (var i=0; (p=this.tools_admin[i]); i++)
                this.setSubMenuVisibility(p, true);

        }, this);

        BQ.Application.on('signedin', function() {
            //console.log('signed in !!!!!');
        });

        BQ.Application.on('signedout', function() {
            // show no user menus
            for (var i=0; (p=this.tools_none[i]); i++)
                this.setSubMenuVisibility(p, true);

            // hide user menus
            for (var i=0; (p=this.tools_user[i]); i++)
                this.setSubMenuVisibility(p, false);

            // hide user menus
            for (var i=0; (p=this.tools_admin[i]); i++)
                this.setSubMenuVisibility(p, false);

        }, this);

        this.fetchResourceTypes();
    },

    setSubMenuVisibility: function(id, v) {
        var m = this.queryById(id);
        if (m) m.setVisible(v);
    },

    onResized: function() {
        /*var w = this.getWidth();
        if (w<1024) {
            for (var i=0; id=this.tools_big_screen[i]; ++i)
               this.queryById(id).setVisible(false);
        } else {
            for (var i=0; id=this.tools_big_screen[i]; ++i)
               this.queryById(id).setVisible(true);
        }*/
    },

    //only admin
    settingUserPage: function() {
        var settings = Ext.create('BQ.setting.Dialog', {
            activeTab: 0,
        });
    },

    //always visible
    settingModuleManagerPage: function() {
        var settings = Ext.create('BQ.setting.Dialog', {
            activeTab: 3,
        });
    },

    //always visible
    settingModuleDeveloperPage: function() {
        var settings = Ext.create('BQ.setting.Dialog', {
            activeTab: 4,
        });
    },

    //should go to the highest level
    settingPreferencePage: function() {
        var settings = Ext.create('BQ.setting.Dialog', {
            activeTab: 5,
        });
    },

    fetchResourceTypes : function() {
        BQFactory.request ({
            uri : '/data_service/',
            cb : callback(this, 'onResourceTypes'),
            errorcb : function(error) {
                BQ.ui.error('Error fetching resource types:<br>'+error.message, 4000);
            },
            cache : false,
        });

        BQFactory.request ({
            uri : '/data_service/template/',
            cb : callback(this, 'onTemplateTypes'),
            errorcb : function(error) {
                BQ.ui.error('Error fetching template types:<br>'+error.message, 4000);
            },
            cache : false,
        });
    },

    onResourceTypes : function(resource) {
        var types = {};
        BQApp.resourceTypes = [];
        var r=null;
        for (var i=0; (r=resource.children[i]); i++) {
            BQApp.resourceTypes.push({name:r.name, uri:r.uri});
            types[r.name] = '/data_service/' + r.name;
        }
        this.addBrowseResourceTypes(types);
        this.addCreateResourceTypes(types);
    },

    onTemplateTypes : function(resource) {
        var types = [];
        var r;
        for (var i=0; (r=resource.children[i]); i++) {
            types.push({
                name: r.name,
                uri: r.uri,
            });
        }
        types.sort();
        types.reverse();
        var t;
        for (var i=0; (t=types[i]); i++) {
            var name = t.name;
            var uri = t.uri;
            if (name)
            this.queryById('menu_create').insert(3, {
                text    : 'Create a new <b>'+name+'</b>',
                itemId  : 'menu_create_'+name.replace(' ', '_'),
                handler: Ext.Function.pass(this.createNewTemplate, [name, uri], this),
                scope   : this,
            });
        }
    },

    addBrowseResourceTypes : function(types) {
        types = Ext.Object.merge(types, BQ.resources.preferred);

        var keys = Object.keys(types).sort(),
            name = null,
            menu_items = [],
            path = null;
        for (var i=0; name=keys[i]; ++i) {
            path = types[name] || '/data_service/'+name;
            menu_items.push({
                text: name,
                scope: this,
                handler: Ext.Function.pass(this.doBrowse, '/client_service/browser?resource='+path),
            });
        }

        this.queryById('menu_images').menu.add(menu_items);
        this.queryById('menu_resources').menu.add(menu_items);
    },

    doBrowse : function (url) {
        var q = '';
        var m = this.queryById('menu_query');
        if (m && m.value != this.image_query_text) { q = '&tag_query='+escape(m.value); }
        pageAction(url+q);
    },

    addCreateResourceTypes : function(types) {
        var mytypes =  Ext.Object.merge(types, BQ.resources.preferred);
        BQ.resources.all = Ext.Object.merge(types, BQ.resources.known);
        /*
        for (var name in mytypes) {
            if (!(name in BQ.resources.ignore))
            this.queryById('menu_create').add({
                text    : 'Create '+name,
                itemId  : 'menu_create_'+name,
                //handler : function() {this.createResource(types, name);},
                handler: Ext.Function.pass(this.createResource, [types, name], this),
                scope   : this,
            });
        }*/

        this.queryById('menu_create_resource').handler = function() {this.createResource(mytypes);};
    },

    createResource : function(types, def) {
        var mykeys =  Ext.Object.merge(types, BQ.resources.preferred);
        if (def) mykeys[def] = null;
        var mydata = [];
        for (var k in mykeys)
            if (!(k in BQ.resources.ignore))
                mydata.push([k]);

        store_types = Ext.create('Ext.data.ArrayStore', {
            fields: [ {name: 'name',}, ],
            data: mydata,
        });
        var ignore = BQ.resources.ignore;
        var formpanel = Ext.create('Ext.form.Panel', {
            //url:'save-form.php',
            frame:true,
            bodyStyle:'padding:5px 5px 0',
            width: 350,
            fieldDefaults: {
                msgTarget: 'side',
                labelWidth: 75
            },
            defaultType: 'textfield',
            defaults: {
                anchor: '100%'
            },

            items: [{
                xtype : 'combobox',
                fieldLabel: 'Type',
                name: 'type',
                allowBlank: false,
                value: def,

                store     : store_types,
                displayField: 'name',
                valueField: 'name',
                queryMode : 'local',

                //invalidText: 'This type is not allowed for creation!',
                validator: function(value) {
                    if (value in ignore) return 'This type is not allowed for creation!';
                    if (/[^\w]/.test(value)) return 'Resource type may only contain word characters: letters, digits, dash and underscore';
                    return true;
                },
            },{
                fieldLabel: 'Name',
                name: 'name',
                allowBlank: false,
            }],

        });

        var w = Ext.create('Ext.window.Window', {
            layout : 'fit',
            modal : true,
            border : false,
            title: 'Create new resource',
            buttonAlign: 'center',
            items: formpanel,
            buttons: [{
                text: 'Save',
                scope: this,
                handler: function () {
                    var form = formpanel.getForm();
                    if (form.isValid()) {
                        var v = form.getValues();
                        var resource = BQFactory.make(v.type, undefined, v.name);
                        resource.save_('/data_service/'+v.type,
                                       callback(this, this.onResourceCreated),
                                       callback(this, this.onResourceError));
                        formpanel.ownerCt.hide();
                    };
                }
            }, {
                text: 'Cancel',
                //scope: this,
                handler: function (me) {
                    formpanel.ownerCt.hide();
                }
            }]

        }).show();
    },

    createNewResource : function(type) {
        var t = type;
        Ext.MessageBox.prompt(
            'Create '+type,
            'Please enter a new <b>'+type+'</b> name:',
            function(btn, name) {
                if (btn !== 'ok' || !name) return;
                var resource = BQFactory.make(t, undefined, name);
                resource.save_('/data_service/'+t,
                               callback(this, this.onResourceCreated),
                               callback(this, this.onResourceError));
            },
            this
        );
    },

    onResourceCreated: function(resource) {
        document.location = '/client_service/view?resource='+resource.uri;
    },

    onResourceError: function(message) {
        BQ.ui.error('Error creating resource: <br>'+message);
    },

    createNewTemplate : function(type, uri) {
        var t = type;
        var u = uri;
        Ext.MessageBox.prompt(
            'Create an instance of '+type,
            'Please enter a new <b>'+type+'</b> name:',
            function(btn, name) {
                if (btn !== 'ok' || !name) return;
                BQ.TemplateManager.createResource({name: name}, this.onResourceCreated, undefined, u);
            },
            this
        );
    },

    setMenuHandler: function(menuitem, f, url, _def) {
        f = f || pageAction;
        if (!(url || _def)) {
            menuitem.setVisible(false);
        } else {
            menuitem.setHandler( Ext.Function.pass(f, url || _def), this );
        }
    },

    onPreferences: function() {
        var registration = BQ.Preferences.get('user', 'Toolbar/registration', '/auth_service/login');
        if (registration === 'disabled') {
            this.queryById('menu_user_register').setVisible(false);
            this.queryById('menu_user_profile').setVisible(false);
            this.queryById('menu_user_recover').setVisible(false);
        } else {
            this.setMenuHandler( this.queryById('menu_user_profile'), pageAction, BQ.Preferences.get('user', 'Toolbar/user_profile', '/registration/edit_user') );
            this.setMenuHandler( this.queryById('menu_user_register'), pageAction, registration );
            this.setMenuHandler( this.queryById('menu_user_recover'), pageAction, BQ.Preferences.get('user', 'Toolbar/password_recovery', '/auth_service/login') );
        }

        var h = [
            { f: htmlAction, n: 'about', d: '/client_service/about' },
            { f: htmlAction, n: 'privacy_policy', d: '/client_service/about' },
            { f: htmlAction, n: 'terms_of_use', d: '/client_service/about/termsofuse.html' },
            { f: htmlAction, n: 'license', d: '/client_service/about/license.html' },
            { f: pageAction, n: 'usage_statistics', d: '/usage/' },
            { f: urlAction,  n: 'help', d: '/client_service/help' },
            { f: urlAction,  n: 'project_website', d: 'http://bioimage.ucsb.edu/bisque' },
            { f: urlAction,  n: 'developers_website', d: 'http://biodev.ece.ucsb.edu/projects/bisquik' },
            { f: urlAction,  n: 'submit_bug', d: 'http://biodev.ece.ucsb.edu/projects/bisquik/newticket' },
            { f: urlAction,  n: 'email', d: 'mailto:bisque-bioimage@googlegroups.com' },
        ];
        var e = null;
        for (var i=0; (e=h[i]); ++i) {
            this.setMenuHandler( this.queryById('menu_help_'+e.n), e.f, BQ.Preferences.get('user', 'Toolbar/'+e.n, e.d) );
        }

        //if (this.preferences.title)
        //    this.queryById('menu_title').setText( '<h3><a href="/">'+this.preferences.title+'</a></h3>' );

    },

    setActiveHelpVideo: function(url) {
        var v = this.queryById('help_video_contextual');
        v.setVideo(url);
    },

    setAnalysisQuery: function(q) {
        var a = this.queryById('analysis_browser');
        if (!a) {
            a = this.queryById('button_analysis');
            a.menu[0].dataset = '/module_service/';
            a.menu[0].tagQuery = q;
            a.menu[0].wpublic = 'true';
        } else {
            a.initQuery({
                baseURL: '/module_service/',
                dataset: '/module_service/',
                offset: 0,
                tag_order: '"@ts":desc',
                tag_query: q,
                wpublic: 'true',
            });
        }
    },

    dispatch_module : function(rb, module) {
        if (module.available === false) return;
        if (module.tags_index['execute_options/type'] === 'external') {
            var url = module.tags_index['interface'];
            if (BQApp.resource)
                url += '?resource=' + BQApp.resource.uri;
            iframeAction( url, '' );
            return;
        }

        if (BQApp.resource)
            pageAction('/module_service/' + module.name + '/?wpublic=1&resource=' + BQApp.resource.uri);
        else
            pageAction('/module_service/' + module.name  + '/?wpublic=1');
    },

    add_to_menu: function(menu_id, items, position) {
        // take care of items array as input
        if (Array.isArray(items)) {
            for (var i=0; i<items.length; ++i) {
                this.add_to_menu(menu_id, items[i], position);
                if (typeof position !== 'undefined') {
                    ++position;
                }
            }
            return;
        }

        // single input case
        var btn = BQApp.getToolbar().queryById(menu_id);
        if (!btn) return;

        // test if item exists then update
        var m = btn.menu.queryById(items.itemId);
        if (m) {
            for (var k in items) {
                m[k] = items[k];
            }
            return;
        }

        // item does not exist: add or insert
        if (position) {
            btn.menu.insert(position, items);
        } else {
            btn.menu.add(items);
        }
    },

});
