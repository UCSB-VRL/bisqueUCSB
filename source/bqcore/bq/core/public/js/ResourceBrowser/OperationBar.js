Ext.define('Bisque.ResourceBrowser.OperationBar', {
    extend : 'Ext.container.Container',
    floating : true,

    constructor: function(config) {
        this.addEvents({
            'removed' : true,
        });
        this.callParent(arguments);
        return this;
    },

    initComponent : function() {
        this.items = this.items || [{
            xtype: 'button',
            icon : BQ.Server.url('/core/js/ResourceBrowser/Images/down.png'),
            tooltip : 'Available operations for this resource.',
            handler : this.menuHandler,
            scope : this
        }, {
            xtype: 'button',
            itemId : 'btn_delete',
            icon : BQ.Server.url('/core/js/ResourceBrowser/Images/close.gif'),
            tooltip : 'Delete this resource',
            handler : this.deleteResource,
            scope : this,
            hidden: !BQApp.user,
        }];
        if (this.updateItems)
            this.updateItems(this.items, this);
        this.callParent();
    },

    deleteResource : function(me, e) {
        e.stopPropagation();
        Ext.MessageBox.confirm( 'Delete resource?', 'Just confirming that you are deleting this resource?', function(btn) {
            if (btn != 'yes') return;
            var list = Ext.Object.getSize(this.browser.resourceQueue.selectedRes);
            if (list > 1) {
                this.fireEvent( 'removed', this.browser.resourceQueue.selectedRes );

                // Client-side temporary dataset
                var tempDS = new BQDataset(), members = [];

                for (var res in this.browser.resourceQueue.selectedRes) {
                    this.browser.resourceQueue.selectedRes[res].setLoading({
                        msg : 'Deleting...'
                    });
                    members.push(this.browser.resourceQueue.selectedRes[res]);
                }

                tempDS.tmp_setMembers(members);

                tempDS.tmp_deleteMembers(Ext.bind(result, this));

                function result(summary) {
                    BQ.ui.notification(summary.success + ' resources deleted. ' + summary.failure + ' resources failed.');
                    this.browser.msgBus.fireEvent('Browser_ReloadData', {});
                }
            } else {
                var selected = {};
                selected[this.resourceCt.resource.uri] = this.resourceCt.resource;
                this.fireEvent( 'removed', selected );

                me.operation = Ext.pass(this.resourceCt.resource.delete_, [Ext.bind(this.success, this), Ext.Function.pass(this.failure, ['Delete operation failed!'])], this.resourceCt.resource);
                this.resourceCt.setLoading({
                    msg : 'Deleting...'
                });
                this.resourceCt.testAuth1(me);
            }
        }, this );
    },

    removeResource : function(me, e) {
        e.stopPropagation();
        if (Ext.Object.getSize(this.browser.resourceQueue.selectedRes) > 1) {
            this.fireEvent( 'removed', this.browser.resourceQueue.selectedRes, true );
        } else {
            var selected = {};
            selected[this.resourceCt.resource.uri] = this.resourceCt.resource;
            this.fireEvent( 'removed', selected, true );
        }
    },

    menuHandler : function(me, e) {
        e.stopPropagation();
        this.menu = this.createMenu().showBy(this, "tr-br");
    },

    createMenu : function() {
        // Look for available resource operations and change menu accordingly
        var list = Ext.Object.getSize(this.browser.resourceQueue.selectedRes);

        var items = [{
            text : 'Download',
            iconCls : 'icon-download-small',
            handler : this.btnMenu,
            scope : this
        }, {
            text : 'Share',
            iconCls : 'icon-group',
            handler : this.btnMenu,
            scope : this,
            hidden: !BQApp.user,
        }];

        // Handle resource permission
        if (list > 1) {
            items.push({
                text : 'Set all published',
                iconCls : 'icon-eye',
                handler : this.btnMenu,
                scope : this,
                hidden: !BQApp.user,
            }, {
                text : 'Set all private',
                iconCls : 'icon-eye-close',
                handler : this.btnMenu,
                scope : this,
                hidden: !BQApp.user,
            });
        } else if (this.resourceCt.resource.permission == 'published')
            items.push({
                text : 'Published',
                iconCls : 'icon-eye',
                handler : this.btnMenu,
                scope : this,
                hidden: !BQApp.user,
            });
        else
            items.push({
                text : 'Private',
                iconCls : 'icon-eye-close',
                handler : this.btnMenu,
                scope : this,
                hidden: !BQApp.user,
            });

        items.push('-', {
            text : 'Add to dataset',
            iconCls : 'icon-add',
            handler : this.btnMenu,
            scope : this,
            hidden: !BQApp.user,
        });

        return Ext.create('Ext.menu.Menu', {
            items : items
        });
    },

    btnMenu : function(btn) {
        var list = Ext.Object.getSize(this.browser.resourceQueue.selectedRes);
        var tempDS = new BQDataset(), members = [];

        if (list > 1) {
            for (var res in this.browser.resourceQueue.selectedRes)
            members.push(this.browser.resourceQueue.selectedRes[res]);

            tempDS.tmp_setMembers(members);
        }

        switch (btn.text) {
            case 'Download':
                (list > 1) ? tempDS.tmp_downloadMembers() : this.resourceCt.downloadOriginal();
                break;
            case 'Share':
                (list > 1) ? tempDS.tmp_shareMembers() : this.resourceCt.shareResource();
                break;
            case 'Private':
                this.resourceCt.changePrivacy('published', Ext.bind(this.success, this));
                break;
            case 'Published':
                this.resourceCt.changePrivacy('private', Ext.bind(this.success, this));
                break;
            case 'Set all published':
                tempDS.tmp_changePermission('published', Ext.bind(this.success, this));
                break;
            case 'Set all private':
                tempDS.tmp_changePermission('private', Ext.bind(this.success, this));
                break;
            case 'Add to dataset': {
                function addToDataset(btn, name) {
                    if (btn == 'ok') {
                        var newDS = new BQDataset(), members = [];
                        newDS.name = name;

                        for (var res in this.browser.resourceQueue.selectedRes)
                            members.push(new BQValue('object', res));

                        newDS.setMembers(members);

                        function openDS(dataset) {
                            window.location = BQ.Server.url('/client_service/view?resource=' + dataset.uri);
                        }


                        newDS.save_(undefined, openDS, this.failure);
                    }
                }


                Ext.MessageBox.prompt('Enter dataset name', 'New name:', addToDataset, this, false, 'NewDataset');
                break;
            }
        }
    },

    success : function(resource, msg) {
        //BQ.ui.notification(msg || 'Operation successful.');
        this.browser.msgBus.fireEvent('Browser_ReloadData', {});
    },

    failure : function(msg) {
        BQ.ui.error(msg || 'Operation failed!');
    },
});
