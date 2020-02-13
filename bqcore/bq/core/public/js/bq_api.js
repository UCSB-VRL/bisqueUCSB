/*-----------------------------------------------------------------------------
 BQAPI - JavaScript Bisque API

 dima: problems i see today
   1) no way to tell if object is completely loaded or needs additional fetches
   2) lot's of repeated functions: load_tags, loadTags, etc...
   3) some objects have non-standard attributes: BQAuth
-----------------------------------------------------------------------------*/

Ext.namespace('BQ.api');

BQTypeError = new Error("Bisque type error");
BQOperationError = new Error("Bisque operation error");

/* //dima - not being used, hiding from the parser
classExtend = function(subClass, baseClass) {
   function inheritance() {}
   inheritance.prototype = baseClass.prototype;

   subClass.prototype = new inheritance();
   subClass.prototype.constructor = subClass;
   subClass.baseConstructor = baseClass;
   subClass.superClass = baseClass.prototype;
}
*/

default_error_callback = function (o) {
    console.log(o.message);
    BQ.ui.error(o.message);
};

//-----------------------------------------------------------------------------
// BQFactory for creating Bisque Objects
//-----------------------------------------------------------------------------

function BQFactory (){}

BQFactory.objects =  {
                       vertex   : BQVertex, // dima: speed optimization, using xpath for sub vertices is much faster
                       value    : BQValue,  // dima: speed optimization, using xpath for sub values is much faster
                       tag      : BQTag,
                       image    : BQImage,
                       file     : BQFile,
                       gobject  : BQGObject,
                       point    : BQGObject,
                       rectangle: BQGObject,
                       square   : BQGObject,
                       ellipse  : BQGObject,
                       circle   : BQGObject,
                       polygon  : BQGObject,
                       polyline : BQGObject,
                       line     : BQGObject,
                       label    : BQGObject,
                       module   : BQModule,
                       mex      : BQMex,
                       session  : BQSession,
                       user     : BQUser,
                       auth     : BQAuth,
                       dataset  : BQDataset,
                       resource : BQResource,
                       template : BQTemplate,
                       dir      : BQDir,
};

BQFactory.ctormap =  {
                       //vertex  : BQVertex, // dima: speed optimization, using xpath for sub vertices is much faster
                       //value   : BQValue,  // dima: speed optimization, using xpath for sub values is much faster
                       tag      : BQTag,
                       image    : BQImage,
                       file     : BQFile,
                       gobject  : BQGObject,
                       point    : BQGObject,
                       rectangle: BQGObject,
                       square   : BQGObject,
                       ellipse  : BQGObject,
                       circle   : BQGObject,
                       polygon  : BQGObject,
                       polyline : BQGObject,
                       line     : BQGObject,
                       label    : BQGObject,
                       module   : BQModule,
                       mex      : BQMex,
                       session  : BQSession,
                       user     : BQUser,
                       auth     : BQAuth,
                       dataset  : BQDataset,
                       resource : BQResource,
                       template : BQTemplate,
                       dir      : BQDir,
};

BQFactory.ignored = {
    vertex  : BQVertex,
    value   : BQValue,
};

BQFactory.escapeXML = function(xml) {
    var specials = [ [ /</g,  "&lt;"],
                     [ />/g,  "&gt;"],
                     [ RegExp("'", 'g') , '&#039;'],
                     [ RegExp('"','g') ,  '&quot;']
                   ] ;
    // Replace Bare & (not followed
    xml = String(xml).replace (/&/g, '&amp;');
    specials.every (function (pair) {
        xml = xml.replace (pair[0], pair[1]);
        return true;
    });
    return xml;
};

BQFactory.session = {};

BQFactory.make = function(ty, uri, name, value) {
    var ctor = BQResource;
    if (ty in BQFactory.ctormap)
        ctor = BQFactory.ctormap[ty];
    var o = new ctor(uri);
    if (ctor == BQResource && ty) o.resource_type = ty;
    o.name = name;
    o.value = value;
    return o;
};

BQFactory.makeShortCopy = function(resource) {
    var ty = resource.resource_type,
        ctor = BQResource;
    if (ty in BQFactory.objects)
        ctor = BQFactory.objects[ty];
    var o = new ctor();
    if (ctor == BQResource && ty) o.resource_type = ty;
    //o.name = name;
    //o.value = value;

    var a = undefined;
    for (var i=0; (a=resource.xmlfields[i]); i++)
        o[a] = resource[a];
    return o;
};

BQFactory.createFromXml = function(xmlResource, resource, parent) {
    var stack = [];
    var resources = [];
    //  Initialize stack with a tuple of
    //    1. The XML node being parsed
    //    2. The current resource being filled out
    //    3. The parent resource if any
    stack.push ([xmlResource, resource, parent]);
    while (stack.length != 0) {
        var elem = stack.shift();
        var node = elem[0];
        var resource  = elem[1];
        var parent = elem[2];
        var type_ = node.nodeName;
        if (resource == null){
            if (type_ == 'resource')
               type_ = attribStr(node, 'type');
            resource = BQFactory.make(type_);
        }
        resource.initializeXml(node);
        resources.push (resource);
        if (parent) {
            resource.setParent(parent) ;
            resource.doc = parent.doc;
        }
        for (var i=0; i < node.childNodes.length; i++ ) {
            var k = node.childNodes[i];
            if (k.nodeType == 1 &&  ! (k.nodeName in BQFactory.ignored)) // Element nodes ONLY
                stack.push ( [ k, null, resource ]);
            //else
            //    console.log ("Got Node type" + k.nodeType + " for " + k.text);
        }
    }

    response = resources[0];

    // dima: do some additional processing after you inited elements
    var rr = resources.reverse();
    for (var p=0; (r=rr[p]); p++)
        if (r.afterInitialized) r.afterInitialized();

    return response;
};


/**
 * Load a Bisque URL as an object. Calls cb (loaded_object) when done.
 * Checks for both outstanding ajax requests and previously loaded objects.
 */
BQFactory.load = function(uri, cb, progresscb, cache) {
    BQFactory.request({ uri : uri,
                        cb  : cb,
                        progresscb: progresscb,
                        cache : cache});
};

BQFactory.request = function(params) {
    var uri =  params.uri;
    var url_params = params.uri_params;
    var cb  =  params.cb;
    var progresscb = params.progresscb;
    var cache = (typeof params.cache=="undefined")?true:false;
    var method = params.method || "get";
    var xmldata = params.xmldata;
    params.errorcb = params.errorcb || default_error_callback;

    if (url_params) {
        var pl = [];
        var v;
        for (var x in url_params) {
            if (url_params[x]) {
                v = encodeURIComponent(url_params[x]);
                pl.push(x+'='+v);
            } else {
                pl.push(x);
            }
        }
        if ( uri.indexOf('?')==-1 )
            uri = uri + '?' + pl.join('&');
        else
            uri = uri + '&' + pl.join('&');
    }

    console.log ("Loading: " + uri);
    if (! uri) {
        console.log("ERROR: trying to load null uri");
    }
    // if (cache && uri in BQFactory.session) {
    //     var o = BQFactory.session[uri];
    //     if (o instanceof XMLHttpRequest) {
    //         console.log ("outstanding request");
    //         if (cb)
    //             chainRequest(o, callback(BQFactory, 'loaded_callback', uri, cb));
    //     } else {
    //         //console.log ("using cache result");
    //         //if (cb) cb(o);
    //         // Just redo the request
    //         console.log ('re-issuing cached result ' + uri);
    //         BQFactory.session[uri] = xmlrequest(uri, callback(BQFactory, 'on_xmlresponse', params), method, xmldata, params.errorcb);
    //     }
    // } else {
        BQFactory.session[uri] = xmlrequest(uri, callback(BQFactory, 'on_xmlresponse', params), method, xmldata, params.errorcb);
//}
};

BQFactory.loaded_callback = function (uri, cb, xmldoc) {
    console.log ("Loaded callback for " + uri);
    var o = BQFactory.session[uri];
    cb (o);
};

BQFactory.on_xmlresponse = function(params, xmldoc) {
    var uri = params.uri;
    var cb  = params.cb;
    var errorcb = params.errorcb;

    console.log('Response: ' + uri);
    try {
        var n = xmldoc.firstChild;
        if (!n) return null;
        if (n.nodeName == 'response')
        n = n.firstChild;
        if (!n) return null;
        var ty = n.nodeName;
        if (ty=='resource') ty = attribStr(n, 'type');
        var bq = BQFactory.make (ty, uri);
        BQFactory.createFromXml(n, bq, null);
        BQFactory.session[uri] = bq;
    } catch  (err) {
        console.log ("on_xmlresponse error" + err);
        if (errorcb) errorcb ({ xmldoc : xmldoc, message : 'parse error in BQFactory.on_xmlresponse' });
        return;
    }
    if (cb) {
        return cb(bq);
    }
    if (params.cb_xml) {
        return params.cb_xml(bq, xmldoc);
    }
};

BQFactory.parseBQDocument = function (xmldoc) {
    if ((typeof xmldoc)==='string') {
        var parser  = new DOMParser ();
        xmldoc = parser.parseFromString(xmldoc, "text/xml");
    }
    n = xmldoc;
    if (!(n.nodeName in BQFactory.objects)) {
        var n = xmldoc.firstChild;
        if (!n) return null;
    }
    if (n.nodeName == 'response')
        n = n.firstChild;
    if (!n) return null;
    var ty = n.nodeName;
    var bq = BQFactory.make (ty);
    BQFactory.createFromXml(n, bq, null);
    return bq;
};

//-----------------------------------------------------------------------------
// BQValue
//-----------------------------------------------------------------------------

function parseValueType(v, t) {
    try {
        if (t && typeof v === 'string' && t == 'number')
            return parseFloat(v);
        else if (t && t == 'boolean')
            return (v=='true') ? true : false;
    } catch(err) {
        return v;
    }
    return v;
};

function BQValue (t, v, i) {
    this.resource_type = "value";
    this.xmlfields = [ 'type', 'index' ];
    if (Ext.isElement(t) && arguments.length==1) {
        this.initializeXml(t);
        return;
    }

    if (t != undefined) this.type = t;
    if (v != undefined) this.value = parseValueType(v, this.type);
    if (i != undefined) this.index = i;
};
BQValue.prototype = new BQXml();

BQValue.prototype.initializeXml = function (node) {
    this.type  = attribStr(node, 'type');
    this.value = parseValueType(node.textContent || node.text, this.type);
    this.index = attribInt(node, 'index');
};

BQValue.prototype.setParent = function (p) {
    p.values = p.values || [];
    p.values.push(this);
};

BQValue.prototype.xmlNode = function () {
    return BQXml.prototype.xmlNode.call (this, this.value); // dima: migrated to DOM based creation
};


//-----------------------------------------------------------------------------
// BQVertex
//-----------------------------------------------------------------------------

function BQVertex(x, y, z, t, ch, index) {
    this.resource_type = "vertex";
    this.xmlfields = [ 'x', 'y', 'z', 't', 'ch', 'index' ];
    if (Ext.isElement(x) && arguments.length==1) {
        this.initializeXml(x);
        return;
    }
    this.x =x;
    this.y =y;
    this.z =z;
    this.t =t;
    this.ch =ch;
    this.index = index;
};
BQVertex.prototype = new BQXml();

BQVertex.prototype.setParent = function (p) {
    p.vertices = p.vertices || [];
    p.vertices.push(this);
};

BQVertex.prototype.initializeXml = function (node) {
    this.x     = attribFloat(node, "x");
    this.y     = attribFloat(node, "y");
    this.z     = attribFloat(node, "z");
    this.t     = attribFloat(node, "t");
    this.ch    = attribInt(node, "ch");
    this.index = attribInt(node, "index");
};

BQVertex.prototype.clone = function () {
    return new BQVertex(this.x, this.y, this.z, this.t, this.ch, this.index);
};

BQVertex.prototype.add = function (p) {
    var v = this.clone();
    if (p.x) v.x += p.x;
    if (p.y) v.y += p.y;
    if (p.z) v.z += p.z;
    if (p.t) v.t += p.t;
    return v;
};

BQVertex.prototype.sub = function (p) {
    var v = this.clone();
    if (p.x) v.x -= p.x;
    if (p.y) v.y -= p.y;
    if (p.z) v.z -= p.z;
    if (p.t) v.t -= p.t;
    return v;
};

BQVertex.prototype.mul = function (p) {
    var v = this.clone();
    if (p.x) v.x *= p.x;
    if (p.y) v.y *= p.y;
    if (p.z) v.z *= p.z;
    if (p.t) v.t *= p.t;
    return v;
};

BQVertex.prototype.div = function (p) {
    var v = this.clone();
    if (p.x) v.x /= p.x;
    if (p.y) v.y /= p.y;
    if (p.z) v.z /= p.z;
    if (p.t) v.t /= p.t;
    return v;
};


//-----------------------------------------------------------------------------
// BQXml
//-----------------------------------------------------------------------------

function BQXml() {
    this.resource_type = '';
    this.xmlfields = [];
};

BQXml.prototype.toXML = function () {
    var doc = this.xmlNode (),
        serializer = new XMLSerializer();
    return serializer.serializeToString(doc);
};

/*
BQXml.prototype.xmlNode = function (content) {
    var tag_name = 'resource';

    var v = '<';
    if (this.resource_type in BQFactory.objects) {
        v += this.resource_type + ' ';
        tag_name = this.resource_type;
    } else {
        v += 'resource resource_type="'+this.resource_type+'" ';
    }
    var fields = this.xmlfields;
    for (var f in fields ){
        if (this[fields[f]] != undefined  &&  this[fields[f]] != null )
        v += (fields[f] + '="' + BQFactory.escapeXML(this[fields[f]]) + '" ');
    }
    if (content && content != "") {
        v += ">";
        v += content;
        v += "</" + tag_name +">";
    } else {
        v += "/>";
    }

    return v;
};
*/

BQXml.prototype.xmlNode = function (content) {
    var tag_name = (this.resource_type in BQFactory.objects) ? this.resource_type : 'resource';
    var doc = document.implementation.createDocument('', tag_name);
    var resource = doc.childNodes[0];

    if (!(this.resource_type in BQFactory.objects)) {
        resource.setAttribute('resource_type', this.resource_type);
    }

    var fields = this.xmlfields;
    for (var f in fields ){
        if (this[fields[f]] !== undefined  &&  this[fields[f]] !== null )
            resource.setAttribute(fields[f], this[fields[f]]);
    }

    if (content && content !== '') { // && typeof content === 'string') {
        resource.textContent = content;
    } /* else if (content && content instanceof Document) {
        resource.appendChild( content.firstChild );
    } else if (content && content instanceof Node) {
        resource.appendChild( content );
    }*/

    if (this.values)
        for (var i=0; i < this.values.length; i++ )
            //xmlrep += this.values[i].xmlNode();
            resource.appendChild( this.values[i].xmlNode() );
    if (this.vertices)
        for (var i=0; i < this.vertices.length; i++ )
            //xmlrep += this.vertices[i].xmlNode();
            resource.appendChild( this.vertices[i].xmlNode() );
    if (this.tags)
        for (var i=0; i < this.tags.length; i++ )
             //xmlrep += this.tags[i].toXML();
             resource.appendChild( this.tags[i].xmlNode() );
    if (this.gobjects)
        for (var i=0; i < this.gobjects.length; i++ )
             //xmlrep += this.gobjects[i].toXML();
             resource.appendChild( this.gobjects[i].xmlNode() );
    if (this.children)
        for (var i=0; i < this.children.length; i++ )
            //xmlrep += this.children[i].toXML();
            resource.appendChild( this.children[i].xmlNode() );

    return resource;
};

//-----------------------------------------------------------------------------
// BQObject
// BQObject interface library for Image, Tags and GObjects.
// BQObject is base class for manipulation, and communication with
// the bisque system from javascript.
//-----------------------------------------------------------------------------

function BQObject (uri, doc) {
    BQXml.call(this, uri, doc);
    this.readonly = false;
    this.uri = stripParams(uri);
    this.doc = doc || this;

    this.children = [];
    this.tags     = [];
    this.gobjects = [];

    // object rationalization, any taggable may have values and vertices, use undefined to mark unfetched lists
    this.values   = undefined;
    this.vertices = undefined;

    this.dirty = true;
    this.created = true;
    this.mex = null;
    this.resource_type = 'resource';
    this.xmlfields  = [ 'type', 'name', 'value', 'uri', 'owner', 'permission', 'ts', 'resource_uniq', 'index', 'hidden'];
};
BQObject.prototype = new BQXml();

BQObject.prototype.initializeXml = function (node) {

    this.resource_type = attribStr(node, 'resource_type') || node.nodeName;
    this.type          = attribStr(node, 'type');
    this.name          = attribStr(node, 'name');
    this.value         = parseValueType(attribStr(node, 'value'), this.type);
    this.uri           = stripParams(attribStr(node, 'uri'));
    this.owner         = attribStr(node, 'owner');
    this.permission    = attribStr(node, 'permission');
    this.ts            = attribStr(node, 'ts');
    this.resource_uniq = attribStr(node, 'resource_uniq');
    this.index         = attribStr(node, 'index');
    this.hidden        = attribStr(node, 'hidden');
    this.attributes    = attribDict (node);
    this.dirty         = false;
    this.created       = false;
    this.template      = {};

    // dima: speed optimization, using xpath for resources with many values is much faster
    // Utkarsh : now uses evaulateXPath from utils.js, which is browser independent
    var values = BQ.util.xpath_nodes(node, 'value');
    this.values = [];

    // values should be an array
    for (var i=0; i<values.length; i++)
        this.values.push(new BQValue(values[i]));

    if (this.resource_uniq && this.uri) {
        this.src  = '/blob_service/' + this.resource_uniq;
        // in the case the data is coming from another server, make sure to load proper URL
        this.src = this.uri.replace(/\/data_service\/.*$/i, this.src);
    }
};

BQObject.prototype.afterInitialized = function () {
    // try to set template

    // first try to find a resource "template"
    var ta = this.find_children('template');
    if (ta && ta instanceof Array && ta.length>0)
        this.template = ta[0].toDict(true);
    else if (ta)
        this.template = ta.toDict(true);

    if (this.template) return;

    // then look for tags "template" - old style
    ta = this.find_tags('template');
    if (ta && ta instanceof Array && ta.length>0)
        this.template = ta[0].toDict(true);
    else if (ta)
        this.template = ta.toDict(true);
};


// dima: this function takes an array of strings or an object value_name - value_type and
//       sets as a new array of values in the resource
BQObject.prototype.setValues = function (vals) {
    if (this.readonly)
        throw "This object is read only!";

    this.values = [];
    if (vals instanceof Array) {
        for (var i=0; i<vals.length; i++)
            this.values.push(new BQValue(undefined, vals[i]));
    } else {
        for (var i in vals)
            this.values.push(new BQValue(vals[i], i));
    }
};

BQObject.prototype.testReadonly = function () {
  if (this.readonly)
      throw "This object is read only!";
};

BQObject.prototype.setParent = function (p) {
    p.children = p.children || [];
    p.children.push (this);
    this.parent = p;
};

BQObject.prototype.getkids = function (){
    // Note concat make new array
    var allkids = this.children.concat( this.tags, this.gobjects);
    return allkids;
};

BQObject.prototype.load = function (uri, cb) {
    this.uri = stripParams(uri);
    makeRequest(this.uri, callback(this, 'load_response', cb), null, "get");
};

BQObject.prototype.load_response = function (cb, ign, xmldoc) {
    // Reach past response object.
    //var node = xmldoc.firstChild.firstChild;
    var node = xmldoc.firstChild;
    if (node.nodeName == "response")
        node = node.firstChild;
    BQFactory.createFromXml(node, this, null);
    if (cb)
        cb(this);
};

/*
BQObject.prototype.toXML = function() {
    var xmlrep = '';
    if (this.values)
        for (var i=0; i < this.values.length; i++ )
            xmlrep += this.values[i].xmlNode();
    if (this.vertices)
        for (var i=0; i < this.vertices.length; i++ )
            xmlrep += this.vertices[i].xmlNode();
    if (this.tags)
        for (var i=0; i < this.tags.length; i++ )
             xmlrep += this.tags[i].toXML();
    if (this.gobjects)
        for (var i=0; i < this.gobjects.length; i++ )
             xmlrep += this.gobjects[i].toXML();
    if (this.children)
        for (var i=0; i < this.children.length; i++ )
            xmlrep += this.children[i].toXML();
    return this.xmlNode(xmlrep);
};
*/

BQObject.prototype.delete_ = function (cb, errorcb) {
    this.testReadonly();
    // Delete object from db
    if (this.uri != null) {
        xmlrequest(this.uri, callback(this, 'response_', 'delete', errorcb, cb), 'delete', null, errorcb);
    }
    else
        cb();
};

BQObject.prototype.rename = function(newName, cb, errorcb) {
    console.log ('BQAPI: BQObject.prototype.rename - Not implemented');
};

BQObject.prototype.deleteTag = function(childTag, cb, errorcb) {
    if (childTag instanceof BQTag)
    {
        this.remove(childTag);
        childTag.delete_(cb, errorcb);
    }
    else
        console.log ('BQAPI: deleteTag - Input is not a BQTag.');
};

BQObject.prototype.find_tags  = function (name, deep, found) {
    found = found || [];
    for (var i=0; i < this.tags.length; i++) {
        var t = this.tags[i];
        if (t.name == name)
            found.push( t );
        if (deep && t.tags.length >0 )
            t.find_tags (name, deep, found);
    }
    if (found.length == 0)
        return null;
    if (found.length == 1)
        return found[0];
    return found;
};

BQObject.prototype.find_children  = function (type, name, deep, found) {
    found = found || [];
    for (var i=0; i < this.children.length; i++) {
        var t = this.children[i];
        if (t.resource_type == type && (!name || name && t.name == name))
            found.push( t );
        if (deep && t.children.length >0 )
            t.find_children (type, name, deep, found);
    }
    if (found.length == 0)
        return null;
    if (found.length == 1)
        return found[0];
    return found;
};

// findTags         :   finds tags whose (input) attribute matches an input value
// config params    :
// attr         =   (required) which attribute to match e.g. name, type, resource_type etc.
// value        =   (required) matched value
// deep         =   (default false) if the search should be deep or not
// returnFirst  =   (default true) True to return first found instance otherwise returns all instances

BQObject.prototype.findTags = function(config)
{
    var found = [], currentObj;
    config.returnFirst = Ext.isDefined(config.returnFirst)?config.returnFirst:true;

    for (var i=0; i<this.tags.length; i++)
    {
        currentObj = this.tags[i];
        if (currentObj[config.attr] == config.value)
        {
            found.push(currentObj);
            if (config.returnFirst)
                break;
        }
        else if (config.deep)
            found = found.concat(currentObj.findTags(config));
    }

    return found;
};

BQObject.prototype.testAuth = function(user, cb, loaded, authRecord)
{
    if (!loaded)
        if (user == this.owner)
            cb('owner');
        else
            this.getAuth(Ext.bind(this.testAuth, this, [user, cb, true], 0));
    else
    {
        authRecord = authRecord.children;

        for (var i=0;i<authRecord.length;i++)
        {
            if (user.endsWith(authRecord[i].user))
            {
                if (authRecord[i].action=='edit' || authRecord[i].action=='owner')
                    cb(true);
                else
                    cb(false, authRecord[i].action);
                return;
            }
        }

        // no user matching the uri was found
        cb(false);
    }
};

BQObject.prototype.getAuth = function(cb, loaded, authRecord)
{
    if (!loaded)
    {
        BQFactory.request({
            uri :   this.uri + '/auth',
            cb  :   Ext.bind(this.getAuth, this, [cb, true], 0)
        });
    }
    else
        cb(authRecord);
};

BQObject.attributes_skip = { 'uri':undefined, 'src':undefined, 'permission':undefined,
                             'ts':undefined, 'owner':undefined, 'parent':undefined,
                             'doc':undefined, 'mex':undefined,  };
BQObject.types_skip = { 'template':undefined, };

function clean_resources(resource, skiptemplate) {
    // remove undesired attributes
    for (var i in resource)
        if (i in BQObject.attributes_skip || (skiptemplate && i=='template'))
            delete resource[i];

    // remove old style template - kept for compatibility, should disappear in the future
    if (skiptemplate && resource.tags) {
        var p=resource.tags.length-1;
        while (p>=0) {
            var t = resource.tags[p];
            if (t.type in BQObject.types_skip)
                resource.tags.splice(p, 1);
            p--;
        }
    }

    // remove template objects
    if (skiptemplate && resource.children) {
        var p=resource.children.length-1;
        while (p>=0) {
            var t = resource.children[p];
            if (t && t.resource_type in BQObject.types_skip)
                resource.children.splice(p, 1);
            p--;
        }
    }

    var r = undefined;
    for (var p=0; (r=resource.tags[p]); p++)
        clean_resources(r, skiptemplate);

    for (var p=0; (r=resource.gobjects[p]); p++)
        clean_resources(r, skiptemplate);

    for (var p=0; (r=resource.children[p]); p++)
        clean_resources(r, skiptemplate);
};

BQObject.prototype.clone = function (skiptemplate) {
    var resource = BQ.util.clone(this, skiptemplate);
    clean_resources(resource, skiptemplate);
    return resource;
};

BQObject.prototype.toDict  = function (deep, found, prefix) {
    deep = deep || false;
    found = found || {};
    prefix = prefix || '';

    var t=null;
    for (var p=0; (t=this.tags[p]); p++) {

        var values = undefined;
        if (t.values && t.values.length>0) {
            values = [];
            for (var i=0; (v=t.values[i]); i++)
               values.push(v.value);
        }

        if (!(prefix+t.name in found)) {
            found[prefix+t.name] = values?values:t.value;
        } else {
            if (found[prefix+t.name] instanceof Array) {
                if (!values)
                    found[prefix+t.name].push(t.value);
                else
                    found[prefix+t.name] = found[prefix+t.name].concat(values);
            } else {
                if (!values)
                    found[prefix+t.name] = [ found[prefix+t.name], t.value ];
                else {
                    found[prefix+t.name] = [ found[prefix+t.name] ];
                    found[prefix+t.name] = found[prefix+t.name].concat(values);
                }
            }
        }

        if (deep && t.tags.length >0 )
            t.toDict (deep, found, prefix+t.name+'/');
    }
    return found;
};

BQObject.prototype.toNestedDict1 = function(deep)
{
    var dict = {}, tag;

    if (!isEmptyObject(this.template))
        dict['_template'] = this.template;

    if (this.tags.length==0)
        return this.value || '';

    for(var i = 0; i < this.tags.length; i++)
    {
        tag = this.tags[i];
        dict[tag.name] = (deep && tag.tags.length > 0) ? tag.toNestedDict(deep) : (tag.value || '');
    }

    return dict;
};

BQObject.prototype.toNestedDict = function(deep)
{
    var data = {}, tags = {};

    Ext.apply(data,
    {
        name        :   this.name,
        value       :   this.value || '',
    });

    if (!isEmptyObject(this.template))
        data['template'] = this.template;

    if (deep)
        for(var i = 0; i < this.tags.length; i++)
            tags[this.tags[i].name] = this.tags[i].toNestedDict(deep);

    return {data:data, tags:tags};
};

BQObject.prototype.fromNestedDict = function(dict)
{
    Ext.apply(this, dict.data);

    for (var tag in dict.tags)
        this.addtag().fromNestedDict(dict.tags[tag]);
};

BQObject.prototype.fromNestedDict1 = function(dict)
{
    var value;

    if (dict['_template'])  // check for template entry
    {
        this._template = dict['_template'];
        delete dict['_template'];
    }

    for (var tag in dict)
    {
        value = dict[tag];

        if (value instanceof Object)
            this.addtag({name:tag}).fromNestedDict(value);
        else
            this.addtag({name:tag, value:value});
    }
};

BQObject.prototype.create_flat_index = function ( index, prefix ) {
    index = index || {};
    prefix = prefix || '';

    var t=null;
    for (var p=0; (t=this.tags[p]); p++) {
        if (!(prefix+t.name in index))
            index[prefix+t.name] = t;

        if (t.tags.length >0)
            index = t.create_flat_index(index, prefix+t.name+'/');
    }
    return index;
};

// dima: not being used
BQObject.prototype.find_resource  = function (ty) {
    for (var i=0; i < this.children.length; i++)
        if (this.children[i].type == ty)
            return this.children[i];
    return null;
};

// dima: used in template, needs different name, e.g. remove_resource_by_uri ?
BQObject.prototype.remove_resource = function (uri) {
    for (var i=0; i < this.children.length; i++)
        if (this.children[i].uri == uri) {
            delete this.children[i];
            this.children.splice(i,1);
        }
    return null;
};

BQObject.prototype.remove = function (o) {
    var index = this.tags.indexOf (o);
    if (index!=-1) this.tags.splice(index,1);
    else {
      index = this.gobjects.indexOf (o);
      if (index!= -1) this.gobjects.splice(index,1);
      else {
          index = this.children.indexOf(o);
          if (index != -1) this.children.splice(index,1);
      }
    }
};

BQObject.prototype.save_ = function (parenturi, cb, errorcb, method) {
    this.testReadonly();
    var docobj = this.doc;
    var req = docobj.toXML();
    errorcb = errorcb || default_error_callback;
    if (docobj.uri) {
        xmlrequest(docobj.uri, callback(docobj, 'response_', 'update', errorcb, cb), method || 'put', req, errorcb);
    } else {
        if (this.resource_type in BQFactory.objects)
            parenturi = parenturi || '/data_service/'+this.resource_type+'/';
        else
            parenturi = parenturi || '/data_service/resource/';
        xmlrequest(parenturi, callback(docobj, 'response_', 'created', errorcb, cb), method || 'post', req, errorcb);
    }
};

BQObject.prototype.save_me = function (cb, errorcb) {
    console.log('save me');
    this.testReadonly();
    var req = this.toXML();
    errorcb = errorcb || default_error_callback;
    if (this.uri) {
        xmlrequest(this.uri, cb, 'put', req, errorcb);
    } else {
        var parenturi = this.parent.uri;
        if (this.resource_type in BQFactory.objects)
            parenturi = parenturi || '/data_service/'+this.resource_type+'/';
        else
            parenturi = parenturi || '/data_service/resource/';
        xmlrequest(parenturi, cb, 'post', req, errorcb);
    }
};

BQObject.prototype.save_ww = function (parenturi, cb, errorcb) {
    this.testReadonly();
    var obj = this;
    var req = obj.toXML();
    errorcb = errorcb || default_error_callback;
    if (obj.uri) {
        xmlrequest(obj.uri, callback(obj, 'response_', 'update', errorcb, cb),'put', req, errorcb);
    } else {
        parenturi = parenturi || '/data_service/'+this.resource_type+'/';
        xmlrequest(parenturi, callback(obj, 'response_', 'created', errorcb, cb),'post', req, errorcb);
    }
};

BQObject.prototype.save_reload = function(parenturi, cb, errorcb) {
    this.testReadonly();
    var obj = this;
    var req = obj.toXML();
    errorcb = errorcb || default_error_callback;
    obj.children = obj.tags = obj.gobjects = [];
    if (obj.uri) {
        xmlrequest(obj.uri + "?view=deep", callback(obj, 'response_', 'update', errorcb, cb), 'put', req, errorcb);
    } else {
        parenturi = parenturi || '/data_service/' + this.resource_type + '/';
        xmlrequest(parenturi + "?view=deep", callback(obj, 'response_', 'created', errorcb, cb), 'post', req, errorcb);
    }
};


// dima: used in browser factory, same thing as save but always does POST
BQObject.prototype.append = function (cb, errorcb)
{
    this.testReadonly();

    var docobj = this.doc;
    var req = docobj.toXML();

    xmlrequest(docobj.uri, callback(docobj, 'response_', 'update', errorcb, cb),'post', req, errorcb);
};

BQObject.prototype.response_ = function (code, errorcb, cb, xmldoc) {
    // The response with FAIL or the save URI is here
    //var  = xmldoc.firstChild.firstChild;

    var node = xmldoc;
    if (node.nodeName == "#document" || node.nodeName == "response")
        node = node.firstChild;
    if (code == "created") {
        //alert (printXML(respobj));
        //this.uri = attribStr (node, 'uri');
        this.children = [];
        this.tags = [];
        this.gobjects = [];
        try {
            BQFactory.createFromXml(node, this, null);
        } catch  (err) {
            console.log ("save_" + err);
            if (errorcb) errorcb ({ xmldoc : xmldoc, message : 'parse error in BQObject.response_' });
            return;
        }
    }
    if (cb != null) {
        cb (this);
    }
};


// Load tags should setup a resource if does not exist and mark
// it top level document.. then should move tags to top level object.
BQObject.prototype.load_tags = function (cb, url, progress) {
    if (!url) {
        if (this.uri)
            url = this.uri + "/tag";
        else {
            if (cb) cb();
            return;
        }
    }
    this.remove_resource (url);
    BQFactory.load (url + "?view=deep",
                    callback(this, 'loaded_tags', cb),
                    progress);
};


// load_children : function to facilitate progressive fetching of tags/gobjects etc.
// config params -
// attrib -- filter tag or gobject usually
// vector -- where the item are store .. tags, gobjects, or kids
// cb : callback
// progress : progress callback
// depth : 'full', 'deep', 'short' etc.
BQObject.prototype.load_children = function (config)
{
    Ext.apply(config,
    {
        attrib : config.attrib || 'tag',
        depth : config.depth || 'deep',
        vector : config.vector || 'tags',
        cb : config.cb || Ext.emptyFn
    });

    Ext.apply(config,
    {
        uri : config.uri || this.uri+'/'+config.attrib,
    });

    this.remove_resource(config.uri);

    BQFactory.request(
    {
        uri : config.uri+'?view='+config.depth,
        cb : Ext.bind(function(resource, config)
        {
            this[config.vector] = resource[config.vector];
            config.cb(resource[config.vector]);
        }, this, [config], true),
        progresscb : config.progress
    });
};

// dima: repeated from load_tags
BQObject.prototype.loadTags = function (config)
{
    config.attrib='tag';
    config.vector='tags';
    BQObject.prototype.load_children.call(this, config);
};

// dima: repeated from load_gobjects
BQObject.prototype.loadGObjects = function (config)
{
    config.attrib='gobject';
    config.vector='gobjects';
    BQObject.prototype.load_children.call(this, config);
};

BQObject.prototype.loaded_tags = function (cb, resource) {
    this.tags = resource.tags;
    if (cb) cb(resource.tags);
};

BQObject.prototype.load_gobjects = function (cb, url, progress) {
    if (!url) url = this.uri + "/gobject";
    this.remove_resource (url);
    BQFactory.load (url + "?view=deep",
                    callback(this, 'loaded_gobjects', cb),
                    progress);
};

BQObject.prototype.loaded_gobjects = function (cb, resource) {
    this.gobjects = resource.gobjects;
    if (cb) cb(resource.gobjects);
};

BQObject.prototype.save_gobjects = function (cb, url, progress, errorcb) {
    this.testReadonly();
    if (!url) url = this.uri;
    var resource = new BQResource (url + "/gobject");
    resource.gobjects = this.gobjects;
    resource.created = false;   // HACK
    resource.save_(resource.uri, cb, errorcb);
};

BQObject.prototype.save_tags = function (cb, url, progress, errorcb) {
    this.testReadonly();
    if (!url) url = this.uri;
    var resource = new BQResource (url + "/tag");
    resource.tags = this.tags;
    resource.created = false;   // HACK
    resource.save_(resource.uri, cb, errorcb);
};

BQObject.prototype.dispose = function (){
    visit = new BQVisitor();
    visit.visit = function (n) { n.doc = null;  };
    visit.visitall(this);
};

BQObject.prototype.addtag = function (tag, deep){
    // Tag must be either a BQTag or dictionary of attribute value pairs { name:xx, value:xx , type:xx }
    if (!(tag instanceof BQTag) || deep) {
        var nt = new BQTag();
        for (var i in tag) {
            nt[i] = tag[i];
        }
        tag = nt;
    }
    tag.setParent(this);
    tag.doc = this.doc;
    this.dirty = true;
    return tag;
};

BQObject.prototype.addtags = function (tags, deep) {
    for (var i=0; i<tags.length; i++)
        this.addtag(tags[i], deep);
};

BQObject.prototype.addgobjects=function (gob){
    if (! (gob instanceof BQGObject)) {
        var ng = new BQGObject();
        for (var i in gob) {
            ng[i] = gob[i];
        }
        gob = ng;
    }
    gob.setParent(this);
    gob.doc = this.doc;
    this.dirty = true;
    return gob;
};

BQObject.prototype.addchild = function (kid) {
    kid.setParent(this);
    kid.doc = this.doc;
    this.dirty = true;
};

BQObject.prototype.convert_tags=function (){
     for (var i=0; i < this.tags.length; i++) {
         var tag = this.tags[i];
         var nm  = tag.name.replace(/\W/g, '_');
         var vl  = tag.value;
         if (this[nm] == undefined) {
             this[nm] = vl;
         } else {
             if (!(this[nm] instanceof Array)) {
                 this[nm] = [ this[nm] ];
             }
             this[nm].push (vl);
         }
     }
};

//-----------------------------------------------------------------------------
// BQResource represents an addressable resource.
// It is often used a the top level document of a tag document
// I1
//  +- R1 == /image/1/tags
//  +- R2 == /image/1/gobjects
//      + G1
//      + G2/R3 == /image/1/gobjects/2  a very large gobject
//-----------------------------------------------------------------------------

function BQResource (uri, doc) {
    BQObject.call(this, uri, doc);
    this.resource_type = 'resource';
};

BQResource.prototype = new BQObject();


//-----------------------------------------------------------------------------
// BQTemplate
//-----------------------------------------------------------------------------

function BQTemplate (uri, doc) {
    BQObject.call(this, uri, doc);
    this.resource_type = 'template';
};
BQTemplate.prototype = new BQObject();


//-----------------------------------------------------------------------------
// BQImage
//-----------------------------------------------------------------------------

function BQImage (uri){
    BQObject.call(this, uri);
    this.resource_type = "image";
    this.path = null;
};
BQImage.prototype = new BQObject();
//extend(BQImage, BQObject);

BQImage.prototype.initializeXml = function (node) {
    BQObject.prototype.initializeXml.call(this, node);
    if (this.resource_uniq) {
        //this.src  = '/image_service/' + this.resource_uniq;
        // in the case the the data is coming from another server, make sure to load proper URL
        //this.src = this.uri.replace(/\/data_service\/.*$/i, this.src);
        this.src = this.uri.replace('/data_service/', '/image_service/');
    }

    /*
    this.x    = attribInt(node,'x');
    this.y    = attribInt(node,'y');
    this.z    = attribInt(node,'z');
    this.t    = attribInt(node,'t');
    this.ch   = attribInt(node,'ch');
    */
};

BQImage.prototype.initFromObject = function (o) {
    var f = null,
        i = 0;
    if (o && o.resource_uniq) {
        for (i=0; (f=this.xmlfields[i]); ++i) {
            this[f] = Ext.clone(o[f]);
        }
        this.src = this.uri.replace('/data_service/', '/image_service/');
    }
};

BQImage.prototype.setPath = function (path) {
    if (path) {
        this.path = path;
        this.src += path;
    }
};


//-----------------------------------------------------------------------------
// BQFile
//-----------------------------------------------------------------------------

function BQFile (uri){
    BQObject.call(this, uri);
    this.resource_type = 'file';
};
BQFile.prototype = new BQObject();
//extend(BQFile, BQObject);

BQFile.prototype.initializeXml = function (node) {
    BQObject.prototype.initializeXml.call(this, node);
};

//-----------------------------------------------------------------------------
// BQTag
//-----------------------------------------------------------------------------

function BQTag (uri, name, value, type) {
    BQObject.call(this, uri);
    //this.values = [];
    this.resource_type = "tag";
    this.name  = name;
    this.value = value;
    this.type  = type;
};
BQTag.prototype = new BQObject();
//extend(BQTag, BQObject);

BQTag.prototype.setParent = function (p) {
    if (p.tags == this.tags)
        alert ('Warning - BQTag.prototype.setParent: parent and child are same');
    p.tags = p.tags || [];
    p.tags.push (this);
    this.parent = p;
};

Ext.namespace('BQ.annotations');
BQ.annotations.name = 'annotation_status';
BQ.annotations.type = 'AnnotationStatus';
BQ.annotations.status = {
    started: 'started',
    finished: 'finished',
    validated: 'validated',
};

BQ.annotations.types_ignore_user_presentation = {
    color: 'color',
    functional: 'functional',
};

//-----------------------------------------------------------------------------
// BQGObject
//-----------------------------------------------------------------------------

function BQGObject(ty, uri){
    BQObject.call(this, uri);
    this.type = ty;           // one of our registeredTypes: point, polygon, etc.
    this.uri=null;
    this.name = null;
    this.vertices = [];
    this.resource_type = "gobject";
};
BQGObject.prototype = new BQObject();
//extend(BQGObject,BQObject)
if(window.location.hash == "#experimental"){
    BQGObject.primitives = {
        circle   : 'circle',
        ellipse  : 'ellipse',
        label    : 'label',
        line     : 'line',
        point    : 'point',
        polygon  : 'polygon',
        polyline : 'polyline',
        freehand_line : 'freehand_line',
        freehand_shape: 'freehand_shape',
        smart_shape: 'smart_shape',
        rectangle: 'rectangle',
        square   : 'square',
    };
}
else
    BQGObject.primitives = {
        point    : 'Point',
        line     : 'Line',
        polygon  : 'Polygon',
        polyline : 'Polyline',
        freehand_line : 'Freehand line',
        freehand_shape: 'Freehand shape',
        circle   : 'Circle',
        ellipse  : 'Ellipse',
        rectangle: 'Rectangle',
        square   : 'Square',
        label    : 'Label',
    };

BQGObject.objects = BQ.util.clone(BQGObject.primitives);
BQGObject.objects['gobject'] = 'Gobject';

BQGObject.primitives_help = {
    point    : '<h2>Point</h2> <li>Click to create points',
    line     : '<h2>Line</h2> <li>Two clicks to create a line',
    polygon  : '<h2>Polygon</h2> <li><b>Double-click</b> or <b>Escape</b> to finish <li><b>Back-space</b> to remove last point <li><b>Delete</b> to remove current',
    polyline : '<h2>Polyline</h2> <li><b>Double-click</b> or <b>Escape</b> to finish <li><b>Back-space</b> to remove last point <li><b>Delete</b> to remove current',
    freehand_line : '<b>Freehand line</b> <li>Click, hold and move',
    freehand_shape: '<b>Freehand shape</b> <li>Click, hold and move',
    circle   : '<h2>Circle</h2> <li>Click, hold and move',
    ellipse  : '<h2>Ellipse</h2> <li>Click, hold and move <li>Rotate by selecting',
    rectangle: '<h2>Rectangle</h2> <li>Click, hold and move',
    square   : '<h2>Square</h2> <li>Click, hold and move',
    label    : '<h2>Label</h2> <li>Click to create',
};

var bq_create_gradient = function (r1,g1,b1,a1,r2,g2,b2,a2) {
    var ri = r1,
        gi = g1,
        bi = b1,
        ai = a1,
        rd = (r2-r1)/100.0,
        gd = (g2-g1)/100.0,
        bd = (b2-b1)/100.0,
        ad = (a2-a1)/100.0;
    for (var i=0; i<101; ++i) {
        BQGObject.color_gradient[i] = {
            r: Math.round(ri),
            g: Math.round(gi),
            b: Math.round(bi),
            a: ai,
        };
        ri += rd;
        gi += gd;
        bi += bd;
        ai += ad;
    }
};

BQGObject.default_color = {
    r: 255,
    g: 0,
    b: 0,
    a: 0.6
};

BQGObject.default_color_stroke = {
    r: 255,
    g: 0,
    b: 0,
    a: 1.0
};

BQGObject.color_rgb2html = function(c) {
    var h = Kinetic.Util._rgbToHex(c.r, c.g, c.b);
    return '#'+h;
};

BQGObject.color_html2rgb = function(c) {
    var rgb = Kinetic.Util._hexToRgb(c);
    return rgb;
};

BQGObject.color_contrasting = function(c) {
    var Y = 0.2126*c.r + 0.7152*c.g + 0.0722*c.b;
    if (Y<70)
        return { r:255, g: 255, b: 255, a: c.a };
    return { r:0, g: 0, b: 0, a: c.a };
};

BQGObject.string_to_color_html = function(str, darker) {
    var hash = 0,
        colour = '#',
        i=0;
    for (i = 0; i < str.length; i++) {
        hash = str.charCodeAt(i) + ((hash << 5) - hash);
    }
    for (i = 0; i < 3; i++) {
        var value = (hash >> (i * 8)) & 0xFF;
        colour += ('00' + value.toString(16)).substr(-2);
    }

    if (!darker) {
        if (colour === '#000000') colour = '#ffffff';
        var c = Ext.draw.Color.fromString(colour);
        var hsl = c.getHSL();
        if (hsl[2]<0.5) {
            hsl[2] = 0.5;
            c = Ext.draw.Color.fromHSL( hsl[0], hsl[1], hsl[2] );
            colour = c.toString();
        }
    } else {
        if (colour === '#ffffff') colour = '#000000';
        var c = Ext.draw.Color.fromString(colour);
        var hsl = c.getHSL();
        if (hsl[2]>0.5) {
            hsl[2] = 0.5;
            c = Ext.draw.Color.fromHSL( hsl[0], hsl[1], hsl[2] );
            colour = c.toString();
        }
    }

    return colour;
};

BQGObject.get_gob_color = function(t, level, separator) {
    if (!t) return;
    var tt = t;

    // parse the type and pick specific level
    if (level && level>0 && separator && separator !== '') {
        try {
            var h = t.split(separator);
            tt = h[level-1].trim();
        } catch (e) {
        }
    }

    return BQGObject.string_to_color_html(tt);
};

BQGObject.styles_per_type = {
   default: { color: '#FF0000', },
};

BQGObject.add_default_style = function(t, level, separator) {
    if (!t) return;
    BQGObject.styles_per_type[t] = {
        color: BQGObject.get_gob_color(t, level, separator),
    };
};

BQGObject.load_default_styles = function(xml, level, separator) {
    if (!xml) {
        Ext.Ajax.request({
            url: '/data_service/image/?gob_types=true&wpublic=true',
            callback: function(opts, succsess, response) {
                if (response.status>=400) {
                    BQ.ui.error('Problem fetching available gobject types');
                } else {
                    BQGObject.load_default_styles(response.responseXML);
                }
            },
            //scope: this,
            disableCaching: false,
        });
        return;
    }
    BQGObject.unique_gobjects_xml = xml;

    var gobs = BQ.util.xpath_nodes(xml, '//gobject'),
        g=undefined, i=0, t=null;
    for (i=0; g=gobs[i]; ++i) {
        t = g.getAttribute('type');
        if (t)
            BQGObject.add_default_style(t, level, separator);
    } // for types
};

// set random colors for objects
BQGObject.load_default_styles(); // dima: load this after loading preferences

BQGObject.parse_colors_from_gob_template = function(resource) {
    /*
    <tag name="gobject" value="freehand_line" />
    <tag name="gobject" value="foreground">
        <tag name="color" value="#00FF00" type="color" />
    </tag>
    <tag name="gobject" value="background">
        <tag name="color" value="#FF0000" type="color" />
    </tag>
    */
    var template = resource.find_children('template');
    if (template && template instanceof Array && template.length>0) {
        template = template[0];
    }
    if (!template) return;

    // walk gobject tags and set colors
    var i=0,
        t=null,
        d=null;
    for (i=0; (t=template.tags[i]); ++i) {
        if (t.name === 'gobject') {
            d = t.toDict(false);
            if (d.color) {
                var s = BQGObject.styles_per_type[t.value] || {};
                s.color = d.color;
                BQGObject.styles_per_type[t.value] = s;
            }
        }
    }
};

BQGObject.coloring_mode = 'class'; // available modes: 'class' 'confidence'
BQGObject.confidence_tag = 'confidence';
BQGObject.confidence_cutoff = 0;
BQGObject.confidence_mult = 1.0;
BQGObject.color_gradient = [];
bq_create_gradient(0,0,255,1.0, 255,255,0,1.0);

BQGObject.prototype.initializeXml = function (node) {
    BQObject.prototype.initializeXml.call(this, node);

    this.type  = node.nodeName;
    if (this.type == 'gobject')
        this.type = attribStr(node, 'type');

    // dima: speed optimization, using xpath for resources with many vertices is much faster
    // Utkarsh : now uses evaulateXPath from utils.js, which is browser independent
    var vertices = BQ.util.xpath_nodes(node, 'vertex');
    this.vertices = [];

    // vertices should be an array
    for (var i=0; i<vertices.length; i++)
        this.vertices.push(new BQVertex(vertices[i]));

    var t = BQ.util.xpath_node(node, 'tag[@name="color"]');
    if (t)
        this.color = t.getAttribute('value').replace('#', '');

    var t = BQ.util.xpath_node(node, 'tag[@name="'+BQGObject.confidence_tag+'"]');
    if (t)
        this.confidence = parseFloat(t.getAttribute('value')) * BQGObject.confidence_mult;
};

BQGObject.prototype.setParent = function (p) {
    p.gobjects = p.gobjects || [];
    p.gobjects.push (this);
    this.parent = p;
};

BQGObject.prototype.isPrimitive = function () {
    return (this.resource_type in BQGObject.primitives || this.type in BQGObject.primitives);
};

BQGObject.prototype.getColor = function (r,g,b,a,no_default) {
    // first of all hide objects if needed
    var confidence = this.getConfidence();
    if (confidence && BQGObject.confidence_cutoff>0 && confidence < BQGObject.confidence_cutoff)
        return {r: 255, g: 0, b: 0, a: 0};

    if (this.color_override) {
        return Kinetic.Util._hexToRgb('#' + this.color_override);
    } else if (this.color) {
        var c = Kinetic.Util._hexToRgb('#' + this.color);
        c.a = BQGObject.default_color.a;
        return c;
    } else if (r && g && b && a) {
        return {r: r, g: g, b: b, a: a};
    } else if (BQGObject.coloring_mode === 'class' && this.type && !(this.type in BQGObject.primitives)) {
        var c = null;
        if (this.type in BQGObject.styles_per_type && BQGObject.styles_per_type[this.type].color) {
            c = BQGObject.styles_per_type[this.type].color;
        } else {
            c = BQGObject.get_gob_color(this.type);
        }
        return Kinetic.Util._hexToRgb(c);
    } else if (BQGObject.coloring_mode === 'confidence' && typeof(confidence) !== 'undefined') {
        var cc = Math.max(0, Math.min(100, Math.round(confidence)));
        var c = BQGObject.color_gradient[cc];
        //return {r: c.r, g: c.g, b: c.b, a: c.a};
        return {r: c.r, g: c.g, b: c.b};
    } else if (no_default===true) {
        return;
    }

    // none of the overrides worked, try walking up the parent chain to get the color or use default
    var c = BQGObject.default_color,
        p = this,
        cc = null;
    while (p.parent && p.parent.getColor) {
        p = p.parent;
        cc = p.getColor(null,null,null,null,true);
        if (cc) {
           c = cc;
           break;
        }
    }

    return {r: c.r, g: c.g, b: c.b, a: c.a};
};

BQGObject.prototype.setColor = function (c, skip_save) {
    this.color = c;
    var t = this.find_tags('color');
    if (!t) {
        t = this.addtag(new BQTag(null, 'color', '#'+this.color, 'color'));
    } else {
        t.value = '#' + this.color;
    }

    // dima: save the user set color back to the DB
    if (skip_save) return;
    t.save_(this.uri);
},

BQGObject.prototype.getConfidence = function () {
    if (typeof this[BQGObject.confidence_tag] === 'undefined') {
        var t = this.find_tags(BQGObject.confidence_tag);
        if (t)
            this[BQGObject.confidence_tag] = t.value * BQGObject.confidence_mult;
    }
    return this[BQGObject.confidence_tag];
};

BQGObject.prototype.perimeter = function (res) {
    var type = this.resource_type === 'gobject' ? this.type : this.resource_type;
    if (!res || !res.x) res = {x:1.0, y:1.0};

    if (type === 'point') {
        return 0;
    } else if (type === 'label') {
        return 0;
    } else if (type === 'circle') {
        p1 = this.vertices[0].mul(res);
        p2 = this.vertices[1].mul(res);
        return 2.0 * Math.PI * Math.max(Math.abs(p1.x-p2.x), Math.abs(p1.y-p2.y));
    } else if (type === 'ellipse') {
        p1 = this.vertices[0].mul(res);
        p2 = this.vertices[1].mul(res);
        p3 = this.vertices[2].mul(res);
        var a = Math.max(Math.abs(p1.x-p2.x), Math.abs(p1.y-p2.y));
        var b = Math.max(Math.abs(p1.x-p3.x), Math.abs(p1.y-p3.y));
        return Math.PI * ( 3.0*(a+b) - Math.sqrt( 10.0*a*b + 3.0*(a*a + b*b)) );
    } else if (type === 'polygon') {
        vx = Ext.Array.clone(this.vertices);
        vx.push(vx[0]);
        var d=0;
        for (var i=0; i<vx.length-1; i++) {
            p1 = vx[i].mul(res);
            p2 = vx[i+1].mul(res);
            d += Math.sqrt( Math.pow(p2.x-p1.x,2.0) + Math.pow(p2.y-p1.y,2.0) );
        }
        return d;
    } else if (type === 'line' || type === 'polyline') {
        vx = this.vertices;
        var d=0;
        for (var i=0; i<vx.length-1; i++) {
            p1 = vx[i].mul(res);
            p2 = vx[i+1].mul(res);
            d += Math.sqrt( Math.pow(p2.x-p1.x,2.0) + Math.pow(p2.y-p1.y,2.0) );
        }
        return d;
    } else if (type === 'rectangle' || type === 'square') {
        p1 = this.vertices[0].mul(res);
        p2 = this.vertices[1].mul(res);
        return Math.abs(p1.x-p2.x)*2.0 + Math.abs(p1.y-p2.y)*2.0;
    }
    return 0;
};

BQGObject.prototype.area = function (res) {
    var type = this.resource_type === 'gobject' ? this.type : this.resource_type;
    if (!res || !res.x) res = {x:1.0, y:1.0};

    if (type === 'point') {
        return 0;
    } else if (type === 'label') {
        return 0;
    } else if (type === 'circle') {
        p1 = this.vertices[0].mul(res);
        p2 = this.vertices[1].mul(res);
        return Math.PI * Math.pow( Math.max(Math.abs(p1.x-p2.x), Math.abs(p1.y-p2.y)), 2.0);
    } else if (type === 'ellipse') {
        p1 = this.vertices[0].mul(res);
        p2 = this.vertices[1].mul(res);
        p3 = this.vertices[2].mul(res);
        var a = Math.max(Math.abs(p1.x-p2.x), Math.abs(p1.y-p2.y));
        var b = Math.max(Math.abs(p1.x-p3.x), Math.abs(p1.y-p3.y));
        return Math.PI * a * b;
    } else if (type === 'line') {
        return 0;
    } else if (type === 'polygon') {
        vx = Ext.Array.clone(this.vertices);
        vx.push(vx[0]);
        var d=0;
        for (var i=0; i<vx.length-1; i++) {
            p1 = vx[i].mul(res);
            p2 = vx[i+1].mul(res);
            d += p1.x*p2.y - p1.y*p2.x;
        }
        return 0.5 * Math.abs(d);
    } else if (type === 'polyline') {
        return 0;
    } else if (type === 'rectangle' || type === 'square') {
        p1 = this.vertices[0].mul(res);
        p2 = this.vertices[1].mul(res);
        return Math.abs(p1.x-p2.x) * Math.abs(p1.y-p2.y);
    }
    return 0;
};

//-----------------------------------------------------------------------------
// BQVisitor
// Simple visitor (mainly for) GObjects
//-----------------------------------------------------------------------------

function BQVisitor () {
};
BQVisitor.prototype.visit_array = function (l, arglist){
    for (var i=0; i < l.length; i++) {
        this.visitall(l[i], arglist);
    }
};
BQVisitor.prototype.visit_special_array = function (l, arglist){
    for (var i=0; i < l.length; i++) {
        this.visit_special(l[i], arglist);
    }
};
BQVisitor.prototype.visit = function(n, arglist) {};
BQVisitor.prototype.start = function(n, arglist) {};
BQVisitor.prototype.finish = function(n, arglist) {};
BQVisitor.prototype.visitall = function (root, arglist) {
    var stack = [];
    stack.push (root);
    while (stack.length != 0) {
        var node = stack.pop();
        this.visit(node,  arglist);
        //for (var i=0; i < kids(node).length; i++ )
        //  stack.push (kids(node)[i]);
        var kids  = node.getkids();
        for (var i=0; i < kids.length; i++)
            stack.push (kids[i]);
    }
};
BQVisitor.prototype.visit_special = function(root,arglist) {
    var stack = [];
    stack.push ([root,null]);
    while (stack.length != 0) {
        var tuple = stack.pop();
        var node = tuple[0];
        var parent = tuple[1];
        if (node == null) {     // found end of parent.
            this.finish(parent, arglist);
            continue;
        }
        var kids  = node.getkids();
        if (kids.length > 0) { // push an end of parent mark/
            stack.push([null, node]);
            this.start (node, arglist);
        }
        this.visit (node,  arglist);
        for (var i=0; i < kids.length; i++ )
            stack.push ([kids[i], node]);
    }
};
////////////////////////////////////////////////
// A visitor with nodes on the class
// A visitor supporting type visits
// The node should have a type field which
// will be used as a dispatch method on the class
// i.e. GobVisitor.polyine (polynode) when visiting polyline objects
// default_visit will be called  for unknown types.
// Simple Gobject types will not be called with start/finish states
// as they do not have children gobjects.
function BQClassVisitor () {
    this.VISIT = 'visit';
    this.START = 'start';
    this.FINISH = 'finish';
    this.state = null;
};
BQClassVisitor.prototype = new BQVisitor();
BQClassVisitor.prototype.callnode = function (n, arglist){
    var f = this[n.type] || this['default_visit'] || null;
    if (f != null) {
        var args = [n].concat(arglist);
        f.apply (this, args);
    }
};
BQClassVisitor.prototype.visit = function (n, arglist){
    this.state=this.VISIT;
    this.callnode(n, arglist);
};
BQClassVisitor.prototype.start = function (n,arglist){
    this.state=this.START;
    this.callnode(n, arglist);
};
BQClassVisitor.prototype.finish = function (n,arglist){
    this.state=this.FINISH;
    this.callnode(n, arglist);
};
//////////////////////////////////////////////////
// Forward node function to another proxy class
// The node should have a type field which
// will be used as a dispatch method on the proxy class
// i.e. Proxy.polyine (visitor, polynode) when visiting polyline objects

function BQProxyClassVisitor (visitor) {
    this.proxy = visitor;
};
BQProxyClassVisitor.prototype = new BQClassVisitor();
BQProxyClassVisitor.prototype.callnode = function (n, arglist){
    var f = this.proxy[n.type] || this.proxy['default_visit'] || null;
    if (f != null) {
        var args = [this, n].concat (arglist);
        f.apply (this.proxy, args);
    }

};
//////////////////////////////////////////////////
// Visitor Utility function
// Usage:   visit_array (some_array, function (n[,args]) {..}[,args]);
//
function visit_all (node, cb) {
    var args = Array.prototype.slice.call(arguments,2);
    var v = new BQVisitor();
    v.visit = cb;
    v.visitall(node, args);

};
function visit_array (arr, cb) {
    var args = Array.prototype.slice.call(arguments,2);
    var v = new BQVisitor();
    v.visit = cb;
    v.visit_array(arr, args);
};


//-------------------------------------------------------------------------------
// BQImagePhys - maintains a record of image physical parameters
//-------------------------------------------------------------------------------

Ext.namespace('BQ.api.Phys');

// visual representation of units string
BQ.api.Phys.units = {
    // metric units
    yotometers   : 'ym',
    yotometer    : 'ym',
    zeptometers  : 'zm',
    zeptometer   : 'zm',
    attometers   : 'am',
    attometer    : 'am',
    femtometers  : 'fm',
    femtometer   : 'fm',
    picometers   : 'pm',
    picometer    : 'pm',
    nanometers   : 'nm',
    nanometer    : 'nm',
    nm           : 'nm',
    microns      : 'μm',
    micron       : 'μm',
    um           : 'μm',
    μm           : 'μm',
    micrometers  : 'μm',
    micrometer   : 'μm',
    milimeters   : 'mm',
    milimeter    : 'mm',
    mm           : 'mm',
    centimeters  : 'cm',
    centimeter   : 'cm',
    cm           : 'cm',
    decimeters   : 'dm',
    decimeter    : 'dm',
    meters       : 'm',
    meter        : 'm',
    m            : 'm',
    decameters   : 'dam',
    decameter    : 'dam',
    hectometers  : 'hm',
    hectometer   : 'hm',
    kilometers   : 'km',
    kilometer    : 'km',
    km           : 'km',
    megameters   : 'Mm',
    megameter    : 'Mm',
    gigameters   : 'Gm',
    gigameter    : 'Gm',
    terameters   : 'Tm',
    terameter    : 'Tm',
    petameters   : 'Pm',
    petameter    : 'Pm',
    exameters    : 'Em',
    exameter     : 'Em',
    zettameters  : 'Zm',
    zettameter   : 'Zm',
    yottameters  : 'Ym',
    yottameter   : 'Ym',

    // imperial units
    inch         : 'in',
    inches       : 'in',
    foot         : 'ft',
    feet         : 'ft',
    yard         : 'yd',
    yards        : 'yd',
    mile         : 'mi',
    miles        : 'mi',

    // nautical
    fathom       : 'ftm',
    fathoms      : 'ftm',
    cable        : 'cb',
    calbles      : 'cb',
    nautical_mile    : 'nmi',
    nautical_miles   : 'nmi',
    'nautical mile'  : 'nmi',
    'nautical miles' : 'nmi',
};

function BQImagePhys(bqimage) {
    this.num_channels = 0;
    this.pixel_depth = null;
    this.pixel_size = [];
    this.pixel_units = [];
    this.channel_names = [];
    this.display_channels = [];
    this.channel_colors = [];

    this.pixel_size_ds = [];
    this.channel_names_ds = [];
    this.display_channels_ds = [];

    this.pixel_size_is = [];
    this.channel_names_is = [];
    this.display_channels_is = [];

    // default mapping
    this.channel_colors_default = [
        new Ext.draw.Color( 255,   0,   0 ), // red
        new Ext.draw.Color(   0, 255,   0 ), // green
        new Ext.draw.Color(   0,   0, 255 ), // blue
        new Ext.draw.Color( 255, 255, 255 ), // gray
        new Ext.draw.Color(   0, 255, 255 ), // cyan
        new Ext.draw.Color( 255,   0, 255 ), // magenta
        new Ext.draw.Color( 255, 255,   0 ), // yellow
    ];

    this.pixel_formats = {
        'unsigned integer': 'u',
        'signed integer'  : 's',
        'floating point'  : 'f',
    };

    this.is_done = false;
    this.ds_done = false;
    this.loadcallback = null;
    this.image = bqimage;
    //this.init();
};

BQImagePhys.prototype.init = function () {
  if (!this.image) return;
  this.num_channels = this.ch || this.image.ch;

  //-------------------------------------------------------
  // image physical sizes
  this.pixel_size = [0, 0, 0, 0];
  this.pixel_units = [undefined, undefined, undefined, undefined];

  //-------------------------------------------------------
  // image channels to display RGB mapping
  this.display_channels[0] = 0;
  this.display_channels[1] = 1;
  this.display_channels[2] = 2;
  if (this.num_channels == 1) {
    this.display_channels[1] = 0;
    this.display_channels[2] = 0;
  }
  if (this.num_channels == 2)
    this.display_channels[2] = -1;


    this.channel_colors = this.channel_colors_default.slice(0, Math.min(this.num_channels, this.channel_colors_default.length));
    var diff = this.num_channels-this.channel_colors.length;
    for (var i=0; i<diff; i++)
        this.channel_colors.push(new Ext.draw.Color(0,0,0));


  //-------------------------------------------------------
  // channel names
  for (var i=0; i<this.num_channels; i++)
    this.channel_names[i] = 'Ch'+(i+1);
  if (this.num_channels == 3) {
    this.channel_names[0] = 'Red';
    this.channel_names[1] = 'Green';
    this.channel_names[2] = 'Blue';
  }
};

function combineValue( v1, v2, def ) {
  //if (v1 && v1 != undefined && v1 != NaN && v1 != '') return v1;
  //if (v2 && v2 != undefined && v2 != NaN && v2 != '') return v2;
  //return def;
  return v1 || v2 || def;
};


BQImagePhys.prototype.normalizeMeta = function() {
    console.log("BQImagePhys: Aggregate metadata");

    // ensure values and their types
    for (var i = 0; i < this.pixel_size.length; i++) {
        this.pixel_size[i] = combineValue(this.pixel_size_ds[i], this.pixel_size_is[i], this.pixel_size[i]);
        this.pixel_size[i] = parseFloat(this.pixel_size[i]);
    }

    for (var i = 0; i < this.channel_names.length; i++) {
        this.channel_names[i] = combineValue(this.channel_names_ds[i], this.channel_names_is[i], this.channel_names[i]);
    }

    for (var i = 0; i < this.display_channels.length; i++) {
        this.display_channels[i] = combineValue(this.display_channels_ds[i], this.display_channels_is[i], this.display_channels[i]);
        this.display_channels[i] = parseInt(this.display_channels[i]);
    }

    if (this.channel_colors_ds && this.channel_colors_ds.length === this.num_channels)
        this.channel_colors = this.channel_colors_ds;

    // set computed variables
    this.units = BQ.api.Phys.units[this.pixel_units[0]] || this.pixel_units[0] || '?';

    this.initialized = true;
};

BQImagePhys.prototype.coordinate_to_phys = function(pt, use_geo) {
    if (!this.geo) {
        use_geo = false;
    }

    // print physical coordinates
    if ((!use_geo && !this.coordinates) && this.pixel_size[0]>0 && this.pixel_size[1]>0) {
        v = [pt.x*(this.pixel_size[0]), pt.y*(this.pixel_size[1])];
        if (pt.z)
            v[2] = pt.z*(this.pixel_size[2]);
        if (pt.t)
            v[3] = pt.t*(this.pixel_size[3]);
        return v;
    }

    // print geo coordinates if available
    if (this.geo && this.geo.proj4 && this.geo.res && this.geo.top_left) {
        try {
            var c = [this.geo.top_left[0] + pt.x*this.geo.res[0], this.geo.top_left[1] - pt.y*this.geo.res[1]];
            var latlong = proj4(this.geo.proj4, 'EPSG:4326', c);
            return [latlong[1], latlong[0]];
        } catch (error) {
            return;
        }
    }

    // print physical geometry coordinates if available
    if (this.coordinates && this.coordinates.top_left) {
        if (this.coordinates.axis_origin !== 'top_left') return;
        if (this.coordinates.axis_orientation !== 'ascending,descending') return;
        try {
            var pt_px = [pt.x + this.coordinates.top_left[0], pt.y + this.coordinates.top_left[1]];
            var pt_ph = [pt_px[0]*this.pixel_size[0], pt_px[1]*this.pixel_size[1]];
            return [pt_ph[0], pt_ph[1], pt_px[0], pt_px[1]];
        } catch (error) {
            return;
        }
    }

    return [pt.x, pt.y];
};

BQImagePhys.prototype.load = function(cb, errorcb) {
    this.initialized = undefined;
    this.loadcallback = cb;

    BQFactory.request({
        uri : this.image.src + '?meta',
        cb_xml: callback(this, this.onloadIS),
        errorcb: errorcb,
    });

    //dima: no longer needed, IS is merging meta from resource
    /*if (this.image.tags.length==0)
      this.image.load_tags(callback(this, 'onloadDS'));
    else*/
      this.onloadDS();
};

BQImagePhys.prototype.onload = function() {
  console.log ("BQImagePhys: onload test: " + this.is_done + " " + this.ds_done );
  if (this.is_done==true && this.ds_done==true) {
    this.normalizeMeta();
    if (this.loadcallback != null) this.loadcallback (this);
  }
};



BQImagePhys.prototype.onloadIS = function (image, xml) {
  console.log ("BQImagePhys: Got metadata from IS");
  this.xml = xml;
  var hash = {};
  for (var t in image.tags )
      hash[image.tags[t].name] = image.tags[t].value;

  //-------------------------------------------------------
  // image physical sizes
  this.pixel_size_is[0] = parseFloat(hash['pixel_resolution_x']);
  this.pixel_size_is[1] = parseFloat(hash['pixel_resolution_y']);
  this.pixel_size_is[2] = parseFloat(hash['pixel_resolution_z']);
  this.pixel_size_is[3] = parseFloat(hash['pixel_resolution_t']);
  this.x  = parseInt(hash['image_num_x']);
  this.y  = parseInt(hash['image_num_y']);
  this.z  = parseInt(hash['image_num_z']);
  this.t  = parseInt(hash['image_num_t']);
  this.ch  = parseInt(hash['image_num_c']);

  // dima: have to pick these from paths "image_series_paths/00000", "image_series_paths/00001", etc...
  this.labels = parseInt(hash['image_num_labels']);
  this.previews = parseInt(hash['image_num_previews']);

  this.init();

  //-------------------------------------------------------
  // units
  var wanted = { 'pixel_resolution_unit_x': 0,
                 'pixel_resolution_unit_y': 1,
                 'pixel_resolution_unit_z': 2,
                 'pixel_resolution_unit_t': 3 };
  for (var v in wanted) {
      if (v in hash)
          this.pixel_units[wanted[v]] = this.pixel_units[wanted[v]] || hash[v];
  }

  //-------------------------------------------------------
  // image channels to display RGB mapping
  this.display_channels_is[0] = hash['display_channel_red'];
  this.display_channels_is[1] = hash['display_channel_green'];
  this.display_channels_is[2] = hash['display_channel_blue'];

  for (var i=0; i<this.num_channels; i++)
     if (hash['channel_color_'+i])
         this.channel_colors[i] = Ext.draw.Color.fromString('rgb('+hash['channel_color_'+i]+')');

  //-------------------------------------------------------
  // image channels to display RGB mapping
  for (var i=0; i<this.num_channels; i++) {
    var tag_name = 'channel_' + i + '_name';
    this.channel_names_is[i] = hash[tag_name];
  }

  //-------------------------------------------------------
  // additional info
  this.pixel_depth = hash['image_pixel_depth'];
  this.pixel_format = hash['image_pixel_format'];

  //-------------------------------------------------------
  // additional info
  //this.pixel_depth = hash['image_pixel_depth'];

  // find geo tags
  if (xml) {

      var coordinates = BQ.util.xpath_node(xml, "resource/tag[@name='coordinates']");
      if (coordinates) {
          var v = BQ.util.xpath_nodes(coordinates, "tag[@name='axis_origin']/@value");
          var axis_origin = v && v.length>0 ? v[0].value : undefined;

          var v = BQ.util.xpath_nodes(coordinates, "tag[@name='axis_orientation']/@value");
          var axis_orientation = v && v.length>0 ? v[0].value : undefined;

          var v = BQ.util.xpath_nodes(coordinates, "tag[@name='tie_points']/tag[@name='top_left']/@value");
          var top_left = v && v.length>0 ? v[0].value.split(',') : undefined;
          if (top_left) {
              top_left[0] = parseFloat(top_left[0]);
              top_left[1] = parseFloat(top_left[1]);
          }

          this.coordinates = this.coordinates || {};
          this.coordinates.axis_origin = axis_origin || this.coordinates.axis_origin;
          this.coordinates.axis_orientation = axis_orientation || this.coordinates.axis_orientation;
          this.coordinates.top_left = top_left || this.coordinates.top_left;
      } else {
          this.coordinates = undefined;
      }

      var geo = BQ.util.xpath_node(xml, "resource/tag[@name='Geo']");
      if (geo) {
          // fetch proj4 model definition
          var v = BQ.util.xpath_nodes(geo, "tag[@name='Model']/tag[@name='proj4_definition']/@value");
          var proj4_defn = v && v.length>0 ? v[0].value : undefined;

          // fetch image 0,0 in model coordinates
          v = BQ.util.xpath_nodes(geo, "tag[@name='Coordinates']/tag[@name='upper_left_model']/@value");
          if (!v || v.length<1) {
              v = BQ.util.xpath_nodes(geo, "tag[@name='Coordinates']/tag[@name='upper_left']/@value");
          }
          var top_left = v && v.length>0 ? BQ.util.parseStringArrayFloat(v[0].value) : undefined;

          // fetch image resolution
          v = BQ.util.xpath_nodes(geo, "tag[@name='Tags']/tag[@name='ModelPixelScaleTag']/@value");
          var res = v && v.length>0 ? BQ.util.parseStringArrayFloat(v[0].value) : undefined;

          // fetch center for simple exif type geo information
          v = BQ.util.xpath_nodes(geo, "tag[@name='Coordinates']/tag[@name='center']/@value");
          var center = v && v.length>0 ? BQ.util.parseStringArrayFloat(v[0].value) : undefined;

          this.geo = this.geo || {};
          this.geo.proj4 = proj4_defn || this.geo.proj4;
          this.geo.top_left = top_left || this.geo.top_left;
          this.geo.res = res || this.geo.res;
          this.geo.center = center || this.geo.center;
      } else {
          this.geo = undefined;
      }

  }

  // find DICOM tags
  if (xml) {
      var dicom = BQ.util.xpath_nodes(xml, "resource/tag[@name='DICOM']");
      if (dicom && dicom.length>0) {
          dicom = dicom[0];
          this.dicom = {
              modality:   BQ.util.xpath_string(dicom, "tag[@name='Modality' and @type=':///DICOM#0008,0060']/@value"),
              wnd_center: BQ.util.xpath_string(dicom, "tag[@name='Window Center' and @type=':///DICOM#0028,1050']/@value"),
              wnd_width:  BQ.util.xpath_string(dicom, "tag[@name='Window Width' and @type=':///DICOM#0028,1051']/@value"),
          };
          // preferred may be lists

      } else {
          this.dicom = undefined;
      }
  }

  this.is_done = true;
  this.onload();
};

BQImagePhys.prototype.onloadDS = function ( ) {
    console.log ("BQImagePhys: Got metadata from DS");

    var image = this.image;
    var ht = {};
    for (var t in image.tags )
        ht[image.tags[t].name] = image.tags[t].value;

    //-------------------------------------------------------
    // image physical sizes
    v  = 'pixel_resolution_x_y';
    if (v in ht) {
        this.pixel_size_ds[0] = parseFloat(ht[v]);
        this.pixel_size_ds[1] = parseFloat(ht[v]);
    }
    var wanted = { 'pixel_resolution_x': 0,
                   'pixel_resolution_y': 1,
                   'pixel_resolution_z': 2,
                   'pixel_resolution_t': 3 };
    for (var v in wanted) {
        if (v in ht)
            this.pixel_size_ds[wanted[v]] = parseFloat(ht[v]);
    }

    //-------------------------------------------------------
    // units
    var wanted = { 'pixel_resolution_unit_x': 0,
                   'pixel_resolution_unit_y': 1,
                   'pixel_resolution_unit_z': 2,
                   'pixel_resolution_unit_t': 3 };
    for (var v in wanted) {
        if (v in ht)
            this.pixel_units[wanted[v]] = ht[v];
    }

    //-------------------------------------------------------
    // image channels to display RGB mapping
    this.display_channels_ds[0] = ht['display_channel_red'];
    this.display_channels_ds[1] = ht['display_channel_green'];
    this.display_channels_ds[2] = ht['display_channel_blue'];

    this.channel_colors_ds = [];
    for (var i=0; i<this.num_channels; i++)
        if (ht['channel_color_'+i])
            this.channel_colors_ds[i] = Ext.draw.Color.fromString('rgb('+ht['channel_color_'+i]+')');

    //-------------------------------------------------------
    // image channels to display RGB mapping
    for (var i=0; i<this.num_channels; i++) {
      var tag_name = 'channel_' + i + '_name';
      this.channel_names_ds[i] = ht[tag_name];
    }

    // -------------------------------------------------------
    // parse geo info
    var geo = image.find_tags('Geo');
    if (geo) {
        var center=null, top_left=null, res=null, proj4_defn=null, t=null,
            coords = geo.find_tags('Coordinates'),
            model = geo.find_tags('Model'),
            tags = geo.find_tags('Tags');

        if (coords) {
            t = coords.find_tags('center');
            center = t && t.value ? BQ.util.parseStringArrayFloat(t.value) : undefined;

            t = coords.find_tags('upper_left');
            top_left = t && t.value ? BQ.util.parseStringArrayFloat(t.value) : undefined;
        }

        if (model) {
            t = model.find_tags('proj4_definition');
            proj4_defn = t && t.value ? t.value : undefined;
        }

        if (tags) {
            t = tags.find_tags('ModelPixelScaleTag');
            res = t && t.value ? BQ.util.parseStringArrayFloat(t.value) : undefined;
        }

        if (center || top_left || res || proj4_defn) {
            this.geo = this.geo || {};
            this.geo.proj4 = proj4_defn || this.geo.proj4;
            this.geo.top_left = top_left || this.geo.top_left;
            this.geo.res = res || this.geo.res;
            this.geo.center = center || this.geo.center;
        }
    }

    this.ds_done = true;
    this.onload();
};

BQImagePhys.prototype.isPixelResolutionValid = function () {
    return this.pixel_size[0]>0 && this.pixel_size[1]>0;
},

BQImagePhys.prototype.getPixelInfo = function (i) {
    var r = [undefined, undefined];
    if (this.pixel_size[i]!=undefined && !isNaN(this.pixel_size[i]) && this.pixel_size[i]!=0.0000) {
        r[0] = this.pixel_size[i];
        r[1] = this.pixel_units[i];
    }
    return r;
};

BQImagePhys.prototype.getPixelInfoZ = function () {
    return this.getPixelInfo(2);
};

BQImagePhys.prototype.getPixelInfoT = function () {
    return this.getPixelInfo(3);
};

BQImagePhys.prototype.getEnhancementOptions = function () {
    var enhancement_options = [
        {"value":"d", "text":"Data range"},
        {"value":"f", "text":"Full range"},
        {"value":"t", "text":"Data + tolerance"},
        {"value":"e", "text":"Equalized"},
    ];
    if (this.dicom && (this.dicom.modality == 'CT' && this.dicom.wnd_center)) {
        var dicom_options = [];

        if (this.dicom.wnd_center.indexOf(',')>=0) {
            // if wnd_center is a list
            var cntrs = this.dicom.wnd_center.split(',');
            var widths = this.dicom.wnd_width.split(',');
            var prefferred = cntrs[0]+','+widths[0];
            for (var i=0; i<cntrs.length; ++i) {
                dicom_options.push(
                    { value:"hounsfield:"+cntrs[i]+','+widths[i], text: "CT: Preferred ("+cntrs[i]+','+widths[i]+")" }
                );
            }
        } else {
            var prefferred = this.dicom.wnd_center+','+this.dicom.wnd_width;
            dicom_options.push(
                { value:"hounsfield:"+prefferred, text: "CT: Preferred ("+prefferred+")" }
            );
        }
        enhancement_options.push.apply(enhancement_options, dicom_options);
        enhancement_options.prefferred = "hounsfield:"+prefferred;

        dicom_options = [
            { value:"hounsfield:40,80", text: "CT: Head Soft Tissue (40/80)" },
            { value:"hounsfield:30,110", text: "CT: Brain (30/110)" },
            { value:"hounsfield:60,300", text: "CT: Neck Soft Tissue (60/300)" },
            { value:"hounsfield:400,2000", text: "CT: Bone (400/2000)" },
            { value:"hounsfield:400,4000", text: "CT: Temporal bones (400/4000)" },
            { value:"hounsfield:350,2500", text: "CT: Bone body (350/2500)" },
            { value:"hounsfield:40,500", text: "CT: Soft Tissue (40/500)" },
            { value:"hounsfield:40,400", text: "CT: Soft Tissue, pediatric (40/400)" },
            { value:"hounsfield:400,1800", text: "CT: Mediastinum (400/1800)" },
            { value:"hounsfield:-180,2600", text: "CT: Bronchial (-180/2600)" },
            { value:"hounsfield:-350,2000", text: "CT: Lung (-350/2000)" },
            { value:"hounsfield:-700,1200", text: "CT: Lung (-700/1200)" },
            { value:"hounsfield:-20,400", text: "CT: Abdomen (-20/400)" },
            { value:"hounsfield:60,180", text: "CT: Liver (60/180)" },
            { value:"hounsfield:40,150", text: "CT: Liver without contrast (40/150)" },
            { value:"hounsfield:100,150", text: "CT: Liver with contrast (100/150)" },
            { value:"hounsfield:30,180", text: "CT: P Fossa (30/180)" },
            { value:"hounsfield:40,250", text: "CT: Cervical spine without contrast (40/250)" },
            { value:"hounsfield:40,500", text: "CT: Thoracic and Lumbar spine (40/500)" },
            { value:"hounsfield:40,60", text: "CT: Infarct (40/60)" },
            { value:"hounsfield:200,700", text: "CT: OBLIQUE MIP (200/700)" },
            { value:"hounsfield:60,650", text: "CT: MYELOGRAM W/L (60/650)" },
        ];
        enhancement_options.push.apply(enhancement_options, dicom_options);
    }

    return enhancement_options;
};

// Display channel colors, mix metadata, system and object preferences

BQImagePhys.prototype.fusion2string = function () {
    var colors = this.channel_colors_display || this.channel_colors,
        fusion='';
    for (var i=0; i<colors.length; i++) {
        fusion += colors[i].getRed() + ',';
        fusion += colors[i].getGreen() + ',';
        fusion += colors[i].getBlue() + ';';
    }
    return fusion;
};

BQImagePhys.prototype.prefsSetFusion = function (resource_uniq) {
    var fusion = this.fusion2string();
    BQ.Preferences.set(resource_uniq, 'Viewer/fusion', fusion);
};

BQImagePhys.prototype.prefsGetFusion = function (resource_uniq, channel_colors) {
    var fusion = BQ.Preferences.get(resource_uniq, 'Viewer/fusion', '').split(':')[0],
        channels = fusion.split(';'),
        value = null;
    if (fusion.indexOf(',')===-1) return;

    for (var i=0; i<channels.length; ++i) {
        if (channels[i] && channels[i].indexOf(',')>=0) {
            channel_colors[i] = Ext.draw.Color.fromString('rgb('+channels[i]+')');
        }
    }
    return channel_colors;
};

BQImagePhys.prototype.prefsGetChannelColorMapping = function (resource_uniq) {
    // DAPI=0,0,255;Alexa Fluor 488=255,0,0;
    var p = BQ.Preferences.get(resource_uniq, 'Viewer/preferred_color_per_channel_name', ''),
        pp = p.split(';'),
        v = null,
        map = {};

    for (var i=0; i<pp.length; ++i) {
        v = pp[i].split('=');
        if (v.length !== 2) continue;
        map[v[0].trim()] = Ext.draw.Color.fromString('rgb('+v[1].trim()+')');
    }

    return map;
};

BQImagePhys.prototype.getDisplayColors = function (resource_uniq) {
    if (this.channel_colors_display) return this.channel_colors_display;

    // fetch preferences mapping for channel names
    var map = this.prefsGetChannelColorMapping (resource_uniq),
        n = null, m=null;

    // ensure channel_colors parsed from metadata and then create a display variant
    this.channel_colors = this.channel_colors || [];

    // update from object preferences
    this.prefsGetFusion(resource_uniq, this.channel_colors);

    // clone metadata based channel names, color objects are not really cloned, we'll replace them later
    this.channel_colors_display = this.channel_colors.slice(0);

    // update from preferred mapping per channel name
    for (var i = 0; i < this.channel_names.length; i++) {
        n = this.channel_names[i];
        m = this.find_match(n, map);
        if (m) {
            this.channel_colors_display[i] = map[m];
        }
    }

    // finally, update from object preferences
    this.prefsGetFusion(resource_uniq, this.channel_colors_display);

    return this.channel_colors_display;
};

// Display channel names, mix metadata, system and object preferences

BQImagePhys.prototype.find_match = function (n, map) {
    if (n in map) return n;

    // try to match map to the name
    for (var i in map) {
        if (n.indexOf(i)>=0) return i;
        if (i.indexOf(n)>=0) return i;
    }

    return null;
};

BQImagePhys.prototype.prefsGetChannelNameMapping = function (resource_uniq) {
    // DAPI=Nuclear;Alexa Fluor 488=Membrane;
    var p = BQ.Preferences.get(resource_uniq, 'Viewer/preferred_text_per_channel_name', ''),
        pp = p.split(';'),
        v = null,
        map = [];

    for (var i=0; i<pp.length; ++i) {
        v = pp[i].split('=');
        if (v.length !== 2) continue;
        map[v[0].trim()] = v[1].trim();
    }

    return map;
};

BQImagePhys.prototype.getDisplayNames = function (resource_uniq) {
    if (this.channel_names_display) return this.channel_names_display;

    // fetch preferences mapping for channel names
    var map = this.prefsGetChannelNameMapping (resource_uniq),
        n = null, m=null;

    // first clone metadata based channel names
    this.channel_names_display = this.channel_names.slice(0);

    // update final display values
    for (var i = 0; i < this.channel_names.length; i++) {
        n = this.channel_names[i];
        m = this.find_match(n, map);
        if (m) {
            this.channel_names_display[i] = map[m];
        }
    }
    return this.channel_names_display;
};

//-------------------------------------------------------------------------------
// parseUri
//-------------------------------------------------------------------------------

/* parseUri JS v0.1, by Steven Levithan (http://badassery.blogspot.com)
Splits any well-formed URI into the following parts (all are optional):
----------------------
* source (since the exec() method returns backreference 0 [i.e., the entire match] as key 0, we might as well use it)
* protocol (scheme)
* authority (includes both the domain and port)
    * domain (part of the authority; can be an IP address)
    * port (part of the authority)
* path (includes both the directory path and filename)
    * directoryPath (part of the path; supports directories with periods, and without a trailing backslash)
    * fileName (part of the path)
* query (does not include the leading question mark)
* anchor (fragment)
*/
function parseUri(sourceUri){
    var uriPartNames = ["source","protocol","authority","domain","port","path","directoryPath","fileName","query","anchor"];
    var uriParts = new RegExp("^(?:([^:/?#.]+):)?(?://)?(([^:/?#]*)(?::(\\d*))?)?((/(?:[^?#](?![^?#/]*\\.[^?#/.]+(?:[\\?#]|$)))*/?)?([^?#/]*))?(?:\\?([^#]*))?(?:#(.*))?").exec(sourceUri);
    var uri = {};

    for(var i = 0; i < 10; i++){
        uri[uriPartNames[i]] = (uriParts[i] ? uriParts[i] : "");
    }

    // Always end directoryPath with a trailing backslash if a path was present in the source URI
    // Note that a trailing backslash is NOT automatically inserted within or appended to the "path" key
    if(uri.directoryPath.length > 0){
        uri.directoryPath = uri.directoryPath.replace(/\/?$/, "/");
    }

    return uri;
};

// strip off all query params
function stripParams(uri) {
    return uri ? uri.split('?')[0] : uri;
};

function BQUrl (u){
  this.uri = parseUri(u);
};

BQUrl.prototype.toString = function () {
  return this.uri['source'];
};

BQUrl.prototype.server = function () {
  return this.uri['protocol'] + '://' + this.uri['authority'];
};

//-------------------------------------------------------------------------------
// BQUser
//-------------------------------------------------------------------------------

function BQUser (){
    BQObject.call(this);
    this.resource_type = "user";
};

BQUser.prototype = new BQObject();
//extend(BQUser, BQObject);

BQUser.prototype.initializeXml = function (node) {
    BQObject.prototype.initializeXml.call(this, node);
    this.user_name     = this.name;
    this.display_name  = this.user_name;
    this.email         = this.value;
    this.email_address = this.email;
};

BQUser.prototype.afterInitialized = function () {
    var display_name  = this.find_tags('display_name');
    this.display_name = (display_name && display_name.value)?display_name.value:this.user_name;
};

BQUser.prototype.get_credentials = function( cb) {
    BQFactory.load (BQ.Server.url('/auth_service/credentials/'));
};

BQUser.prototype.on_credentials = function(cb, cred) {
    this.credentials = cred;
    this.credentials.convert_tags();
    if (cb) cb(cred);
};

BQUser.prototype.is_admin = function () {
    return this.groups && this.groups.indexOf ('admin')>-1;
};

//-------------------------------------------------------------------------------
// BQUser - static methods to cache users
//-------------------------------------------------------------------------------

BQUser.users = {};

BQUser.fetch_user = function(uri, cb, errorcb) {
    if (uri in BQUser.users) {
        cb(BQUser.users[uri]);
        return;
    }
    BQFactory.request({
        uri: uri,
        errorcb: errorcb,
        cb: function(resource) {
            BQUser.users[uri] = resource;
            cb(BQUser.users[uri]);
        },
        cache: true,
        uri_params: {view:'full'},
    });
};

//-------------------------------------------------------------------------------
// BQAuth
//-------------------------------------------------------------------------------

function BQAuth (user, email, action) {
    BQObject.call(this);
    this.resource_type = "auth";
    this.xmlfields = [ "action", "user", "email" ];

    if (user && user !== '') this.user = user;
    if (email && email !== '') this.email = email;
    if (action && action !== '') this.action = action;
};

BQAuth.prototype = new BQObject();
//extend(BQAuth, BQObject);

BQAuth.prototype.initializeXml = function (node) {
    BQObject.prototype.initializeXml.call(this, node);

    // dima: DIFFERENT ATTRIBUTES!!!
    this.action = attribStr(node, 'action');
    this.email  = attribStr(node, 'email');
    this.user   = attribStr(node, 'user');
};

BQAuth.prototype.save_ = function (node)
{
    debugger;
};

//-------------------------------------------------------------------------------
// BQModule
// dima: should produce MEX from inputs section, have both input and output trees
// have them indexed in a flat way for easy access to elements
// template parsing?
//-------------------------------------------------------------------------------

function BQModule () {
    this.readonly = true;
    this.reserved_io_types = {'system-input':null, 'template':null, };
    this.configs = { 'help': 'help',
                     'thumbnail': 'thumbnail',
                     'title': 'title',
                     'authors': 'authors',
                     'description': 'description',
                     'display_options/group': 'group',
                     'module_options/version': 'version',
                     /*'interface': 'interface', // will be missing a tag type
                     'execute_options/type': 'type',
                     'execute_options/parameters': 'parameters',
                     'execute_options/application': 'application',*/
                   };

    BQObject.call(this);
    this.resource_type = "module";
};
BQModule.prototype = new BQObject();

BQModule.prototype.afterInitialized = function () {

    // now copy over all other config params
    var dict = this.toDict(true);
    for (var i in this.configs) {
        if (i in dict && !(i in this))
            this[this.configs[i]] = dict[i];
    }

    // define inputs and outputs
    //BQObject.prototype.afterInitialized.call ();
    var inputs  = this.find_tags('inputs');
    if (inputs && inputs.tags) {
        this.inputs = inputs.tags; // dima - this should be children in the future
        this.inputs_index  = inputs.create_flat_index();
        // fix parent links
        for (var p=0; (t=inputs.tags[p]); p++) {
            t.parent = inputs;
        }
    }

    var outputs = this.find_tags('outputs');
    if (outputs && outputs.tags) {
        this.outputs = outputs.tags; // dima - this should be children in the future
        this.outputs_index  = outputs.create_flat_index();
        // fix parent links
        for (var p=0; (t=outputs.tags[p]); p++) {
            t.parent = outputs;
        }
    }

    // create sorted iterable resource names
    if ('execute_options/iterable' in dict) {
        this.iterables = [].concat( dict['execute_options/iterable'] );
        // make sure dataset renderer is there
        var name = this.iterables[0];
        if (!(name in this.outputs_index)) {
            var r = new BQTag(undefined, name, undefined, 'dataset');
            this.outputs.push(r);
            this.outputs_index[name] = r;
        }
    }
    this.tags_index = dict;

    this.updateTemplates();
};

BQModule.prototype.updateTemplates = function () {
    // create accepted_type
    // unfortunately there's no easy way to test if JS vector has an element
    // change the accepted_type to an object adding the type of the resource
    for (var i in this.inputs_index) {
        var e = this.inputs_index[i];
        if (e.template) {
            var act = {};
            if (e.type) act[e.type] = e.type;

            if (e.template.accepted_type) {
                if (e.template.accepted_type.constructor === String) {
                    act[e.template.accepted_type] = e.template.accepted_type;
                } else if (e.template.accepted_type.constructor === Array) {
                    for (var p=0; (t=e.template.accepted_type[p]); p++)
                        act[t] = t;
                }
            }

            e.template.accepted_type = act;
        }
    }
};


BQModule.prototype.fromNode = function (node) {
    this.initializeXml(node);
};

BQModule.prototype.createMEX = function( ) {
    var mex = new BQMex();

    // create INPUTS block
    var tag_inputs = mex.addtag ({name:'inputs'});
    var i = undefined;
    for (var p=0; (i=this.inputs[p]); p++) {
        var r = i.clone(true);
        tag_inputs.addchild(r);
    }

    // create OUTPUTS block
    //var tag_outputs = mex.addtag ({name:'outputs'}); // dima: the outputs tag will be created by the module?

    // dima: the new iterable structure does not require module to post this anymore
    //       instead MS would look into module definition file for itarables
    // create execute_options block
    if (this.iterables && this.iterables.length>0) {
        var tag_execute = mex.addtag ({name:'execute_options'});
        var iterable_name = undefined;
        var exec_options = [].concat(this.find_tags("execute_options"));
        for (var p=0; (iterable_name=this.iterables[p]); p++) {
            var i = this.inputs_index[iterable_name];
            if (!i) continue;
            // determine the type of the iterable:
            // if i.name is in execute_options/iterable (i.e., pre-defined iterable), use the type listed there
            // if not (i.e., a dynamically added iterable), use i.type
            var iterable_type = i.type;
            var iterable_kids = [];
            if (exec_options.length >= 1) {
                var static_iters = [].concat(exec_options[0].find_tags("iterable"));
                for (var idx=0; (static_iter=static_iters[idx]); idx++) {
                    if (static_iter.value == i.name) {
                        if (static_iter.type == i.type) {
                            iterable_type = static_iter.type;
                            iterable_kids = static_iter.tags;
                        }
                        else {
                            iterable_type = undefined;   // nothing iterable
                        }
                        break;
                    }
                }
            }
            if (iterable_type) {
                iter_tag = tag_execute.addtag({ name:'iterable', value:i.name, type:iterable_type, });
                for (var kid_idx=0; kid_idx < iterable_kids.length; kid_idx++) {
                    iter_tag.addtag(iterable_kids[kid_idx]);
                }
            }
        }
        // add coupled iter flag if requested
        if (this.coupled_iter) {
            tag_execute.addtag({ name:'coupled_iter', value:true, });
        }
        // add blocked iter flag if found in module def
        if (exec_options.length >= 1) {
            var blocked_iter = exec_options[0].find_tags("blocked_iter");
            if (blocked_iter && blocked_iter.value.toLowerCase() == 'true') {
                tag_execute.addtag({ name:'blocked_iter', value:true, });
            }
        }
    }

    return mex;
};


//-------------------------------------------------------------------------------
// BQMex
//-------------------------------------------------------------------------------

function BQMex (){
    BQObject.call(this);
    this.resource_type = "mex";
};

BQMex.prototype = new BQObject();
BQMex.prototype.initializeXml = function (node) {
    BQObject.prototype.initializeXml.call(this, node);
    this.status = this.value;
};

BQMex.prototype.isMultiMex = function () {
    if (this.children && this.children[0] instanceof BQMex) return true;
    if (!this.iterables) return false;
    return (Object.keys(this.iterables).length>0);
};

// creates mapping from iterable resources in sub MEXes to their MEXes
BQMex.prototype.findMexsForIterable = function (name, root) {
    root = root || 'inputs/';
    this.iterables = this.iterables || {};
    if (!name || this.children.length<1) return;
    this.dict = this.dict || this.toDict(true);

    var dataset = this.dict[root+name];
    this.iterables[name] = this.iterables[name] || {};
    this.iterables[name]['dataset'] = dataset;

    var o=null;
    for (var i=0; (o=this.children[i]); i++) {
        if (o instanceof BQMex) {
            var resource = o.dict[root+name];
            if (resource) this.iterables[name][resource] = o;
        }
    }
};

BQMex.prototype.afterInitialized = function () {
    //BQObject.prototype.afterInitialized.call ();
    this.dict = this.dict || this.toDict(true);

    // finally execute afterInitialized
    var inputs  = this.find_tags('inputs');
    if (inputs instanceof Array)
        inputs = inputs[0];
    if (inputs && inputs.tags) {
        this.inputs = inputs.tags; // dima - this should be children in the future
        this.inputs_index  = inputs.create_flat_index();
        // fix parent links
        for (var p=0; (t=inputs.tags[p]); p++) {
            t.parent = inputs;
        }
    }

    var outputs = this.find_tags('outputs');
    if (outputs instanceof Array)
        outputs = outputs[0];
    if (outputs && outputs.tags) {
        this.outputs = outputs.tags; // dima - this should be children in the future
        this.outputs_index  = outputs.create_flat_index();
        // fix parent links
        for (var p=0; (t=outputs.tags[p]); p++) {
            t.parent = outputs;
        }
    }

    // check if the mex has iterables
    if (this.dict['execute_options/iterable']) {
        var name = this.dict['execute_options/iterable'];
        this.findMexsForIterable(name, 'inputs/');
        // if the main output does not have a dataset resource, create one
        this.outputs = this.outputs || [];
        this.outputs_index = this.outputs_index || {};
        if (!(name in this.outputs_index) && this.iterables && name in this.iterables && 'dataset' in this.iterables[name]) {
            var r = new BQTag(undefined, name, this.iterables[name]['dataset'], 'dataset');
            this.outputs.push(r);
            this.outputs_index[name] = r;
        }
    }
};


//-------------------------------------------------------------------------------
// BQDataset
// Each dataset has a special tag 'members' that contains a list
// of the dataset's resources/
// BQFactory.load("/ds/datasets/", callback(this, 'datasets_loaded')
// dataset_loaded (dataset)
//    dataset.getMembers (with_members)
// with_member (members)
//    for (var i =0; i<members.children.length;i++)
//       resource = members.children[i]
//       console.log(resource.uri)
// }

//-------------------------------------------------------------------------------
function BQDataset (){
    BQObject.call(this);
    this.resource_type = "dataset";
};
BQDataset.prototype = new BQObject();

// dima: some method is required to figure out if an additional fetch is required
BQDataset.prototype.getMembers = function (cb) {
    // Call the callback cb with the members tag when loaded
    /*
    var members = this.find_tags ('members');
    if (!members) {
        this.load_tags (callback(this, 'members_loaded', cb));
    } else {
        if (cb) cb(members);
        return members;
    }
    */
    // we need to make sure we fetched values before we can do this properly
    //this.values = this.values || [];

    if (!this.members) {
        BQFactory.request({
            uri: this.uri + '/value',
            cb: callback(this, '_loaded', cb),
            //uri_params: {view:'deep'}
        });
    } else {
        if (cb) cb(this);
    }
    return this;
};
BQDataset.prototype._loaded = function (cb, resource) {
    this.members = resource.children || [];
    if (cb) cb(this);
};

BQDataset.prototype.setMembers = function (nvs) {
    this.values = nvs;
};

BQDataset.prototype.appendMembers = function (newmembers, cb) {
    this.getMembers (callback (this, this.appendMembersResp, newmembers, cb));
};

BQDataset.prototype.appendMembersResp = function (newmembers, cb, members_tag) {
    var members = members_tag.values.concat(newmembers);
    this.setMembers (members);
    if (cb) cb();
};

// deleteMembers    : Deletes members of a temporary dataset (which hasn't been saved, hence no URI)
//                  : Calls individual deletes on the resources and collects results
// output           : callback is called with an object summary which has two members, success and failure e.g.
//                  : summary : {success:7, failure:3}
// temporary until we come up with a permanent (backend?) solution

BQDataset.prototype.tmp_deleteMembers = function(cb)
{
    Ext.apply(this,
    {
        tmp_cb      :   cb,
        tmp_success :   0,
        tmp_failure :   0,
        tmp_final   :   this.tmp_members.length
    });

    function result(success)
    {
        success?this.tmp_success++:this.tmp_failure++;

        if ((this.tmp_success+this.tmp_failure)==this.tmp_final)
            cb({success:this.tmp_success, failure:this.tmp_failure});
    }

    for (var i=0; i<this.tmp_members.length; i++)
        this.tmp_members[i].resource.delete_(Ext.pass(result, [true], this), Ext.pass(result, [false], this));
};

// method for a temporary dataset to set new members
// assumes members are BQResources for now
BQDataset.prototype.tmp_setMembers = function(members)
{
    if (!(members instanceof Array))
        members = [members];

    this.tmp_members = members;
};

// method for a temporary dataset to download all member resources into one TARball
BQDataset.prototype.tmp_downloadMembers = function()
{
    var exporter = Ext.create('BQ.Export.Panel'), members=[];

    for (var i=0; i<this.tmp_members.length; i++)
        members.push(this.tmp_members[i].resource);

    exporter.downloadResource(members, 'tar');
};

// method for a temporary dataset to change permission on all member resources
BQDataset.prototype.tmp_changePermission = function(permission, success, failure)
{
    var no = {count:this.tmp_members.length};

    function result(no, success)
    {
        if (--no.count==0) success();
    }

    for (var i=0; i<this.tmp_members.length; i++)
        this.tmp_members[i].changePrivacy(permission, Ext.pass(result, [no, success]));
};

// method for a temporary dataset to share all member resources
BQDataset.prototype.tmp_shareMembers = function() {
    if (this.tmp_members.length<=0)
        return;
    var exporter = Ext.create('BQ.share.MultiDialog', {
        resources : this.tmp_members,
        permission: this.tmp_members[0].resource.permission,
    });
};



//-------------------------------------------------------------------------------
// BQSession
//-------------------------------------------------------------------------------

function BQSession () {
    BQObject.call(this);
    this.current_timer = null;
    this.timeout = null;
    this.expires = null;
    this.user = undefined;
    this.user_uri = undefined;
    this.callbacks = undefined;
};

BQSession.prototype= new BQObject();
BQSession.current_session = undefined;

// Class-Level functions for use in BQApplication
BQSession.reset_session  = function (){
    // Called to reset time on countdown clock..
    if (BQSession.current_session)
        BQSession.current_session.reset_timeout();
};
BQSession.initialize_session = function (baseurl, opts) {
    if (BQSession.current_session){
        console.log ("SESSION ALREADY SET");
        return ;
    }
    // Load first Session
    BQFactory.load (baseurl + BQ.Server.url("/auth_service/session"),
                    function (session) {
                        BQSession.current_session = session;
                        session.new_session (opts);
                    }, null, false);
};
BQSession.clear_session = function (baseurl) {
    if (BQSession.current_session) {
        BQSession.current_session.end_session();
        BQSession.current_session = undefined;
    }
};

// Instance level functions
BQSession.prototype.new_session  = function (opts) {
    this.callbacks = opts;
    this.parse_session ();
    if (this.timeout) {
        // tag value  is in seconds while timeout is in milliseconds
        console.log ("timeout in " + this.timeout/1000 + " s" );
        this.reset_timeout();
    } else {
        console.log ('no expire');
    }
    if (this.user_uri){
        //BQFactory.request({uri: this.user_uri, cb: callback(this, 'setUser'), cache: false, uri_params: {view:'full'}});
        BQUser.fetch_user(this.user_uri, callback(this, this.setUser), Ext.emptyFn);
        if (this.callbacks.onsignedin) this.callbacks.onsignedin(this);
    }else{
        if (this.callbacks.onnouser) this.callbacks.onnouser(this);
    }
};

BQSession.prototype.end_session  = function () {
    this.timeout = 0;
    this.reset_timeout();
    if (this.callbacks.onsignedout) {
        this.callbacks.onsignedout(this);
    }
};

BQSession.prototype.reset_timeout  = function (){
    clearTimeout (this.current_timer);
    if (this.timeout)
        this.current_timer = setTimeout (callback(this, 'timeout_checker'), this.timeout);
};

BQSession.prototype.timeout_checker = function () {
    BQFactory.load (this.uri, callback(this, 'check_timeout'));
};

BQSession.prototype.check_timeout = function (newsession) {
    var newuser  = newsession.find_tags('user');
    if (!newuser) {
        // User logged out or session timed out
        this.end_session();
        return;
    }
    if (this.user_uri != newuser.value) {
        //window.location = "/";
        //session.new_session (opts);
        Ext.Msg.alert('New login', 'You logged-in as a different user and may not have access to this resource anymore...', function() {
            location.reload();
        });
        return;
    }
    var expires = newsession.find_tags ('expires');
    if (expires) {
        // Check that we are not passed the expires..
        var expiretime = Date.parse(expires.value);
        var nowtime = Date.now()
        //console.log ("now = " + nowtime + " expire=" + expiretime);
        if (nowtime >  expiretime) {
            window.location = "/auth_service/logout_handler";
        }
    }
    this.reset_timeout();
};

BQSession.prototype.session_timeout = function (baseurl) {
    this.parseTags();
    // timeout in more than 30 seconds ?  then just reset
    // as something unexpected has accessed the session (another browser)?
    if (this.expires > 30000) {
        console.log ("session timeout is resetting: expires =" + this.expires );
        this.set_timeout(baseurl);
        return;
    }
    if (this.onsignedout) this.onsignedout();
    //window.location = baseurl + "/auth_service/logout";
    //alert("Your session has  timed out");
};


BQSession.prototype.parse_session  = function (){
    var timeout = this.find_tags ('timeout');
    var expires = this.find_tags ('expires');

    if (expires && timeout) {
        console.log ("session (timeout, expires) " + timeout.value + ':' + expires.value);
        this.timeout = parseInt (timeout.value) * 1000;
        this.expires = parseInt (expires.value) * 1000;
    }
    var user = this.find_tags ('user');
    if (user) {
        this.user_uri = user.value;
    }
    var groups  = this.find_tags ('group');
    if (groups){
        this.groups = groups.value;
    }
};

BQSession.prototype.hasUser = function () {
    return this.user ? true : false;
};

BQSession.prototype.setUser = function (user) {
    this.user = user;
    user.groups = this.groups;
    if (this.callbacks.ongotuser)
        this.callbacks.ongotuser(this.user);
};



//-------------------------------------------------------------------------
// BQQuery - this is something old that probably should gof
//-------------------------------------------------------------------------

function BQQuery(uri, parent, callback) {
    this.parent = parent;
    this.tags = new Array();
    this.callback = callback;
    makeRequest( uri, this.parseResponse, this , "GET", null );
};

BQQuery.prototype.parseResponse = function(o, data) {
    var tags = data.getElementsByTagName("tag");
    for(var i=0; i<tags.length; i++) {
        o.tags[i] = tags[i].getAttribute('value');
    }
    o.callback(o);
};

//-----------------------------------------------------------------------------
// BQFile
//-----------------------------------------------------------------------------

function BQDir (uri){
    BQObject.call(this, uri);
    this.resource_type = 'dir';
};
BQDir.prototype = new BQObject();

/*BQDir.prototype.initializeXml = function (node) {
    BQObject.prototype.initializeXml.call(this, node);
};*/
