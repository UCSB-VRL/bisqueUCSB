// ADD SOME GLOBAL VARS HERE TO KEEP OUR FILE LIST SHORT
// for conformity sake:
// paths will NOT end in a '/' slash
//var server = 'arno.ece.ucsb.edu:8080';
//var fullurl = server  + '/bisquik';

var svgns  = "http://www.w3.org/2000/svg";
var xlinkns  = "http://www.w3.org/1999/xlink";
var xhtmlns = 'http://www.w3.org/1999/xhtml';

// <![CDATA[

// Create a method callback on a javascript objects.
// Used for event handlers binding an object instance
// to a method invocation.
// Usage:
//  on_event =  callback (m, 'some_method' [, arg1, ... ])
// When the event fires the callback will be called with
// both the static arguments and the dynamic arguments provided
// by the event
// Example:
//   m.some_method([arg1, arg,..., evt_arg1, evt_arg2, ...])
//
function callback(obj, method) {
    var thisobj = obj;
    var thismeth = ( typeof method == "string") ? thisobj[method] : method;
    var thisextra = Array.prototype.slice.call(arguments, 2);

    return function() {
        if (!thismeth) return;
        var args = Array.prototype.slice.call(arguments);
        return thismeth.apply(thisobj, thisextra.concat(args));
    };
}
// Create a method callback on a javascript objects.
// Used for event handlers binding an object instance
// to a method invocation.
// Usage:
//  on_event =  callback (m, 'some_method' [, arg1, ... ])
// When the event fires the callback will be called with
// both the static arguments and the dynamic arguments provided
// by the event
// Example:
//   m.some_method( evt_arg1, evt_arg2, ... arg1, arg,...,])
// callback_app{end_args} .. append the fixed args instead of prepending
function callback_app(obj, method) {
    var thisobj = obj;
    var thismeth = ( typeof method == "string") ? thisobj[method] : method;
    var thisextra = Array.prototype.slice.call(arguments, 2);

    return function() {
        var args = Array.prototype.slice.call(arguments);
        return thismeth.apply(thisobj, args.concat (thisextra));
    };
}

/*******************************************************************************
  xpath
*******************************************************************************/

/*
  const unsigned short      ANY_TYPE                       = 0;
  const unsigned short      NUMBER_TYPE                    = 1;
  const unsigned short      STRING_TYPE                    = 2;
  const unsigned short      BOOLEAN_TYPE                   = 3;
  const unsigned short      UNORDERED_NODE_ITERATOR_TYPE   = 4;
  const unsigned short      ORDERED_NODE_ITERATOR_TYPE     = 5;
  const unsigned short      UNORDERED_NODE_SNAPSHOT_TYPE   = 6;
  const unsigned short      ORDERED_NODE_SNAPSHOT_TYPE     = 7;
  const unsigned short      ANY_UNORDERED_NODE_TYPE        = 8;
  const unsigned short      FIRST_ORDERED_NODE_TYPE        = 9;
*/

Ext.namespace('BQ.util');
//var BQ = BQ || {}; // ensure BQ namespace

BQ.util.do_xpath = function(node, expression, result_type) {
	if (!node) return;
    result_type = result_type || XPathResult.ANY_TYPE;
    var xpe = new XPathEvaluator();
    var nsResolver = xpe.createNSResolver(!node.ownerDocument ? node.documentElement : node.ownerDocument.documentElement);
    return xpe.evaluate( expression, node, nsResolver, result_type, null );
};

BQ.util.xpath_nodes = function(node, expression) {
    var result = BQ.util.do_xpath(node, expression, XPathResult.ORDERED_NODE_ITERATOR_TYPE);
    if (!result) return [];
    var found = [];
    var res = null;
    while (res = result.iterateNext())
        found.push(res);
    return found;
};

if (Ext.isIE) {

// dima: need to replace the do_xpath in IE
BQ.util.xpath_nodes = function(node, expression) {
    return node.selectNodes(expression);
};

} // if IE

BQ.util.xpath_node = function(node, expression) {
    var result = BQ.util.do_xpath(node, expression, XPathResult.ANY_UNORDERED_NODE_TYPE);
    if (result) {
        return result.singleNodeValue;
    }
};

BQ.util.xpath_string = function(node, expression) {
    var result = BQ.util.do_xpath(node, expression, XPathResult.STRING_TYPE);
    if (result) {
        return result.stringValue;
    }
};

BQ.util.xpath_number = function(node, expression) {
    var result = BQ.util.do_xpath(node, expression, XPathResult.NUMBER_TYPE);
    if (result) {
        return result.numberValue;
    }
}


/*******************************************************************************
  xhr
*******************************************************************************/

BQ.util.get_xhr_instance = function() {
    var options = [function(){
        return new XMLHttpRequest();
    }, function(){
        return new ActiveXObject('MSXML2.XMLHTTP.3.0');
    }, function(){
        return new ActiveXObject('MSXML2.XMLHTTP');
    }, function(){
        return new ActiveXObject('Microsoft.XMLHTTP');
    }], i=0,
        len = options.length,
        xhr;

    for(i=0; i<len; ++i) {
        try {
            xhr = options[i];
            xhr();
            break;
        } catch(e){}
    }
    return xhr;
};

BQ.util.create_xhr = function() {
    var xhr = BQ.util.get_xhr_instance()();
    if (xhr && xhr.a5) {
        return xhr.a5;
    } else {
        return xhr;
    }
};

/*******************************************************************************
parse strings
*******************************************************************************/

BQ.util.parseStringArrayFloat = function(s) {
    if (!s) return;
    s = s.split(',');
    for (var i=0; i<s.length; ++i) {
        s[i] = parseFloat(s[i]);
    }
    return s;
};

// n - number
// c - number of digits before .
// d - number of digits after .
BQ.util.formatFloat = function(n, c, d, sep) {
    var s = n.toFixed(d),
        p = s.indexOf('.'),
        sep = sep || ' ';
    if (p>=0 && p<c) {
        s = Array(c-p+1).join(sep) + s;
    }
    return s;
};

// n - number
// c - number of digits padded with 0
BQ.util.formatInt = function(n, len) {
    s = n.toString();
    if (s.length < len) {
        s = ('0000000000000000000000' + s).slice(-len);
    }
    return s;
}

BQ.util.clone = function(item, skiptemplate) {
    var type,
        i,
        j,
        k,
        N=0,
        clone,
        key,
        t,
        as_is = {'doc':0, 'parent':0, 'xmlfields':0, 'shape':0, 'edit_parent': 0, },
        ignore = {'parent':0, 'shape':0, 'doc':0, 'edit_parent': 0, };

    if (item === null || item === undefined) {
        return item;
    }

    if (skiptemplate === true && item.resource_type === "template") {
        return undefined;
    }

    // DOM nodes
    // TODO proxy this to Ext.Element.clone to handle automatic id attribute changing
    // recursively
    if (item.nodeType && item.cloneNode) {
        return item.cloneNode(true);
    }

    type = toString.call(item);

    // Array
    if (type === '[object Array]') {
        N = item.length;
        clone = [];
        for (i=0; i<N; ++i) {
            t = BQ.util.clone(item[i], skiptemplate);
            if (t !== undefined && t !== null)
                clone.push(t);
        }

    } else if (type === '[object Function]') {
        return;
    } else if (type === '[object Object]' && item.constructor === Object) {
        clone = {};
        for (key in item) {
            if (key in ignore ) {
                delete clone[key];
            } else if (key in as_is) {
                clone[key] = item[key];
            } else {
                t = BQ.util.clone(item[key], skiptemplate);
                if (t !== undefined && t !== null)
                    clone[key] = t;
                else
                    delete clone[key];
            }
        }
    } else if (type === '[object Object]' && item.resource_type) {
        clone = BQFactory.makeShortCopy(item);
        for (key in item) {
            if (key in ignore) {
                delete clone[key];
            } else if (key in as_is) {
                clone[key] = item[key];
            } else if (toString.call(item[key]) !== '[object Function]') {
                t = BQ.util.clone(item[key], skiptemplate);
                if (t !== undefined && t !== null)
                    clone[key] = t;
                else
                    delete clone[key];
            }
        }
    }

    return clone || item;
};

/*******************************************************************************
  WebGL
*******************************************************************************/

BQ.util.isWebGlAvailable = function() {
    if (typeof(BQ.util.webGlAvailable) !== 'undefined')
        return BQ.util.webGlAvailable;
    try {
        var canvas = document.createElement( 'canvas' );
        BQ.util.webGlAvailable = ( window.WebGLRenderingContext &&
                    ( canvas.getContext( 'webgl' ) ||
                      canvas.getContext( 'experimental-webgl' ) ) );
    } catch(e) {
        BQ.util.webGlAvailable = false;
    }
    return BQ.util.webGlAvailable;
};

/*******************************************************************************

*******************************************************************************/


// e.g.
// str = ellipsis("this is a test", 7, '...')
// str = "this..."

function ellipsis(value, len, eos)
{
    eos = eos || "...";

    if (value && value.length > len)
        return value.substr(0, len-eos.length) + eos;
    return value;
}

// clean up an XML/HTML node by removing all its children nodes
function removeAllChildren(element) {
    while (element.hasChildNodes()) {
        element.removeChild(element.firstChild);
    }
}

// Test if the input object is empty
function isEmptyObject(obj)
{
    return (!Ext.isDefined(obj)) ? true : Object.keys(obj).length === 0;
}


function getX(obj) {
    var curleft = 0;
    while (obj.offsetParent) {
        curleft += obj.offsetLeft;
        obj = obj.offsetParent;
    }
    return curleft;
}

function getY(obj) {
    var curtop = 0;
    while (obj.offsetParent) {
        curtop += obj.offsetTop;
        obj = obj.offsetParent;
    }
    return curtop;
}

function getObj(name)
{
    return document.getElementById(name);
}

function attribDict(node) {
    var d = {};
    var al = node.attributes;
    var i = 0;
    for ( i = 0; i < al.length; i += 1) {
        d[al[i].name] = al[i].value;
    }
    return d;
}

function attribInt(node, a) {
    var v = node.getAttribute(a);
    return v ?  parseInt(v, 10): null;
}

function attribFloat(node, a) {
    var v = node.getAttribute(a);
    return v ? parseFloat(v) : null;
}

function attribStr(node, a) {
    return node.getAttribute(a);
}

function getElement(event) {
    return event.target || event.srcElement;
}

function printXML(node) {
    var xml = "", i = 0, m, at;

    if (node !== null) {
        xml = "<" + node.tagName;
        at = node.attributes;
        if (at) {
            for ( i = 0; i < at.length; i += 1) {
                xml += " " + at[i].name + "=\"" + at[i].value + "\"";
            }
        }
        if (node.hasChildNodes) {
            xml += ">\t";
            for ( m = node.firstChild; m !== null; m = m.nextSibling) {
                xml += printXML(m);
                //m.nodeName +  ";   " ;
            }
            xml += "</" + node.tagName + ">\n";
        } else if (node.value) {
            xml += " value=\"" + node.value + "\"/>\n";
        } else if (node.text) {
            xml += ">" + node.text + "</" + node.tagName + ">\n";
        } else {
            xml += " />\n";
        }
    }
    return xml;
}

// threadsafe asynchronous XMLHTTPRequest code
function makeRequest(url, callback, callbackdata, method, postdata, errorcb) {
    function bindCallback() {
        if (ajaxRequest.readyState === XMLHttpRequest.DONE) {
            //console.log ("ajaxRequest.readyState == 4 and status: " + ajaxRequest.status);
            BQSession.reset_session();
            if (ajaxRequest.status === 200 || ajaxRequest.status === 0) {
                if (ajaxCallback) {
                    if (ajaxRequest.responseXML !== null) {// added to accomodate HTML requests as well as XML requests
                        ajaxCallback(ajaxCallbackData, ajaxRequest.responseXML);
                    } else {
                        ajaxCallback(ajaxCallbackData, ajaxRequest.responseText);
                    }
                } else {
                    console.log("makeRequest - no callback defined: " + url);
                }
            } else {
                var consumed_status = {
                    401 : undefined,
                    403 : undefined,
                    404 : undefined
                };
                var error_short = ("There was a problem with the request:\n" + ajaxRequest.status + ":\t" + ajaxRequest.statusText + "\n");
                var error_str = (error_short + ajaxRequest.responseText);

                if (ajaxRequest.status === 401 || ajaxRequest.status === 403)
                    error_str = "You do not have permission for this operation\nAre you logged in?\n\n" + url;
                else if (ajaxRequest.status === 404)
                    error_str = "Requested resource does not exist:\n" + url;

                if (ajaxCallbackError) {
                    ajaxCallbackError({
                        request : ajaxRequest,
                        message : error_str,
                        message_short : error_short
                    });
                    //throw(error_str);
                    return;
                }

                if (ajaxRequest.status in consumed_status) {
                    //alert(error_str);
                    BQ.ui.error(error_str);
                    return;
                }

                BQ.ui.error(error_str);
                //throw(error_str);
            }
        }
    }

    // use a local variable to hold our request and callback until the inner function is called...
    var ajaxRequest = null;
    var ajaxCallbackData = callbackdata;
    var ajaxCallback = callback;
    var ajaxCallbackError = errorcb;

    try {
        if (window.XMLHttpRequest) {
            ajaxRequest = new XMLHttpRequest();
            ajaxRequest.onreadystatechange = bindCallback;
            if (method == "get" || method == "delete") {
                ajaxRequest.open(method, url, true);
                ajaxRequest.send(null);
            } else {
                ajaxRequest.open(method, url, true);
                //ajaxRequest.setRequestHeader("Content-Type","application/x-www-form-urlencoded; charset=UTF-8");
                ajaxRequest.setRequestHeader("Content-Type", "text/xml");
                ajaxRequest.send(postdata);
            }
            return ajaxRequest;
        }
    } catch (e) {
        console.log("Exception in Ajax request: " + e.toString());
    }
}

// Will call on response will call cb (xmldata)

function xmlrequest(url, cb, method, postdata, errorcb) {
    function checkResponse() {
        if (ajaxRequest.readyState === XMLHttpRequest.DONE) {
            BQSession.reset_session();
            if (ajaxRequest.status === 200) {
                if (ajaxRequest.callback) {
                    if (ajaxRequest.responseXML !== null) {
                        // added to accomodate HTML requests
                        // as well as XML requests
                        ajaxRequest.callback(ajaxRequest.responseXML);
                    }
                    else {
                        console.log('WARNING: xmlrequest return text/html');
                        ajaxRequest.callback(ajaxRequest.responseText);
                    }
                }
                else {
                    console.log("xmlrequest - no callback defined: " + url);
                }
            } else {
                var error_short = "There was a problem with the request:\n";
                if (ajaxRequest.request_url)
                    error_short += 'URL: ' + ajaxRequest.request_url + '\n';
                error_short += 'Status: ' + ajaxRequest.status + '\n';
                error_short += 'Message: ' + ajaxRequest.statusText + '\n';
                var error_str = (error_short + ajaxRequest.responseText);

                var consumed_status = {401 : undefined, 403 : undefined, 404 : undefined,};
                if (ajaxRequest.status === 401) {
                    //error_str = "You do not have permission for this operation\nAre you logged in?\n\n"+url;
                    window.location = "/auth_service/login?came_from=" + window.location;
                }  else if (ajaxRequest.status === 403) {
                    error_str = "You do not have permission for this operation:\n" + url;
                } else if (ajaxRequest.status === 404) {
                    error_str = "Requested resource does not exist:\n" + url;
                }

                if (ajaxRequest.errorcallback) {
                    ajaxRequest.errorcallback({
                        request : ajaxRequest,
                        message : error_str,
                        message_short : error_short
                    });
                }

                // Utkarsh : This shouldn't be called again if a default_error_callback is configured for all requests
                //           Leads to two error message popups
                //BQ.ui.error(error_str);

                //throw(error_str);
            }
        }
    }

    var ajaxRequest = null;
    try {
        if (window.XMLHttpRequest) {
            ajaxRequest = new XMLHttpRequest();
            ajaxRequest.onreadystatechange = checkResponse;
            ajaxRequest.callback = cb;
            ajaxRequest.errorcallback = errorcb;
            ajaxRequest.request_url = url;
            method = method || "get";
            ajaxRequest.open(method, url, true);
            ajaxRequest.setRequestHeader('Accept', 'text/xml');

            if (method === "get" || method === "delete") {
                ajaxRequest.send(null);
            } else {
                //ajaxRequest.setRequestHeader("Content-Type",
                //"application/x-www-form-urlencoded; charset=UTF-8");
                ajaxRequest.setRequestHeader("Content-Type", "text/xml");
                ajaxRequest.send(postdata);
            }
            return ajaxRequest;
        }
    } catch (e) {
        console.log("Exception in Ajax request: " + e.toString());
    }
}

function chainRequest(ajaxRequest, cb) {
    var first = ajaxRequest.callback;
    var second = cb;
    function chain(data) {
        first(data);
        second(data);
    }
    ajaxRequest.callback = chain;
}

if(typeof console == "undefined"){
    window.console = {
        log : function (){}
    };
}

encodeParameters = function(obj) {
    var params = new Array();
    for (key in obj) {
        if (obj[key]) {
            params.push(key + "=" + encodeURIComponent(obj[key]));
        }
    }
    return params.join('&');
};

if (!Array.prototype.reduce) {
    Array.prototype.reduce = function(fun /*, initial*/) {
        var len = this.length;
        if ( typeof fun != "function")
            throw new TypeError();

        // no value to return if no initial value and an empty array
        if (len == 0 && arguments.length == 1)
            throw new TypeError();

        var i = 0;
        if (arguments.length >= 2) {
            var rv = arguments[1];
        } else {
            do {
                if ( i in this) {
                    rv = this[i++];
                    break;
                }

                // if array contains no values, no initial value to return
                if (++i >= len)
                    throw new TypeError();
            } while (true);
        }

        for (; i < len; i++) {
            if ( i in this)
                rv = fun.call(null, rv, this[i], i, this);
        }

        return rv;
    };
}
if (!Array.prototype.forEach) {
    Array.prototype.forEach = function(fun /*, thisp*/) {
        var len = this.length >>> 0;
        if ( typeof fun != "function")
            throw new TypeError();

        var thisp = arguments[1];
        for (var i = 0; i < len; i++) {
            if ( i in this)
                fun.call(thisp, this[i], i, this);
        }
    };
}

Array.prototype.find = function(searchStr) {
    var returnArray = false;
    for (var i = 0; i < this.length; i++) {
        if ( typeof (searchStr) == 'function') {
            if (searchStr.test(this[i])) {
                if (!returnArray) {
                    returnArray = [];
                }
                returnArray.push(i);
            }
        } else {
            if (this[i] === searchStr) {
                if (!returnArray) {
                    returnArray = [];
                }
                returnArray.push(i);
            }
        }
    }
    return returnArray;
};

if (!String.prototype.startswith) {
    String.prototype.startswith = function(input) {
        return this.substr(0, input.length) === input;
    };
};

function extend(child, supertype) {
    child.prototype.__proto__ = supertype.prototype;
}

function isdefined(variable) {
    return ( typeof (window[variable]) == "undefined") ? false : true;
}

// ]]>
