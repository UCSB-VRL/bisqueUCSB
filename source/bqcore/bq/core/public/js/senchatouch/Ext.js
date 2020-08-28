/**
 * @class ExtTouch
 * ExtTouch core utilities and functions.
 * @singleton
 */
if (typeof ExtTouch === "undefined") {
    ExtTouch = {};
}

/**
 * Copies all the properties of config to obj.
 * @param {Object} object The receiver of the properties
 * @param {Object} config The source of the properties
 * @param {Object} defaults A different object that will also be applied for default values
 * @return {Object} returns obj
 * @member ExtTouch apply
 */
ExtTouch.apply = (function() {
    // IE doesn't recognize that toString (and valueOf) method as explicit one but it "thinks" that's a native one.
    for(var key in {valueOf:1}) {
        return function(object, config, defaults) {
            // no "this" reference for friendly out of scope calls
            if (defaults) {
                ExtTouch.apply(object, defaults);
            }
            if (object && config && typeof config === 'object') {
                for (var key in config) {
                    object[key] = config[key];
                }
            }
            return object;
        };
    }
    return function(object, config, defaults) {
        // no "this" reference for friendly out of scope calls
        if (defaults) {
            ExtTouch.apply(object, defaults);
        }
        if (object && config && typeof config === 'object') {
            for (var key in config) {
                object[key] = config[key];
            }
            if (config.toString !== Object.prototype.toString) {
                object.toString = config.toString;
            }
            if (config.valueOf !== Object.prototype.valueOf) {
                object.valueOf = config.valueOf;
            }
        }
        return object;
    };
})();

ExtTouch.apply(ExtTouch, {
    platformVersion: '1.0',
    platformVersionDetail: {
        major: 1,
        minor: 0,
        patch: 3
    },
    userAgent: navigator.userAgent.toLowerCase(),
    cache: {},
    idSeed: 1000,
    BLANK_IMAGE_URL : 'data:image/gif;base64,R0lGODlhAQABAID/AMDAwAAAACH5BAEAAAAALAAAAAABAAEAAAICRAEAOw==',
    isStrict: document.compatMode == "CSS1Compat",

    windowId: 'ExtTouch-window',
    documentId: 'ExtTouch-document',

    /**
    * A reusable empty function
    * @property
    * @type Function
    */
    emptyFn : function() {},

    /**
     * True if the page is running over SSL
     * @type Boolean
     */
    isSecure : /^https/i.test(window.location.protocol),

    /**
     * True when the document is fully initialized and ready for action
     * @type Boolean
     */
    isReady : false,

    /**
     * True to automatically uncache orphaned ExtTouch.Elements periodically (defaults to true)
     * @type Boolean
     */
    enableGarbageCollector : true,

    /**
     * True to automatically purge event listeners during garbageCollection (defaults to true).
     * @type Boolean
     */
    enableListenerCollection : true,

    /**
     * Copies all the properties of config to obj if they don't already exist.
     * @param {Object} obj The receiver of the properties
     * @param {Object} config The source of the properties
     * @return {Object} returns obj
     */
    applyIf : function(object, config) {
        var property, undefined;

        if (object) {
            for (property in config) {
                if (object[property] === undefined) {
                    object[property] = config[property];
                }
            }
        }

        return object;
    },

    /**
     * Repaints the whole page. This fixes frequently encountered painting issues in mobile Safari.
     */
    repaint : function() {
        var mask = ExtTouch.getBody().createChild({
            cls: 'x-mask x-mask-transparent'
        });
        setTimeout(function() {
            mask.remove();
        }, 0);
    },

    /**
     * Generates unique ids. If the element already has an id, it is unchanged
     * @param {Mixed} el (optional) The element to generate an id for
     * @param {String} prefix (optional) Id prefix (defaults "ExtTouch-gen")
     * @return {String} The generated Id.
     */
    id : function(el, prefix) {
        el = ExtTouch.getDom(el) || {};
        if (el === document) {
            el.id = this.documentId;
        }
        else if (el === window) {
            el.id = this.windowId;
        }
        el.id = el.id || ((prefix || 'ExtTouch-gen') + (++ExtTouch.idSeed));
        return el.id;
    },

    /**
     * <p>ExtTouchends one class to create a subclass and optionally overrides members with the passed literal. This method
     * also adds the function "override()" to the subclass that can be used to override members of the class.</p>
     * For example, to create a subclass of ExtTouch GridPanel:
     * <pre><code>
MyGridPanel = ExtTouch.ExtTouchend(ExtTouch.grid.GridPanel, {
constructor: function(config) {

//      Create configuration for this Grid.
    var store = new ExtTouch.data.Store({...});
    var colModel = new ExtTouch.grid.ColumnModel({...});

//      Create a new config object containing our computed properties
//      *plus* whatever was in the config parameter.
    config = ExtTouch.apply({
        store: store,
        colModel: colModel
    }, config);

    MyGridPanel.superclass.constructor.call(this, config);

//      Your postprocessing here
},

yourMethod: function() {
    // etc.
}
});
       </code></pre>
     *
     * <p>This function also supports a 3-argument call in which the subclass's constructor is
     * passed as an argument. In this form, the parameters are as follows:</p>
     * <div class="mdetail-params"><ul>
     * <li><code>subclass</code> : Function <div class="sub-desc">The subclass constructor.</div></li>
     * <li><code>superclass</code> : Function <div class="sub-desc">The constructor of class being ExtTouchended</div></li>
     * <li><code>overrides</code> : Object <div class="sub-desc">A literal with members which are copied into the subclass's
     * prototype, and are therefore shared among all instances of the new class.</div></li>
     * </ul></div>
     *
     * @param {Function} superclass The constructor of class being ExtTouchended.
     * @param {Object} overrides <p>A literal with members which are copied into the subclass's
     * prototype, and are therefore shared between all instances of the new class.</p>
     * <p>This may contain a special member named <tt><b>constructor</b></tt>. This is used
     * to define the constructor of the new class, and is returned. If this property is
     * <i>not</i> specified, a constructor is generated and returned which just calls the
     * superclass's constructor passing on its parameters.</p>
     * <p><b>It is essential that you call the superclass constructor in any provided constructor. See example code.</b></p>
     * @return {Function} The subclass constructor from the <code>overrides</code> parameter, or a generated one if not provided.
     */
    ExtTouchend : function() {
        // inline overrides
        var inlineOverrides = function(o){
            for (var m in o) {
                if (!o.hasOwnProperty(m)) {
                    continue;
                }
                this[m] = o[m];
            }
        };

        var objectConstructor = Object.prototype.constructor;

        return function(subclass, superclass, overrides){
            // First we check if the user passed in just the superClass with overrides
            if (ExtTouch.isObject(superclass)) {
                overrides = superclass;
                superclass = subclass;
                subclass = overrides.constructor != objectConstructor
                    ? overrides.constructor
                    : function(){ superclass.apply(this, arguments); };
            }

            if (!superclass) {
                throw "Attempting to ExtTouchend from a class which has not been loaded on the page.";
            }

            // We create a new temporary class
            var F = function(){},
                subclassProto,
                superclassProto = superclass.prototype;

            F.prototype = superclassProto;
            subclassProto = subclass.prototype = new F();
            subclassProto.constructor = subclass;
            subclass.superclass = superclassProto;

            if(superclassProto.constructor == objectConstructor){
                superclassProto.constructor = superclass;
            }

            subclass.override = function(overrides){
                ExtTouch.override(subclass, overrides);
            };

            subclassProto.superclass = subclassProto.supr = (function(){
                return superclassProto;
            });

            subclassProto.override = inlineOverrides;
            subclassProto.proto = subclassProto;

            subclass.override(overrides);
            subclass.ExtTouchend = function(o) {
                return ExtTouch.ExtTouchend(subclass, o);
            };

            return subclass;
        };
    }(),

    /**
     * Adds a list of functions to the prototype of an existing class, overwriting any existing methods with the same name.
     * Usage:<pre><code>
ExtTouch.override(MyClass, {
newMethod1: function(){
    // etc.
},
newMethod2: function(foo){
    // etc.
}
});
       </code></pre>
     * @param {Object} origclass The class to override
     * @param {Object} overrides The list of functions to add to origClass.  This should be specified as an object literal
     * containing one or more methods.
     * @method override
     */
    override : function(origclass, overrides) {
        ExtTouch.apply(origclass.prototype, overrides);
    },

    /**
     * Creates namespaces to be used for scoping variables and classes so that they are not global.
     * Specifying the last node of a namespace implicitly creates all other nodes. Usage:
     * <pre><code>
ExtTouch.namespace('Company', 'Company.data');
ExtTouch.namespace('Company.data'); // equivalent and preferable to above syntax
Company.Widget = function() { ... }
Company.data.CustomStore = function(config) { ... }
       </code></pre>
     * @param {String} namespace1
     * @param {String} namespace2
     * @param {String} etc
     * @return {Object} The namespace object. (If multiple arguments are passed, this will be the last namespace created)
     * @method namespace
     */
    namespace : function() {
        var ln = arguments.length,
            i, value, split, x, xln, parts, object;

        for (i = 0; i < ln; i++) {
            value = arguments[i];
            parts = value.split(".");
            if (window.ExtTouch) {
                object = window[parts[0]] = Object(window[parts[0]]);
            } else {
                object = arguments.callee.caller.arguments[0];
            }
            for (x = 1, xln = parts.length; x < xln; x++) {
                object = object[parts[x]] = Object(object[parts[x]]);
            }
        }
        return object;
    },

    /**
     * Takes an object and converts it to an encoded URL. e.g. ExtTouch.urlEncode({foo: 1, bar: 2}); would return "foo=1&bar=2".  Optionally,
     * property values can be arrays, instead of keys and the resulting string that's returned will contain a name/value pair for each array value.
     * @param {Object} o The object to encode
     * @param {String} pre (optional) A prefix to add to the url encoded string
     * @return {String}
     */
    urlEncode : function(o, pre) {
        var empty,
            buf = [],
            e = encodeURIComponent;

        ExtTouch.iterate(o, function(key, item){
            empty = ExtTouch.isEmpty(item);
            ExtTouch.each(empty ? key : item, function(val){
                buf.push('&', e(key), '=', (!ExtTouch.isEmpty(val) && (val != key || !empty)) ? (ExtTouch.isDate(val) ? ExtTouch.encode(val).replace(/"/g, '') : e(val)) : '');
            });
        });

        if(!pre){
            buf.shift();
            pre = '';
        }

        return pre + buf.join('');
    },

    /**
     * Takes an encoded URL and and converts it to an object. Example:
     * <pre><code>
ExtTouch.urlDecode("foo=1&bar=2"); // returns {foo: "1", bar: "2"}
ExtTouch.urlDecode("foo=1&bar=2&bar=3&bar=4", false); // returns {foo: "1", bar: ["2", "3", "4"]}
       </code></pre>
     * @param {String} string
     * @param {Boolean} overwrite (optional) Items of the same name will overwrite previous values instead of creating an an array (Defaults to false).
     * @return {Object} A literal with members
     */
    urlDecode : function(string, overwrite) {
        if (ExtTouch.isEmpty(string)) {
            return {};
        }

        var obj = {},
            pairs = string.split('&'),
            d = decodeURIComponent,
            name,
            value;

        ExtTouch.each(pairs, function(pair) {
            pair = pair.split('=');
            name = d(pair[0]);
            value = d(pair[1]);
            obj[name] = overwrite || !obj[name] ? value : [].concat(obj[name]).concat(value);
        });

        return obj;
    },

    /**
     * Convert certain characters (&, <, >, and ') to their HTML character equivalents for literal display in web pages.
     * @param {String} value The string to encode
     * @return {String} The encoded tExtTouch
     */
    htmlEncode : function(value) {
        return ExtTouch.util.Format.htmlEncode(value);
    },

    /**
     * Convert certain characters (&, <, >, and ') from their HTML character equivalents.
     * @param {String} value The string to decode
     * @return {String} The decoded tExtTouch
     */
    htmlDecode : function(value) {
         return ExtTouch.util.Format.htmlDecode(value);
    },

    /**
     * Appends content to the query string of a URL, handling logic for whether to place
     * a question mark or ampersand.
     * @param {String} url The URL to append to.
     * @param {String} s The content to append to the URL.
     * @return (String) The resulting URL
     */
    urlAppend : function(url, s) {
        if (!ExtTouch.isEmpty(s)) {
            return url + (url.indexOf('?') === -1 ? '?' : '&') + s;
        }
        return url;
    },

    /**
     * Converts any iterable (numeric indices and a length property) into a true array
     * Don't use this on strings. IE doesn't support "abc"[0] which this implementation depends on.
     * For strings, use this instead: "abc".match(/./g) => [a,b,c];
     * @param {Iterable} array the iterable object to be turned into a true Array.
     * @param {Number} start a number that specifies where to start the selection.
     * @param {Number} end a number that specifies where to end the selection.
     * @return (Array) array
     */
     toArray : function(array, start, end) {
        return Array.prototype.slice.call(array, start || 0, end || array.length);
     },

     /**
      * Iterates an array calling the supplied function.
      * @param {Array/NodeList/Mixed} array The array to be iterated. If this
      * argument is not really an array, the supplied function is called once.
      * @param {Function} fn The function to be called with each item. If the
      * supplied function returns false, iteration stops and this method returns
      * the current <code>index</code>. This function is called with
      * the following arguments:
      * <div class="mdetail-params"><ul>
      * <li><code>item</code> : <i>Mixed</i>
      * <div class="sub-desc">The item at the current <code>index</code>
      * in the passed <code>array</code></div></li>
      * <li><code>index</code> : <i>Number</i>
      * <div class="sub-desc">The current index within the array</div></li>
      * <li><code>allItems</code> : <i>Array</i>
      * <div class="sub-desc">The <code>array</code> passed as the first
      * argument to <code>ExtTouch.each</code>.</div></li>
      * </ul></div>
      * @param {Object} scope The scope (<code>this</code> reference) in which the specified function is executed.
      * Defaults to the <code>item</code> at the current <code>index</code>util
      * within the passed <code>array</code>.
      * @return See description for the fn parameter.
      */
     each : function(array, fn, scope) {
         if (ExtTouch.isEmpty(array, true)) {
             return 0;
         }
         if (!ExtTouch.isIterable(array) || ExtTouch.isPrimitive(array)) {
             array = [array];
         }
         for (var i = 0, len = array.length; i < len; i++) {
             if (fn.call(scope || array[i], array[i], i, array) === false) {
                 return i;
             }
         }
         return true;
     },

     /**
      * Iterates either the elements in an array, or each of the properties in an object.
      * <b>Note</b>: If you are only iterating arrays, it is better to call {@link #each}.
      * @param {Object/Array} object The object or array to be iterated
      * @param {Function} fn The function to be called for each iteration.
      * The iteration will stop if the supplied function returns false, or
      * all array elements / object properties have been covered. The signature
      * varies depending on the type of object being interated:
      * <div class="mdetail-params"><ul>
      * <li>Arrays : <tt>(Object item, Number index, Array allItems)</tt>
      * <div class="sub-desc">
      * When iterating an array, the supplied function is called with each item.</div></li>
      * <li>Objects : <tt>(String key, Object value, Object)</tt>
      * <div class="sub-desc">
      * When iterating an object, the supplied function is called with each key-value pair in
      * the object, and the iterated object</div></li>
      * </ul></divutil>
      * @param {Object} scope The scope (<code>this</code> reference) in which the specified function is executed. Defaults to
      * the <code>object</code> being iterated.
      */
     iterate : function(obj, fn, scope) {
         if (ExtTouch.isEmpty(obj)) {
             return;
         }
         if (ExtTouch.isIterable(obj)) {
             ExtTouch.each(obj, fn, scope);
             return;
         }
         else if (ExtTouch.isObject(obj)) {
             for (var prop in obj) {
                 if (obj.hasOwnProperty(prop)) {
                     if (fn.call(scope || obj, prop, obj[prop], obj) === false) {
                         return;
                     }
                 }
             }
         }
     },

    /**
     * Plucks the value of a property from each item in the Array
     *
// Example:
ExtTouch.pluck(ExtTouch.query("p"), "className"); // [el1.className, el2.className, ..., elN.className]
     *
     * @param {Array|NodeList} arr The Array of items to pluck the value from.
     * @param {String} prop The property name to pluck from each element.
     * @return {Array} The value from each item in the Array.
     */
    pluck : function(arr, prop) {
        var ret = [];
        ExtTouch.each(arr, function(v) {
            ret.push(v[prop]);
        });
        return ret;
    },

    /**
     * Returns the current document body as an {@link ExtTouch.Element}.
     * @return ExtTouch.Element The document body
     */
    getBody : function() {
        return ExtTouch.get(document.body || false);
    },

    /**
     * Returns the current document head as an {@link ExtTouch.Element}.
     * @return ExtTouch.Element The document head
     */
    getHead : function() {
        var head;

        return function() {
            if (head == undefined) {
                head = ExtTouch.get(DOC.getElementsByTagName("head")[0]);
            }

            return head;
        };
    }(),

    /**
     * Returns the current HTML document object as an {@link ExtTouch.Element}.
     * @return ExtTouch.Element The document
     */
    getDoc : function() {
        return ExtTouch.get(document);
    },

    /**
     * This is shorthand reference to {@link ExtTouch.ComponentMgr#get}.
     * Looks up an existing {@link ExtTouch.Component Component} by {@link ExtTouch.Component#id id}
     * @param {String} id The component {@link ExtTouch.Component#id id}
     * @return ExtTouch.Component The Component, <tt>undefined</tt> if not found, or <tt>null</tt> if a
     * Class was found.
    */
    getCmp : function(id) {
        return ExtTouch.ComponentMgr.get(id);
    },

    /**
     * Returns the current orientation of the mobile device
     * @return {String} Either 'portrait' or 'landscape'
     */
    getOrientation: function() {
        return window.innerHeight > window.innerWidth ? 'portrait' : 'landscape';
    },

    isIterable : function(v) {
        if (!v) {
            return false;
        }
        //check for array or arguments
        if (ExtTouch.isArray(v) || v.callee) {
            return true;
        }
        //check for node list type
        if (/NodeList|HTMLCollection/.test(Object.prototype.toString.call(v))) {
            return true;
        }

        //NodeList has an item and length property
        //IXMLDOMNodeList has nExtTouchNode method, needs to be checked first.
        return ((typeof v.nExtTouchNode != 'undefined' || v.item) && ExtTouch.isNumber(v.length)) || false;
    },

    /**
     * Utility method for validating that a value is numeric, returning the specified default value if it is not.
     * @param {Mixed} value Should be a number, but any type will be handled appropriately
     * @param {Number} defaultValue The value to return if the original value is non-numeric
     * @return {Number} Value, if numeric, else defaultValue
     */
    num : function(v, defaultValue) {
        v = Number(ExtTouch.isEmpty(v) || ExtTouch.isArray(v) || typeof v == 'boolean' || (typeof v == 'string' && ExtTouch.util.Format.trim(v).length == 0) ? NaN : v);
        return isNaN(v) ? defaultValue : v;
    },

    /**
     * <p>Returns true if the passed value is empty.</p>
     * <p>The value is deemed to be empty if it is<div class="mdetail-params"><ul>
     * <li>null</li>
     * <li>undefined</li>
     * <li>an empty array</li>
     * <li>a zero length string (Unless the <tt>allowBlank</tt> parameter is <tt>true</tt>)</li>
     * </ul></div>
     * @param {Mixed} value The value to test
     * @param {Boolean} allowBlank (optional) true to allow empty strings (defaults to false)
     * @return {Boolean}
     */
    isEmpty : function(value, allowBlank) {
        var isNull       = value == null,
            emptyArray   = (ExtTouch.isArray(value) && !value.length),
            blankAllowed = !allowBlank ? value === '' : false;

        return isNull || emptyArray || blankAllowed;
    },

    /**
     * Returns true if the passed value is a JavaScript array, otherwise false.
     * @param {Mixed} value The value to test
     * @return {Boolean}
     */
    isArray : function(v) {
        return Object.prototype.toString.apply(v) === '[object Array]';
    },

    /**
     * Returns true if the passed object is a JavaScript date object, otherwise false.
     * @param {Object} object The object to test
     * @return {Boolean}
     */
    isDate : function(v) {
        return Object.prototype.toString.apply(v) === '[object Date]';
    },

    /**
     * Returns true if the passed value is a JavaScript Object, otherwise false.
     * @param {Mixed} value The value to test
     * @return {Boolean}
     */
    isObject : function(v) {
        return !!v && !v.tagName && Object.prototype.toString.call(v) === '[object Object]';
    },

    /**
     * Returns true if the passed value is a JavaScript 'primitive', a string, number or boolean.
     * @param {Mixed} value The value to test
     * @return {Boolean}
     */
    isPrimitive : function(v) {
        return ExtTouch.isString(v) || ExtTouch.isNumber(v) || ExtTouch.isBoolean(v);
    },

    /**
     * Returns true if the passed value is a JavaScript Function, otherwise false.
     * @param {Mixed} value The value to test
     * @return {Boolean}
     */
    isFunction : function(v) {
        return Object.prototype.toString.apply(v) === '[object Function]';
    },

    /**
     * Returns true if the passed value is a number. Returns false for non-finite numbers.
     * @param {Mixed} value The value to test
     * @return {Boolean}
     */
    isNumber : function(v) {
        return Object.prototype.toString.apply(v) === '[object Number]' && isFinite(v);
    },

    /**
     * Returns true if the passed value is a string.
     * @param {Mixed} value The value to test
     * @return {Boolean}
     */
    isString : function(v) {
        return typeof v === 'string';
    },

    /**util
     * Returns true if the passed value is a boolean.
     * @param {Mixed} value The value to test
     * @return {Boolean}
     */
    isBoolean : function(v) {
        return Object.prototype.toString.apply(v) === '[object Boolean]';
    },

    /**
     * Returns true if the passed value is an HTMLElement
     * @param {Mixed} value The value to test
     * @return {Boolean}
     */
    isElement : function(v) {
        return v ? !!v.tagName : false;
    },

    /**
     * Returns true if the passed value is not undefined.
     * @param {Mixed} value The value to test
     * @return {Boolean}
     */
    isDefined : function(v){
        return typeof v !== 'undefined';
    },

    /**
     * Attempts to destroy any objects passed to it by removing all event listeners, removing them from the
     * DOM (if applicable) and calling their destroy functions (if available).  This method is primarily
     * intended for arguments of type {@link ExtTouch.Element} and {@link ExtTouch.Component}, but any subclass of
     * {@link ExtTouch.util.Observable} can be passed in.  Any number of elements and/or components can be
     * passed into this function in a single call as separate arguments.
     * @param {Object...} args An {@link ExtTouch.Element}, {@link ExtTouch.Component}, or an Array of either of these to destroy
     */
    destroy : function() {
        var ln = arguments.length,
            i, arg;

        for (i = 0; i < ln; i++) {
            arg = arguments[i];
            if (arg) {
                if (ExtTouch.isArray(arg)) {
                    this.destroy.apply(this, arg);
                }
                else if (ExtTouch.isFunction(arg.destroy)) {
                    arg.destroy();
                }
                else if (arg.dom) {
                    arg.remove();
                }
            }
        }
    }
});

/**
 * URL to a blank file used by ExtTouch when in secure mode for iframe src and onReady src to prevent
 * the IE insecure content warning (<tt>'about:blank'</tt>, except for IE in secure mode, which is <tt>'javascript:""'</tt>).
 * @type String
 */
ExtTouch.SSL_SECURE_URL = ExtTouch.isSecure && 'about:blank';

ExtTouch.ns = ExtTouch.namespace;

ExtTouch.ns(
    'ExtTouch.util',
    'ExtTouch.data',
    'ExtTouch.list',
    'ExtTouch.form',
    'ExtTouch.menu',
    'ExtTouch.state',
    'ExtTouch.layout',
    'ExtTouch.app',
    'ExtTouch.ux',
    'ExtTouch.plugins',
    'ExtTouch.direct',
    'ExtTouch.lib',
    'ExtTouch.gesture'
);
