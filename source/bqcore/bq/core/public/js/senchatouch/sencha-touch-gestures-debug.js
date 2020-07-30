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

ExtTouch.onReady = function () {}

/**
 * @class Array
 */
ExtTouch.applyIf(Array.prototype, {
    /**
     * Checks whether or not the specified object exists in the array.
     * @param {Object} o The object to check for
     * @param {Number} from (Optional) The index at which to begin the search
     * @return {Number} The index of o in the array (or -1 if it is not found)
     */
    indexOf: function(o, from) {
        var len = this.length;
        from = from || 0;
        from += (from < 0) ? len: 0;
        for (; from < len; ++from) {
            if (this[from] === o) {
                return from;
            }
        }
        return - 1;
    },

    /**
     * Removes the specified object from the array.  If the object is not found nothing happens.
     * @param {Object} o The object to remove
     * @return {Array} this array
     */
    remove: function(o) {
        var index = this.indexOf(o);
        if (index != -1) {
            this.splice(index, 1);
        }
        return this;
    },

    contains: function(o) {
        return this.indexOf(o) !== -1;
    }
});

/**
 * @class ExtTouch.Element
 * <p>Encapsulates a DOM element, adding simple DOM manipulation facilities, normalizing for browser differences.</p>
 * <p>All instances of this class inherit the methods of {@link ExtTouch.Fx} making visual effects easily available to all DOM elements.</p>
 * <p>Note that the events documented in this class are not ExtTouch events, they encapsulate browser events. To
 * access the underlying browser event, see {@link ExtTouch.EventObject#browserEvent}. Some older
 * browsers may not support the full range of events. Which events are supported is beyond the control of ExtTouchJs.</p>
 * Usage:<br>
<pre><code>
// by id
var el = ExtTouch.get("my-div");

// by DOM element reference
var el = ExtTouch.get(myDivElement);
</code></pre>
 * <b>Animations</b><br />
 * <p>When an element is manipulated, by default there is no animation.</p>
 * <pre><code>
var el = ExtTouch.get("my-div");

// no animation
el.setWidth(100);
 * </code></pre>
 * <p>Many of the functions for manipulating an element have an optional "animate" parameter.  This
 * parameter can be specified as boolean (<tt>true</tt>) for default animation effects.</p>
 * <pre><code>
// default animation
el.setWidth(100, true);
 * </code></pre>
 *
 * <p>To configure the effects, an object literal with animation options to use as the Element animation
 * configuration object can also be specified. Note that the supported Element animation configuration
 * options are a subset of the {@link ExtTouch.Fx} animation options specific to Fx effects.  The supported
 * Element animation configuration options are:</p>
<pre>
Option    Default   Description
--------- --------  ---------------------------------------------
{@link ExtTouch.Fx#duration duration}  .35       The duration of the animation in seconds
{@link ExtTouch.Fx#easing easing}    easeOut   The easing method
{@link ExtTouch.Fx#callback callback}  none      A function to execute when the anim completes
{@link ExtTouch.Fx#scope scope}     this      The scope (this) of the callback function
</pre>
 *
 * <pre><code>
// Element animation options object
var opt = {
    {@link ExtTouch.Fx#duration duration}: 1,
    {@link ExtTouch.Fx#easing easing}: 'elasticIn',
    {@link ExtTouch.Fx#callback callback}: this.foo,
    {@link ExtTouch.Fx#scope scope}: this
};
// animation with some options set
el.setWidth(100, opt);
 * </code></pre>
 * <p>The Element animation object being used for the animation will be set on the options
 * object as "anim", which allows you to stop or manipulate the animation. Here is an example:</p>
 * <pre><code>
// using the "anim" property to get the Anim object
if(opt.anim.isAnimated()){
    opt.anim.stop();
}
 * </code></pre>
 * <p>Also see the <tt>{@link #animate}</tt> method for another animation technique.</p>
 * <p><b> Composite (Collections of) Elements</b></p>
 * <p>For working with collections of Elements, see {@link ExtTouch.CompositeElement}</p>
 * @constructor Create a new Element directly.
 * @param {String/HTMLElement} element
 * @param {Boolean} forceNew (optional) By default the constructor checks to see if there is already an instance of this element in the cache and if there is it returns the same instance. This will skip that check (useful for ExtTouchending this class).
 */

(function() {
var El = ExtTouch.Element = ExtTouch.ExtTouchend(Object, {
    /**
     * The default unit to append to CSS values where a unit isn't provided (defaults to px).
     * @type String
     */
    defaultUnit : "px",

    constructor : function(element, forceNew) {
        var dom = typeof element == 'string'
                ? document.getElementById(element)
                : element,
            id;

        if (!dom) {
            return null;
        }

        id = dom.id;
        if (!forceNew && id && ExtTouch.cache[id]) {
            return ExtTouch.cache[id].el;
        }

        /**
         * The DOM element
         * @type HTMLElement
         */
        this.dom = dom;

        /**
         * The DOM element ID
         * @type String
         */
        this.id = id || ExtTouch.id(dom);
        return this;
    },

    /**
     * Sets the passed attributes as attributes of this element (a style attribute can be a string, object or function)
     * @param {Object} o The object with the attributes
     * @param {Boolean} useSet (optional) false to override the default setAttribute to use expandos.
     * @return {ExtTouch.Element} this
     */
    set : function(o, useSet) {
        var el = this.dom,
            attr,
            value;

        for (attr in o) {
            if (o.hasOwnProperty(attr)) {
                value = o[attr];
                if (attr == 'style') {
                    this.applyStyles(value);
                }
                else if (attr == 'cls') {
                    el.className = value;
                }
                else if (useSet !== false) {
                    el.setAttribute(attr, value);
                }
                else {
                    el[attr] = value;
                }
            }
        }
        return this;
    },

    /**
     * Returns true if this element matches the passed simple selector (e.g. div.some-class or span:first-child)
     * @param {String} selector The simple selector to test
     * @return {Boolean} True if this element matches the selector, else false
     */
    is : function(simpleSelector) {
        return ExtTouch.DomQuery.is(this.dom, simpleSelector);
    },

    /**
     * Returns the value of the "value" attribute
     * @param {Boolean} asNumber true to parse the value as a number
     * @return {String/Number}
     */
    getValue : function(asNumber){
        var val = this.dom.value;
        return asNumber ? parseInt(val, 10) : val;
    },

    /**
     * Appends an event handler to this element.  The shorthand version {@link #on} is equivalent.
     * @param {String} eventName The name of event to handle.
     * @param {Function} fn The handler function the event invokes. This function is passed
     * the following parameters:<ul>
     * <li><b>evt</b> : EventObject<div class="sub-desc">The {@link ExtTouch.EventObject EventObject} describing the event.</div></li>
     * <li><b>el</b> : HtmlElement<div class="sub-desc">The DOM element which was the target of the event.
     * Note that this may be filtered by using the <tt>delegate</tt> option.</div></li>
     * <li><b>o</b> : Object<div class="sub-desc">The options object from the addListener call.</div></li>
     * </ul>
     * @param {Object} scope (optional) The scope (<code><b>this</b></code> reference) in which the handler function is executed.
     * <b>If omitted, defaults to this Element.</b>.
     * @param {Object} options (optional) An object containing handler configuration properties.
     * This may contain any of the following properties:<ul>
     * <li><b>scope</b> Object : <div class="sub-desc">The scope (<code><b>this</b></code> reference) in which the handler function is executed.
     * <b>If omitted, defaults to this Element.</b></div></li>
     * <li><b>delegate</b> String: <div class="sub-desc">A simple selector to filter the target or look for a descendant of the target. See below for additional details.</div></li>
     * <li><b>stopEvent</b> Boolean: <div class="sub-desc">True to stop the event. That is stop propagation, and prevent the default action.</div></li>
     * <li><b>preventDefault</b> Boolean: <div class="sub-desc">True to prevent the default action</div></li>
     * <li><b>stopPropagation</b> Boolean: <div class="sub-desc">True to prevent event propagation</div></li>
     * <li><b>normalized</b> Boolean: <div class="sub-desc">False to pass a browser event to the handler function instead of an ExtTouch.EventObject</div></li>
     * <li><b>target</b> ExtTouch.Element: <div class="sub-desc">Only call the handler if the event was fired on the target Element, <i>not</i> if the event was bubbled up from a child node.</div></li>
     * <li><b>delay</b> Number: <div class="sub-desc">The number of milliseconds to delay the invocation of the handler after the event fires.</div></li>
     * <li><b>single</b> Boolean: <div class="sub-desc">True to add a handler to handle just the nExtTouch firing of the event, and then remove itself.</div></li>
     * <li><b>buffer</b> Number: <div class="sub-desc">Causes the handler to be scheduled to run in an {@link ExtTouch.util.DelayedTask} delayed
     * by the specified number of milliseconds. If the event fires again within that time, the original
     * handler is <em>not</em> invoked, but the new handler is scheduled in its place.</div></li>
     * </ul><br>
     * <p>
     * <b>Combining Options</b><br>
     * In the following examples, the shorthand form {@link #on} is used rather than the more verbose
     * addListener.  The two are equivalent.  Using the options argument, it is possible to combine different
     * types of listeners:<br>
     * <br>
     * A delayed, one-time listener that auto stops the event and adds a custom argument (forumId) to the
     * options object. The options object is available as the third parameter in the handler function.<div style="margin: 5px 20px 20px;">
     * Code:<pre><code>
el.on('tap', this.onTap, this, {
    single: true,
    delay: 100,
    stopEvent : true
});</code></pre></p>
     * <p>
     * <b>Attaching multiple handlers in 1 call</b><br>
     * The method also allows for a single argument to be passed which is a config object containing properties
     * which specify multiple handlers.</p>
     * <p>
     * Code:<pre><code>
el.on({
    'tap' : {
        fn: this.onTap,
        scope: this
    },
    'doubletap' : {
        fn: this.onDoubleTap,
        scope: this
    },
    'swipe' : {
        fn: this.onSwipe,
        scope: this
    }
});</code></pre>
     * <p>
     * Or a shorthand syntax:<br>
     * Code:<pre><code></p>
el.on({
    'tap' : this.onTap,
    'doubletap' : this.onDoubleTap,
    'swipe' : this.onSwipe,
    scope: this
});
     * </code></pre></p>
     * <p><b>delegate</b></p>
     * <p>This is a configuration option that you can pass along when registering a handler for
     * an event to assist with event delegation. Event delegation is a technique that is used to
     * reduce memory consumption and prevent exposure to memory-leaks. By registering an event
     * for a container element as opposed to each element within a container. By setting this
     * configuration option to a simple selector, the target element will be filtered to look for
     * a descendant of the target.
     * For example:<pre><code>
// using this markup:
&lt;div id='elId'>
    &lt;p id='p1'>paragraph one&lt;/p>
    &lt;p id='p2' class='clickable'>paragraph two&lt;/p>
    &lt;p id='p3'>paragraph three&lt;/p>
&lt;/div>
// utilize event delegation to registering just one handler on the container element:
el = ExtTouch.get('elId');
el.on(
    'tap',
    function(e,t) {
        // handle click
        console.info(t.id); // 'p2'
    },
    this,
    {
        // filter the target element to be a descendant with the class 'tappable'
        delegate: '.tappable'
    }
);
     * </code></pre></p>
     * @return {ExtTouch.Element} this
     */
    addListener : function(eventName, fn, scope, options){
        ExtTouch.EventManager.on(this.dom,  eventName, fn, scope || this, options);
        return this;
    },

    /**
     * Removes an event handler from this element.  The shorthand version {@link #un} is equivalent.
     * <b>Note</b>: if a <i>scope</i> was explicitly specified when {@link #addListener adding} the
     * listener, the same scope must be specified here.
     * Example:
     * <pre><code>
el.removeListener('tap', this.handlerFn);
// or
el.un('tap', this.handlerFn);
</code></pre>
     * @param {String} eventName The name of the event from which to remove the handler.
     * @param {Function} fn The handler function to remove. <b>This must be a reference to the function passed into the {@link #addListener} call.</b>
     * @param {Object} scope If a scope (<b><code>this</code></b> reference) was specified when the listener was added,
     * then this must refer to the same object.
     * @return {ExtTouch.Element} this
     */
    removeListener : function(eventName, fn, scope) {
        ExtTouch.EventManager.un(this.dom, eventName, fn, scope);
        return this;
    },

    /**
     * Removes all previous added listeners from this element
     * @return {ExtTouch.Element} this
     */
    removeAllListeners : function(){
        ExtTouch.EventManager.removeAll(this.dom);
        return this;
    },

    /**
     * Recursively removes all previous added listeners from this element and its children
     * @return {ExtTouch.Element} this
     */
    purgeAllListeners : function() {
        ExtTouch.EventManager.purgeElement(this, true);
        return this;
    },

    /**
     * <p>Removes this element's dom reference.  Note that event and cache removal is handled at {@link ExtTouch#removeNode}</p>
     */
    remove : function() {
        var me = this,
            dom = me.dom;

        if (dom) {
            delete me.dom;
            ExtTouch.removeNode(dom);
        }
    },

    isAncestor : function(c) {
        var p = this.dom;
        c = ExtTouch.getDom(c);
        if (p && c) {
            return p.contains(c);
        }
        return false;
    },

    /**
     * Determines if this element is a descendent of the passed in Element.
     * @param {Mixed} element An ExtTouch.Element, HTMLElement or string linking to an id of an Element.
     * @returns {Boolean}
     */
    isDescendent : function(p) {
        return ExtTouch.fly(p, '_internal').isAncestor(this);
    },

    /**
     * Returns true if this element is an ancestor of the passed element
     * @param {HTMLElement/String} el The element to check
     * @return {Boolean} True if this element is an ancestor of el, else false
     */
    contains : function(el) {
        return !el ? false : this.isAncestor(el);
    },

    /**
     * Returns the value of an attribute from the element's underlying DOM node.
     * @param {String} name The attribute name
     * @param {String} namespace (optional) The namespace in which to look for the attribute
     * @return {String} The attribute value
     */
    getAttribute : function(name, ns) {
        var d = this.dom;
        return d.getAttributeNS(ns, name) || d.getAttribute(ns + ":" + name) || d.getAttribute(name) || d[name];
    },

    /**
    * Set the innerHTML of this element
    * @param {String} html The new HTML
    * @return {ExtTouch.Element} this
     */
    setHTML : function(html) {
        if(this.dom) {
            this.dom.innerHTML = html;
        }
        return this;
    },

    /**
     * Returns the innerHTML of an Element or an empty string if the element's
     * dom no longer exists.
     */
    getHTML : function() {
        return this.dom ? this.dom.innerHTML : '';
    },

    /**
     * Hide this element - Uses display mode to determine whether to use "display" or "visibility". See {@link #setVisible}.
     * @param {Boolean/Object} animate (optional) true for the default animation or a standard Element animation config object
     * @return {ExtTouch.Element} this
     */
    hide : function() {
        this.setVisible(false);
        return this;
    },

    /**
    * Show this element - Uses display mode to determine whether to use "display" or "visibility". See {@link #setVisible}.
    * @param {Boolean/Object} animate (optional) true for the default animation or a standard Element animation config object
     * @return {ExtTouch.Element} this
     */
    show : function() {
        this.setVisible(true);
        return this;
    },

    /**
     * Sets the visibility of the element (see details). If the visibilityMode is set to Element.DISPLAY, it will use
     * the display property to hide the element, otherwise it uses visibility. The default is to hide and show using the visibility property.
     * @param {Boolean} visible Whether the element is visible
     * @param {Boolean/Object} animate (optional) True for the default animation, or a standard Element animation config object
     * @return {ExtTouch.Element} this
     */
     setVisible : function(visible, animate) {
        var me = this,
            dom = me.dom,
            mode = this.getVisibilityMode();

        switch (mode) {
            case El.VISIBILITY:
                this.removeCls(['x-hidden-display', 'x-hidden-offsets']);
                this[visible ? 'removeCls' : 'addCls']('x-hidden-visibility');
            break;

            case El.DISPLAY:
                this.removeCls(['x-hidden-visibility', 'x-hidden-offsets']);
                this[visible ? 'removeCls' : 'addCls']('x-hidden-display');
            break;

            case El.OFFSETS:
                this.removeCls(['x-hidden-visibility', 'x-hidden-display']);
                this[visible ? 'removeCls' : 'addCls']('x-hidden-offsets');
            break;
        }

        return me;
    },

    getVisibilityMode: function() {
        var dom = this.dom,
            mode = El.data(dom, 'visibilityMode');

        if (mode === undefined) {
            El.data(dom, 'visibilityMode', mode = El.DISPLAY);
        }

        return mode;
    },

    setVisibilityMode : function(mode) {
        El.data(this.dom, 'visibilityMode', mode);
        return this;
    }
});

var Elp = El.prototype;

/**
 * Visibility mode constant for use with {@link #setVisibilityMode}. Use visibility to hide element
 * @static
 * @type Number
 */
El.VISIBILITY = 1;
/**
 * Visibility mode constant for use with {@link #setVisibilityMode}. Use display to hide element
 * @static
 * @type Number
 */
El.DISPLAY = 2;
/**
 * Visibility mode constant for use with {@link #setVisibilityMode}. Use offsets to hide element
 * @static
 * @type Number
 */
El.OFFSETS = 3;


El.addMethods = function(o){
   ExtTouch.apply(Elp, o);
};


Elp.on = Elp.addListener;
Elp.un = Elp.removeListener;

// Alias for people used to ExtTouch JS and ExtTouch Core
Elp.update = Elp.setHTML;

/**
 * Retrieves ExtTouch.Element objects.
 * <p><b>This method does not retrieve {@link ExtTouch.Component Component}s.</b> This method
 * retrieves ExtTouch.Element objects which encapsulate DOM elements. To retrieve a Component by
 * its ID, use {@link ExtTouch.ComponentMgr#get}.</p>
 * <p>Uses simple caching to consistently return the same object. Automatically fixes if an
 * object was recreated with the same id via AJAX or DOM.</p>
 * @param {Mixed} el The id of the node, a DOM Node or an existing Element.
 * @return {Element} The Element object (or null if no matching element was found)
 * @static
 * @member ExtTouch.Element
 * @method get
 */
El.get = function(el){
    var ExtTouchEl,
        dom,
        id;

    if(!el){
        return null;
    }

    if (typeof el == "string") { // element id
        if (!(dom = document.getElementById(el))) {
            return null;
        }
        if (ExtTouch.cache[el] && ExtTouch.cache[el].el) {
            ExtTouchEl = ExtTouch.cache[el].el;
            ExtTouchEl.dom = dom;
        } else {
            ExtTouchEl = El.addToCache(new El(dom));
        }
        return ExtTouchEl;
    } else if (el.tagName) { // dom element
        if(!(id = el.id)){
            id = ExtTouch.id(el);
        }
        if (ExtTouch.cache[id] && ExtTouch.cache[id].el) {
            ExtTouchEl = ExtTouch.cache[id].el;
            ExtTouchEl.dom = el;
        } else {
            ExtTouchEl = El.addToCache(new El(el));
        }
        return ExtTouchEl;
    } else if (el instanceof El) {
        if(el != El.docEl){
            // refresh dom element in case no longer valid,
            // catch case where it hasn't been appended
            el.dom = document.getElementById(el.id) || el.dom;
        }
        return el;
    } else if(el.isComposite) {
        return el;
    } else if(ExtTouch.isArray(el)) {
        return El.select(el);
    } else if(el == document) {
        // create a bogus element object representing the document object
        if(!El.docEl){
            var F = function(){};
            F.prototype = Elp;
            El.docEl = new F();
            El.docEl.dom = document;
            El.docEl.id = ExtTouch.id(document);
        }
        return El.docEl;
    }
    return null;
};

// private
El.addToCache = function(el, id){
    id = id || el.id;
    ExtTouch.cache[id] = {
        el:  el,
        data: {},
        events: {}
    };
    return el;
};

// private method for getting and setting element data
El.data = function(el, key, value) {
    el = El.get(el);
    if (!el) {
        return null;
    }
    var c = ExtTouch.cache[el.id].data;
    if (arguments.length == 2) {
        return c[key];
    }
    else {
        return (c[key] = value);
    }
};

// private
// Garbage collection - uncache elements/purge listeners on orphaned elements
// so we don't hold a reference and cause the browser to retain them
El.garbageCollect = function() {
    if (!ExtTouch.enableGarbageCollector) {
        clearInterval(El.collectorThreadId);
    }
    else {
        var id,
            dom,
            EC = ExtTouch.cache;

        for (id in EC) {
            if (!EC.hasOwnProperty(id)) {
                continue;
            }
            if(EC[id].skipGarbageCollection){
                continue;
            }
            dom = EC[id].el.dom;
            if(!dom || !dom.parentNode || (!dom.offsetParent && !document.getElementById(id))){
                if(ExtTouch.enableListenerCollection){
                    ExtTouch.EventManager.removeAll(dom);
                }
                delete EC[id];
            }
        }
    }
};
//El.collectorThreadId = setInterval(El.garbageCollect, 20000);

// dom is optional
El.Flyweight = function(dom) {
    this.dom = dom;
};

var F = function(){};
F.prototype = Elp;

El.Flyweight.prototype = new F;
El.Flyweight.prototype.isFlyweight = true;

El._flyweights = {};

/**
 * <p>Gets the globally shared flyweight Element, with the passed node as the active element. Do not store a reference to this element -
 * the dom node can be overwritten by other code. Shorthand of {@link ExtTouch.Element#fly}</p>
 * <p>Use this to make one-time references to DOM elements which are not going to be accessed again either by
 * application code, or by ExtTouch's classes. If accessing an element which will be processed regularly, then {@link ExtTouch#get}
 * will be more appropriate to take advantage of the caching provided by the ExtTouch.Element class.</p>
 * @param {String/HTMLElement} el The dom node or id
 * @param {String} named (optional) Allows for creation of named reusable flyweights to prevent conflicts
 * (e.g. internally ExtTouch uses "_global")
 * @return {Element} The shared Element object (or null if no matching element was found)
 * @member ExtTouch.Element
 * @method fly
 */
El.fly = function(el, named) {
    var ret = null;
    named = named || '_global';

    el = ExtTouch.getDom(el);
    if (el) {
        (El._flyweights[named] = El._flyweights[named] || new El.Flyweight()).dom = el;
        ret = El._flyweights[named];
    }

    return ret;
};

/**
 * Retrieves ExtTouch.Element objects.
 * <p><b>This method does not retrieve {@link ExtTouch.Component Component}s.</b> This method
 * retrieves ExtTouch.Element objects which encapsulate DOM elements. To retrieve a Component by
 * its ID, use {@link ExtTouch.ComponentMgr#get}.</p>
 * <p>Uses simple caching to consistently return the same object. Automatically fixes if an
 * object was recreated with the same id via AJAX or DOM.</p>
 * Shorthand of {@link ExtTouch.Element#get}
 * @param {Mixed} el The id of the node, a DOM Node or an existing Element.
 * @return {Element} The Element object (or null if no matching element was found)
 * @member ExtTouch
 * @method get
 */
ExtTouch.get = El.get;

/**
 * <p>Gets the globally shared flyweight Element, with the passed node as the active element. Do not store a reference to this element -
 * the dom node can be overwritten by other code. Shorthand of {@link ExtTouch.Element#fly}</p>
 * <p>Use this to make one-time references to DOM elements which are not going to be accessed again either by
 * application code, or by ExtTouch's classes. If accessing an element which will be processed regularly, then {@link ExtTouch#get}
 * will be more appropriate to take advantage of the caching provided by the ExtTouch.Element class.</p>
 * @param {String/HTMLElement} el The dom node or id
 * @param {String} named (optional) Allows for creation of named reusable flyweights to prevent conflicts
 * (e.g. internally ExtTouch uses "_global")
 * @return {Element} The shared Element object (or null if no matching element was found)
 * @member ExtTouch
 * @method fly
 */
ExtTouch.fly = El.fly;

/*ExtTouch.EventManager.on(window, 'unload', function(){
    delete ExtTouch.cache;
    delete El._flyweights;
});*/

})(); 

(function() {
    /**
     * @class ExtTouch.Element
     */
    ExtTouch.Element.classReCache = {};
    var El = ExtTouch.Element,
        view = document.defaultView;

    El.addMethods({
        marginRightRe: /marginRight/i,
        trimRe: /^\s+|\s+$/g,
        spacesRe: /\s+/,

        getStyle: function(prop) {

        },


    });
})();

/**
 * @class ExtTouch.is
 * 
 * Determines information about the current platform the application is running on.
 * 
 * @singleton
 */
ExtTouch.is = {

    init: function(navigator) {
        var me = this,
            platforms = me.platforms,
            ln = platforms.length,
            i, platform;

        navigator = navigator || window.navigator;

        for (i = 0; i < ln; i++) {
            platform = platforms[i];
            me[platform.identity] = platform.regex.test(navigator[platform.property]);
        }

        /**
         * @property Desktop True if the browser is running on a desktop machine
         * @type {Boolean}
         */
        me.Desktop = me.Mac || me.Windows || (me.Linux && !me.Android);
        /**
         * @property iOS True if the browser is running on iOS
         * @type {Boolean}
         */
        me.iOS = me.iPhone || me.iPad || me.iPod;

        /**
         * @property Standalone Detects when application has been saved to homescreen.
         * @type {Boolean}
         */
        me.Standalone = !!navigator.standalone;

        /**
         * @property androidVersion Returns Android OS version information.
         * @type {Boolean}
         */
        i = me.Android && (/Android\s(\d+\.\d+)/.exec(navigator.userAgent));
        if (i) {
            me.AndroidVersion = i[1];
            me.AndroidMajorVersion = parseInt(i[1], 10);
        }
        /**
         * @property Tablet True if the browser is running on a tablet (iPad)
         */
        me.Tablet = me.iPad || (me.Android && me.AndroidMajorVersion === 3);

        /**
         * @property Phone True if the browser is running on a phone.
         * @type {Boolean}
         */
        me.Phone = !me.Desktop && !me.Tablet;

        /**
         * @property MultiTouch Returns multitouch availability.
         * @type {Boolean}
         */
        me.MultiTouch = !me.Blackberry && !me.Desktop && !(me.Android && me.AndroidVersion < 3);
    },

    /**
     * @property iPhone True when the browser is running on a iPhone
     * @type {Boolean}
     */
    platforms: [{
        property: 'platform',
        regex: /iPhone/i,
        identity: 'iPhone'
    },

    /**
     * @property iPod True when the browser is running on a iPod
     * @type {Boolean}
     */
    {
        property: 'platform',
        regex: /iPod/i,
        identity: 'iPod'
    },

    /**
     * @property iPad True when the browser is running on a iPad
     * @type {Boolean}
     */
    {
        property: 'userAgent',
        regex: /iPad/i,
        identity: 'iPad'
    },

    /**
     * @property Blackberry True when the browser is running on a Blackberry
     * @type {Boolean}
     */
    {
        property: 'userAgent',
        regex: /Blackberry/i,
        identity: 'Blackberry'
    },

    /**
     * @property Android True when the browser is running on an Android device
     * @type {Boolean}
     */
    {
        property: 'userAgent',
        regex: /Android/i,
        identity: 'Android'
    },

    /**
     * @property Mac True when the browser is running on a Mac
     * @type {Boolean}
     */
    {
        property: 'platform',
        regex: /Mac/i,
        identity: 'Mac'
    },

    /**
     * @property Windows True when the browser is running on Windows
     * @type {Boolean}
     */
    {
        property: 'platform',
        regex: /Win/i,
        identity: 'Windows'
    },

    /**
     * @property Linux True when the browser is running on Linux
     * @type {Boolean}
     */
    {
        property: 'platform',
        regex: /Linux/i,
        identity: 'Linux'
    }]
};

ExtTouch.is.init();

/**
 * @class ExtTouch.supports
 *
 * Determines information about features are supported in the current environment
 * 
 * @singleton
 */
ExtTouch.supports = {
    init: function() {
        var doc = document,
            div = doc.createElement('div'),
            tests = this.tests,
            ln = tests.length,
            i, test;

        div.innerHTML = ['<div style="height:30px;width:50px;">', '<div style="height:20px;width:20px;"></div>', '</div>', '<div style="float:left; background-color:transparent;"></div>'].join('');

        doc.body.appendChild(div);

        for (i = 0; i < ln; i++) {
            test = tests[i];
            this[test.identity] = test.fn.call(this, doc, div);
        }

        doc.body.removeChild(div);
    },

    /**
     * @property OrientationChange True if the device supports orientation change
     * @type {Boolean}
     */
    OrientationChange: ((typeof window.orientation != 'undefined') && ('onorientationchange' in window)),

    /**
     * @property DeviceMotion True if the device supports device motion (acceleration and rotation rate)
     * @type {Boolean}
     */
    DeviceMotion: ('ondevicemotion' in window),

    /**
     * @property Touch True if the device supports touch
     * @type {Boolean}
     */
    // is.Desktop is needed due to the bug in Chrome 5.0.375, Safari 3.1.2
    // and Safari 4.0 (they all have 'ontouchstart' in the window object).
    Touch: ('ontouchstart' in window) && (!ExtTouch.is.Desktop),

    tests: [
    /**
     * @property Transitions True if the device supports CSS3 Transitions
     * @type {Boolean}
     */
    {
        identity: 'Transitions',
        fn: function(doc, div) {
            var prefix = ['webkit', 'Moz', 'o', 'ms', 'khtml'],
                TE = 'TransitionEnd',
                transitionEndName = [
            prefix[0] + TE, 'transitionend', //Moz bucks the prefixing convention
            prefix[2] + TE, prefix[3] + TE, prefix[4] + TE],
                ln = prefix.length,
                i = 0,
                out = false;
            div = ExtTouch.get(div);
            for (; i < ln; i++) {
                if (div.getStyle(prefix[i] + "TransitionProperty")) {
                    ExtTouch.supports.CSS3Prefix = prefix[i];
                    ExtTouch.supports.CSS3TransitionEnd = transitionEndName[i];
                    out = true;
                    break;
                }
            }
            return out;
        }
    },

    /**
     * @property RightMargin True if the device supports right margin
     * @type {Boolean}
     */
    {
        identity: 'RightMargin',
        fn: function(doc, div, view) {
            view = doc.defaultView;
            return ! (view && view.getComputedStyle(div.firstChild.firstChild, null).marginRight != '0px');
        }
    },

    /**
     * @property TransparentColor True if the device supports transparent color
     * @type {Boolean}
     */
    {
        identity: 'TransparentColor',
        fn: function(doc, div, view) {
            view = doc.defaultView;
            return ! (view && view.getComputedStyle(div.lastChild, null).backgroundColor != 'transparent');
        }
    },

    /**
     * @property SVG True if the device supports SVG
     * @type {Boolean}
     */
    {
        identity: 'SVG',
        fn: function(doc) {
            return !!doc.createElementNS && !!doc.createElementNS("http:/" + "/www.w3.org/2000/svg", "svg").createSVGRect;
        }
    },

    /**
     * @property Canvas True if the device supports Canvas
     * @type {Boolean}
     */
    {
        identity: 'Canvas',
        fn: function(doc) {
            return !!doc.createElement('canvas').getContExtTouch;
        }
    },

    /**
     * @property VML True if the device supports VML
     * @type {Boolean}
     */
    {
        identity: 'VML',
        fn: function(doc) {
            var d = doc.createElement("div");
            d.innerHTML = "<!--[if vml]><br><br><![endif]-->";
            return (d.childNodes.length == 2);
        }
    },

    /**
     * @property Float True if the device supports CSS float
     * @type {Boolean}
     */
    {
        identity: 'Float',
        fn: function(doc, div) {
            return !!div.lastChild.style.cssFloat;
        }
    },

    /**
     * @property AudioTag True if the device supports the HTML5 audio tag
     * @type {Boolean}
     */
    {
        identity: 'AudioTag',
        fn: function(doc) {
            return !!doc.createElement('audio').canPlayType;
        }
    },

    /**
     * @property History True if the device supports HTML5 history
     * @type {Boolean}
     */
    {
        identity: 'History',
        fn: function() {
            return !! (window.history && history.pushState);
        }
    },

    /**
     * @property CSS3DTransform True if the device supports CSS3DTransform
     * @type {Boolean}
     */
    {
        identity: 'CSS3DTransform',
        fn: function() {
            return (typeof WebKitCSSMatrix != 'undefined' && new WebKitCSSMatrix().hasOwnProperty('m41'));
        }
    },

    /**
     * @property CSS3LinearGradient True if the device supports CSS3 linear gradients
     * @type {Boolean}
     */
    {
        identity: 'CSS3LinearGradient',
        fn: function(doc, div) {
            var property = 'background-image:',
                webkit = '-webkit-gradient(linear, left top, right bottom, from(black), to(white))',
                w3c = 'linear-gradient(left top, black, white)',
                moz = '-moz-' + w3c,
                options = [property + webkit, property + w3c, property + moz];

            div.style.cssTExtTouch = options.join(';');

            return ("" + div.style.backgroundImage).indexOf('gradient') !== -1;
        }
    },

    /**
     * @property CSS3BorderRadius True if the device supports CSS3 border radius
     * @type {Boolean}
     */
    {
        identity: 'CSS3BorderRadius',
        fn: function(doc, div) {
            var domPrefixes = ['borderRadius', 'BorderRadius', 'MozBorderRadius', 'WebkitBorderRadius', 'OBorderRadius', 'KhtmlBorderRadius'],
                pass = false,
                i;

            for (i = 0; i < domPrefixes.length; i++) {
                if (document.body.style[domPrefixes[i]] !== undefined) {
                    return pass = true;
                }
            }

            return pass;
        }
    },

    /**
     * @property GeoLocation True if the device supports GeoLocation
     * @type {Boolean}
     */
    {
        identity: 'GeoLocation',
        fn: function() {
            return (typeof navigator != 'undefined' && typeof navigator.geolocation != 'undefined') || (typeof google != 'undefined' && typeof google.gears != 'undefined');
        }
    }]
}; 

/**
 * @class ExtTouch
 */
ExtTouch.apply(ExtTouch, {
    /**
     * The version of the framework
     * @type String
     */
    version : '1.1.1',
    versionDetail : {
        major : 1,
        minor : 1,
        patch : 1
    },
    
    /**
     * Sets up a page for use on a mobile device.
     * @param {Object} config
     *
     * Valid configurations are:
     * <ul>
     *  <li>fullscreen - Boolean - Sets an appropriate meta tag for Apple devices to run in full-screen mode.</li>
     *  <li>tabletStartupScreen - String - Startup screen to be used on an iPad. The image must be 768x1004 and in portrait orientation.</li>
     *  <li>phoneStartupScreen - String - Startup screen to be used on an iPhone or iPod touch. The image must be 320x460 and in 
     *  portrait orientation.</li>
     *  <li>icon - Default icon to use. This will automatically apply to both tablets and phones. These should be 72x72.</li>
     *  <li>tabletIcon - String - An icon for only tablets. (This config supersedes icon.) These should be 72x72.</li>
     *  <li>phoneIcon - String - An icon for only phones. (This config supersedes icon.) These should be 57x57.</li>
     *  <li>glossOnIcon - Boolean - Add gloss on icon on iPhone, iPad and iPod Touch</li>
     *  <li>statusBarStyle - String - Sets the status bar style for fullscreen iPhone OS web apps. Valid options are default, black, 
     *  or black-translucent.</li>
     *  <li>onReady - Function - Function to be run when the DOM is ready.<li>
     *  <li>scope - Scope - Scope for the onReady configuraiton to be run in.</li>
     * </ul>
     */
    setup: function(config) {
        if (config && typeof config == 'object') {
            if (config.addMetaTags !== false) {
                this.addMetaTags(config);
            }

            if (ExtTouch.isFunction(config.onReady)) {
                var me = this;

                ExtTouch.onReady(function() {
                    var args = arguments;

                    if (config.fullscreen !== false) {
                        ExtTouch.Viewport.init(function() {
                            config.onReady.apply(me, args);
                        });
                    }
                    else {
                        config.onReady.apply(this, args);
                    }
                }, config.scope);
            }
        }
    },
    
     /**
      * Return the dom node for the passed String (id), dom node, or ExtTouch.Element.
      * Here are some examples:
      * <pre><code>
// gets dom node based on id
var elDom = ExtTouch.getDom('elId');
// gets dom node based on the dom node
var elDom1 = ExtTouch.getDom(elDom);

// If we don&#39;t know if we are working with an
// ExtTouch.Element or a dom node use ExtTouch.getDom
function(el){
 var dom = ExtTouch.getDom(el);
 // do something with the dom node
}
       </code></pre>
     * <b>Note</b>: the dom node to be found actually needs to exist (be rendered, etc)
     * when this method is called to be successful.
     * @param {Mixed} el
     * @return HTMLElement
     */
    getDom : function(el) {
        if (!el || !document) {
            return null;
        }

        return el.dom ? el.dom : (typeof el == 'string' ? document.getElementById(el) : el);
    },
    
    /**
     * <p>Removes this element from the document, removes all DOM event listeners, and deletes the cache reference.
     * All DOM event listeners are removed from this element. If {@link ExtTouch#enableNestedListenerRemoval} is
     * <code>true</code>, then DOM event listeners are also removed from all child nodes. The body node
     * will be ignored if passed in.</p>
     * @param {HTMLElement} node The node to remove
     */
    removeNode : function(node) {
        if (node && node.parentNode && node.tagName != 'BODY') {
            ExtTouch.EventManager.removeAll(node);
            node.parentNode.removeChild(node);
            delete ExtTouch.cache[node.id];
        }
    },
    
    /**
     * @private
     * Creates meta tags for a given config object. This is usually just called internally from ExtTouch.setup - see
     * that method for full usage. ExtTouchracted into its own function so that ExtTouch.Application and other classes can
     * call it without invoking all of the logic inside ExtTouch.setup.
     * @param {Object} config The meta tag configuration object
     */
    addMetaTags: function(config) {
        if (!ExtTouch.isObject(config)) {
            return;
        }
        
        var head = ExtTouch.get(document.getElementsByTagName('head')[0]),
            tag, precomposed;

        /*
         * The viewport meta tag. This disables user scaling. This is supported
         * on most Android phones and all iOS devices and will probably be supported
         * on most future devices (like Blackberry, Palm etc).
         */
        if (!ExtTouch.is.Desktop) {
            tag = ExtTouch.get(document.createElement('meta'));
            tag.set({
                name: 'viewport',
                content: 'width=device-width, user-scalable=no, initial-scale=1.0, maximum-scale=1.0;'
            });
            head.appendChild(tag);                    
        }
        
        /*
         * We want to check now for iOS specific meta tags. Unfortunately most
         * of these are not supported on devices other then iOS.
         */
        if (ExtTouch.is.iOS) {
            /*
             * On iOS, if you save to home screen, you can decide if you want
             * to launch the app fullscreen (without address bar). You can also
             * change the styling of the status bar at the top of the screen.
             */                
            if (config.fullscreen !== false) {
                tag = ExtTouch.get(document.createElement('meta'));
                tag.set({
                    name: 'apple-mobile-web-app-capable',
                    content: 'yes'
                });
                head.appendChild(tag);

                if (ExtTouch.isString(config.statusBarStyle)) {
                    tag = ExtTouch.get(document.createElement('meta'));
                    tag.set({
                        name: 'apple-mobile-web-app-status-bar-style',
                        content: config.statusBarStyle
                    });
                    head.appendChild(tag);
                }
            }
            
            /*
             * iOS allows you to specify a startup screen. This is displayed during
             * the startup of your app if you save to your homescreen. Since we could
             * be dealing with an iPad or iPhone/iPod, we have a tablet startup screen
             * and a phone startup screen.
             */
            if (config.tabletStartupScreen && ExtTouch.is.iPad) {
                tag = ExtTouch.get(document.createElement('link'));
                tag.set({
                    rel: 'apple-touch-startup-image',
                    href: config.tabletStartupScreen
                }); 
                head.appendChild(tag);                  
            }
            
            if (config.phoneStartupScreen && !ExtTouch.is.iPad) {
                tag = ExtTouch.get(document.createElement('link'));
                tag.set({
                    rel: 'apple-touch-startup-image',
                    href: config.phoneStartupScreen
                });
                head.appendChild(tag);
            }
            
            /*
             * On iOS you can specify the icon used when you save the app to your
             * homescreen. You can set an icon that will be used for both iPads
             * and iPhone/iPod, or you can specify specific icons for both.
             */
            if (config.icon) {
                config.phoneIcon = config.tabletIcon = config.icon;
            }
            
            precomposed = (config.glossOnIcon === false) ? '-precomposed' : '';
            if (ExtTouch.is.iPad && ExtTouch.isString(config.tabletIcon)) {
                tag = ExtTouch.get(document.createElement('link'));
                tag.set({
                    rel: 'apple-touch-icon' + precomposed,
                    href: config.tabletIcon
                });
                head.appendChild(tag);
            } 
            else if (!ExtTouch.is.iPad && ExtTouch.isString(config.phoneIcon)) {
                tag = ExtTouch.get(document.createElement('link'));
                tag.set({
                    rel: 'apple-touch-icon' + precomposed,
                    href: config.phoneIcon
                });
                head.appendChild(tag);
            }
        }
    }
});

//Initialize doc classes and feature detections
(function() {
    var initExtTouch = function() {
        // find the body element
        var bd = ExtTouch.getBody(),
            cls = [];
        if (!bd) {
            return false;
        }
        var Is = ExtTouch.is; 
        if (Is.Phone) {
            cls.push('x-phone');
        }
        else if (Is.Tablet) {
            cls.push('x-tablet');
        }
        else if (Is.Desktop) {
            cls.push('x-desktop');
        }
        if (Is.iPad) {
            cls.push('x-ipad');
        }
        if (Is.iOS) {
            cls.push('x-ios');
        }
        if (Is.Android) {
            cls.push('x-android', 'x-android-' + Is.AndroidMajorVersion);
        }
        if (Is.Blackberry) {
            cls.push('x-bb');
        }
        if (Is.Standalone) {
            cls.push('x-standalone');
        }
        if (cls.length) {
            bd.addCls(cls);
        }
        return true;
    };

    if (!initExtTouch()) {
        ExtTouch.onReady(initExtTouch);
    }
})(); 

/**
 * @class ExtTouch.util.Observable
 * Base class that provides a common interface for publishing events. Subclasses are expected to
 * to have a property "events" with all the events defined, and, optionally, a property "listeners"
 * with configured listeners defined.<br>
 * For example:
 * <pre><code>
Employee = ExtTouch.ExtTouchend(ExtTouch.util.Observable, {
    constructor: function(config){
        this.name = config.name;
        this.addEvents({
            "fired" : true,
            "quit" : true
        });

        // Copy configured listeners into *this* object so that the base class&#39;s
        // constructor will add them.
        this.listeners = config.listeners;

        // Call our superclass constructor to complete construction process.
        Employee.superclass.constructor.call(this, config)
    }
});
</code></pre>
 * This could then be used like this:<pre><code>
var newEmployee = new Employee({
    name: employeeName,
    listeners: {
        quit: function() {
            // By default, "this" will be the object that fired the event.
            alert(this.name + " has quit!");
        }
    }
});
</code></pre>
 */

ExtTouch.util.Observable = ExtTouch.ExtTouchend(Object, {
    /**
    * @cfg {Object} listeners (optional) <p>A config object containing one or more event handlers to be added to this
    * object during initialization.  This should be a valid listeners config object as specified in the
    * {@link #addListener} example for attaching multiple handlers at once.</p>
    * <br><p><b><u>DOM events from ExtTouchJs {@link ExtTouch.Component Components}</u></b></p>
    * <br><p>While <i>some</i> ExtTouchJs Component classes export selected DOM events (e.g. "click", "mouseover" etc), this
    * is usually only done when ExtTouchra value can be added. For example the {@link ExtTouch.DataView DataView}'s
    * <b><code>{@link ExtTouch.DataView#click click}</code></b> event passing the node clicked on. To access DOM
    * events directly from a child element of a Component, we need to specify the <code>element</code> option to
    * identify the Component property to add a DOM listener to:
    * <pre><code>
new ExtTouch.Panel({
    width: 400,
    height: 200,
    dockedItems: [{
        xtype: 'toolbar'
    }],
    listeners: {
        click: {
            element: 'el', //bind to the underlying el property on the panel
            fn: function(){ console.log('click el'); }
        },
        dblclick: {
            element: 'body', //bind to the underlying body property on the panel
            fn: function(){ console.log('dblclick body'); }
        }
    }
});
</code></pre>
    * </p>
    */
    // @private
    isObservable: true,

    constructor: function(config) {
        var me = this;

        ExtTouch.apply(me, config);
        if (me.listeners) {
            me.on(me.listeners);
            delete me.listeners;
        }
        me.events = me.events || {};

        if (this.bubbleEvents) {
            this.enableBubble(this.bubbleEvents);
        }
    },

    // @private
    eventOptionsRe : /^(?:scope|delay|buffer|single|stopEvent|preventDefault|stopPropagation|normalized|args|delegate|element|vertical|horizontal)$/,

    /**
     * <p>Adds listeners to any Observable object (or Element) which are automatically removed when this Component
     * is destroyed.
     * @param {Observable|Element} item The item to which to add a listener/listeners.
     * @param {Object|String} ename The event name, or an object containing event name properties.
     * @param {Function} fn Optional. If the <code>ename</code> parameter was an event name, this
     * is the handler function.
     * @param {Object} scope Optional. If the <code>ename</code> parameter was an event name, this
     * is the scope (<code>this</code> reference) in which the handler function is executed.
     * @param {Object} opt Optional. If the <code>ename</code> parameter was an event name, this
     * is the {@link ExtTouch.util.Observable#addListener addListener} options.
     */
    addManagedListener : function(item, ename, fn, scope, options) {
        var me = this,
            managedListeners = me.managedListeners = me.managedListeners || [],
            config;

        if (ExtTouch.isObject(ename)) {
            options = ename;
            for (ename in options) {
                if (!options.hasOwnProperty(ename)) {
                    continue;
                }
                config = options[ename];
                if (!me.eventOptionsRe.test(ename)) {
                    me.addManagedListener(item, ename, config.fn || config, config.scope || options.scope, config.fn ? config : options);
                }
            }
        }
        else {
            managedListeners.push({
                item: item,
                ename: ename,
                fn: fn,
                scope: scope,
                options: options
            });

            item.on(ename, fn, scope, options);
        }
    },

    /**
     * Removes listeners that were added by the {@link #mon} method.
     * @param {Observable|Element} item The item from which to remove a listener/listeners.
     * @param {Object|String} ename The event name, or an object containing event name properties.
     * @param {Function} fn Optional. If the <code>ename</code> parameter was an event name, this
     * is the handler function.
     * @param {Object} scope Optional. If the <code>ename</code> parameter was an event name, this
     * is the scope (<code>this</code> reference) in which the handler function is executed.
     */
     removeManagedListener : function(item, ename, fn, scope) {
        var me = this,
            o,
            config,
            managedListeners,
            managedListener,
            length,
            i;

        if (ExtTouch.isObject(ename)) {
            o = ename;
            for (ename in o) {
                if (!o.hasOwnProperty(ename)) {
                    continue;
                }
                config = o[ename];
                if (!me.eventOptionsRe.test(ename)) {
                    me.removeManagedListener(item, ename, config.fn || config, config.scope || o.scope);
                }
            }
        }

        managedListeners = this.managedListeners ? this.managedListeners.slice() : [];
        length = managedListeners.length;

        for (i = 0; i < length; i++) {
            managedListener = managedListeners[i];
            if (managedListener.item === item && managedListener.ename === ename && (!fn || managedListener.fn === fn) && (!scope || managedListener.scope === scope)) {
                this.managedListeners.remove(managedListener);
                item.un(managedListener.ename, managedListener.fn, managedListener.scope);
            }
        }
    },

    /**
     * <p>Fires the specified event with the passed parameters (minus the event name).</p>
     * <p>An event may be set to bubble up an Observable parent hierarchy (See {@link ExtTouch.Component#getBubbleTarget})
     * by calling {@link #enableBubble}.</p>
     * @param {String} eventName The name of the event to fire.
     * @param {Object...} args Variable number of parameters are passed to handlers.
     * @return {Boolean} returns false if any of the handlers return false otherwise it returns true.
     */
    fireEvent: function() {
        var me = this,
            a = ExtTouch.toArray(arguments),
            ename = a[0].toLowerCase(),
            ret = true,
            ev = me.events[ename],
            queue = me.eventQueue,
            parent;

        if (me.eventsSuspended === true) {
            if (queue) {
                queue.push(a);
            }
            return false;
        }
        else if (ev && ExtTouch.isObject(ev) && ev.bubble) {
            if (ev.fire.apply(ev, a.slice(1)) === false) {
                return false;
            }
            parent = me.getBubbleTarget && me.getBubbleTarget();
            if (parent && parent.isObservable) {
                if (!parent.events[ename] || !ExtTouch.isObject(parent.events[ename]) || !parent.events[ename].bubble) {
                    parent.enableBubble(ename);
                }
                return parent.fireEvent.apply(parent, a);
            }
        }
        else if (ev && ExtTouch.isObject(ev)) {
            a.shift();
            ret = ev.fire.apply(ev, a);
        }
        return ret;
    },

    /**
     * Appends an event handler to this object.
     * @param {String}   eventName The name of the event to listen for. May also be an object who's property names are event names. See 
     * @param {Function} handler The method the event invokes.
     * @param {Object}   scope (optional) The scope (<code><b>this</b></code> reference) in which the handler function is executed.
     * <b>If omitted, defaults to the object which fired the event.</b>
     * @param {Object}   options (optional) An object containing handler configuration.
     * properties. This may contain any of the following properties:<ul>
     * <li><b>scope</b> : Object<div class="sub-desc">The scope (<code><b>this</b></code> reference) in which the handler function is executed.
     * <b>If omitted, defaults to the object which fired the event.</b></div></li>
     * <li><b>delay</b> : Number<div class="sub-desc">The number of milliseconds to delay the invocation of the handler after the event fires.</div></li>
     * <li><b>single</b> : Boolean<div class="sub-desc">True to add a handler to handle just the nExtTouch firing of the event, and then remove itself.</div></li>
     * <li><b>buffer</b> : Number<div class="sub-desc">Causes the handler to be scheduled to run in an {@link ExtTouch.util.DelayedTask} delayed
     * by the specified number of milliseconds. If the event fires again within that time, the original
     * handler is <em>not</em> invoked, but the new handler is scheduled in its place.</div></li>
     * <li><b>target</b> : Observable<div class="sub-desc">Only call the handler if the event was fired on the target Observable, <i>not</i>
     * if the event was bubbled up from a child Observable.</div></li>
     * <li><b>element</b> : String<div class="sub-desc"><b>This option is only valid for listeners bound to {@link ExtTouch.Component Components}.</b>
     * The name of a Component property which references an element to add a listener to.
     * <p>This option is useful during Component construction to add DOM event listeners to elements of {@link ExtTouch.Component Components} which
     * will exist only after the Component is rendered. For example, to add a click listener to a Panel's body:<pre><code>
new ExtTouch.Panel({
    title: 'The title',
    listeners: {
        click: this.handlePanelClick,
        element: 'body'
    }
});
</code></pre></p>
     * <p>When added in this way, the options available are the options applicable to {@link ExtTouch.Element#addListener}</p></div></li>
     * </ul><br>
     * <p>
     * <b>Combining Options</b><br>
     * Using the options argument, it is possible to combine different types of listeners:<br>
     * <br>
     * A delayed, one-time listener.
     * <pre><code>
myPanel.on('hide', this.handleClick, this, {
single: true,
delay: 100
});</code></pre>
     * <p>
     * <b>Attaching multiple handlers in 1 call</b><br>
     * The method also allows for a single argument to be passed which is a config object containing properties
     * which specify multiple events. For example:<pre><code>
myGridPanel.on({
    cellClick: this.onCellClick,
    mouseover: this.onMouseOver,
    mouseout: this.onMouseOut,
    scope: this // Important. Ensure "this" is correct during handler execution
});
</code></pre>.
     * <p>
     */
    addListener: function(ename, fn, scope, o) {
        var me = this,
            config,
            ev;

        if (ExtTouch.isObject(ename)) {
            o = ename;
            for (ename in o) {
                if (!o.hasOwnProperty(ename)) {
                    continue;
                }
                config = o[ename];
                if (!me.eventOptionsRe.test(ename)) {
                    me.addListener(ename, config.fn || config, config.scope || o.scope, config.fn ? config : o);
                }
            }
        }
        else {
            ename = ename.toLowerCase();
            me.events[ename] = me.events[ename] || true;
            ev = me.events[ename] || true;
            if (ExtTouch.isBoolean(ev)) {
                me.events[ename] = ev = new ExtTouch.util.Event(me, ename);
            }
            ev.addListener(fn, scope, ExtTouch.isObject(o) ? o: {});
        }
    },

    /**
     * Removes an event handler.
     * @param {String}   eventName The type of event the handler was associated with.
     * @param {Function} handler   The handler to remove. <b>This must be a reference to the function passed into the {@link #addListener} call.</b>
     * @param {Object}   scope     (optional) The scope originally specified for the handler.
     */
    removeListener: function(ename, fn, scope) {
        var me = this,
            config,
            ev;

        if (ExtTouch.isObject(ename)) {
            var o = ename;
            for (ename in o) {
                if (!o.hasOwnProperty(ename)) {
                    continue;
                }
                config = o[ename];
                if (!me.eventOptionsRe.test(ename)) {
                    me.removeListener(ename, config.fn || config, config.scope || o.scope);
                }
            }
        }
        else {
            ename = ename.toLowerCase();
            ev = me.events[ename];
            if (ev.isEvent) {
                ev.removeListener(fn, scope);
            }
        }
    },

    /**
     * Removes all listeners for this object including the managed listeners
     */
    clearListeners: function() {
        var events = this.events,
            ev,
            key;

        for (key in events) {
            if (!events.hasOwnProperty(key)) {
                continue;
            }
            ev = events[key];
            if (ev.isEvent) {
                ev.clearListeners();
            }
        }

        this.clearManagedListeners();
    },

    //<debug>
    purgeListeners : function() {
        console.warn('MixedCollection: purgeListeners has been deprecated. Please use clearListeners.');
        return this.clearListeners.apply(this, arguments);
    },
    //</debug>

    /**
     * Removes all managed listeners for this object.
     */
    clearManagedListeners : function() {
        var managedListeners = this.managedListeners || [],
            ln = managedListeners.length,
            i, managedListener;

        for (i = 0; i < ln; i++) {
            managedListener = managedListeners[i];
            managedListener.item.un(managedListener.ename, managedListener.fn, managedListener.scope);
        }

        this.managedListener = [];
    },

    //<debug>
    purgeManagedListeners : function() {
        console.warn('MixedCollection: purgeManagedListeners has been deprecated. Please use clearManagedListeners.');
        return this.clearManagedListeners.apply(this, arguments);
    },
    //</debug>

    /**
     * Adds the specified events to the list of events which this Observable may fire.
     * @param {Object|String} o Either an object with event names as properties with a value of <code>true</code>
     * or the first event name string if multiple event names are being passed as separate parameters.
     * @param {string} Optional. Event name if multiple event names are being passed as separate parameters.
     * Usage:<pre><code>
this.addEvents('storeloaded', 'storecleared');
</code></pre>
     */
    addEvents: function(o) {
        var me = this;
            me.events = me.events || {};
        if (ExtTouch.isString(o)) {
            var a = arguments,
            i = a.length;
            while (i--) {
                me.events[a[i]] = me.events[a[i]] || true;
            }
        } else {
            ExtTouch.applyIf(me.events, o);
        }
    },

    /**
     * Checks to see if this object has any listeners for a specified event
     * @param {String} eventName The name of the event to check for
     * @return {Boolean} True if the event is being listened for, else false
     */
    hasListener: function(ename) {
        var e = this.events[ename];
        return e.isEvent === true && e.listeners.length > 0;
    },

    /**
     * Suspend the firing of all events. (see {@link #resumeEvents})
     * @param {Boolean} queueSuspended Pass as true to queue up suspended events to be fired
     * after the {@link #resumeEvents} call instead of discarding all suspended events;
     */
    suspendEvents: function(queueSuspended) {
        this.eventsSuspended = true;
        if (queueSuspended && !this.eventQueue) {
            this.eventQueue = [];
        }
    },

    /**
     * Resume firing events. (see {@link #suspendEvents})
     * If events were suspended using the <tt><b>queueSuspended</b></tt> parameter, then all
     * events fired during event suspension will be sent to any listeners now.
     */
    resumeEvents: function() {
        var me = this,
            queued = me.eventQueue || [];

        me.eventsSuspended = false;
        delete me.eventQueue;

        ExtTouch.each(queued,
        function(e) {
            me.fireEvent.apply(me, e);
        });
    },

    /**
     * Relays selected events from the specified Observable as if the events were fired by <tt><b>this</b></tt>.
     * @param {Object} o The Observable whose events this object is to relay.
     * @param {Array} events Array of event names to relay.
     */
    relayEvents : function(origin, events, prefix) {
        prefix = prefix || '';
        var me = this,
            len = events.length,
            i, ename;

        function createHandler(ename){
            return function(){
                return me.fireEvent.apply(me, [prefix + ename].concat(Array.prototype.slice.call(arguments, 0, -1)));
            };
        }

        for(i = 0, len = events.length; i < len; i++){
            ename = events[i].substr(prefix.length);
            me.events[ename] = me.events[ename] || true;
            origin.on(ename, createHandler(ename), me);
        }
    },

    /**
     * <p>Enables events fired by this Observable to bubble up an owner hierarchy by calling
     * <code>this.getBubbleTarget()</code> if present. There is no implementation in the Observable base class.</p>
     * <p>This is commonly used by ExtTouch.Components to bubble events to owner Containers. See {@link ExtTouch.Component.getBubbleTarget}. The default
     * implementation in ExtTouch.Component returns the Component's immediate owner. But if a known target is required, this can be overridden to
     * access the required target more quickly.</p>
     * <p>Example:</p><pre><code>
ExtTouch.override(ExtTouch.form.Field, {
//  Add functionality to Field&#39;s initComponent to enable the change event to bubble
initComponent : ExtTouch.createSequence(ExtTouch.form.Field.prototype.initComponent, function() {
    this.enableBubble('change');
}),

//  We know that we want Field&#39;s events to bubble directly to the FormPanel.
getBubbleTarget : function() {
    if (!this.formPanel) {
        this.formPanel = this.findParentByType('form');
    }
    return this.formPanel;
}
});

var myForm = new ExtTouch.formPanel({
title: 'User Details',
items: [{
    ...
}],
listeners: {
    change: function() {
        // Title goes red if form has been modified.
        myForm.header.setStyle('color', 'red');
    }
}
});
</code></pre>
     * @param {String/Array} events The event name to bubble, or an Array of event names.
     */
    enableBubble: function(events) {
        var me = this;
        if (!ExtTouch.isEmpty(events)) {
            events = ExtTouch.isArray(events) ? events: ExtTouch.toArray(arguments);
            ExtTouch.each(events,
            function(ename) {
                ename = ename.toLowerCase();
                var ce = me.events[ename] || true;
                if (ExtTouch.isBoolean(ce)) {
                    ce = new ExtTouch.util.Event(me, ename);
                    me.events[ename] = ce;
                }
                ce.bubble = true;
            });
        }
    }
});

ExtTouch.override(ExtTouch.util.Observable, {
    /**
     * Appends an event handler to this object (shorthand for {@link #addListener}.)
     * @param {String}   eventName     The type of event to listen for
     * @param {Function} handler       The method the event invokes
     * @param {Object}   scope         (optional) The scope (<code><b>this</b></code> reference) in which the handler function is executed.
     * <b>If omitted, defaults to the object which fired the event.</b>
     * @param {Object}   options       (optional) An object containing handler configuration.
     * @method
     */
    on: ExtTouch.util.Observable.prototype.addListener,
    /**
     * Removes an event handler (shorthand for {@link #removeListener}.)
     * @param {String}   eventName     The type of event the handler was associated with.
     * @param {Function} handler       The handler to remove. <b>This must be a reference to the function passed into the {@link #addListener} call.</b>
     * @param {Object}   scope         (optional) The scope originally specified for the handler.
     * @method
     */
    un: ExtTouch.util.Observable.prototype.removeListener,

    mon: ExtTouch.util.Observable.prototype.addManagedListener,
    mun: ExtTouch.util.Observable.prototype.removeManagedListener
});

/**
 * Removes <b>all</b> added captures from the Observable.
 * @param {Observable} o The Observable to release
 * @static
 */
ExtTouch.util.Observable.releaseCapture = function(o) {
    o.fireEvent = ExtTouch.util.Observable.prototype.fireEvent;
};

/**
 * Starts capture on the specified Observable. All events will be passed
 * to the supplied function with the event name + standard signature of the event
 * <b>before</b> the event is fired. If the supplied function returns false,
 * the event will not fire.
 * @param {Observable} o The Observable to capture events from.
 * @param {Function} fn The function to call when an event is fired.
 * @param {Object} scope (optional) The scope (<code>this</code> reference) in which the function is executed. Defaults to the Observable firing the event.
 * @static
 */
ExtTouch.util.Observable.capture = function(o, fn, scope) {
    o.fireEvent = ExtTouch.createInterceptor(o.fireEvent, fn, scope);
};

/**
 * Sets observability on the passed class constructor.<p>
 * <p>This makes any event fired on any instance of the passed class also fire a single event through
 * the <i>class</i> allowing for central handling of events on many instances at once.</p>
 * <p>Usage:</p><pre><code>
ExtTouch.util.Observable.observe(ExtTouch.data.Connection);
ExtTouch.data.Connection.on('beforerequest', function(con, options) {
    console.log('Ajax request made to ' + options.url);
});</code></pre>
 * @param {Function} c The class constructor to make observable.
 * @param {Object} listeners An object containing a series of listeners to add. See {@link #addListener}.
 * @static
 */
ExtTouch.util.Observable.observe = function(cls, listeners) {
    if (cls) {
        if (!cls.isObservable) {
            ExtTouch.applyIf(cls, new ExtTouch.util.Observable());
            ExtTouch.util.Observable.capture(cls.prototype, cls.fireEvent, cls);
        }
        if (typeof listeners == 'object') {
            cls.on(listeners);
        }
        return cls;
    }
};

//deprecated, will be removed in 5.0
ExtTouch.util.Observable.observeClass = ExtTouch.util.Observable.observe;

ExtTouch.util.Event = ExtTouch.ExtTouchend(Object, (function() {
    function createBuffered(handler, listener, o, scope) {
        listener.task = new ExtTouch.util.DelayedTask();
        return function() {
            listener.task.delay(o.buffer, handler, scope, ExtTouch.toArray(arguments));
        };
    };

    function createDelayed(handler, listener, o, scope) {
        return function() {
            var task = new ExtTouch.util.DelayedTask();
            if (!listener.tasks) {
                listener.tasks = [];
            }
            listener.tasks.push(task);
            task.delay(o.delay || 10, handler, scope, ExtTouch.toArray(arguments));
        };
    };

    function createSingle(handler, listener, o, scope) {
        return function() {
            listener.ev.removeListener(listener.fn, scope);
            return handler.apply(scope, arguments);
        };
    };

    return {
        isEvent: true,

        constructor: function(observable, name) {
            this.name = name;
            this.observable = observable;
            this.listeners = [];
        },

        addListener: function(fn, scope, options) {
            var me = this,
                listener;
                scope = scope || me.observable;

            if (!me.isListening(fn, scope)) {
                listener = me.createListener(fn, scope, options);
                if (me.firing) {
                    // if we are currently firing this event, don't disturb the listener loop
                    me.listeners = me.listeners.slice(0);
                }
                me.listeners.push(listener);
            }
        },

        createListener: function(fn, scope, o) {
            o = o || {};
            scope = scope || this.observable;

            var listener = {
                    fn: fn,
                    scope: scope,
                    o: o,
                    ev: this
                },
                handler = fn;

            if (o.delay) {
                handler = createDelayed(handler, listener, o, scope);
            }
            if (o.buffer) {
                handler = createBuffered(handler, listener, o, scope);
            }
            if (o.single) {
                handler = createSingle(handler, listener, o, scope);
            }

            listener.fireFn = handler;
            return listener;
        },

        findListener: function(fn, scope) {
            var listeners = this.listeners,
            i = listeners.length,
            listener,
            s;

            while (i--) {
                listener = listeners[i];
                if (listener) {
                    s = listener.scope;
                    if (listener.fn == fn && (s == scope || s == this.observable)) {
                        return i;
                    }
                }
            }

            return - 1;
        },

        isListening: function(fn, scope) {
            return this.findListener(fn, scope) !== -1;
        },

        removeListener: function(fn, scope) {
            var me = this,
                index,
                listener,
                k;
            index = me.findListener(fn, scope);
            if (index != -1) {
                listener = me.listeners[index];

                if (me.firing) {
                    me.listeners = me.listeners.slice(0);
                }

                // cancel and remove a buffered handler that hasn't fired yet
                if (listener.task) {
                    listener.task.cancel();
                    delete listener.task;
                }

                // cancel and remove all delayed handlers that haven't fired yet
                k = listener.tasks && listener.tasks.length;
                if (k) {
                    while (k--) {
                        listener.tasks[k].cancel();
                    }
                    delete listener.tasks;
                }

                // remove this listener from the listeners array
                me.listeners.splice(index, 1);
                return true;
            }

            return false;
        },

        // Iterate to stop any buffered/delayed events
        clearListeners: function() {
            var listeners = this.listeners,
                i = listeners.length;

            while (i--) {
                this.removeListener(listeners[i].fn, listeners[i].scope);
            }
        },

        fire: function() {
            var me = this,
                listeners = me.listeners,
                count = listeners.length,
                i,
                args,
                listener;

            if (count > 0) {
                me.firing = true;
                for (i = 0; i < count; i++) {
                    listener = listeners[i];
                    args = arguments.length ? Array.prototype.slice.call(arguments, 0) : [];
                    if (listener.o) {
                        args.push(listener.o);
                    }
                    if (listener && listener.fireFn.apply(listener.scope || me.observable, args) === false) {
                        return (me.firing = false);
                    }
                }
            }
            me.firing = false;
            return true;
        }
    };
})()); 

/**
 * @class ExtTouch.util.HashMap
 * @ExtTouchends ExtTouch.util.Observable
 * <p>A simple unordered dictionary implementation to store key/value pairs.</p>
 * 
 * @cfg {Function} keyFn A function that is used to retrieve a default key for a passed object.
 * A default is provided that returns the <b>id</b> property on the object. This function is only used
 * if the add method is called with a single argument.
 * 
 * @constructor
 * @param {Object} config The configuration options
 */
ExtTouch.util.HashMap = ExtTouch.ExtTouchend(ExtTouch.util.Observable, {
    constructor: function(config) {
        this.addEvents(
            /**
             * @event add
             * Fires when a new item is added to the hash
             * @param {ExtTouch.util.HashMap} this.
             * @param {String} key The key of the added item.
             * @param {Object} value The value of the added item.
             */
            'add',
            /**
             * @event clear
             * Fires when the hash is cleared.
             * @param {ExtTouch.util.HashMap} this.
             */
            'clear',
            /**
             * @event remove
             * Fires when an item is removed from the hash.
             * @param {ExtTouch.util.HashMap} this.
             * @param {String} key The key of the removed item.
             * @param {Object} value The value of the removed item.
             */
            'remove',
            /**
             * @event replace
             * Fires when an item is replaced in the hash.
             * @param {ExtTouch.util.HashMap} this.
             * @param {String} key The key of the replaced item.
             * @param {Object} value The new value for the item.
             * @param {Object} old The old value for the item.
             */
            'replace'
        );
        
        ExtTouch.util.HashMap.superclass.constructor.call(this, config);
        
        this.clear(true);
    },

    /**
     * Gets the number of items in the hash.
     * @return {Number} The number of items in the hash.
     */
    getCount: function() {
        return this.length;
    },
    
    /**
     * Implementation for being able to ExtTouchract the key from an object if only
     * a single argument is passed.
     * @private
     * @param {String} key The key
     * @param {Object} value The value
     * @return {Array} [key, value]
     */
    getData: function(key, value) {
        // if we have no value, it means we need to get the key from the object
        if (value === undefined) {
            value = key;
            key = this.getKey(value);
        }
        
        return [key, value];
    },
    
    /**
     * ExtTouchracts the key from an object. This is a default implementation, it may be overridden
     * @private
     * @param {Object} o The object to get the key from
     * @return {String} The key to use.
     */
    getKey: function(o) {
        return o.id;    
    },

    /**
     * Add a new item to the hash. An exception will be thrown if the key already exists.
     * @param {String} key The key of the new item.
     * @param {Object} value The value of the new item.
     * @return {Object} The value of the new item added.
     */
    add: function(key, value) {
        var me = this,
            data;
            
        if (me.containsKey(key)) {
            throw new Error('This key already exists in the HashMap');
        }
        
        data = this.getData(key, value);
        key = data[0];
        value = data[1];
        me.map[key] = value;
        ++me.length;
        me.fireEvent('add', me, key, value);
        return value;
    },

    /**
     * Replaces an item in the hash. If the key doesn't exist, the
     * {@link #add} method will be used.
     * @param {String} key The key of the item.
     * @param {Object} value The new value for the item.
     * @return {Object} The new value of the item.
     */
    replace: function(key, value) {
        var me = this,
            map = me.map,
            old;
            
        if (!me.containsKey(key)) {
            me.add(key, value);
        }
        old = map[key];
        map[key] = value;
        me.fireEvent('replace', me, key, value, old);
        return value;
    },

    /**
     * Remove an item from the hash.
     * @param {Object} o The value of the item to remove.
     * @return {Boolean} True if the item was successfully removed.
     */
    remove: function(o) {
        var key = this.findKey(o);
        if (key !== undefined) {
            return this.removeByKey(key);
        }
        return false;
    },

    /**
     * Remove an item from the hash.
     * @param {String} key The key to remove.
     * @return {Boolean} True if the item was successfully removed.
     */
    removeByKey: function(key) {
        var me = this,
            value;
            
        if (me.containsKey(key)) {
            value = me.map[key];
            delete me.map[key];
            --me.length;
            me.fireEvent('remove', me, key, value);
            return true;
        }
        return false;
    },

    /**
     * Retrieves an item with a particular key.
     * @param {String} key The key to lookup.
     * @return {Object} The value at that key. If it doesn't exist, <tt>undefined</tt> is returned.
     */
    get: function(key) {
        return this.map[key];
    },

    /**
     * Removes all items from the hash.
     * @return {ExtTouch.util.HashMap} this
     */
    clear: function(/* private */ initial) {
        var me = this;
        me.map = {};
        me.length = 0;
        if (initial !== true) {
            me.fireEvent('clear', me);
        }
        return me;
    },

    /**
     * Checks whether a key exists in the hash.
     * @param {String} key The key to check for.
     * @return {Boolean} True if they key exists in the hash.
     */
    containsKey: function(key) {
        return this.map[key] !== undefined;
    },

    /**
     * Checks whether a value exists in the hash.
     * @param {Object} value The value to check for.
     * @return {Boolean} True if the value exists in the dictionary.
     */
    contains: function(value) {
        return this.containsKey(this.findKey(value));
    },

    /**
     * Return all of the keys in the hash.
     * @return {Array} An array of keys.
     */
    getKeys: function() {
        return this.getArray(true);
    },

    /**
     * Return all of the values in the hash.
     * @return {Array} An array of values.
     */
    getValues: function() {
        return this.getArray(false);
    },

    /**
     * Gets either the keys/values in an array from the hash.
     * @private
     * @param {Boolean} isKey True to ExtTouchract the keys, otherwise, the value
     * @return {Array} An array of either keys/values from the hash.
     */
    getArray: function(isKey) {
        var arr = [],
            key,
            map = this.map;
        for (key in map) {
            if (map.hasOwnProperty(key)) {
                arr.push(isKey ? key: map[key]);
            }
        }
        return arr;
    },

    /**
     * Executes the specified function once for each item in the hash.
     * Returning false from the function will cease iteration.
     * 
     * The paramaters passed to the function are:
     * <div class="mdetail-params"><ul>
     * <li><b>key</b> : String<p class="sub-desc">The key of the item</p></li>
     * <li><b>value</b> : Number<p class="sub-desc">The value of the item</p></li>
     * <li><b>length</b> : Number<p class="sub-desc">The total number of items in the hash</p></li>
     * </ul></div>
     * @param {Function} fn The function to execute.
     * @param {Object} scope The scope to execute in. Defaults to <tt>this</tt>.
     * @return {ExtTouch.util.HashMap} this
     */
    each: function(fn, scope) { 
        // copy items so they may be removed during iteration.
        var items = ExtTouch.apply({}, this.map),
            key,
            length = this.length;

        scope = scope || this;
        for (key in items) {
            if (items.hasOwnProperty(key)) {
                if (fn.call(scope, key, items[key], length) === false) {
                    break;
                }
            }
        }
        return this;
    },

    /**
     * Performs a shallow copy on this hash.
     * @return {ExtTouch.util.HashMap} The new hash object.
     */
    clone: function() {
        var hash = new ExtTouch.util.HashMap(),
            map = this.map,
            key;
            
        hash.suspendEvents();
        for (key in map) {
            if (map.hasOwnProperty(key)) {
                hash.add(key, map[key]);
            }
        }
        hash.resumeEvents();
        return hash;
    },

    /**
     * @private
     * Find the key for a value.
     * @param {Object} value The value to find.
     * @return {Object} The value of the item. Returns <tt>undefined</tt> if not found.
     */
    findKey: function(value) {
        var key,
            map = this.map;

        for (key in map) {
            if (map.hasOwnProperty(key) && map[key] === value) {
                return key;
            }
        }
        return undefined;
    }
});

/**
 * @class ExtTouch.util.Functions
 * @singleton
 */
ExtTouch.util.Functions = {
    /**
     * Creates an interceptor function. The passed function is called before the original one. If it returns false,
     * the original one is not called. The resulting function returns the results of the original function.
     * The passed function is called with the parameters of the original function. Example usage:
     * <pre><code>
var sayHi = function(name){
    alert('Hi, ' + name);
}

sayHi('Fred'); // alerts "Hi, Fred"

// create a new function that validates input without
// directly modifying the original function:
var sayHiToFriend = ExtTouch.createInterceptor(sayHi, function(name){
    return name == 'Brian';
});

sayHiToFriend('Fred');  // no alert
sayHiToFriend('Brian'); // alerts "Hi, Brian"
       </code></pre>
     * @param {Function} origFn The original function.
     * @param {Function} newFn The function to call before the original
     * @param {Object} scope (optional) The scope (<code><b>this</b></code> reference) in which the passed function is executed.
     * <b>If omitted, defaults to the scope in which the original function is called or the browser window.</b>
     * @param {Mixed} returnValue (optional) The value to return if the passed function return false (defaults to null).
     * @return {Function} The new function
     */
    createInterceptor: function(origFn, newFn, scope, returnValue) { 
        var method = origFn;
        if (!ExtTouch.isFunction(newFn)) {
            return origFn;
        }
        else {
            return function() {
                var me = this,
                    args = arguments;
                newFn.target = me;
                newFn.method = origFn;
                return (newFn.apply(scope || me || window, args) !== false) ?
                        origFn.apply(me || window, args) :
                        returnValue || null;
            };
        }
    },

    /**
     * Creates a delegate (callback) that sets the scope to obj.
     * Call directly on any function. Example: <code>ExtTouch.createDelegate(this.myFunction, this, [arg1, arg2])</code>
     * Will create a function that is automatically scoped to obj so that the <tt>this</tt> variable inside the
     * callback points to obj. Example usage:
     * <pre><code>
var sayHi = function(name){
    // Note this use of "this.tExtTouch" here.  This function expects to
    // execute within a scope that contains a tExtTouch property.  In this
    // example, the "this" variable is pointing to the btn object that
    // was passed in createDelegate below.
    alert('Hi, ' + name + '. You clicked the "' + this.tExtTouch + '" button.');
}

var btn = new ExtTouch.Button({
    tExtTouch: 'Say Hi',
    renderTo: ExtTouch.getBody()
});

// This callback will execute in the scope of the
// button instance. Clicking the button alerts
// "Hi, Fred. You clicked the "Say Hi" button."
btn.on('click', ExtTouch.createDelegate(sayHi, btn, ['Fred']));
       </code></pre>
     * @param {Function} fn The function to delegate.
     * @param {Object} scope (optional) The scope (<code><b>this</b></code> reference) in which the function is executed.
     * <b>If omitted, defaults to the browser window.</b>
     * @param {Array} args (optional) Overrides arguments for the call. (Defaults to the arguments passed by the caller)
     * @param {Boolean/Number} appendArgs (optional) if True args are appended to call args instead of overriding,
     * if a number the args are inserted at the specified position
     * @return {Function} The new function
     */
    createDelegate: function(fn, obj, args, appendArgs) {
        if (!ExtTouch.isFunction(fn)) {
            return fn;
        }
        return function() {
            var callArgs = args || arguments;
            if (appendArgs === true) {
                callArgs = Array.prototype.slice.call(arguments, 0);
                callArgs = callArgs.concat(args);
            }
            else if (ExtTouch.isNumber(appendArgs)) {
                callArgs = Array.prototype.slice.call(arguments, 0);
                // copy arguments first
                var applyArgs = [appendArgs, 0].concat(args);
                // create method call params
                Array.prototype.splice.apply(callArgs, applyArgs);
                // splice them in
            }
            return fn.apply(obj || window, callArgs);
        };
    },

    /**
     * Calls this function after the number of millseconds specified, optionally in a specific scope. Example usage:
     * <pre><code>
var sayHi = function(name){
    alert('Hi, ' + name);
}

// executes immediately:
sayHi('Fred');

// executes after 2 seconds:
ExtTouch.defer(sayHi, 2000, this, ['Fred']);

// this syntax is sometimes useful for deferring
// execution of an anonymous function:
ExtTouch.defer(function(){
    alert('Anonymous');
}, 100);
       </code></pre>
     * @param {Function} fn The function to defer.
     * @param {Number} millis The number of milliseconds for the setTimeout call (if less than or equal to 0 the function is executed immediately)
     * @param {Object} scope (optional) The scope (<code><b>this</b></code> reference) in which the function is executed.
     * <b>If omitted, defaults to the browser window.</b>
     * @param {Array} args (optional) Overrides arguments for the call. (Defaults to the arguments passed by the caller)
     * @param {Boolean/Number} appendArgs (optional) if True args are appended to call args instead of overriding,
     * if a number the args are inserted at the specified position
     * @return {Number} The timeout id that can be used with clearTimeout
     */
    defer: function(fn, millis, obj, args, appendArgs) {
        fn = ExtTouch.util.Functions.createDelegate(fn, obj, args, appendArgs);
        if (millis > 0) {
            return setTimeout(fn, millis);
        }
        fn();
        return 0;
    },


    /**
     * Create a combined function call sequence of the original function + the passed function.
     * The resulting function returns the results of the original function.
     * The passed fcn is called with the parameters of the original function. Example usage:
     * 

var sayHi = function(name){
    alert('Hi, ' + name);
}

sayHi('Fred'); // alerts "Hi, Fred"

var sayGoodbye = ExtTouch.createSequence(sayHi, function(name){
    alert('Bye, ' + name);
});

sayGoodbye('Fred'); // both alerts show

     * @param {Function} origFn The original function.
     * @param {Function} newFn The function to sequence
     * @param {Object} scope (optional) The scope (this reference) in which the passed function is executed.
     * If omitted, defaults to the scope in which the original function is called or the browser window.
     * @return {Function} The new function
     */
    createSequence: function(origFn, newFn, scope) {
        if (!ExtTouch.isFunction(newFn)) {
            return origFn;
        }
        else {
            return function() {
                var retval = origFn.apply(this || window, arguments);
                newFn.apply(scope || this || window, arguments);
                return retval;
            };
        }
    }
};

/**
 * Shorthand for {@link ExtTouch.util.Functions#defer}   
 * @param {Function} fn The function to defer.
 * @param {Number} millis The number of milliseconds for the setTimeout call (if less than or equal to 0 the function is executed immediately)
 * @param {Object} scope (optional) The scope (<code><b>this</b></code> reference) in which the function is executed.
 * <b>If omitted, defaults to the browser window.</b>
 * @param {Array} args (optional) Overrides arguments for the call. (Defaults to the arguments passed by the caller)
 * @param {Boolean/Number} appendArgs (optional) if True args are appended to call args instead of overriding,
 * if a number the args are inserted at the specified position
 * @return {Number} The timeout id that can be used with clearTimeout
 * @member ExtTouch
 * @method defer
 */

ExtTouch.defer = ExtTouch.util.Functions.defer;

/**
 * Shorthand for {@link ExtTouch.util.Functions#createInterceptor}   
 * @param {Function} origFn The original function.
 * @param {Function} newFn The function to call before the original
 * @param {Object} scope (optional) The scope (<code><b>this</b></code> reference) in which the passed function is executed.
 * <b>If omitted, defaults to the scope in which the original function is called or the browser window.</b>
 * @return {Function} The new function
 * @member ExtTouch
 * @method defer
 */

ExtTouch.createInterceptor = ExtTouch.util.Functions.createInterceptor;

/**
 * Shorthand for {@link ExtTouch.util.Functions#createSequence}
 * @param {Function} origFn The original function.
 * @param {Function} newFn The function to sequence
 * @param {Object} scope (optional) The scope (this reference) in which the passed function is executed.
 * If omitted, defaults to the scope in which the original function is called or the browser window.
 * @return {Function} The new function
 * @member ExtTouch
 * @method defer
 */

ExtTouch.createSequence = ExtTouch.util.Functions.createSequence;

/**
 * Shorthand for {@link ExtTouch.util.Functions#createDelegate}
 * @param {Function} fn The function to delegate.
 * @param {Object} scope (optional) The scope (<code><b>this</b></code> reference) in which the function is executed.
 * <b>If omitted, defaults to the browser window.</b>
 * @param {Array} args (optional) Overrides arguments for the call. (Defaults to the arguments passed by the caller)
 * @param {Boolean/Number} appendArgs (optional) if True args are appended to call args instead of overriding,
 * if a number the args are inserted at the specified position
 * @return {Function} The new function
 * @member ExtTouch
 * @method defer
 */
ExtTouch.createDelegate = ExtTouch.util.Functions.createDelegate; 

/**
 * @class ExtTouch.util.Point
 * @ExtTouchends Object
 *
 * Represents a 2D point with x and y properties, useful for comparison and instantiation
 * from an event:
 * <pre><code>
 * var point = ExtTouch.util.Point.fromEvent(e);
 * </code></pre>
 */

ExtTouch.util.Point = ExtTouch.ExtTouchend(Object, {
    constructor: function(x, y) {
        this.x = (x != null && !isNaN(x)) ? x : 0;
        this.y = (y != null && !isNaN(y)) ? y : 0;

        return this;
    },

    /**
     * Copy a new instance of this point
     * @return {ExtTouch.util.Point} the new point
     */
    copy: function() {
        return new ExtTouch.util.Point(this.x, this.y);
    },

    /**
     * Copy the x and y values of another point / object to this point itself
     * @param {}
     * @return {ExtTouch.util.Point} this This point
     */
    copyFrom: function(p) {
        this.x = p.x;
        this.y = p.y;

        return this;
    },

    /**
     * Returns a human-eye-friendly string that represents this point,
     * useful for debugging
     * @return {String}
     */
    toString: function() {
        return "Point[" + this.x + "," + this.y + "]";
    },

    /**
     * Compare this point and another point
     * @param {ExtTouch.util.Point/Object} The point to compare with, either an instance
     * of ExtTouch.util.Point or an object with x and y properties
     * @return {Boolean} Returns whether they are equivalent
     */
    equals: function(p) {
        return (this.x == p.x && this.y == p.y);
    },

    /**
     * Whether the given point is not away from this point within the given threshold amount
     * @param {ExtTouch.util.Point/Object} The point to check with, either an instance
     * of ExtTouch.util.Point or an object with x and y properties
     * @param {Object/Number} threshold Can be either an object with x and y properties or a number
     * @return {Boolean}
     */
    isWithin: function(p, threshold) {
        if (!ExtTouch.isObject(threshold)) {
            threshold = {x: threshold};
            threshold.y = threshold.x;
        }

        return (this.x <= p.x + threshold.x && this.x >= p.x - threshold.x &&
                this.y <= p.y + threshold.y && this.y >= p.y - threshold.y);
    },

    /**
     * Translate this point by the given amounts
     * @param {Number} x Amount to translate in the x-axis
     * @param {Number} y Amount to translate in the y-axis
     * @return {Boolean}
     */
    translate: function(x, y) {
        if (x != null && !isNaN(x))
            this.x += x;

        if (y != null && !isNaN(y))
            this.y += y;
    },

    /**
     * Compare this point with another point when the x and y values of both points are rounded. E.g:
     * [100.3,199.8] will equals to [100, 200]
     * @param {ExtTouch.util.Point/Object} The point to compare with, either an instance
     * of ExtTouch.util.Point or an object with x and y properties
     * @return {Boolean}
     */
    roundedEquals: function(p) {
        return (Math.round(this.x) == Math.round(p.x) && Math.round(this.y) == Math.round(p.y));
    }
});

/**
 * Returns a new instance of ExtTouch.util.Point base on the pageX / pageY values of the given event
 * @static
 * @param {Event} e The event
 * @returns ExtTouch.util.Point
 */
ExtTouch.util.Point.fromEvent = function(e) {
    var a = (e.changedTouches && e.changedTouches.length > 0) ? e.changedTouches[0] : e;
    return new ExtTouch.util.Point(a.pageX, a.pageY);
};

/**
 * @class ExtTouch.AbstractManager
 * @ExtTouchends Object
 * @ignore
 * Base Manager class - ExtTouchended by ComponentMgr and PluginMgr
 */
ExtTouch.AbstractManager = ExtTouch.ExtTouchend(Object, {
    typeName: 'type',

    constructor: function(config) {
        ExtTouch.apply(this, config || {});

        /**
         * Contains all of the items currently managed
         * @property all
         * @type ExtTouch.util.MixedCollection
         */
        this.all = new ExtTouch.util.HashMap();

        this.types = {};
    },

    /**
     * Returns a component by {@link ExtTouch.Component#id id}.
     * For additional details see {@link ExtTouch.util.MixedCollection#get}.
     * @param {String} id The component {@link ExtTouch.Component#id id}
     * @return ExtTouch.Component The Component, <code>undefined</code> if not found, or <code>null</code> if a
     * Class was found.
     */
    get : function(id) {
        return this.all.get(id);
    },

    /**
     * Registers an item to be managed
     * @param {Mixed} item The item to register
     */
    register: function(item) {
        this.all.add(item);
    },

    /**
     * Unregisters a component by removing it from this manager
     * @param {Mixed} item The item to unregister
     */
    unregister: function(item) {
        this.all.remove(item);
    },

    /**
     * <p>Registers a new Component constructor, keyed by a new
     * {@link ExtTouch.Component#xtype}.</p>
     * <p>Use this method (or its alias {@link ExtTouch#reg ExtTouch.reg}) to register new
     * subclasses of {@link ExtTouch.Component} so that lazy instantiation may be used when specifying
     * child Components.
     * see {@link ExtTouch.Container#items}</p>
     * @param {String} xtype The mnemonic string by which the Component class may be looked up.
     * @param {Constructor} cls The new Component class.
     */
    registerType : function(type, cls) {
        this.types[type] = cls;
        cls[this.typeName] = type;
    },

    /**
     * Checks if a Component type is registered.
     * @param {ExtTouch.Component} xtype The mnemonic string by which the Component class may be looked up
     * @return {Boolean} Whether the type is registered.
     */
    isRegistered : function(type){
        return this.types[type] !== undefined;
    },

    /**
     * Creates and returns an instance of whatever this manager manages, based on the supplied type and config object
     * @param {Object} config The config object
     * @param {String} defaultType If no type is discovered in the config object, we fall back to this type
     * @return {Mixed} The instance of whatever this manager is managing
     */
    create: function(config, defaultType) {
        var type        = config[this.typeName] || config.type || defaultType,
            Constructor = this.types[type];

        if (Constructor == undefined) {
            throw new Error(ExtTouch.util.Format.format("The '{0}' type has not been registered with this manager", type));
        }

        return new Constructor(config);
    },

    /**
     * Registers a function that will be called when a Component with the specified id is added to the manager. This will happen on instantiation.
     * @param {String} id The component {@link ExtTouch.Component#id id}
     * @param {Function} fn The callback function
     * @param {Object} scope The scope (<code>this</code> reference) in which the callback is executed. Defaults to the Component.
     */
    onAvailable : function(id, fn, scope){
        var all = this.all;

        all.on("add", function(index, o){
            if (o.id == id) {
                fn.call(scope || o, o);
                all.un("add", fn, scope);
            }
        });
    },
    
    /**
     * Executes the specified function once for each item in the collection.
     * Returning false from the function will cease iteration.
     * 
     * The paramaters passed to the function are:
     * <div class="mdetail-params"><ul>
     * <li><b>key</b> : String<p class="sub-desc">The key of the item</p></li>
     * <li><b>value</b> : Number<p class="sub-desc">The value of the item</p></li>
     * <li><b>length</b> : Number<p class="sub-desc">The total number of items in the collection</p></li>
     * </ul></div>
     * @param {Object} fn The function to execute.
     * @param {Object} scope The scope to execute in. Defaults to <tt>this</tt>.
     */
    each: function(fn, scope){
        this.all.each(fn, scope || this);    
    },
    
    /**
     * Gets the number of items in the collection.
     * @return {Number} The number of items in the collection.
     */
    getCount: function(){
        return this.all.getCount();
    }
}); 

ExtTouch.gesture.Manager = new ExtTouch.AbstractManager({
    eventNames: {
        start: 'touchstart',
        move: 'touchmove',
        end: 'touchend'
    },

    //defaultPreventedMouseEvents: ['click'],

    clickMoveThreshold: 5,

    init: function() {
        this.targets = [];

        this.followTouches = [];
        this.currentGestures = [];
        this.currentTargets = [];

        /*
        if (!ExtTouch.supports.Touch) {
            ExtTouch.apply(this.eventNames, {
                start: 'mousedown',
                move: 'mousemove',
                end: 'mouseup'
            });
        }
        */

        this.listenerWrappers = {
            start: ExtTouch.createDelegate(this.onTouchStart, this),
            move: ExtTouch.createDelegate(this.onTouchMove, this),
            end: ExtTouch.createDelegate(this.onTouchEnd, this),
            //mouse: ExtTouch.createDelegate(this.onMouseEvent, this)
        };

        this.attachListeners();
    },

    freeze: function() {
        this.isFrozen = true;
    },

    thaw: function() {
        this.isFrozen = false;
    },

    getEventSimulator: function() {
        if (!this.eventSimulator) {
            this.eventSimulator = new ExtTouch.util.EventSimulator();
        }

        return this.eventSimulator;
    },

    attachListeners: function() {
        ExtTouch.iterate(this.eventNames, function(key, name) {
            document.addEventListener(name, this.listenerWrappers[key], false);
        }, this);

        /*if (ExtTouch.supports.Touch) {
            this.defaultPreventedMouseEvents.forEach(function(name) {
                document.addEventListener(name, this.listenerWrappers['mouse'], true);
            }, this);
        }*/
    },

    detachListeners: function() {
        ExtTouch.iterate(this.eventNames, function(key, name) {
            document.removeEventListener(name, this.listenerWrappers[key], false);
        }, this);

        /*if (ExtTouch.supports.Touch) {
            this.defaultPreventedMouseEvents.forEach(function(name) {
                document.removeEventListener(name, this.listenerWrappers['mouse'], true);
            }, this);
        }*/
    },
/*
    onMouseEvent: function(e) {
        if (!e.isSimulated) {
            e.preventDefault();
            e.stopPropagation();
        }
    },
*/
    onTouchStart: function(e) {
        var targets = [],
            target = e.target;

        if (e.stopped === true) {
            return;
        }

        if (ExtTouch.is.Android) {
            if (!(target.tagName && ['input', 'tExtToucharea', 'select'].indexOf(target.tagName.toLowerCase()) !== -1)) {
                e.preventDefault();
            }
        }

        if (this.isFrozen) {
            return;
        }

        // There's already a touchstart without any touchend!
        // This used to happen on HTC Desire and HTC Incredible
        // We have to clean it up
        if (this.startEvent) {
            this.onTouchEnd(e);
        }

        this.locks = {};

        this.currentTargets = [target];

        while (target) {
            if (this.targets.indexOf(target) !== -1) {
                targets.unshift(target);
            }

            target = target.parentNode;
            this.currentTargets.push(target);
        }

        this.startEvent = e;
        this.startPoint = ExtTouch.util.Point.fromEvent(e);
        this.lastMovePoint = null;
        this.isClick = true;
        this.handleTargets(targets, e);
    },

    onTouchMove: function(e) {
        if (ExtTouch.is.MultiTouch) {
            e.preventDefault();
        }

        if (!this.startEvent) {
            return;
        }

        if (ExtTouch.is.Desktop) {
            e.target = this.startEvent.target;
        }

        if (this.isFrozen) {
            return;
        }

        var gestures = this.currentGestures,
            gesture,
            touch = e.changedTouches ? e.changedTouches[0] : e;

        this.lastMovePoint = ExtTouch.util.Point.fromEvent(e);

        if (ExtTouch.supports.Touch && this.isClick && !this.lastMovePoint.isWithin(this.startPoint, this.clickMoveThreshold)) {
            this.isClick = false;
        }

        for (var i = 0; i < gestures.length; i++) {
            if (e.stopped) {
                break;
            }

            gesture = gestures[i];

            if (gesture.listenForMove) {
                gesture.onTouchMove(e, touch);
            }
        }
    },

    // This listener is here to always ensure we stop all current gestures
    onTouchEnd: function(e) {
        if (ExtTouch.is.Blackberry) {
            e.preventDefault();
        }

        if (this.isFrozen) {
            return;
        }

        var gestures = this.currentGestures.slice(0),
            ln = gestures.length,
            i, gesture, endPoint,
            needsAnotherMove = false,
            touch = e.changedTouches ? e.changedTouches[0] : e;

        if (this.startPoint) {
            endPoint = ExtTouch.util.Point.fromEvent(e);
            if (!(this.lastMovePoint || this.startPoint)['equals'](endPoint)) {
                needsAnotherMove = true;
            }
        }

        for (i = 0; i < ln; i++) {
            gesture = gestures[i];

            if (!e.stopped && gesture.listenForEnd) {
                // The point has changed, we should execute another onTouchMove before onTouchEnd
                // to deal with the problem of missing events on Androids and alike
                // This significantly improves scrolling experience on Androids!
                if (needsAnotherMove) {
                    gesture.onTouchMove(e, touch);
                }

                gesture.onTouchEnd(e, touch);
            }

            this.stopGesture(gesture);
        }


        if (ExtTouch.supports.Touch && this.isClick) {
            this.isClick = false;
            //this.getEventSimulator().fire('click', this.startEvent.target, touch);
        }

        this.lastMovePoint = null;
        this.followTouches = [];
        this.startedChangedTouch = false;
        this.currentTargets = [];
        this.startEvent = null;
        this.startPoint = null;
    },

    handleTargets: function(targets, e) {
        // In handle targets we have to first handle all the capture targets,
        // then all the bubble targets.
        var ln = targets.length,
            i;

        this.startedChangedTouch = false;
        this.startedTouches = ExtTouch.supports.Touch ? e.touches : [e];

        for (i = 0; i < ln; i++) {
            if (e.stopped) {
                break;
            }

            this.handleTarget(targets[i], e, true);
        }

        for (i = ln - 1; i >= 0; i--) {
            if (e.stopped) {
                break;
            }

            this.handleTarget(targets[i], e, false);
        }

        if (this.startedChangedTouch) {
            this.followTouches = this.followTouches.concat((ExtTouch.supports.Touch && e.targetTouches) ? ExtTouch.toArray(e.targetTouches) : [e]);
        }
    },

    handleTarget: function(target, e, capture) {
        var gestures = ExtTouch.Element.data(target, 'x-gestures') || [],
            ln = gestures.length,
            i, gesture;

        for (i = 0; i < ln; i++) {
            gesture = gestures[i];
            if (
                (!!gesture.capture === !!capture) &&
                (this.followTouches.length < gesture.touches) &&
                ((ExtTouch.supports.Touch && e.targetTouches) ? (e.targetTouches.length === gesture.touches) : true)
            ) {
                this.startedChangedTouch = true;
                this.startGesture(gesture);

                if (gesture.listenForStart) {
                    gesture.onTouchStart(e, e.changedTouches ? e.changedTouches[0] : e);
                }

                if (e.stopped) {
                    break;
                }
            }
        }
    },

    startGesture: function(gesture) {
        gesture.started = true;
        this.currentGestures.push(gesture);
    },

    stopGesture: function(gesture) {
        gesture.started = false;
        this.currentGestures.remove(gesture);
    },

    addEventListener: function(target, eventName, listener, options) {
        target = ExtTouch.getDom(target);
        options = options || {};

        var targets = this.targets,
            name = this.getGestureName(eventName),
            gestures = ExtTouch.Element.data(target, 'x-gestures'),
            gesture;

        if (!gestures) {
            gestures = [];
            ExtTouch.Element.data(target, 'x-gestures', gestures);
        }

        // <debug>
        if (!name) {
            throw new Error('Trying to subscribe to unknown event ' + eventName);
        }
        // </debug>

        if (targets.indexOf(target) === -1) {
            this.targets.push(target);
        }

        gesture = this.get(target.id + '-' + name);

        if (!gesture) {
            gesture = this.create(ExtTouch.apply({}, options, {
                target: target,
                type: name
            }));

            gestures.push(gesture);
            // The line below is not needed, ExtTouch.Element.data(target, 'x-gestures') still reference gestures
            // ExtTouch.Element.data(target, 'x-gestures', gestures);
        }

        gesture.addListener(eventName, listener);

        // If there is already a finger down, then instantly start the gesture
        if (this.startedChangedTouch && this.currentTargets.contains(target) && !gesture.started && !options.subsequent) {
            this.startGesture(gesture);
            if (gesture.listenForStart) {
                gesture.onTouchStart(this.startEvent, this.startedTouches[0]);
            }
        }
    },

    removeEventListener: function(target, eventName, listener) {
        target = ExtTouch.getDom(target);

        var name = this.getGestureName(eventName),
            gestures = ExtTouch.Element.data(target, 'x-gestures') || [],
            gesture;

        gesture = this.get(target.id + '-' + name);

        if (gesture) {
            gesture.removeListener(eventName, listener);

            for (name in gesture.listeners) {
                return;
            }

            gesture.destroy();
            gestures.remove(gesture);
            ExtTouch.Element.data(target, 'x-gestures', gestures);
        }
    },

    getGestureName: function(ename) {
        return this.names && this.names[ename];
    },

    registerType: function(type, cls) {
        var handles = cls.prototype.handles,
            i, ln;

        this.types[type] = cls;

        cls[this.typeName] = type;

        if (!handles) {
            handles = cls.prototype.handles = [type];
        }

        this.names = this.names || {};

        for (i = 0, ln = handles.length; i < ln; i++) {
            this.names[handles[i]] = type;
        }
    }
});

ExtTouch.regGesture = function() {
    return ExtTouch.gesture.Manager.registerType.apply(ExtTouch.gesture.Manager, arguments);
};

ExtTouch.TouchEventObjectImpl = ExtTouch.ExtTouchend(Object, {
    constructor : function(e, args) {
        if (e) {
            this.setEvent(e, args);
        }
    },

    setEvent : function(e, args) {
        ExtTouch.apply(this, {
            event: e,
            time: e.timeStamp
        });

        this.touches = e.touches || [e];
        this.changedTouches = e.changedTouches || [e];
        this.targetTouches = e.targetTouches || [e];
        
        if (args) {
            this.target = args.target;
            ExtTouch.apply(this, args);
        }
        else {
            this.target = e.target;
        }
        return this;
    },

    stopEvent : function() {
        this.stopPropagation();
        this.preventDefault();
    },

    stopPropagation : function() {
        this.event.stopped = true;
    },

    preventDefault : function() {
        this.event.preventDefault();
    },

    getTarget : function(selector, maxDepth, returnEl) {
        if (selector) {
            return ExtTouch.fly(this.target).findParent(selector, maxDepth, returnEl);
        }
        else {
            return returnEl ? ExtTouch.get(this.target) : this.target;
        }
    }
});

ExtTouch.TouchEventObject = new ExtTouch.TouchEventObjectImpl();

ExtTouch.gesture.Gesture = ExtTouch.ExtTouchend(Object, {    
    listenForStart: true,
    listenForEnd: true,
    listenForMove: true,
    
    disableLocking: false,
    
    touches: 1,
    
    constructor: function(config) {
        config = config || {};
        ExtTouch.apply(this, config);
        
        this.target = ExtTouch.getDom(this.target);
        this.listeners = {};
        
        // <debug>
        if (!this.target) {
            throw new Error('Trying to bind a ' + this.type + ' event to element that does\'nt exist: ' + this.target);
        }
        // </debug>
        
        this.id = this.target.id + '-' + this.type;
        
        ExtTouch.gesture.Gesture.superclass.constructor.call(this);
        ExtTouch.gesture.Manager.register(this);
    },
    
    addListener: function(name, listener) {
        this.listeners[name] = this.listeners[name] || [];
        this.listeners[name].push(listener);
    },
    
    removeListener: function(name, listener) {
        var listeners = this.listeners[name];
            
        if (listeners) {
            listeners.remove(listener);

            if (listeners.length == 0) {
                delete this.listeners[name];
            }

            for (name in this.listeners) {
                if (this.listeners.hasOwnProperty(name)) {
                    return;
                }
            }
            
            this.listeners = {};
        }
    },
    
    fire: function(type, e, args) {
        var listeners = this.listeners && this.listeners[type],
            ln = listeners && listeners.length,
            i;

        if (!this.disableLocking && this.isLocked(type)) {
            return false;
        }
        
        if (ln) {
            args = ExtTouch.apply(args || {}, {
                time: e.timeStamp,
                type: type,
                gesture: this,
                target: (e.target.nodeType == 3) ? e.target.parentNode: e.target
            });
            
            for (i = 0; i < ln; i++) {
                listeners[i](e, args);
            }
        }
        
        return true;
    },
    
    stop: function() {
        ExtTouch.gesture.Manager.stopGesture(this);
    },
    
    lock: function() {
        if (!this.disableLocking) {
            var args = arguments,
                ln = args.length,
                i;

            for (i = 0; i < ln; i++) {
                ExtTouch.gesture.Manager.locks[args[i]] = this.id;
            }            
        }
    },
    
    unlock: function() {
        if (!this.disableLocking) {
            var args = arguments,
                ln = args.length,
                i;

            for (i = 0; i < ln; i++) {
                if (ExtTouch.gesture.Manager.locks[args[i]] == this.id) {
                    delete ExtTouch.gesture.Manager.locks[args[i]]; 
                }
            }            
        }
    },
    
    isLocked : function(type) {
        var lock = ExtTouch.gesture.Manager.locks[type];
        return !!(lock && lock !== this.id);
    },
    
    getLockingGesture : function(type) {
        var lock = ExtTouch.gesture.Manager.locks[type];
        if (lock) {
            return ExtTouch.gesture.Manager.get(lock) || null;
        }
        return null;
    },
    
    onTouchStart: ExtTouch.emptyFn,
    onTouchMove: ExtTouch.emptyFn,
    onTouchEnd: ExtTouch.emptyFn,
    
    destroy: function() {
        this.stop();
        this.listeners = null;
        ExtTouch.gesture.Manager.unregister(this);
    }
});

ExtTouch.gesture.Touch = ExtTouch.ExtTouchend(ExtTouch.gesture.Gesture, {
    handles: ['touchstart', 'touchmove', 'touchend', 'touchdown'],
    
    touchDownInterval: 500,
    
    onTouchStart: function(e, touch) {
        this.startX = this.previousX = touch.pageX;
        this.startY = this.previousY = touch.pageY;
        this.startTime = this.previousTime = e.timeStamp;

        this.fire('touchstart', e);
        this.lastEvent = e;
        
        if (this.listeners && this.listeners.touchdown) {
            this.touchDownIntervalId = setInterval(ExtTouch.createDelegate(this.touchDownHandler, this), this.touchDownInterval);
        }
    },
    
    onTouchMove: function(e, touch) {
        this.fire('touchmove', e, this.getInfo(touch));
        this.lastEvent = e;
    },
    
    onTouchEnd: function(e) {
        this.fire('touchend', e, this.lastInfo);
        clearInterval(this.touchDownIntervalId);
    },
    
    touchDownHandler : function() {
        this.fire('touchdown', this.lastEvent, this.lastInfo);
    },
    
    getInfo : function(touch) {
        var time = Date.now(),
            deltaX = touch.pageX - this.startX,
            deltaY = touch.pageY - this.startY,
            info = {
                startX: this.startX,
                startY: this.startY,
                previousX: this.previousX,
                previousY: this.previousY,
                pageX: touch.pageX,
                pageY: touch.pageY,
                deltaX: deltaX,
                deltaY: deltaY,
                absDeltaX: Math.abs(deltaX),
                absDeltaY: Math.abs(deltaY),
                previousDeltaX: touch.pageX - this.previousX,
                previousDeltaY: touch.pageY - this.previousY,
                time: time,
                startTime: this.startTime,
                previousTime: this.previousTime,
                deltaTime: time - this.startTime,
                previousDeltaTime: time - this.previousTime
            };
        
        this.previousTime = info.time;
        this.previousX = info.pageX;
        this.previousY = info.pageY;
        this.lastInfo = info;
        
        return info;
    }
});

ExtTouch.regGesture('touch', ExtTouch.gesture.Touch);

ExtTouch.gesture.Swipe = ExtTouch.ExtTouchend(ExtTouch.gesture.Gesture, {    
    listenForEnd: false,
   
    swipeThreshold: 35,
    swipeTime: 1000,
    
    onTouchStart : function(e, touch) {
        this.startTime = e.timeStamp;
        this.startX = touch.pageX;
        this.startY = touch.pageY;
        this.lock('scroll', 'scrollstart', 'scrollend');
    },
   
    onTouchMove : function(e, touch) {
        var deltaY = touch.pageY - this.startY,
            deltaX = touch.pageX - this.startX,
            absDeltaY = Math.abs(deltaY),
            absDeltaX = Math.abs(deltaX),
            deltaTime = e.timeStamp - this.startTime;

        // If the swipeTime is over, we are not gonna check for it again
        if (absDeltaY - absDeltaX > 3 || deltaTime > this.swipeTime) {
            this.unlock('drag', 'dragstart', 'dragend');
            this.stop();
        }
        else if (absDeltaX > this.swipeThreshold && absDeltaX > absDeltaY) {
           // If this is a swipe, a scroll is not possible anymore
           this.fire('swipe', e, {
               direction: (deltaX < 0) ? 'left' : 'right',
               distance: absDeltaX,
               deltaTime: deltaTime,
               deltaX: deltaX
           });
   
           this.stop();
        }
    }
});
ExtTouch.regGesture('swipe', ExtTouch.gesture.Swipe);

ExtTouch.gesture.Tap = ExtTouch.ExtTouchend(ExtTouch.gesture.Gesture, {
    handles: [
        'tapstart',
        'tapcancel',
        'tap', 
        'doubletap', 
        'taphold',
        'singletap'
    ],
    
    cancelThreshold: 10,
    
    doubleTapThreshold: 800,

    singleTapThreshold: 400,

    holdThreshold: 1000,

    fireClickEvent: false,
    
    onTouchStart : function(e, touch) {
        var me = this;
        
        me.startX = touch.pageX;
        me.startY = touch.pageY;
        me.fire('tapstart', e, me.getInfo(touch));
        
        if (this.listeners.taphold) {    
            me.timeout = setTimeout(function() {
                me.fire('taphold', e, me.getInfo(touch));
                delete me.timeout;
            }, me.holdThreshold);            
        }
        
        me.lastTouch = touch;
    },
    
    onTouchMove : function(e, touch) {
        var me = this;
        if (me.isCancel(touch)) {
            me.fire('tapcancel', e, me.getInfo(touch));
            if (me.timeout) {
                clearTimeout(me.timeout);
                delete me.timeout;
            }
            me.stop();
        }
        
        me.lastTouch = touch;
    },
    
    onTouchEnd : function(e) {
        var me = this,
            info = me.getInfo(me.lastTouch);
        
        this.fireTapEvent(e, info);
        
        if (me.lastTapTime && e.timeStamp - me.lastTapTime <= me.doubleTapThreshold) {
            me.lastTapTime = null;
            e.preventDefault();
            me.fire('doubletap', e, info);
        }
        else {
            me.lastTapTime = e.timeStamp;
        }

        if (me.listeners && me.listeners.singletap && me.singleTapThreshold && !me.preventSingleTap) {
            me.fire('singletap', e, info);
            me.preventSingleTap = true;
            setTimeout(function() {
                me.preventSingleTap = false;
            }, me.singleTapThreshold);
        }
        
        if (me.timeout) {
            clearTimeout(me.timeout);
            delete me.timeout;
        }
    },

    fireTapEvent: function(e, info) {
        this.fire('tap', e, info);
        
        if (e.event)
            e = e.event;

        var target = (e.changedTouches ? e.changedTouches[0] : e).target;

        if (!target.disabled && this.fireClickEvent) {
            var clickEvent = document.createEvent("MouseEvent");
                clickEvent.initMouseEvent('click', e.bubbles, e.cancelable, document.defaultView, e.detail, e.screenX, e.screenY, e.clientX,
                                         e.clientY, e.ctrlKey, e.altKey, e.shiftKey, e.metaKey, e.metaKey, e.button, e.relatedTarget);
                clickEvent.isSimulated = true;


            target.dispatchEvent(clickEvent);
        }
    },
    
    getInfo : function(touch) {
        var x = touch.pageX,
            y = touch.pageY;
            
        return {
            pageX: x,
            pageY: y,
            startX: x,
            startY: y
        };
    },
    
    isCancel : function(touch) {
        var me = this;
        return (
            Math.abs(touch.pageX - me.startX) >= me.cancelThreshold ||
            Math.abs(touch.pageY - me.startY) >= me.cancelThreshold
        );
    }
});
ExtTouch.regGesture('tap', ExtTouch.gesture.Tap);

ExtTouch.gesture.Pinch = ExtTouch.ExtTouchend(ExtTouch.gesture.Gesture, {
    handles: ['pinchstart', 'pinch', 'pinchend'],

    touches: 2,

    onTouchStart: function(e) {
        var me = this;

        if (this.isMultiTouch(e)) {
            me.lock('swipe', 'scroll', 'scrollstart', 'scrollend', 'touchmove', 'touchend', 'touchstart', 'tap', 'tapstart', 'taphold', 'tapcancel', 'doubletap');
            me.pinching = true;

            var targetTouches = e.targetTouches;

            me.startFirstTouch = targetTouches[0];
            me.startSecondTouch = targetTouches[1];

            me.previousDistance = me.startDistance = me.getDistance(me.startFirstTouch, me.startSecondTouch);
            me.previousScale = 1;

            me.fire('pinchstart', e, {
                distance: me.startDistance,
                scale: me.previousScale
            });
        } else if (me.pinching) {
            me.unlock('swipe', 'scroll', 'scrollstart', 'scrollend', 'touchmove', 'touchend', 'touchstart', 'tap', 'tapstart', 'taphold', 'tapcancel', 'doubletap');
            me.pinching = false;
        }
    },

    isMultiTouch: function(e) {
        return e && ExtTouch.supports.Touch && e.targetTouches && e.targetTouches.length > 1;
    },

    onTouchMove: function(e) {
        if (!this.isMultiTouch(e)) {
            this.onTouchEnd(e);
            return;
        }

        if (this.pinching) {
            this.fire('pinch', e, this.getPinchInfo(e));
        }
    },

    onTouchEnd: function(e) {
        if (this.pinching) {
            this.fire('pinchend', e);
        }
    },

    getPinchInfo: function(e) {
        var me = this,
            targetTouches = e.targetTouches,
            firstTouch = targetTouches[0],
            secondTouch = targetTouches[1],
            distance = me.getDistance(firstTouch, secondTouch),
            scale = distance / me.startDistance,
            info = {
            scale: scale,
            deltaScale: scale - 1,
            previousScale: me.previousScale,
            previousDeltaScale: scale - me.previousScale,
            distance: distance,
            deltaDistance: distance - me.startDistance,
            startDistance: me.startDistance,
            previousDistance: me.previousDistance,
            previousDeltaDistance: distance - me.previousDistance,
            firstTouch: firstTouch,
            secondTouch: secondTouch,
            firstPageX: firstTouch.pageX,
            firstPageY: firstTouch.pageY,
            secondPageX: secondTouch.pageX,
            secondPageY: secondTouch.pageY,
            // The midpoint between the touches is (x1 + x2) / 2, (y1 + y2) / 2
            midPointX: (firstTouch.pageX + secondTouch.pageX) / 2,
            midPointY: (firstTouch.pageY + secondTouch.pageY) / 2
        };

        me.previousScale = scale;
        me.previousDistance = distance;

        return info;
    },

    getDistance: function(firstTouch, secondTouch) {
        return Math.sqrt(
        Math.pow(Math.abs(firstTouch.pageX - secondTouch.pageX), 2) + Math.pow(Math.abs(firstTouch.pageY - secondTouch.pageY), 2));
    }
});

ExtTouch.regGesture('pinch', ExtTouch.gesture.Pinch); 

