
/*
<resource uri="/usage/stats">
    <tag name="number_images" value="466"/>
    <tag name="number_images_user" value="15"/>
    <tag name="number_images_planes" value="17588"/>
    <tag name="number_tags" value="17580"/>
</resource>

<resource uri="/usage/uploads">
<tag name="counts" value="0,0,7,8,15,0,0,2,0,29,38,22,0,8,48,22,0,0,0,0,0,19,9,1,8,61,0,3,0,0,0"/>
<tag name="days" value="2011-10-26 11:36:02.707000,2011-10-25 11:36:02.707000,2011-10-24 11:36:02.707000,2011-10-23 11:36:02.707000,2011-10-22 11:36:02.707000,2011-10-21 11:36:02.707000,2011-10-20 11:36:02.707000,2011-10-19 11:36:02.707000,2011-10-18 11:36:02.707000,2011-10-17 11:36:02.707000,2011-10-16 11:36:02.707000,2011-10-15 11:36:02.707000,2011-10-14 11:36:02.707000,2011-10-13 11:36:02.707000,2011-10-12 11:36:02.707000,2011-10-11 11:36:02.707000,2011-10-10 11:36:02.707000,2011-10-09 11:36:02.707000,2011-10-08 11:36:02.707000,2011-10-07 11:36:02.707000,2011-10-06 11:36:02.707000,2011-10-05 11:36:02.707000,2011-10-04 11:36:02.707000,2011-10-03 11:36:02.707000,2011-10-02 11:36:02.707000,2011-10-01 11:36:02.707000,2011-09-30 11:36:02.707000,2011-09-29 11:36:02.707000,2011-09-28 11:36:02.707000,2011-09-27 11:36:02.707000,2011-09-26 11:36:02.707000"/>
</resource>

<resource uri="/usage/analysis">
<tag name="counts" value="3,1,2,2,1,0,1,0,2,0,3,0,0,1,0,2,0,3,1,0,1,2,3,0,2,3,0,2,0,5,0"/>
<tag name="days" value="2011-10-26 11:36:35.165000,2011-10-25 11:36:35.165000,2011-10-24 11:36:35.165000,2011-10-23 11:36:35.165000,2011-10-22 11:36:35.165000,2011-10-21 11:36:35.165000,2011-10-20 11:36:35.165000,2011-10-19 11:36:35.165000,2011-10-18 11:36:35.165000,2011-10-17 11:36:35.165000,2011-10-16 11:36:35.165000,2011-10-15 11:36:35.165000,2011-10-14 11:36:35.165000,2011-10-13 11:36:35.165000,2011-10-12 11:36:35.165000,2011-10-11 11:36:35.165000,2011-10-10 11:36:35.165000,2011-10-09 11:36:35.165000,2011-10-08 11:36:35.165000,2011-10-07 11:36:35.165000,2011-10-06 11:36:35.165000,2011-10-05 11:36:35.165000,2011-10-04 11:36:35.165000,2011-10-03 11:36:35.165000,2011-10-02 11:36:35.165000,2011-10-01 11:36:35.165000,2011-09-30 11:36:35.165000,2011-09-29 11:36:35.165000,2011-09-28 11:36:35.165000,2011-09-27 11:36:35.165000,2011-09-26 11:36:35.165000"/>
</resource>

*/

Ext.define('BQ.usage.Stats', {
    extend: 'Ext.container.Container',
    alias: 'widget.usagestats',

    layout: 'fit',
    defaults: {border: 0,},
    resource: '/usage/stats',
    tag_titles: {'number_images': 'All Images', 'number_images_user': 'My images', 'number_images_planes': '2D Planes', 'number_tags': 'Tags', 'number_gobs': 'GObjects' },

    initComponent : function() {
        this.callParent();
        this.setLoading('Fetching usage...');
        BQFactory.request({
            uri: this.resource,
            cb: callback(this, 'onStats'),
            errorcb: callback(this, 'onError'),
        });
    },

    onError: function() {
        this.setLoading(false);
    },

    onStats: function(stats) {
        this.setLoading(false);
        var dict = stats.toDict(true);
        var s = '<h2><a href="/usage/">Usage statistics</a></h2>';
        for (var i in this.tag_titles) {
            if (i in dict)
                s += '<li>'+this.tag_titles[i]+': '+dict[i]+'</li>';
        }
        this.add({html: s});
    },

});

Ext.define('BQ.usage.Uploads', {
    extend: 'Ext.container.Container',
    alias: 'widget.uploadstats',
    requires: ['Ext.chart.*', 'Ext.layout.container.Fit'],

    heading: 'Image uploads - daily',
    tip: 'Image uploads in ',
    resource: '/usage/uploads',
    modelName: 'UsageUploads',
    axisFormat: 'n/j',
    tipFormat: 'M d, Y',
    showAxisTitles: true,

    layout: {
        type: 'vbox',
        align : 'stretch',
        pack  : 'start',
    },
    defaults: { border: 0, },

    initComponent : function() {
        this.callParent();
        this.setLoading('Fetching usage...');
        Ext.define(this.modelName, {
            extend: 'Ext.data.Model',
            fields: ['count', 'date'],
        });
        BQFactory.request({
            uri: this.resource,
            cb: callback(this, 'onStats'),
            errorcb: callback(this, 'onError'),
        });
    },

    onError: function() {
        this.setLoading(false);
    },

    onStats: function(stats) {
        this.setLoading(false);
        var dict = stats.toDict(true);
        var counts = dict.counts.split(',');
        var dates  = dict.days.split(',');

        var data = [];
        for (var i=0; i<counts.length; i++) {
            var date = new Date();
            date.setISO8601(dates[i]);
            data.push({ index: i, count: parseFloat(counts[i]), date: date });
        }

        var store = Ext.create('Ext.data.Store', {
            model: 'UsageUploads',
            data: data,
        });

        var axisFormat = this.axisFormat;
        var heading = this.heading;
        var tip = this.tip;
        var tipFormat = this.tipFormat;
        this.chart = Ext.create('Ext.chart.Chart', {
            //animate: true,
            flex: 1,
            store: store,
            shadow: false,
            //theme: 'Yellow',
            axes: [{
                title: this.showAxisTitles?'Count':'',
                type: 'Numeric',
                position: 'left',
                fields: ['count'],
                minimum: 0,
                //grid: true,
                /*grid: {
                    odd: {
                        opacity: 1,
                        fill: '#ddd',
                        stroke: '#bbb',
                        'stroke-width': 0.5
                    }
                }*/
            }, {
                title: this.showAxisTitles?'Date':'',
                type: 'Category',
                position: 'bottom',
                fields: ['date'],
                label: {
                    renderer: function(v) {
                        return Ext.Date.format(v, axisFormat);
                    }
                },
            }],

            series: [{
                type: 'line',
                fill: true,
                smooth: 3,
                highlight: true,
                showMarkers: false,
                selectionTolerance: 3, // dima: this here is a problem, gives wrong items if large, no way to split x and y tolerances
                xField: 'date',
                yField: 'count',

                style: {
                    stroke: 'rgb(234, 102, 17)',
                    fill: 'rgb(234, 102, 17)',
                    lineWidth: 2,
                    //opacity: 0.86,
                },
                tips: {
                  trackMouse: true,
                  anchor: 'bottom',
                  width: 300,
                  //height: 28,
                  renderer: function(storeItem, item) {
                      this.setTitle( storeItem.get('count') + ' ' + tip +
                                     Ext.Date.format(new Date(storeItem.get('date')), tipFormat));
                  }
                },


            }],

        });

        this.add({html: '<h2><a href="/usage/">'+this.heading+'</a></h2>'});
        this.add(this.chart);
    },

});

Ext.define('BQ.usage.UploadsMonthly', {
    extend: 'BQ.usage.Uploads',
    alias: 'widget.monthlyuploadstats',
    heading: 'Image uploads - monthly',
    tip: 'Image uploads during ',
    axisFormat: "M 'y",
    tipFormat : "M 'y",

    resource: '/usage/uploads_monthly',
    modelName: 'UsageMonthlyUploads',
});

Ext.define('BQ.usage.Analysis', {
    extend: 'BQ.usage.Uploads',
    alias: 'widget.analysisstats',
    heading: 'Module executions - daily',
    tip: 'Module executions in ',

    resource: '/usage/analysis',
    modelName: 'UsageAnalysis',
});

Ext.define('BQ.usage.AnalysisMonthly', {
    extend: 'BQ.usage.Uploads',
    alias: 'widget.monthlyanalysisstats',
    heading: 'Module executions - monthly',
    tip: 'Module executions during ',
    axisFormat: "M 'y",
    tipFormat : "M 'y",

    resource: '/usage/analysis_monthly',
    modelName: 'UsageMonthlyAnalysis',
});
