/*******************************************************************************

  BQ.dataset.Panel  - 

  Author: Dima Fedorov

  Version: 1
  
  History: 
    2011-09-29 13:57:30 - first creation
    
*******************************************************************************/

Ext.define('BQ.dataset.Panel', {
    alias: 'widget.datasetpanel',    
    extend: 'Ext.panel.Panel',
    requires: ['BQ.dataset.operations'],

    service_url: '/dataset_service/',
    heading : 'Operations',
    status: 'Modify',

    layout: {
        type: 'vbox',
        align : 'stretch',
        pack  : 'start',
    },
    defaults: { border: 0, },     

    constructor: function(config) {
        this.addEvents({
            'done'      : true,
            'error'     : true,        
            'removed'   : true,      
            'changed'   : true,                              
        });
        this.callParent(arguments);
        return this;
    },

    initComponent : function() {
        this.operations = {};
        var op_items = [];
        for (i in BQ.dataset.operations) {
            var o = Ext.create(BQ.dataset.operations[i], {
                listeners: { 'changed': this.onChanged, scope: this },       
            });
            this.operations[i] = o;
            op_items.push(o);
        }
        this.operationChooser = Ext.create('Ext.panel.Panel', {
            flex: 1,
            layout: 'accordion',
            border: 0,
            defaults: { border: 0, }, 
            items: op_items,
        }); 
        
        // header toolbar's elements
        this.btn_modify = Ext.create('Ext.button.Button', {
            text: this.status, 
            disabled: true,
            //iconCls: 'upload', 
            scale: 'large', 
            handler: Ext.Function.bind( this.run, this ),
        });

        this.title = this.heading;
        this.items = [this.operationChooser, this.btn_modify];
        this.callParent();
        this.onChanged(op_items[0]);
    },
   
    setDataset: function(d) {
        this.dataset = d;
        this.setTitle(this.heading+' for "'+this.dataset.name+'"');
        if (this.selected_operation) 
           this.onChanged(this.selected_operation);          
    },     
   
    onChanged: function(o) {
        var disable = this.dataset&&o.validate()?false:true;
        this.selected_operation = o;
        this.status = o.getStatus();
        this.btn_modify.setText( this.status );
        if (!disable)
            BQ.ui.tip(this.btn_modify.getId(), this.status, { anchor:'top', color: 'green', });

        this.status += this.dataset ? ' for dataset "<b>'+this.dataset.name+'</b>"':'';
        //this.btn_modify.setTooltip( this.status );        
        this.btn_modify.setDisabled(disable);
    },    

    run: function(o) {
        if (this.selected_operation && this.dataset) {
            this.btn_modify.setDisabled(true);
            this.setLoading('Running...');

            //this.selected_operation.execute(this.dataset.uri, callback(this, 'onDone'), callback(this, 'onError'));            

            var d = this.selected_operation.getArguments();
            var operation = this.selected_operation.getName();
            d.duri = this.dataset.uri;
            var l = [];
            for (var i in d)
                l.push( i+'='+d[i] );
            var uri = this.service_url + operation + '?' + l.join('&');
            
            BQFactory.request ({uri : uri, 
                                cb : callback(this, 'onDone'),
                                errorcb: callback(this, 'onError'),
                                cache : false});           
        }
    },    

    getStatus: function() {
        return this.status;  
    },

    onDone: function(response) {
        this.btn_modify.setDisabled(false);
        this.setLoading(false);
        this.fireEvent( 'done', this );  
        if (this.selected_operation && this.selected_operation.finished_event)
            this.fireEvent( this.selected_operation.finished_event, this );  
    },    

    onError: function(response) {
        this.btn_modify.setDisabled(false);
        this.setLoading(false);        
        this.fireEvent( 'error', this ); 
    },  

});


