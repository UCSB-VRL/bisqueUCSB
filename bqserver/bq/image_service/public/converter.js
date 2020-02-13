/*******************************************************************************
  Image converter UI - builds Bisque Image Service requests
  Author: Dima Fedorov <dima@dimin.net>
  Copyright 2012, Center for Bio-Image Informatics, UCSB


*******************************************************************************/

//----------------------------------------------------------------------------------
// BQ.is.Service - base class for all IS services
//----------------------------------------------------------------------------------

Ext.define('BQ.panel.ToolCheck', {
    extend: 'Ext.panel.Tool',
    alias: 'widget.toolcheck',

    cls: 'checkbox',
    //checked: false,
    //type: 'unpin',
    tooltip : 'Enable/disable service',
    stopEvent: true,

    initComponent : function() {
        this.checked = this.checked || false;
        this.type = this.checked ? 'pin' : 'unpin';
        this.callParent();
    },

    //privates: { // dima: ext5 overriding
    onClick: function(e, target) {
        this.checked = !this.checked;
        if (this.checked)
            this.setType('pin');
        else
            this.setType('unpin');
        this.callParent(arguments);
    },
    //}, // ext5

    isChecked: function() {
        return this.checked;
    },

});


//----------------------------------------------------------------------------------
// BQ.is.Service - base class for all IS services
//----------------------------------------------------------------------------------

Ext.define('BQ.is.Service', {
    extend: 'Ext.panel.Panel',
    cls: 'service',
    defaults: { border: 0,  },

    constructor: function(config) {
        this.addEvents({
            'changed' : true,
        });
        this.callParent(arguments);
        return this;
    },

    initComponent : function() {
        this.enabled = this.enabled || false;
        this.tools = [{
            xtype   : 'toolcheck',
            itemId  : 'enabeled-checkbox',
            checked : this.enabled,
            scope   : this,
            handler : this.onCheckbox,
        }];
        this.items = [Ext.apply({
            xtype : 'container',
            itemId: 'surface',
            cls: 'surface',
            disabled: !this.enabled,
            defaults: { labelWidth: 120, },
        }, this.surface_config || {})];
        this.callParent();
    },

    createCombo: function (items, config) {
        var options = Ext.create('Ext.data.Store', {
            fields: ['value', 'text'],
            data : items
        });
        combo = {
            xtype: 'combobox',
            store: options,
            queryMode: 'local',
            displayField: 'text',
            valueField: 'value',
            forceSelection: true,
            editable: false,
            flex: 1,
            listeners: {
                scope: this,
                'select': this.emitChange,
            },
        };
        return Ext.apply(combo, config);
    },

    onCheckbox: function(event, el, owner, tool) {
        this.queryById('surface').setDisabled(!tool.isChecked());
        this.fireEvent('changed');
    },

    emitChange: function() {
        this.fireEvent('changed');
    },

    isEnabeled: function() {
        return this.queryById('enabeled-checkbox').isChecked();
    },

    // override in subclass, should return a string with URL attribute for this service
    getOperation: function() {
        return undefined;
    },

    // override in subclass, should return an updated dimensions object
    updateDims: function(dims) {
        return dims;
    },

});

//----------------------------------------------------------------------------------
// BQ.is.Service.Roi
//----------------------------------------------------------------------------------

Ext.define('BQ.is.Service.Slice', {
    extend: 'BQ.is.Service',
    title: 'Slice',
    alias: 'widget.bqis-service-slice',

    initComponent : function() {
        this.surface_config = {
            layout: {
                type: 'table',
                columns: 2,
            },
            items: [{
                    xtype:'tbtext',
                    colspan: 2,
                    text: '<p>Extracts specific planes from the input 4D image<p>',
                }, {
                    xtype: 'numberfield',
                    itemId: 'sel_z1',
                    fieldLabel: 'Initial Z',
                    value: this.slice.z1 || 1,
                    minValue: 1,
                    maxValue: this.phys.z,
                    allowDecimals: false,
                    step: 1,
                    listeners: {
                        scope: this,
                        change: this.validate,
                    },
                }, {
                    xtype: 'numberfield',
                    itemId: 'sel_z2',
                    fieldLabel: 'Final Z',
                    value: this.slice.z2 || 0,
                    minValue: 0,
                    maxValue: this.phys.z,
                    allowDecimals: false,
                    step: 1,
                    listeners: {
                        scope: this,
                        change: this.validate,
                    },
                }, {
                    xtype: 'numberfield',
                    itemId: 'sel_t1',
                    fieldLabel: 'Initial T',
                    value: this.slice.t1 || 1,
                    minValue: 1,
                    maxValue: this.phys.t,
                    allowDecimals: false,
                    step: 1,
                    listeners: {
                        scope: this,
                        change: this.validate,
                    },
                }, {
                    xtype: 'numberfield',
                    itemId: 'sel_t2',
                    fieldLabel: 'Final T',
                    value: this.slice.t2 || 0,
                    minValue: 0,
                    maxValue: this.phys.t,
                    allowDecimals: false,
                    step: 1,
                    listeners: {
                        scope: this,
                        change: this.validate,
                    },
                },
                this.createCombo ([
                        {'value':'', 'text':'None'},
                        {'value':'projectmax', 'text':'Maximum intensity projection'},
                        {'value':'projectmin', 'text':'Minimum intensity projection'},
                    ], {
                        itemId: 'combo-projection',
                        fieldLabel: 'Intensity projection',
                        colspan: 2,
                        //minWidth: 350,
                        //width: '100%',
                        value: this.slice.projection || '',
                        listeners: {
                            scope: this,
                            'select': this.validate,
                        }
                    }),
            ],
        };
        this.callParent();
    },

    validate: function(e) {
        var z1 = this.queryById('sel_z1').getValue();
        var z2 = this.queryById('sel_z2').getValue();
        var t1 = this.queryById('sel_t1').getValue();
        var t2 = this.queryById('sel_t2').getValue();
        var prj = this.queryById('combo-projection').getValue();

        if (z2===0 && t2===0 && prj!=='') {
            if (e) BQ.ui.tip(e.getId(), 'Output image is 2D and projection is impossible', {anchor:'left',});
            this.queryById('combo-projection').setValue('');
        }

        return true;
    },

    updateDims: function(dims) {
        if (!this.validate) return dims;
        var z1 = this.queryById('sel_z1').getValue();
        var z2 = this.queryById('sel_z2').getValue();
        var t1 = this.queryById('sel_t1').getValue();
        var t2 = this.queryById('sel_t2').getValue();
        var prj = this.queryById('combo-projection').getValue();

        dims.z = 1;
        dims.t = 1;
        if (z2>0)
            dims.z = z2-z1;
        if (t2>0)
            dims.t = t2-t1;
        if (prj) {
            dims.z = 1;
            dims.t = 1;
        }
        return dims;
    },

    getOperation: function() {
        if (!this.validate) return undefined;
        var z1 = this.queryById('sel_z1').getValue();
        var z2 = this.queryById('sel_z2').getValue();
        var t1 = this.queryById('sel_t1').getValue();
        var t2 = this.queryById('sel_t2').getValue();
        var prj = this.queryById('combo-projection').getValue();

        var command = 'slice=,,'+z1;
        if (z2>0) command += '-'+z2;
        command += ','+t1;
        if (t2>0) command += '-'+t2;
        command += prj ? '&'+prj:'';
        return command;
    },
});

//----------------------------------------------------------------------------------
// BQ.is.Service.Depth
//----------------------------------------------------------------------------------

Ext.define('BQ.is.Service.Depth', {
    extend: 'BQ.is.Service',
    title: 'Depth',
    alias: 'widget.bqis-service-depth',

    initComponent : function() {
        var format = 'u';
        if (this.phys.pixel_format && this.phys.pixel_format in this.phys.pixel_formats)
            format = this.phys.pixel_formats[this.phys.pixel_format];
        var default_format = this.phys.pixel_depth +','+format;
        this.surface_config = {
            items: [{
                    xtype:'tbtext',
                    text: '<p>Converts pixel depth of the image<p>',
                },
                this.createCombo ([
                        {'value':'8,u', 'text':'8bit unsigned integer'},
                        {'value':'16,u', 'text':'16bit unsigned integer'},
                        {'value':'32,u', 'text':'32bit unsigned integer'},
                        {'value':'64,u', 'text':'64bit unsigned integer'},
                        {'value':'8,s', 'text':'8bit signed integer'},
                        {'value':'16,s', 'text':'16bit signed integer'},
                        {'value':'32,s', 'text':'32bit signed integer'},
                        {'value':'64,s', 'text':'64bit signed integer'},
                        {'value':'32,f', 'text':'32bit floating point'},
                        {'value':'64,f', 'text':'64bit floating point'},
                    ], {
                        itemId: 'combo-format',
                        fieldLabel: 'Format',
                        value: default_format,
                }),

                this.createCombo ([
                        {'value':'f', 'text':'Full range'},
                        {'value':'d', 'text':'Data range'},
                        {'value':'t', 'text':'Data + tolerance'},
                        {'value':'e', 'text':'Equalized'},
                    ], {
                        itemId: 'combo-method',
                        fieldLabel: 'Method',
                        value: 'd',
                 }),
            ],
        };
        this.callParent();
    },

    updateDims: function(dims) {
        var f = this.queryById('combo-format').getValue();
        f = f.replace(/,\w/gi, '');
        dims.d = parseInt(f);
        return dims;
    },

    getOperation: function() {
        var f = this.queryById('combo-format').getValue();
        var m = this.queryById('combo-method').getValue();
        return 'depth='+f.replace(',', ','+m+',');
    },
});

//----------------------------------------------------------------------------------
// BQ.is.Service.Roi
//----------------------------------------------------------------------------------

Ext.define('BQ.is.Service.Roi', {
    extend: 'BQ.is.Service',
    title: 'ROI',
    alias: 'widget.bqis-service-roi',

    initComponent : function() {
        this.surface_config = {
            layout: {
                type: 'table',
                columns: 2,
            },
            items: [{
                xtype:'tbtext',
                colspan: 2,
                text: '<p>Extracts Region Of Interest from any plane<p>',
            }, {
                xtype: 'numberfield',
                itemId: 'top_left_x',
                fieldLabel: 'Top left X',
                value: 1,
                minValue: 1,
                maxValue: this.phys.x,
                allowDecimals: false,
                step: 1,
                listeners: {
                    scope: this,
                    change: this.emitChange,
                },
            }, {
                xtype: 'numberfield',
                itemId: 'top_left_y',
                fieldLabel: 'Top left Y',
                value: 1,
                minValue: 1,
                maxValue: this.phys.y,
                allowDecimals: false,
                step: 1,
                listeners: {
                    scope: this,
                    change: this.emitChange,
                },
            }, {
                xtype: 'numberfield',
                itemId: 'bottom_right_x',
                fieldLabel: 'Bottom right X',
                value: this.phys.x,
                minValue: 1,
                maxValue: this.phys.x,
                allowDecimals: false,
                step: 1,
                listeners: {
                    scope: this,
                    change: this.emitChange,
                },
            }, {
                xtype: 'numberfield',
                itemId: 'bottom_right_y',
                fieldLabel: 'Bottom right Y',
                value: this.phys.y,
                minValue: 1,
                maxValue: this.phys.y,
                allowDecimals: false,
                step: 1,
                listeners: {
                    scope: this,
                    change: this.emitChange,
                },
            }],
        };
        this.callParent();
    },

    getOperation: function() {
        var x1 = this.queryById('top_left_x').getValue();
        var y1 = this.queryById('top_left_y').getValue();
        var x2 = this.queryById('bottom_right_x').getValue();
        var y2 = this.queryById('bottom_right_y').getValue();
        return 'roi='+x1+','+y1+','+x2+','+y2;
    },
});

//----------------------------------------------------------------------------------
// BQ.is.Service.Negative
//----------------------------------------------------------------------------------

Ext.define('BQ.is.Service.Negative', {
    extend: 'BQ.is.Service',
    title: 'Negative',
    alias: 'widget.bqis-service-negative',

    initComponent : function() {
        this.enabled = this.view.negative==='negative' ? true : false;
        this.surface_config = {
            items: [{
                xtype:'tbtext',
                text: '<p>Inverts intesity of the input image<p>',
            }],
        };
        this.callParent();
    },

    getOperation: function() {
        return 'negative';
    },

});

//----------------------------------------------------------------------------------
// BQ.is.Service.Negative
//----------------------------------------------------------------------------------

Ext.define('BQ.is.Service.Deinterlace', {
    extend: 'BQ.is.Service',
    title: 'Deinterlace',
    alias: 'widget.bqis-service-deinterlace',

    initComponent : function() {
        this.enabled = this.view.deinterlace==='deinterlace' ? true : false;
        this.surface_config = {
            items: [{
                xtype:'tbtext',
                text: '<p>Deinterlaces the input image<p>',
            }],
        };
        this.callParent();
    },

    getOperation: function() {
        return 'deinterlace';
    },

});


//----------------------------------------------------------------------------------
// BQ.is.Service.Rotate
//----------------------------------------------------------------------------------

Ext.define('BQ.is.Service.Rotate', {
    extend: 'BQ.is.Service',
    title: 'Rotate',
    alias: 'widget.bqis-service-rotate',

    initComponent : function() {
        this.surface_config = {
            items: [{
                    xtype:'tbtext',
                    text: '<p>Rotates the image<p>',
                },
                this.createCombo ([
                        {'value':'0', 'text':'0'},
                        {'value':'90', 'text':'90 deg'},
                        {'value':'180', 'text':'180 deg'},
                        {'value':'270', 'text':'270 deg'},
                    ], {
                        itemId: 'combo-rotate',
                        fieldLabel: 'Rotation angle',
                        value: '0',
                 }),
            ],
        };
        this.callParent();
    },

    getOperation: function() {
        return 'rotate='+this.queryById('combo-rotate').getValue();
    },
});

//----------------------------------------------------------------------------------
// BQ.is.Service.Resize
//----------------------------------------------------------------------------------

Ext.define('BQ.is.Service.Resize', {
    extend: 'BQ.is.Service',
    title: 'Resize',
    alias: 'widget.bqis-service-resize',

    initComponent : function() {
        this.surface_config = {
            layout: {
                type: 'table',
                columns: 2,
            },
            items: [{
                    xtype:'tbtext',
                    colspan: 2,
                    text: '<p>Resizes each image plane<p>',
                }, {
                    xtype: 'numberfield',
                    itemId: 'selector_w',
                    fieldLabel: 'Width',
                    value: this.phys.x,
                    minValue: 0,
                    //maxValue: this.phys.x,
                    allowDecimals: false,
                    step: 1,
                    listeners: {
                        scope: this,
                        change: this.validate,
                    },
                }, {
                    xtype: 'numberfield',
                    itemId: 'selector_h',
                    fieldLabel: 'Height',
                    value: this.phys.y,
                    minValue: 0,
                    //maxValue: this.phys.x,
                    allowDecimals: false,
                    step: 1,
                    listeners: {
                        scope: this,
                        change: this.validate,
                    },
                },
                this.createCombo ([
                        {'value':'', 'text':'As defined'},
                        {'value':'MX', 'text':'Maximum bounding box'},
                        {'value':'AR', 'text':'Preserve aspect ratio'},
                    ], {
                        itemId: 'combo-sizing',
                        fieldLabel: 'Sizing',
                        value: '',
                        colspan: 2,
                 }),
                this.createCombo ([
                        {'value':'NN', 'text':'Nearest neighbor'},
                        {'value':'BL', 'text':'Bilinear'},
                        {'value':'BC', 'text':'Bicubic'},
                    ], {
                        itemId: 'combo-method',
                        fieldLabel: 'Method',
                        value: 'BC',
                        colspan: 2,
                 }),
            ],
        };
        this.callParent();
    },

    validate: function(e) {
        var w = this.queryById('selector_w').getValue();
        var h = this.queryById('selector_h').getValue();
        if (w===0 && h===0) {
            if (e) BQ.ui.tip(e.getId(), 'Both values can\'t be 0!', {anchor:'left',});
            return false;
        }
        if (w===0 || h===0) {
            if (e) BQ.ui.tip(e.getId(), 'If value is 0 it will be automatically computed using aspect ratio', {anchor:'left',});
            this.queryById('combo-sizing').setValue('AR');
        }

        return true;
    },

    getOperation: function() {
        if (!this.validate) return undefined;
        var w = this.queryById('selector_w').getValue();
        var h = this.queryById('selector_h').getValue();
        var s = this.queryById('combo-sizing').getValue();
        var m = this.queryById('combo-method').getValue();
        return 'resize='+w+','+h+','+m+ (s ? ','+s:'');
    },

});

//----------------------------------------------------------------------------------
// BQ.is.Service.Fuse
//----------------------------------------------------------------------------------

Ext.define('BQ.is.Service.Fuse', {
    extend: 'BQ.is.Service',
    title: 'Fuse channels',
    alias: 'widget.bqis-service-fuse',

    initComponent : function() {
        var items = [{
                xtype:'tbtext',
                text: '<p>Produces an RGB image fusing channels for each plane<p>',
        }];

        for (var ch=0; ch<parseInt(this.phys.ch); ++ch) {
            items.push({
                xtype: 'colorfield',
                itemId: 'channel-color-picker-'+ch,
                fieldLabel: this.phys.channel_names[ch],
                name: 'channel_color_'+ch,
                channel: ch,
                labelWidth: 300,
                value: this.phys.channel_colors[ch].toString().replace('#', ''),
                listeners: {
                    scope: this,
                    change: this.emitChange,
                },
            });
        }

        this.surface_config = {
            layout: {
                type: 'vbox',
                align: 'stretch',
            },
            items: items,
        };
        this.callParent();
    },

    updateDims: function(dims) {
        dims.c = 3;
        return dims;
    },

    getOperation: function() {
        var fusion='';
        for (var c=0; c<parseInt(this.phys.ch); ++c) {
            var val = this.queryById('channel-color-picker-'+c).getValue();
            var cc = Ext.draw.Color.fromString('#'+val);
            fusion += cc.getRed() + ',';
            fusion += cc.getGreen() + ',';
            fusion += cc.getBlue() + ';';
        }
        return 'fuse='+fusion;
    },

});

//----------------------------------------------------------------------------------
// BQ.is.services - list of all supported services
//----------------------------------------------------------------------------------

Ext.namespace('BQ.is');
BQ.is.services = [
    'BQ.is.Service.Slice',
    'BQ.is.Service.Depth',
    'BQ.is.Service.Fuse',
    'BQ.is.Service.Roi',
    'BQ.is.Service.Resize',
    'BQ.is.Service.Rotate',
    'BQ.is.Service.Negative',
    'BQ.is.Service.Deinterlace',
];



//----------------------------------------------------------------------------------
// BQ.is.Converter - main UI elemnet
//----------------------------------------------------------------------------------

Ext.define('BQ.is.Converter', {
    extend: 'Ext.container.Container', //'Ext.panel.Panel',
    alias: 'widget.bqimageconverter',
    requires: ['Ext.toolbar.Toolbar', 'Ext.tip.QuickTipManager', 'Ext.tip.QuickTip'],
    layout: {
        type: 'vbox',
        align : 'stretch',
        pack  : 'start',
    },
    //defaults: { border: 0, },
    cls: 'iconverter',

    initComponent : function() {

        this.dims = {
            w: parseInt(this.phys.x),
            h: parseInt(this.phys.y),
            z: parseInt(this.phys.z),
            t: parseInt(this.phys.t),
            c: parseInt(this.phys.ch),
            d: parseInt(this.phys.pixel_depth),
        };

        this.formatsstore = Ext.create('Ext.data.Store', {
            fields: ['name', 'fullname'],
            //data : items
        });

        this.services = [];
        var s = undefined;
        for (var i=0; s=BQ.is.services[i]; ++i) {
            this.services.push(Ext.create(s, {
                image : this.image,
                phys  : this.phys,
                slice : this.slice,
                view  : this.view,
                listeners: {
                    scope: this,
                    changed: this.onchange,
                },
            }));
        }

        this.items = [{
            //xtype: 'tabpanel',
            xtype: 'container',
            layout: {
                type: 'accordion',
                titleCollapse: true,
            },
            items: this.services,
            flex: 1,
        },{
            xtype: 'container',
            cls: 'converterbuttons',
            layout: {
                type: 'vbox',
                align : 'stretch',
                pack  : 'start',
            },
            items: [{
                xtype: 'combobox',
                itemId: 'format_combo',
                fieldLabel: 'Format',
                store: this.formatsstore,
                queryMode: 'local',
                displayField: 'fullname',
                valueField: 'name',
                forceSelection: true,
                editable: false,
                value: 'OME-TIFF',
                listeners:{
                    scope: this,
                    //'select': cb,
                },
            }, {
                itemId: 'download_btn',
                xtype:'button',
                text: 'Convert',
                scale: 'large',
                cls: 'convert',
                //iconCls: 'converter',
                tooltip: 'Convert and download',
                scope: this,
                handler: this.convert,
            }],
        }];

        this.callParent();
    },

    // private
    afterRender : function() {
        this.callParent();

        this.setLoading('Fetching format info');
        Ext.Ajax.request({
            url: '/image_service/formats',
            callback: function(opts, succsess, response) {
                if (response.status>=400)
                    this.onError();
                else
                    this.onFormats(response.responseXML);
            },
            scope: this,
        });
    },

    onError : function() {
        this.setLoading(false);
        BQ.ui.error('Problem fetching image formats information');
    },

    onFormats : function(xml) {
        this.setLoading(false);
        this.formats = [];
        this.formats_index = {};
        //var codecs = BQ.util.xpath_nodes(xml, '//format[@name != "bioformats"]/codec');
        var codecs = BQ.util.xpath_nodes(xml, '//format/codec');
        var c=undefined;
        for (var i=0; c=codecs[i]; ++i) {
            var name = BQ.util.xpath_nodes(c, '@name')[0].value;
            //if (name==='bioformats') continue;
            var fullname   = BQ.util.xpath_nodes(c, 'tag[@name="fullname"]/@value')[0].value;
            var support    = BQ.util.xpath_nodes(c, 'tag[@name="support"]/@value')[0].value;
            var extensions = BQ.util.xpath_nodes(c, 'tag[@name="extensions"]/@value')[0].value;
            var maxsamples = BQ.util.xpath_nodes(c, 'tag[@name="samples_per_pixel_minmax"]/@value')[0].value;
            var maxbits    = BQ.util.xpath_nodes(c, 'tag[@name="bits_per_sample_minmax"]/@value')[0].value;

            if (support.indexOf('writing')>=0)
            var ix = this.formats.push({
                name      : name,
                fullname  : fullname,
                multipage : support.indexOf('multipage')>=0,
                extensions: extensions.split(','),
                maxsamples: parseInt(maxsamples.split(',')[1]),
                maxbits   : parseInt(maxbits.split(',')[1]),
            });
            this.formats_index[name] = this.formats[ix-1];
        } // for codecs

        this.onchange(true);
    },

    onchange: function(initial) {
        var dims = Ext.clone(this.dims);
        var s=undefined;
        for (var i=0; s=this.services[i]; ++i)
            if (s.isEnabeled())
                dims = s.updateDims(dims);

        if (this.dims_current &&
            this.dims_current.w === dims.w &&
            this.dims_current.h === dims.h &&
            this.dims_current.z === dims.z &&
            this.dims_current.t === dims.t &&
            this.dims_current.c === dims.c &&
            this.dims_current.d === dims.d
        ) return;

        this.dims_current = Ext.clone(dims);
        var format_name = this.queryById('format_combo').getValue() || 'OME-TIFF';

        var fformats = [];
        var index = {};
        var f = undefined;
        for (var i=0; f=this.formats[i]; ++i) {
            if (dims.z*dims.t>1 && !f.multipage) continue;
            if (f.maxsamples>0 && dims.c>f.maxsamples) continue;
            if (f.maxbits>0 && dims.d>f.maxbits) continue;
            var ix = fformats.push(f);
            index[f.name] = ix-1;
        }

        if (fformats.length !== this.formats.length && initial) {
            BQ.ui.tip(this.queryById('format_combo').getId(),
                'Available formats list is reduced to support current image, change conversion to see more...',
                {anchor:'left',}
            );
        }

        if (fformats.length === this.formats.length && !initial) return;
        if (!(format_name in index)) {
            if (!initial)
                BQ.ui.tip(this.queryById('format_combo').getId(),
                    'Selected format can\'t save current image geometry, changed to OME-TIFF',
                    {anchor:'left',}
                );
            format_name = 'OME-TIFF';
        }

        this.formatsstore.loadData(fformats);
        this.queryById('format_combo').setValue(format_name);
    },

    convert: function() {
        var cmd=[];
        var s=undefined;
        for (var i=0; s=this.services[i]; ++i) {
            var op = s.getOperation();
            if (s.isEnabeled() && op)
                cmd.push(op);
        }
        cmd.push('format='+this.queryById('format_combo').getValue()+',stream');
        var command = cmd.join('&');
        var url = '/image_service/images/'+this.image.resource_uniq+'?'+command;
        window.open(url);
    },


});

