/*******************************************************************************

  BQ.dataset.operations  - 

  Author: Dima Fedorov

  Version: 1
  
  History: 
    2011-12-15 15:41:19 - first creation
    
*******************************************************************************/

/*******************************************************************************
  Available operations
*******************************************************************************/

Ext.namespace('BQ.dataset');

BQ.dataset.operations = { 'permission'  :   'BQ.dataset.Permissions', 
                          'delete'      :   'BQ.dataset.Delete',
                          'share'       :   'BQ.dataset.Share'   
                          //'tagedit'    : 'BQ.dataset.Edittags',
                        };

/*******************************************************************************
  Baseclass for dataset operations
  
*******************************************************************************/

Ext.define('BQ.dataset.Operation', {
    alias: 'widget.datasetop',    
    extend: 'Ext.panel.Panel',
    
    // required !!!!
    title: 'Operation name',
    name: 'idem',
    finished_event: undefined, // special event to fire on finished
        
    // configs    
    cls: 'selector',
    border: 0,
    layout: 'auto',
    
    defaults: { border: 0, xtype: 'container', },
    
    statics : { service_url : '/dataset_service/' },

    constructor: function(config) {
        this.addEvents({
            'changed'   : true,
        });
        this.callParent(arguments);
        return this;
    },

    initComponent : function() {
        this.listeners = this.listeners || {};
        //this.listeners.scope = this;
        var me = this;
        this.listeners.expand = function(f) { 
            me.fireEvent( 'changed', me ); 
        };
        this.callParent();
    },

    getName: function() {
        return this.name;
    },

    getStatus: function() {
        return 'Setting dataset to operation';
    },
    
    getArguments: function() {
        return {};
    },    
    
    validate: function() {
        return true;
    },
    
    execute : function(datasetURI, onDone, onError)
    {
        var args = this.getArguments();
        args.duri = datasetURI;

        var uri = Ext.urlAppend(BQ.dataset.Operation.service_url + this.getName(), Ext.Object.toQueryString(args, true));
                    
        BQFactory.request ({uri     :   uri, 
                            cb      :   onDone,
                            errorcb :   onError,
                            cache   :   false});
    }
});




/*******************************************************************************
  BQ.dataset.Permissions
*******************************************************************************/

Ext.define('BQ.dataset.Permissions', {
    alias: 'widget.dataset-permission',    
    extend: 'BQ.dataset.Operation',
    requires: ['Ext.form.Panel'],
    
    title: 'Change access permissions to elements',
    name: 'permission',

    initComponent : function() {
      
        this.form = Ext.create('Ext.form.Panel', {
            cls: 'datasets-form',
            border: false,
            defaultType: 'radiofield',
            items: [{
                cls: 'radio-published',
                name: 'permission',
                value: 'published',
                inputValue: 'published',
                boxLabel: 'Set permission of all elements to "<b>published</b>"',
                listeners: { 'change': function(f) { this.fireEvent( 'changed', this ); }, scope: this },                
            },{
                cls: 'radio-private',                
                name: 'permission',
                value: 'private',
                inputValue: 'private',                
                boxLabel: 'Set permission of all elements to "<b>private</b>"',
                listeners: { 'change': function(f) { this.fireEvent( 'changed', this ); }, scope: this },
            }],
            
        });
      
        this.items = [this.form];       
        this.callParent();
    },

    getStatus: function() {
        var s = this.title;
        var f = this.form.getForm().getFields();
        f.each( function (item) {
            if (item.getValue())
                s = item.boxLabel;
        } );
        return s;
    },
    
    getArguments: function() {
        return this.form.getValues();
    },   

    validate: function() {
        return (this.title != this.getStatus());
    },

});

/*******************************************************************************
  BQ.dataset.Delete
*******************************************************************************/

Ext.define('BQ.dataset.Delete', {
    alias: 'widget.dataset-delete',    
    extend: 'BQ.dataset.Operation',
    requires: ['Ext.form.Panel'],
    
    title: 'Delete elements',
    name: 'delete',  
    finished_event: 'removed',  

    initComponent : function() {
      
        this.form = Ext.create('Ext.form.Panel', {
            cls: 'datasets-form',
            border: false,
            defaultType: 'radiofield',
            items: [{
                name: 'delete',
                value: true,
                checked: true,
                boxLabel: '<b>Delete</b> all elements',
                listeners: { 'change': function(f) { this.fireEvent( 'changed', this ); }, scope: this },                
            }],
            
        });
      
        this.items = [this.form];       
        this.callParent();
    },

    getStatus: function() {
        var s = this.title;
        s = 'Delete nothing';
        var f = this.form.getForm().getFields();
        f.each( function (item) {
            if (item.getValue())
                s = item.boxLabel;
        } );
        return s;
    },

});



/*******************************************************************************
  BQ.dataset.Share
*******************************************************************************/

Ext.define('BQ.dataset.Share',
{
    alias       :   'widget.dataset-share',    
    extend      :   'BQ.dataset.Operation',
    requires    :   ['Ext.form.Panel'],
    
    title           :   'Share all elements',
    name            :   'share',  

    initComponent   :   function()
    {
        this.form = Ext.create('Ext.form.Panel',
        {
            cls         :   'datasets-form',
            border      :   false,
            defaultType :   'radiofield',
            items       :   [{
                                name        :   'share',
                                value       :   true,
                                checked     :   true,
                                boxLabel    :   'Apply dataset\'s <b>share</b> authorization to all elements.',
                                listeners   :   {
                                                    'change'    :   function(f)
                                                    {
                                                        this.fireEvent('changed', this);
                                                    },
                                                    scope       :   this
                                                },                
                            }],
            
        });
      
        this.items = [this.form];
        this.callParent();
    },

    getStatus: function()
    {
        return 'Apply dataset\'s <b>share</b> authorization to all elements.';
    },
});



/*******************************************************************************
  BQ.dataset.Edittags
*******************************************************************************/

Ext.define('BQ.dataset.Edittags', {
    alias: 'widget.datasetpermission',    
    extend: 'BQ.dataset.Operation',
    //requires: ['Ext.button.Button', 'Bisque.ResourceBrowser.Dialog'],
    
    title: 'Edit tags',
    name: 'tagedit',      
    finished_event: 'changed',      

    initComponent : function() {
      
        //this.items = btns;       
        this.callParent();
    },


});
