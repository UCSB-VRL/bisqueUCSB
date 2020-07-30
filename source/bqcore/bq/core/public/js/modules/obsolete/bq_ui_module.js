Ext.define('BQ.ModulePanel', {
    extend: 'Ext.form.Panel',
    requires: [],
    resource_url: null,

    constructor:function (config){
        Ext.apply(this, {
            buttons : [ { 
                text: 'Cancel',
                handler : function () {}
            }, { 
                text : 'Run',
                formBind : true,
                handler : function () {
                    var panel = this.up('form');
                    
                    Ext.Ajax.request({ url : 'execute',
                                       params : { image_url : panel.resource_url },
	                                   success: function ( result, request ) { 
		                                   Ext.MessageBox.alert('Success', 'Data return from the server: '+ result.responseText); 
	                                   },
	                                   failure: function ( result, request) { 
		                                   Ext.MessageBox.alert('Failed', result.responseText); 
	                                   } 
                                     });
                }
            }],
            defaultType: 'textfield',
        });

        this.callParent(arguments);

        //BQ.ModulePanel.superclass.initComponent.apply(this, arguments);
        BQFactory.load(config.module_uri + '?view=deep', Ext.bind (this.module_loaded, this));
    },

    activate_browser : function () {
    },
  
    module_arguments : {},
    filtered_fields : { 'bisque_token':1, 'mex_url':1 },
    special_fields  : { 
        image_url : function (module, input_tag) {
            var module_panel = this;
            this.add ( { xtype: 'fieldcontainer',
                         fieldLabel: 'Resource URL',
                         layout : 'hbox',
                         items : [ { xtype : 'textfield',
                                     id  : 'image_url',
                                     emptyText : input_tag,
                                     allowBlank : false,
                                     flex : 1 },
                                   { xtype: 'splitter' },
                                   { xtype: 'button', 
                                     text : 'Browse',
                                     handler : function () { 
                                         var resourceBrowser  = new Bisque.ResourceBrowser.BrowserWindow({
                                             'layout' : Bisque.ResourceBrowser.LayoutFactory.DEFAULT_LAYOUT,
                                             'height' : '85%',
                                             'width' :  '85%',
                                             'dataset' : '/data_service/images',
                                             'offset': 0,
                                         });
                                         resourceBrowser.on('Select', function(url) { 
                                             //var x = this.findParentByType('BQ.ModulePanel');
                                             module_panel.resource_url = url; 
                                             var tf = Ext.getCmp('image_url')
                                             tf.setValue (url)
                                             resourceBrowser.destroy(); 
                                         }  );    
                                         resourceBrowser.show();
                                         resourceBrowser.center(); 
                                         
                                     }
                                   }
                                 ],
                       });
        }
    },
        
    module_loaded : function (module) {
        this.module = module;
        var inputs = module.inputs
        for (var i=0; i< inputs.length; i++){
            var tag = inputs[i];
            if (tag in this.filtered_fields) continue;
            if (tag in this.special_fields) {
                this.special_fields[tag].call (this, module, tag);
                continue;
            }

            this.add ({ fieldLabel: tag,
                        name : tag,
                        emptyText: tag,
                        allowBlank:false,
                      });
        }
    },
});
 
                
