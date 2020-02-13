/*******************************************************************************

  BQWebApp - a prototype of a fully integrated interface for a module

  This class should be inherited as demonstrated in the example and extended for
  desired functionality of the module. This class also expects a certain structure
  of the HTML page it will be operating on. Pages should have certain elements:
  <div id="">


  Possible configurations:




  Example:

function MyWebApp (args) {
    this.module_url = '/module_service/SeedSize/';
    this.label_run = "Run my analysis";

    BQWebApp.call(this, args);
}

MyWebApp.prototype = new BQWebApp();

*******************************************************************************/

function BQWebApp (urlargs) {
  // a simple safeguard to only run this when an inherited class is instantiated
  // this will only work if the constructr was properly overwritten on declaration
  if (this.constructor === BQWebApp) return;

  // arguments that may be defined by inherited classes
  this.module_url = this.module_url || location.pathname;
  this.label_run = this.label_run || "Run analysis";
  this.label_progress = this.label_progress || "This may take some time, progress will be shown here.";

  this.renderers = {};

  // parse URL arguments
  if (!urlargs) urlargs = document.URL;
  this.args = parseUrlArguments(urlargs);

  // construct holders for ExtJs components
  if (document.getElementById("webapp_results_dataset")) {
      this.holder_result = Ext.create('Ext.container.Container', {
          layout: { type: 'fit' },
          renderTo: 'webapp_results_dataset',
          border: 0,
          //height: 500,
          //cls: 'bordered',
      });
      this.holder_result.hide();
      Ext.EventManager.addListener( window, 'resize', function(e) {
          var w = document.getElementById("webapp_results_dataset").offsetWidth;
          this.holder_result.setSize(w, this.holder_result.height);
      }, this, { delay: 100 } );
  }

    // create grid for plotting status of parallel run
    if (document.getElementById('run')) {
        //var mydata = [ ['r0', 'n0', 's0'], ['r1', 'n1', 's1'], ['r2', 'n2', 's2'], ];
        var myfields = [
           {name: 'resource', title: 'Resource uri'},
           {name: 'name', title: 'Resource name'},
           {name: 'status', title: 'Status'},
        ];

        this.status_store = Ext.create('Ext.data.ArrayStore', {
            data: [],
            fields: myfields,
        });

        this.status_panel = this.create_renderer( 'run', 'Ext.grid.Panel', {
            title: 'Parallel processing status',
            renderTo: 'run',
            cls: 'run-status',
            border: 1,
            height: 250,

            store: this.status_store,
            columns: [
                { text: myfields[1].title, sortable: true, dataIndex: myfields[1].name, flex: 3 },
                { text: myfields[2].title, sortable: true, dataIndex: myfields[2].name, flex: 2 },
            ],

            viewConfig: {
                stripeRows: true,
                enableTextSelection: true
            },
        });
        this.status_panel.setVisible(false);
    }



  if (this.module_url)
  this.ms = new ModuleService(this.module_url, {
      ondone     : callback(this, 'done'),
      onstarted  : callback(this, 'onstarted'),
      onprogress : callback(this, 'onprogress'),
      onerror    : callback(this, 'onerror'),
      onloaded   : callback(this, 'init'),
  });

};

BQWebApp.prototype.init = function (ms) {
    if (ms) this.ms = ms;
    if (!this.ms.module) return;

    this.setupUI();
    this.setupUI_inputs();

  // process arguments
  if ('mex' in this.args) {
      this.showProgress(null, 'Fetching module execution document');
      BQFactory.request({
          uri: this.args.mex,
          cb: callback(this, 'load_from_mex'),
          errorcb: callback(this, 'onerror'),
          //uri_params: {view:'deep'}  });
          uri_params: {view:'full'}
      });
      return;
  }

  // loading resource requires initied input UI renderers
  if ('resource' in this.args)
      BQFactory.request( { uri:     this.args.resource,
                           cb:      callback(this, 'load_from_resource'),
                           errorcb: callback(this, 'onerror'), });
};


//------------------------------------------------------------------------------
// Misc
//------------------------------------------------------------------------------

function setInnerHtml(id, html) {
    var element = document.getElementById(id);
    if (element)
        element.innerHTML = html;
};

function changeVisibility( e, vis ) {
  if (!document.getElementById(e)) return;
  if (vis)
      document.getElementById(e).style.display='';
  else
      document.getElementById(e).style.display='none';
};

function changeDisabled( e, vis ) {
  if (document.getElementById(e))
      document.getElementById(e).disabled = !vis;
};

function parseUrlArguments(urlargs) {
    var a = urlargs.split('?', 2);
    if (a.length<2) {
        a = urlargs.split('#', 2);
        if (a.length<2) return {};
    }

    // see if hash is present
    a = a[1].split('#', 2);
    if (a.length<2)
        a = a[0];
    else
        a = a[0] +'&'+ a[1];

    // now parse all the arguments
    a = a.split('&');
    var d = {};
    for (var i=0; i<a.length; i++) {
        var e = a[i].split('=', 2);
        d[unescape(e[0])] = unescape(e[1]);
    }
    return d;
};

BQWebApp.prototype.mexMode = function (mex) {
    this.mex_mode = true;
    if (mex.status != "FINISHED" && mex.status != "FAILED") return;

    BQ.ui.notification('This application is currently showing previously computed results.<br><br>'+
        '<i>Remove the "mex" url parameter in order to analyse new data.</i>', 20000);
    //document.getElementById("webapp_input").style.display = 'none';
    //document.getElementById("webapp_parameters").style.display = 'none';
    //document.getElementById("webapp_run").style.display = 'none';
    BQ.ui.tip('webapp_results', 'Visualizing results of a selected execution!',
              {color: 'green', timeout: 10000, anchor:'bottom',});
};

BQWebApp.prototype.showProgress = function (p, s) {
    this.hideProgress();
    this.progressbar = new BQProgressBar(p, s, {"float":true});
};

BQWebApp.prototype.hideProgress = function () {
    if (this.progressbar) {
        this.progressbar.stop();
        delete this.progressbar;
        this.progressbar = null;
    }
};

BQWebApp.prototype.onnouser = function () {
    if (!BQSession.current_session || !BQSession.current_session.hasUser()) {
        BQ.ui.warning('You are not logged in! You need to log-in to run any analysis...');
    }
};

BQWebApp.prototype.onerror = function (error) {
    // if the error happened we need to refetch the MEX to see the sum element's status
    if (this.status_panel.isVisible() && this.current_mex_uri)
        BQFactory.request({
            uri:     this.current_mex_uri,
            cb:      callback(this, 'onprogress'),
            errorcb: function(){},
            uri_params: { view:'deep' },
        });

    var str = error;
    if (typeof(error)=="object") str = error.message;

    this.hideProgress();
    BQ.ui.error(str);

    var button_run = document.getElementById("webapp_run_button");
    button_run.childNodes[0].nodeValue = this.label_run;
    var status_field = document.getElementById("webapp_status_text");
    status_field.innerHTML = this.label_progress;

    var result_label = document.getElementById("webapp_results_summary");
    if (result_label)
        result_label.innerHTML = '<h3 class="error">'+str+'</h3>';
};

BQWebApp.prototype.getResourceNameByUrl = function (uri) {
    this.uri_name_map = this.uri_name_map || {};
    if (uri in this.uri_name_map)
        return this.uri_name_map[uri];

    this.uri_name_map[uri] = uri;
    /*BQFactory.request( { uri:     uri,
                         cb:      callback(this, 'map_name'),
                         errorcb: function(){}, });*/
};

BQWebApp.prototype.map_name = function (r) {
    if (!r || !r.name || !r.uri) return;
    this.uri_name_map[r.uri] = r.name;
};


//------------------------------------------------------------------------------
// loading from
//------------------------------------------------------------------------------

BQWebApp.prototype.load_from_resource = function (R) {
    // find first suitable resource renderer
    var renderer = null;
    var inputs = this.ms.module.inputs;
    if (inputs && inputs.length>0)
    for (var p=0; (i=inputs[p]); p++) {
        if (!i.renderer) continue;
        var template = i.template || {};
        var accepted_type = template.accepted_type || {};
        accepted_type[i.type] = i.type;

        if (R.resource_type in accepted_type) {
            renderer = i.renderer;
            break;
        }
    }
    if (renderer && renderer.select)
        renderer.select(R);
};

BQWebApp.prototype.inputs_from_mex = function (mex) {
    // first ensure we have full inputs
    var inputs = mex.find_tags('inputs');
    if (inputs instanceof Array)
        inputs = inputs[0];

    if (!inputs && mex.inputs_index && Object.keys(mex.inputs_index).length<1) {
        BQApp.setLoading('Fetching inputs...');
        BQFactory.request({
            uri: mex.uri,
            cb: callback(this, this.inputs_from_mex),
            errorcb: callback(this, 'onerror'),
            uri_params: { view:'inputs' },
        });
        return;
    }

    // unfortunately we can't fetch inputs deep via view=, refetch
    if (inputs && mex.inputs_index && Object.keys(mex.inputs_index).length<1 && !mex.fetched_inputs) {
        BQApp.setLoading('Fetching inputs...');
        BQFactory.request({
            uri : inputs.uri,
            uri_params : { view: 'deep'},
            errorcb: callback(this, 'onerror'),
            cache : false,
            cb : callback(this, function(doc) {
                inputs.tags = doc.tags;
                mex.fetched_inputs = true;
                mex.dict = null;
                mex.afterInitialized();
                this.inputs_from_mex(mex);
            }),
        });
        return;
    }

    // ensure we fetched execution options (e.g., to render 'coupled' option in inputs)
    var execute_options = mex.find_tags('execute_options');
    if (execute_options && !mex.fetched_execute_options ) {
        BQFactory.request({
            uri : execute_options.uri,
            uri_params : { view: 'deep'},
            cb : callback(this, function(doc) {
                mex.fetched_execute_options = true;
                execute_options.tags = doc.tags;
                this.inputs_from_mex(mex);
            }),
            errorcb: callback(this, 'onerror'),
            cache : false
        });
        return;
    }

    this.hideProgress();
    BQApp.setLoading(false);
    var inputs = this.ms.module.inputs_index;
    var inputs_mex = mex.inputs_index;

    for (var n in inputs_mex) {
        if (!(n in inputs)) continue;
        var renderer = inputs[n].renderer;
        var r = inputs_mex[n];
        if (r && renderer && renderer.select)
            renderer.select(r);
    }
    this.inputsValid();
    this.done(mex);
};

BQWebApp.prototype.load_from_mex = function (mex) {
    this.hideProgress();
    this.mexMode(mex);
    this.inputs_from_mex(mex);
    //this.done(mex); // moved to inputs_from_mex
};


//------------------------------------------------------------------------------
// Selections of resources
//------------------------------------------------------------------------------

BQWebApp.prototype.create_renderer = function ( surface, selector, conf ) {
    conf = conf || {};
    Ext.apply(conf, { width: '100%', renderTo: surface,});
    var renderer = Ext.create(selector, conf);
    var horizontal_padding = 20;

    var do_resize = function() {
            var w = document.getElementById(surface);
            if (w) renderer.setWidth(w.clientWidth-horizontal_padding);
    };

    Ext.EventManager.addListener( window, 'resize', do_resize, this, { delay: 100, }  );
    setTimeout(do_resize, 250);

    return renderer;
};

BQWebApp.prototype.setupUI = function () {
    setInnerHtml('title',       this.ms.module.title || this.ms.module.name);
    setInnerHtml('description', this.ms.module.description);
    setInnerHtml('authors',     'Authors: '+this.ms.module.authors);
    setInnerHtml('version',     'Version: '+this.ms.module.version);
};

BQWebApp.prototype.setupUI_inputs = function (my_renderers) {
    //key = key || 'inputs';
    //this.renderers[key] = this.renderers[key] || {};
    //var my_renderers = this.renderers[key];

    // render input resource pickers
    var inputs = this.ms.module.inputs;
    if (!inputs || inputs.length<=0) return;

    for (var p=0; (i=inputs[p]); p++) {
        var t = i.type;
        if (t in BQ.selectors.resources)
            i.renderer = this.create_renderer( 'inputs', BQ.selectors.resources[t],
                                               { resource: i, module: this.ms.module, webapp: this, } );
            //if (my_renderers) my_renderers(i.name) = i.renderer;
    }

    // check if there are parameters to acquire
    for (var p=0; (i=inputs[p]); p++) {
        var t = (i.type || i.resource_type).toLowerCase();
        if (t in BQ.selectors.parameters) {
            changeVisibility( "webapp_parameters", true );
            break;
        }
    }

    // render all other prameters
    for (var p=0; (i=inputs[p]); p++) {
        var t = (i.type || i.resource_type).toLowerCase();
        if (t in BQ.selectors.parameters)
            i.renderer = this.create_renderer( 'parameters', BQ.selectors.parameters[t],
                                               { resource: i, module: this.ms.module, webapp: this, } );
            //if (my_renderers) my_renderers(i.name) = i.renderer;
    }
};

// this function needed for proper closure creation
BQWebApp.prototype.setupUI_output = function (i, outputs_index, my_renderers, mex) {
    var n = i.name;
    var r = outputs_index[n];
    if (!r) return;
    var t = (r.type || i.type || i.resource_type).toLowerCase();
    if (t in BQ.renderers.resources) {
        var conf = {
            definition: i,
            resource: r,
            mex: mex,
            listeners: {
              scope: this,
              selected_submex: function(submex) {
                  if (typeof submex === 'string') {
                        BQApp.setLoading(true);
                        BQFactory.request({
                            uri : submex,
                            uri_params : { view: 'deep'},
                            cb : callback(this, function(doc) {
                                BQApp.setLoading(false);
                                this.showOutputs(doc, 'outputs-sub');
                            }),
                            errorcb: callback(this, 'onerror'),
                            cache : false
                        });
                  } else {
                      this.showOutputs(submex, 'outputs-sub');
                  }
              },
            }
        };

        // special case if the output is a dataset, we expect sub-Mexs
        if (this.mex.iterables && n in this.mex.iterables) { //&& r.type=='dataset'
            this.mex.findMexsForIterable(n, 'outputs/');
            if (Object.keys(this.mex.iterables[n]).length>0) {
                conf.title = 'Select a thumbnail to see individual results:';
                conf.listeners.selected = function(resource) {
                     var suburl = resource.uri;
                     var submex = this.mex.iterables[n][suburl];
                     this.showOutputs(submex, 'outputs-sub');
                };
            }
        }

        my_renderers[n] = this.create_renderer( 'outputs', BQ.renderers.resources[t], conf );
    }
};

BQWebApp.prototype.setupUI_outputs = function (key, mex) {
    key = key || 'outputs';

    // ensure inputs
    /*
    var inputs = mex.find_tags('inputs');
    if (inputs instanceof Array)
        inputs = inputs[0];
    if ((!inputs || (inputs && inputs.tags && inputs.tags.length<1)) && !mex.fetched_inputs) {
        BQApp.setLoading('Fetching inputs...');
        if (inputs) {
            // in case we have outputs URL
            BQFactory.request({
                uri : inputs.uri,
                uri_params : { view: 'deep'},
                cb : callback(this, function(doc) {
                    BQApp.setLoading(false);
                    inputs.tags = doc.tags;
                    mex.fetched_inputs = true;
                    mex.dict = null;
                    mex.afterInitialized();
                    this.setupUI_outputs(key, mex);
                }),
                errorcb: callback(this, 'onerror'),
                cache : false
            });
        } else {
            // we have nothing to start with, fetch the whole MEX deep
            BQFactory.request({
                uri : mex.uri,
                uri_params : { view: 'deep'},
                cb : callback(this, function(doc) {
                    BQApp.setLoading(false);
                    mex = doc;
                    this.setupUI_outputs(key, mex);
                }),
                errorcb: callback(this, 'onerror'),
                cache : false
            });
        }
        return;
    }
    */

    // outputs must be present
    var outputs = mex.find_tags('outputs');
    if (outputs instanceof Array)
        outputs = outputs[0];

    // in case with no outputs but present sub-mexs (mex fetched with at least "full"), this might be malformed MEX
    // create an output to at least show sub-mexs
    if (!outputs && mex.children.length>0) {
        // create outputs tag with mex renderer inside
        outputs = new BQTag(undefined, 'outputs');
        mex.tags.push(outputs);
        mex.fetched_outputs = true;
        //var t = new BQTag(undefined, 'mex_renderer', mex.uri, 'mex');
        //outputs.tags.push(t);
    }

    // ensure outputs
    if ((!outputs || (outputs && outputs.tags && outputs.tags.length<1)) && !mex.fetched_outputs) {
        BQApp.setLoading('Fetching results...');
        if (outputs) {
            // in case we have outputs URL
            BQFactory.request({
                uri : outputs.uri,
                uri_params : { view: 'deep'},
                cb : callback(this, function(doc) {
                    BQApp.setLoading(false);
                    outputs.tags = doc.tags;
                    mex.fetched_outputs = true;
                    mex.dict = null;
                    mex.afterInitialized();
                    this.setupUI_outputs(key, mex);
                }),
                errorcb: callback(this, 'onerror'),
                cache : false
            });
        } else {
            // we have nothing to start with, fetch the whole MEX deep
            BQFactory.request({
                uri : mex.uri,
                uri_params : { view: 'deep'},
                cb : callback(this, function(doc) {
                    BQApp.setLoading(false);
                    mex = doc;
                    this.setupUI_outputs(key, mex);
                }),
                errorcb: callback(this, 'onerror'),
                cache : false
            });
        }
        return;
    }

    // ensure we fetched names of iterable variables
    var execute_options = mex.find_tags('execute_options');
    if (execute_options && !mex.iterables && !mex.fetched_execute_options ) {
        BQFactory.request({
            uri : execute_options.uri,
            uri_params : { view: 'deep'},
            cb : callback(this, function(doc) {
                mex.fetched_execute_options = true;
                execute_options.tags = doc.tags;
                mex.dict = undefined;
                mex.afterInitialized();
                this.setupUI_outputs(key, mex);
            }),
            errorcb: callback(this, 'onerror'),
            cache : false
        });
        return;
    }

    // inputs must be present in sub-mexs
    if (mex.iterables && mex.children && (mex.children.length<1 || !mex.children[0].inputs) && !this.fetched_inputs) {
        BQFactory.request({
            uri : mex.uri+'/mex',
            uri_params : { view: 'inputs'},
            cb : callback(this, function(doc) {
                this.fetched_inputs = true;
                var sub = null,
                    subsub = null;
                // for every sub-mex
                for (var i=0; (sub=mex.children[i]); ++i) {
                    // update inputs
                    for (var j=0; (subsub=doc.children[j]); ++j) {
                        if (sub.uri == subsub.uri) {
                            Array.prototype.push.apply(sub.tags, subsub.tags);
                            sub.dict = null;
                            sub.afterInitialized();
                            break;
                        }
                    }
                }
                mex.dict = null;
                mex.afterInitialized();
                this.setupUI_outputs(key, mex);
            }),
            errorcb: callback(this, 'onerror'),
            cache : false
        });
        return;
    }

    // dima: some old stuff
    this.outputs = mex.outputs;
    this.outputs_index  = mex.outputs_index;

    // setting up renderers
    this.renderers[key] = this.renderers[key] || {};
    var my_renderers = this.renderers[key];

    var outputs_definitions = this.ms.module.outputs;
    var outputs = this.outputs;
    var outputs_index = this.outputs_index;
    if (!outputs || !outputs_index) return;
    if (!outputs_definitions || outputs_definitions.length<=0) return;

    // create renderers for each outputs element
    if (outputs_definitions && outputs_definitions.length>0)
    for (var p=0; (i=outputs_definitions[p]); p++) {
        this.setupUI_output(i, outputs_index, my_renderers, mex);
    }
};

BQWebApp.prototype.setupUI_output_sub = function (w, i, outputs_index, my_renderers, mex) {
    var n = i.name;
    var r = outputs_index[n];
    if (!r) return;
    var t = (r.type || i.type || i.resource_type).toLowerCase();
    if (t in BQ.renderers.resources) {
        var conf = {
            definition: i,
            resource: r,
            mex: mex,
        };

        // special case if the output is a dataset, we expect sub-Mexs
        if (this.mex.iterables && n in this.mex.iterables) { // && r.type=='dataset'
            this.mex.findMexsForIterable(n, 'outputs/');
            if (Object.keys(this.mex.iterables[n]).length>0) {
                conf.title = 'Select a thumbnail to see individual results:';
                conf.listeners = {
                  scope: this,
                  selected: function(resource) {
                       var suburl = resource.uri;
                       var submex = this.mex.iterables[n][suburl];
                       this.showOutputs(submex, 'outputs-sub');
                  },
                };
            }
        }

        my_renderers[n] = Ext.create(BQ.renderers.resources[t], conf);
        w.add(my_renderers[n]);
    }
};

BQWebApp.prototype.setupUI_outputs_sub = function (key, mex) {
    this.renderers[key] = this.renderers[key] || {};
    var my_renderers = this.renderers[key];

    var outputs_definitions = this.ms.module.outputs;
    var outputs = this.outputs;
    var outputs_index = this.outputs_index;
    if (!outputs || !outputs_index) return;
    if (!outputs_definitions || outputs_definitions.length<=0) return;


    var w = Ext.create('Ext.window.Window', {
      modal: true,
      width: BQApp?BQApp.getCenterComponent().getWidth()*0.95:document.width*0.95,
      height: BQApp?BQApp.getCenterComponent().getHeight()*0.95:document.height*0.95,
      buttonAlign: 'center',
      autoScroll: true,
      defaults: {border: 0, },
      border: 0,
      //loader: { url: url, renderer: 'html', autoLoad: true },
      //buttons: [ { text: 'Ok', handler: function () { .close(); } }]
    });

    // create renderers for each outputs element
    if (outputs_definitions && outputs_definitions.length>0)
    for (var p=0; (i=outputs_definitions[p]); p++)
        this.setupUI_output_sub(w, i, outputs_index, my_renderers, mex);
    w.show();
};

BQWebApp.prototype.clearUI_outputs = function (key) {
    key = key || 'outputs';
    if (!this.renderers[key]) return;
    var my_renderers = this.renderers[key];
    for (var p in my_renderers) {
        var i = my_renderers[p];
        if (i) {
            i.destroy();
            delete my_renderers[p];
        }
    }
};

BQWebApp.prototype.clearUI_outputs_all = function () {
    if (!this.renderers) return;
    for (var k in this.renderers) {
        this.clearUI_outputs(k);
        delete this.renderers[k];
    }
};

BQWebApp.prototype.updateResultsVisibility = function (vis) {
    this.status_panel.setVisible(false);
    if (!vis) {
        if (this.holder_result) this.holder_result.hide();
        var result_label = document.getElementById("webapp_results_summary");
        if (result_label) result_label.innerHTML = '<h3>No results yet...</h3>';
    }
};

BQWebApp.prototype.inputsValid = function () {
    var valid=true;
    var inputs = this.ms.module.inputs;
    if (inputs && inputs.length>0)
    for (var p=0; (i=inputs[p]); p++) {
        var renderer = i.renderer;
        if (renderer)
            //valid = valid && renderer.validate();
            valid = renderer.validate() && valid; // make this run for all inputs and validate them all
    }
    return valid;
};

//------------------------------------------------------------------------------
// Run
//------------------------------------------------------------------------------

BQWebApp.prototype.run = function () {
    var button_run = document.getElementById("webapp_run_button");
    if (button_run.childNodes[0].nodeValue != this.label_run) {
        // already running => try to stop the run
        if (this.current_mex_uri) {
            button_run.childNodes[0].nodeValue = "Stopping ...";
            this.ms.stop(this.current_mex_uri);
        }
        return;
    }

    if (!BQSession.current_session || !BQSession.current_session.hasUser()) {
        BQ.ui.warning('You are not logged in! You need to log-in to run any analysis...');
        BQ.ui.tip('webapp_run_button', 'You are not logged in! You need to log-in to run any analysis...');
        return;
    }
    if (!this.inputsValid()) return;

    this.clearUI_outputs_all();
    this.updateResultsVisibility(false);
    this.mex = undefined;

    button_run.childNodes[0].nodeValue = "STOP";

    this.ms.run();
};

BQWebApp.prototype.onstarted = function (mex) {
    if (!mex) return;
    this.current_mex_uri = mex.uri;
    window.location.hash = 'mex=' + mex.uri;
    //window.location.hash
    //history.pushState({mystate: djksjdskjd, }, "page 2", "bar.html");
};

BQWebApp.prototype.onprogress = function (mex) {
    if (!mex) return;
    if (!(mex instanceof BQMex)) return;
    var status_field = document.getElementById("webapp_status_text");
    //if (mex.status == "FINISHED" || mex.status == "FAILED") return;

    if (!mex.isMultiMex()) {
        status_field.innerHTML = "Progress: " + mex.status;
        return;
    }

    // ok, we're doing a parallel run, let's show status for all sub-mexes
    this.status_panel.setVisible(true);
    var iterable = mex.iterables ? mex.iterables[0] : null;
    for (var i=0; (o=mex.children[i]); i++) {
        if (o instanceof BQMex) {
            var status = o.value || o.status || 'initializing';
            var uri    = o.dict['inputs/'+iterable] || o.uri;
            var name   = uri; //this.getResourceNameByUrl(uri) || uri;

            var r = this.status_store.findRecord( 'resource', uri );
            if (r) {
                r.beginEdit();
                r.set( 'name', name );
                r.set( 'status', status );
                r.endEdit(true);
                r.commit();
            } else {
                r = this.status_store.add( {resource: uri, name: name, status: status, } );
            }
        }
    }
};

//------------------------------------------------------------------------------
// getting results
//------------------------------------------------------------------------------

BQWebApp.prototype.done = function (mex) {
    this.onprogress(mex);
    var button_run = document.getElementById("webapp_run_button");
    button_run.childNodes[0].nodeValue = this.label_run;
    var status_field = document.getElementById("webapp_status_text");
    status_field.innerHTML = this.label_progress;
    //this.status_panel.setVisible(false);
    this.mex = mex;
    this.parseResults(mex);
};

BQWebApp.prototype.getRunTimeString = function (tags) {
    if (!tags['start-time'] || !tags['end-time'])
        return 'a couple of moments';

    var t1 = tags['start-time'];
    var t2 = tags['end-time'];
    if (t1 instanceof Array) t1 = t1[0];
    if (t2 instanceof Array) t2 = t2[0];

    var start = new Date();
    var end   = new Date();
    start.setISO8601(t1);
    end.setISO8601(t2);
    var elapsed = new DateDiff(end - start);
    return elapsed.toString();
};

BQWebApp.prototype.parseResults = function (mex) {
    // dima: add here deep fetch of teh "outputs" tag
    this.showOutputs(mex);
    // Update module run info
    if (mex.status == "FINISHED") {
        var result_label = document.getElementById("webapp_results_summary");
        if (result_label) {
            result_label.innerHTML = '<h3 class="good">The module ran in ' + this.getRunTimeString(mex.dict)+'</h3>';
        }
        if (!this.mex_mode) BQ.ui.notification('Analysis done! Verify results...');
    }
};

BQWebApp.prototype.showOutputs = function (mex, key) {
    if (!mex) {
        BQ.ui.warning('No outputs to show');
        return;
    }
    if (typeof mex === 'string' || mex instanceof String) {
        //dima: fetch mex view=outputs and call showOutputs again
        BQFactory.request({
            uri : mex,
            uri_params : { view: 'full'},
            cb : callback(this, function(doc) { this.showOutputs(doc, key); } ),
            errorcb: callback(this, 'onerror'),
            cache : false
        });
        return;
    }
    this.clearUI_outputs(key);

    if (mex.status == "FINISHED") {
        // setup output renderers
        this.setupUI_outputs(key, mex);
    } else if (mex.status == "FAILED") {
        var message = "Module execution failure:<br>" + mex.toXML();
        if ('error_message' in mex.dict && mex.dict.error_message!='')
            message = "The module reported an internal error:<br>" + mex.dict.error_message;
        else
        if ('http-error' in mex.dict)
            message = "The module reported an internal error:<br>" + mex.dict['http-error'];

        BQ.ui.error(message);
        var result_label = document.getElementById("webapp_results_summary");
        if (result_label)
            result_label.innerHTML = '<h3 class="error">'+ message+'</h3>';
    } else {
        BQ.ui.notification('You are visualizing analysis which is currently in progress...', 25000);
        var result_label = document.getElementById("webapp_results_summary");
        if (result_label)
            result_label.innerHTML = '<h3>Selected analysis is still running, wait for it to complete...</h3>';
        // init properly
        this.onstarted(mex);
        // ensure button is showing "STOP"
        var button_run = document.getElementById("webapp_run_button");
        button_run.childNodes[0].nodeValue = "STOP";
        if (this.ms) {
            this.ms.checkMexStatus(mex);   // keep updating mex status
        }
    }
};

