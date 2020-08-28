BQ.selectors.resources.query = 'BQ.selectors.Botanicam.Query';
BQ.selectors.parameters.tagselector = 'BQ.selectors.Botanicam.TagSelector';


// provide our renderer
Ext.define('BQ.selectors.Botanicam.Query', {
    alias: 'widget.selectorquery',
    extend: 'BQ.selectors.Selector',
    requires: ['Ext.button.Button', 'Bisque.ResourceBrowser.Dialog','Ext.grid.Panel','Ext.data.Store'],
    
    //layout: 'auto',
    height: 100,
    
    layout: {
        type: 'vbox',
        defaultMargins:{top:0, right:0, bottom:0, left:20},
        pack  : 'start',
    },
    
    initComponent : function() {
        var resource = this.resource;
        var template = resource.template || {};
        
        
        Ext.regModel('QUERY', {
            fields: [
                {type: 'string', name: 'Tag'},
                {type: 'string', name: 'Name'},
                    ]
            });
        
        var querytags = [];
        
        // The data store holding the states
        var store = Ext.create('Ext.data.Store', {
            model: 'QUERY',
            data: querytags
        });
            
        //drawing all the items 
        this.items = [];
        this.items.push( {xtype: 'label', text:template.label+':' } );
        this.items.push( {xtype: 'tbtext', text:'<br/>'} );
        this.items.push( Ext.create('Ext.button.Button', {
            id:'query',
            iconAlign: 'right',
            width: 150,
            height: 50,
            text: 'Select a Query',
            //iconCls: 'upload',
            //scale: 'large',
            //cls: 'x-btn-default-large',
            tooltip: template.description,
            handler: Ext.Function.bind( this.selectMex, this ),
        }));
        this.items.push( {xtype: 'tbtext', text:'<br/>'} );
        output = Ext.create('Ext.grid.Panel', {
            store: store,
            hidden:true,
            autoScroll: true,
            width: 360,
            height: 125,
            stateful: true,
            title: 'Tags Query',
            stateId: 'stateGrid',
            enableColumnHide:false,
            forceFit: true,
            columns: [
                {
                    text     : 'Tags',
                    width    : 175,
                    sortable : true,
                    dataIndex: 'Tag'
                },
                {
                    text     : 'Names',
                    width    : 175,
                    sortable : true,
                    dataIndex: 'Name'
                },
            ],
            viewConfig: {
                stripeRows: true,
                //enableTextSelection: true
            }                   
        });
                
        this.output=output;
        this.items.push( this.output )  
        this.callParent();
    },

    selectMex: function() {
        var resource = this.resource;
        var template = resource.template || {};
        var resourceDialog = Ext.create('Bisque.QueryBrowser.Dialog', {
            'height'  : '85%',
            'width'   :  '85%',
            dataset   : '/data_service/image',
            query_resource_type: 'image',
            listeners : {
                'Select' : this.onselected,
                scope: this
            },
        });
    },

    onerror: function(message) {
        BQ.ui.error('Error fetching resource:<br>' + message);
    },

    onselected: function(browser, query) {
    
        this.resource.value = query;
        
        //fires event to place tags in combo box
        this.fireEvent('changed', query);
        var querytags = [];
        //parse query to place in the display box
        d_query=query.replace(/"/g, ""); //removing '"'
        d_query=d_query.split(' AND ');
        for(i=0;i<d_query.length;i++){
            s_query=d_query[i].split(':');
            querytags.push([s_query[0],s_query[1]]);
        }
        
        //resets value after picking new query
        this.output.store.removeAll(); //removes all data from the combo box
        this.output.store.add(querytags); //writes new data to the combo box
        
        
        //set display box to visiable
        this.setHeight(250,true); //resets size
        
        if (this.output.isHidden()){
            this.output.setVisible(true)
        };
        // validate the query selection
        if (!this.validate()) return;
    },

    isValid: function() {
        if (!this.resource.value) {
            BQ.ui.tip(this.getId(), 'You need to select a query to train!', {anchor:'left',});
            return false;
        }
        return true;
    },
    //reloads mex
    select: function(resource) {
        this.onselected([],resource.value);
    },
    
});

Ext.define('BQ.selectors.Botanicam.TagSelector', {
    alias: 'widget.selectortagselector',
    extend: 'BQ.selectors.Selector',

    require: (['Ext.form.Panel','Ext.form.field.ComboBox','Ext.data.Store']),
    
    height: 70,
    layout: {
        type: 'vbox',
        defaultMargins:{top:10, right:0, bottom:0, left:20},
        pack  : 'start',
    
    },

    initComponent : function() {
        var resource = this.resource;
        var template = resource.template || {};
    
        var reference = this.module.inputs_index[template.reference];
        
        Ext.regModel('State', {
                fields: [
                   {type: 'string', name: 'TAGS'},
                        ]
            });
        
        // ComboBox with multiple selection enabled
        var states = [];
        
        // The data store holding the states
        var store = Ext.create('Ext.data.Store', {
            model: 'State',
            data: states
            });
                  
        var multiSelectCombo = Ext.create('Ext.form.field.ComboBox', {
        
            id:'combo1',
            fieldLabel: 'Select atleast one tag',
            multiSelect: true,
            displayField: 'TAGS',
            width: 600,
            labelWidth: 130,
            store: store,
            editable : false, 
            queryMode: 'local',
            
        });
        
        this.multiSelectCombo=multiSelectCombo;
        multiSelectCombo.on('select', this.onselected, this); //validation
        this.items = [];
        this.items.push(multiSelectCombo);
        
        if (reference && reference.renderer) {
            this.reference = reference.renderer;
            //run parcer and reset the variables
            this.reference.on( 'changed', this.parse , this );
        }
        
        this.callParent();
    },
    
    parse : function(ref) {
            //fetches tags
            this.tags=ref;
            var modtags=ref.replace(/"/g, "%22");
            var modtags=modtags.replace(/ /g, "%20");
            this.current_mex_uri='/data_service/image/?tag_names=1&tag_query='+ modtags;
            this.setLoading('Fetching memebrs...');
            BQFactory.request({ 
                uri:     this.current_mex_uri, 
                cb:      callback(this, 'onfetched'),
                errorcb: callback(this, 'onerror'),
            });
            
            this.setLoading(false);
    },
    
    onfetched: function(R) {
        //writes tags to the combo box
        this.Tags = R;
        var x =this.Tags.tags;
        var states = [];
        for ( i=0; i<x.length;i++){
            var y=x[i].name;
            states.push({"TAGS":y});
            }
        this.multiSelectCombo.setValue(); //resets value after picking new query
        this.multiSelectCombo.getStore('combo1').removeAll(); //removes all data from the combo box
        this.multiSelectCombo.getStore('combo1').add(states); //writes new data to the combo box
        if(this.newresource){
            this.multiSelectCombo.setValue(this.newresource);
            delete this.newresource;
        }
    },
    
    onerror: function(message) {
        BQ.ui.error('Error fethnig resource:<br>' + message); 
    },   
    
    
    onselected : function() {
                this.resource.value = this.multiSelectCombo.getValue();
                if (!this.validate()) return;
    },

    isValid: function() {
        if (!this.resource.value) {
            BQ.ui.tip(this.getId(), 'You need to select a tags to train!', {anchor:'left',});
            return false;
        }
        return true;
    },
    
    select: function(resource) { 
        if(!this.multiSelectCombo.store.data.item){
                this.newresource=resource.value ; //creates new resource to store till after select query is rendered
                this.onselected();
                }
    }, 
});

