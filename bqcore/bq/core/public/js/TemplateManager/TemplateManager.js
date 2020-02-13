Ext.define('BQ.TemplateManager',
{
    statics :
    {
        create : function(config)
        {
            return Ext.create('BQ.TemplateManager.Creator', config);
        },

        // Create a blank resource from a template
        createResource : function(config, cb, original, template)
        {
            if (!(template instanceof BQTemplate))
            {
                BQFactory.request({
                    uri     :   template + '?view=deep',
                    cb      :   Ext.pass(BQ.TemplateManager.createResource, [config, cb, original]),
                    cache   :   false,
                });
                return;
            }
            else
            {
                // Parse template URL #http://www.joezimjs.com/javascript/the-lazy-mans-url-parsing/
                var parser = document.createElement('a');
                parser.href = template.uri;

                // Assume the template is fully loaded
                var resource = new BQResource();
                if (!original) {
                    Ext.apply(resource, {
                        resource_type   :   template.name,
                        type            : parser.pathname,
                    }, config);
                } else {
                    resource.uri = original ? original.uri : null;
                    resource.type = parser.pathname;
                }

                templated = null;
                if (original) {
                    templated = findTemplatedTags(original);
                    if (Object.keys(templated).length>0) {
                        resource.tags = original.tags;
                    }
                }
                resource = copyTags.call(this, template, resource, templated);

                if (config.noSave) {
                    cb(resource, template);
                } else {
                    var url = original ? undefined : '/data_service/' + resource.resource_type + '?view=deep';
                    //resource.save_('/data_service/' + resource.resource_type + '?view=deep',
                    resource.save_(url,
                      cb,
                      function(e) {
                          BQ.ui.error('An error occured while trying to create a resource from template: <br>' + e.message_short);
                    }, 'post');
                }
            }

            function copyTags(template, resource, templated)
            {
                var parser = document.createElement('a'),
                    i=0,
                    tag=null,
                    g=null, tt=null;

                for (i=0; (tag=template.tags[i]); ++i) {
                    parser.href = tag.uri;
                    if (!(tag.value.toLowerCase() in BQGObject.objects) ) {
                        if (!templated || !(parser.pathname in templated && templated[parser.pathname] === tag.name)) {
                            tt = resource.addtag({
                                name:tag.name,
                                value:tag.template["defaultValue"] || '',
                                type: parser.pathname,
                            });
                        } else {
                            // find an existing tag in the resource
                            tt = resource.find_tags(tag.name);
                        }
                        copyTags.call(this, tag, tt, templated);
                    } else {
                        var type = tag.value === 'Gobject' ? tag.name : tag.value.toLowerCase(),
                            vrtx = [],
                            l = (tag.template['vertices'] || '').split(';'),
                            j=0, s=null, v=null;
                        for (j=0; (s=l[j]); ++j) {
                            v = s.split(',');
                            var x = v[0] ? parseInt(v[0]) : undefined;
                            var y = v[1] ? parseInt(v[1]) : undefined;
                            var z = v[2] ? parseInt(v[2]) : undefined;
                            var t = v[3] ? parseInt(v[3]) : undefined;
                            var ch = v[4] ? parseInt(v[4]) : undefined;
                            vrtx.push(new BQVertex(x, y, z, t, ch));
                        }

                        var g = resource.addgobjects({
                            type: type,
                            vertices: vrtx,
                            value: tag.template.text
                            //name: tag.name,
                            //value:this.template["defaultValue"] || '',
                            //type: this.template.Type,
                        });

                        if (tag.template.color && tag.template.color.indexOf('#')===0) {
                            g.addtag({
                                name: 'color',
                                value: tag.template.color,
                                type: 'color',
                            });
                        }

                        copyTags.call(this, tag, g, templated);
                    }
                }
                return resource;
            };

            function findTemplatedTags(resource, templated) {
                templated = templated || {};
                for (i=0; (tag=resource.tags[i]); ++i) {
                    // dima: hack here to identify if type points to template, its just optimization for fast query
                    if (tag.type && tag.type[0] === '/') {
                        templated[tag.type] = tag.name;
                    }
                }

                return templated;
            };

        },
    }
});

Ext.define('BQ.TemplateManager.Creator',
{
    extend      :   'Ext.panel.Panel',
    border      :   false,
    layout      :   'border',
    heading     :   'Create template',
    bodyCls     :   'white',

    constructor : function(config)
    {
        Ext.apply(this,
        {
            centerPanel :   Ext.create('Ext.panel.Panel', {
                                region      :   'center',
                                border      :   false,
                                flex        :   7,
                                title       :   'Editing resource template - ' + config.resource.name || '',
                                layout      :   'fit',
                            }),

            eastPanel   :   Ext.create('Ext.panel.Panel', {
                                region      :   'east',
                                frame       :   true,
                                flex        :   3,
                                title       :   'Properties',
                                layout      :   'fit',
                                collapsible :   true,
                                split       :   true
                            })
        });

        Ext.apply(this,
        {
            items   :   [this.centerPanel, this.eastPanel],
        });

        window.onbeforeunload = Ext.bind(this.checkUnsavedChanges, this);
        this.callParent(arguments);
    },

    initComponent : function()
    {
        this.callParent(arguments);

        this.tagger = Ext.create('Bisque.TemplateTagger',
        {
            resource        :   this.resource,
            listeners       :   {
                                    'itemclick' :   this.onFieldSelect,
                                    scope       :   this
                                },
        });

        this.grid = Ext.create('Ext.grid.property.Grid', {
            source: {},
            listeners: {
                'edit': this.onPropertyEdit,
                scope: this
            },
            customEditors: {
                'select': {
                    xtype: 'textareafield',
                    emptyText: 'Enter comma separated display values e.g. Alabama, Alaska'
                },
                'passedValues': {
                    xtype: 'textareafield',
                    emptyText: 'Enter comma separated passed values e.g. AL, AK (defaults to display values)'
                },
                'resourceType': {
                    xtype: 'combo',
                    /* // dima: BQApp.resourceTypes can't be used due to race condition
                    store: Ext.create('Ext.data.Store', {
                        fields  :   ['name', 'uri'],
                        data    :   BQApp.resourceTypes,
                    }), */
                    store: {
                        //fields  :   ['name', 'uri'],
                        //data    :   BQApp.resourceTypes,
                        fields : [
                            { name: 'name', mapping: '@name' },
                            { name: 'uri', mapping: '@uri' },
                        ],
                        proxy : {
                            limitParam : undefined,
                            pageParam: undefined,
                            startParam: undefined,
                            noCache: false,
                            type: 'ajax',
                            url : '/data_service/',
                            reader : {
                                type :  'xml',
                                root :  '/',
                                record: '/*:not(value or vertex or template)',
                            }
                        },
                        autoLoad : true,
                        autoSync : false,
                    },
                    queryMode   :   'local',
                    displayField:   'name',
                    editable    :   false
                },
                'help' : {
                    xtype    : 'hyperreference',
                    viewMode : 'widget',
                },

                'color' : {
                    xtype: 'textareafield',
                    emptyText: 'HTML style color: #FF0000'
                },
                'vertices' : {
                    xtype: 'textareafield',
                    emptyText: 'Semi-colon separated 5D vertices: X1,Y1,Z1;X2,Y2,Z2'
                },

            },
        });

        this.centerPanel.add(this.tagger);
        this.eastPanel.add(this.grid);
    },

    checkUnsavedChanges : function()
    {
        if (this.resource.dirty)
        {
            this.tplToolbar.getComponent('tbTplSave').getEl().highlight('FF9500', {duration:250, iterations:6});
            return "You have unsaved changes which will be lost.";
        }
    },

    saveTemplate : function()
    {
        function success(resource)
        {
            BQ.ui.notification('Changes saved!', 2000);
            this.tagger.setResource(resource);
        }

        this.resource.dirty = false;
        if (this.resource.uri.indexOf('view=deep')===-1) {
            this.resource.uri = this.resource.uri + '?view=deep';
        }
        this.resource.save_(undefined, Ext.bind(success, this), Ext.pass(BQ.ui.error, ['Save failed!']));
    },

    onFieldSelect : function(tree, record)
    {
        this.currentField = record.raw;
        this.currentTemplate = this.currentField.find_children('template');
        this.eastPanel.setTitle('Properties - ' + this.currentField.name);
        this.grid.setSource(BQ.TagRenderer.Base.convertTemplate(this.currentTemplate));
    },

    onPropertyEdit : function(editor, record)
    {
        var tagName = record.record.get('name');
        var tag = this.currentTemplate.find_tags(tagName);

        if (tag)
            tag.value = record.value.toString();
    }
});

Ext.define('BQ.form.field.HyperReference', {
    extend: 'Ext.form.field.Display',
    alias: 'widget.hyperreference',

    setValue : function(value) {
        this.callParent(arguments);
        if (value)
            htmlAction(BQ.Server.url(value), 'Help');
    },
});