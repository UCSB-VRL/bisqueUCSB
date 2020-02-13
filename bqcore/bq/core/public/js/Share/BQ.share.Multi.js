/*******************************************************************************

  BQ.share.MultiDialog - window wrapper for the sharing of multiple resources

  Author: Dima Fedorov <dima@dimin.net>

  Parameters:
      resources - vector of the BQResource objects

------------------------------------------------------------------------------

  Version: 1

  History:
    2014-05-02 13:57:30 - first creation

*******************************************************************************/

//--------------------------------------------------------------------------------------
// BQ.share.Dialog
//--------------------------------------------------------------------------------------

Ext.define('BQ.share.MultiDialog', {
    extend : 'Ext.window.Window',
    alias: 'widget.bqsharemultidialog',
    border: 0,
    layout: {
        type: 'vbox',
        align: 'stretch'
    },
    modal : true,
    border : false,
    width : '70%',
    height : '85%',
    //minHeight: 350,
    //maxWidth: 900,
    buttonAlign: 'center',
    autoScroll: true,
    bodyCls: 'bq-share-dialog',

    constructor : function(config) {
        config = config || {};
        Ext.apply(this, {
            title: 'Add shares to '+config.resources.length+' resources',
            buttons: [{
                xtype: 'progressbar',
                itemId: 'progressbar',
                animate: false,
                flex: 2,
            }, {
                itemId: 'btn_add_shares',
                text: 'Add shares to '+config.resources.length+' resources',
                scale: 'large',
                cls: 'bq-btn-highlight',
                scope: this,
                handler: this.onAddShares,
            }, {
                text: 'Close',
                scale: 'large',
                scope: this,
                handler: this.onFinish,
            }],
            items  : [{
                xtype: 'bqsharepanel',
                itemId: 'sharepanel',
                border: 0,
                flex: 2,
                //resource: config.resource,
                permission: config.permission === 'private' ? 'published' : 'private',
                listeners : {
                    changePermission: this.onChangePermission,
                    scope: this,
                },
            }],
        }, config);

        this.callParent(arguments);
        this.show();
    },

    onFinish: function() {
        if (this.isStoreDirty()) {
            Ext.MessageBox.confirm('Shares modified',
                'Are you sure to discard the modified shares?',
                function(btn) {
                    if (btn=='yes')
                      this.close();
                },
                this
            );
            return;
        }
        this.close();
    },

    onSuccess: function(pos) {
        this.onUpdated();
        if (pos+1>=this.resources.length)
            return;

        var me = this;
        setTimeout( function() { me.doAction(pos+1); }, 1);
    },

    onError: function(pos) {
        var resource = this.resources[pos].resource;
        BQ.ui.error('Error while '+ this.progress_text+' for '+resource.name);
        this.onSuccess(pos);
    },

    onUpdated: function() {
        this.updating--;
        if (this.updating<=0) {
            if (this.cleanup)
                this.cleanup();

            this.action = undefined;
            this.cleanup = undefined;
            this.progress_text = '';

            this.queryById('progressbar').reset();
            this.queryById('progressbar').updateProgress( 0, 'Done', false );
            return;
        }
    },

    doAction: function(pos) {
        var total = this.resources.length;
        if (pos>=total)
            return;

        var resource = this.resources[pos].resource;
        var pr = pos/total;
        this.queryById('progressbar').updateProgress( pr, this.progress_text+resource.name+' ('+(pos+1)+'/'+total+ ')' );

        if (this.action)
            this.action(pos);
    },

    isStoreDirty: function() {
        var store = this.queryById('sharepanel').store;
        for (var i=0; i<store.getCount(); i++) {
            var rec = store.getAt(i);
            if (rec.dirty)
                return true;
        }
        return false;
    },

    // -------------------------------------------------------------------------
    // Auth stuff
    // -------------------------------------------------------------------------

    doAuthCleanup: function() {
        this.queryById('btn_add_shares').setLoading(false);
        this.queryById('btn_add_shares').setDisabled(false);
        this.records = undefined;
    },

    addAuth : function(auth, notify, pos) {
        // append the shares, if repeated the newly appended will overwrite the old permissions
        auth.children.push.apply(auth.children, this.records);
        var url = notify?undefined:Ext.urlAppend(auth.uri, 'notify=false');
        auth.save_(url,
            Ext.bind(this.onSuccess, this, [pos]),
            Ext.bind(this.onError, this, [pos])
        );
    },

    doAddShares: function(pos) {
        var notify = this.queryById('notify_check').getValue();
        var resource = this.resources[pos].resource;
        resource.getAuth(Ext.bind(this.addAuth, this, [notify, pos], 1));
    },

    onAddShares: function() {
        if (this.resources.length<=0) return;

        // change shares for all images
        this.records = [];
        var store = this.queryById('sharepanel').store;
        for (var i=0; i<store.getCount(); i++) {
            var rec = store.getAt(i);
            if (rec.dirty) {
                var user = rec.data.user;
                var email = rec.data.email;
                var action = rec.data.action;
                this.records.push(new BQAuth (user, email, action));
                rec.commit();
            }
        }
        if (this.records.length>0) {
            this.updating = this.resources.length;
            this.action = this.doAddShares;
            this.cleanup = this.doAuthCleanup;
            this.progress_text = 'adding shares to ';

            this.queryById('btn_add_shares').setDisabled(true);
            this.queryById('btn_add_shares').setLoading('');
            this.doAction(0);
        }
    },

    // -------------------------------------------------------------------------
    // Perm stuff
    // -------------------------------------------------------------------------

    doPermCleanup: function() {
        this.queryById('btn_permission').setLoading(false);
        this.queryById('btn_permission').setDisabled(false);
        this.permission = undefined;
    },

    doChangePerm: function(pos) {
        var resource = BQFactory.makeShortCopy(this.resources[pos].resource);
        this.resources[pos].resource.permission = this.permission; // update currently loaded resource
        resource.permission = this.permission;
        resource.save_(undefined,
                       Ext.bind(this.onSuccess, this, [pos]),
                       Ext.bind(this.onError, this, [pos]),
                       'post');
    },

    onChangePermission: function(perm, btn) {
        if (this.resources.length<=0) return;

        // change permission for all images
        this.updating = this.resources.length;
        this.action = this.doChangePerm;
        this.cleanup = this.doPermCleanup;
        this.progress_text = 'changing permission for ';

        this.permission = perm;
        this.queryById('btn_permission').setDisabled(true);
        this.queryById('btn_permission').setLoading('');
        this.doAction(0);
    },

});

//--------------------------------------------------------------------------------------
// BQ.button.ResourceVisibility
// button that shows and changes resource visibility
// Parameters: resource
//--------------------------------------------------------------------------------------

Ext.define('BQ.button.MultiPermissions', {
    extend: 'BQ.button.ResourcePermissions',
    alias: 'widget.bqmultipermissions',

    toggleVisibility: function() {
        this.fireEvent( 'changePermission', this.permission, this );
        this.permission = this.permission === 'private' ? 'published' : 'private';
        this.setVisibility();
    },
});

