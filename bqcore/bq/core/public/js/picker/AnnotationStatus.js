/*******************************************************************************

  BQ.button.AnnotationStatus - changes the annotation status of a resource

  as defined in the API annotation status could be:
    started
    finished
    validated

  Author: Dima Fedorov <dima@dimin.net>

  Parameters:
      resource - the BQResource object for the resource of interest

------------------------------------------------------------------------------

  Version: 1

  History:
    2014-05-02 13:57:30 - first creation

*******************************************************************************/

//--------------------------------------------------------------------------------------
// BQ.button.AnnotationStatus
//--------------------------------------------------------------------------------------

Ext.define('BQ.button.AnnotationStatus', {
    extend: 'Ext.button.Button',
    alias: 'widget.bqannotationstatus',
    cls: 'bq-button-annostatus',

    //iconCls: 'bq-icon-annostatus',
    //minWidth: 120,

    status: undefined,
    text: 'Annotation status',

    initComponent : function() {
        this.menu = {
            xtype: 'menu',
            //cls: 'toolbar-menu',
            cls: 'bq-editor-menu',
            plain: true,
            items: [{
                xtype: 'menucheckitem',
                group: 'status',
                text: BQ.annotations.status.started,
                itemId: 'menu_status_'+BQ.annotations.status.started,
                handler: this.updateStatus,
                scope: this,
            }, {
                xtype: 'menucheckitem',
                group: 'status',
                text: BQ.annotations.status.finished,
                itemId: 'menu_status_'+BQ.annotations.status.finished,
                handler: this.updateStatus,
                scope: this,
            }, {
                xtype: 'menucheckitem',
                group: 'status',
                text: BQ.annotations.status.validated,
                itemId: 'menu_status_'+BQ.annotations.status.validated,
                handler: this.updateStatus,
                scope: this,
            }],
        };
        this.callParent();

        if (this.resource && this.resource.tags) {
            this.status = this.resource.find_tags(BQ.annotations.name);
            if (this.status && this.status instanceof Array && this.status.length>0) {
                this.status = this.status[0];
            }
        }
        if (!this.status) {
            // try to fetch the status tag if not found just to guarantee
            BQFactory.load(this.resource.uri + '?view='+BQ.annotations.name, callback(this, this.onTag));
        } else {
            this.setStatus();
        }
    },

    /*afterRender : function() {
        this.callParent();
    },*/

    onTag: function(r) {
        if (r && r.tags) {
            this.status = r.find_tags(BQ.annotations.name);
        } else {
            this.status = null;
        }
        this.setStatus();
    },

    setStatus: function() {
        if (!this.status) return;
        var btn = this.menu.queryById('menu_status_'+this.status.value);
        if (btn)
            btn.setChecked(true);
    },

    onSuccess: function(r) {
        this.setLoading(false);
        if (this.resource) {
            var t = this.resource.find_tags(BQ.annotations.name);
            if (!t) {
                this.resource.addtag(this.status);
            }
        }
        this.fireEvent('changed', this.status.value, this);
    },

    onError: function() {
        this.setLoading(false);
        BQ.ui.warning('Could not save annotation status');
    },

    updateStatus: function(btn) {
        var v = btn.text;
        this.setLoading('Updating annotation status');
        if (this.status && this.status.uri) {
            this.status.value = v;

            // dima: this code saves the whole image instead of just the tag of interest
            // this.status.save_(
            //     this.status.uri,
            //     callback(this, this.onSuccess),
            //     callback(this, this.onError),
            //     'post'
            // );

            var t = new BQTag(undefined, BQ.annotations.name, v, BQ.annotations.type);
            t.uri = this.status.uri;
            t.save_(t.uri,
                    callback(this, this.onSuccess),
                    callback(this, this.onError),
                    'post');
        } else {
            this.status = new BQTag(undefined, BQ.annotations.name, v, BQ.annotations.type);
            this.status.save_(this.resource.uri,
                           callback(this, this.onSuccess),
                           callback(this, this.onError),
                           'post');
        }
        this.setStatus();
    },

});


