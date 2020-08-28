

Ext.define('BQ.preference.Tagger', {
    extend : 'Bisque.ResourceTagger',
    alias: 'widget.bq_preferences_tagger',
    level: 'user', //options system, user, resource, level
    full_load_on_creation: true,
    borders: false,
    //autoSave : true,

    constructor : function(config) {
        config = config || {};
        //config.viewMode = 'PreferenceTagger';
        config.autoSave = true;
        config.tree = config.tree || {
            btnAdd : false,
            btnDelete : false,
        },
        this.callParent([config]);
    },

    setResource : function(resource_uniq) {
        var preferenceUrl = {
            'system'  : '/preference',
            'user'    : '/preference/user',
            'resource': '/preference/user/'+resource_uniq,
        };

        if (!(this.level in preferenceUrl)) {
            BQ.ui.error('Not a valid preference level');
            return
        }

        // assume it is a resource URI otherwise
        if (this.level=='resource' && !resource_uniq) {
            BQ.ui.error('set resource without resource uniq')
            return
        } else if (this.level=='resource' && resource_uniq) {
            this.resource_uniq = resource_uniq
        }
        this.resource = preferenceUrl[this.level]
        BQFactory.request({
            uri: this.resource,
            cb: Ext.bind(this.loadResourceInfo, this),
            errorcb: function(error) {
                BQ.ui.error('Error fetching resource:<br>'+error.message_short, 4000);
            },
            uri_params: {view:'deep'},
        });

        //this.tree.expandAll(); //show all preferences
    },

    reloadResource: function() {
        this.setResource(this.resource_uniq)
    },

    /*
    * finishEdit
    *
    * custom for preference tagger
    * may not work under curtain circumstance
    */
    finishEdit: function (_editor, me) {
        if (me.record.raw instanceof BQObject) {
            if (this.autoSave) { //name and value are the only things that can be changed
                me.record.raw.value = me.record.data.value;
                me.record.raw.name = me.record.data.name;
                me.record.raw.type = me.record.data.type;
                this.saveTags(me.record.raw);
                me.record.data.qtip = this.getTooltip('', me.record);
                me.record.commit();
            }
            return;
        }

        this.editing = true;
        var newTag = new BQTag();

        newTag = Ext.apply(newTag,
        {
            name: me.record.data.name,
            value: me.record.data.value,
        });

        var parent = (me.record.parentNode.isRoot()) ? this.resource : me.record.parentNode.raw;
        parent.addtag(newTag);

        if (this.isValidURL(newTag.value)) {
            newTag.type = 'link';
            me.record.data.type = 'link';
        }

        if (this.autoSave)
            this.saveTags(parent, undefined, newTag);

        me.record.raw = newTag;
        me.record.loaded = true;
        me.record.data.qtip = this.getTooltip('', me.record);
        me.record.commit();

        //me.record.parentNode.data.iconCls = 'icon-folder';
        me.view.refresh();

        this.editing = false;
    },

    saveTags : function(tag, silent, child) {
        var me = this;
        if (silent === undefined)
            silent = this.silent !== undefined ? this.silent : false;

        if (tag && tag.resource_type=='tag' && this.store.applyModifications() && this.level) {
            var level = (this.level == 'resource') ? this.resource_uniq : this.level,
                path = [],
                value = tag['value'];
            while(tag.resource_type!='preference'&&tag.parent) {
                path.unshift(tag['name']);
                var tag = tag.parent
            }
            var path = path.join('/');
            BQ.Preferences.set(level, path, value);
        } else {
            if (!silent) BQ.ui.notification('No records modified, save canceled!');
        }
    },

    //admin only on system
    addTags: function () {
        BQ.ui.notification('Tags cannot be added through this tagger');
        /*
        var currentItem = this.tree.getSelectionModel().getSelection();
        var editor = this.rowEditor || this.tree.plugins[1];

        if (currentItem.length)// None selected -> add tag to parent document
            currentItem = currentItem[0];
        else
            currentItem = this.tree.getRootNode();

        // Adding new tag to tree
        var child = { name: this.defaultTagName || '', value: this.defaultTagValue || '' };
        child[this.rootProperty] = [];

        var newNode = currentItem.appendChild(child);
        this.newNode = newNode;
        currentItem.expand();
        editor.startEdit(newNode, 0);
        */
    },

    //admin needs to be implimented in a special way
    deleteTags : function() {
        BQ.ui.notification('Tags cannot be deleted through this tagger');
        /*
        var selectedItems = this.tree.getSelectionModel().getSelection(), parent;
        var root = BQ.Preferences.user.tag;

        BQ.Preferences.user.object.tags[0].delete_();

        var cb = Ext.bind(function() {
            this.tree.setLoading(false);
        }, this);

        if (selectedItems.length) {
            this.tree.setLoading(true);

            for (var i = 0; i < selectedItems.length; i++) {
                var tag = root.findTags({
                    attr : 'name',
                    value : selectedItems[i].get('name'),
                    deep : true
                });

                if (!Ext.isEmpty(tag))
                    for (var j = 0; j < tag.length; j++)
                        if (tag[j].value == selectedItems[i].get('value')) {
                            parent = (selectedItems[i].parentNode.isRoot()) ? root : tag[j].parent;
                            parent.deleteTag(tag[j], cb, cb);

                            if (selectedItems[i].parentNode.childNodes.length <= 1)
                                selectedItems[i].parentNode.data.iconCls = 'icon-tag';

                            selectedItems[i].parentNode.removeChild(selectedItems[i], true);

                            break;
                        }
            }

            this.tree.setLoading(false);
            BQ.ui.notification(selectedItems.length + ' record(s) deleted!');
            this.tree.getSelectionModel().deselectAll();
        }
        */
    },
});


Ext.define('BQ.preference.PreferencePage', {
    extend : 'Ext.tab.Panel',
    alias: 'widget.bq_preference_manager',

    layout : 'fit',
    border: false,

    initComponent: function(config) {
        var config = config || {};
        var me = this;

        var resource_uniq = undefined;
        var systemPref = undefined;
        var userPref = undefined;
        var resourcePref = undefined;
        //this.viewMgr.state.btnAdd && this.viewMgr.state.btnDelete
        if (BQApp.user) {
            var userPref = Ext.create('BQ.preference.Tagger', {
                level: 'user',
            });

            if (BQApp.user.is_admin()) { //dumb I know
                var systemPref = Ext.create('BQ.preference.Tagger', {
                    level: 'system',
                });
            }
        }

        if (BQApp.resource){ //initialize resource preference
            var resource_uniq = BQApp.resource.resource_uniq
            var resourcePref = Ext.create('BQ.preference.Tagger', {
                level: 'resource',
                resource: resource_uniq,
            });
        }

        var items = [{ //admin can view
            title: 'System',
            layout: 'fit',
            border: false,
            hidden: systemPref?false:true,
            items: systemPref?systemPref:[],
        }, { //if logged in
            title: 'User',
            layout: 'fit',
            border: false,
            hidden: userPref?false:true,
            items: userPref?userPref:[],
        }, { //if viewing a resource
            title: 'Resource',
            layout: 'fit',
            border: false,
            hidden: resourcePref?false:true,
            items: resourcePref?resourcePref:[],
        }, {
            title: 'Manager',
            xtype: 'bq_preferences_manager',
            border: false,
            hidden: !BQApp.user.is_admin(),
        }];
        Ext.apply(me, {
            items: items,
        });
        this.callParent([config]);
    }
});


//--------------------------------------------------------------------------------
// Preferences Manager
//--------------------------------------------------------------------------------

Ext.define('BQ.preference.Manager', {
    extend: 'Ext.container.Container',
    alias: 'widget.bq_preferences_manager',

    componentCls: 'bq_preferences_manager',

    /*layout: {
        type: 'vbox',
        align: 'left',
    },*/

    initComponent: function() {
        this.items = [{
            xtype: 'container',
            html : '<h2>Preferences manager</h2>',
        }, {
            text: 'Download system preferences',
            xtype: 'button',
            iconCls: 'icon-download',
            scale: 'large',
            scope: this,
            handler: this.download_system_prefs,
        }, {
            xtype: 'filemultifield',
            itemId: 'selector_files',
            buttonOnly: true,
            multiple: false,
            handler: this.on_upload,
            scope: this,
            buttonConfig: {
                scale: 'large',
                iconCls: 'icon-upload',
                text: 'Upload system preferences',
                //tooltip: 'Upload system preferences',
            },
            listeners: {
                change: this.on_upload,
                scope: this,
            },
        }, {
            text: 'Reset preferences to default',
            xtype: 'button',
            iconCls: 'icon-reset',
            scale: 'large',
            scope: this,
            handler: this.reset_system_prefs,
        }];
        this.callParent();
    },

    download_system_prefs: function() {
        window.open('/preference?view=deep');
    },

    on_upload: function(field, value, opts) {
        var me = this,
            files = field.fileInputEl.dom.files,
            reader = new FileReader();

        reader.onload = function(e) {
            var text = e.target.result;
            me.upload_system_prefs(text);
        };
        reader.onerror = function(e) {
            BQ.ui.error('Failed to read the file...');
        };

        reader.readAsText(files[0]);
    },

    upload_system_prefs: function(text) {
        this.setLoading('Uploading...');
        Ext.Ajax.request({
            url: Ext.String.format('/preference'),
            method: 'PUT',
            //xmlData:
            rawData: text,
            headers: {
                'Content-Type': 'text/xml',
            },
            callback: function(opts, succsess, response) {
                this.setLoading(false);
                if (response.status>=400)
                    BQ.ui.error(response.responseText);
                else
                    BQ.ui.notification('Successfully uploaded the preferences document');
            },
            scope: this,
            disableCaching: false,
        });
    },

    reset_system_prefs: function(text) {
        this.setLoading('Uploading...');
        Ext.Ajax.request({
            url: Ext.String.format('/preference/reset'),
            method: 'GET',
            callback: function(opts, succsess, response) {
                this.setLoading(false);
                if (response.status>=400)
                    BQ.ui.error(response.responseText);
                else
                    BQ.ui.notification('Successfully reset the preferences document');
            },
            scope: this,
            disableCaching: false,
        });
    },

});

