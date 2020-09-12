BQ.selectors.parameters.jpstag_selector = 'BQ.selectors.Dream3D.TagSelector';

/*
 *  The tag selector for Dream3D Module
 *
 *  Warning: Takes in only dream3d pipeline
 *
 * Example in XMl
 *
 *  <tag name="tag_names" type="tag_selector">
 *      <template>
 *          <tag name="label" value="Enter parameters for pipeline run" />
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
 * wants to reference (resource must be dream3d_pipeline)
 *
 */
Ext.define('BQ.selectors.Dream3D.TagSelector', {
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
                    this.onselected();
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

            if (me['resource'].type=='dream3d_pipeline'){
                this.tag_url=me['resource'].value+'&tag_names=1';
            }
            else {
                this.onerror(me['resource'].value);
            }
            this.setLoading('Fetching members...');
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
                if (this.resource.value.length != 1) {this.resource.value=null;} //need to set to null to trigger the IsValid
                if (!this.validate()) return;
    },

    isValid: function() {
        if (!this.resource.value) {
            BQ.ui.tip(this.getId(), 'Please select one property to run pipeline', {anchor:'left',});
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
