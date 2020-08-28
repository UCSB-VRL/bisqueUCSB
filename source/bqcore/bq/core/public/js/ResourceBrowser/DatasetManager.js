Ext.define('Bisque.ResourceBrowser.DatasetManager', {
    extend : 'Ext.grid.Panel',

    constructor : function(config) {
        Ext.apply(this, {
            title : 'Datasets',
            width : 350,
            padding : 5,
            autoScroll : true,
            store : Ext.create('Ext.data.ArrayStore', {
                fields : ['Raw', 'Name', 'Date']
            }),
            columns : {
                items : [{
                    width : 8,
                }, {
                    dataIndex : 'Name',
                    text : 'Dataset',
                    flex : 0.5
                }, {
                    dataIndex : 'Date',
                    text : 'Date',
                    align : 'center',
                    flex : 0.5
                }]
            },
            listeners : {
                'select' : function(me, record, index, a, b, c) {
                    var dataset = record.get('Raw');

                    this.msgBus.fireEvent('Browser_ReloadData', {
                        offset : 0,
                        baseURL : dataset.uri + '/value'
                    });
                    this.msgBus.fireEvent('DatasetSelected', dataset);
                },
            },
        });

        this.callParent(arguments);
        this.loadDatasets(false);
    },

    loadDatasets : function(loaded, datasetList) {
        if (!loaded)
            BQFactory.load('/data_service/dataset?view=short&tag_order=@ts:desc', callback(this, 'loadDatasets', true));
        else {
            var list = [], i;

            for ( i = 0; i < datasetList.children.length; i++) {
                var date = Ext.Date.parse(datasetList.children[i].ts, BQ.Date.patterns.BisqueTimestamp);
                list.push([datasetList.children[i], datasetList.children[i].name, Ext.Date.format(date, BQ.Date.patterns.ISO8601Long)]);
            }

            this.store.loadData(list);
        }
    },
});