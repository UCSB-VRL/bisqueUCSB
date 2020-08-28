Ext.define('BQ.module.ModuleUIEditor', {
});


Ext.define('BQ.module.MexInfoPreview', {
    extend: 'Ext.panel.Panel',
    border: false,

});



Ext.define('BQ.module.ModuleInputPreview', {
    extend: 'Ext.panel.Panel',
    layout: 'vbox',
    border: false,
    autoScroll: true,
    inputRenderers: [],
    //padding: '20px 20px 20px 20px',
    defaults: {
        //hidden: true,
        padding: '0px 20px 0px 20px',
        width: '100%',
    },
    initComponent: function(config) {
        var config = config || {};
        var me = this;

        me.noModuleView = Ext.create('Ext.container.Container', {
            html: [
                '<h1>No Module Selected.</h1>'
            ],
        });

        me.previewBanner = Ext.create('Ext.container.Container', {
             html: [
                '<h1>Generated Debug Inputs:</h1>',
                '<p><i>Warning: Not all components will show up as expected since some are custom components and the debugger does not have the renderers for custom components.</i></p>',
            ],
            style: {
              backgroundColor: '#A3FFA3',
              borderColor: '#66FF00',
              borderStyle: 'solid',
              borderWidth: '1px',
              padding: '10px 10px 10px 10px',
              marginBottom: '20px',
              borderRadius: '5px',
            },
        });

        me.moduleHeader = Ext.create('Ext.container.Container', {
            tpl: [
                '<div style="position:relative">',
                    '<h1 style="font-size:40px">{name}</h1>',
                    '<p>Version: {version}  Authors: {authors}</p>',
                    '<p><i>{description}</i></p>',
                    '<tpl if="thumbnail">',
                        '<img style="position:absolute; top: 0px;right: 10px;" src="{thumbnail}" height="150" width="150">',
                    '</tpl>',
                '</div>',
            ],
            data: {
                name:'',
                authors: '',
                version: '',
                description: '',
                thumbnail: '',
            },
        });

        me.resourceSelectorsTitle = Ext.create('Ext.container.Container', {
            tpl: ['<h1>{count}. Select data for processing</h1>'],
            data: {count:1},
            width: '100%',
        });

        me.resourceSelectors = Ext.create('Ext.container.Container', {
            width: '100%',
            style: {
              backgroundColor: '#EEEEEE',
              borderColor: '#CCCCCC',
              borderStyle: 'solid',
              borderWidth: '1px',
              padding: '10px 10px 10px 10px',
              marginBottom: '20px',
              borderRadius: '5px',
            },
        });

        me.parameterSelectorTitle = Ext.create('Ext.container.Container', {
            tpl: ['<h1>{count}. Parameters</h1>'],
            data: {count:1},
            width: '100%',
        });

        me.parameterSelector = Ext.create('Ext.container.Container', {
            width: '100%',
            style: {
              backgroundColor: '#EEEEEE',
              borderColor: '#CCCCCC',
              borderStyle: 'solid',
              borderWidth: '1px',
              padding: '10px 10px 10px 10px',
              marginBottom: '20px',
              borderRadius: '5px',
            },
        });

        me.startDebugTitle = Ext.create('Ext.container.Container', {
            tpl: ['<h1>{count}. Create Mex</h1>'],
            data: {count:1},
            width: '100%',
        });

        me.startDebug = Ext.create('Ext.container.Container', {
            layout: 'hbox',
            width: '100%',
            style: {
              backgroundColor: '#EEEEEE',
              borderColor: '#CCCCCC',
              borderStyle: 'solid',
              borderWidth: '1px',
              padding: '10px 10px 10px 10px',
              marginBottom: '20px',
              borderRadius: '5px',
            },
            items: [{
                xtype: 'button',
                text: 'Create',
                scale : 'large',
                padding: '0px 40px 0px 40px',
                handler: function() {
                    me.createDebugMex(me.module);
                },
            }, {
                xtype: 'container',
                html: '<p>Mex will be initialized and shown below.</p>',
                padding: '0px 20px 0px 20px',
            }],
        });

        var items = [
            me.noModuleView,
            me.previewBanner,
            me.moduleHeader,
            me.resourceSelectorsTitle,
            me.resourceSelectors,
            me.parameterSelectorTitle,
            me.parameterSelector,
            me.startDebugTitle,
            me.startDebug,
        ];

        Ext.apply(me, {
            items: [{
                xtype: 'container',
                padding: '20px 20px 20px 20px',
                items: items,
                defaults: {
                    listeners: {
                        afterrender: function(el) {
                            el.hide();
                        }
                    }
                }
            }],

        });
        me.noModuleViewMode(true);
        this.callParent([config]);
    },

    noModuleViewMode: function(bool) { //switch between modes
        var me = this;
        if (bool) {
            me.noModuleView.show();
            me.previewBanner.hide();
            me.moduleHeader.hide();
            me.resourceSelectorsTitle.hide();
            me.resourceSelectors.hide();
            me.parameterSelectorTitle.hide();
            me.parameterSelector.hide();
            me.startDebugTitle.hide();
            me.startDebug.hide();
        } else {
            me.noModuleView.hide();
            me.previewBanner.show();
            me.moduleHeader.show();
            me.resourceSelectorsTitle.show();
            me.resourceSelectors.show();
            me.parameterSelectorTitle.show();
            me.parameterSelector.show();
            me.startDebugTitle.show();
            me.startDebug.show();
        }
    },

    loadModule: function(el, module_id) {
        var me = this;
        BQFactory.load(
            '/'+module_id+'?view=deep',
            function(resource) {
                if (resource.inputs) {
                    me.renderInputs(resource);
                }
            }
        )
    },

    renderInputs: function(bqmodule) {
        var me = this;
        if (bqmodule.resource_type!='module') {
            BQ.ui.error('Not a module resource!');
            return; //not a module
        }
        me.noModuleViewMode(false);
        me.previewBanner.show();
        //render a title
        if(bqmodule.thumbnail) {
            var thumbnail = bqmodule.thumbnail.replace(new RegExp("^['public']+", "g"), "");
            var thumbnail_url = '/module_service/'+bqmodule.name+'/'+thumbnail;
        } else {
            var thumbnail_url = '';
        }
        me.moduleHeader.update({
                name: bqmodule.name,
                authors: bqmodule.authors,
                version: bqmodule.version,
                description: bqmodule.description,
                thumbnail: thumbnail_url,
        });
        me.moduleHeader.show();

        me.inputRenderers = []
        //render components
        var bq_module_inputs = bqmodule.inputs;
        me.resourceSelectors.removeAll();
        me.parameterSelector.removeAll();
        for (var i = 0; i<bq_module_inputs.length; i++) {
            if(bq_module_inputs[i].type != "system-input") { //if system-input skip
                if (bq_module_inputs[i].type in BQ.selectors.resources) { //add to the resource selectors
                    var resourceSelector = Ext.create(BQ.selectors.resources[bq_module_inputs[i].type], {
                            resource: bq_module_inputs[i],
                            module: bqmodule,
                    })
                    var inputRenderer = me.resourceSelectors.add(resourceSelector);
                    me.inputRenderers.push(inputRenderer);
                } else if (bq_module_inputs[i].type in BQ.selectors.parameters) { //add to the parameter selectos
                    var parameterSelector = Ext.create(BQ.selectors.parameters[bq_module_inputs[i].type], {
                        resource: bq_module_inputs[i],
                        module: bqmodule,
                    })
                    var inputRenderer = me.parameterSelector.add(parameterSelector);
                    me.inputRenderers.push(inputRenderer);
                } else { //custom element, do not know how to render
                }
            }
        }


        var elementCount = 0;
        if (me.resourceSelectors.items.length>0) {
            me.resourceSelectors.doLayout();
            elementCount += 1;
            me.resourceSelectorsTitle.update({count:elementCount});
            me.resourceSelectorsTitle.show();
            me.resourceSelectors.setVisible(true);
        } else { //hide resource elements
            me.resourceSelectorsTitle.setVisible(false);
            me.resourceSelectors.setVisible(false);
        }
        if (me.parameterSelector.items.length>0) {
            me.parameterSelector.doLayout();
            elementCount += 1;
            me.parameterSelectorTitle.update({count:elementCount});
            me.parameterSelectorTitle.setVisible(true);
            me.parameterSelector.setVisible(true);
        } else { //hide parameter elements
            me.parameterSelectorTitle.setVisible(false);
            me.parameterSelector.setVisible(false);
        }
        elementCount += 1;
        me.startDebugTitle.update({count:elementCount});
        me.startDebugTitle.setVisible(true);
        me.module = bqmodule;
    },

    createDebugMex: function(bqmodule) {
        var me = this;
        if (!BQSession.current_session || !BQSession.current_session.hasUser()) {
            BQ.ui.warning('You are not logged in! You need to log-in to run any analysis...');
            return;
        }
        if(!me.isValid()) return
        var mex = bqmodule.createMEX();
        mex.name = bqmodule.name;
        mex.type = bqmodule.uri;
        mex.save_('/module_service/mex', function(mex) {
            me.fireEvent('afterCreated', me, mex)
        });

    },
    isValid: function() {
        var me = this;
        var valid = true;
        for (var i = 0; i<me.inputRenderers.length;i++) {
            valid = me.inputRenderers[i].validate() && valid;
        }
        return valid
    },
})


Ext.define('BQ.module.MexLauncher', {
    extend: 'Ext.panel.Panel',
    bodyStyle:{"background-color":"white"},
    border: false,
    layout: {
        // layout-specific configs go here
        type: 'accordion',
        //titleCollapse: false,
        animate: true,
        //activeOnTop: true
    },
    defaults: {
        border: false,
        collapsible: true,
        split: true,
        bodyStyle: 'padding:0px'
    },
    initComponent: function(config) {
        var config = config || {};
        var me = this;

        var items = [];
        me.ModuleSelector = Ext.create('Ext.panel.Panel',{
            title: 'Choise a type of mex to create.',
            //height: '25%',
            width: '100%',
            layout: 'vbox',
            padding:'0px',
            border: false,
            items: [{
                border: false,
                xtype: 'container',
                html: [
                    '<h2>Mex Launcher</h2>',
                    '<p>Welome to the Mex Launcher. Generates mexs for registered modules or scripts will update the module display based on updated mexes.</p>',
                    '<p>Select a registered module or no module to be run in debug mode.</p>',
                ],
                padding: '10px 10px 0px 20px',
            },{
                border: false,
                xtype: 'combo',
                width: '500px',
                padding: '10px 10px 20px 40px',
                valueField: 'name',
                displayField: 'name',
                /*fieldSubTpl: [
                    '<h1 style="padding-top:10px; height:30px; float:left; text-overflow:ellipsis; width:90%; white-space: nowrap; overflow:hidden; margin:0px;">{name}</h1>',
                    '<div style="width: 100%; overflow: hidden;">',
                        //'<img src="{thumbnail_uri}" alt="Not Found!" style="width:128px; height:128px; float:left; margin:11px"/>',
                        '<div style="margin-left:148px;">',
                            '<p><b>Title:</b> {title}</p>',
                            '<p><b>Description:</b> {description}</p>',
                            '<p><b>Authors:</b> {authors}</p>',
                        '</div>',
                    '</div>',
                ],*/

                store: Ext.create('Ext.data.Store',{
                    noCache: false,
                    proxy:{
                        type: 'ajax',
                        params: {view:'full'},
                        queryParam: null,
                        limitParam: null,
                        pageParam: null,
                        startParam: null,
                        url: '/module_service',
                        reader: {
                            type: 'xml',
                            root:'resource',
                            record: 'module',
                        }
                    },
                    fields: [{
                        name: 'name',
                        mapping: '@name',
                    },{
                        name: 'resource_uniq',
                        mapping: '@resource_uniq',
                    },{
                        name: 'authors',
                        mapping: "tag[@name='authors']/@value",
                    },{
                        name: 'thumbnail',
                        mapping: "tag[@name='thumbnail']/@value",
                    },{
                        name: 'description',
                        mapping: "tag[@name='description']/@value",
                    },{
                        name: 'title',
                        mapping: "tag[@name='title']/@value",
                    }],
                }),

                listeners: {
                    select: function(el, records, eOpts) {
                        var module_id = records[0].get('resource_uniq');
                        me.ModuleSelector.collapse(); //breaks
                        me.modulePage.loadModule(me.modulePage, module_id);
                    },
                },
            }],
        }),
        items.push(me.ModuleSelector);
        me.modulePage = Ext.create('BQ.module.ModuleInputPreview', {
            title: 'Generate Mex',
            width: '100%',
            height: '100%',
            border: false,
            collapsible: false,
            autoScroll: true,
            listeners: {
                afterCreated: function() {
                    me.modulePage.collapse(); //breaks
                }
            }
        }),

        items.push(me.modulePage);

        items.push({
            title: 'Mex Preview',
            border: false,
            layout: 'fit',
            tpl: [
                '<tpl if="!mexUrl">',
                    '<p>No mex has been run yet!</p>',
                    '<p>Choose all the parameters that will be added to the mex and run the module to generate the mex.</p>',
                '</tpl>',
                '<tpl if="mexUrl">',
                    '<p>Mex Url: {mexUrl}</p>',
                    '<p>Mex Token: {mexToken}</p>',
                '</tpl>',
            ],
            data: {
                mexUrl: false,
                mexToken: false,
            },
            listeners: {
                afterrender: function(el) {
                    var mexInfoEl = el;
                    me.modulePage.on('afterCreated', function(el, mex) {
                        BQFactory.load(mex.owner, function(owner){
                            mexInfoEl.update({
                                mexUrl: mex.uri,
                                mexToken: owner.name+':'+mex.resource_uniq,
                            })
                        })

                    })
                }
            }
        });

        Ext.apply(me, {
            items: items,
        });
        this.callParent([config]);
    },
});

Ext.define('BQ.module.ModuleDeveloperPage', {
    extend : 'Ext.panel.Panel',
    alias: 'widget.bq_module_developer',


    layout : 'fit',
    height : '85%',
    width : '85%',
    modal : true,
    border: false,

    initComponent: function(config) {
        var config = config || {};
        var me = this;

        var items = [{
            region: 'center',
            xtype: 'tabpanel',
            items: [{
                title: 'Mex Launcher',
                layout: 'fit',
                border: false,
                items: Ext.create('BQ.module.MexLauncher'),
            },{
                title: 'Module UI Editor',
                layout: 'fit',
                border: false,
                disabled: true,
            }]
        }];

        Ext.apply(me, {
            items: items,
        });
        this.callParent([config]);
    }
});