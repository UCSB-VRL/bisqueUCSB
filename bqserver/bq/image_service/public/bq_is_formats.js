/*
<codec index="0" name="JPEG">
    <tag name="support" value="reading"/>
    <tag name="support" value="writing"/>
    <tag name="support" value="reading metadata"/>
    <tag name="extensions" value="jpg|jpeg|jpe|jif|jfif"/>
</codec>
*/

Ext.define('BQ.model.Formats', {
    extend : 'Ext.data.Model',
    fields : [{
        name: 'Name',
        mapping: '@name'
    }, {
        name: 'Reading',
        mapping: "tag[@name='support']/@value",
        convert: function(v, record) {
            return v.indexOf('reading')!==-1?'yes':'';
        },
    }, {
        name: 'Writing',
        mapping: "tag[@name='support']/@value",
        convert: function(v, record) {
            return v.indexOf('writing')!==-1?'yes':'';
        },
    }, {
        name: 'Metadata',
        mapping: "tag[@name='support']/@value",
        convert: function(v, record) {
            return v.indexOf('metadata')!==-1?'yes':'';
        },
    }, {
        name: 'Extensions',
        mapping: "tag[@name='extensions']/@value",
    }, {
        name: 'Source',
        convert: function(v, record) { // dima: incompatible with extjs5
            var r = BQ.util.xpath_string(record.raw.parentNode, '@name');
            var v = BQ.util.xpath_string(record.raw.parentNode, '@version');
            return r + ' ' + v;
        },
    }],
    proxy : {
        limitParam : undefined,
        pageParam: undefined,
        startParam: undefined,
        noCache: false,
        type: 'ajax',
        url : '/image_service/formats',
        reader : {
            type :  'xml',
            root :  'resource', // ext4
            //rootProperty : 'resource', // ext5
            record: 'codec',
        }
    },

});

Ext.define('BQ.is.Formats', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.bq-formats',
    requires: ['Ext.toolbar.Toolbar', 'Ext.tip.QuickTipManager', 'Ext.tip.QuickTip', 'Ext.data.*', 'Ext.grid.*'],
    layout: 'fit',

    initComponent : function() {
        this.store = new Ext.data.Store( {
            model : 'BQ.model.Formats',
            autoLoad : false,
            autoSync : false,
        });

        //--------------------------------------------------------------------------------------
        // items
        //--------------------------------------------------------------------------------------
        this.items = [{
            xtype: 'grid',
            store: this.store,
            border: 0,
            columns: [
                {text: "Name", flex: 2, dataIndex: 'Name', sortable: true},
                {text: "Reading", width: 60, dataIndex: 'Reading', sortable: true},
                {text: "Writing", width: 60, dataIndex: 'Writing', sortable: true},
                //{text: "Metadata", width: 100, dataIndex: 'Metadata', sortable: true},
                {text: "Extensions", flex: 1, dataIndex: 'Extensions', sortable: true},
                {text: "Source", width: 100, dataIndex: 'Source', sortable: true},
            ],
            viewConfig: {
                stripeRows: true,
                forceFit: true
            },
        }];

        this.callParent();

    },

    afterRender : function() {
        this.callParent();
        this.store.load();
    },

});

//--------------------------------------------------------------------------------------
// Function to fetch formats list
//--------------------------------------------------------------------------------------

Ext.namespace('BQ.is');

BQ.is.FORMAT_CONFIDENCE = {
    'imgcnv'     : 1.0,
    'imaris'     : 0.9,
    'openslide'  : 0.8,
    'bioformats' : 0.5,
};

BQ.is.fetchFormatsList = function( cb_success, cb_error ) {
    Ext.Ajax.request({
        url: '/image_service/formats',
        callback: function(opts, succsess, response) {
            if (response.status>=400)
                if (cb_error)
                    cb_error(response);
                else
                    BQ.ui.error(response.responseText);
            else
                BQ.is.parseFormatsList(response.responseXML, cb_success);
        },
        scope: this,
        disableCaching: false,
        listeners: {
            scope: this,
            //beforerequest   : function() { this.setLoading('Loading images...'); },
            //requestcomplete : function() { this.setLoading(false); },
            requestexception: cb_error,
        },
    });
};

BQ.is.parseFormatsList = function( xml, cb_success ) {
    var formats = {};
    var fmts = BQ.util.xpath_nodes(xml, 'resource/format');
    var f = undefined;
    for (var i=0; (f=fmts[i]); ++i) {
        var fmt = f.getAttribute('name');
        var cdcs = BQ.util.xpath_nodes(f, 'codec');
        var c = undefined;
        for (var j=0; (c=cdcs[j]); ++j) {
            var name = c.getAttribute('name');
            var codec = { name: name, format: fmt, confidence: BQ.is.FORMAT_CONFIDENCE[fmt], };
            var tags = BQ.util.xpath_nodes(c, 'tag');
            var t = undefined;
            for (var k=0; (t=tags[k]); ++k) {
                codec[t.getAttribute('name')] = t.getAttribute('value');
            }
            formats[fmt+':'+name] = codec;
        }
    }
    if (cb_success) cb_success(formats);
};

