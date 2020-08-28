/*******************************************************************************

  ModuleService is used by mini-apps for communication with the module server

  Tests the existance of the global var containing module def XML:
      module_definition_xml

  Possible configurations:
    onloaded   -
    onstarted  -
    ondone     -
    onprogress -
    onerror    -

  Example:



*******************************************************************************/

//----------------------------------------------------------------------------------
// misc
//----------------------------------------------------------------------------------

function ensureTrailingSlash(s) {
    if (s[s.length-1] === '/') return s;
    return s+'/';
}

function removeTrailingSlash(s) {
    if (s[s.length-1] != '/') return s;
    return s.substring(0, s.length-1);
}

//----------------------------------------------------------------------------------
// ModuleService - BQModuleConnector
//----------------------------------------------------------------------------------

function ModuleService(module_URI, conf) {
    this.URI = removeTrailingSlash(module_URI);
    this.conf = conf || {};
    module_definition_xml = undefined;

    // this global variable may be defined by the template and contain the module definition XML
    if (typeof module_definition_xml != 'undefined') {
        this.setModule( BQFactory.parseBQDocument(module_definition_xml) );
    } else {
        // fetch it otherwise
        BQFactory.request({
            uri: this.URI+'/definition',
            cb: callback(this, 'setModule'),
            errorcb: callback(this, 'onerror'),
            cache: false,
            uri_params : { view: 'deep' },
        });
    }
}

ModuleService.prototype.setModule = function (module) {
    this.module = module;
    if (!this.module) {
        var message = "Module you are trying to load could not be found on the host system!\nPlease inform your bisque sysadmin!";
        this.emit_error(message);
        return;
    }

    if (this.conf.onloaded)
        this.conf.onloaded(this);
};

ModuleService.prototype.run = function (parameters) {
    var mex = this.module.createMEX();
    mex.save_(ensureTrailingSlash(this.URI) + 'execute', callback(this, 'onstarted'), callback(this, 'onerror'));
};

ModuleService.prototype.stop = function (mex_uri) {
    var url = mex_uri.split('/');
    BQFactory.request ({
                uri : ensureTrailingSlash(this.URI) + 'kill/' + url[url.length-1],
                uri_params : {},
                method : 'post',
                errorcb: callback(this, this.onerror),
                cache : false,
    });
};

ModuleService.prototype.onstarted = function (mex) {
    if (this.conf.onstarted) this.conf.onstarted(mex);
    this.checkMexStatus(mex);
};

ModuleService.prototype.checkMexStatus = function (mex) {
    var me = this;
    if (mex.status=="FINISHED" || mex.status=="FAILED") {
        if (this.conf.ondone) {
            //this.conf.ondone(mex);
            BQFactory.request ({
                uri : mex.uri,
                uri_params : { view: 'full' }, // we request full to see the sub mexs if present
                cb : function(doc) {
                    me.conf.ondone(doc);
                },
                errorcb: callback(this, this.onerror),
                cache : false,
            });
        }
    } else {
        if (this.conf.onprogress)
            this.conf.onprogress(mex);
        setTimeout (function () {
            me.requestMexStatus(mex.uri);
        }, 5000);
    }
};

ModuleService.prototype.requestMexStatus = function(mex_uri) {
    BQFactory.request ({
        uri : mex_uri,
        uri_params : { view: 'full' }, // we request full to see the sub mexs if present
        cb : callback(this, this.checkMexStatus),
        errorcb: callback(this, this.onerror),
        cache : false,
    });
};

ModuleService.prototype.emit_error = function(message) {
    if (this.conf.onerror)
        this.conf.onerror(message);
    else
        alert(message);
};

ModuleService.prototype.onerror = function(o) {
    if (typeof(o)=='string')
        this.emit_error(o);
    else
        this.emit_error(o.message_short || o.message || o['http-error'] || 'communication error');
};

