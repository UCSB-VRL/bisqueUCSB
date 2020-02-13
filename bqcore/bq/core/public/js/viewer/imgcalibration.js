

Ext.define('BQ.Calibration.StackCount', {
    extend: 'Ext.form.NumberField',
    dimension: 'z',
    minValue: 0,
    margins: '10px',
    originalMetaDoc: undefined,
    initComponent: function(config) {
        var me = this;
        var config = config || {};
        Ext.apply(me, {
            fieldLabel: this.dimension.toUpperCase()+' Count',
            dimsXpath: '//tag[@name="image_num_'+this.dimension.toLowerCase()+'"]',
        });
        this.callParent([config]);
    },
    setValues: function(xmlDoc) {
        var value = BQ.util.xpath_string(xmlDoc, this.dimsXpath+'/@value');
        value = parseInt(value,10);
        this.originalMetaDoc = xmlDoc; //save document
        this.setValue(value||0);
    },
    fromXmlNode: function(imageMeta) {
        //check to see if tag exists
        var oldValue = BQ.util.xpath_string(this.originalMetaDoc, this.dimsXpath+'/@value');
        oldValue = parseInt(oldValue,10);
        var metaValue = BQ.util.xpath_string(imageMeta, this.dimsXpath+'/@value');
        metaValue = parseInt(metaValue,10);
        if (metaValue || oldValue!=this.value) {
            if (this.value) { // if no value delete from metadata
                var tag = document.createElement('tag');
                tag.setAttribute('name', 'image_num_'+this.dimension.toLowerCase());
                tag.setAttribute('value', this.value);
                return tag
            }
        }
    },

    changed: function() {
        var oldValue = BQ.util.xpath_string(this.originalMetaDoc, this.dimsXpath+'/@value')||0;
        oldValue = parseInt(oldValue,10);
        return oldValue!=this.value
    },
});

Ext.define('BQ.Calibration.ChannelOrder', {
    extend: 'Ext.form.Text',
    fieldLabel: 'Dimension Order',
    originalMetaDoc: undefined,
    initComponent: function(config) {
        var me = this;
        var config = config || {};
        Ext.apply(me, {
            dimsXpath: '//tag[@name="dimension"]',
        });
        this.callParent([config]);
    },
    setValues: function(xmlDoc) {
        var value = BQ.util.xpath_string(xmlDoc, this.dimsXpath+'/@value');
        value = parseInt(value,10);
        this.originalMetaDoc = xmlDoc; //save document
        this.setValue(value||'');
    },
    fromXmlNode: function(imageMeta) {
        //check to see if tag exists
        var oldValue = BQ.util.xpath_string(this.originalMetaDoc, this.dimsXpath+'/@value');
        oldValue = parseInt(oldValue,10);
        var metaValue = BQ.util.xpath_string(imageMeta, this.dimsXpath+'/@value');
        metaValue = parseInt(metaValue,10);
        if (metaValue || oldValue!=this.value) {
            if (this.value) { // if no value delete from metadata
                var tag = document.createElement('tag');
                tag.setAttribute('name', 'dimension');
                tag.setAttribute('value', this.value);
                return tag;
            }
        }
    },

    changed: function() {
        var oldValue = BQ.util.xpath_string(this.originalMetaDoc, this.dimsXpath+'/@value')||'';
        oldValue = parseInt(oldValue,10);
        return oldValue!=this.value
    },
})

Ext.define('BQ.Calibration.PixelResolution', {
    alias: 'widget.bq-calibration-pixel-resolution',
    extend: 'Ext.form.Panel',
    componentCls: 'bq-pixel-resolution',

    dimension: 'x',
    width: '100%',
    border: false,
    layout: {
        type: 'hbox',
        //pack: 'center',
    },
    initComponent: function() {
        var d = this.dimension;
        this.items = [{
            text: 'Pixel Resolution '+d,
            xtype: 'label',
            margins: '0 10px 0 0',
        }, {
            name: 'pixel_resolution_'+d,
            xtype: 'numberfield',
            decimalPrecision : 6,
            margins: '0 10px 0 0',
        }, {
            name: 'pixel_resolution_unit_'+d,
            xtype:'combobox',
            store: Object.keys(BQ.api.Phys.units),
            margins: '0 10px 0 0',
        }];
        Ext.apply(this, {
            //fieldLabel: this.dimension.toUpperCase()+'-Stack Count',
            resolutionXpath: '//tag[@name="pixel_resolution_'+d+'"]',
            unitsXpath: '//tag[@name="pixel_resolution_unit_'+d+'"]',
            bodyStyle: 'margin: "center"',
            //items: items,
        });
        this.callParent(arguments);
    },
    setValues: function(xmlDoc) {
        this.originalMetaDoc = xmlDoc; //save document
        var resolutionValue = BQ.util.xpath_string(xmlDoc, this.resolutionXpath+'/@value');
        resolutionValue = parseFloat(resolutionValue);
        var resolutionForm = this.getForm().findField('pixel_resolution_'+this.dimension.toLowerCase());
        resolutionForm.setValue(resolutionValue||'');

        var unitValue = BQ.util.xpath_string(xmlDoc, this.unitsXpath+'/@value');
        var unitForm = this.getForm().findField('pixel_resolution_unit_'+this.dimension.toLowerCase());
        unitForm.setValue(unitValue||'');
    },
    fromXmlNode: function(imageMeta) {
        //check to see if tag exists
        var tagList = [];
        var unitForm = this.getForm().findField('pixel_resolution_'+this.dimension);
        var value = unitForm.getValue();
        var oldValue = BQ.util.xpath_string(this.originalMetaDoc, this.resolutionXpath+'/@value');
        oldValue = parseFloat(oldValue);
        var metaValue = BQ.util.xpath_string(imageMeta, this.resolutionXpath+'/@value');
        metaValue = parseFloat(metaValue);
        if (metaValue || oldValue!=value) {
            if (value) {
                var tag = document.createElement('tag');
                tag.setAttribute('name', 'pixel_resolution_'+this.dimension.toLowerCase());
                tag.setAttribute('type', 'number');
                tag.setAttribute('value', value);
                tagList.push(tag);
            }
        }
        var unitForm = this.getForm().findField('pixel_resolution_unit_'+this.dimension);
        var value = unitForm.getValue();
        var oldValue = BQ.util.xpath_string(this.originalMetaDoc, this.unitsXpath+'/@value')
        var metaValue = BQ.util.xpath_string(imageMeta, this.unitsXpath+'/@value');
        if (metaValue || oldValue!=value) {
            if (value) {
                var tag = document.createElement('tag');
                tag.setAttribute('name', 'pixel_resolution_unit_'+this.dimension.toLowerCase());
                tag.setAttribute('value', value);
                tagList.push(tag);
            }
        }
        return tagList;
    },

    changed: function() {
        var unitForm = this.getForm().findField('pixel_resolution_'+this.dimension);
        var value = unitForm.getValue()||'';
        var oldValue = BQ.util.xpath_string(this.originalMetaDoc, this.resolutionXpath+'/@value')||'';
        oldValue = parseFloat(oldValue);
        var changedFlag = oldValue!=value;

        var unitForm = this.getForm().findField('pixel_resolution_unit_'+this.dimension);
        var value = unitForm.getValue()||'';
        var oldValue = BQ.util.xpath_string(this.originalMetaDoc, this.unitsXpath+'/@value')||'';
        var changedFlag = oldValue!=value || changedFlag;

        return changedFlag;
    },
});

Ext.define('BQ.Calibration.ChannelPanel', {
    //extend: 'Ext.form.Panel',
    extend: 'Ext.container.Container',
    layout: 'hbox',
    width: '100%',
    channel: 0,
    autoSize: true,
    border: false,
    name: '',
    color: '#000000', //default color
    initComponent: function(config) {
        var me = this;
        var config = config || {};
        var items = [{ //channel number
            text: this.channel,
            xtype: 'label',
            labelAlign: 'right',
            margins: '8px',
            flex: 1,
            style: {
                textAlign: 'center',
            }
            //width: '20%',
        },{ //channel name editor
            value: this.name,
            id: 'channel_'+me.channel+'_name',
            xtype: 'textfield',
            margins: '8px',
            //width: '40%',
            flex: 3,
            listeners: {
                scope: this,
                change: function(field, value) {
                    me.name = value;
                },
            },
        },{
            xtype:'container',
            //width:'100%',
            height: '100%',
            flex: 5,
            margin: '0 5 5 0',
            border:false,
            items:[{
                //width: '20%',
                //margins: '10px',
                id: 'channel_color_'+me.channel,
                xtype: 'colorfield',
                value: this.color.toString().replace('#', ''),
                listeners: {
                    scope: this,
                    change: function(field, value) {
                        var color = field.getValue();
                        me.color = '#'+color;
                    },
                },
            }],
        }];
        Ext.apply(me, {
            items: items,
        });
        this.callParent([config]);
    },

    setValues: function(xmlDoc) {
        this.originalMetaDoc = xmlDoc; //save document
        if (this.channel != undefined){
            var nameXpath = '//tag[@name="channel_'+this.channel+'_name"]/@value';
            var nameValue = BQ.util.xpath_string(xmlDoc, nameXpath)||'';
            if (nameValue != undefined) { //add name if name found
                this.name = nameValue;
                var channel_name = this.queryById('channel_'+this.channel+'_name')
                channel_name.setValue(this.name)
            }
            var colorXpath = '//tag[@name="channel_color_'+this.channel+'"]/@value';
            var colorValue = BQ.util.xpath_string(xmlDoc, colorXpath)||'0,0,0';
            if (colorValue) { //add color if color found
                //convert to hex
                var colors = colorValue.match(/(\d*),(\d*),(\d*)/); //return the value only
                if (colors) {
                    var r = parseInt(colors[1]);
                    var g = parseInt(colors[2]);
                    var b = parseInt(colors[3]);
                    var c = Ext.draw.Color.create(r, g, b);
                    this.color = c.toString();
                    color = this.color.replace('#', '');
                    var colorPicker = this.queryById('channel_color_'+this.channel); //color picker is the 3 item, change to look up
                    if (colorPicker) colorPicker.onColorSelected(null, color);
                } else {
                    BQ.ui.error('Cannot parse the color value in the metadata');
                }
            }
        }

    },

    fromXmlNode: function(imageMeta) {
        var tagList = [];
        var nameXpath = '//tag[@name="channel_'+this.channel+'_name"]/@value';
        var oldValue = BQ.util.xpath_string(this.originalMetaDoc, nameXpath);
        var metaValue = BQ.util.xpath_number(imageMeta, nameXpath);
        //if (metaValue || oldValue!=this.name) {
        if (this.name) {
            var tag = document.createElement('tag');
            tag.setAttribute('name', 'channel_'+this.channel+'_name');
            tag.setAttribute('value', this.name);
            tagList.push(tag);
        }
        //}
        var color = Ext.draw.Color.fromString(this.color);
        var color = color.r+','+color.g+','+color.b;
        var colorXpath = '//tag[@name="channel_color_'+this.channel+'"]/@value';
        var oldValue = BQ.util.xpath_string(this.originalMetaDoc, colorXpath);
        var metaValue = BQ.util.xpath_number(imageMeta, colorXpath);
        //if (metaValue || oldValue!=color) {
        if (color) {
            var tag = document.createElement('tag');
            tag.setAttribute('name', 'channel_color_'+this.channel);
            tag.setAttribute('value', color);
            tagList.push(tag);
        }
        //}
        return tagList
    },

    changed: function() {
        var nameXpath = '//tag[@name="channel_'+this.channel+'_name"]/@value';
        var oldValue = BQ.util.xpath_string(this.originalMetaDoc, nameXpath)||'';
        var changedFlag = oldValue!=this.name

        var colorXpath = '//tag[@name="channel_color_'+this.channel+'"]/@value';
        var oldValue = BQ.util.xpath_string(this.originalMetaDoc, colorXpath)||'0,0,0';
        var color = Ext.draw.Color.fromString(this.color);
        var color = color.r+','+color.g+','+color.b;
        var changedFlag = oldValue!=color || changedFlag;

        return changedFlag;
    },
});

Ext.define('BQ.Calibration.ChannelOrganizer', {
    extend: 'Ext.container.Container',
    layout: 'vbox',
    channelNum: 0,
    border: false,
    chStore: [],
    //autoScroll: true,
    //height: '500px',
    width: '100%',
    margin: '10px',

    initComponent: function(config) {
        var me = this;
        var config = config || {};
        var items = [];
        Ext.apply(me, {
            items: items,
        });
        this.callParent([config]);
    },

    setValues: function(xmlDoc) { //resets the entire panel
        this.originalMetaDoc = xmlDoc; //save document
        this.chStore = []; //resets chStore
        var i;
        while(i = this.items.first()){ //clear old panel
            this.remove(i, true);
        }

        this.add({ //title
            width: '100%',
            xtype: 'container',
            layout: 'hbox',
            border: false,
            items: [{
                xtype: 'label',
                text: 'Number',
                flex: 1,
                style: {
                    textAlign: 'center',
                    fontWeight: 'bold',
                }
            }, {
                xtype: 'label',
                text: 'Name',
                flex: 3,
                style: {
                    textAlign: 'center',
                    fontWeight: 'bold',
                }
            }, {
                xtype: 'label',
                text: 'Color',
                flex: 5,
                style: {
                    textAlign: 'center',
                    fontWeight: 'bold',
                }
            }]
        });

        var channelNum = this.channelNum>50? 50 : this.channelNum;
        if (this.channelNum>50) BQ.ui.notification('Channel Editor limited at 50');
        for (var c=0; c<channelNum; c++) {
            var channelPanel = Ext.create('BQ.Calibration.ChannelPanel', {
                channel: c.toString(),
            });
            this.add(channelPanel)
            channelPanel.setValues(xmlDoc)
            this.chStore.push(channelPanel)
        }
        this.doLayout();
    },

    fromXmlNode: function(imageMeta) {
        var tagList = [];
        for (var c=0; c<this.chStore.length; c++) {
            tagList = tagList.concat(this.chStore[c].fromXmlNode(imageMeta));
        }
        return tagList;
    },

    changed: function() {
        var changedFlag = false;
        for (var c=0; c<this.chStore.length; c++) {
            var changedFlag = this.chStore[c].changed()||changedFlag;
        }
        return changedFlag;
    },

    setChannelNum: function(value, xmlDoc) {
        this.channelNum = value;
        this.setValues(xmlDoc);
    },
});


Ext.define('BQ.viewer.Calibration', {
    extend: 'Ext.window.Window',
    layout: 'hbox',
    title: 'Image Calibrator',
    bodyStyle: 'background-color:#FFFFFF',
    image_resource: '', //data_service url (ex. '/data_service/($id)')
    //viewer: {}, //required
    buttonAlign: 'center',

    initComponent: function(config) {
        var config = config || {};
        var items = [];
        var me = this;

        fbar = [{
            scale: 'large',
            xtype: 'button',
            margin: '0 8 0 8',
            text: 'Save',
            handler: me.getImageMetaTag.bind(me, me.updateImageMeta),
        }, {
            scale: 'large',
            margin: '0 8 0 8',
            xtype: 'button',
            text: 'Reload',
            handler: function() {
                //request for image meta
                var url = me.image_resource.replace('/data_service/', '/image_service/');
                Ext.Ajax.request({
                    method: 'GET',
                    disableCaching: false,
                    headers: { 'Content-Type': 'text/xml' },
                    url: url+'?meta',
                    success: function(response) {
                        var xml = response.responseXML;
                        var viewer = this.imageCalibForm.formComponents['imgViewer'];
                        var gobs = viewer.getGobjects();
                        while (gobs.length>0) { //remove all existing gobs on the viewer
                            viewer.viewer.delete_gobjects(gobs);
                        }
                        this.setFormValues(xml);
                    },
                    failure: function(response) {
                        BQ.ui.error('Image Meta failed to be servered for this resource from image service!');
                    },
                    scope: me,
                });
            },
        }, {
            scale: 'large',
            margin: '0 8 0 8',
            xtype: 'button',
            text: 'Set Default',
            handler: me.getImageMetaTag.bind(me, me.deleteImageMeta),
        }],

        this.imageMetaForm = Ext.create('Ext.form.Panel', {
            height : '100%',
            width : '50%',
            margin: '10px',
            border: false,
            autoScroll: true,
            formComponents: {},
            items: [],
            layout: {
                //align: 'center',
                type: 'vbox',
                //align: 'stretch',
            },
            defaults: {
                margins: '5 0 5 0',
                type: 'combobox',
            },
            scope: this,
        });

        //request for image meta
        var url = this.image_resource.replace('/data_service/', '/image_service/');
        Ext.Ajax.request({
            method: 'GET',
            disableCaching: false,
            headers: { 'Content-Type': 'text/xml' },
            url: url+'?meta',
            success: function(response) {
                var xml = response.responseXML;
                this.constructImageMetaForm(xml);
            },
            failure: function(response) {
                BQ.ui.error('Image Meta failed to be servered for this resource from image service!');
            },
            scope: this,
        });

        //set the scales of the lines and return the pixel scaling factor
        this.imageCalibForm = Ext.create('Ext.form.Panel', {
            //flex: 2,
            height:'100%',
            width : '50%',
            margin: '10px',
            formComponents: {},
            items: [],
            layout: {
                //align: 'center',
                type: 'vbox',
                //align: 'stretch',
            },
            bodyStyle: {
                borderColor: '#FFFFFF'
            },
            padding: 0,
            border: 0,
            //margin: '10px',
            defaults: {
                margins: '5px',
            },
        });

        items.push(this.imageMetaForm);
        items.push(this.imageCalibForm);

        Ext.apply(me, {
            fbar: fbar,
            items: items,
        });
        this.callParent([config]);
        this.constructImageCalibrationForm()
    },

    constructImageCalibrationForm: function() {
        var me = this;

        this.imageCalibForm.add({
            xtype: 'box',
            html: '<h2>Image Resolution Calibration</h2><p>A fast and easy way to calibrate pixel resolution when the values are not present.</p>',
            width: '100%',
            cls: 'imgmetaeditor',
            padding: '0px',
            margins:'0px',
        });

        this.imageCalibForm.formComponents['reference_length'] = Ext.createWidget('numberfield',{
            fieldLabel: 'Reference Length',
            //xtype: 'numberfield',

            decimalPrecision : 6,
            margin: '10px',
            minValue: 0,
            listeners: {
                scope: this,
                change: this.updateReferenceLength,
            },
        });

        this.imageCalibForm.add({
            border: false,
            layout: {
                align: 'middle',
                type: 'hbox',
                //pack: 'justify'
                //pack: 'center',
            },
            width: '100%',
            padding: '0px',
            margins:'0px',
            items: [
                this.imageCalibForm.formComponents['reference_length'],
                {
                    xtype: 'box',
                    html: '<p> Set the reference length and to a known object length in the image.</p>',
                    //width: '100%',
                    flex: 1,
                    cls: 'imgmetaeditor',
                },
            ],
        });

        this.imageCalibForm.add({
            xtype: 'box',
            html: '<p>Select the gobject line in the image viewer and draw a line spanning the reference length in the image. The average of the lines drawn will update the x-y pixel resolutions.</p>',
            width: '100%',
            cls: 'imgmetaeditor',
            padding: 0,
            margins:'0px',
        });

        this.imageCalibForm.formComponents['imgViewer'] = this.imageCalibForm.add(
            Ext.create('BQ.viewer.Image',{
                width:'100%',
                flex: 1,
                resource: me.image_resource,
                parameters: {
                    onlyedit: true,
                    nosave: true,
                    editprimitives: 'line',
                    semantic_types: false,
                },

                listeners: {
                    //'afterPhys': me.updateReferenceLength.bind(me),
                    'changed': me.updateReferenceLength.bind(me),
                    'delete': me.updateReferenceLength.bind(me),
                    'moveend': me.updateReferenceLength.bind(me),
                },
            })
        );
    },

    constructImageMetaForm: function(imMetaXML) {
        //add components
        var me = this;

        this.imageMetaForm.add({
            xtype: 'box',
            html: '<h2>Image Calibrator</h2><p>Welcome to the image calibrator. Edit the fields that need to be corrected and update the metadata by selecting Save. If a field is left empty or 0 the original metadata will be applied.</p>',
            width: '100%',
            cls: 'imgmetaeditor',
            padding: '0px',
            margins:'0px',
        });


        //stack count panel
        this.imageMetaForm.formComponents['image_num_z'] = this.imageMetaForm.add(
            Ext.create('BQ.Calibration.StackCount',{
                dimension: 'z',
            })
        );

        this.imageMetaForm.formComponents['image_num_t'] = this.imageMetaForm.add(
            Ext.create('BQ.Calibration.StackCount',{
                dimension: 't',
            })
        );

        this.imageMetaForm.formComponents['image_num_c'] = this.imageMetaForm.add(
            Ext.create('BQ.Calibration.StackCount',{
                dimension: 'c',
            })
        );

        /*
        this.imageMetaForm.formComponents['dimension'] = this.imageMetaForm.add(
            Ext.create('BQ.Calibration.ChannelOrder')
        );
        */

        //dimensions panel
        this.imageMetaForm.formComponents['pixel_resolution_x'] = this.imageMetaForm.add(
            Ext.create('BQ.Calibration.PixelResolution',{
                dimension: 'x',
            })
        );

        this.imageMetaForm.formComponents['pixel_resolution_y'] = this.imageMetaForm.add(
            Ext.create('BQ.Calibration.PixelResolution',{
                dimension: 'y',
            })
        );

        this.imageMetaForm.formComponents['pixel_resolution_z'] = this.imageMetaForm.add(
            Ext.create('BQ.Calibration.PixelResolution',{
                dimension: 'z',
            })
        );

        this.imageMetaForm.formComponents['pixel_resolution_t'] = this.imageMetaForm.add(
            Ext.create('BQ.Calibration.PixelResolution',{
                dimension: 't',
            })
        );

        //channel panel
        this.imageMetaForm.add({
            xtype: 'box',
            html: '<h2>Channel Meta</h2><p>C Count will determine the channels shown below.</p>',
            width: '100%',
            cls: 'imgmetaeditor',
            padding: '0px',
            margins:'0px',
        });

        this.imageMetaForm.formComponents['channels'] = this.imageMetaForm.add(
            Ext.create('BQ.Calibration.ChannelOrganizer')
        );

        //adding listeners to components
        this.imageMetaForm.formComponents['image_num_c'].on('change', function() {
            //var image_num_c_value = me.value;
            //set back to default
            var value = this.value;
            if (me.imageMetaForm.formComponents['image_num_c'].event_timeout) clearTimeout (me.imageMetaForm.formComponents['image_num_c'].event_timeout);
            me.imageMetaForm.formComponents['image_num_c'].event_timeout = setTimeout(function(){
                me.imageMetaForm.formComponents['channels'].setChannelNum(value, imMetaXML)
            }, 250);
        });


        //populate values
        this.setFormValues(imMetaXML);
    },

    updateReferenceLength: function() {
        var me = this;
        var gobjects = this.imageCalibForm.formComponents['imgViewer'].getGobjects();
        var estimated = this.imageCalibForm.formComponents['reference_length'].getValue();

        var xform = me.imageMetaForm.formComponents['pixel_resolution_x'].getForm().findField('pixel_resolution_x');
        var yform = me.imageMetaForm.formComponents['pixel_resolution_y'].getForm().findField('pixel_resolution_y');
        if (estimated && gobjects.length>0) {
            var lengths = [];
            for (var g=0; g<gobjects.length; g++) {
                //distance of gobjcts times scalar
                var x1 = gobjects[g].vertices[0].x;
                var x2 = gobjects[g].vertices[1].x;

                var y1 = gobjects[g].vertices[0].y;
                var y2 = gobjects[g].vertices[1].y;
                lengths.push(Math.sqrt(Math.pow(x1-x2,2)+Math.pow(y1-y2,2)));
            }
            var avg_lengths = 0;
            for (var i=0; i<lengths.length; i++) {
                 avg_lengths += lengths[i];
            }
            avg_lengths = avg_lengths/lengths.length;
            //average all the distances together

            xform.setValue(estimated/avg_lengths);
            yform.setValue(estimated/avg_lengths);
        } else {
            if (!estimated) { //if no reference length is added but a gobject is selected
                var referenceLength = this.imageCalibForm.formComponents['reference_length'];
                BQ.ui.tip(referenceLength.getId(), 'You need to set a reference length!', {
                    anchor:'left',
                    color: 'red',
                });
                referenceLength.getEl().highlight('ff0000', {duration:250, iterations:6}); //suppose to flash red
                this.imageCalibForm.formComponents['reference_length'].markInvalid('Requires a reference length'); //underline because highlight it is not working
            }
        }
    },

    setFormValues: function(imMetaXML) {
        if (this.imageMetaForm.formComponents) {
            for (var k in this.imageMetaForm.formComponents) {
                this.imageMetaForm.formComponents[k].setValues(imMetaXML);
            }
        }
    },


    getImageMetaTag: function(cb) {
        var me = this;
        //request for image meta
        Ext.Ajax.request({
            method: 'GET',
            disableCaching :false,
            headers: { 'Content-Type': 'text/xml' },
            url: this.image_resource+'/tag?name=image_meta&view=full',
            params: {view:'full'},
            success: function(response) {
                var xml = response.responseXML;
                cb.apply(this,[xml]);
            },
            failure: function(response) {
                BQ.ui.error('Image Meta failed to be servered for this resource!');
            },
            scope: this,
        });
    },

    //POST all values back to data_service
    updateImageMeta: function(imMetaXML) {
        //image meta check for multi tiff to put the correct tags
        //from xml document to post
        var me = this;
        var image_meta = document.createElement('tag');
        image_meta.setAttribute('name','image_meta')
        image_meta.setAttribute('type','image_meta')
        var uri = BQ.util.xpath_string(imMetaXML, '//tag[@name="image_meta"]/@uri');
        if (uri) { //overiding the current image_meta tag
            image_meta.setAttribute('uri', uri);
            var method = 'PUT';
        }
        var changedFlag = false; //a flag that keeps track if any changes had occurred to the image meta document
        if (this.imageMetaForm.formComponents) {
            for (var k in this.imageMetaForm.formComponents) {
                var tag = this.imageMetaForm.formComponents[k].fromXmlNode(imMetaXML);
                var changedFlag = this.imageMetaForm.formComponents[k].changed() || changedFlag; //check for changes
                if(tag instanceof Array) { //appends lists of tags to the document
                    for (var t=0; t<tag.length; t++) {
                        if (tag[t] instanceof Element) image_meta.appendChild(tag[t]);
                    }
                } else if (tag instanceof Element) image_meta.appendChild(tag);
            }
        }
        if (!changedFlag) {
            BQ.ui.notification('Nothing updated.');
            return
        }

        //since nothing is in image meta the tag is removed
        if (image_meta.childElementCount<1) {
            me.deleteImageMeta(imMetaXML); //remove image meta
            return;
        }

        me.setLoading('Setting Metadata')
        //post to image meta
        Ext.Ajax.request({
            method: method||'POST',
            disableCaching: false,
            headers: {'Content-Type': 'text/xml'},
            url: uri||this.image_resource,
            xmlData: image_meta.outerHTML,
            success: function(response) {
                this.cleanImageCache();
            },
            failure: function(response) {
                me.setLoading(false)
                BQ.ui.error('Failed to update Image Meta Tag!');
            },
            scope: this,
        });
    },

    deleteImageMeta: function(imMetaXML) {
        var me = this;
        var uri = BQ.util.xpath_string(imMetaXML, '//tag[@name="image_meta"]/@uri');
        me.setLoading('Deleting Metadata')
        if (uri) {
            Ext.Ajax.request({
                method: 'DELETE',
                disableCaching: false,
                headers: { 'Content-Type': 'text/xml' },
                url: uri,
                success: function(response) {
                    this.cleanImageCache();
                },
                failure: function(response) {
                    me.setLoading(false);
                    BQ.ui.error('Failed to delete Image Meta Tag!');
                },
                scope: this,
            });
        } else {
            BQ.ui.notification('No image meta found.');
            return
        }
    },

    cleanImageCache: function() {
        var me = this,
            url = this.image_resource.replace('/data_service/', '/image_service/');
        Ext.Ajax.request({
            method: 'POST',
            disableCaching: false,
            headers: { 'Content-Type': 'text/xml' },
            url: url+'?cleancache=true',
            success: function(response) {

                // invalidate browser cache of image metadata
                Ext.Ajax.request({
                    method: 'GET',
                    disableCaching: false,
                    headers: { 'Cache-Control': 'no-cache, max-age=0, must-revalidate', 'Pragma': 'no-cache', },
                    //If-Modified-Since: Fri, 12 May 2006 19:03:59 GMT
                    //If-None-Match: W/"50b1c1d4f775c61:df3"

                    url: url+'?meta',
                    scope: this,
                    success: function(response) {
                        me.setLoading(false);
                        Ext.MessageBox.show({
                            title: 'Updated Image Meta Data',
                            msg: 'Updating image metadata was successful! Click ok to reload the page.',
                            buttons: Ext.MessageBox.OK,
                            scope: this,
                            fn: function() {
                                location.reload(true);
                            },
                        });
                    },
                    failure: function(response) {
                        me.setLoading(false);
                        BQ.ui.error('Browser cache has failed to clear!');
                    },
                });

                /*
                me.setLoading(false);
                Ext.MessageBox.show({
                    title: 'Updated Image Meta Data',
                    msg: 'Updating image metadata was successful! Clean browser cache and then click ok to reload the page.',
                    buttons: Ext.MessageBox.OK,
                    scope: this,
                    fn: function() {
                        location.reload(true);
                    },
                });
                */
            },
            failure: function(response) {
                me.setLoading(false);
                BQ.ui.error('Server side cache has failed to clear!');
            },
            scope: this,
        });
    },
});
