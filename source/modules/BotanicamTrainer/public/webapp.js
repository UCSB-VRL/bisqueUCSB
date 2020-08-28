//BQ.selectors.resources.resource_set = 'BQ.selectors.Botanicam.ResourceSet';
BQ.selectors.parameters.tag_selector = 'BQ.selectors.Botanicam.TagSelector';
BQ.renderers.resources.model_viewer = 'BQ.renderers.Botanicam.ModelViewer';

/*
 *  The tag selector for Botanicam Trainer Module
 * 
 *  Warning: Takes in only dataset and query resources
 *  
 * Example in XMl
 * 
 *  <tag name="tag_names" type="tag_selector">     
 *      <template>
 *          <tag name="label" value="Enter tags to be classified" />
 *          <tag name="reference" value="resource_url"/>
 *      </template>  
 *  </tag>
 * 
 * tag_name - variable for the resource returned
 * tag_selector - the parameter to define the tag selector template
 * 
 *  parameters
 *      label - The text displayed next to the combo box
 *      reference - choose the variable of the resource selected or the resource one 
 * wants to reference (resource must be a query or dataset)
 *      
 */
Ext.define('BQ.selectors.Botanicam.TagSelector', {
    alias: 'widget.selectortagselector',
    extend: 'BQ.selectors.Selector',

    require: (['Ext.form.field.ComboBox','Ext.data.Store']),
    
    height: 30,
    width: '100%',
    anchor: '0 0',
    layout: 'hbox',

    initComponent : function() {
      
        var resource = this.resource;
        var template = resource.template || {};
    
        var reference = this.module.inputs_index[template.reference];
        
        Ext.regModel('State', {
                fields: [{type: 'string', name: 'TagValues'}]
            });
        
        // ComboBox with multiple selection enabled
        var states = [];
        
        // The data store holding the states
        var store = Ext.create('Ext.data.Store', {
            model: 'State',
            data: states
            });
                  
        this.multiSelectCombo = Ext.create('Ext.form.field.ComboBox', {
            name: resource.name,
            labelWidth: 200,
            //autoWidth: true,
            labelAlign: 'right',
            fieldLabel: template.label?template.label:'',
            multiSelect: true,
            displayField: 'TagValues',
            width: '100%',
            store: store,
            editable : false,
            queryMode: 'local',
            listeners: {
                scope: this,
                change: function() {
                    this.onselected()
                }
            },
            
        });
        this.items = [];
        this.items.push(this.multiSelectCombo);
        
        if (reference && reference.renderer) {
            this.reference = reference.renderer;
            //run parcer and reset the variables
            this.reference.on( 'changed', this.fetchTagList , this );
        }
        
        this.callParent();
    },
    
    fetchTagList : function(me) {
            //fetches tags

            if (me['resource'].type=='resource'){
                this.tag_url=me['resource'].value+'&tag_names=1';
            }
            else if (me['resource'].type=='dataset') {
                this.tag_url=me['resource'].value+'/value?tag_names=1';
            } 
            else {
                this.onerror(me['resource'].value)
            }
            this.setLoading('Fetching memebrs...');
            BQFactory.request({ 
                uri:     this.tag_url,
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
            states.push({"TagValues":y});
            }
        this.multiSelectCombo.setValue(); //resets value after picking new query
        this.multiSelectCombo.store.removeAll(); //removes all data from the combo box
        this.multiSelectCombo.store.add(states); //writes new data to the combo box
        if(this.newresource){
            this.multiSelectCombo.setValue(this.newresource);
            delete this.newresource;
            this.onselected();
        }
    },
    
    onerror: function(message) {
        BQ.ui.error('Error fetching resource:<br>' + message); 
    },   
    
    
    onselected : function() {
                this.resource.value = this.multiSelectCombo.getValue();
                if (this.resource.value.length<1) {this.resource.value=null} //need to set to null to trigger the IsValid
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
        }
    },
    
});

Ext.define('BQ.renderers.Botanicam.ModelViewer', {
    alias: 'widget.rendererclassifiermodel',
    extend: 'BQ.renderers.Renderer',
    requires: ['Bisque.ResourceTagger'],

    height: 300,
    layout: {
        type: 'vbox',
        align : 'stretch',
        pack  : 'start',
    },

    initComponent : function() {
        var definition = this.definition;
        var template = definition.template || {};
        var resource = this.resource;
        if (!definition || !resource) return;
        template.label = template.label || 'Output file';

        BQFactory.request( { uri: resource.value,
                             cb:  callback(this, 'onFile'), });
    


        this.items = [];
        this.items.push( {xtype: 'label', html:(template.label?template.label:resource.name),  } );
        this.callParent();
    },

    onFile : function(r) {
        this.file = r;
        this.tagger = Ext.create('Bisque.ResourceTagger', {
            //resource: resource.type?resource.value:resource, // reference or resource
            resource: this.file.uri,
            flex: 1,
            cls: 'tagger',
            //title : template.label?template.label:resource.name,
            viewMode : 'ReadOnly',
            tbarCfg : {
                layout: {
                    pack: 'center'
                }
            },  //for center align
            tbar: [{
                xtype: 'button',
                text: 'Open "<b>'+this.file.name+'</b>"',
                //iconCls: 'folder',
                scale: 'large',
                //style:{width:'30%'},
                width: '30%',
                //cls: 'x-btn-default-large',
                //tooltip: 'Download',
                //handler: Ext.Function.bind( this.download, this ),
                listeners: {
                    click: function(me, resource) {
                        window.open('/client_service/view?resource='+this.file.uri);
                    },
                    scope: this
                },
            },{
                xtype: 'button',
                text: 'Download "<b>'+this.file.name+'</b>"',
                //iconCls: 'download',
                scale: 'large',
                width: '30%',
                //cls: 'x-btn-default-large',
                //tooltip: 'Download',
                //handler: Ext.Function.bind( this.download, this ),
                listeners: { 
                    click: function(me, resource) {
                        window.open(this.file.src);
                    },
                    scope: this
                },
            }]
        });
        //this.items.push(this.tagger);
        this.add(this.tagger);
        /*
        this.add({
            xtype: 'button',
            text: 'Open "<b>'+this.file.name+'</b>"',
            iconCls: 'folder',
            //scale: 'large',
            //style:{width:'30%'},
            width: '30%',
            //cls: 'x-btn-default-large',
            //tooltip: 'Download',
            //handler: Ext.Function.bind( this.download, this ),
            listeners: { 
                click: function(me, resource) {
                    window.open(bq.url('/client_service/view?resource='+this.file.uri));
                },
                scope: this
            },
        });
        this.add({
            xtype: 'button',
            text: 'Download "<b>'+this.file.name+'</b>"',
            iconCls: 'download',
            scale: 'large',
            width: '30%',
            //cls: 'x-btn-default-large',
            //tooltip: 'Download',
            //handler: Ext.Function.bind( this.download, this ),
            listeners: { 
                click: function(me, resource) {
                    window.open(this.file.src);
                },
                scope: this
            },
        });*/
    },    

});

