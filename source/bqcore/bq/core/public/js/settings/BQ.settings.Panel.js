
Ext.define('BQ.setting.Dialog', {
    extend : 'Ext.window.Window',
    alias: 'widget.bqsettingsdialog',
    border: 0,
    title: 'Settings',
    layout: 'fit',
    modal : true,
    width : '85%',
    height : '85%',
    buttonAlign: 'center',
    bodyCls: 'bq_settings_dialog',

    constructor : function(config) {
        config = config || {};
        Ext.apply(this, {
            items  : [{
                xtype: 'bq_settings_panel',
                itemId: 'bq_settings_panel',
                border: 0,
                activeTab: config.activeTab,
            }]
        }, config);

        this.callParent(arguments);
        this.show();
    },
});

Ext.define('BQ.setting.Panel', {
    extend : 'Ext.tab.Panel',
    alias: 'widget.bq_settings_panel',

    border: false,
    plain: true,
    componentCls: 'bq_settings_panel',

    defaults: {
        border: false,
        hidden: true,
    },

    initComponent: function() {
        var me = this;
        this.items = [{
            xtype: 'bq_user_manager',
            itemId: 'settings_user_manager',
            title: 'Users',
            users: { user: false, admin: true, },
        }, {
            xtype: 'bq_groups_manager',
            itemId: 'settings_group_manager',
            title: 'Groups',
            users: { user: false, admin: true, },
        }, {
            xtype: 'bq_cache_manager',
            itemId: 'settings_cache_manager',
            title: 'Cache',
            users: { user: false, admin: true, },
        }, {
            xtype: 'bq_module_manager',
            title: 'Modules',
            itemId: 'settings_module_manager',
            users: { user: true, admin: true, },
        },{
            xtype: 'bq_module_developer',
            title: 'Module developer',
            itemId: 'settings_module_developer',
            users: { user: true, admin: true, },
        }, {
            xtype: 'bq_preference_manager',
            title: 'Preferences',
            itemId: 'setting_preference',
            users: { user: true, admin: true, },
            activeTab: 1,
        }, {
            xtype: 'bq_loggers_manager',
            itemId: 'loggers_manager',
            title: 'Loggers',
            users: { user: false, admin: true, },
        }, {
            xtype: 'bq_logs_manager',
            itemId: 'settings_log_viewer',
            title: 'Logs',
            users: { user: false, admin: true, },
        }, {
            xtype: 'bq_notifications_manager',
            itemId: 'notifications_manager',
            title: 'Notifications',
            users: { user: false, admin: true, },
        }];

        this.on('beforerender', this.setVisibility);
        this.callParent();
    },

    setVisibility : function() {
        var p = null,
            is_admin = BQApp.user.is_admin(),
            is_user = BQApp.user;
        for (var i=0; (p=this.items.items[i]); ++i) {
            if (p.users && p.users.user===true && is_user) {
                p.tab.setVisible(true);
            }
            if (p.users && p.users.admin===true && is_admin) {
                p.tab.setVisible(true);
            }
        }
    },

});

//--------------------------------------------------------------------------------
// Cache
//--------------------------------------------------------------------------------

Ext.define('BQ.admin.cache.Manager', {
    extend: 'Ext.container.Container',
    alias: 'widget.bq_cache_manager',

    componentCls: 'bq_cache_manager',

    initComponent: function() {
        this.items = [{
            xtype: 'container',
            html : '<h2>Cache manager</h2><p>Select to clear all the cache for all the users.</p>',
        }, {
            text: 'Clear cache',
            xtype: 'button',
            scale: 'large',
            scope: this,
            handler: this.clearCache,
        }];
        this.callParent();
    },

    clearCache: function() {
        Ext.Ajax.request({
            url: '/admin/cache',
            method: 'DELETE',
            headers: {
                'Content-Type': 'text/xml'
            },
            success: function(response) {
                var xml = response.responseXML;
                BQ.ui.notification('Cache cleared!');
            },
            failure: function(response) {
                BQ.ui.error('Cache failed to be cleared!')
            },
            scope: this,
        });
    },

});

