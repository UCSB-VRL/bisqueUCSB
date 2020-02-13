/*******************************************************************************
  stats.js - data accessor and plotter for Bisque Statistics Service
  <http://www.bioimage.ucsb.edu/downloads/Bisque%20Database>

  @author Dmitry Fedorov  <fedorov@ece.ucsb.edu>

  Copyright (c) 2011-2012 Dmitry Fedorov, Center for Bio-Image Informatics

  ver: 1.0 - ExtJS3
  ver: 2.0 - Update to ExtJS4
  ver: 3.0 - Update to ExtJS4 plotting

Usage:

  The most basic way is by creating a visualizer:
    var visualizer = new BQStatisticsVisualizer( plotter, url, xpath, xmap, xreduce, { 'height':500 } );
  where:
    plotter - dom element or it's id where visualizer will be created
    url - is the url of the Bisque resource you want to summarize
    xpath, xmap and xreduce - are either vectors or just strings of respective statistics service commands.
                              if they are vectors, you will do and receive multiple outputs,
                              if the vectors are not of equal sizes they will get padded by the last value.
                              Note: see expanation about xpath, xmap and xreduce in the end of this header.
    options - the last dictionary is the options dictionary, available configs are presented in the "options"
              section to follow

  You may want to get data first and visualize it yourself, in this case use:
    var accessor = new BQStatisticsAccessor( url, xpath, xmap, xreduce,
                                             { 'ondone': callback(this, "onDone"), 'onerror': callback(this, "onError") } );


Options:

  title  - optional parameter to define the title
  width  - optional parameter to control the width of the main panel, default is '100%'
  height - optional parameter to control the height of the main panel, default is 500

  grid - if set to false then no grid will be displayed, default is true
  plot - if set to false then no plot will be displayed, default is true

  width_plot - optional parameter to control the width of the plot panel, default is '65%'
  width_grid - optional parameter to control the width of the grid panel, default is '35%'

  plot_margin_top    - optional parameter to control the margin of the plot in teh panel, default is 30
  plot_margin_lelf   - optional parameter to control the margin of the plot in teh panel, default is 60
  plot_margin_bottom - optional parameter to control the margin of the plot in teh panel, default is 30
  plot_margin_righ   - optional parameter to control the margin of the plot in teh panel, default is 30

  args - dictionary of arguments passed directly to the statistics service, ex: args: {numbins: 25}

Statistics service:

 The idea for the statistics service is in the sequence of filter applied to the data
 URL specifies the documents URL, which can be: gobjects, tags or dataset
 1) QUERY: [etree -> vector of objects]
    Elements are extracted from the document into the vector using XPath expression
    at this stage the vector should only comntain:
        a) tags (where values could be either numeric or string),
        b) primitive gobjects (only graphical elements like poits and polygones...)
        c) numerics as a result of operation in XPath
 2) MAP: [vector of objects -> uniform vector of numbers or strings]
    An operator is applied onto the vector of objects to produce a vector of numbers or strings
    The operator is specified by the user and can take specific elements and produces specific result
    for example: operator "area" could take polygon or rect and produce a number
                 operator "numeric-value" can take a "tag" and return tag's value as a number
                 possible operator functions should be extensible and maintained by the stat service
 3) REDUCE: [uniform vector of numbers or strings -> summary as XML]
    A summarizer function is applied to the vector of objects to produce some summary
    the summary is returned as an XML document
    for example: summary "vector" could simply pass the input vector for output
                 summary "histogram" could bin the values of the input vector and could work on both text and numbers
                 summary "max" would return max value of the input vector

*******************************************************************************/

Ext.require([
    'Ext.chart.*',
    'Ext.fx.target.Sprite',
]);

STAT_VECTOR_TAGS = { 'vector':0, 'unique':0, 'set':0, 'histogram':0, 'bin_centroids':0, 'vector-sorted':0, 'unique-sorted':0, 'set-sorted':0 };

//------------------------------------------------------------------------------
// Utils
//------------------------------------------------------------------------------
/*
function showHourGlass(surface, text) {
  surface.style.height = '140px';
  //surface.innerHTML = '<img src="/static/stats/images/progress_128.gif">';
  if (!text) text = 'Fetching data';
  var p = new BQProgressBar( surface, text );
}
*/
function allNumbers(v) {
  for (var i=0; i<v.length; ++i) {
    if (typeof v[i] == 'number' && isFinite(v[i]) ) continue;
    f = parseFloat(v[i]);
    if (typeof f == 'number' && isFinite(f)) continue;
    return false;
  }
  return true;
}

function splitUrl(u) {
  var r = {}
  var l = u.split('?', 2);
  if (l.length>1) {
    r.path = l[0];
    r.attrs = l[1];
  } else {
    r.attrs = l[0];
  }

  var atts = r.attrs.split('&');
  r.attrs = {};
  for (var i=0; i<atts.length; i++) {
    var a = atts[i].split('=');
    if (a.length<2) continue;
    r.attrs[decodeURIComponent(a[0])] = decodeURIComponent(a[1]);
  }

  return r;
}

function getUrlArg(basename, arg) {
  if (arg instanceof Array) {
    var s='';
    for (var i=0; i<arg.length; i++) {
      var num = i.toString();
      if (i==0) num = '';
      s += '&'+basename+num+'='+escape(arg[i]);
    }
    return s;
  } else {
    return '&'+basename+'='+escape(arg);
  }
}

function getUrlArgEncoded(basename, arg) {
  if (arg instanceof Array) {
    var s='';
    for (var i=0; i<arg.length; i++) {
      var num = i.toString();
      if (i==0) num = '';
      s += '&'+basename+num+'='+encodeURIComponent(arg[i]);
    }
    return s;
  } else {
    return '&'+basename+'='+escape(arg);
  }
}

function getUrlArgs(d) {
  var s='';
  for (k in d)
    s += '&'+k+'='+escape(d[k]);
  return s;
}

//------------------------------------------------------------------------------
// BQStatisticsAccessor
//------------------------------------------------------------------------------

function BQStatisticsAccessor( url, xpath, xmap, xreduce, opts ) {
  this.url     = url;
  this.xpath   = xpath;
  this.xmap    = xmap;
  this.xreduce = xreduce;
  this.args    = {}; // additional arguments to pass to statistics service

  this.opts = opts || {};
  if ('args' in opts) this.args = opts['args'];
  if (this.opts['ondone']) this.ondone = this.opts['ondone'];
  if (this.opts['onerror']) this.onerror = this.opts['onerror'];

  this.fetch();
}

BQStatisticsAccessor.prototype.fetch = function () {
  //escape, encodeURI and encodeURIComponent
  var stat_url = '/stats/compute?';
  if (this.opts.root) stat_url = this.opts.root+'/stats/compute?';
  //stat_url += 'url='+encodeURIComponent(this.url);
  stat_url += getUrlArgEncoded('url', this.url);
  stat_url += getUrlArg('xpath', this.xpath);
  stat_url += getUrlArg('xmap', this.xmap);
  stat_url += getUrlArg('xreduce', this.xreduce);
  stat_url += getUrlArgs(this.args);
  BQFactory.request( { uri: stat_url, cb: callback(this, "onLoad"), errorcb: callback(this, "onError") } );
};

BQStatisticsAccessor.prototype.onLoad = function (stats) {
    if (stats.resource_type != 'resource' || stats.type != 'statistic') {
        this.onError('Statistics server returned document in unknow format');
        return;
    }

    // retrieve all the tags available as a result
    this.results = [];
    var resource=null;
    for (var c=0; (resource=stats.children[c]); c++) {
        if (resource.resource_type != 'resource') continue;
        var tags = resource.tags;
        var result = {};
        result.uri = resource.attributes.uri;
        var u = splitUrl(result.uri);
        result.xpath   = u.attrs.xpath;
        result.xmap    = u.attrs.xmap;
        result.xreduce = u.attrs.xreduce;

        for (var i=0; i<tags.length; i++) {
            if (tags[i] == null) continue;
            var val_str = tags[i].value;
            if (val_str == null || val_str == '')
                val_str = tags[i].values[0].value;
            result[tags[i].name] = val_str;
        }

        // turn all vector tags into arrays
        for (var k in result) {
            if (k in STAT_VECTOR_TAGS) {
                result[k] = result[k].split(',');
                for (var i=0; i<result[k].length; i++)
                    result[k][i] = decodeURIComponent(result[k][i]);
            }
        }

        this.results.push(result);
    }

    //this.results.stats = stats;
    if (this.ondone && this.results.length>0) this.ondone(this.results);
    if (this.results.length<1) this.onError('Statistics server returned no parsable results');
};

BQStatisticsAccessor.prototype.onError = function (str) {
  if (this.onerror) this.onerror(str);
};


//******************************************************************************
// BQ.stats.plotter.Factory - ExtJS4 rewrite of BQPlotterFactory
//******************************************************************************

Ext.namespace('BQ.stats.plotter.Factory');

BQ.stats.plotter.Factory.ctormap = { vector          : 'BQ.stats.plotter.Line',
                                     'vector-sorted' : 'BQ.stats.plotter.Line',
                                     unique          : 'BQ.stats.plotter.Line',
                                     'unique-sorted' : 'BQ.stats.plotter.Line',
                                     set             : 'BQ.stats.plotter.Line',
                                     'set-sorted'    : 'BQ.stats.plotter.Line',
                                     histogram       : 'BQ.stats.plotter.Histogram',
};

BQ.stats.plotter.Factory.make = function(xreduce, results, opts) {
    var ctor = undefined;
    if (xreduce in BQ.stats.plotter.Factory.ctormap)
        ctor = BQ.stats.plotter.Factory.ctormap[xreduce];
    if (!ctor) return undefined;

    var conf = {
        xreduce: xreduce,
        results: results,
        flex: 1,
    };
    if (opts) Ext.applyIf(conf, opts);

    return Ext.create(ctor, conf);
};

BQ.stats.plotter.Factory.xtypemap = { vector          : 'statslineplot',
                                      'vector-sorted' : 'statslineplot',
                                      unique          : 'statslineplot',
                                      'unique-sorted' : 'statslineplot',
                                      set             : 'statslineplot',
                                      'set-sorted'    : 'statslineplot',
                                      histogram       : 'statshistplot',
};


BQ.stats.plotter.Factory.define = function(xreduce, results, opts) {
    var ctor = undefined;
    if (xreduce in BQ.stats.plotter.Factory.xtypemap)
        ctor = BQ.stats.plotter.Factory.xtypemap[xreduce];
    if (!ctor) return undefined;

    var conf = {
        xtype: ctor,
        xreduce: xreduce,
        results: results,
        flex: 1,
    };
    if (opts) Ext.applyIf(conf, opts);

    return conf;
};


//------------------------------------------------------------------------------
// BQ.stats.plotter.Plotter
//------------------------------------------------------------------------------
BQ.stats.plotter.SMALL_PLOT_SIZE = 100;

Ext.define('BQ.stats.plotter.Plotter', {
    alias: 'widget.statsplotter',
    //extend: 'Ext.panel.Panel',
    extend: 'Ext.container.Container', // dima - apparently requires Panel
    requires: ['Ext.chart.*', 'Ext.layout.container.Fit'],

    // required inputs
    xreduce : undefined,
    results : undefined,

    // configs
    layout: 'fit',
    defaults: { border: 0, },

    constructor: function(config) {
        this.addEvents({
            'selected' : true,
        });
        this.callParent(arguments);
        return this;
    },

    initComponent : function() {
        this.callParent();
        this.plot = undefined;

        //if (!this.xreduce) return;
        //if (!this.xreduce in this.results) return;
        //this.createStore();
    },

    afterRender : function() {
        if (!this.xreduce) return;
        if (!this.xreduce in this.results) return;
        this.createStore();

        if (this.store)
            this.add(this.createPlot());
        //this.doComponentLayout();

        //this.queryById('plot').redraw();
    },

    createStore: function () {
        var results = this.results;
        var fields = [];
        var data = [];
        var maxsz = 0;
        var minval = Number.MAX_VALUE;
        var maxval = -Number.MAX_VALUE;
        this.titles = this.titles || [];

        for (var i=0; i<results.length; i++) {
            if (!(this.xreduce in results[i])) continue;
            var v = results[i][this.xreduce];
            if (!allNumbers(v)) continue;

            var name = 'data'+i;
            fields.push(name);
            maxsz = Math.max(maxsz, v.length);
            for (var k=0; k<v.length; k++) {
                data[k] = data[k] || { 'index': k, };
                data[k][name] = parseFloat(v[k]);
                if (data[k][name] < minval) minval = data[k][name];
                if (data[k][name] > maxval) maxval = data[k][name];
            }
            this.titles[i] = this.titles[i] || results[i].xpath;
        }

        this.min_value = minval;
        this.max_value = maxval;

        this.store = Ext.create('Ext.data.JsonStore', {
            fields: ['index'].concat(fields),
            data: data,
        });

        this.fields = fields;
        this.large_array = maxsz>BQ.stats.plotter.SMALL_PLOT_SIZE;
    },

    createPlot: function () {
        return undefined;
    },

});



//------------------------------------------------------------------------------
// BQ.stats.plotter.Line
//------------------------------------------------------------------------------

Ext.define('BQ.stats.plotter.Line', {
    alias: 'widget.statslineplot',
    extend: 'BQ.stats.plotter.Plotter',
    requires: ['Ext.chart.Chart'],

    createPlot: function () {
        var series = [];
        var f = undefined;
        for (var i=0; (f=this.fields[i]); i++) {
            series.push({
                type: 'line',
                title: this.titles?this.titles[i]:undefined,
                axis: 'left',
                xField: 'index',
                yField: f,

                smooth: 3,
                selectionTolerance: 3, // dima: this here is a problem, gives wrong items if large, no way to split x and y tolerances

                showMarkers: this.large_array?false:true,
                markerConfig: {
                    size: 4,
                    radius: 4,
                    //'stroke-width': 0,
                },

                //highlight: true,
                highlight: {
                    size: 4,
                    radius: 4,
                },
                style: {
                    //opacity: 0.86,
                    'stroke-width': 2,
                },

                tips: {
                  trackMouse: true,
                  anchor: 'bottom',
                  //width: 300,
                  //height: 28,
                  renderer: function(storeItem, item) {
                      this.setTitle( item.value[1] );
                  }
                },

               listeners: {
                    'itemmouseover': function( item, e ) {
                            this.fireEvent( 'selected', this, item);
                        },
                    scope: this
                },
            });
        }

        var plot = this.queryById('plot');
        if (plot)
            plot.destroy();
        return {
            xtype: 'chart',
            itemId  : 'plot',
            region: 'center',
            flex: 2,
            border: 0,
            title: 'My chart',
            animate: false,
            shadow: false,
            border: 0,
            /*
            legend: {
                position: 'bottom',
                boxStroke: '',
                boxStrokeWidth: '0',
            },*/

            store: this.store,
            axes: [{
                type: 'Numeric',
                position: 'left',
                fields: this.fields,
                label: {
                    renderer: Ext.util.Format.numberRenderer('0.0')
                },
                //title: 'Sample Values',
                //grid: true,
                //minimum: 0
                minimum: this.min_value,   // otherwise plots for small numbers have wrong Y-axis scale (at least for ExtJS 4)
                maximum: this.max_value,
            }, {
                type: 'Numeric',
                position: 'bottom',
                fields: ['index'],
                //title: 'Sample Metrics'
            }],

            series: series,
        };
    },

});



//------------------------------------------------------------------------------
// BQ.stats.plotter.Histogram
//------------------------------------------------------------------------------

Ext.define('BQ.stats.plotter.Histogram', {
    alias: 'widget.statshistplot',
    extend: 'BQ.stats.plotter.Plotter',
    requires: ['Ext.chart.Chart'],

    createStore: function () {
        var results = this.results;
        var fields = [];
        var data = [];
        var maxsz = 0;
        this.titles = this.titles || [];

        for (var i=0; i<results.length; i++) {
            if (!(this.xreduce in results[i])) continue;
            var v = results[i][this.xreduce];
            var b = results[i]['bin_centroids'];
            if (!allNumbers(v)) continue;

            var name = 'data'+i;
            fields.push(name);
            maxsz = Math.max(maxsz, v.length);
            for (var k=0; k<v.length; k++) {
                data[k] = data[k] || { 'index': k, };
                data[k][name] = parseFloat(v[k]);
                data[k][name+'_centroid'] = parseFloat(b[k]);
            }

            this.titles[i] = this.titles[i] || results[i].xpath;
        }

        this.store = Ext.create('Ext.data.JsonStore', {
            fields: ['index'].concat(fields),
            data: data,
        });

        this.fields = fields;
        //this.large_array = maxsz>BQ.stats.plotter.SMALL_PLOT_SIZE;

    },

    createPlot: function () {
        var series = [];
        var f = undefined;
        var centroids = [];
        for (var i=0; (f=this.fields[i]); i++) {
            centroids[i] = this.fields[i] + '_centroid';
        }

        //for (var i=0; (f=this.fields[i]); i++) {
            var h = Math.floor(Math.random()*256);
            var color = 'hsl('+h+', 75%, 70%)';

            series.push({
                type: 'column',
                //title: this.titles?this.titles[i]:undefined,
                title: this.titles?this.titles:undefined,
                axis: 'left',
                xField: centroids,
                yField: this.fields,

                groupGutter: 2,
                gutter: 10,

                highlight: false,
                /*highlight: {
                    fill: '#ff0000',
                    'stroke-width': 0,
                    stroke: '',
                },*/

                /*style: {
                    //opacity: 0.86,
                    //'stroke-width': 2,
                    fill: color,
                },*/

                label: {
                    display: 'insideEnd',
                    'text-anchor': 'middle',
                    //field: f,
                    field: this.fields,
                    renderer: Ext.util.Format.numberRenderer('0'),
                    orientation: 'vertical',
                },

                tips: {
                  trackMouse: true,
                  anchor: 'bottom',
                  width: 200,
                  //height: 28,
                  renderer: function(storeItem, item) {
                      var s = 'Frequency: '+item.value[1];
                      s += item.value[0]?'<br>'+'Centroid: '+item.value[0]:'';
                      this.setTitle( s );
                  }
                },

                listeners: {
                    'itemmouseover': function( item, e ) {
                            this.fireEvent( 'selected', this, item);
                        },
                    scope: this
                },

            });
        //}


        var plot = this.queryById('plot');
        if (plot)
            plot.destroy();

        plot = {
            xtype: 'chart',
            itemId  : 'plot',
            style: 'background:#fff',
            border: 0,
            //title: 'My chart',
            animate: false,
            shadow: false,
            store: this.store,
            /*legend: {
                position: 'bottom',
                boxStroke: '',
                boxStrokeWidth: '0',
            },*/

            axes: [{
                type: 'Numeric',
                position: 'bottom',
                //fields: ['index'],
                fields: centroids,
                //title: 'Sample Metrics'
            }, {
                type: 'Numeric',
                position: 'left',
                fields: this.fields,
                label: {
                    renderer: Ext.util.Format.numberRenderer('0,0')
                },
                //title: 'Sample Values',
                //grid: true,
                //minimum: 0
            }],

            series: series,
        };
        return plot;
    },

});


//******************************************************************************
// BQ.stats.grid.Factory - ExtJS4 rewrite of BQGridFactory
//******************************************************************************

Ext.namespace('BQ.stats.grid.Factory');

BQ.stats.grid.Factory.ctormap = { vector          : 'BQ.stats.grid.Vector',
                                  'vector-sorted' : 'BQ.stats.grid.Vector',
                                  unique          : 'BQ.stats.grid.Vector',
                                  'unique-sorted' : 'BQ.stats.grid.Vector',
                                  set             : 'BQ.stats.grid.Vector',
                                  'set-sorted'    : 'BQ.stats.grid.Vector',
                                  histogram       : 'BQ.stats.grid.Histogram',
};

BQ.stats.grid.Factory.make = function(xreduce, results, opts) {
    var ctor = 'BQ.stats.grid.Grid';
    if (xreduce in BQ.stats.grid.Factory.ctormap)
        ctor = BQ.stats.grid.Factory.ctormap[xreduce];

    var conf = {
        xreduce: xreduce,
        results: results,
        //flex: 1,
    };
    if (opts) Ext.applyIf(conf, opts);

    return Ext.create(ctor, conf);
};

//------------------------------------------------------------------------------
// BQ.stats.grid.Grid
//------------------------------------------------------------------------------

Ext.define('BQ.stats.grid.Grid', {
    alias: 'widget.statsgrid',
    extend: 'Ext.panel.Panel',
    //extend: 'Ext.container.Container', // dima - apparently requires Panel
    requires: ['Ext.grid.Panel'],

    // required inputs
    xreduce : undefined,
    results : undefined,
    opts    : undefined,

    // configs
    layout: 'fit',

    constructor: function(config) {
        this.addEvents({
            'selected' : true,
        });
        this.callParent(arguments);
        return this;
    },

    initComponent : function() {
        this.createStore();
        this.createGrid();
        this.callParent();
    },

    createStore: function () {
        if (!this.xreduce) return;
        if (!this.xreduce in this.results) return;

        var mydata = [
            [this.xreduce, this.results[this.xreduce]]
        ];

        var myfields = [
               {name: 'name', title: 'Name'},
               {name: 'value', title: 'Value'},
            ];

        this.store = Ext.create('Ext.data.ArrayStore', {
            fields: myfields,
            data: mydata
        });
        this.store.bqfields = myfields;
    },

    createGrid: function () {
        if (!this.store) return;
        if (!this.xreduce) return;
        if (!this.xreduce in this.results) return;
        var store = this.store;

        var mytitle = this.title ? this.title : this.xreduce;
        this.title = mytitle;


        Ext.QuickTips.init();
        //Ext.state.Manager.setProvider(Ext.create('Ext.state.CookieProvider'));

        var myfields = store.bqfields;
        this.grid = Ext.create('Ext.grid.Panel', {
            store: store,
            columnLines: true,
            border: 0,
            //title: mytitle,
            viewConfig: { stripeRows: true },

            columns: [{
                text     : myfields[0].title,
                sortable : true,
                dataIndex: myfields[0].name
            }, {
                text     : myfields[1].title,
                flex     : 1,
                sortable : true,
                dataIndex: myfields[1].name
            }],
            listeners: {
                'itemclick': function( view, record, item, index, e, eOpts) {
                        this.fireEvent( 'selected', this, record );
                    },
                scope: this
            },
        });
        //this.add(this.grid);
        this.items = [this.grid];
    },

});

//------------------------------------------------------------------------------
// BQ.stats.grid.Vector
//------------------------------------------------------------------------------

Ext.define('BQ.stats.grid.Vector', {
    alias: 'widget.statsgridvector',
    extend: 'BQ.stats.grid.Grid',

    createStore: function () {
        if (!this.xreduce) return;
        if (!this.xreduce in this.results) return;

        var mydata = [];
        for (var i in this.results[this.xreduce]) {
          mydata[i] = [i, this.results[this.xreduce][i]];
        }
        var data_type = 'auto'; // auto string int float boolean date
        if (!isNaN(this.results[this.xreduce][0]))
          data_type = 'float';

        var myfields = [
               {name: 'index', title: 'Index', type: 'int' },
               {name: 'value', title: 'Value', type: data_type },
            ];

        this.store = Ext.create('Ext.data.ArrayStore', {
            fields: myfields,
            data: mydata
        });
        this.store.bqfields = myfields;
    },

});

//------------------------------------------------------------------------------
// BQ.stats.grid.Histogram
//------------------------------------------------------------------------------

Ext.define('BQ.stats.grid.Histogram', {
    alias: 'widget.statsgridvector',
    extend: 'BQ.stats.grid.Grid',

    createStore: function () {
        if (!this.xreduce) return;
        if (!this.xreduce in this.results) return;

        var mydata = [];
        for (var i in this.results[this.xreduce]) {
          mydata[i] = [this.results['bin_centroids'][i], this.results[this.xreduce][i]];
        }
        var data_type = 'auto'; // auto string int float boolean date
        if (!isNaN(this.results['bin_centroids'][0]))
          data_type = 'float';

        var myfields = [
               {name: 'centroid', title: 'Centroid', type: data_type},
               {name: 'frequency', title: 'Frequency', type: 'int'},
            ];

        this.store = Ext.create('Ext.data.ArrayStore', {
            fields: myfields,
            data: mydata
        });
        this.store.bqfields = myfields;
    },

});

//******************************************************************************
// BQ.stats.Visualizer - ExtJS4 rewrite of BQStatisticsVisualizer
//******************************************************************************

Ext.define('BQ.stats.Visualizer', {
    alias: 'widget.statsvisualizer',
    extend: 'Ext.panel.Panel', // extend: 'Ext.container.Container',
    //requires: ['BQ.viewer.Image'],

    // required inputs
    url     : undefined,
    xpath   : undefined,
    xmap    : undefined,
    xreduce : undefined,
    opts    : undefined,

    // configs
    //cls: 'selector',
    border: 0,
    layout: 'border',

    initComponent : function() {
        this.opts = this.opts || {};
        if (!('grid' in this.opts)) this.opts.grid = true;
        if (!('plot' in this.opts)) this.opts.plot = true;

        this.items = [];
        if (this.opts.grid == true) {
            this.items.push({
                xtype: 'container',
                itemId  : 'panel_grid',
                region: 'west',
                //collapsible: true,
                split: true,
                //flex: 1,
                width: 250,
                layout: 'accordion',
                defaults: { border: 0, },
            });
        }

        // center plot panel has to exist for the layout to work correctly
        this.items.push({
            xtype: 'container',
            itemId  : 'panel_plot',
            collapsible: false,
            region: 'center',
            flex: 2,
            layout: 'fit',
            split: true,
            //layout: 'auto',
            defaults: { border: 0, },
        });

        this.callParent();
    },

    afterRender : function() {
        this.load();
    },

    load : function() {
        var m = this.setLoading('Fetching data');
        var opts = { 'ondone': callback(this, 'ondone'), 'onerror': callback(this, 'onerror') };
        if ('args' in opts) opts.args = this.opts.args;
        if (this.root) opts.root = this.root;
        this.accessor = new BQStatisticsAccessor( this.url, this.xpath, this.xmap, this.xreduce, opts );
    },

    onerror: function (e) {
        this.setLoading(false);
        var message = typeof(e)=='string'?e:e.message;
        BQ.ui.error(message);
    },

    ondone: function (results) {
        this.setLoading(false);
        if (results.length<1) {
            BQ.ui.warning('Statistics server did not return any results...');
            return;
        }
        // create tables and plots here
        if (this.opts.grid == true) {
            this.grids = [];
            for (var i=0; i<results.length; i++) {
                var opts = {
                    title: this.opts.titles ? this.opts.titles[i] :
                           results[i].xreduce +' of '+ results[i].xmap +' for '+  results[i].xpath,
                    listeners: {
                        'selected': function( gr, record ) {

                        },
                        scope: this
                    },
                };

                this.grids[i] = BQ.stats.grid.Factory.make(results[i].xreduce, results[i], opts);
                this.queryById('panel_grid').add(this.grids[i]);
            }
        }

        if (this.opts.plot == true) {
            var opts = {
                border: 0,
                titles: this.opts?this.opts.titles:undefined,
                listeners: {
                    'selected': function( pl, item ) {

                    },
                    scope: this
                },
            };

            //TODO: find first vector type to be plotted
            var plotter = BQ.stats.plotter.Factory.define( results[0].xreduce, results, opts );
            if (plotter) {
                this.queryById('panel_plot').add(plotter);
                this.doComponentLayout();
            }
            //else
            //    this.plotPanel.setVisible(false);
        }

    },

});

//--------------------------------------------------------------------------------------
// BQ.upload.Dialog
// Instantiates upload panel in a modal window
//--------------------------------------------------------------------------------------
BQ.stats.DEFAULTS = { 'title':null, 'width':null, 'height':null, };

Ext.define('BQ.stats.Dialog', {
    extend : 'Ext.window.Window',
    alias: 'widget.statsdialog',
    requires: ['BQ.stats.Visualizer'],

    layout : 'fit',
    modal : true,
    border : false,

    constructor : function(config) {

        var conf = {
            xtype: 'statsvisualizer',
            border: 0,
            flex: 1,
        };

        // move the config options that belong to the uploader
        for (var c in config)
            if (!(c in BQ.stats.DEFAULTS))
                 conf[c] = config[c];

        this.items = [conf];
        this.callParent(arguments);

        this.show();
        return this;
    },

    initComponent : function() {
        this.width  = this.width || BQApp?BQApp.getCenterComponent().getWidth()/1.2:document.width/1.2;
        this.height = this.height || BQApp?BQApp.getCenterComponent().getHeight()/1.2:document.height/1.2;
        this.callParent();
    },

});

